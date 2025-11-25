from flask import session, redirect, url_for, request, jsonify
from functools import wraps
import secrets
import base64
import json
from datetime import datetime
import hashlib
from models import db, User

def hash_password(password):
    """Hashuj hasło"""
    return hashlib.sha256(password.encode()).hexdigest()

def get_user_credentials(user):
    """Pobierz credentials użytkownika z bazy danych"""
    if user.webauthn_credentials:
        return json.loads(user.webauthn_credentials)
    return {}

def save_user_credential(user, credential_id, credential_data):
    """Zapisz credential użytkownika do bazy danych"""
    credentials = get_user_credentials(user)
    credentials[credential_id] = credential_data
    user.webauthn_credentials = json.dumps(credentials)
    db.session.commit()

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'error': 'Unauthorized'}), 401
        return f(*args, **kwargs)
    return decorated_function

def init_auth_routes(app):
    """Inicjalizacja tras autentykacji"""
    
    # ============ Tradycyjne logowanie hasłem ============
    
    @app.route('/auth/register/password', methods=['POST'])
    def register_password():
        """Rejestracja z hasłem"""
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            return jsonify({'error': 'Username and password required'}), 400
        
        # Sprawdź czy użytkownik już istnieje
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            return jsonify({'error': 'Username already exists'}), 400
        
        # Utwórz nowego użytkownika
        user_id = secrets.token_hex(16)
        new_user = User(
            id=user_id,
            username=username,
            password_hash=hash_password(password)
        )
        
        db.session.add(new_user)
        db.session.commit()
        
        # Zaloguj użytkownika
        session['user_id'] = user_id
        session['username'] = username
        
        return jsonify({'success': True, 'username': username})
    
    @app.route('/auth/login/password', methods=['POST'])
    def login_password():
        """Logowanie z hasłem"""
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            return jsonify({'error': 'Username and password required'}), 400
        
        # Sprawdź użytkownika
        user = User.query.filter_by(username=username).first()
        if not user or not user.password_hash:
            return jsonify({'error': 'Invalid credentials'}), 401
        
        # Sprawdź hasło
        if user.password_hash != hash_password(password):
            return jsonify({'error': 'Invalid credentials'}), 401
        
        # Zaloguj użytkownika
        session['user_id'] = user.id
        session['username'] = user.username
        
        return jsonify({'success': True, 'username': user.username})
    
    # ============ WebAuthn (biometria) ============
    
    @app.route('/auth/register/start', methods=['POST'])
    def register_start():
        """Rozpocznij rejestrację z WebAuthn"""
        data = request.get_json()
        username = data.get('username')
        
        if not username:
            return jsonify({'error': 'Username required'}), 400
        
        # Generuj challenge
        challenge = secrets.token_bytes(32)
        user_id = secrets.token_bytes(16)
        
        # Zapisz tymczasowo
        session['registration_challenge'] = base64.b64encode(challenge).decode()
        session['registration_username'] = username
        session['registration_user_id'] = base64.b64encode(user_id).decode()
        
        # Utwórz użytkownika w bazie (bez hasła, tylko dla WebAuthn)
        new_user = User(
            id=base64.b64encode(user_id).decode(),
            username=username,
            password_hash=None
        )
        db.session.add(new_user)
        db.session.commit()
        
        # Opcje dla WebAuthn
        options = {
            'challenge': base64.b64encode(challenge).decode(),
            'rp': {
                'name': 'Rejestr Klientów',
                'id': request.host.split(':')[0]
            },
            'user': {
                'id': base64.b64encode(user_id).decode(),
                'name': username,
                'displayName': username
            },
            'pubKeyCredParams': [
                {'type': 'public-key', 'alg': -7},  # ES256
                {'type': 'public-key', 'alg': -257}  # RS256
            ],
            'authenticatorSelection': {
                'authenticatorAttachment': 'platform',  # Preferuj biometrię wbudowaną
                'requireResidentKey': False,
                'userVerification': 'preferred'
            },
            'timeout': 60000,
            'attestation': 'none'
        }
        
        return jsonify(options)
    
    @app.route('/auth/register/finish', methods=['POST'])
    def register_finish():
        """Zakończ rejestrację z WebAuthn"""
        data = request.get_json()
        username = session.get('registration_username')
        user_id = session.get('registration_user_id')
        
        if not username or not user_id:
            return jsonify({'error': 'Registration not started'}), 400
        
        # Pobierz użytkownika z bazy
        user = User.query.filter_by(id=user_id).first()
        if not user:
            return jsonify({'error': 'User not found'}), 400
        
        # Zapisz credential do bazy danych
        credential_id = data.get('id')
        credential_data = {
            'user_id': user_id,
            'public_key': data.get('response', {}).get('attestationObject'),
            'counter': 0
        }
        save_user_credential(user, credential_id, credential_data)
        
        # Wyczyść sesję rejestracji
        session.pop('registration_challenge', None)
        session.pop('registration_username', None)
        session.pop('registration_user_id', None)
        
        # Zaloguj użytkownika
        session['user_id'] = user_id
        session['username'] = username
        
        return jsonify({'success': True, 'username': username})
    
    @app.route('/auth/login/start', methods=['POST'])
    def login_start():
        """Rozpocznij logowanie z WebAuthn"""
        challenge = secrets.token_bytes(32)
        session['login_challenge'] = base64.b64encode(challenge).decode()
        
        # Pobierz wszystkie credentials ze wszystkich użytkowników
        all_credentials = []
        users = User.query.all()
        for user in users:
            user_creds = get_user_credentials(user)
            for cred_id in user_creds.keys():
                all_credentials.append({'type': 'public-key', 'id': cred_id})
        
        options = {
            'challenge': base64.b64encode(challenge).decode(),
            'timeout': 60000,
            'rpId': request.host.split(':')[0],
            'allowCredentials': all_credentials,
            'userVerification': 'preferred'
        }
        
        return jsonify(options)
    
    @app.route('/auth/login/finish', methods=['POST'])
    def login_finish():
        """Zakończ logowanie z WebAuthn"""
        data = request.get_json()
        credential_id = data.get('id')
        
        # Wyszukaj credential w bazie danych
        user = None
        for u in User.query.all():
            user_creds = get_user_credentials(u)
            if credential_id in user_creds:
                user = u
                break
        
        if not user:
            return jsonify({'error': 'Credential not found'}), 400
        
        # Zaloguj użytkownika
        session['user_id'] = user.id
        session['username'] = user.username
        
        return jsonify({'success': True, 'username': user.username})
    
    # ============ Dodawanie klucza do istniejącego konta ============
    
    @app.route('/auth/add-key/start', methods=['POST'])
    @login_required
    def add_key_start():
        """Rozpocznij dodawanie klucza biometrycznego do istniejącego konta"""
        user_id = session.get('user_id')
        username = session.get('username')
        
        if not user_id or not username:
            return jsonify({'error': 'Not logged in'}), 401
        
        # Generuj challenge
        challenge = secrets.token_bytes(32)
        
        # Zapisz tymczasowo
        session['add_key_challenge'] = base64.b64encode(challenge).decode()
        
        # Opcje dla WebAuthn
        options = {
            'challenge': base64.b64encode(challenge).decode(),
            'rp': {
                'name': 'Rejestr Klientów',
                'id': request.host.split(':')[0]
            },
            'user': {
                'id': user_id,
                'name': username,
                'displayName': username
            },
            'pubKeyCredParams': [
                {'type': 'public-key', 'alg': -7},  # ES256
                {'type': 'public-key', 'alg': -257}  # RS256
            ],
            'authenticatorSelection': {
                'authenticatorAttachment': 'platform',  # Preferuj biometrię wbudowaną
                'requireResidentKey': False,
                'userVerification': 'preferred'
            },
            'timeout': 60000,
            'attestation': 'none'
        }
        
        return jsonify(options)
    
    @app.route('/auth/add-key/finish', methods=['POST'])
    @login_required
    def add_key_finish():
        """Zakończ dodawanie klucza biometrycznego"""
        data = request.get_json()
        user_id = session.get('user_id')
        username = session.get('username')
        
        if not user_id or not username:
            return jsonify({'error': 'Not logged in'}), 401
        
        # Pobierz użytkownika z bazy
        user = User.query.filter_by(id=user_id).first()
        if not user:
            return jsonify({'error': 'User not found'}), 400
        
        # Zapisz credential do bazy danych
        credential_id = data.get('id')
        credential_data = {
            'user_id': user_id,
            'public_key': data.get('response', {}).get('attestationObject'),
            'counter': 0
        }
        save_user_credential(user, credential_id, credential_data)
        
        # Wyczyść sesję
        session.pop('add_key_challenge', None)
        
        return jsonify({'success': True, 'message': 'Klucz biometryczny dodany pomyślnie'})
    
    @app.route('/auth/logout', methods=['POST'])
    def logout():
        """Wyloguj użytkownika"""
        session.clear()
        return jsonify({'success': True})
    
    @app.route('/auth/status', methods=['GET'])
    def auth_status():
        """Sprawdź status autentykacji"""
        if 'user_id' in session:
            user = User.query.filter_by(id=session.get('user_id')).first()
            if user:
                return jsonify({
                    'authenticated': True,
                    'username': user.username
                })
        return jsonify({'authenticated': False})
