from flask import Flask, render_template
from config import Config
from models import db, Customer, User
from routes import api_bp
from auth import init_auth_routes

def create_app():
    """Factory funkcja do tworzenia aplikacji Flask"""
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Inicjalizacja bazy danych
    db.init_app(app)
    
    # Rejestracja blueprintów
    app.register_blueprint(api_bp)
    
    # Inicjalizacja autentykacji
    init_auth_routes(app)
    
    # Tworzenie tabel
    with app.app_context():
        db.create_all()
    
    # Strona główna
    @app.route('/')
    def index():
        return render_template('index.html')
    
    # Strona logowania
    @app.route('/login')
    def login_page():
        return render_template('login.html')
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)
