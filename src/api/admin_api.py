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

        # A28: si se aprobó, premiar en gamificación (idempotente y a prueba de fallos).
        recompensa = None
        if nuevo_estado == 'aprobado':
            try:
                from src.api.utils.challenge_gamif_service import premiar_participacion_aprobada
                from src.models.database import db as _db
                recompensa = premiar_participacion_aprobada(_db.session, participacion_id)
            except Exception as _ge:
                logger.warning(f"[A28] premio participación no crítico: {_ge}")

        return jsonify({
            'success': True,
            'message': f'Participación actualizada a "{nuevo_estado}"',
            'recompensa_gamif': recompensa,
        }), 200

    except Exception as e:
        logger.error(f"Error actualizando participación: {e}")
        return jsonify({'error': str(e)}), 500


# ═══════════════════════════════════════════════════════════════════════════════
# CHALLENGES 2.0 — integración con gamificación (Admin Panel A28)
# Finalizar challenge premiando al ganador + recompensas configurables.
# ═══════════════════════════════════════════════════════════════════════════════
@admin_bp.route('/challenges/<int:challenge_id>/finalizar', methods=['POST'])
@requiere_permiso('challenges')
def finalizar_challenge(challenge_id):
    """
    POST /api/admin/challenges/<id>/finalizar
    Marca el challenge como finalizado y premia (idempotente) al ganador en gamificación.
    """
    from src.models.database import db as _db
    try:
        from src.api.utils.challenge_gamif_service import finalizar_y_premiar
        resultado = finalizar_y_premiar(_db.session, challenge_id)
        if not resultado.get('success'):
            return build_cors_response({'success': False, 'error': resultado.get('error', 'Error')}, 404)
        registrar_auditoria('editar', 'challenge', challenge_id, {
            'accion': 'finalizar',
            'ganador': resultado.get('ganador'),
            'ya_premiado': resultado.get('ya_premiado'),
        })
        msg = 'Challenge finalizado'
        if resultado.get('ganador'):
            g_ = resultado['ganador']
            msg += f" — ganador: {g_['nombre']} (+{g_['xp']} XP, +{g_['tukoins']} TuKoins)"
        elif resultado.get('ya_premiado'):
            msg += ' (ya estaba premiado)'
        return build_cors_response({'success': True, 'message': msg, **resultado})
    except Exception as e:
        logger.error(f"Error en finalizar_challenge: {e}")
        try:
            _db.session.rollback()
        except Exception:
            pass
        return build_cors_response({'success': False, 'error': str(e)}, 500)


@admin_bp.route('/challenges/recompensas-config', methods=['GET'])
@requiere_permiso('challenges')
def get_challenge_rewards_cfg():
    """GET /api/admin/challenges/recompensas-config → recompensas efectivas + default."""
    try:
        from src.models.colombia_data.ratings.config_gamificacion import (
            get_challenge_rewards, CHALLENGE_REWARDS_DEFAULT
        )
        return build_cors_response({'success': True, 'config': get_challenge_rewards(),
                                    'default': CHALLENGE_REWARDS_DEFAULT})
    except Exception as e:
        logger.error(f"Error en get_challenge_rewards_cfg: {e}")
        return build_cors_response({'success': False, 'error': str(e)}, 200)


