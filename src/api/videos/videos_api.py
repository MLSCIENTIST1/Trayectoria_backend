"""
═══════════════════════════════════════════════════════════════════════════════
TUKOMERCIO - API FEED DE VIDEOS
Endpoint para scroll infinito de videos con badges y métricas
═══════════════════════════════════════════════════════════════════════════════
"""

from flask import Blueprint, request, jsonify
from datetime import datetime, timedelta
from src.models.database import db
from sqlalchemy import text

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
        
        # Query base
        query = """
            SELECT 
                v.id, v.titulo, v.descripcion, v.url_video, v.url_thumbnail,
                v.duracion, v.calidad, v.vistas, v.likes, v.fecha_creacion,
                v.metrica_nombre, v.metrica_valor, v.metrica_tendencia,
                v.mostrar_badges, v.badges_ids,
                n.id_negocio as negocio_id, n.nombre_negocio, n.slug, n.logo_url,
                n.categoria, n.verificado, n.ciudad
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
        
        videos = []
        for row in rows:
            negocio_id = row[15]
            mostrar_badges = row[13]
            badges_ids = row[14]
            
            badges = []
            if mostrar_badges is not False:
                badge_result = db.session.execute(text("""
                    SELECT cb.id, cb.nombre, cb.descripcion, cb.icono, cb.color
                    FROM negocio_badges nb
                    JOIN catalogo_badges cb ON nb.badge_id = cb.id
                    WHERE nb.negocio_id = :negocio_id AND nb.visible = true LIMIT 3
                """), {'negocio_id': negocio_id})
                
                for badge_row in badge_result.fetchall():
                    badges.append({
                        'id': badge_row[0], 'nombre': badge_row[1],
                        'descripcion': badge_row[2], 'icono': badge_row[3], 'color': badge_row[4]
                    })
            
            videos.append({
                'id': row[0],
                'titulo': row[1],
                'descripcion': row[2],
                'url_video': row[3],
                'thumbnail': row[4],
                'duracion': row[5],
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
                'metrica': {
                    'nombre': row[10] or 'Rendimiento',
                    'valor': row[11] or '---',
                    'tendencia': row[12] or 'neutral'
                }
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
        result = db.session.execute(text("""
            SELECT 
                v.id, v.titulo, v.descripcion, v.url_video, v.url_thumbnail,
                v.duracion, v.calidad, v.vistas, v.likes, v.fecha_creacion,
                v.metrica_nombre, v.metrica_valor, v.metrica_tendencia,
                n.id, n.nombre_negocio, n.slug, n.logo_url, n.categoria, n.verificado, n.ciudad
            FROM negocio_videos v
            JOIN negocios n ON v.negocio_id = n.id_negocio
            WHERE v.id = :video_id AND v.visible = true
        """), {'video_id': video_id})
        
        row = result.fetchone()
        
        if not row:
            return jsonify({'success': False, 'error': 'Video no encontrado'}), 404
        
        badge_result = db.session.execute(text("""
            SELECT cb.id, cb.nombre, cb.descripcion, cb.icono, cb.color
            FROM negocio_badges nb
            JOIN catalogo_badges cb ON nb.badge_id = cb.id
            WHERE nb.negocio_id = :negocio_id AND nb.visible = true LIMIT 3
        """), {'negocio_id': row[13]})
        
        badges = [{'id': b[0], 'nombre': b[1], 'descripcion': b[2], 'icono': b[3], 'color': b[4]} 
                  for b in badge_result.fetchall()]
        
        return jsonify({
            'success': True,
            'data': {
                'id': row[0],
                'titulo': row[1],
                'descripcion': row[2],
                'url_video': row[3],
                'thumbnail': row[4],
                'duracion': row[5],
                'calidad': row[6] or 'HD',
                'vistas': row[7] or 0,
                'likes': row[8] or 0,
                'fecha': row[9].isoformat() if row[9] else None,
                'negocio': {
                    'id': row[13],
                    'nombre': row[14],
                    'slug': row[15],
                    'logo_url': row[16],
                    'categoria': row[17],
                    'verificado': row[18] or False,
                    'ubicacion': row[19]
                },
                'badges': badges,
                'metrica': {
                    'nombre': row[10] or 'Rendimiento',
                    'valor': row[11] or '---',
                    'tendencia': row[12] or 'neutral'
                }
            }
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


# ═══════════════════════════════════════════════════════════════════════════════
# ENDPOINT: POST /api/videos/upload
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
        
        # Insertar video
        result = db.session.execute(text("""
            INSERT INTO negocio_videos (
                negocio_id, titulo, descripcion, url_video, fuente,
                url_thumbnail, categoria, hashtags, mostrar_badges, badges_ids,
                metrica_nombre, metrica_valor, metrica_tendencia,
                vistas, likes, comentarios, compartidos, visible, fecha_creacion
            ) VALUES (
                :negocio_id, :titulo, :descripcion, :url_video, :fuente,
                :url_thumbnail, :categoria, :hashtags, :mostrar_badges, :badges_ids,
                :metrica_nombre, :metrica_valor, :metrica_tendencia,
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
            'metrica_nombre': data.get('metrica_nombre'),
            'metrica_valor': data.get('metrica_valor'),
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
            SELECT cb.id, cb.nombre, cb.descripcion, cb.icono, cb.color, nb.nivel
            FROM negocio_badges nb
            JOIN catalogo_badges cb ON nb.badge_id = cb.id
            WHERE nb.negocio_id = :negocio_id AND nb.visible = true
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
# ENDPOINT: GET /api/videos/negocio/<negocio_id>
# ═══════════════════════════════════════════════════════════════════════════════
@videos_api.route('/negocio/<int:negocio_id>', methods=['GET'])
def get_negocio_videos(negocio_id):
    """Obtiene todos los videos de un negocio"""
    try:
        result = db.session.execute(text("""
            SELECT id, titulo, descripcion, url_video, fuente, url_thumbnail,
                   categoria, hashtags, duracion, calidad, vistas, likes,
                   metrica_nombre, metrica_valor, metrica_tendencia,
                   destacado, visible, fecha_creacion
            FROM negocio_videos
            WHERE negocio_id = :negocio_id AND visible = true
            ORDER BY destacado DESC, fecha_creacion DESC
        """), {'negocio_id': negocio_id})
        
        videos = []
        for row in result.fetchall():
            videos.append({
                'id': row[0], 'titulo': row[1], 'descripcion': row[2],
                'url_video': row[3], 'fuente': row[4], 'url_thumbnail': row[5],
                'categoria': row[6], 'hashtags': row[7] or [], 'duracion': row[8],
                'calidad': row[9], 'vistas': row[10] or 0, 'likes': row[11] or 0,
                'metrica': {'nombre': row[12], 'valor': row[13], 'tendencia': row[14]} if row[12] else None,
                'destacado': row[15], 'activo': row[16],
                'fecha': row[17].isoformat() if row[17] else None
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
# ENDPOINT: POST /api/videos/<id>/reaction
# ═══════════════════════════════════════════════════════════════════════════════
@videos_api.route('/<int:video_id>/reaction', methods=['POST'])
def toggle_reaction(video_id):
    """Agrega o quita una reacción a un video"""
    try:
        data = request.get_json() or {}
        reaction_type = data.get('reaction_type')
        action = data.get('action', 'add')
        
        if reaction_type not in VALID_REACTIONS:
            return jsonify({'success': False, 'error': f'Reacción inválida. Válidas: {VALID_REACTIONS}'}), 400
        
        session_id = request.headers.get('X-Session-ID') or request.cookies.get('session_id')
        if not session_id:
            import uuid
            session_id = str(uuid.uuid4())
        
        if action == 'add':
            db.session.execute(text("""
                INSERT INTO video_reacciones (video_id, session_id, tipo_reaccion)
                VALUES (:video_id, :session_id, :tipo)
                ON CONFLICT (video_id, session_id) 
                DO UPDATE SET tipo_reaccion = EXCLUDED.tipo_reaccion, created_at = NOW()
            """), {'video_id': video_id, 'session_id': session_id, 'tipo': reaction_type})
        else:
            db.session.execute(text(
                "DELETE FROM video_reacciones WHERE video_id = :video_id AND session_id = :session_id"
            ), {'video_id': video_id, 'session_id': session_id})
        
        db.session.commit()
        
        result = db.session.execute(text("""
            SELECT tipo_reaccion, COUNT(*) FROM video_reacciones
            WHERE video_id = :video_id GROUP BY tipo_reaccion
        """), {'video_id': video_id})
        
        counts = {row[0]: row[1] for row in result.fetchall()}
        
        return jsonify({
            'success': True,
            'action': action,
            'reaction_type': reaction_type,
            'counts': counts,
            'session_id': session_id
        })
        
    except Exception as e:
        db.session.rollback()
        print(f"❌ Error en reacción: {e}")
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
            counts[row[0]] = row[1]
            total += row[1]
        
        session_id = request.headers.get('X-Session-ID') or request.cookies.get('session_id')
        user_reaction = None
        if session_id:
            ur_result = db.session.execute(text(
                "SELECT tipo_reaccion FROM video_reacciones WHERE video_id = :video_id AND session_id = :session_id"
            ), {'video_id': video_id, 'session_id': session_id})
            row = ur_result.fetchone()
            if row:
                user_reaction = row[0]
        
        return jsonify({
            'success': True,
            'data': {'video_id': video_id, 'total': total, 'counts': counts, 'user_reaction': user_reaction}
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
        
        allowed_fields = ['titulo', 'descripcion', 'categoria', 'hashtags', 
                         'metrica_nombre', 'metrica_valor', 'metrica_tendencia', 'destacado']
        
        updates = []
        params = {'video_id': video_id}
        
        for field in allowed_fields:
            if field in data:
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