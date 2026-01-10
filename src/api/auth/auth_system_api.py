"""
BizFlow Studio - Sistema de Autenticación Unificado
Backend: Render | Frontend: Firebase
Optimizado para cross-domain con cookies seguras
"""

import logging
import secrets
from datetime import datetime, timedelta
from functools import wraps

from flask import Blueprint, request, jsonify, session, make_response
from flask_login import login_user, logout_user, current_user, login_required
from src.models.database import db
from src.models.usuarios import Usuario

# Configuración de Logger
logger = logging.getLogger(__name__)

# Blueprint de autenticación
auth_bp = Blueprint('auth_system', __name__, url_prefix='/api/auth')

# ==========================================
# DECORADOR DE VALIDACIÓN DE SESIÓN
# ==========================================
def require_active_session(f):
    """
    Decorador que valida la sesión del servidor ANTES de permitir acceso.
    Reemplaza la validación manual de localStorage en cada módulo.
    
    USO:
        @auth_bp.route('/protected-endpoint')
        @require_active_session
        def my_endpoint():
            # current_user ya está validado aquí
            return jsonify({"data": "..."})
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            logger.warning(f"❌ Acceso denegado: Sesión inválida para {request.endpoint}")
            return jsonify({
                "error": "session_expired",
                "message": "Tu sesión ha expirado. Inicia sesión nuevamente.",
                "redirect": "/login.html"
            }), 401
        
        # Validación adicional: Usuario activo
        if not current_user.active:
            logger.warning(f"❌ Usuario inactivo: {current_user.id_usuario}")
            logout_user()
            return jsonify({
                "error": "account_disabled",
                "message": "Tu cuenta ha sido desactivada."
            }), 403
        
        # Log de actividad (útil para auditoría)
        logger.info(f"✅ Acceso autorizado: {current_user.correo} → {request.endpoint}")
        
        return f(*args, **kwargs)
    
    return decorated_function

# ==========================================
# ENDPOINT 1: INICIO DE SESIÓN
# ==========================================
@auth_bp.route('/login', methods=['POST', 'OPTIONS'])
def login():
    """
    Endpoint ÚNICO de autenticación con gestión de cookies seguras.
    
    Request body:
        {
            "correo": "usuario@ejemplo.com",
            "password": "contraseña123"
        }
    
    Response (200):
        {
            "status": "success",
            "session_token": "...",
            "user": {
                "id": 123,
                "nombre": "...",
                "correo": "...",
                ...
            }
        }
    """
    # Manejar preflight CORS
    if request.method == 'OPTIONS':
        return _build_cors_response()
    
    logger.info("--- Nueva solicitud de inicio de sesión ---")
    
    # 1. Verificar si ya está autenticado
    if current_user.is_authenticated:
        logger.info(f"👤 Usuario {current_user.nombre} ya tiene sesión activa")
        return jsonify({
            "status": "already_authenticated",
            "user": _serialize_user(current_user)
        }), 200
    
    # 2. Validar datos de entrada
    data = request.get_json()
    if not data:
        return jsonify({"error": "No se proporcionaron datos"}), 400
    
    correo = data.get('correo', '').strip().lower()
    password = data.get('password', '').strip()
    
    if not correo or not password:
        return jsonify({"error": "Correo y contraseña son requeridos"}), 400
    
    # 3. Control de intentos fallidos (Anti-Brute Force)
    attempts_key = f"login_attempts_{correo}"
    attempts = session.get(attempts_key, 0)
    
    if attempts >= 5:
        logger.warning(f"🚫 Bloqueo por intentos: {correo} ({attempts} intentos)")
        return jsonify({
            "error": "too_many_attempts",
            "message": "Demasiados intentos fallidos. Intenta en 15 minutos."
        }), 429
    
    # 4. Buscar y validar usuario
    try:
        usuario = Usuario.query.filter_by(correo=correo).first()
        
        if not usuario or not usuario.check_password(password):
            session[attempts_key] = attempts + 1
            logger.warning(f"❌ Credenciales incorrectas para: {correo}")
            return jsonify({"error": "Credenciales incorrectas"}), 401
        
        if not usuario.active:
            logger.warning(f"❌ Cuenta inactiva: {correo}")
            return jsonify({
                "error": "account_inactive",
                "message": "Tu cuenta está desactivada. Contacta a soporte."
            }), 403
        
        # 5. CREAR SESIÓN SEGURA
        # remember=True hace que la sesión persista
        login_user(usuario, remember=True, duration=timedelta(days=7))
        
        # Forzar permanencia de sesión
        session.permanent = True
        session[attempts_key] = 0  # Reset de intentos
        
        # Generar token de sesión único (para sincronización adicional)
        session_token = secrets.token_urlsafe(32)
        session['session_token'] = session_token
        session['user_id'] = usuario.id_usuario
        session['login_timestamp'] = datetime.utcnow().isoformat()
        
        # Actualizar último login en DB
        try:
            usuario.last_login = datetime.utcnow()
            db.session.commit()
        except Exception as e:
            logger.error(f"Error actualizando last_login: {e}")
            db.session.rollback()
        
        logger.info(f"✅ Login exitoso: {correo} (ID: {usuario.id_usuario})")
        
        # 6. Respuesta con configuración explícita de cookies
        response_data = {
            "status": "success",
            "message": "Inicio de sesión exitoso",
            "session_token": session_token,
            "user": _serialize_user(usuario)
        }
        
        response = make_response(jsonify(response_data), 200)
        
        # CRÍTICO: Configurar cookie de sesión activa (para detección en frontend)
        response.set_cookie(
            'session_active',
            value='true',
            max_age=7*24*60*60,  # 7 días
            secure=True,         # Solo HTTPS
            httponly=False,      # Permitir acceso desde JS
            samesite='None',     # CRÍTICO para cross-domain
            domain=None          # No restringir dominio
        )
        
        # Headers CORS adicionales
        response.headers['Access-Control-Allow-Credentials'] = 'true'
        
        return response
    
    except Exception as e:
        logger.error(f"🔥 Error crítico en login: {str(e)}", exc_info=True)
        return jsonify({"error": "Error interno del servidor"}), 500

# ==========================================
# ENDPOINT 2: VERIFICACIÓN DE SESIÓN
# ==========================================
@auth_bp.route('/session/verify', methods=['GET', 'OPTIONS'])
@require_active_session
def verify_session():
    """
    Endpoint para verificar si la sesión sigue activa.
    El frontend debe llamarlo periódicamente.
    
    Response (200):
        {
            "status": "active",
            "user": {...},
            "session_token": "..."
        }
    """
    if request.method == 'OPTIONS':
        return _build_cors_response()
    
    return jsonify({
        "status": "active",
        "user": _serialize_user(current_user),
        "session_token": session.get('session_token'),
        "authenticated_at": session.get('login_timestamp')
    }), 200

# ==========================================
# ENDPOINT 3: CIERRE DE SESIÓN
# ==========================================
@auth_bp.route('/logout', methods=['POST', 'GET', 'OPTIONS'])
def logout():
    """
    Cierre de sesión con limpieza completa.
    
    Response (200):
        {
            "status": "success",
            "message": "Sesión cerrada exitosamente"
        }
    """
    if request.method == 'OPTIONS':
        return _build_cors_response()
    
    user_info = None
    if current_user.is_authenticated:
        user_info = f"{current_user.correo} (ID: {current_user.id_usuario})"
        logout_user()
    
    # Limpiar sesión del servidor
    session.clear()
    
    logger.info(f"🚪 Logout exitoso: {user_info or 'Usuario anónimo'}")
    
    # Preparar respuesta
    response = make_response(jsonify({
        "status": "success",
        "message": "Sesión cerrada exitosamente"
    }), 200)
    
    # Eliminar todas las cookies
    cookies_to_clear = ['session_active', 'remember_token', 'session', 'bizflow_session', 'bizflow_remember']
    for cookie_name in cookies_to_clear:
        response.set_cookie(
            cookie_name, 
            '', 
            expires=0, 
            path='/',
            secure=True,
            samesite='None'
        )
    
    # Headers anti-caché
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    response.headers['Access-Control-Allow-Credentials'] = 'true'
    
    return response

# ==========================================
# ENDPOINT 4: PERFIL DE USUARIO
# ==========================================
@auth_bp.route('/user/profile', methods=['GET', 'OPTIONS'])
@require_active_session
def get_user_profile():
    """
    Devuelve el perfil completo del usuario autenticado.
    """
    if request.method == 'OPTIONS':
        return _build_cors_response()
    
    return jsonify({
        "status": "success",
        "user": _serialize_user(current_user, include_sensitive=True)
    }), 200

# ==========================================
# ENDPOINT 5: ESTADO DE SESIÓN (LEGACY)
# ==========================================
@auth_bp.route('/session_status', methods=['GET', 'OPTIONS'])
def session_status():
    """
    Endpoint de compatibilidad con código antiguo.
    Usa /session/verify en su lugar.
    """
    if request.method == 'OPTIONS':
        return _build_cors_response()
    
    if current_user.is_authenticated:
        return jsonify({
            "authenticated": True,
            "user": _serialize_user(current_user)
        }), 200
    
    return jsonify({
        "authenticated": False,
        "error": "Sesión expirada"
    }), 401

# ==========================================
# FUNCIONES AUXILIARES
# ==========================================
def _serialize_user(usuario, include_sensitive=False):
    """
    Serializa un objeto Usuario a JSON de manera consistente.
    Esta es la ÚNICA fuente de verdad para la estructura de datos de usuario.
    
    Args:
        usuario: Objeto Usuario de SQLAlchemy
        include_sensitive: Si True, incluye información sensible
    
    Returns:
        dict: Datos del usuario serializados
    """
    data = {
        "id": usuario.id_usuario,
        "id_usuario": usuario.id_usuario,  # Redundancia para compatibilidad
        "nombre": usuario.nombre,
        "correo": usuario.correo,
        "telefono": usuario.telefono if hasattr(usuario, 'telefono') else None,
        "activo": usuario.active,
        "negocio_id": usuario.negocio_id if hasattr(usuario, 'negocio_id') else None,
        "sucursal_id": usuario.sucursal_id if hasattr(usuario, 'sucursal_id') else None,
    }
    
    if include_sensitive:
        data['last_login'] = usuario.last_login.isoformat() if hasattr(usuario, 'last_login') and usuario.last_login else None
        data['created_at'] = usuario.created_at.isoformat() if hasattr(usuario, 'created_at') and usuario.created_at else None
    
    return data

def _build_cors_response():
    """
    Construye una respuesta CORS para preflight OPTIONS.
    """
    response = make_response('', 204)
    response.headers['Access-Control-Allow-Origin'] = request.headers.get('Origin', '*')
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS, PUT, DELETE'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, X-User-ID'
    response.headers['Access-Control-Allow-Credentials'] = 'true'
    response.headers['Access-Control-Max-Age'] = '3600'
    return response

# ==========================================
# MIDDLEWARE DE SINCRONIZACIÓN
# ==========================================
@auth_bp.before_app_request
def sync_session_data():
    """
    Middleware que se ejecuta antes de cada request para validar coherencia.
    """
    if current_user.is_authenticated:
        # Actualizar timestamp de última actividad
        session['last_activity'] = datetime.utcnow().isoformat()
        
        # Validar que el user_id en sesión coincida con current_user
        stored_id = session.get('user_id')
        if stored_id and stored_id != current_user.id_usuario:
            logger.error(f"🔥 COLISIÓN DE SESIÓN DETECTADA: Stored={stored_id}, Current={current_user.id_usuario}")
            logout_user()
            session.clear()

# ==========================================
# ENDPOINTS DE COMPATIBILIDAD (LEGACY)
# ==========================================
# Mantener temporalmente para no romper código antiguo

@auth_bp.route('/ingreso', methods=['POST', 'OPTIONS'])
def ingreso_legacy():
    """Alias de /login para compatibilidad"""
    return login()

# ==========================================
# HEALTH CHECK DEL MÓDULO
# ==========================================
@auth_bp.route('/health', methods=['GET'])
def auth_health():
    """Health check específico del módulo de autenticación"""
    return jsonify({
        "status": "online",
        "module": "authentication",
        "version": "2.0.0"
    }), 200