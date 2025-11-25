"""
Skrypt migracji bazy danych - dodanie tabeli users i powiązanie klientów z użytkownikami.
UWAGA: Usuwa starą bazę i tworzy nową!
"""

import os
from app import create_app
from models import db

def migrate_database():
    app = create_app()
    
    with app.app_context():
        # Sprawdź czy istnieje stara baza
        db_path = 'customers.db'
        if os.path.exists(db_path):
            print(f"Znaleziono starą bazę danych: {db_path}")
            response = input("UWAGA: Migracja usunie wszystkie dane! Kontynuować? (tak/nie): ")
            
            if response.lower() != 'tak':
                print("Migracja anulowana.")
                return
            
            # Usuń starą bazę
            os.remove(db_path)
            print(f"Usunięto starą bazę danych.")
        
        # Utwórz nowe tabele
        db.create_all()
        print("Utworzono nowe tabele z powiązaniem użytkownik-klient.")
        print("\nMigracja zakończona pomyślnie!")
        print("Teraz każdy użytkownik będzie miał swoją oddzielną bazę klientów.")

if __name__ == '__main__':
    migrate_database()
