from flask import Flask, render_template, request, redirect, url_for, jsonify, session
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_wtf.csrf import CSRFProtect
from config import Config
from models import db, User, Video, Summary, DailyUsage, SubscriptionPlan
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

# Inicializar Flask
app = Flask(__name__)
app.config.from_object(Config)

# Inicializar extensões
db.init_app(app)
csrf = CSRFProtect(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.login'
login_manager.login_message = 'Por favor, faça login para continuar.'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Importar blueprints
from routes import main_bp, auth_bp, api_bp, payment_bp

app.register_blueprint(main_bp)
app.register_blueprint(auth_bp)
app.register_blueprint(api_bp)
app.register_blueprint(payment_bp)

# Criar tabelas e migrar colunas novas
with app.app_context():
    from sqlalchemy import inspect, text
    db.create_all()
    inspector = inspect(db.engine)
    if 'summaries' in inspector.get_table_names():
        columns = {col['name'] for col in inspector.get_columns('summaries')}
        if 'transcript_segments' not in columns:
            with db.engine.begin() as connection:
                connection.execute(text('ALTER TABLE summaries ADD COLUMN transcript_segments TEXT'))

@app.context_processor
def inject_globals():
    return {
        'current_user': current_user,
        'site_name': app.config.get('SITE_NAME', 'Art.Resumos'),
    }

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(e):
    db.session.rollback()
    return render_template('500.html'), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
