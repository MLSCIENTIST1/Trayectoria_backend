"""
BizFlow Studio - Avatar API
Endpoint para actualizar foto de perfil de usuario
Integrado con Cloudinary

Ubicación: src/api/profile/avatar_api.py
"""

from flask import Blueprint, request, jsonify, make_response
from flask_login import current_user
import logging

# Importar base de datos y modelo (igual que auth_system.py)
from src.models.database import db
from src.models.usuarios import Usuario

logger = logging.getLogger(__name__)

# ==========================================
# BLUEPRINT
# ==========================================
avatar_api_bp = Blueprint('avatar_api', __name__)


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
    
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS, PUT, DELETE, PATCH'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, X-User-ID, X-Business-ID, Accept, Cache-Control'
    response.headers['Access-Control-Allow-Credentials'] = 'true'
    response.headers['Access-Control-Max-Age'] = '3600'
    
    return response


# ==========================================
# ACTUALIZAR AVATAR
# PATCH /api/users/<user_id>/avatar
# ==========================================
@avatar_api_bp.route('/api/users/<int:user_id>/avatar', methods=['PATCH', 'OPTIONS'])
def update_avatar(user_id):
    """
    Actualiza la foto de perfil del usuario.
    
    La imagen ya fue subida a Cloudinary desde el frontend.
    Este endpoint solo guarda la URL en la base de datos.
    
    Body:
        {
            "foto_url": "https://res.cloudinary.com/..."
        }
    
    Returns:
        200: Avatar actualizado correctamente
        400: foto_url es requerido
        404: Usuario no encontrado
        500: Error interno
    """
    
    # Manejar preflight CORS
    if request.method == 'OPTIONS':
        return build_cors_response()
    
    logger.info(f"📸 Solicitud de actualización de avatar para usuario {user_id}")
    
    try:
        # Obtener datos del request
        data = request.get_json()
        
        if not data:
            logger.warning("📸 No se recibieron datos JSON")
            return build_cors_response({
                'success': False,
                'error': 'No se recibieron datos'
            }, 400)
        
        foto_url = data.get('foto_url')
        
        if not foto_url:
            logger.warning("📸 foto_url no proporcionada")
            return build_cors_response({
                'success': False,
                'error': 'foto_url es requerido'
            }, 400)
        
        # Validar que sea URL de Cloudinary
        if 'cloudinary.com' not in foto_url and 'res.cloudinary.com' not in foto_url:
            logger.warning(f"📸 URL no es de Cloudinary: {foto_url}")
            return build_cors_response({
                'success': False,
                'error': 'URL debe ser de Cloudinary'
            }, 400)
        
        logger.info(f"📸 Actualizando avatar de usuario {user_id} con URL: {foto_url[:50]}...")
        
        # Buscar usuario en base de datos (usando SQLAlchemy)
        usuario = Usuario.query.get(user_id)
        
        if not usuario:
            logger.warning(f"📸 Usuario {user_id} no encontrado")
            return build_cors_response({
                'success': False,
                'error': 'Usuario no encontrado'
            }, 404)
        
        # Actualizar foto_url
        usuario.foto_url = foto_url
        
        # Guardar cambios
        db.session.commit()
        
        logger.info(f"✅ Avatar actualizado para usuario {user_id}")
        
        return build_cors_response({
            'success': True,
            'message': 'Avatar actualizado correctamente',
            'foto_url': foto_url
        }, 200)
            
    except Exception as e:
        logger.error(f"❌ Error actualizando avatar: {str(e)}")
        db.session.rollback()
        import traceback
        traceback.print_exc()
        return build_cors_response({
            'success': False,
            'error': f'Error interno: {str(e)}'
        }, 500)


# ==========================================
# OBTENER AVATAR
# GET /api/users/<user_id>/avatar
# ==========================================
@avatar_api_bp.route('/api/users/<int:user_id>/avatar', methods=['GET'])
def get_avatar(user_id):
    """
    Obtiene la URL del avatar del usuario.
    
    Returns:
        200: foto_url del usuario
        404: Usuario no encontrado
    """
    
    logger.info(f"📸 Solicitud de avatar para usuario {user_id}")
    
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
        logger.error(f"❌ Error obteniendo avatar: {str(e)}")
        return build_cors_response({
            'success': False,
            'error': f'Error interno: {str(e)}'
        }, 500)


# ==========================================
# HEALTH CHECK
# ==========================================
@avatar_api_bp.route('/api/avatar/health', methods=['GET'])
def avatar_health():
    """Health check del módulo avatar"""
    return jsonify({
        'status': 'ok',
        'module': 'avatar_api',
        'endpoints': [
            'PATCH /api/users/<user_id>/avatar',
            'GET /api/users/<user_id>/avatar'
        ]
    }), 200