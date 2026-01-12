"""
BizFlow Studio - Sistema de Autenticación Unificado v2.2
Backend: Render | Frontend: Firebase
ACTUALIZADO: Soporte JWT para autenticación desde iframes
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
# CONFIGURACIÓN DE CORS ORIGINS
# ==========================================
ALLOWED_ORIGINS = [
    "https://trayectoria-rxdc1.web.app",
    "https://mitrayectoria.web.app",
    "http://localhost:5001",
    "http://localhost:5173",
    "http://localhost:3000"
]


# ==========================================
# DECORADOR DE VALIDACIÓN DE SESIÓN
# ==========================================
def require_active_session(f):
    """Decorador que valida la sesión del servidor."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            logger.warning(f"❌ Acceso denegado: Sesión inválida para {request.endpoint}")
            return jsonify({
                "error": "session_expired",
                "message": "Tu sesión ha expirado. Inicia sesión nuevamente.",
                "redirect": "/login.html"
            }), 401
        
        if not current_user.active:
            logger.warning(f"❌ Usuario inactivo: {current_user.id_usuario}")
            logout_user()
            return jsonify({
                "error": "account_disabled",
                "message": "Tu cuenta ha sido desactivada."
            }), 403
        
        return f(*args, **kwargs)
    
    return decorated_function


# ==========================================
# HELPER: CONSTRUIR RESPUESTA CORS
# ==========================================
def build_cors_response(data=None, status=200):
    """Construye respuesta con headers CORS correctos."""
    if data is None:
        response = make_response('', 204)
    else:
        response = make_response(jsonify(data), status)
    
    origin = request.headers.get('Origin', '')
    
    if origin in ALLOWED_ORIGINS:
        response.headers['Access-Control-Allow-Origin'] = origin
    
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS, PUT, DELETE'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, X-User-ID, X-Business-ID, Accept, Cache-Control'
    response.headers['Access-Control-Allow-Credentials'] = 'true'
    response.headers['Access-Control-Max-Age'] = '3600'
    
    return response


# ==========================================
# HELPER: SERIALIZAR USUARIO
# ==========================================
def serialize_user(usuario, include_sensitive=False):
    """Serializa objeto Usuario a JSON."""
    if not usuario:
        return None
    
    data = {
        "id": usuario.id_usuario,
        "id_usuario": usuario.id_usuario,
        "nombre": usuario.nombre,
        "apellidos": getattr(usuario, 'apellidos', ''),
        "correo": usuario.correo,
        "telefono": getattr(usuario, 'celular', None),
        "profesion": getattr(usuario, 'profesion', ''),
        "activo": usuario.active,
        "validado": getattr(usuario, 'validate', False),
        "ciudad_id": getattr(usuario, 'ciudad_id', None),
    }
    
    if include_sensitive:
        data['cedula'] = getattr(usuario, 'cedula', None)
        data['last_login'] = usuario.last_login.isoformat() if hasattr(usuario, 'last_login') and usuario.last_login else None
        data['created_at'] = usuario.created_at.isoformat() if hasattr(usuario, 'created_at') and usuario.created_at else None
    
    return data


