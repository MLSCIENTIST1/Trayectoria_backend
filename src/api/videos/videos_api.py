"""
═══════════════════════════════════════════════════════════════════════════════
TUKOMERCIO - API FEED DE VIDEOS
Endpoint para scroll infinito de videos con badges y métricas
v2.2 - Con métricas automáticas calculadas desde contratos
═══════════════════════════════════════════════════════════════════════════════
"""

from flask import Blueprint, request, jsonify
from datetime import datetime, timedelta
from src.models.database import db
from sqlalchemy import text
import uuid

# Importar servicio de métricas
try:
    from src.api.utils.metricas_service import MetricasService, NOMBRES_METRICAS
    METRICAS_SERVICE_AVAILABLE = True
except ImportError:
    METRICAS_SERVICE_AVAILABLE = False
    NOMBRES_METRICAS = {}
    print("⚠️ MetricasService no disponible, usando métricas manuales")

# Crear Blueprint
videos_api = Blueprint('videos_api', __name__)

# ═══════════════════════════════════════════════════════════════════════════════
# CORS CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════════
ALLOWED_ORIGINS = [
    "https://tuko.pages.dev",
    "https://tukomercio.pages.dev",
    "https://trayectoria-rxdc1.web.app",
    "http://localhost:3000",
    "http://127.0.0.1:5500",
    "http://localhost:5500"
]

@videos_api.before_request
def handle_preflight():
    """Maneja las peticiones OPTIONS (preflight CORS)"""
    if request.method == 'OPTIONS':
        origin = request.headers.get('Origin', '')
        response = jsonify({'status': 'ok'})
        
        if origin in ALLOWED_ORIGINS or origin.endswith('.pages.dev'):
            response.headers['Access-Control-Allow-Origin'] = origin
        else:
            response.headers['Access-Control-Allow-Origin'] = ALLOWED_ORIGINS[0]
        
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, X-Session-ID, X-User-ID'
        response.headers['Access-Control-Allow-Credentials'] = 'true'
        response.headers['Access-Control-Max-Age'] = '3600'
        
        return response, 200

@videos_api.after_request
def add_cors_headers(response):
    """Agrega headers CORS a todas las respuestas"""
    origin = request.headers.get('Origin', '')
    
    if origin in ALLOWED_ORIGINS or origin.endswith('.pages.dev'):
        response.headers['Access-Control-Allow-Origin'] = origin
    else:
        response.headers['Access-Control-Allow-Origin'] = ALLOWED_ORIGINS[0]
    
    response.headers['Access-Control-Allow-Credentials'] = 'true'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, X-Session-ID, X-User-ID'
    
    return response

# ═══════════════════════════════════════════════════════════════════════════════
# TIPOS DE REACCIONES VÁLIDAS
# ═══════════════════════════════════════════════════════════════════════════════
VALID_REACTIONS = ['fuego', 'profesional', 'inspirador', 'loquiero', 'crack', 'wow']

# ═══════════════════════════════════════════════════════════════════════════════
# TIPOS DE MÉTRICAS VÁLIDAS
# ═══════════════════════════════════════════════════════════════════════════════
VALID_METRICA_TIPOS = [
    'tasa_exito', 'satisfaccion', 'clientes_recurrentes', 
    'tiempo_respuesta', 'proyectos_completados', 'años_experiencia',
    'entregas_anticipadas', 'mejor_precio', 'ninguna'
]


# ═══════════════════════════════════════════════════════════════════════════════
# HELPER: OBTENER IDENTIFICADOR DE USUARIO
# ═══════════════════════════════════════════════════════════════════════════════
def get_user_identifier():
    """
    Obtiene el identificador del usuario.
    Prioriza X-User-ID (usuario autenticado) sobre X-Session-ID (anónimo).
    Returns: tuple (user_id, session_id) - uno será None
    """
    user_id = request.headers.get('X-User-ID')
    session_id = request.headers.get('X-Session-ID') or request.cookies.get('session_id')
    
    # Validar que user_id sea numérico
    if user_id:
        try:
            user_id = int(user_id)
        except (ValueError, TypeError):
            user_id = None
    
    return user_id, session_id


