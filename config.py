import os
import secrets

class Config:
    """Konfiguracja aplikacji"""
    SQLALCHEMY_DATABASE_URI = 'sqlite:///customers.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.environ.get('SECRET_KEY') or secrets.token_hex(32)
    SESSION_COOKIE_SECURE = False  # Ustaw True w produkcji z HTTPS
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    PERMANENT_SESSION_LIFETIME = 86400  # 24 godziny
    DEBUG = True