@admin_bp.route('/challenges/recompensas-config', methods=['PUT'])
@requiere_permiso('challenges')
def update_challenge_rewards_cfg():
    """PUT /api/admin/challenges/recompensas-config  body: { xp_participar, tukoins_participar, xp_ganador, tukoins_ganador }"""
    try:
        from src.models.colombia_data.ratings.config_gamificacion import (
            validar_challenge_rewards, set_challenge_rewards, get_challenge_rewards
        )
        antes = get_challenge_rewards()
        ok, limpio, error = validar_challenge_rewards(request.get_json(silent=True) or {})
        if not ok:
            return build_cors_response({'success': False, 'error': error}, 400)
        set_challenge_rewards(limpio)
        registrar_auditoria('editar', 'challenge_rewards', None, {'antes': antes, 'despues': limpio})
        return build_cors_response({'success': True, 'config': limpio, 'message': 'Recompensas de challenge actualizadas'})
    except Exception as e:
        logger.error(f"Error en update_challenge_rewards_cfg: {e}")
        try:
            from src.models.database import db as _db
            _db.session.rollback()
        except Exception:
            pass
        return build_cors_response({'success': False, 'error': str(e)}, 500)


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

        # A30: excluir usuarios en papelera del listado normal.
        where = "WHERE COALESCE(u.eliminado, FALSE) = FALSE"
        params = []
        if search:
            where += """
                AND (
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


# ═══════════════════════════════════════════════════════════════════════════════
# SOFT-DELETE + PAPELERA (Admin Panel A30)
# Baja lógica con papelera y restauración para negocios y usuarios. El borrado
# permanente (purga) sigue siendo el DELETE en cascada existente (superadmin).
# ═══════════════════════════════════════════════════════════════════════════════
@admin_bp.route('/negocios/<int:negocio_id>/papelera', methods=['POST'])
@requiere_permiso('negocios')
def negocio_a_papelera(negocio_id):
    """POST /api/admin/negocios/<id>/papelera → baja lógica (eliminado=true, activo=false)."""
    try:
        conn = get_db_connection(); cur = conn.cursor()
        cur.execute("SELECT nombre_negocio FROM negocios WHERE id_negocio = %s", (negocio_id,))
        row = cur.fetchone()
        if not row:
            cur.close(); conn.close()
            return build_cors_response({'success': False, 'error': 'Negocio no encontrado'}, 404)
        cur.execute("""
            UPDATE negocios
            SET eliminado = TRUE, eliminado_en = NOW(), eliminado_por = %s, activo = FALSE
            WHERE id_negocio = %s
        """, (getattr(g, 'user_email', None) or 'admin', negocio_id))
        conn.commit(); cur.close(); conn.close()
        registrar_auditoria('eliminar', 'negocio', negocio_id,
                            {'tipo': 'papelera', 'nombre': row['nombre_negocio']})
        return build_cors_response({'success': True, 'message': f"Negocio '{row['nombre_negocio']}' enviado a la papelera"})
    except Exception as e:
        logger.error(f"Error en negocio_a_papelera: {e}")
        return build_cors_response({'success': False, 'error': str(e)}, 500)


@admin_bp.route('/negocios/<int:negocio_id>/restaurar', methods=['POST'])
@requiere_permiso('negocios')
def restaurar_negocio(negocio_id):
    """POST /api/admin/negocios/<id>/restaurar → revierte la baja lógica."""
    try:
        conn = get_db_connection(); cur = conn.cursor()
        cur.execute("SELECT nombre_negocio FROM negocios WHERE id_negocio = %s", (negocio_id,))
        row = cur.fetchone()
        if not row:
            cur.close(); conn.close()
            return build_cors_response({'success': False, 'error': 'Negocio no encontrado'}, 404)
        cur.execute("""
            UPDATE negocios
            SET eliminado = FALSE, eliminado_en = NULL, eliminado_por = NULL, activo = TRUE
            WHERE id_negocio = %s
        """, (negocio_id,))
        conn.commit(); cur.close(); conn.close()
        registrar_auditoria('restaurar', 'negocio', negocio_id, {'nombre': row['nombre_negocio']})
        return build_cors_response({'success': True, 'message': f"Negocio '{row['nombre_negocio']}' restaurado"})
    except Exception as e:
        logger.error(f"Error en restaurar_negocio: {e}")
        return build_cors_response({'success': False, 'error': str(e)}, 500)


@admin_bp.route('/usuarios/<int:user_id>/papelera', methods=['POST'])
@superadmin_required
def usuario_a_papelera(user_id):
    """POST /api/admin/usuarios/<id>/papelera → baja lógica (eliminado=true, active=false). No admins."""
    try:
        conn = get_db_connection(); cur = conn.cursor()
        cur.execute("""
            SELECT u.correo, a.id AS es_admin
            FROM usuarios u
            LEFT JOIN administradores a ON LOWER(a.email) = LOWER(u.correo) AND a.activo = true
            WHERE u.id_usuario = %s
        """, (user_id,))
        u = cur.fetchone()
        if not u:
            cur.close(); conn.close()
            return build_cors_response({'success': False, 'error': 'Usuario no encontrado'}, 404)
        if u['es_admin']:
            cur.close(); conn.close()
            return build_cors_response({'success': False, 'error': 'No se puede enviar a papelera a un administrador activo. Desactívalo primero.'}, 403)
        cur.execute("""
            UPDATE usuarios
            SET eliminado = TRUE, eliminado_en = NOW(), eliminado_por = %s, active = FALSE
            WHERE id_usuario = %s
        """, (getattr(g, 'user_email', None) or 'admin', user_id))
        conn.commit(); cur.close(); conn.close()
        registrar_auditoria('eliminar', 'usuario', user_id, {'tipo': 'papelera', 'correo': u['correo']})
        return build_cors_response({'success': True, 'message': f"Usuario '{u['correo']}' enviado a la papelera"})
    except Exception as e:
        logger.error(f"Error en usuario_a_papelera: {e}")
        return build_cors_response({'success': False, 'error': str(e)}, 500)


@admin_bp.route('/usuarios/<int:user_id>/restaurar', methods=['POST'])
@superadmin_required
def restaurar_usuario(user_id):
    """POST /api/admin/usuarios/<id>/restaurar → revierte la baja lógica."""
    try:
        conn = get_db_connection(); cur = conn.cursor()
        cur.execute("SELECT correo FROM usuarios WHERE id_usuario = %s", (user_id,))
        u = cur.fetchone()
        if not u:
            cur.close(); conn.close()
            return build_cors_response({'success': False, 'error': 'Usuario no encontrado'}, 404)
        cur.execute("""
            UPDATE usuarios
            SET eliminado = FALSE, eliminado_en = NULL, eliminado_por = NULL, active = TRUE
            WHERE id_usuario = %s
        """, (user_id,))
        conn.commit(); cur.close(); conn.close()
        registrar_auditoria('restaurar', 'usuario', user_id, {'correo': u['correo']})
        return build_cors_response({'success': True, 'message': f"Usuario '{u['correo']}' restaurado"})
    except Exception as e:
        logger.error(f"Error en restaurar_usuario: {e}")
        return build_cors_response({'success': False, 'error': str(e)}, 500)


@admin_bp.route('/papelera', methods=['GET'])
@requiere_permiso('negocios')
def listar_papelera():
    """GET /api/admin/papelera → negocios y usuarios en papelera (baja lógica)."""
    try:
        conn = get_db_connection(); cur = conn.cursor()
        cur.execute("""
            SELECT id_negocio, nombre_negocio, slug, eliminado_en, eliminado_por
            FROM negocios WHERE eliminado IS TRUE
            ORDER BY eliminado_en DESC NULLS LAST LIMIT 200
        """)
        negocios = [{
            'id': r['id_negocio'], 'nombre': r['nombre_negocio'], 'slug': r.get('slug'),
            'eliminado_en': r['eliminado_en'].isoformat() if r['eliminado_en'] else None,
            'eliminado_por': r.get('eliminado_por'),
        } for r in cur.fetchall()]
        cur.execute("""
            SELECT id_usuario, nombre, apellidos, correo, eliminado_en, eliminado_por
            FROM usuarios WHERE eliminado IS TRUE
            ORDER BY eliminado_en DESC NULLS LAST LIMIT 200
        """)
        usuarios = [{
            'id': r['id_usuario'], 'nombre': f"{r['nombre']} {r.get('apellidos') or ''}".strip(),
            'correo': r['correo'],
            'eliminado_en': r['eliminado_en'].isoformat() if r['eliminado_en'] else None,
            'eliminado_por': r.get('eliminado_por'),
        } for r in cur.fetchall()]
        cur.close(); conn.close()
        return build_cors_response({'success': True, 'negocios': negocios, 'usuarios': usuarios,
                                    'total': len(negocios) + len(usuarios)})
    except Exception as e:
        logger.error(f"Error en listar_papelera: {e}")
        return build_cors_response({'success': False, 'error': str(e), 'negocios': [], 'usuarios': []}, 200)


# ═══════════════════════════════════════════════════════════════════════════════
# MODERACIÓN DE VIDEOS / FEED + PERFILES DE CREADOR (Admin Panel A31)
# ═══════════════════════════════════════════════════════════════════════════════
@admin_bp.route('/videos', methods=['GET'])
@requiere_permiso('negocios')
def admin_videos():
    """GET /api/admin/videos?estado=&limit= → videos con negocio + resumen de moderación."""
    from sqlalchemy import text as _t
    from src.models.database import db as _db
    try:
        estado = (request.args.get('estado', '') or '').strip().lower()
        limit  = min(int(request.args.get('limit', 60) or 60), 200)
        sql = """
            SELECT v.id, v.titulo, v.url_thumbnail, v.url_video, v.negocio_id,
                   n.nombre_negocio, v.estado_moderacion, v.visible, v.destacado,
                   v.vistas, v.likes, v.motivo_rechazo, v.fecha_creacion
            FROM negocio_videos v
            LEFT JOIN negocios n ON n.id_negocio = v.negocio_id
        """
        params = {'lim': limit}
        cond = []
        if estado == 'ocultos':
            cond.append("v.visible = FALSE")
        elif estado in ('pendiente', 'aprobado', 'rechazado'):
            cond.append("LOWER(v.estado_moderacion) = :estado"); params['estado'] = estado
        if cond:
            sql += " WHERE " + " AND ".join(cond)
        sql += " ORDER BY v.fecha_creacion DESC NULLS LAST LIMIT :lim"
        rows = _db.session.execute(_t(sql), params).fetchall()
        videos = [{
            'id': r[0], 'titulo': r[1], 'thumbnail': r[2], 'url': r[3],
            'negocio_id': r[4], 'negocio': r[5] or f'#{r[4]}',
            'estado_moderacion': r[6], 'visible': r[7], 'destacado': r[8],
            'vistas': r[9] or 0, 'likes': r[10] or 0, 'motivo_rechazo': r[11],
            'fecha': r[12].isoformat() if r[12] else None,
        } for r in rows]
        res = _db.session.execute(_t("""
            SELECT LOWER(estado_moderacion), COUNT(*) FROM negocio_videos GROUP BY LOWER(estado_moderacion)
        """)).fetchall()
        resumen = {row[0]: row[1] for row in res}
        resumen['ocultos'] = int(_db.session.execute(_t(
            "SELECT COUNT(*) FROM negocio_videos WHERE visible = FALSE")).scalar() or 0)
        return build_cors_response({'success': True, 'videos': videos, 'resumen': resumen})
    except Exception as e:
        logger.error(f"Error en admin_videos: {e}")
        return build_cors_response({'success': False, 'error': str(e), 'videos': []}, 200)


@admin_bp.route('/videos/<int:video_id>/moderar', methods=['POST'])
@requiere_permiso('negocios')
def moderar_video(video_id):
    """POST /api/admin/videos/<id>/moderar  body: { accion, motivo? }"""
    from sqlalchemy import text as _t
    from src.models.database import db as _db
    try:
        from src.models.colombia_data.negocio_video import aplicar_accion_video
        payload = request.get_json(silent=True) or {}
        accion = (payload.get('accion') or '').strip().lower()
        cambios = aplicar_accion_video(accion)
        if not cambios:
            return build_cors_response({'success': False, 'error': 'Acción inválida'}, 400)
        existe = _db.session.execute(_t("SELECT 1 FROM negocio_videos WHERE id = :id"), {'id': video_id}).fetchone()
        if not existe:
            return build_cors_response({'success': False, 'error': 'Video no encontrado'}, 404)
        sets, params = [], {'id': video_id}
        for col, val in cambios.items():
            sets.append(f"{col} = :{col}"); params[col] = val
        if accion in ('aprobar', 'rechazar'):
            sets.append("fecha_moderacion = NOW()")
        if accion == 'rechazar':
            sets.append("motivo_rechazo = :motivo"); params['motivo'] = str(payload.get('motivo', ''))[:255]
        _db.session.execute(_t(f"UPDATE negocio_videos SET {', '.join(sets)} WHERE id = :id"), params)
        _db.session.commit()
        registrar_auditoria('editar', 'video', video_id, {'accion': accion, 'cambios': cambios})
        return build_cors_response({'success': True, 'message': f'Video: {accion}'})
    except Exception as e:
        logger.error(f"Error en moderar_video: {e}")
        try:
            _db.session.rollback()
        except Exception:
            pass
        return build_cors_response({'success': False, 'error': str(e)}, 500)


@admin_bp.route('/perfiles-creador', methods=['GET'])
@requiere_permiso('negocios')
def admin_perfiles_creador():
    """GET /api/admin/perfiles-creador?buscar= → negocios con su perfil público (creador)."""
    try:
        buscar = (request.args.get('buscar', '') or '').strip()
        conn = get_db_connection(); cur = conn.cursor()
        if buscar:
            cur.execute("""
                SELECT id_negocio, nombre_negocio, slug, ciudad, perfil_publico
                FROM negocios
                WHERE COALESCE(eliminado, FALSE) = FALSE
                  AND (nombre_negocio ILIKE %s OR slug ILIKE %s)
                ORDER BY nombre_negocio LIMIT 50
            """, (f'%{buscar}%', f'%{buscar}%'))
        else:
            cur.execute("""
                SELECT id_negocio, nombre_negocio, slug, ciudad, perfil_publico
                FROM negocios
                WHERE COALESCE(eliminado, FALSE) = FALSE AND perfil_publico IS TRUE
                ORDER BY fecha_registro DESC LIMIT 50
            """)
        perfiles = [{
            'id': r['id_negocio'], 'nombre': r['nombre_negocio'], 'slug': r.get('slug'),
            'ciudad': r.get('ciudad'), 'perfil_publico': r['perfil_publico'],
        } for r in cur.fetchall()]
        cur.close(); conn.close()
        return build_cors_response({'success': True, 'perfiles': perfiles})
    except Exception as e:
        logger.error(f"Error en admin_perfiles_creador: {e}")
        return build_cors_response({'success': False, 'error': str(e), 'perfiles': []}, 200)


@admin_bp.route('/negocios/<int:negocio_id>/perfil-publico', methods=['POST'])
@requiere_permiso('negocios')
def moderar_perfil_creador(negocio_id):
    """POST /api/admin/negocios/<id>/perfil-publico  body: { visible: bool } → muestra/oculta el perfil de creador."""
    try:
        visible = bool((request.get_json(silent=True) or {}).get('visible'))
        conn = get_db_connection(); cur = conn.cursor()
        cur.execute("SELECT nombre_negocio FROM negocios WHERE id_negocio = %s", (negocio_id,))
        row = cur.fetchone()
        if not row:
            cur.close(); conn.close()
            return build_cors_response({'success': False, 'error': 'Negocio no encontrado'}, 404)
        cur.execute("UPDATE negocios SET perfil_publico = %s WHERE id_negocio = %s", (visible, negocio_id))
        conn.commit(); cur.close(); conn.close()
        registrar_auditoria('editar', 'perfil_creador', negocio_id,
                            {'perfil_publico': visible, 'nombre': row['nombre_negocio']})
        return build_cors_response({'success': True, 'perfil_publico': visible,
                                    'message': f"Perfil de '{row['nombre_negocio']}' {'visible' if visible else 'oculto'}"})
    except Exception as e:
        logger.error(f"Error en moderar_perfil_creador: {e}")
        return build_cors_response({'success': False, 'error': str(e)}, 500)


# ═══════════════════════════════════════════════════════════════════════════════
# MODERACIÓN DEL FEED DE COMUNIDAD (Admin Panel A32)
# Logros destacados (S32): nivel mínimo configurable + ocultar eventos abusivos.
# ═══════════════════════════════════════════════════════════════════════════════
@admin_bp.route('/feed-comunidad', methods=['GET'])
@requiere_permiso('gamificacion')
def admin_feed_comunidad():
    """GET /api/admin/feed-comunidad?limit= → eventos del feed (incluye ocultos) + config."""
    from sqlalchemy import text as _t
    from src.models.database import db as _db
    try:
        from src.models.colombia_data.ratings.config_gamificacion import get_feed_comunidad_config
        cfg = get_feed_comunidad_config()
        limit = min(int(request.args.get('limit', 50) or 50), 200)
        rows = _db.session.execute(_t("""
            SELECT o.id, n.id_negocio, n.nombre_negocio, b.nombre, b.icono, b.nivel,
                   o.fecha_obtencion, COALESCE(o.oculto_feed, FALSE) AS oculto,
                   COALESCE(o.activo, TRUE) AS activo
            FROM negocio_badges_obtenidos o
            JOIN negocio_badges b ON b.id = o.badge_id
            JOIN negocios n ON n.id_negocio = o.negocio_id
            WHERE b.nivel >= :niv
            ORDER BY o.fecha_obtencion DESC NULLS LAST
            LIMIT :lim
        """), {'niv': int(cfg.get('nivel_minimo', 3)), 'lim': limit}).fetchall()
        eventos = [{
            'id': r[0], 'negocio_id': r[1], 'negocio': r[2] or f'#{r[1]}',
            'badge': r[3], 'icono': r[4] or 'bi-award-fill', 'nivel': r[5] or 3,
            'fecha': r[6].isoformat() if r[6] else None,
            'oculto': bool(r[7]), 'activo': bool(r[8]),
        } for r in rows]
        return build_cors_response({'success': True, 'eventos': eventos, 'config': cfg})
    except Exception as e:
        logger.error(f"Error en admin_feed_comunidad: {e}")
        return build_cors_response({'success': False, 'error': str(e), 'eventos': []}, 200)


@admin_bp.route('/feed-comunidad/<int:obtenido_id>/ocultar', methods=['POST'])
@requiere_permiso('gamificacion')
def ocultar_evento_comunidad(obtenido_id):
    """POST /api/admin/feed-comunidad/<id>/ocultar  body: { oculto: bool } → oculta/muestra el logro en el feed (sin revocar el badge)."""
    from sqlalchemy import text as _t
    from src.models.database import db as _db
    try:
        oculto = bool((request.get_json(silent=True) or {}).get('oculto'))
        existe = _db.session.execute(_t("SELECT 1 FROM negocio_badges_obtenidos WHERE id = :id"), {'id': obtenido_id}).fetchone()
        if not existe:
            return build_cors_response({'success': False, 'error': 'Evento no encontrado'}, 404)
        _db.session.execute(_t("UPDATE negocio_badges_obtenidos SET oculto_feed = :o WHERE id = :id"),
                            {'o': oculto, 'id': obtenido_id})
        _db.session.commit()
        registrar_auditoria('editar', 'feed_comunidad', obtenido_id, {'oculto_feed': oculto})
        return build_cors_response({'success': True, 'oculto': oculto,
                                    'message': f"Logro {'oculto del' if oculto else 'visible en el'} feed"})
    except Exception as e:
        logger.error(f"Error en ocultar_evento_comunidad: {e}")
        try:
            _db.session.rollback()
        except Exception:
            pass
        return build_cors_response({'success': False, 'error': str(e)}, 500)


@admin_bp.route('/feed-comunidad/config', methods=['PUT'])
@requiere_permiso('gamificacion')
def update_feed_comunidad_config():
    """PUT /api/admin/feed-comunidad/config  body: { nivel_minimo, limite }"""
    try:
        from src.models.colombia_data.ratings.config_gamificacion import (
            validar_feed_comunidad_config, set_feed_comunidad_config, get_feed_comunidad_config
        )
        antes = get_feed_comunidad_config()
        ok, limpio, error = validar_feed_comunidad_config(request.get_json(silent=True) or {})
        if not ok:
            return build_cors_response({'success': False, 'error': error}, 400)
        set_feed_comunidad_config(limpio)
        registrar_auditoria('editar', 'feed_comunidad_config', None, {'antes': antes, 'despues': limpio})
        return build_cors_response({'success': True, 'config': limpio, 'message': 'Config del feed de comunidad actualizada'})
    except Exception as e:
        logger.error(f"Error en update_feed_comunidad_config: {e}")
        try:
            from src.models.database import db as _db
            _db.session.rollback()
        except Exception:
            pass
        return build_cors_response({'success': False, 'error': str(e)}, 500)


# ═══════════════════════════════════════════════════════════════════════════════
# ANUNCIOS / NOTIFICACIONES MASIVAS (Admin Panel A33)
# Enviar avisos in-app a segmentos (ciudad / plan / nivel) con plantillas.
# ═══════════════════════════════════════════════════════════════════════════════
@admin_bp.route('/anuncios/plantillas', methods=['GET'])
@requiere_permiso('usuarios')
def get_anuncio_plantillas():
    """GET /api/admin/anuncios/plantillas → plantillas rápidas predefinidas."""
    try:
        from src.api.utils.anuncios_service import PLANTILLAS_ANUNCIO
        return build_cors_response({'success': True, 'plantillas': PLANTILLAS_ANUNCIO})
    except Exception as e:
        logger.error(f"Error en get_anuncio_plantillas: {e}")
        return build_cors_response({'success': False, 'error': str(e), 'plantillas': []}, 200)


@admin_bp.route('/anuncios/preview', methods=['POST'])
@requiere_permiso('usuarios')
def preview_anuncio():
    """POST /api/admin/anuncios/preview  body: { ciudad?, plan?, nivel_min? } → nº de destinatarios."""
    from src.models.database import db as _db
    try:
        from src.api.utils.anuncios_service import contar_destinatarios
        filtros = request.get_json(silent=True) or {}
        total = contar_destinatarios(_db.session, filtros)
        return build_cors_response({'success': True, 'destinatarios': total})
    except Exception as e:
        logger.error(f"Error en preview_anuncio: {e}")
        return build_cors_response({'success': False, 'error': str(e), 'destinatarios': 0}, 200)


@admin_bp.route('/anuncios/enviar', methods=['POST'])
@requiere_permiso('usuarios')
def enviar_anuncio_masivo():
    """
    POST /api/admin/anuncios/enviar
    body: { titulo, mensaje, prioridad?, ciudad?, plan?, nivel_min?, confirmar:true }
    Crea una notificación in-app por cada usuario del segmento. Auditado.
    """
    from src.models.database import db as _db
    try:
        from src.api.utils.anuncios_service import enviar_anuncio, contar_destinatarios
        data = request.get_json(silent=True) or {}
        mensaje = (data.get('mensaje') or '').strip()
        if not mensaje:
            return build_cors_response({'success': False, 'error': 'El mensaje es obligatorio'}, 400)
        if not data.get('confirmar'):
            return build_cors_response({'success': False, 'error': 'Falta confirmar:true (revisa el preview primero)'}, 400)
        filtros = {'ciudad': data.get('ciudad'), 'plan': data.get('plan'), 'nivel_min': data.get('nivel_min')}
        titulo = (data.get('titulo') or '').strip()
        prioridad = data.get('prioridad', 'media')
        previstos = contar_destinatarios(_db.session, filtros)
        enviados = enviar_anuncio(_db.session, filtros, titulo, mensaje, prioridad)
        registrar_auditoria('enviar', 'anuncio_masivo', None, {
            'filtros': filtros, 'titulo': titulo, 'prioridad': prioridad,
            'destinatarios': enviados or previstos,
        })
        return build_cors_response({'success': True, 'enviados': enviados or previstos,
                                    'message': f'Anuncio enviado a {enviados or previstos} usuario(s)'})
    except Exception as e:
        logger.error(f"Error en enviar_anuncio_masivo: {e}")
        try:
            _db.session.rollback()
        except Exception:
            pass
        return build_cors_response({'success': False, 'error': str(e)}, 500)


# ═══════════════════════════════════════════════════════════════════════════════
# MODO SOPORTE / "VER COMO EL USUARIO" (Admin Panel A35)
# Snapshot de SOLO LECTURA + diagnóstico automático. NO suplanta la sesión del
# usuario (eso sería inseguro). Acceso auditado.
# ═══════════════════════════════════════════════════════════════════════════════
@admin_bp.route('/soporte/negocio/<int:negocio_id>', methods=['GET'])
@requiere_permiso('negocios')
def soporte_negocio(negocio_id):
    """GET /api/admin/soporte/negocio/<id> → snapshot read-only + diagnóstico + accesos rápidos."""
    from src.models.database import db as _db
    try:
        conn = get_db_connection(); cur = conn.cursor()
        cur.execute("""
            SELECT id_negocio, nombre_negocio, slug, ciudad, logo_url, activo, verificado,
                   perfil_publico, tiene_pagina, plan_key, COALESCE(eliminado, FALSE) AS eliminado,
                   usuario_id
            FROM negocios WHERE id_negocio = %s
        """, (negocio_id,))
        n = cur.fetchone()
        if not n:
            cur.close(); conn.close()
            return build_cors_response({'success': False, 'error': 'Negocio no encontrado'}, 404)
        n = dict(n)

        dueno = None
        if n.get('usuario_id'):
            cur.execute("SELECT id_usuario, nombre, correo FROM usuarios WHERE id_usuario = %s", (n['usuario_id'],))
            u = cur.fetchone()
            if u:
                dueno = {'usuario_id': u['id_usuario'], 'nombre': u['nombre'], 'correo': u['correo']}

        # Últimos pedidos y productos (solo lectura)
        cur.execute("""
            SELECT id_pedido, estado, total, fecha_pedido FROM pedidos
            WHERE negocio_id = %s ORDER BY fecha_pedido DESC NULLS LAST LIMIT 5
        """, (negocio_id,))
        ult_pedidos = [{'id': r['id_pedido'], 'estado': r['estado'],
                        'total': float(r['total'] or 0),
                        'fecha': r['fecha_pedido'].isoformat() if r['fecha_pedido'] else None}
                       for r in cur.fetchall()]
        cur.execute("""
            SELECT nombre, precio, stock, activo FROM productos_catalogo
            WHERE negocio_id = %s ORDER BY id_producto DESC LIMIT 5
        """, (negocio_id,))
        ult_productos = [{'nombre': r['nombre'], 'precio': float(r['precio'] or 0),
                          'stock': r['stock'], 'activo': r['activo']} for r in cur.fetchall()]
        cur.close(); conn.close()

        # Suscripción (tolerante)
        suscripcion = None
        try:
            from src.models.colombia_data.suscripcion_negocio import SuscripcionNegocio
            sus = SuscripcionNegocio.query.filter_by(negocio_id=negocio_id).first()
            if sus:
                suscripcion = {'estado': sus.estado, 'es_trial': sus.es_trial}
        except Exception:
            pass

        productos = int(_scalar_admin("SELECT COUNT(*) AS v FROM productos_catalogo WHERE negocio_id = %s", (negocio_id,)))
        pedidos = int(_scalar_admin("SELECT COUNT(*) AS v FROM pedidos WHERE negocio_id = %s", (negocio_id,)))
        videos = int(_scalar_admin("SELECT COUNT(*) AS v FROM negocio_videos WHERE negocio_id = %s", (negocio_id,)))

        negocio = {
            'id': n['id_negocio'], 'nombre': n['nombre_negocio'], 'slug': n.get('slug'),
            'ciudad': n.get('ciudad'), 'logo_url': n.get('logo_url'), 'activo': n.get('activo'),
            'verificado': n.get('verificado'), 'perfil_publico': n.get('perfil_publico'),
            'tiene_pagina': n.get('tiene_pagina'), 'plan_key': n.get('plan_key') or 'basic',
            'eliminado': n.get('eliminado'),
        }
        snapshot = {'negocio': negocio, 'suscripcion': suscripcion,
                    'productos': productos, 'pedidos': pedidos, 'videos': videos}

        from src.api.utils.soporte_service import diagnosticar_negocio
        diagnostico = diagnosticar_negocio(snapshot)

        # Acceso a soporte = ver datos del usuario → auditado.
        registrar_auditoria('soporte', 'soporte_negocio', negocio_id,
                            {'dueno': (dueno or {}).get('correo')})

        tienda_url = f"https://tukomercio.co/tienda/{negocio['slug']}" if negocio.get('slug') else None
        return build_cors_response({
            'success': True, 'negocio': negocio, 'dueno': dueno, 'suscripcion': suscripcion,
            'productos': productos, 'pedidos': pedidos, 'videos': videos,
            'ultimos_pedidos': ult_pedidos, 'ultimos_productos': ult_productos,
            'diagnostico': diagnostico, 'tienda_url': tienda_url,
        })
    except Exception as e:
        logger.error(f"Error en soporte_negocio: {e}")
        return build_cors_response({'success': False, 'error': str(e)}, 200)


# ═══════════════════════════════════════════════════════════════════════════════
# CENTRO DE REPORTES EXPORTABLES (Admin Panel A36)
# Resumen analítico de plataforma + exportación CSV. Arranca Fase 5.
# ═══════════════════════════════════════════════════════════════════════════════
@admin_bp.route('/reportes/resumen', methods=['GET'])
@requiere_permiso('reportes')
def reportes_resumen():
    """GET /api/admin/reportes/resumen → métricas agregadas de plataforma."""
    from sqlalchemy import text as _t
    from src.models.database import db as _db
    try:
        def _scalar(sql, params=None):
            try:
                return int(_db.session.execute(_t(sql), params or {}).scalar() or 0)
            except Exception:
                return 0

        totales = {
            'negocios':          _scalar("SELECT COUNT(*) FROM negocios WHERE COALESCE(eliminado,FALSE)=FALSE"),
            'negocios_activos':  _scalar("SELECT COUNT(*) FROM negocios WHERE activo=TRUE AND COALESCE(eliminado,FALSE)=FALSE"),
            'con_pagina':        _scalar("SELECT COUNT(*) FROM negocios WHERE tiene_pagina=TRUE AND COALESCE(eliminado,FALSE)=FALSE"),
            'usuarios':          _scalar("SELECT COUNT(*) FROM usuarios WHERE COALESCE(eliminado,FALSE)=FALSE"),
            'usuarios_activos':  _scalar("SELECT COUNT(*) FROM usuarios WHERE active=TRUE AND COALESCE(eliminado,FALSE)=FALSE"),
            'productos':         _scalar("SELECT COUNT(*) FROM productos_catalogo"),
            'pedidos':           _scalar("SELECT COUNT(*) FROM pedidos"),
        }

        # Distribución por plan
        planes = []
        try:
            for r in _db.session.execute(_t(
                "SELECT COALESCE(plan_key,'basic') AS plan, COUNT(*) AS n "
                "FROM negocios WHERE COALESCE(eliminado,FALSE)=FALSE GROUP BY plan_key ORDER BY n DESC")).fetchall():
                planes.append({'plan': r[0], 'cantidad': int(r[1])})
        except Exception:
            pass

        # Economía de TuKoins
        tukoins = {
            'emitidos':       _scalar("SELECT COALESCE(SUM(cantidad),0) FROM tukoins_transacciones WHERE tipo='ganado'"),
            'gastados':       _scalar("SELECT COALESCE(SUM(cantidad),0) FROM tukoins_transacciones WHERE tipo='gastado'"),
            'en_circulacion': _scalar("SELECT COALESCE(SUM(tukoins),0) FROM negocio_gamificacion"),
            'transacciones':  _scalar("SELECT COUNT(*) FROM tukoins_transacciones"),
        }

        # Crecimiento últimos 6 meses (negocios y usuarios nuevos por mes)
        crecimiento = []
        try:
            rows = _db.session.execute(_t("""
                SELECT to_char(date_trunc('month', fecha_registro), 'YYYY-MM') AS mes, COUNT(*) AS n
                FROM negocios
                WHERE fecha_registro >= (CURRENT_DATE - INTERVAL '6 months')
                GROUP BY 1 ORDER BY 1
            """)).fetchall()
            neg_por_mes = {r[0]: int(r[1]) for r in rows}
            rows_u = _db.session.execute(_t("""
                SELECT to_char(date_trunc('month', created_at), 'YYYY-MM') AS mes, COUNT(*) AS n
                FROM usuarios
                WHERE created_at >= (CURRENT_DATE - INTERVAL '6 months')
                GROUP BY 1 ORDER BY 1
            """)).fetchall()
            usr_por_mes = {r[0]: int(r[1]) for r in rows_u}
            meses = sorted(set(neg_por_mes) | set(usr_por_mes))
            crecimiento = [{'mes': m, 'negocios_nuevos': neg_por_mes.get(m, 0),
                            'usuarios_nuevos': usr_por_mes.get(m, 0)} for m in meses]
        except Exception as _ce:
            logger.warning(f"[reportes] crecimiento no disponible: {_ce}")

        # Top ciudades
        top_ciudades = []
        try:
            for r in _db.session.execute(_t(
                "SELECT COALESCE(NULLIF(TRIM(ciudad),''),'(sin ciudad)') AS c, COUNT(*) AS n "
                "FROM negocios WHERE COALESCE(eliminado,FALSE)=FALSE GROUP BY c ORDER BY n DESC LIMIT 10")).fetchall():
                top_ciudades.append({'ciudad': r[0], 'negocios': int(r[1])})
        except Exception:
            pass

        return build_cors_response({'success': True, 'totales': totales, 'planes': planes,
                                    'tukoins': tukoins, 'crecimiento': crecimiento,
                                    'top_ciudades': top_ciudades})
    except Exception as e:
        logger.error(f"Error en reportes_resumen: {e}")
        return build_cors_response({'success': False, 'error': str(e)}, 200)


@admin_bp.route('/reportes/export', methods=['GET'])
@requiere_permiso('reportes')
def reportes_export():
    """GET /api/admin/reportes/export?tipo=negocios|usuarios|tukoins|crecimiento → {filename, csv}."""
    from sqlalchemy import text as _t
    from src.models.database import db as _db
    try:
        from src.api.utils.reportes_service import a_csv
        tipo = (request.args.get('tipo', 'negocios') or 'negocios').strip().lower()

        if tipo == 'negocios':
            headers = [('id', 'ID'), ('nombre', 'Negocio'), ('ciudad', 'Ciudad'), ('plan', 'Plan'),
                       ('activo', 'Activo'), ('correo', 'Correo dueño'), ('registro', 'Registro')]
            rows = []
            for r in _db.session.execute(_t("""
                SELECT n.id_negocio, n.nombre_negocio, n.ciudad, COALESCE(n.plan_key,'basic'),
                       n.activo, u.correo, n.fecha_registro
                FROM negocios n LEFT JOIN usuarios u ON u.id_usuario = n.usuario_id
                WHERE COALESCE(n.eliminado,FALSE)=FALSE
                ORDER BY n.fecha_registro DESC NULLS LAST LIMIT 5000
            """)).fetchall():
                rows.append({'id': r[0], 'nombre': r[1], 'ciudad': r[2], 'plan': r[3],
                             'activo': 'Sí' if r[4] else 'No', 'correo': r[5] or '',
                             'registro': r[6].strftime('%Y-%m-%d') if r[6] else ''})
        elif tipo == 'usuarios':
            headers = [('id', 'ID'), ('nombre', 'Nombre'), ('correo', 'Correo'),
                       ('activo', 'Activo'), ('registro', 'Registro')]
            rows = []
            for r in _db.session.execute(_t("""
                SELECT id_usuario, (nombre || ' ' || COALESCE(apellidos,'')), correo, active, created_at
                FROM usuarios WHERE COALESCE(eliminado,FALSE)=FALSE
                ORDER BY created_at DESC NULLS LAST LIMIT 5000
            """)).fetchall():
                rows.append({'id': r[0], 'nombre': (r[1] or '').strip(), 'correo': r[2],
                             'activo': 'Sí' if r[3] else 'No',
                             'registro': r[4].strftime('%Y-%m-%d') if r[4] else ''})
        elif tipo == 'tukoins':
            headers = [('fecha', 'Fecha'), ('negocio_id', 'Negocio'), ('tipo', 'Tipo'),
                       ('cantidad', 'Cantidad'), ('concepto', 'Concepto'), ('balance', 'Balance')]
            rows = []
            for r in _db.session.execute(_t("""
                SELECT fecha, negocio_id, tipo, cantidad, concepto, balance_tras
                FROM tukoins_transacciones ORDER BY fecha DESC NULLS LAST LIMIT 5000
            """)).fetchall():
                rows.append({'fecha': r[0].strftime('%Y-%m-%d %H:%M') if r[0] else '',
                             'negocio_id': r[1], 'tipo': r[2], 'cantidad': r[3],
                             'concepto': r[4], 'balance': r[5]})
        elif tipo == 'crecimiento':
            headers = [('mes', 'Mes'), ('negocios_nuevos', 'Negocios nuevos'), ('usuarios_nuevos', 'Usuarios nuevos')]
            neg = {r[0]: int(r[1]) for r in _db.session.execute(_t(
                "SELECT to_char(date_trunc('month', fecha_registro),'YYYY-MM'), COUNT(*) FROM negocios GROUP BY 1")).fetchall()}
            usr = {r[0]: int(r[1]) for r in _db.session.execute(_t(
                "SELECT to_char(date_trunc('month', created_at),'YYYY-MM'), COUNT(*) FROM usuarios GROUP BY 1")).fetchall()}
            rows = [{'mes': m, 'negocios_nuevos': neg.get(m, 0), 'usuarios_nuevos': usr.get(m, 0)}
                    for m in sorted(set(neg) | set(usr))]
        else:
            return build_cors_response({'success': False, 'error': 'Tipo de reporte inválido'}, 400)

        csv = a_csv(headers, rows)
        registrar_auditoria('export', 'reporte', None, {'tipo': tipo, 'filas': len(rows)})
        return build_cors_response({'success': True, 'tipo': tipo, 'filas': len(rows),
                                    'filename': f'reporte_{tipo}.csv', 'csv': csv})
    except Exception as e:
        logger.error(f"Error en reportes_export: {e}")
        return build_cors_response({'success': False, 'error': str(e)}, 500)


# ═══════════════════════════════════════════════════════════════════════════════
# SALUD DEL SISTEMA (Admin Panel A37)
# Health de BD/API + errores recientes (reportes) + métricas de uso.
# ═══════════════════════════════════════════════════════════════════════════════
@admin_bp.route('/salud', methods=['GET'])
@requiere_permiso('reportes')
def salud_sistema():
    """GET /api/admin/salud → estado general, health BD, errores recientes y uso."""
    from sqlalchemy import text as _t
    from src.models.database import db as _db
    import time as _time
    try:
        def _scalar(sql, params=None):
            try:
                return int(_db.session.execute(_t(sql), params or {}).scalar() or 0)
            except Exception:
                return 0

        # ── Health de la BD (latencia de un SELECT 1) ──
        db_ok = True
        db_ms = None
        try:
            _t0 = _time.time()
            _db.session.execute(_t("SELECT 1"))
            db_ms = round((_time.time() - _t0) * 1000, 1)
        except Exception as _dbe:
            db_ok = False
            logger.error(f"[salud] BD no responde: {_dbe}")

        # ── Errores / reportes (sistema de feedback, tipo bug) ──
        bugs = {
            'nuevos':      _scalar("SELECT COUNT(*) FROM feedback WHERE tipo_feedback='bug' AND estado='nuevo'"),
            'en_revision': _scalar("SELECT COUNT(*) FROM feedback WHERE tipo_feedback='bug' AND estado='en_revision'"),
            'resueltos':   _scalar("SELECT COUNT(*) FROM feedback WHERE tipo_feedback='bug' AND estado='resuelto'"),
        }
        recientes = []
        try:
            for r in _db.session.execute(_t("""
                SELECT id_feedback, descripcion, url_contexto, fecha_envio, estado, prioridad
                FROM feedback WHERE tipo_feedback='bug'
                ORDER BY fecha_envio DESC NULLS LAST LIMIT 10
            """)).fetchall():
                recientes.append({
                    'id': r[0], 'descripcion': (r[1] or '')[:160], 'url': r[2],
                    'fecha': r[3].isoformat() if r[3] else None,
                    'estado': r[4], 'prioridad': r[5],
                })
        except Exception:
            pass

        # ── Métricas de uso ──
        uso = {
            'pedidos_24h':        _scalar("SELECT COUNT(*) FROM pedidos WHERE fecha_pedido >= (NOW() - INTERVAL '24 hours')"),
            'pedidos_7d':         _scalar("SELECT COUNT(*) FROM pedidos WHERE fecha_pedido >= (NOW() - INTERVAL '7 days')"),
            'negocios_nuevos_7d': _scalar("SELECT COUNT(*) FROM negocios WHERE fecha_registro >= (NOW() - INTERVAL '7 days')"),
            'usuarios_nuevos_7d': _scalar("SELECT COUNT(*) FROM usuarios WHERE created_at >= (NOW() - INTERVAL '7 days')"),
            'usuarios_activos_7d':_scalar("SELECT COUNT(*) FROM usuarios WHERE last_login >= (NOW() - INTERVAL '7 days')"),
            'productos_7d':       _scalar("SELECT COUNT(*) FROM productos_catalogo WHERE fecha_creacion >= (NOW() - INTERVAL '7 days')"),
        }
        acciones_admin_24h = _scalar("SELECT COUNT(*) FROM admin_audit_log WHERE created_at >= (NOW() - INTERVAL '24 hours')")

        from src.api.utils.salud_service import evaluar_salud
        estado = evaluar_salud({'db_ok': db_ok, 'bugs_nuevos': bugs['nuevos']})

        return build_cors_response({
            'success': True, 'estado': estado,
            'db': {'ok': db_ok, 'latencia_ms': db_ms},
            'bugs': bugs, 'errores_recientes': recientes,
            'uso': uso, 'acciones_admin_24h': acciones_admin_24h,
        })
    except Exception as e:
        logger.error(f"Error en salud_sistema: {e}")
        return build_cors_response({'success': False, 'error': str(e)}, 200)


# ═══════════════════════════════════════════════════════════════════════════════
# CONFIGURACIÓN GLOBAL DE LA PLATAFORMA (Admin Panel A38)
# Mantenimiento, registro abierto/cerrado, textos legales/landing.
# ═══════════════════════════════════════════════════════════════════════════════
@admin_bp.route('/config-global', methods=['GET'])
@requiere_permiso('configuracion')
def get_config_global_admin():
    """GET /api/admin/config-global → configuración global efectiva + defaults."""
    try:
        from src.models.colombia_data.config_plataforma import get_config_global, CONFIG_GLOBAL_DEFAULT
        return build_cors_response({'success': True, 'config': get_config_global(),
                                    'default': CONFIG_GLOBAL_DEFAULT})
    except Exception as e:
        logger.error(f"Error en get_config_global_admin: {e}")
        return build_cors_response({'success': False, 'error': str(e)}, 200)


@admin_bp.route('/config-global', methods=['PUT'])
@superadmin_required
def update_config_global_admin():
    """PUT /api/admin/config-global → actualiza toggles/textos globales. Solo superadmin (mantenimiento es crítico)."""
    try:
        from src.models.colombia_data.config_plataforma import (
            validar_config_global, set_config_global, get_config_global
        )
        antes = get_config_global()
        ok, limpio, error = validar_config_global(request.get_json(silent=True) or {})
        if not ok:
            return build_cors_response({'success': False, 'error': error}, 400)
        nueva = set_config_global(limpio)
        # En el detalle de auditoría no metemos los textos largos completos.
        registrar_auditoria('editar', 'config_global', None,
                            {'cambios': {k: (v if not isinstance(v, str) or len(v) <= 80 else v[:80] + '…')
                                         for k, v in limpio.items()}})
        return build_cors_response({'success': True, 'config': nueva, 'message': 'Configuración global actualizada'})
    except Exception as e:
        logger.error(f"Error en update_config_global_admin: {e}")
        try:
            from src.models.database import db as _db
            _db.session.rollback()
        except Exception:
            pass
        return build_cors_response({'success': False, 'error': str(e)}, 500)


# ═══════════════════════════════════════════════════════════════════════════════
# CENTRO DE PAGOS — WOMPI (Admin Panel A41) · arranca Fase 6
# Estado de la integración Wompi por negocio + salud del webhook + métricas de cobro.
# NUNCA expone las claves secretas (solo presencia / máscara del public_key).
# ═══════════════════════════════════════════════════════════════════════════════
@admin_bp.route('/pagos/wompi', methods=['GET'])
@requiere_permiso('pagos')
def admin_pagos_wompi():
    """GET /api/admin/pagos/wompi → resumen + negocios con Wompi configurado + métricas de pago."""
    from sqlalchemy import text as _t
    from src.models.database import db as _db
    try:
        from src.api.utils.pagos_service import evaluar_config_wompi
        rows = _db.session.execute(_t("""
            SELECT w.negocio_id, n.nombre_negocio, w.public_key, w.integrity_key, w.events_key,
                   w.ambiente, w.activo
            FROM wompi_configs w
            LEFT JOIN negocios n ON n.id_negocio = w.negocio_id
            ORDER BY w.updated_at DESC NULLS LAST
        """)).fetchall()
        negocios = []
        resumen = {'total': 0, 'activos': 0, 'en_prod': 0, 'webhook_roto': 0, 'incompletos': 0}
        for r in rows:
            ev = evaluar_config_wompi({'public_key': r[2], 'integrity_key': r[3], 'events_key': r[4],
                                       'ambiente': r[5], 'activo': r[6]})
            resumen['total'] += 1
            if ev['activo']:
                resumen['activos'] += 1
            if ev['prod']:
                resumen['en_prod'] += 1
            if ev['activo'] and not ev['webhook_ok']:
                resumen['webhook_roto'] += 1     # activo pero el webhook rechazará cobros
            if ev['estado'] == 'incompleto':
                resumen['incompletos'] += 1
            negocios.append({
                'negocio_id': r[0], 'nombre': r[1] or f'#{r[0]}',
                'estado': ev['estado'], 'activo': ev['activo'], 'ambiente': ev['ambiente'],
                'webhook_ok': ev['webhook_ok'], 'faltantes': ev['faltantes'],
            })

        # Métricas de cobro Wompi (pedidos pagados por la pasarela)
        def _scalar(sql):
            try:
                return int(_db.session.execute(_t(sql)).scalar() or 0)
            except Exception:
                return 0
        pagos = {
            'aprobados':  _scalar("SELECT COUNT(*) FROM pedidos WHERE estado_pago='aprobado'"),
            'pendientes': _scalar("SELECT COUNT(*) FROM pedidos WHERE estado_pago='pendiente'"),
            'rechazados': _scalar("SELECT COUNT(*) FROM pedidos WHERE estado_pago IN ('rechazado','declined','error')"),
        }
        try:
            pagos['monto_aprobado'] = float(_db.session.execute(_t(
                "SELECT COALESCE(SUM(total),0) FROM pedidos WHERE estado_pago='aprobado'")).scalar() or 0)
        except Exception:
            pagos['monto_aprobado'] = 0

        return build_cors_response({'success': True, 'resumen': resumen, 'negocios': negocios, 'pagos': pagos})
    except Exception as e:
        logger.error(f"Error en admin_pagos_wompi: {e}")
        return build_cors_response({'success': False, 'error': str(e), 'negocios': []}, 200)


@admin_bp.route('/pagos/wompi/<int:negocio_id>', methods=['GET'])
@requiere_permiso('pagos')
def admin_pagos_wompi_detalle(negocio_id):
    """GET /api/admin/pagos/wompi/<id> → detalle de config (enmascarada) + últimas transacciones."""
    from sqlalchemy import text as _t
    from src.models.database import db as _db
    try:
        from src.api.utils.pagos_service import evaluar_config_wompi, mascara_clave
        r = _db.session.execute(_t("""
            SELECT public_key, integrity_key, events_key, ambiente, activo, updated_at
            FROM wompi_configs WHERE negocio_id = :nid
        """), {'nid': negocio_id}).fetchone()
        if not r:
            return build_cors_response({'success': False, 'error': 'Este negocio no tiene Wompi configurado'}, 404)
        ev = evaluar_config_wompi({'public_key': r[0], 'integrity_key': r[1], 'events_key': r[2],
                                   'ambiente': r[3], 'activo': r[4]})
        config = {
            **ev,
            'public_key_mask': mascara_clave(r[0]),
            'tiene_integrity_key': bool(r[1]),
            'tiene_events_key': bool(r[2]),
            'updated_at': r[5].isoformat() if r[5] else None,
        }
        tx = []
        for p in _db.session.execute(_t("""
            SELECT codigo_pedido, total, estado_pago, metodo_pago, referencia_pago, fecha_pedido
            FROM pedidos WHERE negocio_id = :nid AND (metodo_pago ILIKE '%wompi%' OR referencia_pago IS NOT NULL)
            ORDER BY fecha_pedido DESC NULLS LAST LIMIT 15
        """), {'nid': negocio_id}).fetchall():
            tx.append({'codigo': p[0], 'total': float(p[1] or 0), 'estado_pago': p[2],
                       'metodo': p[3], 'referencia': p[4],
                       'fecha': p[5].isoformat() if p[5] else None})
        return build_cors_response({'success': True, 'negocio_id': negocio_id,
                                    'config': config, 'transacciones': tx})
    except Exception as e:
        logger.error(f"Error en admin_pagos_wompi_detalle: {e}")
        return build_cors_response({'success': False, 'error': str(e)}, 200)


# ═══════════════════════════════════════════════════════════════════════════════
# FACTURACIÓN Y COBRO DE SUSCRIPCIONES (Admin Panel A42)
# Cómo pagan los tenderos su plan a TuKomercio: estado, vencimientos, dunning, MRR.
# ═══════════════════════════════════════════════════════════════════════════════
@admin_bp.route('/facturacion/resumen', methods=['GET'])
@requiere_permiso('pagos')
def facturacion_resumen():
    """GET /api/admin/facturacion/resumen → conteos por estado, MRR estimado, cobros y dunning."""
    from sqlalchemy import text as _t
    from src.models.database import db as _db
    try:
        from src.models.colombia_data.suscripcion_negocio import SuscripcionNegocio
        from src.api.utils.pagos_service import clasificar_cobro

        # Precios de plan por id (para MRR)
        precios = {}
        try:
            for r in _db.session.execute(_t("SELECT id, nombre, COALESCE(precio_mensual,0) FROM planes")).fetchall():
                precios[r[0]] = {'nombre': r[1], 'precio': float(r[2] or 0)}
        except Exception:
            pass

        subs = SuscripcionNegocio.query.all()
        conteo = {'trial': 0, 'activa': 0, 'gracia': 0, 'vencida': 0, 'cancelada': 0, 'pausada': 0}
        mrr = 0.0
        requieren = []
        for s in subs:
            est = s.estado_actual
            conteo[est] = conteo.get(est, 0) + 1
            if est == 'activa':
                mrr += (precios.get(s.plan_id, {}).get('precio', 0) or 0)
            cl = clasificar_cobro(est, s.dias_restantes)
            if cl['requiere_accion']:
                requieren.append({
                    'negocio_id': s.negocio_id, 'estado': est,
                    'dias_restantes': s.dias_restantes,
                    'plan': precios.get(s.plan_id, {}).get('nombre', '—'),
                    'fecha_vencimiento': s.fecha_vencimiento.isoformat() if s.fecha_vencimiento else None,
                    'bucket': cl['bucket'], 'accion': cl['accion'], 'color': cl['color'],
                })

        # Nombres de los negocios que requieren acción
        if requieren:
            ids = [r['negocio_id'] for r in requieren]
            nombres = {}
            for r in _db.session.execute(_t(
                "SELECT id_negocio, nombre_negocio FROM negocios WHERE id_negocio = ANY(:ids)"),
                {'ids': ids}).fetchall():
                nombres[r[0]] = r[1]
            for r in requieren:
                r['nombre'] = nombres.get(r['negocio_id'], f"#{r['negocio_id']}")
        # Vencidas primero, luego en gracia, luego por vencer
        orden = {'vencida': 0, 'en_gracia': 1, 'por_vencer': 2}
        requieren.sort(key=lambda x: (orden.get(x['bucket'], 9), x['dias_restantes'] if x['dias_restantes'] is not None else 999))

        def _scalar(sql):
            try:
                return _db.session.execute(_t(sql)).scalar() or 0
            except Exception:
                return 0
        cobros = {
            'total_pagos': int(_scalar("SELECT COUNT(*) FROM pagos_suscripcion WHERE estado='completado'")),
            'monto_total': float(_scalar("SELECT COALESCE(SUM(monto),0) FROM pagos_suscripcion WHERE estado='completado'")),
            'monto_30d':   float(_scalar("SELECT COALESCE(SUM(monto),0) FROM pagos_suscripcion WHERE estado='completado' AND created_at >= (NOW() - INTERVAL '30 days')")),
        }

        return build_cors_response({
            'success': True, 'conteo': conteo, 'mrr_estimado': round(mrr, 2),
            'cobros': cobros, 'requieren_accion': requieren[:100],
            'total_requieren': len(requieren),
        })
    except Exception as e:
        logger.error(f"Error en facturacion_resumen: {e}")
        return build_cors_response({'success': False, 'error': str(e), 'requieren_accion': []}, 200)


# ═══════════════════════════════════════════════════════════════════════════════
# MODERACIÓN GLOBAL DE RESEÑAS (Admin Panel A43)
# Vista de todas las reseñas + ocultar/aprobar + banear reseñadores por email.
# ═══════════════════════════════════════════════════════════════════════════════
@admin_bp.route('/resenas', methods=['GET'])
@requiere_permiso('negocios')
def admin_resenas():
    """GET /api/admin/resenas?estado=&rating=&buscar=&limit= → reseñas de toda la plataforma."""
    from sqlalchemy import text as _t
    from src.models.database import db as _db
    try:
        from src.api.utils.resenas_service import evaluar_resena_sospechosa, normalizar_email
        estado = (request.args.get('estado', '') or '').strip().lower()
        buscar = (request.args.get('buscar', '') or '').strip()
        rating = request.args.get('rating')
        limit = min(int(request.args.get('limit', 50) or 50), 200)

        cond = []
        params = {'lim': limit}
        if estado == 'aprobadas':
            cond.append("r.aprobado IS TRUE")
        elif estado == 'pendientes':
            cond.append("(r.aprobado IS FALSE OR r.aprobado IS NULL)")
        if rating and rating.isdigit():
            cond.append("r.rating = :rating"); params['rating'] = int(rating)
        if buscar:
            cond.append("(r.comentario ILIKE :q OR r.cliente_nombre ILIKE :q OR r.cliente_email ILIKE :q)")
            params['q'] = f"%{buscar}%"
        where = ("WHERE " + " AND ".join(cond)) if cond else ""

        rows = _db.session.execute(_t(f"""
            SELECT r.id, r.negocio_id, n.nombre_negocio, r.producto_id, pc.nombre,
                   r.cliente_nombre, r.cliente_email, r.rating, r.titulo, r.comentario,
                   r.verificado, r.aprobado, r.fecha
            FROM producto_reviews r
            LEFT JOIN negocios n ON n.id_negocio = r.negocio_id
            LEFT JOIN productos_catalogo pc ON pc.id_producto = r.producto_id
            {where}
            ORDER BY r.fecha DESC NULLS LAST LIMIT :lim
        """), params).fetchall()

        # baneos actuales
        baneados = set()
        try:
            for b in _db.session.execute(_t("SELECT email FROM resena_baneos")).fetchall():
                baneados.add(normalizar_email(b[0]))
        except Exception:
            pass

        resenas = []
        for r in rows:
            ev = evaluar_resena_sospechosa({'rating': r[7], 'comentario': r[9], 'titulo': r[8], 'verificado': r[10]})
            resenas.append({
                'id': r[0], 'negocio_id': r[1], 'negocio': r[2] or f'#{r[1]}',
                'producto': r[4] or f'#{r[3]}', 'cliente': r[5] or '', 'email': r[6] or '',
                'rating': r[7], 'titulo': r[8], 'comentario': r[9],
                'verificado': r[10], 'aprobado': r[11],
                'fecha': r[12].isoformat() if r[12] else None,
                'sospechosa': ev['sospechosa'], 'motivos': ev['motivos'],
                'baneado': normalizar_email(r[6]) in baneados,
            })
        return build_cors_response({'success': True, 'resenas': resenas})
    except Exception as e:
        logger.error(f"Error en admin_resenas: {e}")
        return build_cors_response({'success': False, 'error': str(e), 'resenas': []}, 200)


@admin_bp.route('/resenas/<int:resena_id>/moderar', methods=['POST'])
@requiere_permiso('negocios')
def moderar_resena_admin(resena_id):
    """POST /api/admin/resenas/<id>/moderar  body: { accion: 'aprobar'|'ocultar' }"""
    from sqlalchemy import text as _t
    from src.models.database import db as _db
    try:
        accion = ((request.get_json(silent=True) or {}).get('accion') or '').strip().lower()
        if accion not in ('aprobar', 'ocultar'):
            return build_cors_response({'success': False, 'error': "accion debe ser 'aprobar' u 'ocultar'"}, 400)
        existe = _db.session.execute(_t("SELECT 1 FROM producto_reviews WHERE id = :id"), {'id': resena_id}).fetchone()
        if not existe:
            return build_cors_response({'success': False, 'error': 'Reseña no encontrada'}, 404)
        _db.session.execute(_t("UPDATE producto_reviews SET aprobado = :ap WHERE id = :id"),
                            {'ap': accion == 'aprobar', 'id': resena_id})
        _db.session.commit()
        registrar_auditoria('editar', 'resena', resena_id, {'accion': accion})
        return build_cors_response({'success': True, 'message': f'Reseña {accion}da'})
    except Exception as e:
        logger.error(f"Error en moderar_resena_admin: {e}")
        try:
            _db.session.rollback()
        except Exception:
            pass
        return build_cors_response({'success': False, 'error': str(e)}, 500)


@admin_bp.route('/resenas/baneos', methods=['GET'])
@requiere_permiso('negocios')
def listar_baneos_resenas():
    """GET /api/admin/resenas/baneos → emails baneados."""
    from sqlalchemy import text as _t
    from src.models.database import db as _db
    try:
        rows = _db.session.execute(_t(
            "SELECT email, motivo, created_by, created_at FROM resena_baneos ORDER BY created_at DESC LIMIT 200")).fetchall()
        return build_cors_response({'success': True, 'baneos': [{
            'email': r[0], 'motivo': r[1], 'created_by': r[2],
            'created_at': r[3].isoformat() if r[3] else None} for r in rows]})
    except Exception as e:
        logger.error(f"Error en listar_baneos_resenas: {e}")
        return build_cors_response({'success': False, 'error': str(e), 'baneos': []}, 200)


@admin_bp.route('/resenas/banear', methods=['POST'])
@requiere_permiso('negocios')
def banear_resenador():
    """POST /api/admin/resenas/banear  body: { email, motivo? } → veta a un reseñador + oculta sus reseñas."""
    from sqlalchemy import text as _t
    from src.models.database import db as _db
    try:
        from src.api.utils.resenas_service import normalizar_email
        data = request.get_json(silent=True) or {}
        email = normalizar_email(data.get('email'))
        if not email or '@' not in email:
            return build_cors_response({'success': False, 'error': 'Email inválido'}, 400)
        _db.session.execute(_t("""
            INSERT INTO resena_baneos (email, motivo, created_by)
            VALUES (:e, :m, :by) ON CONFLICT (email) DO UPDATE SET motivo = EXCLUDED.motivo
        """), {'e': email, 'm': (data.get('motivo') or '')[:255], 'by': getattr(g, 'user_email', None) or 'admin'})
        # Ocultar todas sus reseñas existentes
        ocultadas = _db.session.execute(_t(
            "UPDATE producto_reviews SET aprobado = FALSE WHERE LOWER(cliente_email) = :e"), {'e': email}).rowcount
        _db.session.commit()
        registrar_auditoria('excluir', 'resena_baneo', None, {'email': email, 'resenas_ocultadas': ocultadas})
        return build_cors_response({'success': True, 'message': f'{email} baneado; {ocultadas or 0} reseña(s) ocultada(s)'})
    except Exception as e:
        logger.error(f"Error en banear_resenador: {e}")
        try:
            _db.session.rollback()
        except Exception:
            pass
        return build_cors_response({'success': False, 'error': str(e)}, 500)


@admin_bp.route('/resenas/banear', methods=['DELETE'])
@requiere_permiso('negocios')
def desbanear_resenador():
    """DELETE /api/admin/resenas/banear  body: { email } → quita el baneo."""
    from sqlalchemy import text as _t
    from src.models.database import db as _db
    try:
        from src.api.utils.resenas_service import normalizar_email
        email = normalizar_email((request.get_json(silent=True) or {}).get('email'))
        _db.session.execute(_t("DELETE FROM resena_baneos WHERE email = :e"), {'e': email})
        _db.session.commit()
        registrar_auditoria('readmitir', 'resena_baneo', None, {'email': email})
        return build_cors_response({'success': True, 'message': f'{email} desbaneado'})
    except Exception as e:
        logger.error(f"Error en desbanear_resenador: {e}")
        return build_cors_response({'success': False, 'error': str(e)}, 500)


# ═══════════════════════════════════════════════════════════════════════════════
# ADMINISTRACIÓN DE DORA IA (Admin Panel A44)
# Toggle global, modelo/tokens, límites por plan y monitoreo de consumo.
# ═══════════════════════════════════════════════════════════════════════════════
@admin_bp.route('/ia', methods=['GET'])
@requiere_permiso('configuracion')
def admin_ia():
    """GET /api/admin/ia → config de IA + consumo (hoy/30d) + top consumidores."""
    from sqlalchemy import text as _t
    from src.models.database import db as _db
    try:
        from src.models.colombia_data.config_plataforma import get_ia_config, IA_CONFIG_DEFAULT
        cfg = get_ia_config()

        def _scalar(sql):
            try:
                return int(_db.session.execute(_t(sql)).scalar() or 0)
            except Exception:
                return 0
        consumo = {
            'usos_hoy':  _scalar("SELECT COALESCE(SUM(usos),0) FROM ia_uso WHERE fecha = CURRENT_DATE"),
            'usos_30d':  _scalar("SELECT COALESCE(SUM(usos),0) FROM ia_uso WHERE fecha >= (CURRENT_DATE - 30)"),
            'negocios_hoy': _scalar("SELECT COUNT(DISTINCT negocio_id) FROM ia_uso WHERE fecha = CURRENT_DATE"),
        }
        top = []
        try:
            for r in _db.session.execute(_t("""
                SELECT u.negocio_id, n.nombre_negocio, SUM(u.usos) AS total
                FROM ia_uso u LEFT JOIN negocios n ON n.id_negocio = u.negocio_id
                WHERE u.fecha >= (CURRENT_DATE - 30)
                GROUP BY u.negocio_id, n.nombre_negocio
                ORDER BY total DESC LIMIT 10
            """)).fetchall():
                top.append({'negocio_id': r[0], 'nombre': r[1] or f'#{r[0]}', 'usos_30d': int(r[2] or 0)})
        except Exception:
            pass

        return build_cors_response({'success': True, 'config': cfg, 'default': IA_CONFIG_DEFAULT,
                                    'consumo': consumo, 'top_consumidores': top})
    except Exception as e:
        logger.error(f"Error en admin_ia: {e}")
        return build_cors_response({'success': False, 'error': str(e)}, 200)


@admin_bp.route('/ia/config', methods=['PUT'])
@superadmin_required
def update_ia_config():
    """PUT /api/admin/ia/config → toggle, modelo, max_tokens, límites por plan. Solo superadmin (afecta costos)."""
    try:
        from src.models.colombia_data.config_plataforma import (
            validar_ia_config, set_ia_config, get_ia_config
        )
        antes = get_ia_config()
        ok, limpio, error = validar_ia_config(request.get_json(silent=True) or {})
        if not ok:
            return build_cors_response({'success': False, 'error': error}, 400)
        nueva = set_ia_config(limpio)
        registrar_auditoria('editar', 'ia_config', None, {'antes': antes, 'despues': limpio})
        return build_cors_response({'success': True, 'config': nueva, 'message': 'Configuración de IA actualizada'})
    except Exception as e:
        logger.error(f"Error en update_ia_config: {e}")
        try:
            from src.models.database import db as _db
            _db.session.rollback()
        except Exception:
            pass
        return build_cors_response({'success': False, 'error': str(e)}, 500)


# ═══════════════════════════════════════════════════════════════════════════════
# HABEAS DATA / PRIVACIDAD (Admin Panel A45) — Ley 1581 (Colombia)
# Portabilidad (export), derecho al olvido (eliminación trazable), consentimientos.
# ═══════════════════════════════════════════════════════════════════════════════
@admin_bp.route('/privacidad/usuario/<int:user_id>/export', methods=['GET'])
@requiere_permiso('usuarios')
def privacidad_export(user_id):
    """GET /api/admin/privacidad/usuario/<id>/export → paquete de portabilidad (JSON, sin secretos)."""
    from sqlalchemy import text as _t
    from src.models.database import db as _db
    try:
        from src.api.utils.privacidad_service import construir_export_usuario
        conn = get_db_connection(); cur = conn.cursor()
        cur.execute("""
            SELECT id_usuario, nombre, apellidos, correo, profesion, cedula, celular,
                   foto_url, active, created_at, last_login, acepto_terminos, fecha_aceptacion_terminos
            FROM usuarios WHERE id_usuario = %s
        """, (user_id,))
        u = cur.fetchone()
        if not u:
            cur.close(); conn.close()
            return build_cors_response({'success': False, 'error': 'Usuario no encontrado'}, 404)
        usuario = dict(u)
        # serializar fechas
        for k in ('created_at', 'last_login', 'fecha_aceptacion_terminos'):
            if usuario.get(k):
                usuario[k] = usuario[k].isoformat()
        correo = usuario.get('correo')

        cur.execute("""
            SELECT id_negocio, nombre_negocio, slug, ciudad, categoria, plan_key, fecha_registro
            FROM negocios WHERE usuario_id = %s
        """, (user_id,))
        negocios = []
        for n in cur.fetchall():
            nd = dict(n)
            if nd.get('fecha_registro'):
                nd['fecha_registro'] = nd['fecha_registro'].isoformat()
            negocios.append(nd)

        resenas = []
        if correo:
            cur.execute("""
                SELECT producto_id, negocio_id, rating, titulo, comentario, fecha
                FROM producto_reviews WHERE LOWER(cliente_email) = LOWER(%s) LIMIT 500
            """, (correo,))
            for r in cur.fetchall():
                rd = dict(r)
                if rd.get('fecha'):
                    rd['fecha'] = rd['fecha'].isoformat()
                resenas.append(rd)
        cur.close(); conn.close()

        export = construir_export_usuario(usuario, negocios=negocios, resenas=resenas,
                                          generado_en=datetime.utcnow().isoformat())
        registrar_auditoria('export', 'privacidad', user_id, {'correo': correo, 'tipo': 'habeas_data'})
        return build_cors_response({'success': True, 'filename': f'datos_usuario_{user_id}.json', 'export': export})
    except Exception as e:
        logger.error(f"Error en privacidad_export: {e}")
        return build_cors_response({'success': False, 'error': str(e)}, 200)


@admin_bp.route('/privacidad/solicitudes', methods=['GET'])
@requiere_permiso('usuarios')
def privacidad_solicitudes():
    """GET /api/admin/privacidad/solicitudes?estado= → lista de solicitudes de privacidad."""
    from sqlalchemy import text as _t
    from src.models.database import db as _db
    try:
        estado = (request.args.get('estado', '') or '').strip().lower()
        sql = """
            SELECT s.id, s.usuario_id, u.nombre, u.correo, s.tipo, s.estado, s.nota,
                   s.atendida_por, s.fecha_solicitud, s.fecha_atencion
            FROM solicitudes_privacidad s
            LEFT JOIN usuarios u ON u.id_usuario = s.usuario_id
        """
        params = {}
        if estado in ('pendiente', 'completada', 'rechazada'):
            sql += " WHERE s.estado = :e"; params['e'] = estado
        sql += " ORDER BY s.fecha_solicitud DESC NULLS LAST LIMIT 200"
        rows = _db.session.execute(_t(sql), params).fetchall()
        return build_cors_response({'success': True, 'solicitudes': [{
            'id': r[0], 'usuario_id': r[1], 'nombre': r[2] or f'#{r[1]}', 'correo': r[3] or '',
            'tipo': r[4], 'estado': r[5], 'nota': r[6], 'atendida_por': r[7],
            'fecha_solicitud': r[8].isoformat() if r[8] else None,
            'fecha_atencion': r[9].isoformat() if r[9] else None,
        } for r in rows]})
    except Exception as e:
        logger.error(f"Error en privacidad_solicitudes: {e}")
        return build_cors_response({'success': False, 'error': str(e), 'solicitudes': []}, 200)


@admin_bp.route('/privacidad/solicitudes', methods=['POST'])
@requiere_permiso('usuarios')
def privacidad_crear_solicitud():
    """POST /api/admin/privacidad/solicitudes  body: { usuario_id, tipo, nota? } → registra una solicitud."""
    from sqlalchemy import text as _t
    from src.models.database import db as _db
    try:
        from src.api.utils.privacidad_service import validar_tipo_solicitud
        data = request.get_json(silent=True) or {}
        try:
            uid = int(data.get('usuario_id'))
        except (TypeError, ValueError):
            return build_cors_response({'success': False, 'error': 'usuario_id inválido'}, 400)
        tipo = (data.get('tipo') or '').strip().lower()
        if not validar_tipo_solicitud(tipo):
            return build_cors_response({'success': False, 'error': "tipo debe ser 'export' o 'eliminacion'"}, 400)
        if not _db.session.execute(_t("SELECT 1 FROM usuarios WHERE id_usuario=:u"), {'u': uid}).fetchone():
            return build_cors_response({'success': False, 'error': 'Usuario no encontrado'}, 404)
        _db.session.execute(_t("""
            INSERT INTO solicitudes_privacidad (usuario_id, tipo, nota) VALUES (:u, :t, :n)
        """), {'u': uid, 't': tipo, 'n': (data.get('nota') or '')[:500]})
        _db.session.commit()
        registrar_auditoria('crear', 'solicitud_privacidad', uid, {'tipo': tipo})
        return build_cors_response({'success': True, 'message': 'Solicitud registrada'})
    except Exception as e:
        logger.error(f"Error en privacidad_crear_solicitud: {e}")
        try:
            _db.session.rollback()
        except Exception:
            pass
        return build_cors_response({'success': False, 'error': str(e)}, 500)


@admin_bp.route('/privacidad/solicitudes/<int:solicitud_id>/procesar', methods=['POST'])
@superadmin_required
def privacidad_procesar_solicitud(solicitud_id):
    """
    POST /api/admin/privacidad/solicitudes/<id>/procesar  body: { accion: 'completar'|'rechazar', nota? }
    Para 'eliminacion' + 'completar' → baja lógica del usuario (papelera). Solo superadmin. Trazable.
    """
    from sqlalchemy import text as _t
    from src.models.database import db as _db
    try:
        data = request.get_json(silent=True) or {}
        accion = (data.get('accion') or '').strip().lower()
        if accion not in ('completar', 'rechazar'):
            return build_cors_response({'success': False, 'error': "accion debe ser 'completar' o 'rechazar'"}, 400)
        row = _db.session.execute(_t(
            "SELECT usuario_id, tipo, estado FROM solicitudes_privacidad WHERE id=:id"), {'id': solicitud_id}).fetchone()
        if not row:
            return build_cors_response({'success': False, 'error': 'Solicitud no encontrada'}, 404)
        uid, tipo, estado = row[0], row[1], row[2]
        if estado != 'pendiente':
            return build_cors_response({'success': False, 'error': f'La solicitud ya está «{estado}»'}, 400)

        eliminado = False
        if accion == 'completar' and tipo == 'eliminacion':
            # Derecho al olvido → baja lógica (papelera), no se purga aquí.
            no_admin = _db.session.execute(_t("""
                SELECT a.id FROM administradores a JOIN usuarios u ON LOWER(a.email)=LOWER(u.correo)
                WHERE u.id_usuario=:u AND a.activo=true"""), {'u': uid}).fetchone()
            if no_admin:
                return build_cors_response({'success': False, 'error': 'El usuario es administrador activo; desactívalo primero.'}, 403)
            _db.session.execute(_t("""
                UPDATE usuarios SET eliminado=TRUE, eliminado_en=NOW(),
                       eliminado_por=:by, active=FALSE WHERE id_usuario=:u
            """), {'by': getattr(g, 'user_email', None) or 'admin', 'u': uid})
            eliminado = True

        nuevo_estado = 'completada' if accion == 'completar' else 'rechazada'
        _db.session.execute(_t("""
            UPDATE solicitudes_privacidad
            SET estado=:e, atendida_por=:by, fecha_atencion=NOW(),
                nota = COALESCE(:n, nota) WHERE id=:id
        """), {'e': nuevo_estado, 'by': getattr(g, 'user_email', None) or 'admin',
               'n': (data.get('nota') or None), 'id': solicitud_id})
        _db.session.commit()
        registrar_auditoria('editar', 'solicitud_privacidad', solicitud_id,
                            {'accion': accion, 'tipo': tipo, 'usuario_id': uid, 'eliminado': eliminado})
        return build_cors_response({'success': True, 'eliminado': eliminado,
                                    'message': f'Solicitud {nuevo_estado}' + (' — usuario enviado a papelera' if eliminado else '')})
    except Exception as e:
        logger.error(f"Error en privacidad_procesar_solicitud: {e}")
        try:
            _db.session.rollback()
        except Exception:
            pass
        return build_cors_response({'success': False, 'error': str(e)}, 500)


# ═══════════════════════════════════════════════════════════════════════════════
# GESTOR DE PLANTILLAS DE EMAIL / RESEND (Admin Panel A46)
# Editar correos transaccionales + estado de deliverability + envío de prueba.
# ═══════════════════════════════════════════════════════════════════════════════
@admin_bp.route('/emails', methods=['GET'])
@requiere_permiso('configuracion')
def admin_emails():
    """GET /api/admin/emails → plantillas efectivas + estado de Resend."""
    import os as _os
    try:
        from src.models.colombia_data.config_plataforma import get_email_plantillas
        plantillas = get_email_plantillas()
        resend_ok = bool(_os.environ.get('RESEND_API_KEY', '').strip())
        from_email = _os.environ.get('RESEND_FROM', '') or _os.environ.get('EMAIL_FROM', '')
        return build_cors_response({'success': True, 'plantillas': plantillas,
                                    'deliverability': {'resend_configurado': resend_ok, 'from': from_email}})
    except Exception as e:
        logger.error(f"Error en admin_emails: {e}")
        return build_cors_response({'success': False, 'error': str(e), 'plantillas': {}}, 200)


@admin_bp.route('/emails/<clave>', methods=['PUT'])
@requiere_permiso('configuracion')
def update_email_plantilla(clave):
    """PUT /api/admin/emails/<clave>  body: { subject, html } → edita una plantilla."""
    try:
        from src.models.colombia_data.config_plataforma import (
            validar_plantilla_email, set_email_plantilla, EMAIL_PLANTILLAS_DEFAULT, get_email_plantillas
        )
        if clave not in EMAIL_PLANTILLAS_DEFAULT and clave not in get_email_plantillas():
            return build_cors_response({'success': False, 'error': 'Plantilla desconocida'}, 404)
        ok, limpio, error = validar_plantilla_email(request.get_json(silent=True) or {})
        if not ok:
            return build_cors_response({'success': False, 'error': error}, 400)
        set_email_plantilla(clave, limpio['subject'], limpio['html'])
        registrar_auditoria('editar', 'email_plantilla', None, {'clave': clave, 'subject': limpio['subject']})
        return build_cors_response({'success': True, 'message': f"Plantilla '{clave}' actualizada"})
    except Exception as e:
        logger.error(f"Error en update_email_plantilla: {e}")
        try:
            from src.models.database import db as _db
            _db.session.rollback()
        except Exception:
            pass
        return build_cors_response({'success': False, 'error': str(e)}, 500)


@admin_bp.route('/emails/<clave>/test', methods=['POST'])
@requiere_permiso('configuracion')
def test_email_plantilla(clave):
    """POST /api/admin/emails/<clave>/test  body: { email } → envía un correo de prueba renderizado."""
    try:
        from src.models.colombia_data.config_plataforma import get_email_plantilla, render_email
        destino = ((request.get_json(silent=True) or {}).get('email') or '').strip()
        if not destino or '@' not in destino:
            return build_cors_response({'success': False, 'error': 'Email de destino inválido'}, 400)
        pl = get_email_plantilla(clave)
        if not pl:
            return build_cors_response({'success': False, 'error': 'Plantilla no encontrada'}, 404)
        # Variables de muestra para la previsualización
        muestra = {v: f'[{v}]' for v in (pl.get('variables') or [])}
        muestra.update({'nombre': 'Carlos (prueba)', 'reset_url': 'https://tukomercio.co/reset_password.html?token=PRUEBA',
                        'negocio': 'Tienda Demo', 'codigo_pedido': 'DEMO-0001', 'total': '$10.000'})
        subject = '[PRUEBA] ' + render_email(pl.get('subject', ''), muestra)
        html = render_email(pl.get('html', ''), muestra)
        # Reusar el emisor existente (Resend)
        from src.api.auth.password_reset_api import send_email_resend
        ok, msg = send_email_resend(destino, subject, html)
        registrar_auditoria('enviar', 'email_prueba', None, {'clave': clave, 'destino': destino, 'ok': ok})
        if not ok:
            return build_cors_response({'success': False, 'error': msg or 'No se pudo enviar'}, 200)
        return build_cors_response({'success': True, 'message': f'Correo de prueba enviado a {destino}'})
    except Exception as e:
        logger.error(f"Error en test_email_plantilla: {e}")
        return build_cors_response({'success': False, 'error': str(e)}, 500)


# ═══════════════════════════════════════════════════════════════════════════════
# VERTICALES + OVERVIEW DE TIENDA AVANZADA (Admin Panel A47)
# Distribución por vertical (tipo_pagina) + cupones, carritos abandonados, etc.
# ═══════════════════════════════════════════════════════════════════════════════
@admin_bp.route('/verticales/overview', methods=['GET'])
@requiere_permiso('negocios')
def verticales_overview():
    """GET /api/admin/verticales/overview → distribución por vertical + métricas de tienda avanzada."""
    from sqlalchemy import text as _t
    from src.models.database import db as _db
    try:
        from src.api.utils.verticales_service import etiqueta_vertical

        verticales = []
        try:
            for r in _db.session.execute(_t("""
                SELECT COALESCE(NULLIF(tipo_pagina,''),'landing') AS t, COUNT(*) AS n
                FROM negocios WHERE COALESCE(eliminado,FALSE)=FALSE
                GROUP BY t ORDER BY n DESC
            """)).fetchall():
                meta = etiqueta_vertical(r[0])
                verticales.append({**meta, 'cantidad': int(r[1])})
        except Exception:
            pass

        def _scalar(sql):
            try:
                return _db.session.execute(_t(sql)).scalar() or 0
            except Exception:
                return 0
        cupones = {
            'total':   int(_scalar("SELECT COUNT(*) FROM cupones")),
            'activos': int(_scalar("SELECT COUNT(*) FROM cupones WHERE activo IS TRUE")),
            'usos':    int(_scalar("SELECT COALESCE(SUM(usos_actuales),0) FROM cupones")),
        }
        carritos = {
            'abandonados': int(_scalar("SELECT COUNT(*) FROM carritos_abandonados WHERE estado='abandonado'")),
            'recuperados': int(_scalar("SELECT COUNT(*) FROM carritos_abandonados WHERE estado <> 'abandonado'")),
            'valor_recuperable': float(_scalar("SELECT COALESCE(SUM(total_estimado),0) FROM carritos_abandonados WHERE estado='abandonado'")),
        }
        resenas = {
            'total':     int(_scalar("SELECT COUNT(*) FROM producto_reviews")),
            'aprobadas': int(_scalar("SELECT COUNT(*) FROM producto_reviews WHERE aprobado IS TRUE")),
        }

        return build_cors_response({'success': True, 'verticales': verticales,
                                    'cupones': cupones, 'carritos': carritos, 'resenas': resenas})
    except Exception as e:
        logger.error(f"Error en verticales_overview: {e}")
        return build_cors_response({'success': False, 'error': str(e), 'verticales': []}, 200)


# ═══════════════════════════════════════════════════════════════════════════════
# INTEGRACIONES Y AUTOMATIZACIONES (Admin Panel A48)
# Estado de integraciones externas + WhatsApp post-venta + import CSV.
# ═══════════════════════════════════════════════════════════════════════════════
@admin_bp.route('/integraciones', methods=['GET'])
@requiere_permiso('configuracion')
def admin_integraciones():
    """GET /api/admin/integraciones → estado de integraciones + config de automatizaciones."""
    import os as _os
    from sqlalchemy import text as _t
    from src.models.database import db as _db
    try:
        from src.api.utils.integraciones_service import estado_integraciones, TRIGGERS_POSTVENTA
        from src.models.colombia_data.config_plataforma import get_integraciones_config
        try:
            wompi_activos = int(_db.session.execute(_t("SELECT COUNT(*) FROM wompi_configs WHERE activo IS TRUE")).scalar() or 0)
        except Exception:
            wompi_activos = 0
        env = {'RESEND_API_KEY': _os.environ.get('RESEND_API_KEY', ''),
               'GROQ_API_KEY': _os.environ.get('GROQ_API_KEY', '')}
        return build_cors_response({
            'success': True,
            'integraciones': estado_integraciones(env, wompi_activos),
            'config': get_integraciones_config(),
            'triggers': sorted(TRIGGERS_POSTVENTA),
            'import_csv_endpoint': '/api/contabilidad/carga-masiva',  # ya existe (referencia)
        })
    except Exception as e:
        logger.error(f"Error en admin_integraciones: {e}")
        return build_cors_response({'success': False, 'error': str(e), 'integraciones': []}, 200)


@admin_bp.route('/integraciones/config', methods=['PUT'])
@requiere_permiso('configuracion')
def update_integraciones_config():
    """PUT /api/admin/integraciones/config → automatizaciones (WhatsApp post-venta)."""
    try:
        from src.api.utils.integraciones_service import validar_integraciones_config
        from src.models.colombia_data.config_plataforma import set_integraciones_config, get_integraciones_config
        antes = get_integraciones_config()
        ok, limpio, error = validar_integraciones_config(request.get_json(silent=True) or {})
        if not ok:
            return build_cors_response({'success': False, 'error': error}, 400)
        nueva = set_integraciones_config(limpio)
        registrar_auditoria('editar', 'integraciones', None, {'antes': antes, 'despues': limpio})
        return build_cors_response({'success': True, 'config': nueva, 'message': 'Integraciones actualizadas'})
    except Exception as e:
        logger.error(f"Error en update_integraciones_config: {e}")
        try:
            from src.models.database import db as _db
            _db.session.rollback()
        except Exception:
            pass
        return build_cors_response({'success': False, 'error': str(e)}, 500)


# ═══════════════════════════════════════════════════════════════════════════════
# GESTOR CENTRAL DE TEXTOS / COPYS (Admin Panel A49) ⭐ — cierra Fase 6
# Editar TODO el texto visible al usuario sin tocar código. Base i18n.
# ═══════════════════════════════════════════════════════════════════════════════
@admin_bp.route('/textos', methods=['GET'])
@requiere_permiso('configuracion')
def admin_textos():
    """GET /api/admin/textos → catálogo de textos efectivos (con overrides marcados)."""
    try:
        from src.models.colombia_data.config_plataforma import get_textos
        return build_cors_response({'success': True, 'textos': get_textos()})
    except Exception as e:
        logger.error(f"Error en admin_textos: {e}")
        return build_cors_response({'success': False, 'error': str(e), 'textos': {}}, 200)


@admin_bp.route('/textos', methods=['PUT'])
@requiere_permiso('configuracion')
def update_textos():
    """PUT /api/admin/textos  body: { textos: { clave: valor, ... } } → guarda overrides."""
    try:
        from src.models.colombia_data.config_plataforma import validar_textos, set_textos
        payload = request.get_json(silent=True) or {}
        textos = payload.get('textos', payload if isinstance(payload, dict) and 'textos' not in payload else {})
        ok, limpio, error = validar_textos(textos)
        if not ok:
            return build_cors_response({'success': False, 'error': error}, 400)
        set_textos(limpio)
        registrar_auditoria('editar', 'textos', None, {'claves': list(limpio.keys())})
        return build_cors_response({'success': True, 'message': f'{len(limpio)} texto(s) guardado(s)'})
    except Exception as e:
        logger.error(f"Error en update_textos: {e}")
        try:
            from src.models.database import db as _db
            _db.session.rollback()
        except Exception:
            pass
        return build_cors_response({'success': False, 'error': str(e)}, 500)


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


# ═══════════════════════════════════════════════════════════════════════════════
# FICHA 360° DEL NEGOCIO (Admin Panel A29)
# Todo de un negocio en una vista: datos, dueño, plan/suscripción, gamificación,
# insignias, pedidos, videos y estado. Cada bloque es a prueba de fallos.
# ═══════════════════════════════════════════════════════════════════════════════
@admin_bp.route('/negocios/<int:negocio_id>/ficha360', methods=['GET'])
@requiere_permiso('negocios')
def ficha_negocio_360(negocio_id):
    """GET /api/admin/negocios/<id>/ficha360 → agregado completo del negocio."""
    try:
        conn = get_db_connection(); cur = conn.cursor()
        cur.execute("""
            SELECT id_negocio, nombre_negocio, slug, categoria, ciudad, telefono, whatsapp,
                   email, logo_url, color_tema, activo, verificado, perfil_publico, tiene_pagina,
                   plan_key, fecha_registro, usuario_id
            FROM negocios WHERE id_negocio = %s
        """, (negocio_id,))
        n = cur.fetchone()
        if not n:
            cur.close(); conn.close()
            return build_cors_response({'success': False, 'error': 'Negocio no encontrado'}, 404)
        n = dict(n)

        # Dueño
        dueno = None
        try:
            cur.execute("SELECT id_usuario, nombre, correo FROM usuarios WHERE id_usuario = %s",
                        (n.get('usuario_id'),))
            u = cur.fetchone()
            if u:
                dueno = {'usuario_id': u['id_usuario'], 'nombre': u['nombre'], 'correo': u['correo']}
        except Exception:
            pass
        cur.close(); conn.close()

        negocio = {
            'id': n['id_negocio'], 'nombre': n['nombre_negocio'], 'slug': n.get('slug'),
            'categoria': n.get('categoria'), 'ciudad': n.get('ciudad'),
            'telefono': n.get('telefono'), 'whatsapp': n.get('whatsapp'), 'email': n.get('email'),
            'logo_url': n.get('logo_url'), 'color_tema': n.get('color_tema'),
            'activo': n.get('activo'), 'verificado': n.get('verificado'),
            'perfil_publico': n.get('perfil_publico'), 'tiene_pagina': n.get('tiene_pagina'),
            'plan_key': n.get('plan_key') or 'basic',
            'fecha_registro': n['fecha_registro'].isoformat() if n.get('fecha_registro') else None,
        }

        # Suscripción (a prueba de fallos: si la tabla/columna falla, queda None)
        suscripcion = None
        try:
            from src.models.colombia_data.suscripcion_negocio import SuscripcionNegocio
            from src.models.database import db as _db
            sus = SuscripcionNegocio.query.filter_by(negocio_id=negocio_id).first()
            if sus:
                suscripcion = {
                    'estado': sus.estado, 'es_trial': sus.es_trial,
                    'fecha_fin_trial': sus.fecha_fin_trial.isoformat() if sus.fecha_fin_trial else None,
                    'fecha_fin': sus.fecha_fin.isoformat() if sus.fecha_fin else None,
                    'plan_id': sus.plan_id, 'trial_usado': sus.trial_usado,
                }
        except Exception as _se:
            logger.warning(f"[ficha360] suscripción no disponible: {_se}")

        # Gamificación
        gamificacion = None
        try:
            from src.models.colombia_data.ratings.negocio_gamificacion import NegocioGamificacion
            gami = NegocioGamificacion.query.filter_by(negocio_id=negocio_id).first()
            if gami:
                g = gami.serialize()
                gamificacion = {
                    'nivel': g.get('nivel'), 'xp_total': g.get('xp_total'),
                    'tukoins': g.get('tukoins'), 'prestigio': g.get('prestigio'),
                    'racha': (g.get('racha_actividad') or {}).get('dias') if isinstance(g.get('racha_actividad'), dict) else g.get('racha_actividad'),
                }
        except Exception as _ge:
            logger.warning(f"[ficha360] gamificación no disponible: {_ge}")

        # Conteos (escalares tolerantes)
        insignias = int(_scalar_admin(
            "SELECT COUNT(*) AS v FROM negocio_badges_obtenidos WHERE negocio_id = %s "
            "AND (activo IS TRUE OR activo IS NULL)", (negocio_id,)))
        pedidos = {
            'total': int(_scalar_admin("SELECT COUNT(*) AS v FROM pedidos WHERE negocio_id = %s", (negocio_id,))),
            'entregados': int(_scalar_admin(
                "SELECT COUNT(*) AS v FROM pedidos WHERE negocio_id = %s AND estado = 'entregado'", (negocio_id,))),
            'ventas_total': float(_scalar_admin(
                "SELECT COALESCE(SUM(total),0) AS v FROM pedidos WHERE negocio_id = %s AND estado = 'entregado'", (negocio_id,))),
        }
        productos = int(_scalar_admin(
            "SELECT COUNT(*) AS v FROM productos_catalogo WHERE negocio_id = %s", (negocio_id,)))
        videos = {
            'total': int(_scalar_admin("SELECT COUNT(*) AS v FROM negocio_videos WHERE negocio_id = %s", (negocio_id,))),
            'aprobados': int(_scalar_admin(
                "SELECT COUNT(*) AS v FROM negocio_videos WHERE negocio_id = %s AND estado_moderacion = 'aprobado'", (negocio_id,))),
            'pendientes': int(_scalar_admin(
                "SELECT COUNT(*) AS v FROM negocio_videos WHERE negocio_id = %s AND estado_moderacion = 'pendiente'", (negocio_id,))),
        }
        if gamificacion is not None:
            gamificacion['insignias'] = insignias

        return build_cors_response({
            'success': True, 'negocio': negocio, 'dueno': dueno,
            'suscripcion': suscripcion, 'gamificacion': gamificacion,
            'insignias': insignias, 'pedidos': pedidos, 'productos': productos, 'videos': videos,
        })
    except Exception as e:
        logger.error(f"Error en ficha_negocio_360: {e}")
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

@admin_bp.route('/gamificacion/eventos', methods=['GET'])
@requiere_permiso('gamificacion')
def get_gamif_eventos():
    """GET /api/admin/gamificacion/eventos → lista efectiva de eventos especiales + default."""
    try:
        from src.models.colombia_data.ratings.config_gamificacion import get_eventos_especiales, _eventos_default
        from src.models.colombia_data.ratings.negocio_gamificacion import evento_especial
        activo = evento_especial()
        return build_cors_response({
            'success': True,
            'eventos': get_eventos_especiales(),
            'default': _eventos_default(),
            'activo': activo,
        })
    except Exception as e:
        logger.error(f"Error en get_gamif_eventos: {e}")
        return build_cors_response({'success': False, 'error': str(e)}, 200)


@admin_bp.route('/gamificacion/eventos', methods=['PUT'])
@requiere_permiso('gamificacion')
def update_gamif_eventos():
    """PUT /api/admin/gamificacion/eventos  body: { eventos: [ {codigo,nombre,icono,mes,dia_ini,dia_fin,xp_mult} ] }"""
    try:
        from src.models.colombia_data.ratings.config_gamificacion import (
            validar_eventos, set_eventos_especiales, get_eventos_especiales
        )
        antes = get_eventos_especiales()
        payload = request.get_json(silent=True) or {}
        lista = payload.get('eventos', payload if isinstance(payload, list) else [])
        ok, limpio, error = validar_eventos(lista)
        if not ok:
            return build_cors_response({'success': False, 'error': error}, 400)
        set_eventos_especiales(limpio)
        registrar_auditoria('editar', 'gamif_eventos', None,
                            {'antes': antes, 'despues': limpio, 'total': len(limpio)})
        return build_cors_response({'success': True, 'eventos': limpio,
                                    'message': f'{len(limpio)} evento(s) guardado(s)'})
    except Exception as e:
        logger.error(f"Error en update_gamif_eventos: {e}")
        try:
            from src.models.database import db as _db
            _db.session.rollback()
        except Exception:
            pass
        return build_cors_response({'success': False, 'error': str(e)}, 500)


@admin_bp.route('/gamificacion/retos', methods=['GET'])
@requiere_permiso('gamificacion')
def get_gamif_retos():
    """GET /api/admin/gamificacion/retos → pool efectivo, default, métricas, programación y reto actual."""
    try:
        from src.models.colombia_data.ratings.config_gamificacion import (
            get_retos_mensuales, get_programacion_retos, _retos_default, METRICAS_RETO
        )
        from src.api.gamificacion.gamificacion_api import _reto_del_mes
        return build_cors_response({
            'success': True,
            'retos': get_retos_mensuales(),
            'default': _retos_default(),
            'metricas': METRICAS_RETO,
            'programacion': get_programacion_retos(),
            'actual': _reto_del_mes(),
        })
    except Exception as e:
        logger.error(f"Error en get_gamif_retos: {e}")
        return build_cors_response({'success': False, 'error': str(e)}, 200)


@admin_bp.route('/gamificacion/retos', methods=['PUT'])
@requiere_permiso('gamificacion')
def update_gamif_retos():
    """PUT /api/admin/gamificacion/retos  body: { retos: [...], programacion: {YYYY-MM: codigo} }"""
    try:
        from src.models.colombia_data.ratings.config_gamificacion import (
            validar_retos, validar_programacion_retos,
            set_retos_mensuales, set_programacion_retos,
            get_retos_mensuales, get_programacion_retos
        )
        antes = {'retos': get_retos_mensuales(), 'programacion': get_programacion_retos()}
        payload = request.get_json(silent=True) or {}
        ok, retos, error = validar_retos(payload.get('retos', []))
        if not ok:
            return build_cors_response({'success': False, 'error': error}, 400)
        codigos = {r['codigo'] for r in retos}
        ok2, prog, error2 = validar_programacion_retos(payload.get('programacion', {}), codigos)
        if not ok2:
            return build_cors_response({'success': False, 'error': error2}, 400)
        set_retos_mensuales(retos)
        set_programacion_retos(prog)
        registrar_auditoria('editar', 'gamif_retos', None,
                            {'antes': antes, 'despues': {'retos': retos, 'programacion': prog}})
        return build_cors_response({'success': True, 'retos': retos, 'programacion': prog,
                                    'message': f'{len(retos)} reto(s) guardado(s)'})
    except Exception as e:
        logger.error(f"Error en update_gamif_retos: {e}")
        try:
            from src.models.database import db as _db
            _db.session.rollback()
        except Exception:
            pass
        return build_cors_response({'success': False, 'error': str(e)}, 500)


# ═══════════════════════════════════════════════════════════════════════════════
# MODERACIÓN DE LIGAS (Admin Panel A24)
# Ver ligas por ciudad/categoría, detectar anomalías, vetar/readmitir negocios.
# ═══════════════════════════════════════════════════════════════════════════════
@admin_bp.route('/gamificacion/ligas', methods=['GET'])
@requiere_permiso('gamificacion')
def admin_ligas():
    """GET /api/admin/gamificacion/ligas?ciudad=&categoria=&limit= → ranking + stats + anomalías + excluidos."""
    from sqlalchemy import text as _t
    from src.models.database import db as _db
    try:
        from src.api.gamificacion.gamificacion_api import _rango_mes, _armar_ranking
        from src.models.colombia_data.ratings.config_gamificacion import (
            get_ligas_config, get_negocios_excluidos_ligas, detectar_anomalias
        )
        ciudad    = (request.args.get('ciudad', '') or '').strip()
        categoria = (request.args.get('categoria', '') or '').strip()
        limit     = min(int(request.args.get('limit', 20) or 20), 100)
        inicio, fin, etiqueta = _rango_mes()
        cfg = get_ligas_config()
        excluidos = get_negocios_excluidos_ligas()

        sql = """
            SELECT n.id_negocio, n.nombre_negocio, n.ciudad, n.categoria,
                   n.logo_url, n.slug, COUNT(p.id_pedido) AS ventas_mes
            FROM negocios n
            LEFT JOIN pedidos p ON p.negocio_id = n.id_negocio
                 AND p.estado = 'entregado'
                 AND p.fecha_pedido >= :ini AND p.fecha_pedido < :fin
            WHERE n.activo = true AND n.perfil_publico = true
        """
        params = {'ini': inicio, 'fin': fin, 'lim': limit}
        if ciudad:
            sql += " AND LOWER(n.ciudad) LIKE :ciudad"; params['ciudad'] = f"%{ciudad.lower()}%"
        if categoria:
            sql += " AND LOWER(n.categoria) LIKE :categoria"; params['categoria'] = f"%{categoria.lower()}%"
        sql += """
            GROUP BY n.id_negocio, n.nombre_negocio, n.ciudad, n.categoria, n.logo_url, n.slug
            HAVING COUNT(p.id_pedido) > 0
            ORDER BY ventas_mes DESC
            LIMIT :lim
        """
        filas = [tuple(f) for f in _db.session.execute(_t(sql), params).fetchall()]
        # Anomalías sobre TODOS los participantes (incluye excluidos para no sesgar el cálculo).
        anomalias = detectar_anomalias(filas, cfg.get('umbral_anomalia', 3.0))
        data = _armar_ranking(filas, None)
        # Enriquecer cada fila con flags de moderación.
        for fila in data['ranking']:
            nid = fila['negocio_id']
            fila['excluido'] = nid in excluidos
            fila['anomalia'] = anomalias.get(nid)  # z-score o None

        puntajes = [int(f[6] or 0) for f in filas]
        total = len(filas)
        liga = ciudad or categoria or 'Nacional'
        stats = {
            'participantes': total,
            'segmentada': total >= cfg.get('min_participantes', 3),
            'ventas_total': sum(puntajes),
            'promedio': round(sum(puntajes) / total, 2) if total else 0,
            'top_puntaje': max(puntajes) if puntajes else 0,
            'anomalias': len(anomalias),
            'excluidos_en_vista': sum(1 for f in data['ranking'] if f['excluido']),
        }
        return build_cors_response({
            'success': True, 'mes': etiqueta, 'liga': liga,
            'config': cfg, 'excluidos': excluidos, 'stats': stats, **data,
        })
    except Exception as e:
        logger.error(f"Error en admin_ligas: {e}")
        return build_cors_response({'success': False, 'error': str(e), 'ranking': []}, 200)


@admin_bp.route('/gamificacion/ligas/config', methods=['PUT'])
@requiere_permiso('gamificacion')
def update_admin_ligas_config():
    """PUT /api/admin/gamificacion/ligas/config  body: { min_participantes, umbral_anomalia }"""
    try:
        from src.models.colombia_data.ratings.config_gamificacion import (
            validar_ligas_config, set_ligas_config, get_ligas_config
        )
        antes = get_ligas_config()
        ok, limpio, error = validar_ligas_config(request.get_json(silent=True) or {})
        if not ok:
            return build_cors_response({'success': False, 'error': error}, 400)
        set_ligas_config(limpio)
        registrar_auditoria('editar', 'gamif_ligas_config', None, {'antes': antes, 'despues': limpio})
        return build_cors_response({'success': True, 'config': limpio, 'message': 'Configuración de ligas actualizada'})
    except Exception as e:
        logger.error(f"Error en update_admin_ligas_config: {e}")
        try:
            from src.models.database import db as _db
            _db.session.rollback()
        except Exception:
            pass
        return build_cors_response({'success': False, 'error': str(e)}, 500)


@admin_bp.route('/gamificacion/ligas/moderar', methods=['POST'])
@requiere_permiso('gamificacion')
def moderar_liga_negocio():
    """
    POST /api/admin/gamificacion/ligas/moderar  body: { negocio_id, accion: 'excluir'|'readmitir' }
    Veta o readmite a un negocio en las ligas (anti-fraude). Auditado.
    """
    try:
        from src.models.colombia_data.ratings.config_gamificacion import (
            get_negocios_excluidos_ligas, set_negocios_excluidos_ligas
        )
        payload = request.get_json(silent=True) or {}
        try:
            nid = int(payload.get('negocio_id'))
        except (TypeError, ValueError):
            return build_cors_response({'success': False, 'error': 'negocio_id inválido'}, 400)
        accion = (payload.get('accion') or '').strip().lower()
        if accion not in ('excluir', 'readmitir'):
            return build_cors_response({'success': False, 'error': "accion debe ser 'excluir' o 'readmitir'"}, 400)
        excluidos = set(get_negocios_excluidos_ligas())
        if accion == 'excluir':
            excluidos.add(nid)
        else:
            excluidos.discard(nid)
        nueva = set_negocios_excluidos_ligas(list(excluidos))
        registrar_auditoria(accion, 'gamif_liga_negocio', nid, {'excluidos': nueva})
        return build_cors_response({'success': True, 'excluidos': nueva,
                                    'message': f"Negocio {nid} {'vetado de' if accion=='excluir' else 'readmitido en'} las ligas"})
    except Exception as e:
        logger.error(f"Error en moderar_liga_negocio: {e}")
        try:
            from src.models.database import db as _db
            _db.session.rollback()
        except Exception:
            pass
        return build_cors_response({'success': False, 'error': str(e)}, 500)


# ═══════════════════════════════════════════════════════════════════════════════
# RECOMPENSAS AUTOMÁTICAS DE LIGA (Admin Panel A25) — cron + UI
# Premia al top-N del mes anterior. Idempotente (tabla liga_recompensas).
# Condición de seguridad (como A14): preview disponible vía GET/simular; APLICAR
# exige @superadmin_required y queda auditado con el conteo de premios otorgados.
# ═══════════════════════════════════════════════════════════════════════════════
@admin_bp.route('/gamificacion/ligas/recompensas', methods=['GET'])
@requiere_permiso('gamificacion')
def get_liga_recompensas():
    """GET /api/admin/gamificacion/ligas/recompensas?ciudad=&categoria= → config + preview (dry-run) + historial."""
    from src.models.database import db as _db
    try:
        from src.models.colombia_data.ratings.config_gamificacion import get_recompensas_liga, RECOMPENSAS_LIGA_DEFAULT
        from src.api.utils.liga_recompensas_service import calcular_recompensas_liga, historial_recompensas_liga
        ciudad    = (request.args.get('ciudad', '') or '').strip()
        categoria = (request.args.get('categoria', '') or '').strip()
        preview = calcular_recompensas_liga(_db.session, ciudad, categoria)
        return build_cors_response({
            'success': True,
            'config': get_recompensas_liga(),
            'default': RECOMPENSAS_LIGA_DEFAULT,
            'preview': preview,
            'historial': historial_recompensas_liga(_db.session, 50),
        })
    except Exception as e:
        logger.error(f"Error en get_liga_recompensas: {e}")
        return build_cors_response({'success': False, 'error': str(e)}, 200)


@admin_bp.route('/gamificacion/ligas/recompensas/config', methods=['PUT'])
@requiere_permiso('gamificacion')
def update_liga_recompensas_config():
    """PUT /api/admin/gamificacion/ligas/recompensas/config  body: { recompensas: [{pos,xp,tukoins}] }"""
    try:
        from src.models.colombia_data.ratings.config_gamificacion import (
            validar_recompensas_liga, set_recompensas_liga, get_recompensas_liga
        )
        antes = get_recompensas_liga()
        payload = request.get_json(silent=True) or {}
        ok, limpio, error = validar_recompensas_liga(payload.get('recompensas', payload if isinstance(payload, list) else []))
        if not ok:
            return build_cors_response({'success': False, 'error': error}, 400)
        set_recompensas_liga(limpio)
        registrar_auditoria('editar', 'gamif_liga_recompensas', None, {'antes': antes, 'despues': limpio})
        return build_cors_response({'success': True, 'recompensas': limpio,
                                    'message': f'{len(limpio)} posición(es) configurada(s)'})
    except Exception as e:
        logger.error(f"Error en update_liga_recompensas_config: {e}")
        try:
            from src.models.database import db as _db
            _db.session.rollback()
        except Exception:
            pass
        return build_cors_response({'success': False, 'error': str(e)}, 500)


@admin_bp.route('/gamificacion/ligas/recompensas/simular', methods=['POST'])
@requiere_permiso('gamificacion')
def simular_liga_recompensas():
    """POST /api/admin/gamificacion/ligas/recompensas/simular → dry-run (NO escribe). Obligatorio antes de aplicar."""
    from src.models.database import db as _db
    try:
        from src.api.utils.liga_recompensas_service import calcular_recompensas_liga
        payload = request.get_json(silent=True) or {}
        ciudad    = (payload.get('ciudad', '') or '').strip()
        categoria = (payload.get('categoria', '') or '').strip()
        preview = calcular_recompensas_liga(_db.session, ciudad, categoria)
        return build_cors_response({'success': True, 'dry_run': True, **preview})
    except Exception as e:
        logger.error(f"Error en simular_liga_recompensas: {e}")
        return build_cors_response({'success': False, 'error': str(e)}, 200)


@admin_bp.route('/gamificacion/ligas/recompensas/ejecutar', methods=['POST'])
@superadmin_required
def ejecutar_liga_recompensas():
    """
    POST /api/admin/gamificacion/ligas/recompensas/ejecutar  body: { ciudad?, categoria?, confirmar:true }
    APLICA los premios al top-N del mes anterior. Solo superadmin. Idempotente. Auditado.
    También sirve como endpoint de cron mensual (scheduler externo con API key admin).
    """
    from src.models.database import db as _db
    try:
        from src.api.utils.liga_recompensas_service import otorgar_recompensas_liga
        payload = request.get_json(silent=True) or {}
        if not payload.get('confirmar'):
            return build_cors_response({'success': False, 'error': 'Falta confirmar:true (revisa el dry-run primero)'}, 400)
        ciudad    = (payload.get('ciudad', '') or '').strip()
        categoria = (payload.get('categoria', '') or '').strip()
        actor = getattr(g, 'user_email', None) or 'cron'
        resultado = otorgar_recompensas_liga(_db.session, ciudad, categoria, actor=actor)
        registrar_auditoria('otorgar', 'gamif_liga_recompensas', None, {
            'periodo': resultado['periodo'], 'liga': resultado['liga'],
            'otorgados': resultado['total_otorgados'], 'omitidos': resultado['total_omitidos'],
            'total_xp': resultado['total_xp'], 'total_tukoins': resultado['total_tukoins'],
        })
        return build_cors_response({'success': True, **resultado,
                                    'message': f"{resultado['total_otorgados']} premio(s) otorgado(s), {resultado['total_omitidos']} omitido(s)"})
    except Exception as e:
        logger.error(f"Error en ejecutar_liga_recompensas: {e}")
        try:
            _db.session.rollback()
        except Exception:
            pass
        return build_cors_response({'success': False, 'error': str(e)}, 500)


# ═══════════════════════════════════════════════════════════════════════════════
# GESTIÓN DE REFERIDOS (Admin Panel A27)
# Árbol de referidos, conversiones, detección de fraude y recompensas editables.
# ═══════════════════════════════════════════════════════════════════════════════
@admin_bp.route('/gamificacion/referidos', methods=['GET'])
@requiere_permiso('gamificacion')
def admin_referidos():
    """GET /api/admin/gamificacion/referidos?limit= → stats + top referidores (con fraude) + recientes + config."""
    from sqlalchemy import text as _t
    from src.models.database import db as _db
    try:
        from src.models.colombia_data.ratings.config_gamificacion import (
            get_referidos_config, marcar_referidores_sospechosos
        )
        limit = min(int(request.args.get('limit', 50) or 50), 200)
        cfg = get_referidos_config()

        # Estadísticas globales.
        g_row = _db.session.execute(_t("""
            SELECT COUNT(*) AS total,
                   COUNT(*) FILTER (WHERE convertido) AS convertidos,
                   COUNT(*) FILTER (WHERE recompensado) AS recompensados
            FROM referidos
        """)).fetchone()
        total = g_row[0] or 0; convertidos = g_row[1] or 0; recompensados = g_row[2] or 0
        stats = {
            'total': total, 'convertidos': convertidos, 'recompensados': recompensados,
            'tasa_conversion': round(convertidos / total, 3) if total else 0,
        }

        # Top referidores (el "árbol": quién ha referido y cuántos convirtieron).
        top_rows = _db.session.execute(_t("""
            SELECT r.referidor_usuario_id, u.nombre, u.correo,
                   COUNT(*) AS total,
                   COUNT(*) FILTER (WHERE r.convertido) AS convertidos
            FROM referidos r
            LEFT JOIN usuarios u ON u.id_usuario = r.referidor_usuario_id
            GROUP BY r.referidor_usuario_id, u.nombre, u.correo
            ORDER BY total DESC
            LIMIT :lim
        """), {'lim': limit}).fetchall()
        filas_fraude = [{'usuario_id': r[0], 'total': r[3], 'convertidos': r[4]} for r in top_rows]
        sospechosos = marcar_referidores_sospechosos(
            filas_fraude, cfg.get('umbral_fraude', 10), cfg.get('ratio_min', 0.2))
        top = [{
            'usuario_id': r[0], 'nombre': r[1] or f'#{r[0]}', 'correo': r[2] or '',
            'total': r[3], 'convertidos': r[4],
            'tasa': round((r[4] / r[3]), 2) if r[3] else 0,
            'sospechoso': r[0] in sospechosos,
        } for r in top_rows]

        # Referidos recientes.
        rec_rows = _db.session.execute(_t("""
            SELECT r.id, r.referidor_usuario_id, ur.nombre,
                   r.referido_usuario_id, ud.nombre,
                   r.convertido, r.recompensado, r.fecha_registro, r.fecha_conversion
            FROM referidos r
            LEFT JOIN usuarios ur ON ur.id_usuario = r.referidor_usuario_id
            LEFT JOIN usuarios ud ON ud.id_usuario = r.referido_usuario_id
            ORDER BY r.fecha_registro DESC
            LIMIT :lim
        """), {'lim': limit}).fetchall()
        recientes = [{
            'id': r[0],
            'referidor': {'usuario_id': r[1], 'nombre': r[2] or f'#{r[1]}'},
            'referido':  {'usuario_id': r[3], 'nombre': r[4] or f'#{r[3]}'},
            'convertido': r[5], 'recompensado': r[6],
            'fecha_registro': r[7].isoformat() if r[7] else None,
            'fecha_conversion': r[8].isoformat() if r[8] else None,
        } for r in rec_rows]

        return build_cors_response({'success': True, 'config': cfg, 'stats': stats,
                                    'top': top, 'recientes': recientes,
                                    'sospechosos': len(sospechosos)})
    except Exception as e:
        logger.error(f"Error en admin_referidos: {e}")
        return build_cors_response({'success': False, 'error': str(e), 'top': [], 'recientes': []}, 200)


@admin_bp.route('/gamificacion/referidos/config', methods=['PUT'])
@requiere_permiso('gamificacion')
def update_referidos_config():
    """PUT /api/admin/gamificacion/referidos/config  body: { xp_referidor, tukoins_referidor, umbral_fraude, ratio_min }"""
    try:
        from src.models.colombia_data.ratings.config_gamificacion import (
            validar_referidos_config, set_referidos_config, get_referidos_config
        )
        antes = get_referidos_config()
        ok, limpio, error = validar_referidos_config(request.get_json(silent=True) or {})
        if not ok:
            return build_cors_response({'success': False, 'error': error}, 400)
        set_referidos_config(limpio)
        registrar_auditoria('editar', 'gamif_referidos_config', None, {'antes': antes, 'despues': limpio})
        return build_cors_response({'success': True, 'config': limpio, 'message': 'Config de referidos actualizada'})
    except Exception as e:
        logger.error(f"Error en update_referidos_config: {e}")
        try:
            from src.models.database import db as _db
            _db.session.rollback()
        except Exception:
            pass
        return build_cors_response({'success': False, 'error': str(e)}, 500)


# ═══════════════════════════════════════════════════════════════════════════════
# MODERACIÓN DE DUELOS (Admin Panel A26)
# Ver duelos activos/históricos con marcadores y cancelar los abusivos.
# ═══════════════════════════════════════════════════════════════════════════════
@admin_bp.route('/gamificacion/duelos', methods=['GET'])
@requiere_permiso('gamificacion')
def admin_duelos():
    """GET /api/admin/gamificacion/duelos?estado=&limit= → lista de duelos + nombres + resumen."""
    from sqlalchemy import text as _t
    from src.models.database import db as _db
    try:
        estado = (request.args.get('estado', '') or '').strip().lower()
        limit  = min(int(request.args.get('limit', 50) or 50), 200)
        sql = """
            SELECT d.id, d.retador_negocio_id, nr.nombre_negocio,
                   d.retado_negocio_id, nt.nombre_negocio,
                   d.estado, d.fecha_inicio, d.fecha_fin, d.creado_en,
                   d.ganador_negocio_id, d.ventas_retador, d.ventas_retado
            FROM duelos d
            LEFT JOIN negocios nr ON nr.id_negocio = d.retador_negocio_id
            LEFT JOIN negocios nt ON nt.id_negocio = d.retado_negocio_id
        """
        params = {'lim': limit}
        if estado:
            sql += " WHERE LOWER(d.estado) = :estado"; params['estado'] = estado
        sql += " ORDER BY d.creado_en DESC LIMIT :lim"
        rows = _db.session.execute(_t(sql), params).fetchall()

        from src.models.colombia_data.ratings.duelo import puede_cancelar_duelo
        duelos = []
        for r in rows:
            duelos.append({
                'id': r[0],
                'retador': {'negocio_id': r[1], 'nombre': r[2] or f'#{r[1]}', 'ventas': r[10] or 0},
                'retado':  {'negocio_id': r[3], 'nombre': r[4] or f'#{r[3]}', 'ventas': r[11] or 0},
                'estado': r[5],
                'fecha_inicio': r[6].isoformat() if r[6] else None,
                'fecha_fin': r[7].isoformat() if r[7] else None,
                'creado_en': r[8].isoformat() if r[8] else None,
                'ganador_negocio_id': r[9],
                'cancelable': puede_cancelar_duelo(r[5]),
            })

        # Resumen por estado (sobre toda la tabla, no solo la página).
        res = _db.session.execute(_t("SELECT LOWER(estado), COUNT(*) FROM duelos GROUP BY LOWER(estado)")).fetchall()
        resumen = {row[0]: row[1] for row in res}
        return build_cors_response({'success': True, 'duelos': duelos, 'resumen': resumen,
                                    'total': sum(resumen.values())})
    except Exception as e:
        logger.error(f"Error en admin_duelos: {e}")
        return build_cors_response({'success': False, 'error': str(e), 'duelos': []}, 200)


@admin_bp.route('/gamificacion/duelos/<int:duelo_id>/cancelar', methods=['POST'])
@requiere_permiso('gamificacion')
def cancelar_duelo(duelo_id):
    """POST /api/admin/gamificacion/duelos/<id>/cancelar  body: { motivo? } → cancela un duelo abusivo."""
    from src.models.database import db as _db
    try:
        from src.models.colombia_data.ratings.duelo import Duelo, puede_cancelar_duelo
        d = Duelo.query.get(duelo_id)
        if not d:
            return build_cors_response({'success': False, 'error': 'Duelo no encontrado'}, 404)
        if not puede_cancelar_duelo(d.estado):
            return build_cors_response({'success': False, 'error': f'No se puede cancelar un duelo «{d.estado}»'}, 400)
        antes = d.estado
        motivo = (request.get_json(silent=True) or {}).get('motivo', '')
        d.estado = 'cancelado'
        _db.session.commit()
        registrar_auditoria('rechazar', 'duelo', duelo_id,
                            {'antes': antes, 'despues': 'cancelado', 'motivo': motivo,
                             'retador': d.retador_negocio_id, 'retado': d.retado_negocio_id})
        return build_cors_response({'success': True, 'duelo': d.serialize(), 'message': 'Duelo cancelado'})
    except Exception as e:
        logger.error(f"Error en cancelar_duelo: {e}")
        try:
            _db.session.rollback()
        except Exception:
            pass
        return build_cors_response({'success': False, 'error': str(e)}, 500)


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
        'vigencia_inicio': b.vigencia_inicio.isoformat() if getattr(b, 'vigencia_inicio', None) else None,
        'vigencia_fin': b.vigencia_fin.isoformat() if getattr(b, 'vigencia_fin', None) else None,
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


# ═══════════════════════════════════════════════════════════════════════════════
# INSIGNIAS — VALIDADOR DE COHERENCIA POR TIER (Admin Panel A18)
# Avisa (no bloquea) si la dificultad rompe la monotonicidad por tier.
# ═══════════════════════════════════════════════════════════════════════════════

@admin_bp.route('/insignias/coherencia', methods=['POST', 'OPTIONS'])
@requiere_permiso('insignias')
def coherencia_insignia():
    """
    POST /api/admin/insignias/coherencia
    body: { criterio_tipo, criterio_operador, criterio_valor, nivel, id? }
    Devuelve advertencias de coherencia de dificultad por tier (no bloquea).
    """
    if request.method == 'OPTIONS':
        return build_cors_response()
    try:
        from src.models.colombia_data.ratings.negocio_badge import NegocioBadge
        from src.models.colombia_data.ratings.config_gamificacion import evaluar_coherencia_tier
        data = request.get_json(silent=True) or {}
        tipo = (data.get('criterio_tipo') or '').strip()
        op = (data.get('criterio_operador') or '>=').strip()
        try:
            valor = float(data.get('criterio_valor'))
            nivel = int(data.get('nivel'))
        except (TypeError, ValueError):
            return build_cors_response({'success': False, 'error': 'nivel/valor inválidos'}, 400)
        propio_id = data.get('id')

        otros = []
        for b in NegocioBadge.query.filter_by(criterio_tipo=tipo).all():
            if propio_id and b.id == propio_id:
                continue
            otros.append({'nivel': b.nivel, 'criterio_valor': b.criterio_valor,
                          'criterio_operador': b.criterio_operador, 'nombre': b.nombre})
        adv = evaluar_coherencia_tier(nivel, tipo, op, valor, otros)
        return build_cors_response({'success': True, 'coherente': len(adv) == 0,
                                    'advertencias': adv})
    except Exception as e:
        logger.error(f"Error en coherencia_insignia: {e}")
        return build_cors_response({'success': False, 'error': str(e), 'advertencias': []}, 200)


# ═══════════════════════════════════════════════════════════════════════════════
# INSIGNIAS — PROGRESO / OTORGAMIENTOS (Admin Panel A20)
# Distribución global por tier + estadísticas por insignia (quién la tiene, cercanía).
# ═══════════════════════════════════════════════════════════════════════════════

@admin_bp.route('/insignias/distribucion', methods=['GET'])
@requiere_permiso('insignias')
def insignias_distribucion():
    """GET /api/admin/insignias/distribucion → conteo de insignias y otorgamientos por tier."""
    try:
        conn = get_db_connection(); cur = conn.cursor()
        cur.execute("""
            SELECT nivel, COUNT(*) AS badges, COALESCE(SUM(total_otorgados),0) AS otorgados
            FROM negocio_badges GROUP BY nivel ORDER BY nivel
        """)
        por_tier = [{'tier': r['nivel'] or 1, 'badges': r['badges'], 'otorgados': int(r['otorgados'] or 0)}
                    for r in cur.fetchall()]
        cur.close(); conn.close()
        return build_cors_response({
            'success': True, 'por_tier': por_tier,
            'total_badges': sum(t['badges'] for t in por_tier),
            'total_otorgados': sum(t['otorgados'] for t in por_tier),
        })
    except Exception as e:
        logger.error(f"Error en insignias_distribucion: {e}")
        return build_cors_response({'success': False, 'error': str(e), 'por_tier': []}, 200)


@admin_bp.route('/insignias/<int:badge_id>/estadisticas', methods=['GET'])
@requiere_permiso('insignias')
def insignia_estadisticas(badge_id):
    """
    GET /api/admin/insignias/<id>/estadisticas → cuántos la tienen, últimos en obtenerla
    y ranking de cercanía (negocios sin ella, ordenados por % de progreso).
    """
    try:
        from src.models.colombia_data.ratings.negocio_badge import NegocioBadge
        from src.api.utils.badge_verification_service import BadgeVerificationService
        from src.models.colombia_data.ratings.negocio_gamificacion import NegocioGamificacion

        badge = NegocioBadge.query.get(badge_id)
        if not badge:
            return build_cors_response({'success': False, 'error': 'Insignia no encontrada'}, 404)

        total = int(_scalar_admin(
            "SELECT COUNT(*) AS v FROM negocio_badges_obtenidos WHERE badge_id=%s AND (activo IS TRUE OR activo IS NULL)",
            (badge_id,)))

        # Últimos en obtenerla
        recientes = []
        try:
            conn = get_db_connection(); cur = conn.cursor()
            cur.execute("""
                SELECT o.negocio_id, n.nombre_negocio, o.fecha_obtencion
                FROM negocio_badges_obtenidos o
                LEFT JOIN negocios n ON n.id_negocio = o.negocio_id
                WHERE o.badge_id=%s AND (o.activo IS TRUE OR o.activo IS NULL)
                ORDER BY o.fecha_obtencion DESC LIMIT 5
            """, (badge_id,))
            for r in cur.fetchall():
                recientes.append({'negocio_id': r['negocio_id'],
                                  'nombre': r['nombre_negocio'] or f"Negocio {r['negocio_id']}",
                                  'fecha': r['fecha_obtencion'].isoformat() if r['fecha_obtencion'] else None})
            cur.close(); conn.close()
        except Exception:
            pass

        # Ranking de cercanía (solo criterios numéricos acumulativos >=)
        cercanos, nota = [], None
        if badge.criterio_operador == '>=' and (badge.criterio_valor or 0) > 0 and not badge.es_secreto:
            objetivo = float(badge.criterio_valor)
            ya = set(int(x) for x in (_scalar_admin_list(
                "SELECT negocio_id FROM negocio_badges_obtenidos WHERE badge_id=%s AND (activo IS TRUE OR activo IS NULL)",
                (badge_id,)) or []))
            CAP = 800
            filas = (NegocioGamificacion.query.with_entities(NegocioGamificacion.negocio_id).limit(CAP).all())
            tmp = []
            for (nid,) in filas:
                if nid in ya:
                    continue
                try:
                    val = BadgeVerificationService._calcular_metricas_para_badges(nid).get(badge.criterio_tipo)
                    if val is None:
                        continue
                    val = float(val)
                    if val >= objetivo:
                        continue  # ya cumple (se otorgará solo)
                    pct = max(0.0, min(99.0, round(val / objetivo * 100, 1)))
                    tmp.append({'negocio_id': nid, 'actual': val, 'objetivo': objetivo,
                                'falta': round(objetivo - val, 2), 'pct': pct})
                except Exception:
                    continue
            tmp.sort(key=lambda x: x['pct'], reverse=True)
            cercanos = tmp[:10]
            # nombres
            for c in cercanos:
                c['nombre'] = (_scalar_admin("SELECT nombre_negocio AS v FROM negocios WHERE id_negocio=%s",
                                             (c['negocio_id'],)) or f"Negocio {c['negocio_id']}")
        else:
            nota = 'Ranking de cercanía solo disponible para criterios numéricos acumulativos (>=) no secretos.'

        return build_cors_response({
            'success': True, 'badge': _badge_admin_dict(badge),
            'total_otorgados': total, 'recientes': recientes,
            'cercanos': cercanos, 'nota': nota,
        })
    except Exception as e:
        logger.error(f"Error en insignia_estadisticas: {e}")
        return build_cors_response({'success': False, 'error': str(e)}, 200)


def _scalar_admin_list(sql, params):
    """Devuelve una lista de la primera columna (tolerante a fallos)."""
    try:
        conn = get_db_connection(); cur = conn.cursor()
        cur.execute(sql, params); rows = cur.fetchall(); cur.close(); conn.close()
        return [list(r.values())[0] for r in rows]
    except Exception:
        return []
