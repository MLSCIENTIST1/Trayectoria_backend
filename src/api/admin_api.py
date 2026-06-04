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
    "https://tukomercio.co",          # A-SEC-1: faltaba el dominio de producción
    "https://www.tukomercio.co",
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
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, Accept, X-User-ID, X-Business-ID, X-Session-FP, Cache-Control, Pragma'
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
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, Accept, X-User-ID, X-Business-ID, X-Session-FP, Cache-Control, Pragma'
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
# PERMISOS GRANULARES POR MÓDULO (Admin Panel A3)
# ═══════════════════════════════════════════════════════════════════════════════

# Catálogo canónico de módulos del panel. La clave coincide con `data-section`
# del frontend para poder ocultar secciones según los permisos del admin.
MODULOS_PERMISOS = [
    {'key': 'challenges',      'label': 'Challenges',          'grupo': 'Gestión'},
    {'key': 'participaciones', 'label': 'Participaciones',     'grupo': 'Gestión'},
    {'key': 'reportes',        'label': 'Reportes de errores', 'grupo': 'Gestión'},
    {'key': 'features',        'label': 'Feature Flags',       'grupo': 'Plataforma'},
    {'key': 'planes',          'label': 'Planes',              'grupo': 'Plataforma'},
    {'key': 'negocios',        'label': 'Negocios',            'grupo': 'Plataforma'},
    {'key': 'usuarios',        'label': 'Usuarios',            'grupo': 'Usuarios'},
    {'key': 'gamificacion',    'label': 'Gamificación',        'grupo': 'Gamificación'},
    {'key': 'insignias',       'label': 'Insignias',           'grupo': 'Gamificación'},
    {'key': 'eventos',         'label': 'Eventos',             'grupo': 'Gamificación'},
    {'key': 'economia',        'label': 'Economía / TuKoins',  'grupo': 'Gamificación'},
    {'key': 'pagos',           'label': 'Pagos',               'grupo': 'Finanzas'},
    {'key': 'auditoria',       'label': 'Auditoría',           'grupo': 'Configuración'},
    {'key': 'admins',          'label': 'Administradores',     'grupo': 'Configuración'},
    {'key': 'configuracion',   'label': 'Configuración',       'grupo': 'Configuración'},
]
PERMISOS_VALIDOS = {m['key'] for m in MODULOS_PERMISOS}


def admin_tiene_permiso(admin_data, permiso):
    """Función PURA: ¿este admin tiene el permiso? El superadmin siempre sí."""
    if not admin_data:
        return False
    if admin_data.get('rol') == 'superadmin':
        return True
    return permiso in (admin_data.get('permisos') or [])


def requiere_permiso(permiso):
    """
    Decorator para proteger un endpoint por permiso de módulo.
    superadmin pasa siempre; un admin necesita el permiso en su lista.
    Listo para que los nuevos módulos (gamificación, insignias, pagos…) lo adopten.
    """
    def deco(f):
        @wraps(f)
        @login_required
        def inner(*args, **kwargs):
            email = get_current_user_email()
            if not email:
                return jsonify({'error': 'No autorizado'}), 401
            is_adm, admin_data = is_admin(email)
            if not is_adm:
                return jsonify({'error': 'Acceso denegado. No eres administrador.'}), 403
            if not admin_tiene_permiso(admin_data, permiso):
                return jsonify({'error': f'No tienes permiso para el módulo: {permiso}'}), 403
            g.user_email = email
            g.admin = admin_data
            return f(*args, **kwargs)
        return inner
    return deco


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

        registrar_auditoria('crear', 'administrador', new_admin['id'],
                            {'email': email, 'rol': rol, 'permisos': permisos})
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

        registrar_auditoria('desactivar', 'administrador', admin_id,
                            {'email': admin_to_remove['email']})
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

        registrar_auditoria('activar', 'administrador', admin_id,
                            {'email': result['email']})
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

        # Conteo de usuarios registrados
        cur.execute("SELECT COUNT(*) as total FROM usuarios WHERE active = true")
        stats['usuarios'] = cur.fetchone()['total']

        cur.close()
        conn.close()

        return jsonify(stats), 200

    except Exception as e:
        logger.error(f"Error obteniendo stats: {e}")
        return jsonify({'error': str(e)}), 500


@admin_bp.route('/metrics', methods=['GET'])
@admin_required
def get_admin_metrics():
    """
    GET /api/admin/metrics
    KPIs reales de la plataforma para el dashboard (A4).
    Cada métrica es tolerante a fallos: si una consulta falla, devuelve 0
    y las demás siguen funcionando.
    """
    conn = None
    metrics = {}
    try:
        conn = get_db_connection()

        def escalar(sql, default=0):
            try:
                cur = conn.cursor()
                cur.execute(sql)
                row = cur.fetchone()
                cur.close()
                if not row:
                    return default
                val = list(row.values())[0]
                return val if val is not None else default
            except Exception as e:
                logger.warning(f"[metrics] consulta falló: {e}")
                try:
                    conn.rollback()
                except Exception:
                    pass
                return default

        # ── Usuarios y negocios ──
        metrics['usuarios_total']   = int(escalar("SELECT COUNT(*) AS v FROM usuarios WHERE active = true"))
        metrics['negocios_total']   = int(escalar("SELECT COUNT(*) AS v FROM negocios"))
        metrics['negocios_activos'] = int(escalar("SELECT COUNT(*) AS v FROM negocios WHERE activo = true"))
        metrics['negocios_publicos']= int(escalar("SELECT COUNT(*) AS v FROM negocios WHERE perfil_publico = true"))

        # ── Pedidos / ventas ──
        metrics['pedidos_entregados'] = int(escalar("SELECT COUNT(*) AS v FROM pedidos WHERE estado = 'entregado'"))
        metrics['pedidos_total']      = int(escalar("SELECT COUNT(*) AS v FROM pedidos"))
        metrics['ventas_volumen']     = float(escalar(
            "SELECT COALESCE(SUM(COALESCE(subtotal,0) - COALESCE(descuento,0)),0) AS v "
            "FROM pedidos WHERE estado = 'entregado'"))

        # ── Gamificación / economía ──
        metrics['xp_repartido']      = int(escalar("SELECT COALESCE(SUM(xp_total),0) AS v FROM negocio_gamificacion"))
        metrics['tukoins_circulando']= int(escalar("SELECT COALESCE(SUM(tukoins),0) AS v FROM negocio_gamificacion"))
        metrics['negocios_jugando']  = int(escalar("SELECT COUNT(*) AS v FROM negocio_gamificacion WHERE xp_total > 0"))
        metrics['insignias_otorgadas'] = int(escalar(
            "SELECT COUNT(*) AS v FROM negocio_badges_obtenidos WHERE activo IS TRUE OR activo IS NULL"))
        metrics['onboarding_completos'] = int(escalar(
            "SELECT COUNT(*) AS v FROM negocio_gamificacion WHERE onboarding_completado = true"))

        # ── Soporte / contenido ──
        metrics['admins_activos'] = int(escalar("SELECT COUNT(*) AS v FROM administradores WHERE activo = true"))
        metrics['acciones_admin_30d'] = int(escalar(
            "SELECT COUNT(*) AS v FROM admin_audit_log WHERE created_at >= NOW() - INTERVAL '30 days'"))

        conn.close()

        # ── Evento especial activo (Python, no DB) ──
        try:
            from src.models.colombia_data.ratings.negocio_gamificacion import evento_especial
            ev = evento_especial()
            metrics['evento_activo'] = ({'nombre': ev['nombre'], 'icono': ev['icono'],
                                         'xp_mult': ev['xp_mult']} if ev else None)
        except Exception:
            metrics['evento_activo'] = None

        return build_cors_response({'success': True, 'metrics': metrics})
    except Exception as e:
        logger.error(f"Error obteniendo metrics: {e}")
        try:
            if conn:
                conn.close()
        except Exception:
            pass
        return build_cors_response({'success': False, 'error': str(e), 'metrics': metrics}, 200)


