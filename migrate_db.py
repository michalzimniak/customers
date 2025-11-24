"""
Skrypt migracji bazy danych - dodanie kolumny telefon
"""
import sqlite3
import os

db_path = 'customers.db'

if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Sprawdź czy kolumna już istnieje
        cursor.execute("PRAGMA table_info(customer)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'telefon' not in columns:
            print("Dodawanie kolumny 'telefon' do tabeli customer...")
            cursor.execute("ALTER TABLE customer ADD COLUMN telefon VARCHAR(20)")
            conn.commit()
            print("✓ Kolumna 'telefon' została dodana!")
        else:
            print("Kolumna 'telefon' już istnieje.")
            
    except sqlite3.Error as e:
        print(f"Błąd: {e}")
        conn.rollback()
    finally:
        conn.close()
else:
    print(f"Baza danych '{db_path}' nie istnieje. Zostanie utworzona przy pierwszym uruchomieniu app.py")
