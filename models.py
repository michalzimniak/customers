from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Customer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    imie = db.Column(db.String(100), nullable=False)
    nazwisko = db.Column(db.String(100), nullable=False)
    miejscowosc = db.Column(db.String(100), nullable=False)
    ulica_nr = db.Column(db.String(200))
    telefon = db.Column(db.String(20))
    notatka = db.Column(db.Text)
    status = db.Column(db.String(50), nullable=False)  # 'mozliwa_kolejna_proba', 'nie_rokujacy', 'zadowolony'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
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
