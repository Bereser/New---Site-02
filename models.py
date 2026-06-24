from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
import secrets

db = SQLAlchemy()

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    full_name = db.Column(db.String(120))
    
    # Plano
    plan = db.Column(db.String(20), default='free')  # 'free' ou 'premium'
    stripe_customer_id = db.Column(db.String(255))
    stripe_subscription_id = db.Column(db.String(255))
    paid_until = db.Column(db.DateTime)
    
    # Status
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    videos = db.relationship('Video', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    summaries = db.relationship('Summary', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    usage = db.relationship('DailyUsage', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def get_daily_usage(self):
        today = datetime.utcnow().date()
        usage = DailyUsage.query.filter_by(
            user_id=self.id,
            date=today
        ).first()
        return usage.count if usage else 0
    
    def can_summarize(self):
        if self.plan == 'premium':
            return True
        
        daily_usage = self.get_daily_usage()
        return daily_usage < 3  # Limite de 3 por dia para plano free
    
    def add_summary_usage(self):
        today = datetime.utcnow().date()
        usage = DailyUsage.query.filter_by(
            user_id=self.id,
            date=today
        ).first()
        
        if not usage:
            usage = DailyUsage(user_id=self.id, date=today, count=1)
        else:
            usage.count += 1
        
        db.session.add(usage)
        db.session.commit()
    
    def is_premium(self):
        if self.plan != 'premium':
            return False
        if self.paid_until and self.paid_until > datetime.utcnow():
            return True
        return False

class Video(db.Model):
    __tablename__ = 'videos'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    url = db.Column(db.String(500), nullable=False)
    title = db.Column(db.String(255))
    duration = db.Column(db.Integer)  # em segundos
    thumbnail = db.Column(db.String(500))
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    summaries = db.relationship('Summary', backref='video', lazy='dynamic', cascade='all, delete-orphan')

class Summary(db.Model):
    __tablename__ = 'summaries'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    video_id = db.Column(db.Integer, db.ForeignKey('videos.id'), nullable=False)
    
    original_transcript = db.Column(db.Text)
    transcript_segments = db.Column(db.Text)
    summary = db.Column(db.Text, default='', nullable=False)  # Valor padrão vazio
    summary_length = db.Column(db.Integer, default=0)
    
    status = db.Column(db.String(20), default='processing')  # 'processing', 'completed', 'failed'
    error_message = db.Column(db.String(500))
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime)

class DailyUsage(db.Model):
    __tablename__ = 'daily_usage'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    count = db.Column(db.Integer, default=0)
    
    __table_args__ = (db.UniqueConstraint('user_id', 'date', name='unique_user_date'),)

class SubscriptionPlan(db.Model):
    __tablename__ = 'subscription_plans'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    price = db.Column(db.Float, nullable=False)
    currency = db.Column(db.String(10), default='BRL')
    max_videos_per_day = db.Column(db.Integer, default=-1)  # -1 = ilimitado
    description = db.Column(db.Text)
    stripe_price_id = db.Column(db.String(255))
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
