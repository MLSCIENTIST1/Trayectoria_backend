"""
═══════════════════════════════════════════════════════════════════════════════
TUKOMERCIO - ADMIN API v2.0
Sistema de administración usando Flask-Login (current_user)
═══════════════════════════════════════════════════════════════════════════════
"""

from flask import Blueprint, request, jsonify, g, make_response
from flask_login import current_user, login_required
from functools import wraps
from datetime import datetime
import json
import os
import logging

logger = logging.getLogger(__name__)

# ═══════════════════════════════════════════════════════════════════════════════
# BLUEPRINT SETUP
# ═══════════════════════════════════════════════════════════════════════════════

admin_bp = Blueprint('admin', __name__, url_prefix='/api/admin')


# ═══════════════════════════════════════════════════════════════════════════════
# CORS CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════════

ALLOWED_ORIGINS = [
    "https://tuko.pages.dev",
    "https://trayectoria-rxdc1.web.app",
    "https://mitrayectoria.web.app",
    "http://localhost:5001",
    "http://localhost:5173",
    "http://localhost:3000"
]


def build_cors_response(data=None, status=200):
    """Construye respuesta con headers CORS que permiten credentials."""
    if data is None:
        response = make_response('', 204)
    else:
        response = make_response(jsonify(data), status)
    
    origin = request.headers.get('Origin', '')
    
    if origin in ALLOWED_ORIGINS:
        response.headers['Access-Control-Allow-Origin'] = origin
        response.headers['Access-Control-Allow-Credentials'] = 'true'  # ← CRÍTICO
    
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS, PUT, DELETE'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, Accept'
    response.headers['Access-Control-Max-Age'] = '3600'
    
    return response


@admin_bp.before_request
def handle_preflight():
    """Maneja requests OPTIONS para CORS preflight."""
    if request.method == 'OPTIONS':
        response = make_response('', 204)
        origin = request.headers.get('Origin', '')
        if origin in ALLOWED_ORIGINS:
            response.headers['Access-Control-Allow-Origin'] = origin
            response.headers['Access-Control-Allow-Credentials'] = 'true'
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS, PUT, DELETE'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, Accept'
        response.headers['Access-Control-Max-Age'] = '3600'
        return response


@admin_bp.after_request
def add_cors_headers(response):
    """Agrega headers CORS a todas las respuestas."""
    origin = request.headers.get('Origin', '')
    if origin in ALLOWED_ORIGINS:
        response.headers['Access-Control-Allow-Origin'] = origin
        response.headers['Access-Control-Allow-Credentials'] = 'true'
    return response


# ═══════════════════════════════════════════════════════════════════════════════
# DATABASE CONNECTION
# ═══════════════════════════════════════════════════════════════════════════════

def get_db_connection():
    """Obtener conexión a la base de datos."""
    import psycopg2
    from psycopg2.extras import RealDictCursor
    
    DATABASE_URL = os.environ.get('DATABASE_URL')
    conn = psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)
    return conn


# ═══════════════════════════════════════════════════════════════════════════════
# AUTH HELPERS
# ═══════════════════════════════════════════════════════════════════════════════

def get_current_user_email():
    """Obtiene el email del usuario actual usando Flask-Login."""
    if current_user.is_authenticated:
        return current_user.correo.lower() if current_user.correo else None
    return None


def is_admin(email):
    """Verifica si un email está en la lista de administradores."""
    if not email:
        return False, None
    
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        cur.execute("""
            SELECT id, email, nombre, rol, permisos, activo
            FROM administradores
            WHERE LOWER(email) = LOWER(%s) AND activo = true
        """, (email,))
        
        admin = cur.fetchone()
        cur.close()
        conn.close()
        
        if admin:
            return True, dict(admin)
        return False, None
        
    except Exception as e:
        logger.error(f"Error verificando admin: {e}")
        return False, None