@admin_bp.route('/search', methods=['GET'])
@admin_required
def admin_search():
    """
    GET /api/admin/search?q=texto
    Buscador global del panel (A5): usuarios, negocios y administradores.
    Cada grupo es tolerante a fallos. Devuelve resultados con la 'seccion'
    a la que debe saltar el frontend.
    """
    q = (request.args.get('q') or '').strip()
    resultados = {'usuarios': [], 'negocios': [], 'administradores': []}
    if len(q) < 2:
        return build_cors_response({'success': True, 'q': q, 'resultados': resultados,
                                    'total': 0, 'message': 'Escribe al menos 2 caracteres'})
    like = f"%{q}%"
    conn = None
    try:
        conn = get_db_connection()

        # ── Usuarios ──
        try:
            cur = conn.cursor()
            cur.execute("""
                SELECT id_usuario, nombre, apellidos, correo, active
                FROM usuarios
                WHERE LOWER(nombre || ' ' || COALESCE(apellidos,'')) LIKE LOWER(%s)
                   OR LOWER(correo) LIKE LOWER(%s)
                   OR CAST(cedula AS TEXT) LIKE %s
                ORDER BY created_at DESC
                LIMIT 6
            """, (like, like, like))
            for r in cur.fetchall():
                resultados['usuarios'].append({
                    'id': r['id_usuario'],
                    'titulo': f"{r['nombre'] or ''} {r['apellidos'] or ''}".strip() or r['correo'],
                    'subtitulo': r['correo'],
                    'estado': 'activo' if r['active'] else 'inactivo',
                    'seccion': 'usuarios',
                })
            cur.close()
        except Exception as e:
            logger.warning(f"[search] usuarios: {e}")
            conn.rollback()

        # ── Negocios ──
        try:
            cur = conn.cursor()
            cur.execute("""
                SELECT id_negocio, nombre_negocio, ciudad, slug, activo
                FROM negocios
                WHERE LOWER(nombre_negocio) LIKE LOWER(%s)
                   OR LOWER(COALESCE(slug,'')) LIKE LOWER(%s)
                   OR LOWER(COALESCE(ciudad,'')) LIKE LOWER(%s)
                ORDER BY id_negocio DESC
                LIMIT 6
            """, (like, like, like))
            for r in cur.fetchall():
                resultados['negocios'].append({
                    'id': r['id_negocio'],
                    'titulo': r['nombre_negocio'],
                    'subtitulo': r['ciudad'] or '',
                    'slug': r['slug'],
                    'estado': 'activo' if r['activo'] else 'inactivo',
                    'seccion': 'negocios',
                })
            cur.close()
        except Exception as e:
            logger.warning(f"[search] negocios: {e}")
            conn.rollback()

        # ── Administradores ──
        try:
            cur = conn.cursor()
            cur.execute("""
                SELECT id, email, nombre, rol, activo
                FROM administradores
                WHERE LOWER(email) LIKE LOWER(%s) OR LOWER(COALESCE(nombre,'')) LIKE LOWER(%s)
                ORDER BY id ASC
                LIMIT 6
            """, (like, like))
            for r in cur.fetchall():
                resultados['administradores'].append({
                    'id': r['id'],
                    'titulo': r['nombre'] or r['email'],
                    'subtitulo': f"{r['email']} · {r['rol']}",
                    'estado': 'activo' if r['activo'] else 'inactivo',
                    'seccion': 'admins',
                })
            cur.close()
        except Exception as e:
            logger.warning(f"[search] admins: {e}")
            conn.rollback()

        conn.close()
        total = sum(len(v) for v in resultados.values())
        return build_cors_response({'success': True, 'q': q, 'resultados': resultados, 'total': total})
    except Exception as e:
        logger.error(f"Error en admin_search: {e}")
        try:
            if conn:
                conn.close()
        except Exception:
            pass
        return build_cors_response({'success': False, 'error': str(e), 'resultados': resultados, 'total': 0}, 200)


# ═══════════════════════════════════════════════════════════════════════════════
# GESTIÓN DE USUARIOS (CRUD SUPERADMIN)
# ═══════════════════════════════════════════════════════════════════════════════

