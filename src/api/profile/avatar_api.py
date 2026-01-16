"""
BizFlow Studio - Avatar API
Endpoint para actualizar foto de perfil de usuario
Integrado con Cloudinary

Ubicación: src/api/profile/avatar_api.py
VERSION: DEBUG con logs detallados
"""

from flask import Blueprint, request, jsonify, make_response
from flask_login import current_user
import logging

# Importar base de datos y modelo (igual que auth_system.py)
from src.models.database import db
from src.models.usuarios import Usuario

logger = logging.getLogger(__name__)

print("=" * 60)
print("📸 AVATAR_API.PY: MÓDULO CARGADO")
print("=" * 60)

# ==========================================
# BLUEPRINT
# ==========================================
avatar_api_bp = Blueprint('avatar_api', __name__)

print(f"📸 Blueprint creado: {avatar_api_bp.name}")


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
    else:
        # Si el origin no está en la lista, usar el primero permitido
        response.headers['Access-Control-Allow-Origin'] = ALLOWED_ORIGINS[0]
    
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS, PUT, DELETE, PATCH'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, X-User-ID, X-Business-ID, Accept, Cache-Control, X-Session-FP'
    response.headers['Access-Control-Allow-Credentials'] = 'true'
    response.headers['Access-Control-Max-Age'] = '3600'
    
    return response


# ==========================================
# ACTUALIZAR AVATAR
# PATCH /users/<user_id>/avatar
# ==========================================
@avatar_api_bp.route('/users/<int:user_id>/avatar', methods=['PATCH', 'OPTIONS'])
def update_avatar(user_id):
    """
    Actualiza la foto de perfil del usuario.
    """
    
    print("=" * 60)
    print(f"📸 AVATAR ENDPOINT HIT!")
    print(f"📸 Method: {request.method}")
    print(f"📸 User ID: {user_id}")
    print(f"📸 Origin: {request.headers.get('Origin', 'NO ORIGIN')}")
    print(f"📸 Content-Type: {request.headers.get('Content-Type', 'NO CT')}")
    print("=" * 60)
    
    logger.info("=" * 60)
    logger.info(f"📸 AVATAR ENDPOINT - Method: {request.method}, User: {user_id}")
    logger.info("=" * 60)
    
    # Manejar preflight CORS
    if request.method == 'OPTIONS':
        print("📸 → Respondiendo a OPTIONS (preflight)")
        logger.info("📸 → Respondiendo a OPTIONS (preflight)")
        return build_cors_response()
    
    print("📸 → Procesando PATCH request...")
    logger.info("📸 → Procesando PATCH request...")
    
    try:
        # Log de headers
        print(f"📸 Headers recibidos: {dict(request.headers)}")
        logger.info(f"📸 Headers: {dict(request.headers)}")
        
        # Obtener datos del request
        raw_data = request.get_data(as_text=True)
        print(f"📸 Raw data: {raw_data[:200] if raw_data else 'EMPTY'}")
        logger.info(f"📸 Raw data: {raw_data[:200] if raw_data else 'EMPTY'}")
        
        data = request.get_json()
        print(f"📸 JSON data: {data}")
        logger.info(f"📸 JSON data: {data}")
        
        if not data:
            print("📸 ❌ No se recibieron datos JSON")
            logger.warning("📸 ❌ No se recibieron datos JSON")
            return build_cors_response({
                'success': False,
                'error': 'No se recibieron datos'
            }, 400)
        
        foto_url = data.get('foto_url')
        print(f"📸 foto_url extraída: {foto_url[:50] if foto_url else 'NONE'}...")
        logger.info(f"📸 foto_url: {foto_url[:50] if foto_url else 'NONE'}...")
        
        if not foto_url:
            print("📸 ❌ foto_url no proporcionada")
            logger.warning("📸 ❌ foto_url no proporcionada")
            return build_cors_response({
                'success': False,
                'error': 'foto_url es requerido'
            }, 400)
        
        # Validar URL de Cloudinary (más flexible)
        if 'cloudinary' not in foto_url.lower():
            print(f"📸 ⚠️ URL no parece ser de Cloudinary: {foto_url}")
            logger.warning(f"📸 ⚠️ URL no es de Cloudinary: {foto_url}")
            # Permitir igual para debug
        
        print(f"📸 Buscando usuario {user_id} en BD...")
        logger.info(f"📸 Buscando usuario {user_id} en BD...")
        
        # Buscar usuario
        usuario = Usuario.query.get(user_id)
        
        if not usuario:
            print(f"📸 ❌ Usuario {user_id} NO encontrado")
            logger.warning(f"📸 ❌ Usuario {user_id} no encontrado")
            return build_cors_response({
                'success': False,
                'error': 'Usuario no encontrado'
            }, 404)
        
        print(f"📸 ✅ Usuario encontrado: {usuario.correo}")
        logger.info(f"📸 ✅ Usuario encontrado: {usuario.correo}")
        
        # Actualizar foto_url
        old_foto = getattr(usuario, 'foto_url', None)
        print(f"📸 foto_url anterior: {old_foto[:30] if old_foto else 'NONE'}...")
        
        usuario.foto_url = foto_url
        
        print("📸 Guardando en BD...")
        logger.info("📸 Guardando en BD...")
        
        db.session.commit()
        
        print(f"📸 ✅✅✅ AVATAR ACTUALIZADO EXITOSAMENTE ✅✅✅")
        logger.info(f"📸 ✅ Avatar actualizado para usuario {user_id}")
        
        return build_cors_response({
            'success': True,
            'message': 'Avatar actualizado correctamente',
            'foto_url': foto_url
        }, 200)
            
    except Exception as e:
        print(f"📸 ❌❌❌ EXCEPTION: {str(e)}")
        logger.error(f"📸 ❌ Error actualizando avatar: {str(e)}")
        db.session.rollback()
        import traceback
        traceback.print_exc()
        return build_cors_response({
            'success': False,
            'error': f'Error interno: {str(e)}'
        }, 500)


