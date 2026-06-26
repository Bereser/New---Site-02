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
    # Optional: directly provide cookies file content via env var (useful on PaaS)
    # If YT_COOKIES_FILE is not set but YT_COOKIES_CONTENT is, write it to a
    # temporary file and point YT_COOKIES_FILE to it.
    YT_COOKIES_CONTENT = os.environ.get('YT_COOKIES_CONTENT') or None
    if not YT_COOKIES_FILE and YT_COOKIES_CONTENT:
        try:
            # prefer writable tmp dir in container
            tmp_path = os.environ.get('YT_COOKIES_PATH') or '/tmp/youtube_cookies.txt'
            with open(tmp_path, 'w', encoding='utf-8') as _f:
                _f.write(YT_COOKIES_CONTENT)
            YT_COOKIES_FILE = tmp_path
        except Exception:
            # if write fails, leave YT_COOKIES_FILE as None
            YT_COOKIES_FILE = None