@admin_bp.route('/usuarios', methods=['GET'])
@superadmin_required
def list_usuarios():
    """
    GET /api/admin/usuarios
    Lista todos los usuarios registrados con conteo de negocios.
    Soporta ?search=texto para filtrar por nombre/correo/cédula.
    """
    try:
        search = request.args.get('search', '').strip()
        page   = max(1, int(request.args.get('page', 1)))
        limit  = 50
        offset = (page - 1) * limit

        conn = get_db_connection()
        cur  = conn.cursor()

        where = ""
        params = []
        if search:
            where = """
                WHERE (
                    LOWER(u.nombre || ' ' || u.apellidos) LIKE LOWER(%s)
                    OR LOWER(u.correo) LIKE LOWER(%s)
                    OR CAST(u.cedula AS TEXT) LIKE %s
                )
            """
            like = f"%{search}%"
            params = [like, like, like]

        # Conteo total
        cur.execute(f"SELECT COUNT(*) as total FROM usuarios u {where}", params)
        total = cur.fetchone()['total']

        # Lista paginada con conteo de negocios
        cur.execute(f"""
            SELECT
                u.id_usuario,
                u.nombre,
                u.apellidos,
                u.correo,
                u.cedula,
                u.celular,
                u.profesion,
                u.active,
                u.black_list,
                u.created_at,
                u.last_login,
                COUNT(n.id_negocio) AS total_negocios
            FROM usuarios u
            LEFT JOIN negocios n ON n.usuario_id = u.id_usuario
            {where}
            GROUP BY u.id_usuario
            ORDER BY u.created_at DESC
            LIMIT %s OFFSET %s
        """, params + [limit, offset])

        rows = cur.fetchall()
        cur.close()
        conn.close()

        usuarios = []
        for r in rows:
            d = dict(r)
            # Serializar datetimes
            d['created_at'] = d['created_at'].isoformat() if d['created_at'] else None
            d['last_login']  = d['last_login'].isoformat()  if d['last_login']  else None
            usuarios.append(d)

        return build_cors_response({
            'usuarios': usuarios,
            'total': total,
            'page': page,
            'pages': max(1, -(-total // limit))   # ceil division
        })

    except Exception as e:
        logger.error(f"Error listando usuarios: {e}")
        return build_cors_response({'error': str(e)}, 500)


@admin_bp.route('/usuarios/<int:user_id>', methods=['GET'])
@superadmin_required
def get_usuario(user_id):
    """
    GET /api/admin/usuarios/<id>
    Retorna detalle completo del usuario + lista de sus negocios.
    """
    try:
        conn = get_db_connection()
        cur  = conn.cursor()

        cur.execute("""
            SELECT
                u.id_usuario, u.nombre, u.apellidos, u.correo,
                u.cedula, u.celular, u.profesion,
                u.active, u.black_list, u.validate,
                u.created_at, u.last_login
            FROM usuarios u
            WHERE u.id_usuario = %s
        """, (user_id,))

        usuario = cur.fetchone()
        if not usuario:
            cur.close()
            conn.close()
            return build_cors_response({'error': 'Usuario no encontrado'}, 404)

        usuario = dict(usuario)
        usuario['created_at'] = usuario['created_at'].isoformat() if usuario['created_at'] else None
        usuario['last_login']  = usuario['last_login'].isoformat()  if usuario['last_login']  else None

        # Negocios del usuario
        cur.execute("""
            SELECT id_negocio, nombre_negocio, slug, tipo_negocio, estado, created_at
            FROM negocios
            WHERE usuario_id = %s
            ORDER BY created_at DESC
        """, (user_id,))

        negocios = []
        for n in cur.fetchall():
            nd = dict(n)
            nd['created_at'] = nd['created_at'].isoformat() if nd['created_at'] else None
            negocios.append(nd)

        cur.close()
        conn.close()

        return build_cors_response({
            'usuario': usuario,
            'negocios': negocios
        })

    except Exception as e:
        logger.error(f"Error obteniendo usuario {user_id}: {e}")
        return build_cors_response({'error': str(e)}, 500)


@admin_bp.route('/usuarios/<int:user_id>', methods=['DELETE'])
@superadmin_required
def delete_usuario(user_id):
    """
    DELETE /api/admin/usuarios/<id>
    Borrado TOTAL e irreversible del usuario y todos sus datos en cascada.
    La FK negocios.usuario_id tiene ondelete=CASCADE → borra negocios automáticamente.
    """
    try:
        conn = get_db_connection()
        cur  = conn.cursor()

        # Verificar que existe y no es admin
        cur.execute("""
            SELECT u.id_usuario, u.correo, u.nombre, u.apellidos,
                   a.id AS es_admin
            FROM usuarios u
            LEFT JOIN administradores a ON LOWER(a.email) = LOWER(u.correo) AND a.activo = true
            WHERE u.id_usuario = %s
        """, (user_id,))

        usuario = cur.fetchone()

        if not usuario:
            cur.close()
            conn.close()
            return build_cors_response({'error': 'Usuario no encontrado'}, 404)

        if usuario['es_admin']:
            cur.close()
            conn.close()
            return build_cors_response(
                {'error': 'No se puede eliminar un usuario que es administrador activo. Desactívalo primero.'},
                403
            )

        # Guardar datos para el log antes de borrar
        correo_eliminado = usuario['correo']
        nombre_eliminado = f"{usuario['nombre']} {usuario['apellidos']}"

        # ── Obtener IDs de negocios del usuario ──
        cur.execute("SELECT id_negocio FROM negocios WHERE usuario_id = %s", (user_id,))
        negocio_rows = cur.fetchall()
        negocio_ids = [r['id_negocio'] for r in negocio_rows]
        total_negocios = len(negocio_ids)

        # ── 1. Limpiar dependencias de los NEGOCIOS (FKs sin CASCADE a negocios) ──
        if negocio_ids:
            # psycopg2 acepta lista con ANY(%s::int[])
            nids = negocio_ids  # lista Python, se pasa como array

            # movimientos_stock.negocio_id (NOT NULL, sin cascade) → borrar filas
            cur.execute("DELETE FROM movimientos_stock   WHERE negocio_id = ANY(%s)", (nids,))

            # categorias_producto.negocio_id (NOT NULL, sin cascade) → borrar filas
            cur.execute("DELETE FROM categorias_producto WHERE negocio_id = ANY(%s)", (nids,))

            # notification.negocio_id (nullable, sin cascade) → poner NULL
            cur.execute("UPDATE notification SET negocio_id = NULL WHERE negocio_id = ANY(%s)", (nids,))

            # servicio.negocio_contratante_id / negocio_contratado_id (nullable, sin cascade)
            cur.execute("UPDATE servicio SET negocio_contratante_id = NULL WHERE negocio_contratante_id = ANY(%s)", (nids,))
            cur.execute("UPDATE servicio SET negocio_contratado_id  = NULL WHERE negocio_contratado_id  = ANY(%s)", (nids,))

        # ── 2. Limpiar dependencias del USUARIO (FKs sin CASCADE a usuarios) ──

        # Tokens de reset de contraseña
        cur.execute("DELETE FROM password_reset_tokens WHERE user_id = %s", (user_id,))

        # Notificaciones (sender y receiver)
        cur.execute("DELETE FROM notification WHERE user_id = %s OR sender_id = %s", (user_id, user_id))

        # Mensajes (sender y receiver)
        cur.execute("DELETE FROM message WHERE sender_id = %s OR receiver_id = %s", (user_id, user_id))

        # Servicios en los que participa como cualquier rol
        cur.execute("""
            DELETE FROM servicio
            WHERE id_usuario = %s OR id_contratante = %s OR id_contratado = %s
        """, (user_id, user_id, user_id))

        # movimientos_stock / categorias_producto que apuntan al usuario directamente
        # (usuario_id es NOT NULL en ambas → DELETE, no SET NULL)
        cur.execute("DELETE FROM movimientos_stock   WHERE usuario_id = %s", (user_id,))
        cur.execute("DELETE FROM categorias_producto WHERE usuario_id = %s", (user_id,))

        # ── 3. Borrado final ──
        # CASCADE de la BD elimina: negocios → productos, sucursales,
        # transacciones, gamificación, negocio_plan, etc.
        cur.execute("DELETE FROM usuarios WHERE id_usuario = %s", (user_id,))
        conn.commit()
        cur.close()
        conn.close()

        logger.warning(
            f"🗑️ USUARIO ELIMINADO por {g.user_email}: "
            f"id={user_id} | correo={correo_eliminado} | negocios_borrados={total_negocios}"
        )

        registrar_auditoria('eliminar', 'usuario', user_id,
                            {'correo': correo_eliminado, 'nombre': nombre_eliminado,
                             'negocios_eliminados': total_negocios})
        return build_cors_response({
            'success': True,
            'message': f'Usuario "{nombre_eliminado}" ({correo_eliminado}) eliminado permanentemente.',
            'negocios_eliminados': total_negocios
        })

    except Exception as e:
        logger.error(f"Error eliminando usuario {user_id}: {e}")
        return build_cors_response({'error': str(e)}, 500)


# ═══════════════════════════════════════════════════════════════════════════════
# LOG DE AUDITORÍA (Admin Panel A2)
# Registra toda acción mutante del admin. A PRUEBA DE FALLOS: usa su propia
# conexión y nunca interrumpe la operación principal si algo falla.
# ═══════════════════════════════════════════════════════════════════════════════

def registrar_auditoria(accion, entidad, entidad_id=None, detalle=None):
    """
    Registra una acción de admin en admin_audit_log. Lee el admin de g.admin.
    Silencioso ante errores (jamás rompe el endpoint que la llama).
    """
    try:
        from src.models.admin_audit import normalizar_accion
        admin = getattr(g, 'admin', None) or {}
        admin_id = admin.get('id')
        admin_email = admin.get('email') or getattr(g, 'user_email', None)
        ip = (request.headers.get('X-Forwarded-For', '') or request.remote_addr or '')[:64]
        ua = (request.headers.get('User-Agent', '') or '')[:300]
        det = detalle if isinstance(detalle, dict) else ({'info': detalle} if detalle else {})

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO admin_audit_log
                (admin_id, admin_email, accion, entidad, entidad_id, detalle, ip, user_agent, created_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, NOW())
        """, (admin_id, admin_email, normalizar_accion(accion), entidad,
              str(entidad_id) if entidad_id is not None else None,
              json.dumps(det), ip, ua))
        conn.commit()
        cur.close()
        conn.close()
    except Exception as e:
        logger.warning(f"[auditoria] no se pudo registrar ({accion} {entidad}): {e}")


@admin_bp.route('/auditoria', methods=['GET'])
@admin_required
def list_auditoria():
    """
    GET /api/admin/auditoria
    Lista el log de auditoría con filtros: ?entidad=&accion=&admin_id=&q=&page=&limit=
    """
    try:
        entidad  = (request.args.get('entidad') or '').strip()
        accion   = (request.args.get('accion') or '').strip()
        admin_id = (request.args.get('admin_id') or '').strip()
        q        = (request.args.get('q') or '').strip()
        try:
            page  = max(1, int(request.args.get('page', 1)))
            limit = min(100, max(1, int(request.args.get('limit', 50))))
        except (TypeError, ValueError):
            page, limit = 1, 50
        offset = (page - 1) * limit

        where, params = ["1=1"], []
        if entidad:
            where.append("entidad = %s"); params.append(entidad)
        if accion:
            where.append("accion = %s"); params.append(accion)
        if admin_id.isdigit():
            where.append("admin_id = %s"); params.append(int(admin_id))
        if q:
            where.append("(admin_email ILIKE %s OR entidad_id ILIKE %s OR detalle::text ILIKE %s)")
            like = f"%{q}%"; params += [like, like, like]
        where_sql = " AND ".join(where)

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(f"SELECT COUNT(*) AS total FROM admin_audit_log WHERE {where_sql}", params)
        total = cur.fetchone()['total']
        cur.execute(f"""
            SELECT id, admin_id, admin_email, accion, entidad, entidad_id, detalle, ip, created_at
            FROM admin_audit_log
            WHERE {where_sql}
            ORDER BY created_at DESC
            LIMIT %s OFFSET %s
        """, params + [limit, offset])
        rows = cur.fetchall()
        cur.close()
        conn.close()

        eventos = []
        for r in rows:
            d = dict(r)
            if d.get('created_at'):
                d['created_at'] = d['created_at'].isoformat()
            eventos.append(d)

        return build_cors_response({
            'success': True,
            'eventos': eventos,
            'total': total,
            'page': page,
            'limit': limit,
            'pages': (total + limit - 1) // limit,
        })
    except Exception as e:
        logger.error(f"Error listando auditoría: {e}")
        return build_cors_response({'success': False, 'error': str(e), 'eventos': []}, 200)


# ═══════════════════════════════════════════════════════════════════════════════
# PERMISOS GRANULARES — ENDPOINTS (A3)
# ═══════════════════════════════════════════════════════════════════════════════

@admin_bp.route('/permisos/modulos', methods=['GET'])
@admin_required
def list_modulos_permisos():
    """GET /api/admin/permisos/modulos → catálogo de módulos para asignar permisos."""
    return build_cors_response({'success': True, 'modulos': MODULOS_PERMISOS})


@admin_bp.route('/<int:admin_id>/permisos', methods=['PUT'])
@superadmin_required
def update_admin_permisos(admin_id):
    """
    PUT /api/admin/<id>/permisos  body: { permisos: [...] }
    Actualiza los permisos de módulo de un admin (solo superadmin). Auditado.
    """
    try:
        data = request.get_json(silent=True) or {}
        permisos_in = data.get('permisos', [])
        if not isinstance(permisos_in, list):
            return build_cors_response({'error': 'permisos debe ser una lista'}, 400)
        # Saneo: solo claves válidas, sin duplicados, preservando orden del catálogo
        limpios = [m['key'] for m in MODULOS_PERMISOS if m['key'] in set(permisos_in)]

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT id, email, rol, permisos FROM administradores WHERE id = %s", (admin_id,))
        target = cur.fetchone()
        if not target:
            cur.close(); conn.close()
            return build_cors_response({'error': 'Administrador no encontrado'}, 404)
        if target['rol'] == 'superadmin':
            cur.close(); conn.close()
            return build_cors_response({'error': 'El superadmin ya tiene todos los permisos'}, 400)

        cur.execute("""
            UPDATE administradores
            SET permisos = %s, updated_at = CURRENT_TIMESTAMP
            WHERE id = %s
            RETURNING id, email, nombre, rol, permisos, activo
        """, (json.dumps(limpios), admin_id))
        actualizado = cur.fetchone()
        conn.commit()
        cur.close(); conn.close()

        registrar_auditoria('editar', 'permisos_admin', admin_id,
                            {'email': target['email'], 'antes': target['permisos'] or [], 'despues': limpios})
        return build_cors_response({'success': True, 'admin': dict(actualizado),
                                    'message': 'Permisos actualizados'})
    except Exception as e:
        logger.error(f"Error actualizando permisos de admin {admin_id}: {e}")
        return build_cors_response({'error': str(e)}, 500)

# ═══════════════════════════════════════════════════════════════════════════════
# GAMIFICACIÓN — CONFIG EDITABLE (Admin Panel A6)
# XP por evento editable desde el panel (con fallback al DEFAULT). Niveles: lectura.
# ═══════════════════════════════════════════════════════════════════════════════

@admin_bp.route('/gamificacion/config', methods=['GET'])
@requiere_permiso('gamificacion')
def get_gamif_config():
    """GET /api/admin/gamificacion/config → XP por evento (efectivo + default) y niveles."""
    try:
        from src.models.colombia_data.ratings.config_gamificacion import (
            get_xp_eventos, XP_EVENTOS_DEFAULT, XP_EVENTOS_LABELS
        )
        from src.models.colombia_data.ratings.negocio_gamificacion import NegocioGamificacion
        niveles = [{'xp_req': x, 'nivel': n, 'nombre': nom} for (x, n, nom) in NegocioGamificacion.NIVELES]
        return build_cors_response({
            'success': True,
            'xp_eventos': get_xp_eventos(),
            'xp_eventos_default': XP_EVENTOS_DEFAULT,
            'labels': XP_EVENTOS_LABELS,
            'niveles': niveles,
        })
    except Exception as e:
        logger.error(f"Error en get_gamif_config: {e}")
        return build_cors_response({'success': False, 'error': str(e)}, 200)


@admin_bp.route('/gamificacion/xp-eventos', methods=['PUT'])
@requiere_permiso('gamificacion')
def update_gamif_xp_eventos():
    """PUT /api/admin/gamificacion/xp-eventos  body: { xp_eventos: {evento:{xp,tukoins}} }"""
    try:
        from src.models.colombia_data.ratings.config_gamificacion import (
            validar_xp_eventos, set_xp_eventos, get_xp_eventos
        )
        data = request.get_json(silent=True) or {}
        payload = data.get('xp_eventos', data)
        antes = get_xp_eventos()
        ok, limpio, error = validar_xp_eventos(payload)
        if not ok:
            return build_cors_response({'success': False, 'error': error}, 400)
        efectivo = set_xp_eventos(limpio)
        registrar_auditoria('editar', 'gamif_xp_eventos', None,
                            {'antes': antes, 'despues': efectivo})
        return build_cors_response({'success': True, 'xp_eventos': efectivo,
                                    'message': 'XP por evento actualizado'})
    except Exception as e:
        logger.error(f"Error en update_gamif_xp_eventos: {e}")
        try:
            from src.models.database import db as _db
            _db.session.rollback()
        except Exception:
            pass
        return build_cors_response({'success': False, 'error': str(e)}, 500)


# ═══════════════════════════════════════════════════════════════════════════════
# GAMIFICACIÓN — MISIONES (Admin Panel A7)
# Editar nombre/descripcion/icono/xp/tukoins y activar/desactivar misiones.
# ═══════════════════════════════════════════════════════════════════════════════

@admin_bp.route('/gamificacion/misiones', methods=['GET'])
@requiere_permiso('gamificacion')
def get_gamif_misiones():
    """GET /api/admin/gamificacion/misiones → pools (diaria/semanal/mensual) con estado actual."""
    try:
        from src.models.colombia_data.ratings.config_gamificacion import (
            _default_pool, get_misiones_override
        )
        override = get_misiones_override()

        def annotate(pool):
            res = []
            for m in pool:
                ov = override.get(m['codigo'], {}) if isinstance(override, dict) else {}
                res.append({
                    'codigo': m['codigo'],
                    'nombre': ov.get('nombre') or m.get('nombre', ''),
                    'descripcion': ov.get('descripcion') or m.get('descripcion', ''),
                    'icono': ov.get('icono') or m.get('icono', '🎯'),
                    'xp': ov.get('xp', m.get('xp', 0)),
                    'tukoins': ov.get('tukoins', m.get('tukoins', 0)),
                    'tipo': m.get('tipo', ''),
                    'activa': ov.get('activa', True),
                    'default': {'xp': m.get('xp', 0), 'tukoins': m.get('tukoins', 0)},
                })
            return res

        return build_cors_response({
            'success': True,
            'diaria':  annotate(_default_pool('diaria')),
            'semanal': annotate(_default_pool('semanal')),
            'mensual': annotate(_default_pool('mensual')),
        })
    except Exception as e:
        logger.error(f"Error en get_gamif_misiones: {e}")
        return build_cors_response({'success': False, 'error': str(e)}, 200)


@admin_bp.route('/gamificacion/misiones', methods=['PUT'])
@requiere_permiso('gamificacion')
def update_gamif_misiones():
    """PUT /api/admin/gamificacion/misiones  body: { overrides: {codigo:{...}} }"""
    try:
        from src.models.colombia_data.ratings.config_gamificacion import (
            validar_misiones_override, set_misiones_override, get_misiones_override
        )
        data = request.get_json(silent=True) or {}
        payload = data.get('overrides', data)
        antes = get_misiones_override()
        ok, limpio, error = validar_misiones_override(payload)
        if not ok:
            return build_cors_response({'success': False, 'error': error}, 400)
        set_misiones_override(limpio)
        registrar_auditoria('editar', 'gamif_misiones', None,
                            {'antes': antes, 'despues': limpio})
        return build_cors_response({'success': True, 'overrides': limpio,
                                    'message': 'Misiones actualizadas'})
    except Exception as e:
        logger.error(f"Error en update_gamif_misiones: {e}")
        try:
            from src.models.database import db as _db
            _db.session.rollback()
        except Exception:
            pass
        return build_cors_response({'success': False, 'error': str(e)}, 500)


# ═══════════════════════════════════════════════════════════════════════════════
# GAMIFICACIÓN — TIENDA DE ÍTEMS (Admin Panel A8)
# La tabla tienda_items ya existe; CRUD admin (editar precio/activar/crear).
# ═══════════════════════════════════════════════════════════════════════════════

@admin_bp.route('/gamificacion/tienda', methods=['GET'])
@requiere_permiso('gamificacion')
def get_gamif_tienda():
    """GET /api/admin/gamificacion/tienda → todos los ítems (activos e inactivos)."""
    try:
        from src.models.colombia_data.ratings.negocio_gamificacion import TiendaItem, seed_tienda_items
        from src.models.database import db
        seed_tienda_items(db.session)  # idempotente: asegura catálogo base
        items = TiendaItem.query.order_by(TiendaItem.activo.desc(), TiendaItem.precio_tukoins).all()
        data = []
        for it in items:
            d = it.serialize()
            d['activo'] = bool(it.activo)
            data.append(d)
        return build_cors_response({'success': True, 'items': data, 'total': len(data)})
    except Exception as e:
        logger.error(f"Error en get_gamif_tienda: {e}")
        return build_cors_response({'success': False, 'error': str(e), 'items': []}, 200)


@admin_bp.route('/gamificacion/tienda/<int:item_id>', methods=['PUT'])
@requiere_permiso('gamificacion')
def update_gamif_tienda_item(item_id):
    """PUT /api/admin/gamificacion/tienda/<id> → edita un ítem."""
    try:
        from src.models.colombia_data.ratings.negocio_gamificacion import TiendaItem
        from src.models.colombia_data.ratings.config_gamificacion import validar_item_tienda
        from src.models.database import db
        item = TiendaItem.query.get(item_id)
        if not item:
            return build_cors_response({'error': 'Ítem no encontrado'}, 404)
        ok, limpio, error = validar_item_tienda(request.get_json(silent=True) or {})
        if not ok:
            return build_cors_response({'success': False, 'error': error}, 400)
        antes = {'precio_tukoins': item.precio_tukoins, 'nombre': item.nombre, 'activo': bool(item.activo)}
        for campo, valor in limpio.items():
            setattr(item, campo, valor)
        db.session.commit()
        registrar_auditoria('editar', 'tienda_item', item_id, {'antes': antes, 'despues': limpio})
        d = item.serialize(); d['activo'] = bool(item.activo)
        return build_cors_response({'success': True, 'item': d, 'message': 'Ítem actualizado'})
    except Exception as e:
        logger.error(f"Error en update_gamif_tienda_item: {e}")
        try:
            from src.models.database import db as _db
            _db.session.rollback()
        except Exception:
            pass
        return build_cors_response({'success': False, 'error': str(e)}, 500)


@admin_bp.route('/gamificacion/tienda', methods=['POST'])
@requiere_permiso('gamificacion')
def create_gamif_tienda_item():
    """POST /api/admin/gamificacion/tienda → crea un ítem nuevo."""
    try:
        from src.models.colombia_data.ratings.negocio_gamificacion import TiendaItem
        from src.models.colombia_data.ratings.config_gamificacion import validar_item_tienda
        from src.models.database import db
        ok, limpio, error = validar_item_tienda(request.get_json(silent=True) or {}, requerir_codigo=True)
        if not ok:
            return build_cors_response({'success': False, 'error': error}, 400)
        if TiendaItem.query.filter_by(codigo=limpio['codigo']).first():
            return build_cors_response({'success': False, 'error': 'Ya existe un ítem con ese código'}, 400)
        item = TiendaItem(**limpio)
        db.session.add(item)
        db.session.commit()
        registrar_auditoria('crear', 'tienda_item', item.id, limpio)
        d = item.serialize(); d['activo'] = bool(item.activo)
        return build_cors_response({'success': True, 'item': d, 'message': 'Ítem creado'}, 201)
    except Exception as e:
        logger.error(f"Error en create_gamif_tienda_item: {e}")
        try:
            from src.models.database import db as _db
            _db.session.rollback()
        except Exception:
            pass
        return build_cors_response({'success': False, 'error': str(e)}, 500)


# ═══════════════════════════════════════════════════════════════════════════════
# GAMIFICACIÓN — ECONOMÍA DE TUKOINS (Admin Panel A9)
# Circulación, top holders, ajuste manual y bono por fecha configurable.
# ═══════════════════════════════════════════════════════════════════════════════

@admin_bp.route('/gamificacion/economia', methods=['GET'])
@requiere_permiso('gamificacion')
def get_gamif_economia():
    """GET /api/admin/gamificacion/economia → circulación, top holders, bono."""
    data = {'success': True, 'tukoins_circulando': 0, 'xp_repartido': 0,
            'negocios_con_saldo': 0, 'top_holders': [], 'bono': None}
    try:
        conn = get_db_connection()

        def escalar(sql, default=0):
            try:
                cur = conn.cursor(); cur.execute(sql); row = cur.fetchone(); cur.close()
                v = list(row.values())[0] if row else default
                return v if v is not None else default
            except Exception:
                try: conn.rollback()
                except Exception: pass
                return default

        data['tukoins_circulando'] = int(escalar("SELECT COALESCE(SUM(tukoins),0) AS v FROM negocio_gamificacion"))
        data['xp_repartido'] = int(escalar("SELECT COALESCE(SUM(xp_total),0) AS v FROM negocio_gamificacion"))
        data['negocios_con_saldo'] = int(escalar("SELECT COUNT(*) AS v FROM negocio_gamificacion WHERE tukoins > 0"))

        try:
            cur = conn.cursor()
            cur.execute("""
                SELECT g.negocio_id, g.tukoins, g.nivel, n.nombre_negocio
                FROM negocio_gamificacion g
                LEFT JOIN negocios n ON n.id_negocio = g.negocio_id
                WHERE g.tukoins > 0
                ORDER BY g.tukoins DESC
                LIMIT 10
            """)
            data['top_holders'] = [{'negocio_id': r['negocio_id'],
                                    'nombre': r['nombre_negocio'] or f"Negocio {r['negocio_id']}",
                                    'tukoins': r['tukoins'], 'nivel': r['nivel']} for r in cur.fetchall()]
            cur.close()
        except Exception as e:
            logger.warning(f"[economia] top_holders: {e}"); conn.rollback()

        conn.close()

        from src.models.colombia_data.ratings.config_gamificacion import get_bono_config, DIAS_SEMANA
        bono = get_bono_config()
        bono['dia_nombre'] = DIAS_SEMANA[bono['dia_semana']] if 0 <= bono.get('dia_semana', 6) <= 6 else ''
        data['bono'] = bono
        return build_cors_response(data)
    except Exception as e:
        logger.error(f"Error en get_gamif_economia: {e}")
        return build_cors_response(data, 200)


@admin_bp.route('/gamificacion/economia/ajuste', methods=['POST'])
@requiere_permiso('gamificacion')
def ajustar_tukoins():
    """POST /api/admin/gamificacion/economia/ajuste  body: {negocio_id, cantidad, motivo}"""
    try:
        from src.models.colombia_data.ratings.negocio_gamificacion import NegocioGamificacion
        from src.models.database import db
        data = request.get_json(silent=True) or {}
        try:
            nid = int(data.get('negocio_id'))
            cantidad = int(data.get('cantidad'))
        except (TypeError, ValueError):
            return build_cors_response({'success': False, 'error': 'negocio_id y cantidad deben ser números'}, 400)
        motivo = str(data.get('motivo', '')).strip()
        if not motivo:
            return build_cors_response({'success': False, 'error': 'El motivo es obligatorio'}, 400)
        if cantidad == 0:
            return build_cors_response({'success': False, 'error': 'La cantidad no puede ser 0'}, 400)
        if abs(cantidad) > 1000000:
            return build_cors_response({'success': False, 'error': 'Cantidad fuera de rango'}, 400)

        gami = NegocioGamificacion.obtener_o_crear(nid, db.session)
        saldo_antes = gami.tukoins
        gami.agregar_tukoins(cantidad, f"Ajuste admin: {motivo}", db_session=db.session)
        db.session.commit()
        registrar_auditoria('ajustar', 'tukoins', nid,
                            {'cantidad': cantidad, 'motivo': motivo,
                             'saldo_antes': saldo_antes, 'saldo_despues': gami.tukoins})
        return build_cors_response({'success': True, 'saldo': gami.tukoins,
                                    'message': f'Ajuste aplicado. Nuevo saldo: {gami.tukoins} TuKoins'})
    except Exception as e:
        logger.error(f"Error en ajustar_tukoins: {e}")
        try:
            from src.models.database import db as _db
            _db.session.rollback()
        except Exception:
            pass
        return build_cors_response({'success': False, 'error': str(e)}, 500)


@admin_bp.route('/gamificacion/bono', methods=['PUT'])
@requiere_permiso('gamificacion')
def update_gamif_bono():
    """PUT /api/admin/gamificacion/bono → configura el bono de TuKoins por fecha."""
    try:
        from src.models.colombia_data.ratings.config_gamificacion import (
            validar_bono_config, set_bono_config, get_bono_config
        )
        antes = get_bono_config()
        ok, limpio, error = validar_bono_config(request.get_json(silent=True) or {})
        if not ok:
            return build_cors_response({'success': False, 'error': error}, 400)
        set_bono_config(limpio)
        registrar_auditoria('editar', 'gamif_bono', None, {'antes': antes, 'despues': limpio})
        return build_cors_response({'success': True, 'bono': limpio, 'message': 'Bono actualizado'})
    except Exception as e:
        logger.error(f"Error en update_gamif_bono: {e}")
        try:
            from src.models.database import db as _db
            _db.session.rollback()
        except Exception:
            pass
        return build_cors_response({'success': False, 'error': str(e)}, 500)


# ═══════════════════════════════════════════════════════════════════════════════
# GAMIFICACIÓN — FICHA POR NEGOCIO (Admin Panel A10)
# Ver y corregir XP/nivel/prestigio/rachas/TuKoins de un negocio (soporte).
# ═══════════════════════════════════════════════════════════════════════════════

@admin_bp.route('/gamificacion/negocio/<int:negocio_id>', methods=['GET'])
@requiere_permiso('gamificacion')
def get_gamif_negocio(negocio_id):
    """GET /api/admin/gamificacion/negocio/<id> → ficha de gamificación del negocio."""
    try:
        from src.models.colombia_data.ratings.negocio_gamificacion import NegocioGamificacion
        from src.models.database import db
        gami = NegocioGamificacion.query.filter_by(negocio_id=negocio_id).first()
        if not gami:
            return build_cors_response({'success': True, 'existe': False,
                                        'message': 'Este negocio aún no tiene gamificación.'}, 200)
        data = gami.serialize()
        # nombre del negocio
        try:
            cur = get_db_connection().cursor()
            cur.execute("SELECT nombre_negocio FROM negocios WHERE id_negocio = %s", (negocio_id,))
            row = cur.fetchone(); cur.close()
            data['nombre_negocio'] = row['nombre_negocio'] if row else f"Negocio {negocio_id}"
        except Exception:
            data['nombre_negocio'] = f"Negocio {negocio_id}"
        # insignias obtenidas (conteo)
        data['insignias'] = int(_scalar_admin(
            "SELECT COUNT(*) AS v FROM negocio_badges_obtenidos WHERE negocio_id = %s "
            "AND (activo IS TRUE OR activo IS NULL)", (negocio_id,)))
        return build_cors_response({'success': True, 'existe': True, 'gamificacion': data})
    except Exception as e:
        logger.error(f"Error en get_gamif_negocio: {e}")
        return build_cors_response({'success': False, 'error': str(e)}, 200)


def _scalar_admin(sql, params):
    """Helper: escalar tolerante a fallos para consultas admin puntuales."""
    try:
        conn = get_db_connection(); cur = conn.cursor()
        cur.execute(sql, params); row = cur.fetchone(); cur.close(); conn.close()
        if not row:
            return 0
        v = list(row.values())[0]
        return v if v is not None else 0
    except Exception:
        return 0


@admin_bp.route('/gamificacion/negocio/<int:negocio_id>/ajuste', methods=['POST'])
@requiere_permiso('gamificacion')
def ajustar_gamif_negocio(negocio_id):
    """
    POST /api/admin/gamificacion/negocio/<id>/ajuste
    body: { xp_total?, prestigio?, tukoins?, reset_racha?, motivo }
    Corrige los valores de gamificación de un negocio. Auditado.
    """
    try:
        from src.models.colombia_data.ratings.negocio_gamificacion import NegocioGamificacion
        from src.models.database import db
        data = request.get_json(silent=True) or {}
        motivo = str(data.get('motivo', '')).strip()
        if not motivo:
            return build_cors_response({'success': False, 'error': 'El motivo es obligatorio'}, 400)

        gami = NegocioGamificacion.obtener_o_crear(negocio_id, db.session)
        antes = {'xp_total': gami.xp_total, 'nivel': gami.nivel, 'prestigio': gami.prestigio,
                 'tukoins': gami.tukoins, 'racha': gami.racha_actividad_dias}
        cambios = {}

        def _int(v):
            return int(v)

        if 'xp_total' in data and data['xp_total'] not in (None, ''):
            try:
                xp = max(0, _int(data['xp_total']))
            except (TypeError, ValueError):
                return build_cors_response({'success': False, 'error': 'xp_total inválido'}, 400)
            if xp > 100000000:
                return build_cors_response({'success': False, 'error': 'xp_total fuera de rango'}, 400)
            gami.xp_total = xp
            gami.calcular_nivel()
            cambios['xp_total'] = xp

        if 'prestigio' in data and data['prestigio'] not in (None, ''):
            try:
                pr = max(0, _int(data['prestigio']))
            except (TypeError, ValueError):
                return build_cors_response({'success': False, 'error': 'prestigio inválido'}, 400)
            if pr > 1000:
                return build_cors_response({'success': False, 'error': 'prestigio fuera de rango'}, 400)
            gami.prestigio = pr
            cambios['prestigio'] = pr

        if 'tukoins' in data and data['tukoins'] not in (None, ''):
            try:
                tk = max(0, _int(data['tukoins']))
            except (TypeError, ValueError):
                return build_cors_response({'success': False, 'error': 'tukoins inválido'}, 400)
            if tk > 100000000:
                return build_cors_response({'success': False, 'error': 'tukoins fuera de rango'}, 400)
            delta = tk - gami.tukoins
            if delta != 0:
                gami.agregar_tukoins(delta, f"Ajuste admin (ficha): {motivo}", db_session=db.session)
            cambios['tukoins'] = tk

        if data.get('reset_racha'):
            gami.racha_actividad_dias = 0
            gami.racha_actividad_fecha = None
            cambios['racha'] = 0

        if not cambios:
            return build_cors_response({'success': False, 'error': 'No se indicó ningún cambio'}, 400)

        db.session.commit()
        registrar_auditoria('ajustar', 'gamif_negocio', negocio_id,
                            {'motivo': motivo, 'antes': antes, 'cambios': cambios})
        return build_cors_response({'success': True, 'gamificacion': gami.serialize(),
                                    'message': 'Gamificación del negocio actualizada'})
    except Exception as e:
        logger.error(f"Error en ajustar_gamif_negocio: {e}")
        try:
            from src.models.database import db as _db
            _db.session.rollback()
        except Exception:
            pass
        return build_cors_response({'success': False, 'error': str(e)}, 500)


# ═══════════════════════════════════════════════════════════════════════════════
# GAMIFICACIÓN — REGLAS DE RACHAS (Admin Panel A11)
# Umbral de récord + bono opcional de TuKoins al alcanzarlo.
# ═══════════════════════════════════════════════════════════════════════════════

@admin_bp.route('/gamificacion/rachas', methods=['GET'])
@requiere_permiso('gamificacion')
def get_gamif_rachas():
    """GET /api/admin/gamificacion/rachas → config efectiva de rachas + default."""
    try:
        from src.models.colombia_data.ratings.config_gamificacion import get_rachas_config, RACHAS_DEFAULT
        return build_cors_response({'success': True, 'rachas': get_rachas_config(), 'default': RACHAS_DEFAULT})
    except Exception as e:
        logger.error(f"Error en get_gamif_rachas: {e}")
        return build_cors_response({'success': False, 'error': str(e)}, 200)


@admin_bp.route('/gamificacion/rachas', methods=['PUT'])
@requiere_permiso('gamificacion')
def update_gamif_rachas():
    """PUT /api/admin/gamificacion/rachas  body: { umbral_record, tukoins_por_record }"""
    try:
        from src.models.colombia_data.ratings.config_gamificacion import (
            validar_rachas_config, set_rachas_config, get_rachas_config
        )
        antes = get_rachas_config()
        ok, limpio, error = validar_rachas_config(request.get_json(silent=True) or {})
        if not ok:
            return build_cors_response({'success': False, 'error': error}, 400)
        set_rachas_config(limpio)
        registrar_auditoria('editar', 'gamif_rachas', None, {'antes': antes, 'despues': limpio})
        return build_cors_response({'success': True, 'rachas': limpio, 'message': 'Reglas de rachas actualizadas'})
    except Exception as e:
        logger.error(f"Error en update_gamif_rachas: {e}")
        try:
            from src.models.database import db as _db
            _db.session.rollback()
        except Exception:
            pass
        return build_cors_response({'success': False, 'error': str(e)}, 500)


# ═══════════════════════════════════════════════════════════════════════════════
# GAMIFICACIÓN — SIMULADOR / MODO PRUEBA (Admin Panel A13)
# Dry-run: calcula qué otorgaría un evento con la config ACTUAL. NO persiste nada.
# ═══════════════════════════════════════════════════════════════════════════════

@admin_bp.route('/gamificacion/simular', methods=['POST', 'OPTIONS'])
@requiere_permiso('gamificacion')
def simular_gamificacion():
    """
    POST /api/admin/gamificacion/simular
    body: { evento, negocio_id?, xp_inicial?, misiones?:[codigos] }
    Devuelve el desglose de recompensas SIN tocar la base de datos.
    """
    if request.method == 'OPTIONS':
        return build_cors_response()
    try:
        from src.models.colombia_data.ratings.config_gamificacion import (
            get_xp_eventos, simular_evento, get_pool
        )
        from src.models.colombia_data.ratings.negocio_gamificacion import (
            NegocioGamificacion, multiplicador_xp, bono_tukoins, evento_especial
        )
        data = request.get_json(silent=True) or {}
        evento = (data.get('evento') or '').strip()
        xp_eventos = get_xp_eventos()
        if not evento or evento not in xp_eventos:
            return build_cors_response({'success': False,
                'error': 'Evento inválido', 'eventos_validos': list(xp_eventos.keys())}, 400)

        # XP inicial: del negocio (solo lectura) o el indicado, o 0
        xp_inicial = 0
        negocio_id = data.get('negocio_id')
        if negocio_id:
            try:
                gami = NegocioGamificacion.query.filter_by(negocio_id=int(negocio_id)).first()
                if gami:
                    xp_inicial = gami.xp_total
            except Exception:
                pass
        elif data.get('xp_inicial') not in (None, ''):
            try:
                xp_inicial = max(0, int(data['xp_inicial']))
            except (TypeError, ValueError):
                xp_inicial = 0

        # Misiones a simular (por código), desde los pools efectivos
        codigos = data.get('misiones') or []
        misiones = []
        if codigos:
            pool = get_pool('diaria') + get_pool('semanal') + get_pool('mensual')
            por_codigo = {m['codigo']: m for m in pool}
            misiones = [por_codigo[c] for c in codigos if c in por_codigo]

        # Config actual (la misma que usa el motor real)
        xp_mult = multiplicador_xp()
        bono_mult, bono_nombre = bono_tukoins()
        ev_esp = evento_especial()

        resultado = simular_evento(
            evento, xp_inicial, xp_eventos, xp_mult, bono_mult,
            NegocioGamificacion.NIVELES, misiones
        )
        resultado['evento_especial'] = ({'nombre': ev_esp['nombre'], 'icono': ev_esp['icono'],
                                         'xp_mult': ev_esp['xp_mult']} if ev_esp else None)
        resultado['bono_tukoins'] = ({'nombre': bono_nombre, 'mult': bono_mult} if bono_mult > 1 else None)
        # Auditoría suave: registrar que se hizo una simulación (sin efecto sobre datos)
        registrar_auditoria('simular', 'gamif_simulacion', None,
                            {'evento': evento, 'xp_inicial': xp_inicial, 'dry_run': True})
        return build_cors_response({'success': True, 'simulacion': resultado})
    except Exception as e:
        logger.error(f"Error en simular_gamificacion: {e}")
        return build_cors_response({'success': False, 'error': str(e)}, 200)


# ═══════════════════════════════════════════════════════════════════════════════
# GAMIFICACIÓN — RECÁLCULO MASIVO (Admin Panel A14)
# Condición 1: dry-run OBLIGATORIO (preview) antes de aplicar.
# Condición 2: aplicar exige @superadmin_required y queda auditado con el conteo.
# ═══════════════════════════════════════════════════════════════════════════════

RECALC_CAP = 2000  # tope de negocios procesados por corrida (se reporta si se alcanza)


def _recalc_niveles_diffs(limite=RECALC_CAP):
    """Calcula (sin escribir) qué negocios cambiarían de nivel. Devuelve (diffs, total, capado)."""
    from src.models.colombia_data.ratings.negocio_gamificacion import NegocioGamificacion
    from src.models.colombia_data.ratings.config_gamificacion import nivel_por_xp
    niveles = NegocioGamificacion.NIVELES
    filas = (NegocioGamificacion.query
             .order_by(NegocioGamificacion.negocio_id)
             .limit(limite + 1).all())
    capado = len(filas) > limite
    filas = filas[:limite]
    diffs = []
    for g in filas:
        nuevo, nombre = nivel_por_xp(g.xp_total or 0, niveles)
        if nuevo != g.nivel:
            diffs.append({'negocio_id': g.negocio_id, 'nivel_antes': g.nivel,
                          'nivel_despues': nuevo, 'nombre_despues': nombre})
    return diffs, len(filas), capado


def _recalc_insignias_preview(limite=RECALC_CAP):
    """Cuenta (sin escribir) cuántas insignias se otorgarían por negocio. (diffs, total, capado)."""
    from src.models.colombia_data.ratings.negocio_gamificacion import NegocioGamificacion
    from src.api.utils.badge_verification_service import BadgeVerificationService
    filas = (NegocioGamificacion.query
             .order_by(NegocioGamificacion.negocio_id)
             .limit(limite + 1).all())
    capado = len(filas) > limite
    filas = filas[:limite]
    diffs = []
    for g in filas:
        pend = BadgeVerificationService.simular_badges(g.negocio_id)
        if pend:
            diffs.append({'negocio_id': g.negocio_id, 'nuevas': len(pend),
                          'codigos': [p['codigo'] for p in pend][:8]})
    return diffs, len(filas), capado


@admin_bp.route('/gamificacion/recalcular/preview', methods=['POST', 'OPTIONS'])
@requiere_permiso('gamificacion')
def recalcular_preview():
    """
    POST /api/admin/gamificacion/recalcular/preview  body: { tipo: 'niveles'|'insignias' }
    DRY-RUN obligatorio: muestra cuántos negocios cambiarían y una muestra. NO escribe.
    """
    if request.method == 'OPTIONS':
        return build_cors_response()
    try:
        tipo = (request.get_json(silent=True) or {}).get('tipo', 'niveles')
        if tipo not in ('niveles', 'insignias'):
            return build_cors_response({'success': False, 'error': 'tipo inválido'}, 400)
        if tipo == 'niveles':
            diffs, total, capado = _recalc_niveles_diffs()
            total_afectados = len(diffs)
        else:
            diffs, total, capado = _recalc_insignias_preview()
            total_afectados = sum(d['nuevas'] for d in diffs)
        return build_cors_response({
            'success': True, 'tipo': tipo, 'dry_run': True,
            'negocios_revisados': total,
            'negocios_afectados': len(diffs),
            'total_cambios': total_afectados,
            'muestra': diffs[:50],
            'capado': capado, 'cap': RECALC_CAP,
        })
    except Exception as e:
        logger.error(f"Error en recalcular_preview: {e}")
        return build_cors_response({'success': False, 'error': str(e)}, 200)


@admin_bp.route('/gamificacion/recalcular/aplicar', methods=['POST', 'OPTIONS'])
@superadmin_required   # Condición 2: solo superadmin puede aplicar
def recalcular_aplicar():
    """
    POST /api/admin/gamificacion/recalcular/aplicar  body: { tipo, confirmar: true }
    Aplica el recálculo. Requiere superadmin + confirmar=true (el panel solo lo envía tras el preview).
    Auditado con el conteo de registros modificados.
    """
    if request.method == 'OPTIONS':
        return build_cors_response()
    try:
        data = request.get_json(silent=True) or {}
        tipo = data.get('tipo', 'niveles')
        if tipo not in ('niveles', 'insignias'):
            return build_cors_response({'success': False, 'error': 'tipo inválido'}, 400)
        if data.get('confirmar') is not True:
            return build_cors_response({'success': False,
                'error': 'Debes ejecutar y confirmar la vista previa antes de aplicar'}, 400)

        from src.models.database import db
        modificados = 0
        detalle = {}

        if tipo == 'niveles':
            from src.models.colombia_data.ratings.negocio_gamificacion import NegocioGamificacion
            from src.models.colombia_data.ratings.config_gamificacion import nivel_por_xp
            niveles = NegocioGamificacion.NIVELES
            for g in NegocioGamificacion.query.limit(RECALC_CAP).all():
                nuevo, _ = nivel_por_xp(g.xp_total or 0, niveles)
                if nuevo != g.nivel:
                    g.nivel = nuevo
                    modificados += 1
            db.session.commit()
            detalle = {'niveles_actualizados': modificados}
        else:
            from src.models.colombia_data.ratings.negocio_gamificacion import NegocioGamificacion
            from src.api.utils.badge_verification_service import BadgeVerificationService
            insignias_nuevas = 0
            for g in NegocioGamificacion.query.limit(RECALC_CAP).all():
                res = BadgeVerificationService.verificar_badges(g.negocio_id)
                n = res.get('total_nuevos', 0) if isinstance(res, dict) else 0
                if n:
                    modificados += 1
                    insignias_nuevas += n
            detalle = {'negocios_con_insignias_nuevas': modificados, 'insignias_otorgadas': insignias_nuevas}

        registrar_auditoria('recalcular', f'gamif_{tipo}', None,
                            {'tipo': tipo, 'modificados': modificados, **detalle})
        return build_cors_response({'success': True, 'tipo': tipo,
                                    'modificados': modificados, 'detalle': detalle,
                                    'message': f'Recálculo aplicado: {modificados} registros modificados'})
    except Exception as e:
        logger.error(f"Error en recalcular_aplicar: {e}")
        try:
            from src.models.database import db as _db
            _db.session.rollback()
        except Exception:
            pass
        return build_cors_response({'success': False, 'error': str(e)}, 500)


# ═══════════════════════════════════════════════════════════════════════════════
# GAMIFICACIÓN — PARÁMETROS DE SUGERENCIAS/COMPARATIVAS (Admin Panel A12)
# ═══════════════════════════════════════════════════════════════════════════════

@admin_bp.route('/gamificacion/sugerencias-config', methods=['GET'])
@requiere_permiso('gamificacion')
def get_gamif_sugerencias():
    """GET /api/admin/gamificacion/sugerencias-config → parámetros efectivos + default."""
    try:
        from src.models.colombia_data.ratings.config_gamificacion import (
            get_sugerencias_config, SUGERENCIAS_DEFAULT
        )
        return build_cors_response({'success': True,
                                    'config': get_sugerencias_config(),
                                    'default': SUGERENCIAS_DEFAULT})
    except Exception as e:
        logger.error(f"Error en get_gamif_sugerencias: {e}")
        return build_cors_response({'success': False, 'error': str(e)}, 200)


@admin_bp.route('/gamificacion/sugerencias-config', methods=['PUT'])
@requiere_permiso('gamificacion')
def update_gamif_sugerencias():
    """PUT /api/admin/gamificacion/sugerencias-config → ajusta umbrales y límites."""
    try:
        from src.models.colombia_data.ratings.config_gamificacion import (
            validar_sugerencias_config, set_sugerencias_config, get_sugerencias_config
        )
        antes = get_sugerencias_config()
        ok, limpio, error = validar_sugerencias_config(request.get_json(silent=True) or {})
        if not ok:
            return build_cors_response({'success': False, 'error': error}, 400)
        set_sugerencias_config(limpio)
        registrar_auditoria('editar', 'gamif_sugerencias', None, {'antes': antes, 'despues': limpio})
        return build_cors_response({'success': True, 'config': limpio, 'message': 'Parámetros actualizados'})
    except Exception as e:
        logger.error(f"Error en update_gamif_sugerencias: {e}")
        try:
            from src.models.database import db as _db
            _db.session.rollback()
        except Exception:
            pass
        return build_cors_response({'success': False, 'error': str(e)}, 500)


# ═══════════════════════════════════════════════════════════════════════════════
# INSIGNIAS — CRUD del catálogo (Admin Panel A15)
# Editar/crear/desactivar badges sin tocar código. Editar marca editado_admin=True
# para que el seeder de arranque NO sobreescriba los cambios.
# ═══════════════════════════════════════════════════════════════════════════════

def _badge_admin_dict(b):
    return {
        'id': b.id, 'codigo': b.codigo, 'nombre': b.nombre, 'descripcion': b.descripcion,
        'icono': b.icono, 'color_primario': b.color_primario, 'color_fondo': b.color_fondo,
        'gradiente': b.gradiente, 'categoria': b.categoria, 'nivel': b.nivel,
        'nivel_nombre': b.get_nivel_nombre(), 'puntos': b.puntos,
        'criterio_tipo': b.criterio_tipo, 'criterio_valor': b.criterio_valor,
        'criterio_operador': b.criterio_operador, 'activo': bool(b.activo),
        'es_secreto': bool(b.es_secreto), 'es_exclusivo': bool(b.es_exclusivo),
        'visible_en_catalogo': bool(b.visible_en_catalogo), 'orden': b.orden,
        'max_otorgamientos': b.max_otorgamientos, 'total_otorgados': b.total_otorgados or 0,
        'editado_admin': bool(getattr(b, 'editado_admin', False)),
    }


@admin_bp.route('/insignias', methods=['GET'])
@requiere_permiso('insignias')
def list_insignias():
    """GET /api/admin/insignias → catálogo completo (incl. inactivas y secretas)."""
    try:
        from src.models.colombia_data.ratings.negocio_badge import NegocioBadge
        badges = NegocioBadge.query.order_by(NegocioBadge.orden, NegocioBadge.nivel.desc()).all()
        return build_cors_response({'success': True, 'total': len(badges),
                                    'insignias': [_badge_admin_dict(b) for b in badges]})
    except Exception as e:
        logger.error(f"Error en list_insignias: {e}")
        return build_cors_response({'success': False, 'error': str(e), 'insignias': []}, 200)


@admin_bp.route('/insignias', methods=['POST'])
@requiere_permiso('insignias')
def create_insignia():
    """POST /api/admin/insignias → crea un badge nuevo."""
    try:
        from src.models.colombia_data.ratings.negocio_badge import NegocioBadge
        from src.models.colombia_data.ratings.config_gamificacion import validar_badge
        from src.models.database import db
        ok, limpio, error = validar_badge(request.get_json(silent=True) or {}, requerir_codigo=True)
        if not ok:
            return build_cors_response({'success': False, 'error': error}, 400)
        if NegocioBadge.query.filter_by(codigo=limpio['codigo']).first():
            return build_cors_response({'success': False, 'error': 'Ya existe una insignia con ese código'}, 400)
        limpio['editado_admin'] = True
        badge = NegocioBadge(**limpio)
        db.session.add(badge)
        db.session.commit()
        registrar_auditoria('crear', 'insignia', badge.id, {'codigo': badge.codigo, 'nombre': badge.nombre})
        return build_cors_response({'success': True, 'insignia': _badge_admin_dict(badge),
                                    'message': 'Insignia creada'}, 201)
    except Exception as e:
        logger.error(f"Error en create_insignia: {e}")
        try:
            from src.models.database import db as _db; _db.session.rollback()
        except Exception:
            pass
        return build_cors_response({'success': False, 'error': str(e)}, 500)


@admin_bp.route('/insignias/<int:badge_id>', methods=['PUT'])
@requiere_permiso('insignias')
def update_insignia(badge_id):
    """PUT /api/admin/insignias/<id> → edita un badge (marca editado_admin)."""
    try:
        from src.models.colombia_data.ratings.negocio_badge import NegocioBadge
        from src.models.colombia_data.ratings.config_gamificacion import validar_badge
        from src.models.database import db
        badge = NegocioBadge.query.get(badge_id)
        if not badge:
            return build_cors_response({'error': 'Insignia no encontrada'}, 404)
        ok, limpio, error = validar_badge(request.get_json(silent=True) or {})
        if not ok:
            return build_cors_response({'success': False, 'error': error}, 400)
        antes = {'nombre': badge.nombre, 'nivel': badge.nivel, 'puntos': badge.puntos,
                 'activo': bool(badge.activo)}
        for campo, valor in limpio.items():
            setattr(badge, campo, valor)
        badge.editado_admin = True
        db.session.commit()
        registrar_auditoria('editar', 'insignia', badge_id, {'antes': antes, 'cambios': limpio})
        return build_cors_response({'success': True, 'insignia': _badge_admin_dict(badge),
                                    'message': 'Insignia actualizada'})
    except Exception as e:
        logger.error(f"Error en update_insignia: {e}")
        try:
            from src.models.database import db as _db; _db.session.rollback()
        except Exception:
            pass
        return build_cors_response({'success': False, 'error': str(e)}, 500)


@admin_bp.route('/insignias/<int:badge_id>', methods=['DELETE'])
@superadmin_required   # borrado = solo superadmin
def delete_insignia(badge_id):
    """DELETE /api/admin/insignias/<id> → elimina un badge SOLO si nadie lo tiene."""
    try:
        from src.models.colombia_data.ratings.negocio_badge import NegocioBadge
        from src.models.database import db
        badge = NegocioBadge.query.get(badge_id)
        if not badge:
            return build_cors_response({'error': 'Insignia no encontrada'}, 404)
        if (badge.total_otorgados or 0) > 0:
            return build_cors_response({'success': False,
                'error': 'No se puede eliminar: ya fue otorgada. Desactívala en su lugar.'}, 400)
        cod = badge.codigo
        db.session.delete(badge)
        db.session.commit()
        registrar_auditoria('eliminar', 'insignia', badge_id, {'codigo': cod})
        return build_cors_response({'success': True, 'message': 'Insignia eliminada'})
    except Exception as e:
        logger.error(f"Error en delete_insignia: {e}")
        try:
            from src.models.database import db as _db; _db.session.rollback()
        except Exception:
            pass
        return build_cors_response({'success': False, 'error': str(e)}, 500)


# ═══════════════════════════════════════════════════════════════════════════════
# INSIGNIAS — EDITOR VISUAL DE CRITERIOS (Admin Panel A16)
# Lista de métricas disponibles + vista previa de cuántos negocios cumplirían.
# ═══════════════════════════════════════════════════════════════════════════════

@admin_bp.route('/insignias/metricas', methods=['GET'])
@requiere_permiso('insignias')
def list_metricas_criterio():
    """GET /api/admin/insignias/metricas → métricas disponibles + operadores."""
    try:
        from src.models.colombia_data.ratings.config_gamificacion import (
            METRICAS_CRITERIO, OPERADORES_CRITERIO
        )
        return build_cors_response({'success': True, 'metricas': METRICAS_CRITERIO,
                                    'operadores': sorted(OPERADORES_CRITERIO)})
    except Exception as e:
        logger.error(f"Error en list_metricas_criterio: {e}")
        return build_cors_response({'success': False, 'error': str(e), 'metricas': []}, 200)


@admin_bp.route('/insignias/criterio/preview', methods=['POST', 'OPTIONS'])
@requiere_permiso('insignias')
def preview_criterio():
    """
    POST /api/admin/insignias/criterio/preview
    body: { criterio_tipo, criterio_operador, criterio_valor }
    Cuenta cuántos negocios CUMPLIRÍAN el criterio (sin otorgar nada). Acotado.
    """
    if request.method == 'OPTIONS':
        return build_cors_response()
    try:
        from src.models.colombia_data.ratings.config_gamificacion import (
            METRICAS_CRITERIO_KEYS, OPERADORES_CRITERIO
        )
        from src.api.utils.badge_verification_service import BadgeVerificationService
        from src.models.colombia_data.ratings.negocio_gamificacion import NegocioGamificacion

        data = request.get_json(silent=True) or {}
        tipo = (data.get('criterio_tipo') or '').strip()
        op = (data.get('criterio_operador') or '>=').strip()
        if tipo not in METRICAS_CRITERIO_KEYS:
            return build_cors_response({'success': False, 'error': 'Métrica desconocida'}, 400)
        if op not in OPERADORES_CRITERIO:
            return build_cors_response({'success': False, 'error': 'Operador inválido'}, 400)
        try:
            valor = float(data.get('criterio_valor'))
        except (TypeError, ValueError):
            return build_cors_response({'success': False, 'error': 'Valor inválido'}, 400)

        CAP = 1000
        filas = (NegocioGamificacion.query
                 .with_entities(NegocioGamificacion.negocio_id)
                 .limit(CAP + 1).all())
        capado = len(filas) > CAP
        filas = filas[:CAP]
        revisados = cumplen = 0
        for (nid,) in filas:
            try:
                metr = BadgeVerificationService._calcular_metricas_para_badges(nid)
                val_actual = metr.get(tipo)
                if val_actual is None:
                    continue
                revisados += 1
                if BadgeVerificationService._evaluar_criterio(val_actual, op, valor):
                    cumplen += 1
            except Exception:
                continue
        return build_cors_response({
            'success': True, 'cumplen': cumplen, 'revisados': revisados,
            'capado': capado, 'criterio': f"{tipo} {op} {valor}",
        })
    except Exception as e:
        logger.error(f"Error en preview_criterio: {e}")
        return build_cors_response({'success': False, 'error': str(e)}, 200)


# ═══════════════════════════════════════════════════════════════════════════════
# INSIGNIAS — OTORGAR / REVOCAR MANUALMENTE (Admin Panel A17)
# Para soporte y premios especiales. Idempotente y auditado.
# ═══════════════════════════════════════════════════════════════════════════════

@admin_bp.route('/insignias/<int:badge_id>/otorgar', methods=['POST', 'OPTIONS'])
@requiere_permiso('insignias')
def otorgar_insignia(badge_id):
    """POST /api/admin/insignias/<badge_id>/otorgar  body: {negocio_id, motivo?}"""
    if request.method == 'OPTIONS':
        return build_cors_response()
    try:
        from src.models.colombia_data.ratings.negocio_badge import NegocioBadge
        from src.models.colombia_data.ratings.negocio_badge_obtenido import NegocioBadgeObtenido
        from src.models.database import db
        from datetime import datetime as _dt
        data = request.get_json(silent=True) or {}
        try:
            nid = int(data.get('negocio_id'))
        except (TypeError, ValueError):
            return build_cors_response({'success': False, 'error': 'negocio_id inválido'}, 400)
        motivo = str(data.get('motivo', '')).strip()[:255]

        badge = NegocioBadge.query.get(badge_id)
        if not badge:
            return build_cors_response({'success': False, 'error': 'Insignia no encontrada'}, 404)
        # validar que el negocio exista
        if not _scalar_admin("SELECT 1 AS v FROM negocios WHERE id_negocio = %s", (nid,)):
            return build_cors_response({'success': False, 'error': 'Negocio no encontrado'}, 404)

        ob = NegocioBadgeObtenido.query.filter_by(negocio_id=nid, badge_id=badge_id).first()
        if ob and ob.activo:
            return build_cors_response({'success': True, 'ya_tenia': True,
                                        'message': 'El negocio ya tiene esta insignia'})
        if ob and not ob.activo:
            ob.activo = True
            ob.fecha_revocacion = None
            ob.motivo_revocacion = None
            ob.contexto = f'Otorgada por admin{": " + motivo if motivo else ""}'
        else:
            ob = NegocioBadgeObtenido(
                negocio_id=nid, badge_id=badge_id, fecha_obtencion=_dt.utcnow(),
                contexto=f'Otorgada por admin{": " + motivo if motivo else ""}',
                notificado=False, visto=False, activo=True)
            db.session.add(ob)
        badge.total_otorgados = (badge.total_otorgados or 0) + 1
        db.session.commit()
        registrar_auditoria('otorgar', 'insignia', badge_id,
                            {'negocio_id': nid, 'codigo': badge.codigo, 'motivo': motivo})
        return build_cors_response({'success': True, 'message': f'Insignia «{badge.nombre}» otorgada al negocio {nid}'})
    except Exception as e:
        logger.error(f"Error en otorgar_insignia: {e}")
        try:
            from src.models.database import db as _db; _db.session.rollback()
        except Exception:
            pass
        return build_cors_response({'success': False, 'error': str(e)}, 500)


@admin_bp.route('/insignias/<int:badge_id>/revocar', methods=['POST', 'OPTIONS'])
@superadmin_required   # revocar = solo superadmin (acción sensible)
def revocar_insignia(badge_id):
    """POST /api/admin/insignias/<badge_id>/revocar  body: {negocio_id, motivo}"""
    if request.method == 'OPTIONS':
        return build_cors_response()
    try:
        from src.models.colombia_data.ratings.negocio_badge import NegocioBadge
        from src.models.colombia_data.ratings.negocio_badge_obtenido import NegocioBadgeObtenido
        from src.models.database import db
        from datetime import datetime as _dt
        data = request.get_json(silent=True) or {}
        try:
            nid = int(data.get('negocio_id'))
        except (TypeError, ValueError):
            return build_cors_response({'success': False, 'error': 'negocio_id inválido'}, 400)
        motivo = str(data.get('motivo', '')).strip()[:255]
        if not motivo:
            return build_cors_response({'success': False, 'error': 'El motivo es obligatorio para revocar'}, 400)

        ob = NegocioBadgeObtenido.query.filter_by(negocio_id=nid, badge_id=badge_id, activo=True).first()
        if not ob:
            return build_cors_response({'success': False, 'error': 'El negocio no tiene esa insignia activa'}, 404)
        ob.activo = False
        ob.fecha_revocacion = _dt.utcnow()
        ob.motivo_revocacion = motivo
        badge = NegocioBadge.query.get(badge_id)
        if badge:
            badge.total_otorgados = max(0, (badge.total_otorgados or 0) - 1)
        db.session.commit()
        registrar_auditoria('revocar', 'insignia', badge_id,
                            {'negocio_id': nid, 'motivo': motivo,
                             'codigo': badge.codigo if badge else None})
        return build_cors_response({'success': True, 'message': f'Insignia revocada al negocio {nid}'})
    except Exception as e:
        logger.error(f"Error en revocar_insignia: {e}")
        try:
            from src.models.database import db as _db; _db.session.rollback()
        except Exception:
            pass
        return build_cors_response({'success': False, 'error': str(e)}, 500)
