# Rejestr Klientów

Aplikacja webowa do zarządzania rejestrem klientów, zbudowana z użyciem Flask (Python) i Bootstrap.

## Funkcjonalności

- 📋 Przeglądanie listy klientów w tabeli
- ➕ Dodawanie nowych klientów przez modal
- ✏️ Edycja istniejących klientów
- 🗑️ Usuwanie klientów
- 👁️ Szczegółowy podgląd danych klienta po kliknięciu
- 🎨 Kolorowe statusy klientów:
  - 🟡 Żółty - Możliwa kolejna próba
  - 🔴 Czerwony - Nie rokujący
  - 🟢 Zielony - Zadowolony
- 📱 Responsywny design - działa na telefonach
- 🌓 Tryb ciemny - automatyczne dostosowanie do ustawień systemowych
- 🔍 Wyszukiwanie i filtrowanie po nazwisku, statusie i miejscowości
- 📞 Szybkie dzwonienie - kliknij numer telefonu
- 🗺️ Nawigacja GPS - przycisk nawigacji do adresu klienta
- 📲 Instalacja jako aplikacja - możliwość zainstalowania na telefonie (PWA)

## Struktura danych klienta

- Imię
- Nazwisko
- Miejscowość
- Ulica i nr domu/mieszkania
- Telefon
- Notatka
- Status (z kolorowym oznaczeniem)

## Struktura projektu

```
Customers/
├── app.py              # Główna aplikacja Flask (Factory Pattern)
├── config.py           # Konfiguracja aplikacji
├── models.py           # Modele bazy danych (Customer)
├── routes.py           # Endpointy API (Blueprint)
├── requirements.txt    # Zależności Python
├── templates/
│   └── index.html     # Interfejs użytkownika
└── customers.db       # Baza danych SQLite (tworzona automatycznie)
```

## Instalacja i uruchomienie

### 1. Zainstaluj zależności

```powershell
pip install -r requirements.txt
```

### 2. Uruchom aplikację

```powershell
python app.py
```

### 3. Otwórz przeglądarkę

Przejdź do adresu: http://localhost:6000

### 4. Zainstaluj jako aplikację (opcjonalnie)

**Na telefonie:**
1. Otwórz aplikację w przeglądarce Chrome/Safari
2. Kliknij menu (⋮) i wybierz "Dodaj do ekranu głównego" lub "Zainstaluj aplikację"
3. Aplikacja pojawi się na ekranie głównym jak normalna aplikacja

**Na komputerze:**
1. W Chrome kliknij ikonę instalacji w pasku adresu (⊕)
2. Lub menu (⋮) → "Zainstaluj aplikację"

## Technologie

- **Backend**: Python, Flask, SQLAlchemy
- **Frontend**: HTML5, Bootstrap 5, JavaScript (Vanilla)
- **Baza danych**: SQLite
- **Ikony**: Bootstrap Icons
- **Architektura**: Factory Pattern, Blueprints

## API Endpoints

- `GET /api/customers` - Lista wszystkich klientów
- `GET /api/customers/<id>` - Szczegóły klienta
- `POST /api/customers` - Dodaj nowego klienta
- `PUT /api/customers/<id>` - Aktualizuj klienta
- `DELETE /api/customers/<id>` - Usuń klienta

## Obsługa aplikacji

1. **Dodawanie klienta**: Kliknij przycisk "Dodaj klienta" lub FAB (na mobile)
2. **Edycja**: Kliknij ikonę ołówka przy wybranym kliencie lub otwórz szczegóły i kliknij "Edytuj"
3. **Usuwanie**: Kliknij ikonę kosza przy wybranym kliencie
4. **Podgląd szczegółów**: Kliknij na dowolny wiersz w tabeli
5. **Dzwonienie**: Kliknij numer telefonu lub ikonę telefonu

## Funkcje mobilne

- Floating Action Button (FAB) w prawym dolnym rogu
- Ukryte kolumny na małych ekranach
- Przyciski akcji w modalach zamiast w tabeli
- Ukryty nagłówek tabeli dla lepszego wykorzystania przestrzeni
- Automatyczny tryb ciemny zgodny z systemem

## Uwagi

- Baza danych jest automatycznie tworzona przy pierwszym uruchomieniu
- Wszystkie operacje są wykonywane dynamicznie bez przeładowywania strony
- Aplikacja jest w pełni responsywna i działa na urządzeniach mobilnych
- Tryb ciemny/jasny dostosowuje się do ustawień systemowych
