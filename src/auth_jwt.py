"""
🔐 JWT AUTHENTICATION MODULE - BizFlow Studio
==============================================
Módulo para manejar autenticación con JSON Web Tokens

INSTALACIÓN:
    pip install PyJWT

UBICACIÓN:
    Guardar como: src/auth_jwt.py

VARIABLES DE ENTORNO (Render):
    JWT_SECRET_KEY=tu-clave-secreta-aqui
    JWT_EXPIRATION_HOURS=24
"""

import jwt
import os
from datetime import datetime, timedelta
from flask import request
import logging

logger = logging.getLogger(__name__)

# ==========================================
# CONFIGURACIÓN
# ==========================================

# Clave secreta - CAMBIAR EN PRODUCCIÓN
# Generar con: python -c "import secrets; print(secrets.token_hex(32))"
JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'bizflow-dev-key-change-in-production-2026')
JWT_ALGORITHM = 'HS256'
JWT_EXPIRATION_HOURS = int(os.environ.get('JWT_EXPIRATION_HOURS', 24))
JWT_REFRESH_DAYS = 7


# ==========================================
# CREAR TOKENS
# ==========================================

def create_token(user_id, user_email=None, user_name=None):
    """
    Crea un par de tokens JWT (access + refresh).
    
    Args:
        user_id: ID del usuario
        user_email: Email del usuario
        user_name: Nombre del usuario
    
    Returns:
        dict con access_token, refresh_token, expires_in
    """
    now = datetime.utcnow()
    
    # Access token (corta duración)
    access_payload = {
        'user_id': user_id,
        'email': user_email,
        'name': user_name,
        'type': 'access',
        'iat': now,
        'exp': now + timedelta(hours=JWT_EXPIRATION_HOURS),
    }
    
    # Refresh token (larga duración)
    refresh_payload = {
        'user_id': user_id,
        'type': 'refresh',
        'iat': now,
        'exp': now + timedelta(days=JWT_REFRESH_DAYS),
    }
    
    access_token = jwt.encode(access_payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    refresh_token = jwt.encode(refresh_payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    
    logger.info(f"🔐 Token JWT creado para user_id={user_id}")
    
    return {
        'access_token': access_token,
        'refresh_token': refresh_token,
        'token_type': 'Bearer',
        'expires_in': JWT_EXPIRATION_HOURS * 3600
    }


# ==========================================
# VERIFICAR TOKENS
# ==========================================

def verify_token(token, token_type='access'):
    """
    Verifica y decodifica un token JWT.
    
    Args:
        token: El token a verificar
        token_type: 'access' o 'refresh'
    
    Returns:
        dict con payload si válido, None si inválido
    """
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        
        if payload.get('type') != token_type:
            logger.warning(f"⚠️ Tipo de token incorrecto: esperado={token_type}")
            return None
        
        return payload
        
    except jwt.ExpiredSignatureError:
        logger.warning("⚠️ Token JWT expirado")
        return None
    except jwt.InvalidTokenError as e:
        logger.warning(f"⚠️ Token JWT inválido: {e}")
        return None


# ==========================================
# EXTRAER TOKEN DE REQUEST
# ==========================================

def get_token_from_request():
    """
    Extrae el token del header Authorization.
    Formato esperado: "Bearer <token>"
    
    Returns:
        str: El token o None
    """
    auth_header = request.headers.get('Authorization', '')
    
    if auth_header.startswith('Bearer '):
        return auth_header[7:]
    
    # Fallback: query param
    return request.args.get('token')


# ==========================================
# OBTENER USER_ID DESDE JWT
# ==========================================

def get_user_id_from_jwt():
    """
    Obtiene el user_id desde el token JWT en el request actual.
    
    Returns:
        int: user_id si el token es válido, None si no
    """
    token = get_token_from_request()
    
    if not token:
        return None
    
    payload = verify_token(token)
    
    if payload:
        return payload.get('user_id')
    
    return None


# ==========================================
# REFRESCAR ACCESS TOKEN
# ==========================================

def refresh_access_token(refresh_token):
    """
    Genera un nuevo access token usando un refresh token válido.
    
    Args:
        refresh_token: El refresh token
    
    Returns:
        dict con nuevos tokens o None si falla
    """
    payload = verify_token(refresh_token, token_type='refresh')
    
    if not payload:
        return None
    
    return create_token(
        user_id=payload['user_id'],
        user_email=payload.get('email'),
        user_name=payload.get('name')
    )