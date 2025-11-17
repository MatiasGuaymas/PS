import jwt
from datetime import datetime, timedelta
from flask import current_app
from functools import wraps
from flask import request, jsonify

def create_access_token(user_id: int, email: str, role: str = None, is_admin: bool = False):
    """Crea un token de acceso JWT"""
    payload = {
        'user_id': user_id,
        'email': email,
        'role': role,
        'is_admin': is_admin,
        'exp': datetime.utcnow() + current_app.config['JWT_ACCESS_TOKEN_EXPIRES'],
        'iat': datetime.utcnow(),
        'type': 'access'
    }
    
    token = jwt.encode(
        payload,
        current_app.config['JWT_SECRET_KEY'],
        algorithm=current_app.config['JWT_ALGORITHM']
    )
    
    return token


def create_refresh_token(user_id: int):
    """Crea un token de refresh JWT"""
    payload = {
        'user_id': user_id,
        'exp': datetime.utcnow() + current_app.config['JWT_REFRESH_TOKEN_EXPIRES'],
        'iat': datetime.utcnow(),
        'type': 'refresh'
    }
    
    token = jwt.encode(
        payload,
        current_app.config['JWT_SECRET_KEY'],
        algorithm=current_app.config['JWT_ALGORITHM']
    )
    
    return token


def decode_token(token: str):
    """Decodifica y valida un token JWT"""
    try:
        payload = jwt.decode(
            token,
            current_app.config['JWT_SECRET_KEY'],
            algorithms=[current_app.config['JWT_ALGORITHM']]
        )
        return payload
    except jwt.ExpiredSignatureError:
        return None  # Token expirado
    except jwt.InvalidTokenError:
        return None  # Token inválido


def get_token_from_request():
    """Extrae el token del header Authorization o de las cookies"""
    # Intentar obtener del header Authorization
    auth_header = request.headers.get('Authorization')
    if auth_header and auth_header.startswith('Bearer '):
        return auth_header.split(' ')[1]
    
    # Intentar obtener de las cookies
    token = request.cookies.get('access_token')
    if token:
        return token
    
    return None


def jwt_required(fn):
    """Decorador para proteger rutas que requieren autenticación JWT"""
    @wraps(fn)
    def wrapper(*args, **kwargs):
        token = get_token_from_request()
        
        if not token:
            return jsonify({'error': 'Token no proporcionado'}), 401
        
        payload = decode_token(token)
        
        if not payload:
            return jsonify({'error': 'Token inválido o expirado'}), 401
        
        if payload.get('type') != 'access':
            return jsonify({'error': 'Tipo de token inválido'}), 401
        
        # Agregar datos del usuario al request
        request.current_user = {
            'user_id': payload.get('user_id'),
            'email': payload.get('email'),
            'role': payload.get('role'),
            'is_admin': payload.get('is_admin', False)
        }
        
        return fn(*args, **kwargs)
    
    return wrapper
