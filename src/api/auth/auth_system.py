# ═══════════════════════════════════════════════════════════════════════════════
# ███████╗██╗   ██╗██╗  ██╗ ██████╗ ███╗   ███╗███████╗██████╗  ██████╗██╗ ██████╗ 
# ╚══██╔══╝██║   ██║██║ ██╔╝██╔═══██╗████╗ ████║██╔════╝██╔══██╗██╔════╝██║██╔═══██╗
#    ██║   ██║   ██║█████╔╝ ██║   ██║██╔████╔██║█████╗  ██████╔╝██║     ██║██║   ██║
#    ██║   ██║   ██║██╔═██╗ ██║   ██║██║╚██╔╝██║██╔══╝  ██╔══██╗██║     ██║██║   ██║
#    ██║   ╚██████╔╝██║  ██╗╚██████╔╝██║ ╚═╝ ██║███████╗██║  ██║╚██████╗██║╚██████╔╝
#    ╚═╝    ╚═════╝ ╚═╝  ╚═╝ ╚═════╝ ╚═╝     ╚═╝╚══════╝╚═╝  ╚═╝ ╚═════╝╚═╝ ╚═════╝ 
# ═══════════════════════════════════════════════════════════════════════════════
#
# TUKOMERCIO - Plataforma de Comercio Electrónico, Gamificación y Gestión Empresarial
# Anteriormente conocido como: Trayectoria / BizFlow Studio
#
# ═══════════════════════════════════════════════════════════════════════════════
# AVISO DE PROPIEDAD INTELECTUAL Y DERECHOS DE AUTOR
# ═══════════════════════════════════════════════════════════════════════════════
#
# © 2024-2026 Carlos Eduardo Huérfano Bermúdez. Todos los derechos reservados.
#
# TITULAR DE DERECHOS:
#   Nombre:     Carlos Eduardo Huérfano Bermúdez
#   C.C.:       1.064.986.917 (Cereté, Córdoba, Colombia)
#   Contacto:   carlos-5100@hotmail.com | +57 322 818 8375
#   Ubicación:  Bogotá D.C., Colombia
#
# INFORMACIÓN DEL PROYECTO:
#   Nombre:     TuKomercio
#   Inicio:     Julio 24, 2024
#   Repositorio: github.com/routeres (routeres@gmail.com)
#
# ═══════════════════════════════════════════════════════════════════════════════
# TÉRMINOS DE USO Y RESTRICCIONES
# ═══════════════════════════════════════════════════════════════════════════════
#
# Este código fuente es CONFIDENCIAL y constituye un SECRETO COMERCIAL.
#
# QUEDA ESTRICTAMENTE PROHIBIDO sin autorización ESCRITA del titular:
#
#   1. Copiar, reproducir o duplicar este código, total o parcialmente
#   2. Modificar, adaptar o crear obras derivadas
#   3. Distribuir, publicar, sublicenciar o transferir a terceros
#   4. Usar para desarrollo de productos competidores
#   5. Realizar ingeniería inversa, descompilar o desensamblar
#   6. Remover o alterar este aviso de propiedad intelectual
#
# El acceso a este código NO otorga ninguna licencia implícita o explícita.
#
# ═══════════════════════════════════════════════════════════════════════════════
# PROTECCIÓN LEGAL
# ═══════════════════════════════════════════════════════════════════════════════
#
# Este software está protegido por:
#
#   • Ley 23 de 1982 - Derechos de Autor (Colombia)
#   • Ley 1915 de 2018 - Modernización Derechos de Autor (Colombia)
#   • Decisión Andina 351 de 1993 - Régimen Común sobre Derecho de Autor
#   • Convenio de Berna para la Protección de Obras Literarias y Artísticas
#   • Tratado OMPI sobre Derecho de Autor (WCT)
#   • Acuerdo ADPIC/TRIPS - Organización Mundial del Comercio
#
# SANCIONES POR INFRACCIÓN:
#   • Civiles: Indemnización por daños y perjuicios (Art. 57, Ley 23/1982)
#   • Penales: Prisión de 4 a 8 años y multa (Art. 271, Código Penal Colombiano)
#
# ═══════════════════════════════════════════════════════════════════════════════
# JURISDICCIÓN
# ═══════════════════════════════════════════════════════════════════════════════
#
# Cualquier disputa será resuelta exclusivamente por los tribunales de
# Bogotá D.C., Colombia, bajo las leyes de la República de Colombia.
#
# ═══════════════════════════════════════════════════════════════════════════════
#
# Para solicitar autorización de uso: carlos-5100@hotmail.com
#
# ═══════════════════════════════════════════════════════════════════════════════