# ==========================================
# ENDPOINT: LOGIN (con JWT)
# ==========================================
@auth_bp.route('/login', methods=['POST', 'OPTIONS'])
def login():
    """
    Endpoint principal de autenticación.
    
    🔐 ACTUALIZADO: Ahora devuelve tokens JWT además de cookie de sesión.
    
    Request:
        POST /api/auth/login
        {
            "correo": "usuario@ejemplo.com",
            "password": "contraseña123"
        }
    
    Response (200):
        {
            "status": "success",
            "session_token": "...",
            "user": {...},
            "access_token": "...",      // JWT access token
            "refresh_token": "...",     // JWT refresh token
            "expires_in": 86400         // segundos hasta expiración
        }
    """
    if request.method == 'OPTIONS':
        return build_cors_response()
    
    logger.info("--- Nueva solicitud de login ---")
    
    # Verificar si ya está autenticado
    if current_user.is_authenticated:
        logger.info(f"👤 Usuario {current_user.correo} ya tiene sesión activa")
        
        # Generar JWT también para usuario ya autenticado
        jwt_tokens = {}
        try:
            from src.auth_jwt import create_token
            jwt_tokens = create_token(
                user_id=current_user.id_usuario,
                user_email=current_user.correo,
                user_name=current_user.nombre
            )
        except ImportError:
            logger.warning("⚠️ Módulo auth_jwt no disponible")
        except Exception as e:
            logger.warning(f"⚠️ Error generando JWT: {e}")
        
        return build_cors_response({
            "status": "already_authenticated",
            "user": serialize_user(current_user),
            **jwt_tokens
        }, 200)
    
    # Validar datos de entrada
    data = request.get_json()
    if not data:
        return build_cors_response({"error": "No se proporcionaron datos"}, 400)
    
    correo = data.get('correo', '').strip().lower()
    password = data.get('password', '').strip()
    
    if not correo or not password:
        return build_cors_response({"error": "Correo y contraseña son requeridos"}, 400)
    
    # Control de intentos fallidos
    attempts_key = f"login_attempts_{correo}"
    attempts = session.get(attempts_key, 0)
    
    if attempts >= 5:
        logger.warning(f"🚫 Bloqueo por intentos: {correo}")
        return build_cors_response({
            "error": "too_many_attempts",
            "message": "Demasiados intentos fallidos. Intenta en 15 minutos."
        }, 429)
    
    # Buscar y validar usuario
    try:
        usuario = Usuario.query.filter_by(correo=correo).first()
        
        if not usuario or not usuario.check_password(password):
            session[attempts_key] = attempts + 1
            logger.warning(f"❌ Credenciales incorrectas para: {correo}")
            return build_cors_response({"error": "Credenciales incorrectas"}, 401)
        
        if not usuario.active:
            logger.warning(f"❌ Cuenta inactiva: {correo}")
            return build_cors_response({
                "error": "account_inactive",
                "message": "Tu cuenta está desactivada. Contacta a soporte."
            }, 403)
        
        # CREAR SESIÓN (cookies)
        login_user(usuario, remember=True, duration=timedelta(days=7))
        
        session.permanent = True
        session[attempts_key] = 0
        
        session_token = secrets.token_urlsafe(32)
        session['session_token'] = session_token
        session['user_id'] = usuario.id_usuario
        session['login_timestamp'] = datetime.utcnow().isoformat()
        
        # Actualizar último login
        try:
            usuario.last_login = datetime.utcnow()
            db.session.commit()
        except Exception as e:
            logger.error(f"Error actualizando last_login: {e}")
            db.session.rollback()
        
        logger.info(f"✅ Login exitoso: {correo} (ID: {usuario.id_usuario})")
        
        # ==========================================
        # 🔐 NUEVO: GENERAR TOKENS JWT
        # ==========================================
        jwt_tokens = {}
        try:
            from src.auth_jwt import create_token
            jwt_tokens = create_token(
                user_id=usuario.id_usuario,
                user_email=usuario.correo,
                user_name=usuario.nombre
            )
            logger.info(f"🔐 JWT generado para usuario {usuario.id_usuario}")
        except ImportError:
            logger.warning("⚠️ Módulo auth_jwt no disponible - login sin JWT")
        except Exception as e:
            logger.warning(f"⚠️ Error generando JWT: {e}")
        
        # Construir respuesta
        response_data = {
            "status": "success",
            "message": "Inicio de sesión exitoso",
            "session_token": session_token,
            "user": serialize_user(usuario),
            # 🔐 NUEVO: Tokens JWT
            **jwt_tokens
        }
        
        response = build_cors_response(response_data, 200)
        
        # Cookie adicional para detección en frontend
        response.set_cookie(
            'session_active',
            value='true',
            max_age=7*24*60*60,
            secure=True,
            httponly=False,
            samesite='None',
            domain=None
        )
        
        return response
    
    except Exception as e:
        logger.error(f"🔥 Error crítico en login: {str(e)}", exc_info=True)
        return build_cors_response({"error": "Error interno del servidor"}, 500)


# ==========================================
# ENDPOINT: REFRESH TOKEN (NUEVO)
# ==========================================
@auth_bp.route('/refresh', methods=['POST', 'OPTIONS'])
def refresh_token():
    """
    🔐 Renueva el access token usando un refresh token válido.
    
    Request:
        POST /api/auth/refresh
        {
            "refresh_token": "..."
        }
    
    Response (200):
        {
            "success": true,
            "access_token": "...",
            "refresh_token": "...",
            "expires_in": 86400
        }
    """
    if request.method == 'OPTIONS':
        return build_cors_response()
    
    try:
        from src.auth_jwt import verify_token, create_token
    except ImportError:
        logger.error("❌ Módulo auth_jwt no disponible")
        return build_cors_response({
            "success": False,
            "error": "JWT no configurado en el servidor"
        }, 500)
    
    data = request.get_json()
    refresh_token = data.get('refresh_token') if data else None
    
    if not refresh_token:
        return build_cors_response({
            "success": False,
            "error": "refresh_token es requerido"
        }, 400)
    
    # Verificar refresh token
    payload = verify_token(refresh_token, token_type='refresh')
    
    if not payload:
        return build_cors_response({
            "success": False,
            "error": "Token inválido o expirado"
        }, 401)
    
    # Buscar usuario para verificar que sigue activo
    user_id = payload.get('user_id')
    usuario = Usuario.query.get(user_id)
    
    if not usuario or not usuario.active:
        return build_cors_response({
            "success": False,
            "error": "Usuario no válido"
        }, 401)
    
    # Generar nuevos tokens
    new_tokens = create_token(
        user_id=usuario.id_usuario,
        user_email=usuario.correo,
        user_name=usuario.nombre
    )
    
    logger.info(f"🔄 Token refrescado para usuario {usuario.id_usuario}")
    
    return build_cors_response({
        "success": True,
        **new_tokens
    }, 200)


