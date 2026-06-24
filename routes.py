from flask import Blueprint, render_template, request, redirect, url_for, jsonify, session, current_app
from flask_login import login_user, logout_user, login_required, current_user
from models import db, User, Video, Summary, DailyUsage, SubscriptionPlan
from datetime import datetime, timedelta
from werkzeug.urls import url_parse
import stripe
import json
from utils import (
    get_video_info, get_video_transcript, summarize_text, is_valid_youtube_url,
    extract_transcript_highlights, get_transcript_error, parse_transcript_segments,
)

# Blueprints
main_bp = Blueprint('main', __name__)
auth_bp = Blueprint('auth', __name__)
api_bp = Blueprint('api', __name__, url_prefix='/api')
payment_bp = Blueprint('payment', __name__, url_prefix='/payment')

# ==================== ROTAS PRINCIPAIS ====================

@main_bp.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    return render_template('index.html')

@main_bp.route('/pricing')
def pricing():
    return render_template('pricing.html')

@main_bp.route('/dashboard')
@login_required
def dashboard():
    summaries = Summary.query.filter_by(user_id=current_user.id).order_by(
        Summary.created_at.desc()
    ).limit(10).all()
    
    daily_usage = current_user.get_daily_usage()
    plan_limit = 999999 if current_user.plan == 'premium' else 3
    plan_display = 'Ilimitado' if current_user.plan == 'premium' else '3'
    
    return render_template('dashboard.html', 
                         summaries=summaries,
                         daily_usage=daily_usage,
                         plan_limit=plan_limit,
                         plan_display=plan_display)

# ==================== ROTAS DE AUTENTICAÇÃO ====================

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        full_name = request.form.get('full_name')
        
        # Validações
        if not all([username, email, password, confirm_password]):
            return render_template('register.html', error='Todos os campos são obrigatórios')
        
        if len(username) < 3:
            return render_template('register.html', error='Username deve ter pelo menos 3 caracteres')
        
        if password != confirm_password:
            return render_template('register.html', error='As senhas não coincidem')
        
        if len(password) < 6:
            return render_template('register.html', error='Senha deve ter pelo menos 6 caracteres')
        
        if User.query.filter_by(username=username).first():
            return render_template('register.html', error='Username já existe')
        
        if User.query.filter_by(email=email).first():
            return render_template('register.html', error='Email já cadastrado')
        
        # Criar novo usuário
        user = User(username=username, email=email, full_name=full_name)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        
        login_user(user)
        return redirect(url_for('main.dashboard'))
    
    return render_template('register.html')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.query.filter_by(username=username).first()
        
        if user is None or not user.check_password(password):
            return render_template('login.html', error='Username ou senha inválidos')
        
        if not user.is_active:
            return render_template('login.html', error='Conta desativada')
        
        login_user(user, remember=request.form.get('remember') is not None)
        
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('main.dashboard')
        
        return redirect(next_page)
    
    return render_template('login.html')

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))

# ==================== ROTAS DA API ====================

@api_bp.route('/summarize', methods=['POST'])
@login_required
def summarize_video():
    try:
        data = request.get_json()
        url = data.get('url', '').strip()
        
        if not url:
            return jsonify({'error': 'URL do vídeo é obrigatória'}), 400
        
        if not is_valid_youtube_url(url):
            return jsonify({'error': 'URL do YouTube inválida'}), 400
        
        # Verificar limite do plano
        if not current_user.can_summarize():
            return jsonify({
                'error': 'Limite de 3 resumos por dia atingido. Upgrade para Premium!'
            }), 429
        
        # Obter informações do vídeo
        video_info = get_video_info(url)
        if not video_info:
            return jsonify({'error': 'Não foi possível obter informações do vídeo'}), 400
        
        # Verificar duração
        if video_info.get('duration', 0) > current_app.config['MAX_VIDEO_LENGTH'] * 60:
            return jsonify({'error': f'Vídeo muito longo. Máximo: {current_app.config["MAX_VIDEO_LENGTH"]} minutos'}), 400
        
        # Criar registro de vídeo
        video = Video(
            user_id=current_user.id,
            url=url,
            title=video_info.get('title'),
            duration=video_info.get('duration'),
            thumbnail=video_info.get('thumbnail')
        )
        db.session.add(video)
        db.session.flush()
        
        # Criar registro de resumo (inicialmente processando)
        summary = Summary(
            user_id=current_user.id,
            video_id=video.id,
            summary='',  # Valor padrão vazio em vez de None
            status='processing'
        )
        db.session.add(summary)
        db.session.commit()
        
        # Processar em background (aqui fazemos de forma síncrona para simplicidade)
        try:
            transcript_result = get_video_transcript(url)

            if not transcript_result or not transcript_result.get('text'):
                error_message = get_transcript_error() or 'Não foi possível extrair a transcrição do vídeo'
                summary.status = 'failed'
                summary.error_message = error_message
                db.session.commit()
                return jsonify({'error': error_message}), 400

            transcript = transcript_result['text']
            paragraphs = transcript_result.get('paragraphs') or []

            summary.original_transcript = transcript
            summary.transcript_segments = json.dumps(paragraphs, ensure_ascii=False)
            
            # Gerar resumo com IA
            ai_summary = summarize_text(transcript)
            
            if not ai_summary:
                summary.status = 'failed'
                summary.error_message = 'Erro ao gerar resumo com IA'
                db.session.commit()
                return jsonify({'error': 'Erro ao gerar resumo'}), 500
            
            summary.summary = ai_summary
            summary.summary_length = len(ai_summary)
            summary.status = 'completed'
            summary.completed_at = datetime.utcnow()
            
            # Adicionar uso diário
            current_user.add_summary_usage()
            
            db.session.commit()
            
            return jsonify({
                'success': True,
                'summary_id': summary.id,
                'title': video.title,
                'summary': ai_summary,
                'transcript': transcript,
                'transcript_paragraphs': paragraphs,
                'transcript_highlights': extract_transcript_highlights(transcript),
                'duration': video.duration
            })
        
        except Exception as e:
            summary.status = 'failed'
            summary.error_message = str(e)
            db.session.commit()
            return jsonify({'error': f'Erro ao processar vídeo: {str(e)}'}), 500
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/summaries', methods=['GET'])
@login_required
def get_summaries():
    summaries = Summary.query.filter_by(user_id=current_user.id).order_by(
        Summary.created_at.desc()
    ).all()
    
    data = []
    for summary in summaries:
        video = Video.query.get(summary.video_id)
        data.append({
            'id': summary.id,
            'title': video.title,
            'url': video.url,
            'summary': summary.summary,
            'status': summary.status,
            'created_at': summary.created_at.strftime('%d/%m/%Y %H:%M'),
            'duration': video.duration
        })
    
    return jsonify(data)

