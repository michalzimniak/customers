class Config:
    """Konfiguracja aplikacji"""
    SQLALCHEMY_DATABASE_URI = 'sqlite:///customers.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = 'your-secret-key-here-change-in-production'
    DEBUG = True
