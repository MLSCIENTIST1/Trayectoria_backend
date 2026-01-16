"""
BizFlow Studio - Avatar API
Endpoint para actualizar foto de perfil de usuario
Integrado con Cloudinary

Ubicación: src/api/profile/avatar_api.py
"""

from flask import Blueprint, request, jsonify
import logging

# Importar decorador de autenticación
from src.api.auth.auth_system import token_required

# Importar conexión a base de datos
from src.database import get_db_connection

logger = logging.getLogger(__name__)

# ==========================================
# BLUEPRINT
# ==========================================
avatar_api_bp = Blueprint('avatar_api', __name__)


# ==========================================
# ACTUALIZAR AVATAR
# PATCH /api/users/<user_id>/avatar
# ==========================================
@avatar_api_bp.route('/users/<int:user_id>/avatar', methods=['PATCH'])
@token_required
def update_avatar(current_user, user_id):
    """
    Actualiza la foto de perfil del usuario.
    
    La imagen ya fue subida a Cloudinary desde el frontend.
    Este endpoint solo guarda la URL en la base de datos.
    
    Headers requeridos:
        - Authorization: Bearer <token>
    
    Body:
        {
            "foto_url": "https://res.cloudinary.com/dp50v0bwj/image/upload/..."
        }
    """
    
    logger.info(f"📸 Solicitud de actualización de avatar para usuario {user_id}")
    
    # ==========================================
    # 1. VERIFICAR AUTORIZACIÓN
    # ==========================================
    current_user_id = None
    
    # Manejar diferentes formatos de current_user
    if hasattr(current_user, 'id_usuario'):
        current_user_id = current_user.id_usuario
    elif hasattr(current_user, 'id'):
        current_user_id = current_user.id
    elif hasattr(current_user, 'get'):
        current_user_id = current_user.get('id_usuario') or current_user.get('id') or current_user.get('usuario_id')
    elif isinstance(current_user, dict):
        current_user_id = current_user.get('id_usuario') or current_user.get('id') or current_user.get('usuario_id')
    
    if current_user_id is None:
        logger.error("❌ No se pudo obtener ID del usuario actual")
        return jsonify({
            'success': False,
            'error': 'Error de autenticación'
        }), 401
    
    if int(current_user_id) != int(user_id):
        logger.warning(f"⚠️ Usuario {current_user_id} intentó actualizar avatar de usuario {user_id}")
        return jsonify({
            'success': False,
            'error': 'No autorizado para actualizar este perfil'
        }), 403
    
    # ==========================================
    # 2. VALIDAR DATOS DE ENTRADA
    # ==========================================
    data = request.get_json()
    
    if not data:
        return jsonify({
            'success': False,
            'error': 'Se requiere un cuerpo JSON'
        }), 400
    
    foto_url = data.get('foto_url')
    
    if not foto_url:
        return jsonify({
            'success': False,
            'error': 'foto_url es requerido'
        }), 400
    
    # Validar que sea una URL de Cloudinary válida
    if not foto_url.startswith('https://res.cloudinary.com/'):
        logger.warning(f"⚠️ URL de imagen no válida: {foto_url[:50]}...")
        return jsonify({
            'success': False,
            'error': 'URL de imagen no válida. Debe ser una URL de Cloudinary.'
        }), 400
    
    # Validar longitud máxima
    if len(foto_url) > 500:
        return jsonify({
            'success': False,
            'error': 'URL demasiado larga (máximo 500 caracteres)'
        }), 400
    
    # ==========================================
    # 3. ACTUALIZAR EN BASE DE DATOS
    # ==========================================
    conn = None
    cursor = None
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Actualizar foto_url en la tabla usuarios
        # NOTA: El ID es id_usuario, no id
        cursor.execute("""
            UPDATE usuarios 
            SET foto_url = %s,
                updated_at = NOW()
            WHERE id_usuario = %s
            RETURNING id_usuario, nombre, correo, foto_url
        """, (foto_url, user_id))
        
        result = cursor.fetchone()
        
        if not result:
            logger.error(f"❌ Usuario {user_id} no encontrado en base de datos")
            return jsonify({
                'success': False,
                'error': 'Usuario no encontrado'
            }), 404
        
        conn.commit()
        
        logger.info(f"✅ Avatar actualizado para usuario {user_id}: {foto_url[:60]}...")
        
        return jsonify({
            'success': True,
            'message': 'Avatar actualizado correctamente',
            'data': {
                'id': result[0],
                'nombre': result[1],
                'email': result[2],
                'foto_url': result[3]
            }
        }), 200
        
    except Exception as e:
        logger.error(f"❌ Error actualizando avatar: {str(e)}")
        import traceback
        traceback.print_exc()
        if conn:
            conn.rollback()
        return jsonify({
            'success': False,
            'error': 'Error interno del servidor'
        }), 500
        
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


# ==========================================
# OBTENER AVATAR
# GET /api/users/<user_id>/avatar
# ==========================================
@avatar_api_bp.route('/users/<int:user_id>/avatar', methods=['GET'])
def get_avatar(user_id):
    """
    Obtiene la URL del avatar de un usuario.
    No requiere autenticación (es información pública).
    """
    
    conn = None
    cursor = None
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT foto_url, nombre 
            FROM usuarios 
            WHERE id_usuario = %s
        """, (user_id,))
        
        result = cursor.fetchone()
        
        if not result:
            return jsonify({
                'success': False,
                'error': 'Usuario no encontrado'
            }), 404
        
        return jsonify({
            'success': True,
            'data': {
                'foto_url': result[0],
                'nombre': result[1],
                'tiene_foto': result[0] is not None
            }
        }), 200
        
    except Exception as e:
        logger.error(f"❌ Error obteniendo avatar: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Error interno del servidor'
        }), 500
        
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


# ==========================================
# ELIMINAR AVATAR
# DELETE /api/users/<user_id>/avatar
# ==========================================
@avatar_api_bp.route('/users/<int:user_id>/avatar', methods=['DELETE'])
@token_required
def delete_avatar(current_user, user_id):
    """
    Elimina la foto de perfil del usuario (la pone en NULL).
    """
    
    # Verificar autorización
    current_user_id = None
    if hasattr(current_user, 'id_usuario'):
        current_user_id = current_user.id_usuario
    elif hasattr(current_user, 'id'):
        current_user_id = current_user.id
    elif isinstance(current_user, dict):
        current_user_id = current_user.get('id_usuario') or current_user.get('id')
    
    if current_user_id is None or int(current_user_id) != int(user_id):
        return jsonify({
            'success': False,
            'error': 'No autorizado'
        }), 403
    
    conn = None
    cursor = None
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE usuarios 
            SET foto_url = NULL,
                updated_at = NOW()
            WHERE id_usuario = %s
        """, (user_id,))
        
        conn.commit()
        
        logger.info(f"✅ Avatar eliminado para usuario {user_id}")
        
        return jsonify({
            'success': True,
            'message': 'Avatar eliminado correctamente'
        }), 200
        
    except Exception as e:
        logger.error(f"❌ Error eliminando avatar: {str(e)}")
        if conn:
            conn.rollback()
        return jsonify({
            'success': False,
            'error': 'Error interno del servidor'
        }), 500
        
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()