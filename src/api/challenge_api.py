"""
═══════════════════════════════════════════════════════════════════════════════
TUKOMERCIO CHALLENGE API
#MiNegocioEn15Segundos - Backend Completo
═══════════════════════════════════════════════════════════════════════════════

Endpoints para:
- Gestión de challenges (CRUD)
- Participaciones (videos del challenge)
- Sistema de votación
- Leaderboard en tiempo real
- Estadísticas y métricas

Autor: TuKomercio Team
Versión: 1.0.0
═══════════════════════════════════════════════════════════════════════════════
"""

from flask import Blueprint, request, jsonify, g
from functools import wraps
from datetime import datetime, timedelta
from decimal import Decimal
import json
import os

# ═══════════════════════════════════════════════════════════════════════════════
# BLUEPRINT SETUP
# ═══════════════════════════════════════════════════════════════════════════════

challenge_bp = Blueprint('challenge', __name__, url_prefix='/api/challenge')

# ═══════════════════════════════════════════════════════════════════════════════
# DATABASE CONNECTION (usar el existente de tu app)
# ═══════════════════════════════════════════════════════════════════════════════

def get_db_connection():
    """Obtener conexión a la base de datos."""
    import psycopg2
    from psycopg2.extras import RealDictCursor
    
    DATABASE_URL = os.environ.get('DATABASE_URL')
    conn = psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)
    return conn

# ═══════════════════════════════════════════════════════════════════════════════
# AUTH DECORATOR (usar el existente de tu app)
# ═══════════════════════════════════════════════════════════════════════════════

def token_required(f):
    """Decorator para endpoints que requieren autenticación."""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        
        if not token:
            return jsonify({'error': 'Token requerido'}), 401
        
        try:
            # Decodificar token JWT (usar tu implementación existente)
            import jwt
            SECRET_KEY = os.environ.get('SECRET_KEY', 'tu-secret-key')
            payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
            g.user_id = payload.get('user_id')
            g.negocio_id = payload.get('negocio_id')
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Token expirado'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'error': 'Token inválido'}), 401
        
        return f(*args, **kwargs)
    return decorated

def token_optional(f):
    """Decorator para endpoints donde el token es opcional."""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        
        g.user_id = None
        g.negocio_id = None
        
        if token:
            try:
                import jwt
                SECRET_KEY = os.environ.get('SECRET_KEY', 'tu-secret-key')
                payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
                g.user_id = payload.get('user_id')
                g.negocio_id = payload.get('negocio_id')
            except:
                pass
        
        return f(*args, **kwargs)
    return decorated

# ═══════════════════════════════════════════════════════════════════════════════
# CHALLENGE ENDPOINTS
# ═══════════════════════════════════════════════════════════════════════════════