def get_user_reaction_for_video(video_id, user_id, session_id):
    """
    Obtiene la reacción del usuario para un video específico.
    Prioriza usuario_id sobre session_id.
    """
    user_reaction = None
    
    if user_id:
        # Usuario autenticado - buscar por usuario_id
        ur_result = db.session.execute(text("""
            SELECT tipo_reaccion FROM video_reacciones 
            WHERE video_id = :video_id AND usuario_id = :user_id
            LIMIT 1
        """), {'video_id': video_id, 'user_id': user_id})
        ur_row = ur_result.fetchone()
        if ur_row:
            user_reaction = ur_row[0]
    elif session_id:
        # Usuario anónimo - buscar por session_id
        ur_result = db.session.execute(text("""
            SELECT tipo_reaccion FROM video_reacciones 
            WHERE video_id = :video_id AND session_id = :session_id
            LIMIT 1
        """), {'video_id': video_id, 'session_id': session_id})
        ur_row = ur_result.fetchone()
        if ur_row:
            user_reaction = ur_row[0]
    
    return user_reaction


# ═══════════════════════════════════════════════════════════════════════════════
# HELPER: OBTENER MÉTRICA PARA VIDEO
# ═══════════════════════════════════════════════════════════════════════════════
def get_metrica_para_video(negocio_id, metrica_tipo, metrica_manual=None):
    """
    Obtiene la métrica a mostrar en un video.
    
    Prioridad:
    1. Si metrica_tipo está definido y el servicio está disponible → calcular
    2. Si hay métrica manual → usar manual
    3. Default → vacío
    
    Args:
        negocio_id: ID del negocio
        metrica_tipo: Tipo de métrica a calcular (tasa_exito, satisfaccion, etc.)
        metrica_manual: Dict con {nombre, valor, tendencia} manuales (fallback)
    
    Returns:
        dict con nombre, valor, tendencia
    """
    # Si no quiere mostrar métrica
    if metrica_tipo == 'ninguna':
        return None
    
    # Intentar calcular métrica automática
    if metrica_tipo and metrica_tipo in VALID_METRICA_TIPOS and METRICAS_SERVICE_AVAILABLE:
        try:
            metrica = MetricasService.get_metrica_para_video(negocio_id, metrica_tipo)
            if metrica and metrica.get('valor') != '---':
                return metrica
        except Exception as e:
            print(f"⚠️ Error calculando métrica: {e}")
    
    # Fallback a métrica manual si existe
    if metrica_manual and metrica_manual.get('valor'):
        return metrica_manual
    
    # Default vacío
    return {
        'nombre': 'Rendimiento',
        'valor': '---',
        'tendencia': 'neutral'
    }


