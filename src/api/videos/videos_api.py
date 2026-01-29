"""
═══════════════════════════════════════════════════════════════════════════════
TUKOMERCIO - API FEED DE VIDEOS
Endpoint para scroll infinito de videos con badges y métricas
═══════════════════════════════════════════════════════════════════════════════
"""

from flask import Blueprint, request, jsonify
from datetime import datetime, timedelta
import random
from src.models import db

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
# Feed de videos con paginación, filtros y badges
# ═══════════════════════════════════════════════════════════════════════════════
@videos_api.route('/feed', methods=['GET'])
def get_video_feed():
    """
    Obtiene el feed de videos con scroll infinito.
    """
    try:
        # Obtener parámetros
        page = request.args.get('page', 1, type=int)
        limit = min(request.args.get('limit', 10, type=int), 20)
        tab = request.args.get('tab', 'para-ti')
        category = request.args.get('category', '')
        city = request.args.get('city', '')
        
        offset = (page - 1) * limit
        
        from db import get_db_connection
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Query base
        base_query = """
            SELECT 
                v.id, v.titulo, v.descripcion, v.video_url, v.thumbnail_url,
                v.duracion, v.calidad, v.vistas, v.likes, v.fecha_creacion,
                v.metrica_nombre, v.metrica_valor, v.metrica_tendencia,
                v.mostrar_badges, v.badges_ids,
                n.id as negocio_id, n.nombre_negocio, n.slug, n.logo_url,
                n.categoria, n.verificado, n.ciudad
            FROM negocio_videos v
            JOIN negocios n ON v.negocio_id = n.id
            WHERE v.activo = true AND n.activo = true
        """
        
        params = []
        
        if category:
            base_query += " AND LOWER(n.categoria) = LOWER(%s)"
            params.append(category)
        
        if city:
            base_query += " AND LOWER(n.ciudad) = LOWER(%s)"
            params.append(city)
        
        # Ordenamiento según tab
        if tab == 'tendencias':
            base_query += " ORDER BY v.vistas DESC, v.likes DESC"
        elif tab == 'nuevos':
            base_query += " ORDER BY v.fecha_creacion DESC"
        else:
            base_query += " ORDER BY v.fecha_creacion DESC"
        
        base_query += " LIMIT %s OFFSET %s"
        params.extend([limit, offset])
        
        cursor.execute(base_query, params)
        rows = cursor.fetchall()
        
        videos = []
        for row in rows:
            video_id = row[0]
            mostrar_badges = row[13]
            badges_ids = row[14]
            negocio_id = row[15]
            
            badges = []
            if mostrar_badges is not False:
                if badges_ids and len(badges_ids) > 0:
                    cursor.execute("""
                        SELECT id, nombre, descripcion, icono, color
                        FROM catalogo_badges WHERE id = ANY(%s)
                    """, [badges_ids])
                    for badge_row in cursor.fetchall():
                        badges.append({
                            'id': badge_row[0], 'nombre': badge_row[1],
                            'descripcion': badge_row[2], 'icono': badge_row[3], 'color': badge_row[4]
                        })
                else:
                    cursor.execute("""
                        SELECT cb.id, cb.nombre, cb.descripcion, cb.icono, cb.color
                        FROM negocio_badges nb
                        JOIN catalogo_badges cb ON nb.badge_id = cb.id
                        WHERE nb.negocio_id = %s AND nb.activo = true LIMIT 3
                    """, [negocio_id])
                    for badge_row in cursor.fetchall():
                        badges.append({
                            'id': badge_row[0], 'nombre': badge_row[1],
                            'descripcion': badge_row[2], 'icono': badge_row[3], 'color': badge_row[4]
                        })
            
            videos.append({
                'id': row[0],
                'titulo': row[1],
                'descripcion': row[2],
                'video_url': row[3],
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
        cursor.execute("SELECT COUNT(*) FROM negocio_videos WHERE activo = true")
        total = cursor.fetchone()[0]
        
        cursor.close()
        conn.close()
        
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
        return jsonify({'success': False, 'error': str(e)}), 500


# ═══════════════════════════════════════════════════════════════════════════════
# ENDPOINT: GET /api/videos/<id>
# ═══════════════════════════════════════════════════════════════════════════════
@videos_api.route('/<int:video_id>', methods=['GET'])
def get_video(video_id):
    """Obtiene un video específico por ID"""
    try:
        from db import get_db_connection
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT 
                v.id, v.titulo, v.descripcion, v.video_url, v.thumbnail_url,
                v.duracion, v.calidad, v.vistas, v.likes, v.fecha_creacion,
                v.metrica_nombre, v.metrica_valor, v.metrica_tendencia,
                n.id, n.nombre_negocio, n.slug, n.logo_url, n.categoria, n.verificado, n.ciudad
            FROM negocio_videos v
            JOIN negocios n ON v.negocio_id = n.id
            WHERE v.id = %s AND v.activo = true
        """, [video_id])
        
        row = cursor.fetchone()
        
        if not row:
            cursor.close()
            conn.close()
            return jsonify({'success': False, 'error': 'Video no encontrado'}), 404
        
        cursor.execute("""
            SELECT cb.id, cb.nombre, cb.descripcion, cb.icono, cb.color
            FROM negocio_badges nb
            JOIN catalogo_badges cb ON nb.badge_id = cb.id
            WHERE nb.negocio_id = %s AND nb.activo = true LIMIT 3
        """, [row[13]])
        
        badges = [{'id': b[0], 'nombre': b[1], 'descripcion': b[2], 'icono': b[3], 'color': b[4]} 
                  for b in cursor.fetchall()]
        
        cursor.close()
        conn.close()
        
        return jsonify({
            'success': True,
            'data': {
                'id': row[0],
                'titulo': row[1],
                'descripcion': row[2],
                'video_url': row[3],
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
        
        badges_ids = data.get('badges_ids', [])
        badges_ids_str = '{' + ','.join(map(str, badges_ids)) + '}' if badges_ids else None
        
        hashtags = data.get('hashtags', [])
        hashtags_str = '{' + ','.join(f'"{tag}"' for tag in hashtags[:5]) + '}' if hashtags else None
        
        from db import get_db_connection
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT id FROM negocios WHERE id = %s AND activo = true", [data['negocio_id']])
        if not cursor.fetchone():
            cursor.close()
            conn.close()
            return jsonify({'success': False, 'error': 'Negocio no encontrado'}), 404
        
        cursor.execute("""
            INSERT INTO negocio_videos (
                negocio_id, titulo, descripcion, video_url, video_tipo,
                thumbnail_url, categoria, hashtags, mostrar_badges, badges_ids,
                metrica_nombre, metrica_valor, metrica_tendencia,
                vistas, likes, comentarios, compartidos, activo, fecha_creacion
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 0, 0, 0, 0, true, NOW()
            )
            RETURNING id, fecha_creacion
        """, [
            data['negocio_id'],
            titulo,
            data.get('descripcion', '').strip()[:500],
            data.get('video_url', '').strip(),
            data.get('video_tipo', 'cloudinary'),
            data.get('thumbnail_url'),
            data.get('categoria'),
            hashtags_str,
            data.get('mostrar_badges', True),
            badges_ids_str,
            data.get('metrica_nombre'),
            data.get('metrica_valor'),
            data.get('metrica_tendencia', 'up')
        ])
        
        result = cursor.fetchone()
        video_id = result[0]
        fecha_creacion = result[1]
        
        conn.commit()
        cursor.close()
        conn.close()
        
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
        from db import get_db_connection
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT cb.id, cb.nombre, cb.descripcion, cb.icono, cb.color, nb.nivel
            FROM negocio_badges nb
            JOIN catalogo_badges cb ON nb.badge_id = cb.id
            WHERE nb.negocio_id = %s AND nb.activo = true
            ORDER BY nb.fecha_obtencion DESC
        """, [negocio_id])
        
        badges = []
        for row in cursor.fetchall():
            badges.append({
                'id': row[0], 'nombre': row[1], 'descripcion': row[2],
                'icono': row[3] or 'bi-award', 'color': row[4] or '#a855f7', 'nivel': row[5] or 1
            })
        
        cursor.close()
        conn.close()
        
        return jsonify({'success': True, 'data': {'badges': badges, 'total': len(badges)}})
        
    except Exception as e:
        print(f"❌ Error obteniendo badges: {e}")
        # Fallback
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
        from db import get_db_connection
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, titulo, descripcion, video_url, video_tipo, thumbnail_url,
                   categoria, hashtags, duracion, calidad, vistas, likes,
                   metrica_nombre, metrica_valor, metrica_tendencia,
                   destacado, activo, fecha_creacion
            FROM negocio_videos
            WHERE negocio_id = %s AND activo = true
            ORDER BY destacado DESC, fecha_creacion DESC
        """, [negocio_id])
        
        videos = []
        for row in cursor.fetchall():
            videos.append({
                'id': row[0], 'titulo': row[1], 'descripcion': row[2],
                'video_url': row[3], 'video_tipo': row[4], 'thumbnail_url': row[5],
                'categoria': row[6], 'hashtags': row[7] or [], 'duracion': row[8],
                'calidad': row[9], 'vistas': row[10] or 0, 'likes': row[11] or 0,
                'metrica': {'nombre': row[12], 'valor': row[13], 'tendencia': row[14]} if row[12] else None,
                'destacado': row[15], 'activo': row[16],
                'fecha': row[17].isoformat() if row[17] else None
            })
        
        cursor.close()
        conn.close()
        
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
        from db import get_db_connection
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("UPDATE negocio_videos SET vistas = COALESCE(vistas, 0) + 1 WHERE id = %s", [video_id])
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({'success': True})
        
    except Exception as e:
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
        
        from db import get_db_connection
        conn = get_db_connection()
        cursor = conn.cursor()
        
        if action == 'like':
            cursor.execute("UPDATE negocio_videos SET likes = COALESCE(likes, 0) + 1 WHERE id = %s", [video_id])
        else:
            cursor.execute("UPDATE negocio_videos SET likes = GREATEST(COALESCE(likes, 0) - 1, 0) WHERE id = %s", [video_id])
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({'success': True, 'action': action})
        
    except Exception as e:
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
        
        from db import get_db_connection
        conn = get_db_connection()
        cursor = conn.cursor()
        
        if action == 'add':
            cursor.execute("""
                INSERT INTO video_reacciones (video_id, session_id, tipo_reaccion)
                VALUES (%s, %s, %s)
                ON CONFLICT (video_id, session_id) 
                DO UPDATE SET tipo_reaccion = EXCLUDED.tipo_reaccion, created_at = NOW()
            """, [video_id, session_id, reaction_type])
        else:
            cursor.execute("DELETE FROM video_reacciones WHERE video_id = %s AND session_id = %s", [video_id, session_id])
        
        conn.commit()
        
        cursor.execute("""
            SELECT tipo_reaccion, COUNT(*) FROM video_reacciones
            WHERE video_id = %s GROUP BY tipo_reaccion
        """, [video_id])
        
        counts = {row[0]: row[1] for row in cursor.fetchall()}
        
        cursor.close()
        conn.close()
        
        return jsonify({
            'success': True,
            'action': action,
            'reaction_type': reaction_type,
            'counts': counts,
            'session_id': session_id
        })
        
    except Exception as e:
        print(f"❌ Error en reacción: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


# ═══════════════════════════════════════════════════════════════════════════════
# ENDPOINT: GET /api/videos/<id>/reactions
# ═══════════════════════════════════════════════════════════════════════════════
@videos_api.route('/<int:video_id>/reactions', methods=['GET'])
def get_reactions(video_id):
    """Obtiene el conteo de reacciones de un video"""
    try:
        from db import get_db_connection
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT tipo_reaccion, COUNT(*) FROM video_reacciones
            WHERE video_id = %s GROUP BY tipo_reaccion
        """, [video_id])
        
        counts = {r: 0 for r in VALID_REACTIONS}
        total = 0
        for row in cursor.fetchall():
            counts[row[0]] = row[1]
            total += row[1]
        
        session_id = request.headers.get('X-Session-ID') or request.cookies.get('session_id')
        user_reaction = None
        if session_id:
            cursor.execute("SELECT tipo_reaccion FROM video_reacciones WHERE video_id = %s AND session_id = %s", [video_id, session_id])
            row = cursor.fetchone()
            if row:
                user_reaction = row[0]
        
        cursor.close()
        conn.close()
        
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
        from db import get_db_connection
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("UPDATE negocio_videos SET activo = false WHERE id = %s RETURNING id", [video_id])
        result = cursor.fetchone()
        
        if not result:
            cursor.close()
            conn.close()
            return jsonify({'success': False, 'error': 'Video no encontrado'}), 404
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({'success': True, 'message': 'Video eliminado'})
        
    except Exception as e:
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
        values = []
        for field in allowed_fields:
            if field in data:
                updates.append(f"{field} = %s")
                values.append(data[field])
        
        if not updates:
            return jsonify({'success': False, 'error': 'No hay campos para actualizar'}), 400
        
        values.append(video_id)
        
        from db import get_db_connection
        conn = get_db_connection()
        cursor = conn.cursor()
        
        query = f"UPDATE negocio_videos SET {', '.join(updates)} WHERE id = %s RETURNING id"
        cursor.execute(query, values)
        result = cursor.fetchone()
        
        if not result:
            cursor.close()
            conn.close()
            return jsonify({'success': False, 'error': 'Video no encontrado'}), 404
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({'success': True, 'message': 'Video actualizado'})
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


# ═══════════════════════════════════════════════════════════════════════════════
# ENDPOINT: POST /api/videos/<video_id>/destacar
# ═══════════════════════════════════════════════════════════════════════════════
@videos_api.route('/<int:video_id>/destacar', methods=['POST'])
def toggle_destacado(video_id):
    """Marca o desmarca un video como destacado"""
    try:
        from db import get_db_connection
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("UPDATE negocio_videos SET destacado = NOT destacado WHERE id = %s RETURNING id, destacado", [video_id])
        result = cursor.fetchone()
        
        if not result:
            cursor.close()
            conn.close()
            return jsonify({'success': False, 'error': 'Video no encontrado'}), 404
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({
            'success': True,
            'destacado': result[1],
            'message': 'Video destacado' if result[1] else 'Video ya no destacado'
        })
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500