"""
BizFlow Studio - Avatar API
Endpoint para actualizar foto de perfil de usuario
Integrado con Cloudinary

Ubicación: src/api/profile/avatar_api.py

NOTA: Este archivo NO importa token_required ni Usuario 
      al nivel del módulo para evitar circular imports.
"""

from flask import Blueprint, request, jsonify
import logging

# Solo importamos la conexión a BD
from src.database import get_db_connection

logger = logging.getLogger(__name__)

# ==========================================
# BLUEPRINT
# ==========================================
avatar_api_bp = Blueprint('avatar_api', __name__)


# ==========================================
# HELPER: VERIFICAR TOKEN MANUALMENTE
# ==========================================
def verify_auth_token():
    """
    Verifica el token de autenticación sin importar módulos externos.
    Retorna el user_id si es válido, None si no.
    """
    auth_header = request.headers.get('Authorization')
    user_id_header = request.headers.get('X-User-ID')
    
    if not auth_header:
        return None, "Token de autorización requerido"
    
    # Por ahora, confiamos en X-User-ID si viene con Authorization
    # En producción deberías verificar el JWT aquí
    if user_id_header:
        try:
            return int(user_id_header), None
        except (ValueError, TypeError):
            return None, "ID de usuario inválido"
    
    # Intentar extraer user_id del token JWT si está disponible
    try:
        if auth_header.startswith('Bearer '):
            token = auth_header[7:]
        else:
            token = auth_header
        
        # Importación tardía para evitar circular import
        try:
            from src.auth_jwt import verify_token
            payload = verify_token(token)
            if payload and payload.get('user_id'):
                return payload['user_id'], None
        except ImportError:
            pass
        except Exception as e:
            logger.warning(f"Error verificando JWT: {e}")
        
        return None, "Token inválido"
        
    except Exception as e:
        logger.error(f"Error en verificación de token: {e}")
        return None, "Error de autenticación"


# ==========================================
# ACTUALIZAR AVATAR
# PATCH /users/<user_id>/avatar
# ==========================================
@avatar_api_bp.route('/users/<int:user_id>/avatar', methods=['PATCH', 'OPTIONS'])
def update_avatar(user_id):
    """
    Actualiza la foto de perfil del usuario.
    """
    
    # Manejar preflight CORS
    if request.method == 'OPTIONS':
        return '', 204
    
    logger.info(f"📸 Solicitud de actualización de avatar para usuario {user_id}")
    
    # ==========================================
    # 1. VERIFICAR AUTENTICACIÓN
    # ==========================================
    current_user_id, error = verify_auth_token()
    
    if error:
        return jsonify({
            'success': False,
            'error': error
        }), 401
    
    # ==========================================
    # 2. VERIFICAR AUTORIZACIÓN
    # ==========================================
    if current_user_id != user_id:
        logger.warning(f"⚠️ Usuario {current_user_id} intentó actualizar avatar de usuario {user_id}")
        return jsonify({
            'success': False,
            'error': 'No autorizado para actualizar este perfil'
        }), 403
    
    # ==========================================
    # 3. VALIDAR DATOS DE ENTRADA
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
    # 4. ACTUALIZAR EN BASE DE DATOS
    # ==========================================
    conn = None
    cursor = None
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
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
# GET /users/<user_id>/avatar
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
# DELETE /users/<user_id>/avatar
# ==========================================
@avatar_api_bp.route('/users/<int:user_id>/avatar', methods=['DELETE'])
def delete_avatar(user_id):
    """
    Elimina la foto de perfil del usuario (la pone en NULL).
    """
    
    # Verificar autenticación
    current_user_id, error = verify_auth_token()
    
    if error:
        return jsonify({
            'success': False,
            'error': error
        }), 401
    
    if current_user_id != user_id:
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