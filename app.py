from flask import Flask, render_template
from config import Config
from models import db, Customer
from routes import api_bp

def create_app():
    """Factory funkcja do tworzenia aplikacji Flask"""
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Inicjalizacja bazy danych
    db.init_app(app)
    
    # Rejestracja blueprintów
    app.register_blueprint(api_bp)
    
    # Tworzenie tabel
    with app.app_context():
        db.create_all()
    
    # Strona główna
    @app.route('/')
    def index():
        return render_template('index.html')
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=6000)
