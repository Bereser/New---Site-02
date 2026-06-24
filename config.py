import os
from datetime import timedelta

class Config:
    # Flask Config
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'sua-chave-secreta-super-segura-aqui-2024'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///videos_ai.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Session
    PERMANENT_SESSION_LIFETIME = timedelta(days=30)
    SESSION_COOKIE_SECURE = os.environ.get('FLASK_ENV') == 'production'
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # APIs
    GOOGLE_API_KEY = os.environ.get('GOOGLE_API_KEY') or 'sua-chave-google-aqui'
    STRIPE_PUBLIC_KEY = os.environ.get('STRIPE_PUBLIC_KEY') or 'pk_test_sua_chave_publica'
    STRIPE_SECRET_KEY = os.environ.get('STRIPE_SECRET_KEY') or 'sk_test_sua_chave_secreta'
    STRIPE_WEBHOOK_SECRET = os.environ.get('STRIPE_WEBHOOK_SECRET') or 'whsec_test'
    
    # Pricing
    FREE_PLAN_LIMIT = 3  # 3 vídeos por dia no plano gratuito
    PAID_PLAN_PRICE = 1999  # R$19,99 em centavos (ou US$2.00)
    PAID_PLAN_INTERVAL = 'month'
    
    # Limites
    MAX_VIDEO_LENGTH = 180  # 3 horas em minutos
    MAX_SUMMARY_LENGTH = 2000  # caracteres
    SITE_NAME = 'Art.Resumos'
    # Optional proxy for YouTube requests (format: http://user:pass@host:port)
    YT_PROXY = os.environ.get('YT_PROXY') or None
    # Optional Netscape cookies file exported from browser for YouTube
    YT_COOKIES_FILE = os.environ.get('YT_COOKIES_FILE') or None