# ==========================================
# OBTENER AVATAR
# GET /users/<user_id>/avatar
# ==========================================
@avatar_api_bp.route('/users/<int:user_id>/avatar', methods=['GET'])
def get_avatar(user_id):
    """Obtiene la URL del avatar del usuario."""
    
    print(f"📸 GET AVATAR - User: {user_id}")
    logger.info(f"📸 GET avatar para usuario {user_id}")
    
    try:
        usuario = Usuario.query.get(user_id)
        
        if not usuario:
            return build_cors_response({
                'success': False,
                'error': 'Usuario no encontrado'
            }, 404)
        
        foto_url = getattr(usuario, 'foto_url', None)
        
        return build_cors_response({
            'success': True,
            'foto_url': foto_url
        }, 200)
        
    except Exception as e:
        logger.error(f"📸 ❌ Error obteniendo avatar: {str(e)}")
        return build_cors_response({
            'success': False,
            'error': f'Error interno: {str(e)}'
        }, 500)


# ==========================================
# HEALTH CHECK
# ==========================================
@avatar_api_bp.route('/avatar/health', methods=['GET'])
def avatar_health():
    """Health check del módulo avatar"""
    return jsonify({
        'status': 'ok',
        'module': 'avatar_api',
        'version': 'DEBUG_V2',
        'endpoints': [
            'PATCH /api/users/<user_id>/avatar',
            'GET /api/users/<user_id>/avatar'
        ]
    }), 200


print("📸 AVATAR_API.PY: Todas las rutas definidas")
print(f"📸 Rutas del blueprint: {[rule.rule for rule in avatar_api_bp.url_map.iter_rules()] if hasattr(avatar_api_bp, 'url_map') else 'N/A'}")