"""
BizFlow Studio - Sistema de Autenticación Unificado v2.3
Backend: Render | Frontend: Firebase
ACTUALIZADO: Siempre verifica contraseña + Logout seguro
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
    # Firebase legacy
    "https://trayectoria-rxdc1.web.app",
    "https://mitrayectoria.web.app",
    # Cloudflare Pages (producción actual)
    "https://tuko.pages.dev",
    "https://tukomercio.pages.dev",
    # Desarrollo local
    "http://localhost:5001",
    "http://localhost:5173",
    "http://localhost:3000",
    "http://127.0.0.1:5500",
    "http://127.0.0.1:3000",
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
        response.headers['Access-Control-Allow-Credentials'] = 'true'  # necesario para cookies cross-origin
    elif not origin:
        # Requests sin Origin (curl, Postman, etc.)
        response.headers['Access-Control-Allow-Origin'] = '*'

    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS, PUT, DELETE'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, X-User-ID, X-Business-ID, Accept, Cache-Control, X-Session-FP'
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
# ENDPOINT: LOGIN (SEGURO - Siempre verifica contraseña)
# ==========================================
@auth_bp.route('/login', methods=['POST', 'OPTIONS'])
def login():
    """
    Endpoint principal de autenticación.
    
    🔐 v2.3: SIEMPRE verifica la contraseña, incluso con sesión activa.
    """
    if request.method == 'OPTIONS':
        return build_cors_response()
    
    logger.info("--- Nueva solicitud de login ---")
    
    # Validar datos de entrada
    data = request.get_json()
    if not data:
        return build_cors_response({"error": "No se proporcionaron datos"}, 400)
    
    correo = data.get('correo', '').strip().lower()
    password = data.get('password', '').strip()
    
    if not correo or not password:
        return build_cors_response({"error": "Correo y contraseña son requeridos"}, 400)
    
    # Control de intentos fallidos (A-SEC-1): server-side por IP+email (la sesión
    # cookie no sirve: el atacante la ignora). Bloqueo tras 5 fallos en 15 min.
    import time as _time
    from src.api.utils.seguridad import (
        esta_bloqueado, registrar_fallo, limpiar_intentos,
        registrar_evento_seguridad, UMBRAL_INTENTOS,
    )
    _ip = (request.headers.get('X-Forwarded-For', '') or request.remote_addr or '').split(',')[0].strip()
    _ahora = _time.time()
    _bloq, _restante = esta_bloqueado(_ip, correo, _ahora)
    if _bloq:
        logger.warning(f"🚫 Bloqueo por intentos: {correo} (ip {_ip})")
        return build_cors_response({
            "error": "too_many_attempts",
            "message": f"Demasiados intentos fallidos. Intenta en {max(1, _restante // 60)} minutos."
        }, 429)

    # Buscar y validar usuario
    try:
        usuario = Usuario.query.filter_by(correo=correo).first()

        # ==========================================
        # 🔐 FIX: SIEMPRE verificar contraseña
        # ==========================================
        if not usuario or not usuario.check_password(password):
            _n = registrar_fallo(_ip, correo, _ahora)
            logger.warning(f"❌ Credenciales incorrectas para: {correo} (intento {_n})")
            if _n >= UMBRAL_INTENTOS:
                registrar_evento_seguridad('login', 'login_bloqueado',
                                           {'intentos': _n, 'motivo': 'fuerza_bruta'},
                                           ip=_ip, email=correo)
            return build_cors_response({"error": "Credenciales incorrectas"}, 401)
        
        if not usuario.active:
            logger.warning(f"❌ Cuenta inactiva: {correo}")
            return build_cors_response({
                "error": "account_inactive",
                "message": "Tu cuenta está desactivada. Contacta a soporte."
            }, 403)
        
        # Si había sesión previa, cerrarla primero
        if current_user.is_authenticated:
            logger.info(f"🔄 Cerrando sesión previa de {current_user.correo}")
            logout_user()
            session.clear()
        
        # CREAR NUEVA SESIÓN
        login_user(usuario, remember=True, duration=timedelta(days=7))
        
        session.permanent = True
        limpiar_intentos(_ip, correo)   # A-SEC-1: login OK → reinicia contador

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

        # ★ GAMIFICACIÓN (S2) — racha de actividad + XP diario por negocio.
        # En su propio try/except: jamás puede afectar el login.
        # Solo otorga XP una vez al día (lo controla la racha interna).
        try:
            from src.api.gamificacion.gamificacion_hooks import on_login, on_login_usuario
            from src.models.colombia_data.negocio import Negocio
            # Gamificación de la PERSONA (S8): racha + XP de creador
            on_login_usuario(usuario.id_usuario)
            # Gamificación de cada NEGOCIO del usuario (S2): racha + XP de negocio
            negocios_usuario = Negocio.query.filter_by(
                usuario_id=usuario.id_usuario).with_entities(Negocio.id_negocio).all()
            for (nid,) in negocios_usuario:
                on_login(nid)
        except Exception as ge:
            logger.warning(f"[gamif] Hook login no crítico: {ge}")

        logger.info(f"✅ Login exitoso: {correo} (ID: {usuario.id_usuario})")
        
        # Generar tokens JWT si está disponible
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
# ENDPOINT: REFRESH TOKEN
# ==========================================
@auth_bp.route('/refresh', methods=['POST', 'OPTIONS'])
def refresh_token():
    """Renueva el access token usando un refresh token válido."""
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
    refresh_token_value = data.get('refresh_token') if data else None
    
    if not refresh_token_value:
        return build_cors_response({
            "success": False,
            "error": "refresh_token es requerido"
        }, 400)
    
    payload = verify_token(refresh_token_value, token_type='refresh')
    
    if not payload:
        return build_cors_response({
            "success": False,
            "error": "Token inválido o expirado"
        }, 401)
    
    user_id = payload.get('user_id')
    usuario = Usuario.query.get(user_id)
    
    if not usuario or not usuario.active:
        return build_cors_response({
            "success": False,
            "error": "Usuario no válido"
        }, 401)
    
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
# ENDPOINT: LOGOUT (SEGURIDAD MÁXIMA)
# ==========================================
@auth_bp.route('/logout', methods=['POST', 'GET', 'OPTIONS'])
def logout():
    """
    Cierra la sesión del usuario de forma SEGURA.
    
    🔐 Medidas de seguridad:
    1. Invalida sesión en servidor (Flask-Login)
    2. Limpia todas las variables de sesión
    3. Elimina TODAS las cookies posibles
    4. Actualiza BD para invalidar tokens
    5. Headers anti-cache
    """
    if request.method == 'OPTIONS':
        return build_cors_response()
    
    logger.info("=" * 60)
    logger.info("🚪 LOGOUT: Iniciando cierre de sesión seguro")
    logger.info("=" * 60)
    
    user_info = None
    user_id = None
    
    # 1. CAPTURAR INFO DEL USUARIO
    if current_user.is_authenticated:
        user_info = f"{current_user.correo} (ID: {current_user.id_usuario})"
        user_id = current_user.id_usuario
        logger.info(f"📍 Usuario a desconectar: {user_info}")
    
    # 2. INVALIDAR EN BASE DE DATOS
    if user_id:
        try:
            usuario = Usuario.query.get(user_id)
            if usuario:
                usuario.last_login = None
                db.session.commit()
                logger.info(f"📍 Sesión invalidada en BD para usuario {user_id}")
        except Exception as e:
            logger.warning(f"⚠️ Error invalidando sesión en BD: {e}")
            db.session.rollback()
    
    # 3. CERRAR SESIÓN FLASK-LOGIN
    try:
        logout_user()
        logger.info("📍 Flask-Login: logout_user() ejecutado")
    except Exception as e:
        logger.warning(f"⚠️ Error en logout_user(): {e}")
    
    # 4. LIMPIAR TODA LA SESIÓN
    try:
        keys_to_clear = [
            'session_token', 'user_id', 'login_timestamp',
            'last_activity', '_fresh', '_id', '_user_id',
            'csrf_token', 'remember_token'
        ]
        for key in keys_to_clear:
            session.pop(key, None)
        
        session.clear()
        logger.info("📍 Sesión del servidor limpiada completamente")
    except Exception as e:
        logger.warning(f"⚠️ Error limpiando sesión: {e}")
    
    # 5. PREPARAR RESPUESTA
    response = build_cors_response({
        "status": "success",
        "message": "Sesión cerrada exitosamente",
        "logged_out_user": user_info
    }, 200)
    
    # 6. ELIMINAR TODAS LAS COOKIES POSIBLES
    cookies_to_clear = [
        'session',
        'session_active',
        'bizflow_session',
        'bizflow_remember',
        'remember_token',
        '_fresh',
        'csrf_token',
        'user_id',
        'auth_token',
        'access_token',
        'refresh_token'
    ]
    
    for cookie_name in cookies_to_clear:
        # Variante 1: SameSite=None, Secure
        response.set_cookie(
            cookie_name, 
            '', 
            expires=0,
            max_age=0,
            path='/',
            secure=True,
            httponly=True,
            samesite='None'
        )
        # Variante 2: SameSite=Lax
        response.set_cookie(
            cookie_name, 
            '', 
            expires=0,
            max_age=0,
            path='/',
            secure=True,
            httponly=True,
            samesite='Lax'
        )
    
    logger.info(f"📍 {len(cookies_to_clear)} cookies eliminadas")
    
    # 7. HEADERS ANTI-CACHE
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate, private, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    response.headers['Clear-Site-Data'] = '"cache", "cookies", "storage"'
    
    logger.info("=" * 60)
    logger.info(f"✅ LOGOUT COMPLETADO: {user_info or 'Usuario anónimo'}")
    logger.info("=" * 60)
    
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
# MIDDLEWARE: VALIDACIÓN DE SESIÓN (SEGURIDAD)
# ==========================================
@auth_bp.before_app_request
def sync_session_data():
    """
    Middleware que valida coherencia y seguridad de sesión.
    
    🔐 Validaciones:
    1. Coherencia de user_id
    2. Usuario sigue activo en BD
    3. Sesión no fue invalidada
    """
    if current_user.is_authenticated:
        # Actualizar última actividad
        session['last_activity'] = datetime.utcnow().isoformat()
        
        # Verificar coherencia de IDs
        stored_id = session.get('user_id')
        if stored_id and stored_id != current_user.id_usuario:
            logger.error(f"🔥 COLISIÓN DE SESIÓN: Stored={stored_id}, Current={current_user.id_usuario}")
            logout_user()
            session.clear()
            return
        
        # Verificar que el usuario sigue activo en BD
        try:
            usuario = Usuario.query.get(current_user.id_usuario)
            if not usuario or not usuario.active or usuario.black_list:
                logger.warning(f"⚠️ Usuario {current_user.id_usuario} ya no está activo - cerrando sesión")
                logout_user()
                session.clear()
                return
        except Exception as e:
            logger.error(f"Error verificando usuario: {e}")


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
        "version": "2.3.0",
        "jwt_status": jwt_status,
        "security_features": [
            "always_verify_password",
            "secure_logout",
            "session_invalidation",
            "anti_cache_headers",
            "clear_site_data"
        ],
        "timestamp": datetime.utcnow().isoformat()
    }), 200