@api_bp.route('/summary/<int:summary_id>', methods=['GET'])
@login_required
def get_summary(summary_id):
    summary = Summary.query.get_or_404(summary_id)
    
    if summary.user_id != current_user.id:
        return jsonify({'error': 'Não autorizado'}), 403
    
    video = Video.query.get(summary.video_id)
    paragraphs = parse_transcript_segments(summary.transcript_segments, summary.original_transcript)

    return jsonify({
        'id': summary.id,
        'title': video.title,
        'url': video.url,
        'summary': summary.summary,
        'transcript': summary.original_transcript,
        'transcript_paragraphs': paragraphs,
        'transcript_highlights': extract_transcript_highlights(summary.original_transcript),
        'status': summary.status,
        'created_at': summary.created_at.strftime('%d/%m/%Y %H:%M'),
        'duration': video.duration
    })

@api_bp.route('/delete/<int:summary_id>', methods=['DELETE'])
@login_required
def delete_summary(summary_id):
    summary = Summary.query.get_or_404(summary_id)
    
    if summary.user_id != current_user.id:
        return jsonify({'error': 'Não autorizado'}), 403
    
    db.session.delete(summary)
    db.session.commit()
    
    return jsonify({'success': True})

# ==================== ROTAS DE PAGAMENTO ====================

@payment_bp.route('/upgrade', methods=['GET', 'POST'])
@login_required
def upgrade():
    if current_user.plan == 'premium':
        return redirect(url_for('main.dashboard'))
    
    try:
        stripe.api_key = current_app.config['STRIPE_SECRET_KEY']
        
        # Criar sessão de checkout
        session_checkout = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'usd',
                    'unit_amount': 200,  # US$2.00
                    'product_data': {
                        'name': 'Art.Resumos Premium - Mensal',
                        'description': 'Acesso ilimitado a resumos de vídeos com IA'
                    }
                },
                'quantity': 1
            }],
            mode='payment',
            success_url=url_for('payment.success', _external=True),
            cancel_url=url_for('payment.cancel', _external=True),
            customer_email=current_user.email
        )
        
        return redirect(session_checkout.url)
    
    except Exception as e:
        return render_template('payment_error.html', error=str(e))

@payment_bp.route('/success')
@login_required
def success():
    # Atualizar plano do usuário
    current_user.plan = 'premium'
    current_user.paid_until = datetime.utcnow() + timedelta(days=30)
    db.session.commit()
    
    return render_template('payment_success.html')

@payment_bp.route('/cancel')
@login_required
def cancel():
    return render_template('payment_cancel.html')

@payment_bp.route('/webhook', methods=['POST'])
def webhook():
    payload = request.get_data(as_text=True)
    sig_header = request.headers.get('Stripe-Signature')
    
    try:
        stripe.api_key = current_app.config['STRIPE_SECRET_KEY']
        event = stripe.Webhook.construct_event(
            payload, sig_header, current_app.config['STRIPE_WEBHOOK_SECRET']
        )
    except ValueError:
        return 'Invalid payload', 400
    except stripe.error.SignatureVerificationError:
        return 'Invalid signature', 400
    
    # Processar evento
    if event['type'] == 'payment_intent.succeeded':
        payment_intent = event['data']['object']
        # Processar pagamento bem-sucedido
    
    return 'OK', 200