def admin_required(f):
    """Decorator que requiere que el usuario sea administrador."""
    @wraps(f)
    @login_required
    def decorated(*args, **kwargs):
        email = get_current_user_email()
        
        if not email:
            return jsonify({'error': 'No autorizado', 'is_admin': False}), 401
        
        is_adm, admin_data = is_admin(email)
        
        if not is_adm:
            return jsonify({'error': 'Acceso denegado. No eres administrador.', 'is_admin': False}), 403
        
        g.user_email = email
        g.admin = admin_data
        
        return f(*args, **kwargs)
    return decorated


def superadmin_required(f):
    """Decorator que requiere que el usuario sea superadmin."""
    @wraps(f)
    @login_required
    def decorated(*args, **kwargs):
        email = get_current_user_email()
        
        if not email:
            return jsonify({'error': 'No autorizado'}), 401
        
        is_adm, admin_data = is_admin(email)
        
        if not is_adm or admin_data.get('rol') != 'superadmin':
            return jsonify({'error': 'Acceso denegado. Se requiere rol de superadmin.'}), 403
        
        g.user_email = email
        g.admin = admin_data
        
        return f(*args, **kwargs)
    return decorated


# ═══════════════════════════════════════════════════════════════════════════════
# VERIFICACIÓN DE ADMIN (público, sin login_required)
# ═══════════════════════════════════════════════════════════════════════════════

@admin_bp.route('/check', methods=['GET', 'OPTIONS'])
def check_admin():
    """
    GET /api/admin/check
    Verifica si el usuario actual es administrador.
    Usado para mostrar/ocultar el botón de admin en el navbar.
    """
    if request.method == 'OPTIONS':
        return build_cors_response()
    
    # Verificar si hay sesión activa
    if not current_user.is_authenticated:
        return build_cors_response({
            'is_admin': False,
            'message': 'No autenticado'
        }, 200)
    
    email = get_current_user_email()
    
    if not email:
        return build_cors_response({
            'is_admin': False,
            'message': 'Email no disponible'
        }, 200)
    
    is_adm, admin_data = is_admin(email)
    
    if is_adm:
        return build_cors_response({
            'is_admin': True,
            'admin': {
                'email': admin_data['email'],
                'nombre': admin_data['nombre'],
                'rol': admin_data['rol'],
                'permisos': admin_data['permisos']
            }
        }, 200)
    
    return build_cors_response({
        'is_admin': False,
        'message': 'No eres administrador'
    }, 200)


# ═══════════════════════════════════════════════════════════════════════════════
# GESTIÓN DE ADMINISTRADORES
# ═══════════════════════════════════════════════════════════════════════════════

@admin_bp.route('/list', methods=['GET'])
@admin_required
def list_admins():
    """
    GET /api/admin/list
    Lista todos los administradores.
    """
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        cur.execute("""
            SELECT id, email, nombre, rol, permisos, activo, created_at
            FROM administradores
            ORDER BY created_at ASC
        """)
        
        admins = cur.fetchall()
        cur.close()
        conn.close()
        
        return jsonify({
            'admins': [dict(a) for a in admins],
            'total': len(admins)
        }), 200
        
    except Exception as e:
        logger.error(f"Error listando admins: {e}")
        return jsonify({'error': str(e)}), 500


@admin_bp.route('/add', methods=['POST'])
@superadmin_required
def add_admin():
    """
    POST /api/admin/add
    Agregar nuevo administrador (solo superadmin).
    """
    try:
        data = request.get_json()
        
        email = data.get('email', '').lower().strip()
        nombre = data.get('nombre', '')
        rol = data.get('rol', 'admin')
        permisos = data.get('permisos', ['challenges', 'usuarios', 'negocios', 'reportes'])
        
        if not email:
            return jsonify({'error': 'Email es requerido'}), 400
        
        # No permitir crear superadmins desde la API
        if rol == 'superadmin':
            rol = 'admin'
        
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Verificar si ya existe
        cur.execute("SELECT id FROM administradores WHERE LOWER(email) = LOWER(%s)", (email,))
        if cur.fetchone():
            cur.close()
            conn.close()
            return jsonify({'error': 'Este email ya está registrado como administrador'}), 400
        
        # Insertar nuevo admin
        cur.execute("""
            INSERT INTO administradores (email, nombre, rol, permisos, created_by)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING id, email, nombre, rol, permisos, activo, created_at
        """, (email, nombre, rol, json.dumps(permisos), g.admin['id']))
        
        new_admin = cur.fetchone()
        conn.commit()
        cur.close()
        conn.close()
        
        return jsonify({
            'success': True,
            'message': f'Administrador {email} agregado exitosamente',
            'admin': dict(new_admin)
        }), 201
        
    except Exception as e:
        logger.error(f"Error agregando admin: {e}")
        return jsonify({'error': str(e)}), 500