# ==========================================
# ENDPOINT: VERIFICAR SESIÓN
# ==========================================
@auth_bp.route('/session/verify', methods=['GET', 'OPTIONS'])
def verify_session():
    """Verifica si la sesión actual es válida."""
    if request.method == 'OPTIONS':
        return build_cors_response()
    
    if not current_user.is_authenticated:
        return build_cors_response({
            "status": "inactive",
            "authenticated": False
        }, 401)
    
    if not current_user.active:
        logout_user()
        return build_cors_response({
            "status": "disabled",
            "authenticated": False,
            "message": "Cuenta desactivada"
        }, 403)
    
    return build_cors_response({
        "status": "active",
        "authenticated": True,
        "user": serialize_user(current_user),
        "session_token": session.get('session_token'),
        "authenticated_at": session.get('login_timestamp')
    }, 200)


# ==========================================
# ENDPOINT: LOGOUT
# ==========================================
@auth_bp.route('/logout', methods=['POST', 'GET', 'OPTIONS'])
def logout():
    """Cierra la sesión del usuario."""
    if request.method == 'OPTIONS':
        return build_cors_response()
    
    user_info = None
    if current_user.is_authenticated:
        user_info = f"{current_user.correo} (ID: {current_user.id_usuario})"
        logout_user()
    
    session.clear()
    
    logger.info(f"🚪 Logout exitoso: {user_info or 'Usuario anónimo'}")
    
    response = build_cors_response({
        "status": "success",
        "message": "Sesión cerrada exitosamente"
    }, 200)
    
    cookies_to_clear = ['session_active', 'bizflow_session', 'bizflow_remember', 'session']
    for cookie_name in cookies_to_clear:
        response.set_cookie(
            cookie_name, 
            '', 
            expires=0, 
            path='/',
            secure=True,
            samesite='None'
        )
    
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    
    return response


# ==========================================
# ENDPOINT: PERFIL DE USUARIO
# ==========================================
@auth_bp.route('/user/profile', methods=['GET', 'OPTIONS'])
@require_active_session
def get_user_profile():
    """Devuelve el perfil completo del usuario autenticado."""
    if request.method == 'OPTIONS':
        return build_cors_response()
    
    return build_cors_response({
        "status": "success",
        "user": serialize_user(current_user, include_sensitive=True)
    }, 200)


# ==========================================
# ENDPOINT: ESTADO DE SESIÓN (LEGACY)
# ==========================================
@auth_bp.route('/session_status', methods=['GET', 'OPTIONS'])
def session_status():
    """Endpoint de compatibilidad."""
    if request.method == 'OPTIONS':
        return build_cors_response()
    
    if current_user.is_authenticated and current_user.active:
        return build_cors_response({
            "authenticated": True,
            "user": serialize_user(current_user)
        }, 200)
    
    return build_cors_response({
        "authenticated": False,
        "error": "Sesión expirada"
    }, 401)


# ==========================================
# ENDPOINT: INGRESO (LEGACY)
# ==========================================
@auth_bp.route('/ingreso', methods=['POST', 'OPTIONS'])
def ingreso_legacy():
    """Alias de /login para compatibilidad."""
    return login()


# ==========================================
# MIDDLEWARE: SINCRONIZACIÓN DE SESIÓN
# ==========================================
@auth_bp.before_app_request
def sync_session_data():
    """Middleware que valida coherencia de sesión."""
    if current_user.is_authenticated:
        session['last_activity'] = datetime.utcnow().isoformat()
        
        stored_id = session.get('user_id')
        if stored_id and stored_id != current_user.id_usuario:
            logger.error(f"🔥 COLISIÓN DE SESIÓN: Stored={stored_id}, Current={current_user.id_usuario}")
            logout_user()
            session.clear()


# ==========================================
# HEALTH CHECK
# ==========================================
@auth_bp.route('/health', methods=['GET'])
def auth_health():
    """Health check del módulo de autenticación."""
    
    jwt_status = "unavailable"
    try:
        from src.auth_jwt import JWT_SECRET_KEY
        jwt_status = "configured"
    except ImportError:
        jwt_status = "not_installed"
    
    return jsonify({
        "status": "online",
        "module": "authentication",
        "version": "2.2.0",
        "jwt_status": jwt_status,
        "timestamp": datetime.utcnow().isoformat()
    }), 200