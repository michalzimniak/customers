from flask import Blueprint, render_template, request, jsonify, session
from models import db, Customer
import requests

api_bp = Blueprint('api', __name__, url_prefix='/api')

def login_required(f):
    """Dekorator wymagający zalogowania"""
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'error': 'Unauthorized', 'redirect': '/login'}), 401
        return f(*args, **kwargs)
    return decorated_function

# Lista najpopularniejszych polskich miejscowości
POLISH_CITIES = [
    'Warszawa', 'Kraków', 'Łódź', 'Wrocław', 'Poznań', 'Gdańsk', 'Szczecin', 'Bydgoszcz',
    'Lublin', 'Białystok', 'Katowice', 'Gdynia', 'Częstochowa', 'Radom', 'Sosnowiec',
    'Toruń', 'Kielce', 'Rzeszów', 'Gliwice', 'Zabrze', 'Olsztyn', 'Bielsko-Biała',
    'Bytom', 'Zielona Góra', 'Rybnik', 'Ruda Śląska', 'Opole', 'Tychy', 'Gorzów Wielkopolski',
    'Elbląg', 'Płock', 'Dąbrowa Górnicza', 'Wałbrzych', 'Włocławek', 'Tarnów', 'Chorzów',
    'Koszalin', 'Kalisz', 'Legnica', 'Grudziądz', 'Jaworzno', 'Słupsk', 'Jastrzębie-Zdrój',
    'Nowy Sącz', 'Jelenia Góra', 'Siedlce', 'Mysłowice', 'Konin', 'Piła', 'Piotrków Trybunalski',
    'Inowrocław', 'Lubin', 'Ostrów Wielkopolski', 'Gniezno', 'Suwałki', 'Głogów', 'Chełm',
    'Tomaszów Mazowiecki', 'Zamość', 'Przemyśl', 'Stalowa Wola', 'Kędzierzyn-Koźle', 
    'Leszno', 'Łomża', 'Żory', 'Mielec', 'Tarnobrzeg', 'Pabianice', 'Ełk', 'Tczew',
    'Świdnica', 'Będzin', 'Zgierz', 'Racibórz', 'Pruszków', 'Legionowo', 'Ostrołęka',
    'Skierniewice', 'Starachowice', 'Ostrowiec Świętokrzyski', 'Puławy', 'Starogard Gdański',
    'Wejherowo', 'Radomsko', 'Zawiercie', 'Krosno', 'Skarżysko-Kamienna', 'Biała Podlaska'
]

# API - Lista wszystkich klientów
@api_bp.route('/customers', methods=['GET'])
@login_required
def get_customers():
    customers = Customer.query.order_by(Customer.nazwisko, Customer.imie).all()
    return jsonify([customer.to_dict() for customer in customers])

# API - Szczegóły klienta
@api_bp.route('/customers/<int:customer_id>', methods=['GET'])
@login_required
def get_customer(customer_id):
    customer = Customer.query.get_or_404(customer_id)
    return jsonify(customer.to_dict())

# API - Dodanie nowego klienta
@api_bp.route('/customers', methods=['POST'])
@login_required
def add_customer():
    data = request.get_json()
    
    new_customer = Customer(
        imie=data.get('imie'),
        nazwisko=data.get('nazwisko'),
        miejscowosc=data.get('miejscowosc'),
        ulica_nr=data.get('ulica_nr'),
        telefon=data.get('telefon'),
        notatka=data.get('notatka'),
        status=data.get('status', 'mozliwa_kolejna_proba')
    )
    
    db.session.add(new_customer)
    db.session.commit()
    
    return jsonify(new_customer.to_dict()), 201

