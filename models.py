from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    """Model użytkownika"""
    __tablename__ = 'users'
    
    id = db.Column(db.String(32), primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(64), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relacja z klientami
    customers = db.relationship('Customer', backref='owner', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class Customer(db.Model):
    """Model klienta"""
    __tablename__ = 'customers'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(32), db.ForeignKey('users.id'), nullable=False)
    imie = db.Column(db.String(100), nullable=False)
    nazwisko = db.Column(db.String(100), nullable=False)
    miejscowosc = db.Column(db.String(100), nullable=False)
    ulica_nr = db.Column(db.String(200))
    telefon = db.Column(db.String(20))
    notatka = db.Column(db.Text)
    status = db.Column(db.String(50), default='mozliwa_kolejna_proba')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'imie': self.imie,
            'nazwisko': self.nazwisko,
            'miejscowosc': self.miejscowosc,
            'ulica_nr': self.ulica_nr,
            'telefon': self.telefon,
            'notatka': self.notatka,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
