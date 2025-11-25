"""
Skrypt do migracji bazy danych - dodanie kolumny webauthn_credentials
"""
import sqlite3
import os

def migrate_database():
    db_path = 'instance/customers.db'
    
    if not os.path.exists(db_path):
        print("❌ Baza danych nie istnieje")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Sprawdź czy kolumna już istnieje
    cursor.execute("PRAGMA table_info(users)")
    columns = [column[1] for column in cursor.fetchall()]
    
    if 'webauthn_credentials' in columns:
        print("✓ Kolumna webauthn_credentials już istnieje")
    else:
        print("Dodawanie kolumny webauthn_credentials...")
        cursor.execute("ALTER TABLE users ADD COLUMN webauthn_credentials TEXT")
        conn.commit()
        print("✓ Kolumna webauthn_credentials dodana")
    
    conn.close()
    print("\n✓ Migracja zakończona pomyślnie")

if __name__ == "__main__":
    migrate_database()