@admin_bp.route('/remove/<int:admin_id>', methods=['DELETE'])
@superadmin_required
def remove_admin(admin_id):
    """
    DELETE /api/admin/remove/<id>
    Desactivar un administrador (solo superadmin).
    """
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Verificar que existe y no es superadmin
        cur.execute("SELECT id, email, rol FROM administradores WHERE id = %s", (admin_id,))
        admin_to_remove = cur.fetchone()
        
        if not admin_to_remove:
            cur.close()
            conn.close()
            return jsonify({'error': 'Administrador no encontrado'}), 404
        
        if admin_to_remove['rol'] == 'superadmin':
            cur.close()
            conn.close()
            return jsonify({'error': 'No se puede eliminar a un superadmin'}), 403
        
        if admin_to_remove['email'].lower() == g.user_email.lower():
            cur.close()
            conn.close()
            return jsonify({'error': 'No puedes eliminarte a ti mismo'}), 403
        
        # Desactivar
        cur.execute("""
            UPDATE administradores 
            SET activo = false, updated_at = CURRENT_TIMESTAMP
            WHERE id = %s
        """, (admin_id,))
        
        conn.commit()
        cur.close()
        conn.close()
        
        return jsonify({
            'success': True,
            'message': f'Administrador {admin_to_remove["email"]} desactivado'
        }), 200
        
    except Exception as e:
        logger.error(f"Error removiendo admin: {e}")
        return jsonify({'error': str(e)}), 500


@admin_bp.route('/reactivate/<int:admin_id>', methods=['PUT'])
@superadmin_required
def reactivate_admin(admin_id):
    """
    PUT /api/admin/reactivate/<id>
    Reactivar un administrador desactivado.
    """
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        cur.execute("""
            UPDATE administradores 
            SET activo = true, updated_at = CURRENT_TIMESTAMP
            WHERE id = %s
            RETURNING email
        """, (admin_id,))
        
        result = cur.fetchone()
        
        if not result:
            cur.close()
            conn.close()
            return jsonify({'error': 'Administrador no encontrado'}), 404
        
        conn.commit()
        cur.close()
        conn.close()
        
        return jsonify({
            'success': True,
            'message': f'Administrador {result["email"]} reactivado'
        }), 200
        
    except Exception as e:
        logger.error(f"Error reactivando admin: {e}")
        return jsonify({'error': str(e)}), 500


# ═══════════════════════════════════════════════════════════════════════════════
# GESTIÓN DE CHALLENGES
# ═══════════════════════════════════════════════════════════════════════════════

@admin_bp.route('/challenges', methods=['GET'])
@admin_required
def list_challenges():
    """
    GET /api/admin/challenges
    Lista todos los challenges con estadísticas.
    """
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        cur.execute("""
            SELECT 
                c.*,
                (SELECT COUNT(*) FROM challenge_participaciones WHERE challenge_id = c.id) as total_participaciones,
                (SELECT COUNT(*) FROM challenge_participaciones WHERE challenge_id = c.id AND estado = 'aprobado') as participaciones_aprobadas,
                (SELECT COUNT(*) FROM challenge_participaciones WHERE challenge_id = c.id AND estado = 'pendiente') as participaciones_pendientes,
                (SELECT COUNT(*) FROM challenge_votos cv 
                 JOIN challenge_participaciones cp ON cp.id = cv.participacion_id 
                 WHERE cp.challenge_id = c.id) as total_votos
            FROM challenges c
            ORDER BY c.created_at DESC
        """)
        
        challenges = cur.fetchall()
        cur.close()
        conn.close()
        
        result = []
        for ch in challenges:
            ch = dict(ch)
            ch['premios'] = ch.get('premios_json') or []
            ch['reglas'] = ch.get('reglas_json') or []
            result.append(ch)
        
        return jsonify({
            'challenges': result,
            'total': len(result)
        }), 200
        
    except Exception as e:
        logger.error(f"Error listando challenges: {e}")
        return jsonify({'error': str(e)}), 500