# API - Aktualizacja klienta
@api_bp.route('/customers/<int:customer_id>', methods=['PUT'])
@login_required
def update_customer(customer_id):
    customer = Customer.query.get_or_404(customer_id)
    data = request.get_json()
    
    customer.imie = data.get('imie', customer.imie)
    customer.nazwisko = data.get('nazwisko', customer.nazwisko)
    customer.miejscowosc = data.get('miejscowosc', customer.miejscowosc)
    customer.ulica_nr = data.get('ulica_nr', customer.ulica_nr)
    customer.telefon = data.get('telefon', customer.telefon)
    customer.notatka = data.get('notatka', customer.notatka)
    customer.status = data.get('status', customer.status)
    
    db.session.commit()
    
    return jsonify(customer.to_dict())

# API - Usunięcie klienta
@api_bp.route('/customers/<int:customer_id>', methods=['DELETE'])
@login_required
def delete_customer(customer_id):
    customer = Customer.query.get_or_404(customer_id)
    db.session.delete(customer)
    db.session.commit()
    
    return jsonify({'message': 'Klient usunięty'}), 200

# API - Geoportal - Wyszukiwanie miejscowości
@api_bp.route('/geocode/cities', methods=['GET'])
def search_cities():
    query = request.args.get('q', '').strip()
    
    if not query or len(query) < 2:
        return jsonify([])
    
    query_lower = query.lower()
    
    # Najpierw szukaj w lokalnej liście polskich miast
    local_matches = [
        {'name': city, 'display': city}
        for city in POLISH_CITIES
        if query_lower in city.lower()
    ]
    
    # Jeśli znaleziono wyniki lokalnie, zwróć je
    if local_matches:
        return jsonify(local_matches[:10])
    
    # Jeśli nie znaleziono lokalnie, użyj Nominatim jako backup
    try:
        url = "https://nominatim.openstreetmap.org/search"
        params = {
            'q': f"{query}, Poland",
            'format': 'json',
            'limit': 10,
            'addressdetails': 1
        }
        headers = {
            'User-Agent': 'CustomerRegistry/1.0'
        }
        
        response = requests.get(url, params=params, headers=headers, timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            
            cities = []
            seen = set()
            
            for item in data:
                if not isinstance(item, dict):
                    continue
                
                address = item.get('address', {})
                
                # Próbuj różne pola dla nazwy miejscowości
                city = (address.get('city') or 
                       address.get('town') or 
                       address.get('village') or 
                       address.get('municipality') or
                       item.get('name', ''))
                
                state = address.get('state', '')
                
                if city and city not in seen:
                    display = city
                    if state:
                        display = f"{city}, {state}"
                    
                    cities.append({
                        'name': city,
                        'display': display
                    })
                    seen.add(city)
            
            return jsonify(cities[:10])
        else:
            return jsonify([])
            
    except Exception as e:
        print(f"Błąd Nominatim API: {e}")
        return jsonify([])

# API - Geoportal - Wyszukiwanie ulic w miejscowości
@api_bp.route('/geocode/streets', methods=['GET'])
def search_streets():
    city = request.args.get('city', '').strip()
    query = request.args.get('q', '').strip()
    
    if not city or not query or len(query) < 2:
        return jsonify([])
    
    try:
        # Nominatim API - wyszukiwanie ulic
        url = "https://nominatim.openstreetmap.org/search"
        params = {
            'q': f"{query}, {city}, Poland",
            'format': 'json',
            'limit': 15,
            'addressdetails': 1
        }
        headers = {
            'User-Agent': 'CustomerRegistry/1.0'
        }
        
        response = requests.get(url, params=params, headers=headers, timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            
            streets = []
            seen = set()
            
            for item in data:
                if not isinstance(item, dict):
                    continue
                
                address = item.get('address', {})
                street = address.get('road', '')
                
                if street and street not in seen:
                    streets.append({
                        'name': street,
                        'display': street
                    })
                    seen.add(street)
            
            return jsonify(streets[:15])
        else:
            return jsonify([])
            
    except Exception as e:
        print(f"Błąd Nominatim API (ulice): {e}")
        return jsonify([])