# ═══════════════════════════════════════════════════════════════════════════════
# ENDPOINT: GET /api/videos/feed
# ═══════════════════════════════════════════════════════════════════════════════
@videos_api.route('/feed', methods=['GET'])
def get_video_feed():
    """Obtiene el feed de videos con scroll infinito"""
    try:
        page = request.args.get('page', 1, type=int)
        limit = min(request.args.get('limit', 10, type=int), 20)
        tab = request.args.get('tab', 'para-ti')
        category = request.args.get('category', '')
        city = request.args.get('city', '')
        
        offset = (page - 1) * limit
        
        # Obtener identificador del usuario para user_reaction
        user_id, session_id = get_user_identifier()
        
        # Query base - ahora incluye metrica_tipo
        query = """
            SELECT 
                v.id, v.titulo, v.descripcion, v.url_video, v.url_thumbnail,
                v.duracion_segundos, v.calidad, v.vistas, v.likes, v.fecha_creacion,
                v.metrica_nombre, v.metrica_valor, v.metrica_tendencia,
                v.mostrar_badges, v.badges_ids,
                n.id_negocio as negocio_id, n.nombre_negocio, n.slug, n.logo_url,
                n.categoria, n.verificado, n.ciudad,
                v.metrica_tipo
            FROM negocio_videos v
            JOIN negocios n ON v.negocio_id = n.id_negocio
            WHERE v.visible = true AND n.activo = true
        """
        
        params = {}
        
        if category:
            query += " AND LOWER(n.categoria) = LOWER(:category)"
            params['category'] = category
        
        if city:
            query += " AND LOWER(n.ciudad) = LOWER(:city)"
            params['city'] = city
        
        if tab == 'tendencias':
            query += " ORDER BY v.vistas DESC, v.likes DESC"
        elif tab == 'nuevos':
            query += " ORDER BY v.fecha_creacion DESC"
        else:
            query += " ORDER BY v.fecha_creacion DESC"
        
        query += " LIMIT :limit OFFSET :offset"
        params['limit'] = limit
        params['offset'] = offset
        
        result = db.session.execute(text(query), params)
        rows = result.fetchall()
        
        # Cache de métricas por negocio (evitar recalcular)
        metricas_cache = {}
        
        videos = []
        for row in rows:
            video_id = row[0]
            negocio_id = row[15]
            mostrar_badges = row[13]
            badges_ids = row[14]
            metrica_tipo = row[22] if len(row) > 22 else None  # Nuevo campo
            
            # Obtener badges
            badges = []
            if mostrar_badges is not False:
                badge_result = db.session.execute(text("""
                    SELECT b.id, b.nombre, b.descripcion, b.icono, b.color
                    FROM negocio_badges_obtenidos nb
                    JOIN negocio_badges b ON nb.badge_id = b.id
                    WHERE nb.negocio_id = :negocio_id AND nb.activo = true LIMIT 3
                """), {'negocio_id': negocio_id})
                
                for badge_row in badge_result.fetchall():
                    badges.append({
                        'id': badge_row[0], 'nombre': badge_row[1],
                        'descripcion': badge_row[2], 'icono': badge_row[3], 'color': badge_row[4]
                    })
            
            # Obtener conteos de reacciones
            reactions_result = db.session.execute(text("""
                SELECT tipo_reaccion, COUNT(*) FROM video_reacciones
                WHERE video_id = :video_id GROUP BY tipo_reaccion
            """), {'video_id': video_id})
            reactions = {r: 0 for r in VALID_REACTIONS}
            for r_row in reactions_result.fetchall():
                if r_row[0] in VALID_REACTIONS:
                    reactions[r_row[0]] = r_row[1]
            
            # Obtener user_reaction
            user_reaction = get_user_reaction_for_video(video_id, user_id, session_id)
            
            # ═══════════════════════════════════════════════════════════════
            # NUEVO: Obtener métrica (automática o manual)
            # ═══════════════════════════════════════════════════════════════
            metrica_manual = {
                'nombre': row[10] or 'Rendimiento',
                'valor': row[11] or '---',
                'tendencia': row[12] or 'neutral'
            }
            
            metrica = get_metrica_para_video(negocio_id, metrica_tipo, metrica_manual)
            
            videos.append({
                'id': video_id,
                'titulo': row[1],
                'descripcion': row[2],
                'video_url': row[3],
                'thumbnail': row[4],
                'duracion_segundos': row[5],
                'calidad': row[6] or 'HD',
                'vistas': row[7] or 0,
                'likes': row[8] or 0,
                'fecha': row[9].isoformat() if row[9] else None,
                'negocio': {
                    'id': negocio_id,
                    'nombre': row[16],
                    'slug': row[17],
                    'logo_url': row[18],
                    'categoria': row[19],
                    'verificado': row[20] or False,
                    'ubicacion': row[21]
                },
                'badges': badges,
                'mostrar_badges': mostrar_badges if mostrar_badges is not None else True,
                'metrica': metrica,
                'metrica_tipo': metrica_tipo,  # Para debug/frontend
                'reactions': reactions,
                'user_reaction': user_reaction
            })
        
        # Contar total
        count_result = db.session.execute(text("SELECT COUNT(*) FROM negocio_videos WHERE visible = true"))
        total = count_result.scalar()
        
        return jsonify({
            'success': True,
            'data': {
                'videos': videos,
                'pagination': {
                    'page': page,
                    'limit': limit,
                    'total': total,
                    'has_more': offset + len(videos) < total
                }
            }
        })
        
    except Exception as e:
        print(f"❌ Error en feed: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500


# ═══════════════════════════════════════════════════════════════════════════════
# ENDPOINT: GET /api/videos/<id>
# ═══════════════════════════════════════════════════════════════════════════════
@videos_api.route('/<int:video_id>', methods=['GET'])
def get_video(video_id):
    """Obtiene un video específico por ID"""
    try:
        # Obtener identificador del usuario
        user_id, session_id = get_user_identifier()
        
        result = db.session.execute(text("""
            SELECT 
                v.id, v.titulo, v.descripcion, v.url_video, v.url_thumbnail,
                v.duracion_segundos, v.calidad, v.vistas, v.likes, v.fecha_creacion,
                v.metrica_nombre, v.metrica_valor, v.metrica_tendencia,
                n.id_negocio, n.nombre_negocio, n.slug, n.logo_url, n.categoria, n.verificado, n.ciudad,
                v.metrica_tipo
            FROM negocio_videos v
            JOIN negocios n ON v.negocio_id = n.id_negocio
            WHERE v.id = :video_id AND v.visible = true
        """), {'video_id': video_id})
        
        row = result.fetchone()
        
        if not row:
            return jsonify({'success': False, 'error': 'Video no encontrado'}), 404
        
        negocio_id = row[13]
        metrica_tipo = row[20] if len(row) > 20 else None
        
        badge_result = db.session.execute(text("""
            SELECT b.id, b.nombre, b.descripcion, b.icono, b.color
            FROM negocio_badges_obtenidos nb
            JOIN negocio_badges b ON nb.badge_id = b.id
            WHERE nb.negocio_id = :negocio_id AND nb.activo = true LIMIT 3
        """), {'negocio_id': negocio_id})
        
        badges = [{'id': b[0], 'nombre': b[1], 'descripcion': b[2], 'icono': b[3], 'color': b[4]} 
                  for b in badge_result.fetchall()]
        
        # Obtener reacciones
        reactions_result = db.session.execute(text("""
            SELECT tipo_reaccion, COUNT(*) FROM video_reacciones
            WHERE video_id = :video_id GROUP BY tipo_reaccion
        """), {'video_id': video_id})
        reactions = {r: 0 for r in VALID_REACTIONS}
        for r_row in reactions_result.fetchall():
            if r_row[0] in VALID_REACTIONS:
                reactions[r_row[0]] = r_row[1]
        
        # Obtener user_reaction
        user_reaction = get_user_reaction_for_video(video_id, user_id, session_id)
        
        # Obtener métrica
        metrica_manual = {
            'nombre': row[10] or 'Rendimiento',
            'valor': row[11] or '---',
            'tendencia': row[12] or 'neutral'
        }
        metrica = get_metrica_para_video(negocio_id, metrica_tipo, metrica_manual)
        
        return jsonify({
            'success': True,
            'data': {
                'id': row[0],
                'titulo': row[1],
                'descripcion': row[2],
                'video_url': row[3],
                'thumbnail': row[4],
                'duracion_segundos': row[5],
                'calidad': row[6] or 'HD',
                'vistas': row[7] or 0,
                'likes': row[8] or 0,
                'fecha': row[9].isoformat() if row[9] else None,
                'negocio': {
                    'id': negocio_id,
                    'nombre': row[14],
                    'slug': row[15],
                    'logo_url': row[16],
                    'categoria': row[17],
                    'verificado': row[18] or False,
                    'ubicacion': row[19]
                },
                'badges': badges,
                'metrica': metrica,
                'metrica_tipo': metrica_tipo,
                'reactions': reactions,
                'user_reaction': user_reaction
            }
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


# ═══════════════════════════════════════════════════════════════════════════════
# ENDPOINT: POST /api/videos/upload - ACTUALIZADO para metrica_tipo
# ═══════════════════════════════════════════════════════════════════════════════
@videos_api.route('/upload', methods=['POST'])
def upload_video():
    """Sube un nuevo video al feed"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'success': False, 'error': 'No se recibieron datos'}), 400
        
        required_fields = ['negocio_id', 'titulo', 'video_url']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'success': False, 'error': f'Campo requerido: {field}'}), 400
        
        titulo = data.get('titulo', '').strip()
        if len(titulo) < 5:
            return jsonify({'success': False, 'error': 'El título debe tener al menos 5 caracteres'}), 400
        
        if len(titulo) > 100:
            return jsonify({'success': False, 'error': 'El título no puede exceder 100 caracteres'}), 400
        
        # Verificar negocio
        negocio_check = db.session.execute(text(
            "SELECT id_negocio FROM negocios WHERE id_negocio = :id AND activo = true"
        ), {'id': data['negocio_id']})
        
        if not negocio_check.fetchone():
            return jsonify({'success': False, 'error': 'Negocio no encontrado'}), 404
        
        # Procesar badges_ids
        badges_ids = data.get('badges_ids', [])
        badges_ids_str = '{' + ','.join(map(str, badges_ids)) + '}' if badges_ids else None
        
        # Procesar hashtags
        hashtags = data.get('hashtags', [])
        hashtags_str = '{' + ','.join(f'"{tag}"' for tag in hashtags[:5]) + '}' if hashtags else None
        
        # Validar metrica_tipo
        metrica_tipo = data.get('metrica_tipo')
        if metrica_tipo and metrica_tipo not in VALID_METRICA_TIPOS:
            metrica_tipo = None
        
        # Insertar video - ahora con metrica_tipo
        result = db.session.execute(text("""
            INSERT INTO negocio_videos (
                negocio_id, titulo, descripcion, url_video, fuente,
                url_thumbnail, categoria, hashtags, mostrar_badges, badges_ids,
                metrica_tipo, metrica_nombre, metrica_valor, metrica_tendencia,
                vistas, likes, comentarios, compartidos, visible, fecha_creacion
            ) VALUES (
                :negocio_id, :titulo, :descripcion, :url_video, :fuente,
                :url_thumbnail, :categoria, :hashtags, :mostrar_badges, :badges_ids,
                :metrica_tipo, :metrica_nombre, :metrica_valor, :metrica_tendencia,
                0, 0, 0, 0, true, NOW()
            )
            RETURNING id, fecha_creacion
        """), {
            'negocio_id': data['negocio_id'],
            'titulo': titulo,
            'descripcion': data.get('descripcion', '').strip()[:500],
            'url_video': data.get('video_url', '').strip(),
            'fuente': data.get('fuente', 'cloudinary'),
            'url_thumbnail': data.get('thumbnail_url'),
            'categoria': data.get('categoria'),
            'hashtags': hashtags_str,
            'mostrar_badges': data.get('mostrar_badges', True),
            'badges_ids': badges_ids_str,
            'metrica_tipo': metrica_tipo,  # NUEVO: tipo de métrica a calcular
            'metrica_nombre': data.get('metrica_nombre'),  # Fallback manual
            'metrica_valor': data.get('metrica_valor'),    # Fallback manual
            'metrica_tendencia': data.get('metrica_tendencia', 'up')
        })
        
        row = result.fetchone()
        video_id = row[0]
        fecha_creacion = row[1]
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '¡Video publicado exitosamente!',
            'data': {
                'id': video_id,
                'titulo': titulo,
                'metrica_tipo': metrica_tipo,
                'fecha_creacion': fecha_creacion.isoformat() if fecha_creacion else None
            }
        }), 201
        
    except Exception as e:
        db.session.rollback()
        print(f"❌ Error subiendo video: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500


# ═══════════════════════════════════════════════════════════════════════════════
# ENDPOINT: GET /api/videos/negocios/<id>/badges
# ═══════════════════════════════════════════════════════════════════════════════
@videos_api.route('/negocios/<int:negocio_id>/badges', methods=['GET'])
def get_negocio_badges_for_video(negocio_id):
    """Obtiene los badges de un negocio para el editor de video"""
    try:
        result = db.session.execute(text("""
            SELECT b.id, b.nombre, b.descripcion, b.icono, b.color, nb.nivel
            FROM negocio_badges_obtenidos nb
            JOIN negocio_badges b ON nb.badge_id = b.id
            WHERE nb.negocio_id = :negocio_id AND nb.activo = true
            ORDER BY nb.fecha_obtencion DESC
        """), {'negocio_id': negocio_id})
        
        badges = []
        for row in result.fetchall():
            badges.append({
                'id': row[0], 'nombre': row[1], 'descripcion': row[2],
                'icono': row[3] or 'bi-award', 'color': row[4] or '#a855f7', 'nivel': row[5] or 1
            })
        
        return jsonify({'success': True, 'data': {'badges': badges, 'total': len(badges)}})
        
    except Exception as e:
        print(f"❌ Error obteniendo badges: {e}")
        return jsonify({
            'success': True,
            'data': {
                'badges': [
                    {'id': 1, 'nombre': 'Perfeccionista', 'descripcion': '10 trabajos perfectos', 'icono': 'bi-gem', 'color': '#a855f7'},
                    {'id': 2, 'nombre': 'Primera Estrella', 'descripcion': 'Primera calificación 5★', 'icono': 'bi-trophy-fill', 'color': '#f59e0b'},
                    {'id': 3, 'nombre': 'Rayo Veloz', 'descripcion': 'Responde en <1h', 'icono': 'bi-lightning-charge-fill', 'color': '#10b981'},
                ],
                'total': 3
            }
        })


# ═══════════════════════════════════════════════════════════════════════════════
# ENDPOINT: GET /api/videos/negocios/<id>/metricas - NUEVO
# ═══════════════════════════════════════════════════════════════════════════════
@videos_api.route('/negocios/<int:negocio_id>/metricas', methods=['GET'])
def get_negocio_metricas(negocio_id):
    """
    Obtiene las métricas calculadas de un negocio.
    Útil para el editor de video y para mostrar estadísticas.
    """
    try:
        if not METRICAS_SERVICE_AVAILABLE:
            return jsonify({
                'success': False, 
                'error': 'Servicio de métricas no disponible'
            }), 503
        
        metricas = MetricasService.calcular_metricas_negocio(negocio_id)
        
        # Convertir a formato para selector del editor
        opciones = []
        for tipo, data in metricas.items():
            if data.get('valor') and data.get('valor') != '---':
                opciones.append({
                    'tipo': tipo,
                    'nombre': NOMBRES_METRICAS.get(tipo, tipo),
                    'valor': data['valor'],
                    'tendencia': data['tendencia'],
                    'disponible': True
                })
            else:
                opciones.append({
                    'tipo': tipo,
                    'nombre': NOMBRES_METRICAS.get(tipo, tipo),
                    'valor': '---',
                    'tendencia': 'neutral',
                    'disponible': False
                })
        
        return jsonify({
            'success': True,
            'data': {
                'negocio_id': negocio_id,
                'metricas': metricas,
                'opciones_selector': opciones,
                'tipos_validos': VALID_METRICA_TIPOS
            }
        })
        
    except Exception as e:
        print(f"❌ Error obteniendo métricas: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500


# ═══════════════════════════════════════════════════════════════════════════════
# ENDPOINT: GET /api/videos/negocio/<negocio_id>
# ═══════════════════════════════════════════════════════════════════════════════
@videos_api.route('/negocio/<int:negocio_id>', methods=['GET'])
def get_negocio_videos(negocio_id):
    """Obtiene todos los videos de un negocio"""
    try:
        # Obtener identificador del usuario
        user_id, session_id = get_user_identifier()
        
        result = db.session.execute(text("""
            SELECT id, titulo, descripcion, url_video, fuente, url_thumbnail,
                   categoria, hashtags, duracion, calidad, vistas, likes,
                   metrica_nombre, metrica_valor, metrica_tendencia, metrica_tipo,
                   destacado, visible, fecha_creacion
            FROM negocio_videos
            WHERE negocio_id = :negocio_id AND visible = true
            ORDER BY destacado DESC, fecha_creacion DESC
        """), {'negocio_id': negocio_id})
        
        videos = []
        for row in result.fetchall():
            video_id = row[0]
            metrica_tipo = row[15]
            
            # Obtener reacciones
            reactions_result = db.session.execute(text("""
                SELECT tipo_reaccion, COUNT(*) FROM video_reacciones
                WHERE video_id = :video_id GROUP BY tipo_reaccion
            """), {'video_id': video_id})
            reactions = {r: 0 for r in VALID_REACTIONS}
            for r_row in reactions_result.fetchall():
                if r_row[0] in VALID_REACTIONS:
                    reactions[r_row[0]] = r_row[1]
            
            # Obtener user_reaction
            user_reaction = get_user_reaction_for_video(video_id, user_id, session_id)
            
            # Obtener métrica
            metrica_manual = {'nombre': row[12], 'valor': row[13], 'tendencia': row[14]} if row[12] else None
            metrica = get_metrica_para_video(negocio_id, metrica_tipo, metrica_manual)
            
            videos.append({
                'id': video_id, 'titulo': row[1], 'descripcion': row[2],
                'video_url': row[3], 'fuente': row[4], 'url_thumbnail': row[5],
                'categoria': row[6], 'hashtags': row[7] or [], 'duracion_segundos': row[8],
                'calidad': row[9], 'vistas': row[10] or 0, 'likes': row[11] or 0,
                'metrica': metrica,
                'metrica_tipo': metrica_tipo,
                'reactions': reactions,
                'user_reaction': user_reaction,
                'destacado': row[16], 'activo': row[17],
                'fecha': row[18].isoformat() if row[18] else None
            })
        
        return jsonify({'success': True, 'data': {'videos': videos, 'total': len(videos)}})
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


# ═══════════════════════════════════════════════════════════════════════════════
# ENDPOINT: POST /api/videos/<id>/view
# ═══════════════════════════════════════════════════════════════════════════════
@videos_api.route('/<int:video_id>/view', methods=['POST'])
def register_view(video_id):
    """Registra una vista del video"""
    try:
        db.session.execute(text(
            "UPDATE negocio_videos SET vistas = COALESCE(vistas, 0) + 1 WHERE id = :id"
        ), {'id': video_id})
        db.session.commit()
        
        return jsonify({'success': True})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500


# ═══════════════════════════════════════════════════════════════════════════════
# ENDPOINT: POST /api/videos/<id>/like
# ═══════════════════════════════════════════════════════════════════════════════
@videos_api.route('/<int:video_id>/like', methods=['POST'])
def toggle_like(video_id):
    """Toggle like en un video"""
    try:
        data = request.get_json() or {}
        action = data.get('action', 'like')
        
        if action == 'like':
            db.session.execute(text(
                "UPDATE negocio_videos SET likes = COALESCE(likes, 0) + 1 WHERE id = :id"
            ), {'id': video_id})
        else:
            db.session.execute(text(
                "UPDATE negocio_videos SET likes = GREATEST(COALESCE(likes, 0) - 1, 0) WHERE id = :id"
            ), {'id': video_id})
        
        db.session.commit()
        return jsonify({'success': True, 'action': action})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500


# ═══════════════════════════════════════════════════════════════════════════════
# ENDPOINT: POST /api/videos/<id>/reaction - MEJORADO CON X-User-ID
# ═══════════════════════════════════════════════════════════════════════════════
@videos_api.route('/<int:video_id>/reaction', methods=['POST'])
def toggle_reaction(video_id):
    """
    Agrega o quita una reacción a un video.
    Prioriza X-User-ID (usuario autenticado) sobre X-Session-ID (anónimo).
    - Si action='add': elimina reacción anterior y agrega la nueva
    - Si action='remove': elimina la reacción
    """
    try:
        data = request.get_json() or {}
        reaction_type = data.get('reaction_type')
        action = data.get('action', 'add')
        
        if reaction_type not in VALID_REACTIONS:
            return jsonify({'success': False, 'error': f'Reacción inválida. Válidas: {VALID_REACTIONS}'}), 400
        
        # Obtener identificador del usuario
        user_id, session_id = get_user_identifier()
        
        # Si no hay ningún identificador, generar session_id
        if not user_id and not session_id:
            session_id = str(uuid.uuid4())
        
        # Eliminar reacción existente
        if user_id:
            db.session.execute(text("""
                DELETE FROM video_reacciones 
                WHERE video_id = :video_id AND usuario_id = :user_id
            """), {'video_id': video_id, 'user_id': user_id})
        elif session_id:
            db.session.execute(text("""
                DELETE FROM video_reacciones 
                WHERE video_id = :video_id AND session_id = :session_id
            """), {'video_id': video_id, 'session_id': session_id})
        
        # Agregar nueva reacción
        if action == 'add':
            db.session.execute(text("""
                INSERT INTO video_reacciones (video_id, usuario_id, session_id, tipo_reaccion, created_at)
                VALUES (:video_id, :user_id, :session_id, :reaction_type, NOW())
            """), {
                'video_id': video_id,
                'user_id': user_id,
                'session_id': session_id if not user_id else None,
                'reaction_type': reaction_type
            })
        
        db.session.commit()
        
        # Obtener conteos actualizados
        result = db.session.execute(text("""
            SELECT tipo_reaccion, COUNT(*) FROM video_reacciones
            WHERE video_id = :video_id GROUP BY tipo_reaccion
        """), {'video_id': video_id})
        
        counts = {r: 0 for r in VALID_REACTIONS}
        for row in result.fetchall():
            if row[0] in VALID_REACTIONS:
                counts[row[0]] = row[1]
        
        return jsonify({
            'success': True,
            'action': action,
            'reaction_type': reaction_type,
            'counts': counts,
            'user_id': user_id,
            'session_id': session_id if not user_id else None
        })
        
    except Exception as e:
        db.session.rollback()
        print(f"❌ Error en reacción: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500


# ═══════════════════════════════════════════════════════════════════════════════
# ENDPOINT: GET /api/videos/<id>/reactions
# ═══════════════════════════════════════════════════════════════════════════════
@videos_api.route('/<int:video_id>/reactions', methods=['GET'])
def get_reactions(video_id):
    """Obtiene el conteo de reacciones de un video"""
    try:
        result = db.session.execute(text("""
            SELECT tipo_reaccion, COUNT(*) FROM video_reacciones
            WHERE video_id = :video_id GROUP BY tipo_reaccion
        """), {'video_id': video_id})
        
        counts = {r: 0 for r in VALID_REACTIONS}
        total = 0
        for row in result.fetchall():
            if row[0] in VALID_REACTIONS:
                counts[row[0]] = row[1]
                total += row[1]
        
        # Obtener user_reaction
        user_id, session_id = get_user_identifier()
        user_reaction = get_user_reaction_for_video(video_id, user_id, session_id)
        
        return jsonify({
            'success': True,
            'data': {
                'video_id': video_id, 
                'total': total, 
                'counts': counts, 
                'user_reaction': user_reaction
            }
        })
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


# ═══════════════════════════════════════════════════════════════════════════════
# ENDPOINT: DELETE /api/videos/<video_id>
# ═══════════════════════════════════════════════════════════════════════════════
@videos_api.route('/<int:video_id>', methods=['DELETE'])
def delete_video(video_id):
    """Elimina un video (soft delete)"""
    try:
        result = db.session.execute(text(
            "UPDATE negocio_videos SET visible = false WHERE id = :id RETURNING id"
        ), {'id': video_id})
        
        if not result.fetchone():
            return jsonify({'success': False, 'error': 'Video no encontrado'}), 404
        
        db.session.commit()
        return jsonify({'success': True, 'message': 'Video eliminado'})
        
    except Exception as e:
        db.session.rollback()
        print(f"❌ Error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


# ═══════════════════════════════════════════════════════════════════════════════
# ENDPOINT: PUT /api/videos/<video_id>
# ═══════════════════════════════════════════════════════════════════════════════
@videos_api.route('/<int:video_id>', methods=['PUT'])
def update_video(video_id):
    """Actualiza la información de un video"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'error': 'No se recibieron datos'}), 400
        
        # Ahora incluye metrica_tipo
        allowed_fields = ['titulo', 'descripcion', 'categoria', 'hashtags', 
                         'metrica_tipo', 'metrica_nombre', 'metrica_valor', 'metrica_tendencia', 'destacado']
        
        updates = []
        params = {'video_id': video_id}
        
        for field in allowed_fields:
            if field in data:
                # Validar metrica_tipo
                if field == 'metrica_tipo' and data[field] not in VALID_METRICA_TIPOS:
                    continue
                updates.append(f"{field} = :{field}")
                params[field] = data[field]
        
        if not updates:
            return jsonify({'success': False, 'error': 'No hay campos para actualizar'}), 400
        
        query = f"UPDATE negocio_videos SET {', '.join(updates)} WHERE id = :video_id RETURNING id"
        result = db.session.execute(text(query), params)
        
        if not result.fetchone():
            return jsonify({'success': False, 'error': 'Video no encontrado'}), 404
        
        db.session.commit()
        return jsonify({'success': True, 'message': 'Video actualizado'})
        
    except Exception as e:
        db.session.rollback()
        print(f"❌ Error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


# ═══════════════════════════════════════════════════════════════════════════════
# ENDPOINT: POST /api/videos/<video_id>/destacar
# ═══════════════════════════════════════════════════════════════════════════════
@videos_api.route('/<int:video_id>/destacar', methods=['POST'])
def toggle_destacado(video_id):
    """Marca o desmarca un video como destacado"""
    try:
        result = db.session.execute(text(
            "UPDATE negocio_videos SET destacado = NOT destacado WHERE id = :id RETURNING id, destacado"
        ), {'id': video_id})
        
        row = result.fetchone()
        if not row:
            return jsonify({'success': False, 'error': 'Video no encontrado'}), 404
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'destacado': row[1],
            'message': 'Video destacado' if row[1] else 'Video ya no destacado'
        })
        
    except Exception as e:
        db.session.rollback()
        print(f"❌ Error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500