@admin_bp.route('/challenges', methods=['POST'])
@admin_required
def create_challenge():
    """
    POST /api/admin/challenges
    Crear nuevo challenge.
    """
    try:
        data = request.get_json()
        
        required = ['nombre', 'hashtag', 'fecha_inicio', 'fecha_fin']
        for field in required:
            if field not in data:
                return jsonify({'error': f'{field} es requerido'}), 400
        
        conn = get_db_connection()
        cur = conn.cursor()
        
        cur.execute("""
            INSERT INTO challenges (
                nombre, hashtag, descripcion, fecha_inicio, fecha_fin,
                premios_json, reglas_json, imagen_banner, video_promo_url,
                estado, max_participantes, max_videos_por_negocio, duracion_max_video,
                created_by
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
            )
            RETURNING id
        """, (
            data.get('nombre'),
            data.get('hashtag'),
            data.get('descripcion', ''),
            data.get('fecha_inicio'),
            data.get('fecha_fin'),
            json.dumps(data.get('premios', [])),
            json.dumps(data.get('reglas', [])),
            data.get('imagen_banner'),
            data.get('video_promo_url'),
            data.get('estado', 'borrador'),
            data.get('max_participantes', 10000),
            data.get('max_videos_por_negocio', 3),
            data.get('duracion_max_video', 15),
            g.admin['id']
        ))
        
        new_id = cur.fetchone()['id']
        conn.commit()
        cur.close()
        conn.close()
        
        return jsonify({
            'success': True,
            'message': 'Challenge creado exitosamente',
            'challenge_id': new_id
        }), 201
        
    except Exception as e:
        logger.error(f"Error creando challenge: {e}")
        return jsonify({'error': str(e)}), 500


@admin_bp.route('/challenges/<int:challenge_id>', methods=['GET'])
@admin_required
def get_challenge(challenge_id):
    """
    GET /api/admin/challenges/<id>
    Obtener detalles de un challenge.
    """
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        cur.execute("SELECT * FROM challenges WHERE id = %s", (challenge_id,))
        challenge = cur.fetchone()
        
        if not challenge:
            cur.close()
            conn.close()
            return jsonify({'error': 'Challenge no encontrado'}), 404
        
        challenge = dict(challenge)
        challenge['premios'] = challenge.get('premios_json') or []
        challenge['reglas'] = challenge.get('reglas_json') or []
        
        cur.close()
        conn.close()
        
        return jsonify(challenge), 200
        
    except Exception as e:
        logger.error(f"Error obteniendo challenge: {e}")
        return jsonify({'error': str(e)}), 500


@admin_bp.route('/challenges/<int:challenge_id>', methods=['PUT'])
@admin_required
def update_challenge(challenge_id):
    """
    PUT /api/admin/challenges/<id>
    Actualizar challenge.
    """
    try:
        data = request.get_json()
        
        conn = get_db_connection()
        cur = conn.cursor()
        
        updates = []
        values = []
        
        fields_map = {
            'nombre': 'nombre',
            'hashtag': 'hashtag',
            'descripcion': 'descripcion',
            'fecha_inicio': 'fecha_inicio',
            'fecha_fin': 'fecha_fin',
            'imagen_banner': 'imagen_banner',
            'video_promo_url': 'video_promo_url',
            'estado': 'estado',
            'max_participantes': 'max_participantes',
            'max_videos_por_negocio': 'max_videos_por_negocio',
            'duracion_max_video': 'duracion_max_video'
        }
        
        for key, col in fields_map.items():
            if key in data:
                updates.append(f"{col} = %s")
                values.append(data[key])
        
        if 'premios' in data:
            updates.append("premios_json = %s")
            values.append(json.dumps(data['premios']))
        
        if 'reglas' in data:
            updates.append("reglas_json = %s")
            values.append(json.dumps(data['reglas']))
        
        if not updates:
            cur.close()
            conn.close()
            return jsonify({'error': 'No hay datos para actualizar'}), 400
        
        updates.append("updated_at = CURRENT_TIMESTAMP")
        values.append(challenge_id)
        
        query = f"UPDATE challenges SET {', '.join(updates)} WHERE id = %s RETURNING id"
        
        cur.execute(query, values)
        result = cur.fetchone()
        
        if not result:
            cur.close()
            conn.close()
            return jsonify({'error': 'Challenge no encontrado'}), 404
        
        conn.commit()
        cur.close()
        conn.close()
        
        return jsonify({
            'success': True,
            'message': 'Challenge actualizado exitosamente'
        }), 200
        
    except Exception as e:
        logger.error(f"Error actualizando challenge: {e}")
        return jsonify({'error': str(e)}), 500


