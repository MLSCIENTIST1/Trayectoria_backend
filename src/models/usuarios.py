"""
BizFlow Studio - Avatar API
Endpoint para actualizar foto de perfil de usuario
Versión: 1.0
"""

from flask import Blueprint, request, jsonify
import logging

# Importar el decorador de autenticación y el modelo
from src.api.auth.auth_system import token_required
from src.database import db
from src.usuarios import Usuario  # Ajusta si el modelo está en otro lugar

logger = logging.getLogger(__name__)

# ==========================================
# BLUEPRINT
# ==========================================
avatar_api_bp = Blueprint('avatar_api', __name__)


# ==========================================
# ACTUALIZAR AVATAR
# ==========================================
@avatar_api_bp.route('/api/users/<int:user_id>/avatar', methods=['PATCH'])
@token_required
def update_avatar(current_user, user_id):
    """
    Actualiza la foto de perfil del usuario
    
    Headers requeridos:
        - Authorization: Bearer <token>
    
    Body:
        {
            "foto_url": "https://res.cloudinary.com/dp50v0bwj/image/upload/..."
        }
    
    Returns:
        - 200: Avatar actualizado correctamente
        - 400: Datos inválidos
        - 403: No autorizado
        - 404: Usuario no encontrado
        - 500: Error interno
    """
    
    logger.info(f"📸 Actualizando avatar para usuario {user_id}")
    
    # Verificar que el usuario solo pueda actualizar su propio avatar
    if current_user.id != user_id:
        logger.warning(f"⚠️ Usuario {current_user.id} intentó modificar avatar de {user_id}")
        return jsonify({
            'success': False,
            'error': 'No autorizado para modificar este perfil'
        }), 403
    
    # Obtener datos del request
    data = request.get_json()
    
    if not data:
        return jsonify({
            'success': False,
            'error': 'No se recibieron datos'
        }), 400
    
    foto_url = data.get('foto_url')
    
    if not foto_url:
        return jsonify({
            'success': False,
            'error': 'foto_url es requerido'
        }), 400
    
    # Validar que sea una URL de Cloudinary válida
    if not foto_url.startswith('https://res.cloudinary.com/'):
        logger.warning(f"⚠️ URL inválida recibida: {foto_url[:50]}...")
        return jsonify({
            'success': False,
            'error': 'URL de imagen no válida. Debe ser de Cloudinary.'
        }), 400
    
    # Validar longitud máxima
    if len(foto_url) > 500:
        return jsonify({
            'success': False,
            'error': 'URL demasiado larga'
        }), 400
    
    try:
        # Buscar el usuario en la base de datos
        usuario = Usuario.query.get(user_id)
        
        if not usuario:
            return jsonify({
                'success': False,
                'error': 'Usuario no encontrado'
            }), 404
        
        # Guardar URL anterior (por si necesitas eliminar la imagen vieja de Cloudinary)
        old_foto_url = usuario.foto_url
        
        # Actualizar el campo foto_url
        usuario.foto_url = foto_url
        
        # Guardar en base de datos
        db.session.commit()
        
        logger.info(f"✅ Avatar actualizado para usuario {user_id}")
        logger.info(f"   URL anterior: {old_foto_url}")
        logger.info(f"   URL nueva: {foto_url}")
        
        return jsonify({
            'success': True,
            'message': 'Avatar actualizado correctamente',
            'data': {
                'user_id': user_id,
                'foto_url': foto_url
            }
        }), 200
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"❌ Error actualizando avatar: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Error interno del servidor'
        }), 500


# ==========================================
# OBTENER AVATAR (OPCIONAL)
# ==========================================
@avatar_api_bp.route('/api/users/<int:user_id>/avatar', methods=['GET'])
@token_required
def get_avatar(current_user, user_id):
    """
    Obtiene la URL del avatar de un usuario
    """
    
    try:
        usuario = Usuario.query.get(user_id)
        
        if not usuario:
            return jsonify({
                'success': False,
                'error': 'Usuario no encontrado'
            }), 404
        
        return jsonify({
            'success': True,
            'data': {
                'user_id': user_id,
                'foto_url': usuario.foto_url,
                'tiene_foto': usuario.foto_url is not None
            }
        }), 200
        
    except Exception as e:
        logger.error(f"❌ Error obteniendo avatar: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Error interno del servidor'
        }), 500


# ==========================================
# ELIMINAR AVATAR
# ==========================================
@avatar_api_bp.route('/api/users/<int:user_id>/avatar', methods=['DELETE'])
@token_required
def delete_avatar(current_user, user_id):
    """
    Elimina la foto de perfil del usuario (la pone en NULL)
    """
    
    # Verificar autorización
    if current_user.id != user_id:
        return jsonify({
            'success': False,
            'error': 'No autorizado'
        }), 403
    
    try:
        usuario = Usuario.query.get(user_id)
        
        if not usuario:
            return jsonify({
                'success': False,
                'error': 'Usuario no encontrado'
            }), 404
        
        # Guardar URL para posible eliminación en Cloudinary
        old_url = usuario.foto_url
        
        # Eliminar referencia
        usuario.foto_url = None
        db.session.commit()
        
        logger.info(f"✅ Avatar eliminado para usuario {user_id}")
        
        # TODO: Opcional - Eliminar imagen de Cloudinary usando su API
        # if old_url:
        #     delete_from_cloudinary(old_url)
        
        return jsonify({
            'success': True,
            'message': 'Avatar eliminado correctamente'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"❌ Error eliminando avatar: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Error interno del servidor'
        }), 500