@challenge_bp.route('/active', methods=['GET'])
def get_active_challenge():
    """
    GET /api/challenge/active
    Obtener el challenge activo actual.
    """
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        cur.execute("""
            SELECT 
                c.id,
                c.nombre,
                c.hashtag,
                c.descripcion,
                c.fecha_inicio,
                c.fecha_fin,
                c.premios_json,
                c.reglas_json,
                c.imagen_banner,
                c.video_promo_url,
                c.estado,
                c.max_participantes,
                c.max_videos_por_negocio,
                c.duracion_max_video,
                c.created_at,
                (SELECT COUNT(*) FROM challenge_participaciones WHERE challenge_id = c.id AND estado = 'aprobado') as total_participantes,
                (SELECT COALESCE(SUM(vistas), 0) FROM videos v 
                 JOIN challenge_participaciones cp ON v.id = cp.video_id 
                 WHERE cp.challenge_id = c.id) as total_vistas,
                (SELECT COALESCE(SUM(cv.votos), 0) FROM challenge_votos cv 
                 JOIN challenge_participaciones cp ON cv.participacion_id = cp.id 
                 WHERE cp.challenge_id = c.id) as total_votos
            FROM challenges c
            WHERE c.estado = 'activo'
            AND c.fecha_inicio <= NOW()
            AND c.fecha_fin >= NOW()
            ORDER BY c.fecha_inicio DESC
            LIMIT 1
        """)
        
        challenge = cur.fetchone()
        
        if not challenge:
            return jsonify({'error': 'No hay challenge activo actualmente'}), 404
        
        # Parsear JSON fields
        challenge = dict(challenge)
        challenge['premios'] = json.loads(challenge.pop('premios_json', '[]') or '[]')
        challenge['reglas'] = json.loads(challenge.pop('reglas_json', '[]') or '[]')
        
        # Calcular tiempo restante
        fecha_fin = challenge['fecha_fin']
        if isinstance(fecha_fin, str):
            fecha_fin = datetime.fromisoformat(fecha_fin)
        
        tiempo_restante = fecha_fin - datetime.now()
        challenge['tiempo_restante'] = {
            'dias': max(0, tiempo_restante.days),
            'horas': max(0, tiempo_restante.seconds // 3600),
            'minutos': max(0, (tiempo_restante.seconds % 3600) // 60),
            'segundos': max(0, tiempo_restante.seconds % 60),
            'total_segundos': max(0, int(tiempo_restante.total_seconds()))
        }
        
        # Cupos restantes
        challenge['cupos_restantes'] = max(0, (challenge.get('max_participantes') or 10000) - challenge['total_participantes'])
        
        cur.close()
        conn.close()
        
        return jsonify(challenge), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@challenge_bp.route('/<int:challenge_id>', methods=['GET'])
def get_challenge_details(challenge_id):
    """
    GET /api/challenge/<id>
    Obtener detalles de un challenge específico.
    """
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        cur.execute("""
            SELECT 
                c.*,
                (SELECT COUNT(*) FROM challenge_participaciones WHERE challenge_id = c.id AND estado = 'aprobado') as total_participantes,
                (SELECT COALESCE(SUM(vistas), 0) FROM videos v 
                 JOIN challenge_participaciones cp ON v.id = cp.video_id 
                 WHERE cp.challenge_id = c.id) as total_vistas
            FROM challenges c
            WHERE c.id = %s
        """, (challenge_id,))
        
        challenge = cur.fetchone()
        
        if not challenge:
            return jsonify({'error': 'Challenge no encontrado'}), 404
        
        challenge = dict(challenge)
        challenge['premios'] = json.loads(challenge.pop('premios_json', '[]') or '[]')
        challenge['reglas'] = json.loads(challenge.pop('reglas_json', '[]') or '[]')
        
        cur.close()
        conn.close()
        
        return jsonify(challenge), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ═══════════════════════════════════════════════════════════════════════════════
# PARTICIPACIONES ENDPOINTS
# ═══════════════════════════════════════════════════════════════════════════════

@challenge_bp.route('/participar', methods=['POST'])
@token_required
def participar_challenge():
    """
    POST /api/challenge/participar
    Registrar participación en el challenge.
    
    Body:
    {
        "challenge_id": 1,
        "video_id": 123,
        "negocio_id": 456  (opcional, usa el del token si no se envía)
    }
    """
    try:
        data = request.get_json()
        
        challenge_id = data.get('challenge_id')
        video_id = data.get('video_id')
        negocio_id = data.get('negocio_id') or g.negocio_id
        
        if not all([challenge_id, video_id, negocio_id]):
            return jsonify({'error': 'challenge_id, video_id y negocio_id son requeridos'}), 400
        
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Verificar que el challenge existe y está activo
        cur.execute("""
            SELECT id, estado, fecha_inicio, fecha_fin, max_participantes, max_videos_por_negocio, duracion_max_video
            FROM challenges
            WHERE id = %s
        """, (challenge_id,))
        
        challenge = cur.fetchone()
        
        if not challenge:
            return jsonify({'error': 'Challenge no encontrado'}), 404
        
        if challenge['estado'] != 'activo':
            return jsonify({'error': 'El challenge no está activo'}), 400
        
        now = datetime.now()
        if now < challenge['fecha_inicio']:
            return jsonify({'error': 'El challenge aún no ha comenzado'}), 400
        
        if now > challenge['fecha_fin']:
            return jsonify({'error': 'El challenge ya ha terminado'}), 400
        
        # Verificar cupos disponibles
        cur.execute("""
            SELECT COUNT(*) as total
            FROM challenge_participaciones
            WHERE challenge_id = %s AND estado = 'aprobado'
        """, (challenge_id,))
        
        total_participantes = cur.fetchone()['total']
        
        if challenge['max_participantes'] and total_participantes >= challenge['max_participantes']:
            return jsonify({'error': 'El challenge ha alcanzado el máximo de participantes'}), 400
        
        # Verificar videos por negocio
        cur.execute("""
            SELECT COUNT(*) as total
            FROM challenge_participaciones
            WHERE challenge_id = %s AND negocio_id = %s AND estado != 'rechazado'
        """, (challenge_id, negocio_id))
        
        videos_negocio = cur.fetchone()['total']
        max_videos = challenge['max_videos_por_negocio'] or 3
        
        if videos_negocio >= max_videos:
            return jsonify({'error': f'Ya has alcanzado el máximo de {max_videos} videos para este challenge'}), 400
        
        # Verificar que el video existe y pertenece al negocio
        cur.execute("""
            SELECT id, duracion, negocio_id
            FROM videos
            WHERE id = %s
        """, (video_id,))
        
        video = cur.fetchone()
        
        if not video:
            return jsonify({'error': 'Video no encontrado'}), 404
        
        if video['negocio_id'] != negocio_id:
            return jsonify({'error': 'El video no pertenece a tu negocio'}), 403
        
        # Verificar duración del video
        duracion_max = challenge['duracion_max_video'] or 15
        if video['duracion'] and video['duracion'] > duracion_max:
            return jsonify({'error': f'El video excede la duración máxima de {duracion_max} segundos'}), 400
        
        # Verificar que el video no esté ya participando
        cur.execute("""
            SELECT id FROM challenge_participaciones
            WHERE challenge_id = %s AND video_id = %s
        """, (challenge_id, video_id))
        
        if cur.fetchone():
            return jsonify({'error': 'Este video ya está participando en el challenge'}), 400
        
        # Crear participación
        cur.execute("""
            INSERT INTO challenge_participaciones 
            (challenge_id, video_id, negocio_id, usuario_id, estado, created_at)
            VALUES (%s, %s, %s, %s, 'aprobado', NOW())
            RETURNING id, created_at
        """, (challenge_id, video_id, negocio_id, g.user_id))
        
        participacion = cur.fetchone()
        
        # Marcar el video con el hashtag del challenge
        cur.execute("""
            UPDATE videos 
            SET hashtags = COALESCE(hashtags, '') || ' #MiNegocioEn15Segundos',
                challenge_id = %s
            WHERE id = %s
        """, (challenge_id, video_id))
        
        # Dar badge de participante al negocio
        cur.execute("""
            INSERT INTO negocio_badges (negocio_id, badge_id, fecha_obtencion)
            SELECT %s, b.id, NOW()
            FROM badges b
            WHERE b.codigo = 'challenge_participant_2026'
            AND NOT EXISTS (
                SELECT 1 FROM negocio_badges nb 
                WHERE nb.negocio_id = %s AND nb.badge_id = b.id
            )
        """, (negocio_id, negocio_id))
        
        # Dar XP al negocio
        cur.execute("""
            UPDATE negocios 
            SET xp_total = COALESCE(xp_total, 0) + 500
            WHERE id = %s
        """, (negocio_id,))
        
        conn.commit()
        cur.close()
        conn.close()
        
        return jsonify({
            'success': True,
            'message': '¡Felicidades! Tu video está participando en el challenge',
            'participacion_id': participacion['id'],
            'xp_ganado': 500,
            'badge_obtenido': 'Participante Challenge 2026'
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@challenge_bp.route('/mis-participaciones', methods=['GET'])
@token_required
def get_mis_participaciones():
    """
    GET /api/challenge/mis-participaciones
    Obtener las participaciones del usuario actual.
    """
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        cur.execute("""
            SELECT 
                cp.id,
                cp.challenge_id,
                cp.video_id,
                cp.estado,
                cp.created_at,
                c.nombre as challenge_nombre,
                c.hashtag,
                v.titulo as video_titulo,
                v.thumbnail_url,
                v.vistas,
                (SELECT COUNT(*) FROM challenge_votos WHERE participacion_id = cp.id) as total_votos,
                (SELECT rank FROM (
                    SELECT cp2.id, RANK() OVER (ORDER BY COUNT(cv.id) DESC) as rank
                    FROM challenge_participaciones cp2
                    LEFT JOIN challenge_votos cv ON cv.participacion_id = cp2.id
                    WHERE cp2.challenge_id = cp.challenge_id AND cp2.estado = 'aprobado'
                    GROUP BY cp2.id
                ) ranked WHERE ranked.id = cp.id) as posicion
            FROM challenge_participaciones cp
            JOIN challenges c ON c.id = cp.challenge_id
            JOIN videos v ON v.id = cp.video_id
            WHERE cp.negocio_id = %s
            ORDER BY cp.created_at DESC
        """, (g.negocio_id,))
        
        participaciones = cur.fetchall()
        
        cur.close()
        conn.close()
        
        return jsonify([dict(p) for p in participaciones]), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ═══════════════════════════════════════════════════════════════════════════════
# VOTACIÓN ENDPOINTS
# ═══════════════════════════════════════════════════════════════════════════════

@challenge_bp.route('/votar', methods=['POST'])
@token_required
def votar_participacion():
    """
    POST /api/challenge/votar
    Votar por una participación.
    
    Body:
    {
        "participacion_id": 123
    }
    """
    try:
        data = request.get_json()
        participacion_id = data.get('participacion_id')
        
        if not participacion_id:
            return jsonify({'error': 'participacion_id es requerido'}), 400
        
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Verificar que la participación existe y está aprobada
        cur.execute("""
            SELECT cp.id, cp.negocio_id, cp.challenge_id, c.estado as challenge_estado
            FROM challenge_participaciones cp
            JOIN challenges c ON c.id = cp.challenge_id
            WHERE cp.id = %s
        """, (participacion_id,))
        
        participacion = cur.fetchone()
        
        if not participacion:
            return jsonify({'error': 'Participación no encontrada'}), 404
        
        if participacion['challenge_estado'] != 'activo':
            return jsonify({'error': 'El challenge no está activo'}), 400
        
        # No puedes votar por tu propio negocio
        if participacion['negocio_id'] == g.negocio_id:
            return jsonify({'error': 'No puedes votar por tu propio video'}), 400
        
        # Verificar si ya votó
        cur.execute("""
            SELECT id FROM challenge_votos
            WHERE participacion_id = %s AND usuario_id = %s
        """, (participacion_id, g.user_id))
        
        voto_existente = cur.fetchone()
        
        if voto_existente:
            # Quitar voto
            cur.execute("""
                DELETE FROM challenge_votos
                WHERE id = %s
            """, (voto_existente['id'],))
            
            conn.commit()
            cur.close()
            conn.close()
            
            return jsonify({
                'success': True,
                'action': 'removed',
                'message': 'Voto eliminado'
            }), 200
        else:
            # Agregar voto
            cur.execute("""
                INSERT INTO challenge_votos (participacion_id, usuario_id, created_at)
                VALUES (%s, %s, NOW())
                RETURNING id
            """, (participacion_id, g.user_id))
            
            voto = cur.fetchone()
            
            # Dar XP al que vota
            cur.execute("""
                UPDATE usuarios 
                SET xp_total = COALESCE(xp_total, 0) + 5
                WHERE id = %s
            """, (g.user_id,))
            
            conn.commit()
            cur.close()
            conn.close()
            
            return jsonify({
                'success': True,
                'action': 'added',
                'message': '¡Voto registrado!',
                'voto_id': voto['id'],
                'xp_ganado': 5
            }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@challenge_bp.route('/mis-votos', methods=['GET'])
@token_required
def get_mis_votos():
    """
    GET /api/challenge/mis-votos
    Obtener los IDs de participaciones que el usuario ha votado.
    """
    try:
        challenge_id = request.args.get('challenge_id')
        
        conn = get_db_connection()
        cur = conn.cursor()
        
        query = """
            SELECT cv.participacion_id
            FROM challenge_votos cv
            JOIN challenge_participaciones cp ON cp.id = cv.participacion_id
            WHERE cv.usuario_id = %s
        """
        params = [g.user_id]
        
        if challenge_id:
            query += " AND cp.challenge_id = %s"
            params.append(challenge_id)
        
        cur.execute(query, params)
        votos = [row['participacion_id'] for row in cur.fetchall()]
        
        cur.close()
        conn.close()
        
        return jsonify(votos), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ═══════════════════════════════════════════════════════════════════════════════
# LEADERBOARD ENDPOINTS
# ═══════════════════════════════════════════════════════════════════════════════

@challenge_bp.route('/leaderboard', methods=['GET'])
@token_optional
def get_leaderboard():
    """
    GET /api/challenge/leaderboard
    Obtener el leaderboard del challenge.
    
    Query params:
    - challenge_id: ID del challenge (opcional, usa el activo por defecto)
    - period: 'today', 'week', 'all' (default: 'all')
    - limit: número de resultados (default: 50)
    - offset: para paginación (default: 0)
    """
    try:
        challenge_id = request.args.get('challenge_id', type=int)
        period = request.args.get('period', 'all')
        limit = min(request.args.get('limit', 50, type=int), 100)
        offset = request.args.get('offset', 0, type=int)
        
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Si no se especifica challenge_id, usar el activo
        if not challenge_id:
            cur.execute("""
                SELECT id FROM challenges
                WHERE estado = 'activo'
                AND fecha_inicio <= NOW()
                AND fecha_fin >= NOW()
                ORDER BY fecha_inicio DESC
                LIMIT 1
            """)
            result = cur.fetchone()
            if result:
                challenge_id = result['id']
            else:
                return jsonify({'error': 'No hay challenge activo'}), 404
        
        # Filtro de período
        period_filter = ""
        if period == 'today':
            period_filter = "AND cv.created_at >= CURRENT_DATE"
        elif period == 'week':
            period_filter = "AND cv.created_at >= CURRENT_DATE - INTERVAL '7 days'"
        
        # Query del leaderboard
        cur.execute(f"""
            WITH votos_count AS (
                SELECT 
                    cp.id as participacion_id,
                    COUNT(cv.id) as votos
                FROM challenge_participaciones cp
                LEFT JOIN challenge_votos cv ON cv.participacion_id = cp.id {period_filter}
                WHERE cp.challenge_id = %s AND cp.estado = 'aprobado'
                GROUP BY cp.id
            ),
            ranked AS (
                SELECT 
                    cp.id as participacion_id,
                    cp.video_id,
                    cp.negocio_id,
                    cp.created_at as fecha_participacion,
                    v.titulo as video_titulo,
                    v.thumbnail_url,
                    v.vistas,
                    v.duracion,
                    n.nombre as negocio_nombre,
                    n.logo_url as negocio_logo,
                    n.categoria,
                    n.verificado,
                    COALESCE(vc.votos, 0) as total_votos,
                    RANK() OVER (ORDER BY COALESCE(vc.votos, 0) DESC, cp.created_at ASC) as posicion,
                    LAG(RANK() OVER (ORDER BY COALESCE(vc.votos, 0) DESC)) OVER (ORDER BY COALESCE(vc.votos, 0) DESC) as posicion_anterior
                FROM challenge_participaciones cp
                JOIN videos v ON v.id = cp.video_id
                JOIN negocios n ON n.id = cp.negocio_id
                LEFT JOIN votos_count vc ON vc.participacion_id = cp.id
                WHERE cp.challenge_id = %s AND cp.estado = 'aprobado'
            )
            SELECT 
                *,
                CASE 
                    WHEN posicion_anterior IS NULL THEN 'new'
                    WHEN posicion < posicion_anterior THEN 'up'
                    WHEN posicion > posicion_anterior THEN 'down'
                    ELSE 'same'
                END as cambio_posicion
            FROM ranked
            ORDER BY posicion ASC
            LIMIT %s OFFSET %s
        """, (challenge_id, challenge_id, limit, offset))
        
        leaderboard = cur.fetchall()
        
        # Obtener total de participantes
        cur.execute("""
            SELECT COUNT(*) as total
            FROM challenge_participaciones
            WHERE challenge_id = %s AND estado = 'aprobado'
        """, (challenge_id,))
        
        total = cur.fetchone()['total']
        
        # Si el usuario está logueado, obtener su posición
        mi_posicion = None
        if g.negocio_id:
            cur.execute(f"""
                WITH votos_count AS (
                    SELECT 
                        cp.id as participacion_id,
                        COUNT(cv.id) as votos
                    FROM challenge_participaciones cp
                    LEFT JOIN challenge_votos cv ON cv.participacion_id = cp.id {period_filter}
                    WHERE cp.challenge_id = %s AND cp.estado = 'aprobado'
                    GROUP BY cp.id
                ),
                ranked AS (
                    SELECT 
                        cp.negocio_id,
                        RANK() OVER (ORDER BY COALESCE(vc.votos, 0) DESC) as posicion,
                        COALESCE(vc.votos, 0) as votos
                    FROM challenge_participaciones cp
                    LEFT JOIN votos_count vc ON vc.participacion_id = cp.id
                    WHERE cp.challenge_id = %s AND cp.estado = 'aprobado'
                )
                SELECT posicion, votos
                FROM ranked
                WHERE negocio_id = %s
                ORDER BY posicion ASC
                LIMIT 1
            """, (challenge_id, challenge_id, g.negocio_id))
            
            mi_result = cur.fetchone()
            if mi_result:
                mi_posicion = dict(mi_result)
        
        cur.close()
        conn.close()
        
        return jsonify({
            'challenge_id': challenge_id,
            'period': period,
            'leaderboard': [dict(row) for row in leaderboard],
            'total_participantes': total,
            'mi_posicion': mi_posicion,
            'pagination': {
                'limit': limit,
                'offset': offset,
                'has_more': offset + limit < total
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@challenge_bp.route('/leaderboard/live', methods=['GET'])
def get_leaderboard_live():
    """
    GET /api/challenge/leaderboard/live
    Endpoint optimizado para actualizaciones en tiempo real.
    Devuelve solo posición, votos y cambios.
    """
    try:
        challenge_id = request.args.get('challenge_id', type=int)
        
        conn = get_db_connection()
        cur = conn.cursor()
        
        if not challenge_id:
            cur.execute("""
                SELECT id FROM challenges
                WHERE estado = 'activo' AND fecha_inicio <= NOW() AND fecha_fin >= NOW()
                LIMIT 1
            """)
            result = cur.fetchone()
            challenge_id = result['id'] if result else None
        
        if not challenge_id:
            return jsonify({'error': 'No hay challenge activo'}), 404
        
        cur.execute("""
            SELECT 
                cp.id as participacion_id,
                cp.negocio_id,
                n.nombre as negocio_nombre,
                COUNT(cv.id) as votos,
                RANK() OVER (ORDER BY COUNT(cv.id) DESC) as posicion
            FROM challenge_participaciones cp
            JOIN negocios n ON n.id = cp.negocio_id
            LEFT JOIN challenge_votos cv ON cv.participacion_id = cp.id
            WHERE cp.challenge_id = %s AND cp.estado = 'aprobado'
            GROUP BY cp.id, cp.negocio_id, n.nombre
            ORDER BY votos DESC
            LIMIT 20
        """, (challenge_id,))
        
        leaderboard = cur.fetchall()
        
        # Stats generales
        cur.execute("""
            SELECT 
                COUNT(DISTINCT cp.id) as total_videos,
                COUNT(DISTINCT cp.negocio_id) as total_negocios,
                COALESCE(SUM(v.vistas), 0) as total_vistas,
                COUNT(cv.id) as total_votos
            FROM challenge_participaciones cp
            JOIN videos v ON v.id = cp.video_id
            LEFT JOIN challenge_votos cv ON cv.participacion_id = cp.id
            WHERE cp.challenge_id = %s AND cp.estado = 'aprobado'
        """, (challenge_id,))
        
        stats = cur.fetchone()
        
        cur.close()
        conn.close()
        
        return jsonify({
            'timestamp': datetime.now().isoformat(),
            'leaderboard': [dict(row) for row in leaderboard],
            'stats': dict(stats)
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ═══════════════════════════════════════════════════════════════════════════════
# VIDEOS DEL CHALLENGE
# ═══════════════════════════════════════════════════════════════════════════════

@challenge_bp.route('/videos', methods=['GET'])
@token_optional
def get_challenge_videos():
    """
    GET /api/challenge/videos
    Obtener videos del challenge con filtros.
    
    Query params:
    - challenge_id: ID del challenge
    - filter: 'trending', 'recent', 'top', 'creative', 'near'
    - limit: número de resultados
    - offset: para paginación
    - lat, lng: coordenadas para filtro 'near'
    """
    try:
        challenge_id = request.args.get('challenge_id', type=int)
        filter_type = request.args.get('filter', 'trending')
        limit = min(request.args.get('limit', 12, type=int), 50)
        offset = request.args.get('offset', 0, type=int)
        lat = request.args.get('lat', type=float)
        lng = request.args.get('lng', type=float)
        
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Obtener challenge activo si no se especifica
        if not challenge_id:
            cur.execute("""
                SELECT id FROM challenges
                WHERE estado = 'activo' AND fecha_inicio <= NOW() AND fecha_fin >= NOW()
                LIMIT 1
            """)
            result = cur.fetchone()
            challenge_id = result['id'] if result else None
        
        if not challenge_id:
            return jsonify({'error': 'No hay challenge activo'}), 404
        
        # Base query
        base_query = """
            SELECT 
                cp.id as participacion_id,
                cp.video_id,
                cp.negocio_id,
                cp.created_at as fecha_participacion,
                v.titulo,
                v.descripcion,
                v.video_url,
                v.thumbnail_url,
                v.duracion,
                v.vistas,
                v.likes,
                n.nombre as negocio_nombre,
                n.logo_url as negocio_logo,
                n.categoria,
                n.verificado,
                n.latitud,
                n.longitud,
                COUNT(cv.id) as votos,
                COUNT(c.id) as comentarios,
                RANK() OVER (ORDER BY COUNT(cv.id) DESC) as posicion,
                {user_voted}
            FROM challenge_participaciones cp
            JOIN videos v ON v.id = cp.video_id
            JOIN negocios n ON n.id = cp.negocio_id
            LEFT JOIN challenge_votos cv ON cv.participacion_id = cp.id
            LEFT JOIN comentarios c ON c.video_id = v.id
            WHERE cp.challenge_id = %s AND cp.estado = 'aprobado'
            GROUP BY cp.id, v.id, n.id
        """
        
        # User voted subquery
        if g.user_id:
            user_voted = f"EXISTS(SELECT 1 FROM challenge_votos WHERE participacion_id = cp.id AND usuario_id = {g.user_id}) as votado"
        else:
            user_voted = "FALSE as votado"
        
        base_query = base_query.format(user_voted=user_voted)
        
        # Order by según filtro
        order_by = ""
        if filter_type == 'trending':
            # Trending: combinación de votos recientes + vistas
            order_by = """
                ORDER BY (
                    (SELECT COUNT(*) FROM challenge_votos 
                     WHERE participacion_id = cp.id 
                     AND created_at >= NOW() - INTERVAL '24 hours') * 2 
                    + v.vistas / 1000
                ) DESC
            """
        elif filter_type == 'recent':
            order_by = "ORDER BY cp.created_at DESC"
        elif filter_type == 'top':
            order_by = "ORDER BY votos DESC, v.vistas DESC"
        elif filter_type == 'creative':
            # Creative: más comentarios y engagement
            order_by = "ORDER BY (COUNT(c.id) + COUNT(cv.id)) DESC"
        elif filter_type == 'near' and lat and lng:
            # Near: por distancia geográfica
            order_by = f"""
                ORDER BY (
                    6371 * acos(
                        cos(radians({lat})) * cos(radians(n.latitud)) *
                        cos(radians(n.longitud) - radians({lng})) +
                        sin(radians({lat})) * sin(radians(n.latitud))
                    )
                ) ASC
            """
        else:
            order_by = "ORDER BY votos DESC"
        
        final_query = base_query + order_by + f" LIMIT {limit} OFFSET {offset}"
        
        cur.execute(final_query, (challenge_id,))
        videos = cur.fetchall()
        
        # Total
        cur.execute("""
            SELECT COUNT(*) as total
            FROM challenge_participaciones
            WHERE challenge_id = %s AND estado = 'aprobado'
        """, (challenge_id,))
        
        total = cur.fetchone()['total']
        
        cur.close()
        conn.close()
        
        return jsonify({
            'videos': [dict(v) for v in videos],
            'total': total,
            'filter': filter_type,
            'pagination': {
                'limit': limit,
                'offset': offset,
                'has_more': offset + limit < total
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ═══════════════════════════════════════════════════════════════════════════════
# ESTADÍSTICAS
# ═══════════════════════════════════════════════════════════════════════════════

@challenge_bp.route('/stats', methods=['GET'])
def get_challenge_stats():
    """
    GET /api/challenge/stats
    Estadísticas generales del challenge.
    """
    try:
        challenge_id = request.args.get('challenge_id', type=int)
        
        conn = get_db_connection()
        cur = conn.cursor()
        
        if not challenge_id:
            cur.execute("""
                SELECT id FROM challenges
                WHERE estado = 'activo' AND fecha_inicio <= NOW() AND fecha_fin >= NOW()
                LIMIT 1
            """)
            result = cur.fetchone()
            challenge_id = result['id'] if result else None
        
        if not challenge_id:
            return jsonify({'error': 'No hay challenge activo'}), 404
        
        # Stats principales
        cur.execute("""
            SELECT 
                COUNT(DISTINCT cp.id) as total_videos,
                COUNT(DISTINCT cp.negocio_id) as total_negocios,
                COALESCE(SUM(v.vistas), 0) as total_vistas,
                (SELECT COUNT(*) FROM challenge_votos cv2 
                 JOIN challenge_participaciones cp2 ON cp2.id = cv2.participacion_id 
                 WHERE cp2.challenge_id = %s) as total_votos,
                COALESCE(AVG(v.duracion), 0) as duracion_promedio
            FROM challenge_participaciones cp
            JOIN videos v ON v.id = cp.video_id
            WHERE cp.challenge_id = %s AND cp.estado = 'aprobado'
        """, (challenge_id, challenge_id))
        
        stats = dict(cur.fetchone())
        
        # Top categorías
        cur.execute("""
            SELECT n.categoria, COUNT(*) as cantidad
            FROM challenge_participaciones cp
            JOIN negocios n ON n.id = cp.negocio_id
            WHERE cp.challenge_id = %s AND cp.estado = 'aprobado'
            GROUP BY n.categoria
            ORDER BY cantidad DESC
            LIMIT 5
        """, (challenge_id,))
        
        stats['top_categorias'] = [dict(row) for row in cur.fetchall()]
        
        # Participantes por día
        cur.execute("""
            SELECT 
                DATE(created_at) as fecha,
                COUNT(*) as nuevos_participantes
            FROM challenge_participaciones
            WHERE challenge_id = %s AND estado = 'aprobado'
            GROUP BY DATE(created_at)
            ORDER BY fecha DESC
            LIMIT 14
        """, (challenge_id,))
        
        stats['participantes_por_dia'] = [dict(row) for row in cur.fetchall()]
        
        # Votos por hora (últimas 24h)
        cur.execute("""
            SELECT 
                DATE_TRUNC('hour', cv.created_at) as hora,
                COUNT(*) as votos
            FROM challenge_votos cv
            JOIN challenge_participaciones cp ON cp.id = cv.participacion_id
            WHERE cp.challenge_id = %s
            AND cv.created_at >= NOW() - INTERVAL '24 hours'
            GROUP BY DATE_TRUNC('hour', cv.created_at)
            ORDER BY hora DESC
        """, (challenge_id,))
        
        stats['votos_por_hora'] = [dict(row) for row in cur.fetchall()]
        
        cur.close()
        conn.close()
        
        return jsonify(stats), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ═══════════════════════════════════════════════════════════════════════════════
# ADMIN ENDPOINTS (para gestión interna)
# ═══════════════════════════════════════════════════════════════════════════════

@challenge_bp.route('/admin/create', methods=['POST'])
@token_required
def create_challenge():
    """
    POST /api/challenge/admin/create
    Crear un nuevo challenge (solo admins).
    """
    try:
        # TODO: Verificar que el usuario es admin
        data = request.get_json()
        
        required_fields = ['nombre', 'hashtag', 'fecha_inicio', 'fecha_fin']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'{field} es requerido'}), 400
        
        conn = get_db_connection()
        cur = conn.cursor()
        
        cur.execute("""
            INSERT INTO challenges (
                nombre, hashtag, descripcion, fecha_inicio, fecha_fin,
                premios_json, reglas_json, imagen_banner, video_promo_url,
                estado, max_participantes, max_videos_por_negocio, duracion_max_video,
                created_at
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW()
            )
            RETURNING id
        """, (
            data.get('nombre'),
            data.get('hashtag'),
            data.get('descripcion'),
            data.get('fecha_inicio'),
            data.get('fecha_fin'),
            json.dumps(data.get('premios', [])),
            json.dumps(data.get('reglas', [])),
            data.get('imagen_banner'),
            data.get('video_promo_url'),
            data.get('estado', 'borrador'),
            data.get('max_participantes', 10000),
            data.get('max_videos_por_negocio', 3),
            data.get('duracion_max_video', 15)
        ))
        
        challenge = cur.fetchone()
        
        conn.commit()
        cur.close()
        conn.close()
        
        return jsonify({
            'success': True,
            'challenge_id': challenge['id']
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ═══════════════════════════════════════════════════════════════════════════════
# REGISTRAR BLUEPRINT
# ═══════════════════════════════════════════════════════════════════════════════

def register_challenge_api(app):
    """Registrar el blueprint del challenge en la app Flask."""
    app.register_blueprint(challenge_bp)
    print("✅ Challenge API registrada: /api/challenge/*")