@admin_bp.route('/challenges/<int:challenge_id>', methods=['DELETE'])
@superadmin_required
def delete_challenge(challenge_id):
    """
    DELETE /api/admin/challenges/<id>
    Eliminar challenge (solo superadmin, solo si no tiene participaciones).
    """
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        cur.execute("""
            SELECT COUNT(*) as total FROM challenge_participaciones WHERE challenge_id = %s
        """, (challenge_id,))
        
        count = cur.fetchone()['total']
        
        if count > 0:
            cur.close()
            conn.close()
            return jsonify({
                'error': f'No se puede eliminar. El challenge tiene {count} participaciones.'
            }), 400
        
        cur.execute("DELETE FROM challenges WHERE id = %s RETURNING nombre", (challenge_id,))
        result = cur.fetchone()
        
        if not result:
            cur.close()
            conn.close()
            return jsonify({'error': 'Challenge no encontrado'}), 404
        
        conn.commit()
        cur.close()
        conn.close()
        
        return jsonify({
            'success': True,
            'message': f'Challenge "{result["nombre"]}" eliminado'
        }), 200
        
    except Exception as e:
        logger.error(f"Error eliminando challenge: {e}")
        return jsonify({'error': str(e)}), 500


# ═══════════════════════════════════════════════════════════════════════════════
# GESTIÓN DE PARTICIPACIONES
# ═══════════════════════════════════════════════════════════════════════════════

@admin_bp.route('/challenges/<int:challenge_id>/participaciones', methods=['GET'])
@admin_required
def list_participaciones(challenge_id):
    """
    GET /api/admin/challenges/<id>/participaciones
    Lista participaciones de un challenge con filtros.
    """
    try:
        estado = request.args.get('estado')
        limit = min(request.args.get('limit', 50, type=int), 100)
        offset = request.args.get('offset', 0, type=int)
        
        conn = get_db_connection()
        cur = conn.cursor()
        
        query = """
            SELECT 
                cp.id,
                cp.video_id,
                cp.negocio_id,
                cp.estado,
                cp.motivo_rechazo,
                cp.created_at,
                v.titulo as video_titulo,
                v.thumbnail_url,
                v.duracion,
                v.video_url,
                n.nombre as negocio_nombre,
                n.logo_url as negocio_logo,
                (SELECT COUNT(*) FROM challenge_votos WHERE participacion_id = cp.id) as votos
            FROM challenge_participaciones cp
            LEFT JOIN videos v ON v.id = cp.video_id
            LEFT JOIN negocios n ON n.id = cp.negocio_id
            WHERE cp.challenge_id = %s
        """
        params = [challenge_id]
        
        if estado:
            query += " AND cp.estado = %s"
            params.append(estado)
        
        query += " ORDER BY cp.created_at DESC LIMIT %s OFFSET %s"
        params.extend([limit, offset])
        
        cur.execute(query, params)
        participaciones = cur.fetchall()
        
        cur.execute("""
            SELECT 
                COUNT(*) as total,
                COUNT(*) FILTER (WHERE estado = 'pendiente') as pendientes,
                COUNT(*) FILTER (WHERE estado = 'aprobado') as aprobados,
                COUNT(*) FILTER (WHERE estado = 'rechazado') as rechazados
            FROM challenge_participaciones
            WHERE challenge_id = %s
        """, (challenge_id,))
        
        counts = cur.fetchone()
        
        cur.close()
        conn.close()
        
        return jsonify({
            'participaciones': [dict(p) for p in participaciones],
            'counts': dict(counts),
            'pagination': {
                'limit': limit,
                'offset': offset
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Error listando participaciones: {e}")
        return jsonify({'error': str(e)}), 500


@admin_bp.route('/participaciones/<int:participacion_id>/estado', methods=['PUT'])
@admin_required
def update_participacion_estado(participacion_id):
    """
    PUT /api/admin/participaciones/<id>/estado
    Cambiar estado de una participación.
    """
    try:
        data = request.get_json()
        nuevo_estado = data.get('estado')
        motivo = data.get('motivo', '')
        
        if nuevo_estado not in ['pendiente', 'aprobado', 'rechazado', 'descalificado']:
            return jsonify({'error': 'Estado inválido'}), 400
        
        conn = get_db_connection()
        cur = conn.cursor()
        
        cur.execute("""
            UPDATE challenge_participaciones
            SET estado = %s, motivo_rechazo = %s, updated_at = CURRENT_TIMESTAMP
            WHERE id = %s
            RETURNING id, video_id, negocio_id
        """, (nuevo_estado, motivo if nuevo_estado in ['rechazado', 'descalificado'] else None, participacion_id))
        
        result = cur.fetchone()
        
        if not result:
            cur.close()
            conn.close()
            return jsonify({'error': 'Participación no encontrada'}), 404
        
        conn.commit()
        cur.close()
        conn.close()
        
        return jsonify({
            'success': True,
            'message': f'Participación actualizada a "{nuevo_estado}"'
        }), 200
        
    except Exception as e:
        logger.error(f"Error actualizando participación: {e}")
        return jsonify({'error': str(e)}), 500


# ═══════════════════════════════════════════════════════════════════════════════
# ESTADÍSTICAS GENERALES
# ═══════════════════════════════════════════════════════════════════════════════

@admin_bp.route('/stats', methods=['GET'])
@admin_required
def get_admin_stats():
    """
    GET /api/admin/stats
    Estadísticas generales del sistema.
    """
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        stats = {}
        
        cur.execute("""
            SELECT 
                COUNT(*) as total,
                COUNT(*) FILTER (WHERE estado = 'activo') as activos,
                COUNT(*) FILTER (WHERE estado = 'borrador') as borradores,
                COUNT(*) FILTER (WHERE estado = 'finalizado') as finalizados
            FROM challenges
        """)
        stats['challenges'] = dict(cur.fetchone())
        
        cur.execute("""
            SELECT 
                COUNT(*) as total,
                COUNT(*) FILTER (WHERE estado = 'aprobado') as aprobadas,
                COUNT(*) FILTER (WHERE estado = 'pendiente') as pendientes
            FROM challenge_participaciones
        """)
        stats['participaciones'] = dict(cur.fetchone())
        
        cur.execute("SELECT COUNT(*) as total FROM challenge_votos")
        stats['votos'] = cur.fetchone()['total']
        
        cur.execute("SELECT COUNT(*) as total FROM administradores WHERE activo = true")
        stats['admins'] = cur.fetchone()['total']
        
        cur.execute("""
            SELECT c.id, c.nombre, c.estado, COUNT(cp.id) as participaciones
            FROM challenges c
            LEFT JOIN challenge_participaciones cp ON cp.challenge_id = c.id
            GROUP BY c.id
            ORDER BY participaciones DESC
            LIMIT 5
        """)
        stats['top_challenges'] = [dict(row) for row in cur.fetchall()]
        
        cur.close()
        conn.close()
        
        return jsonify(stats), 200
        
    except Exception as e:
        logger.error(f"Error obteniendo stats: {e}")
        return jsonify({'error': str(e)}), 500