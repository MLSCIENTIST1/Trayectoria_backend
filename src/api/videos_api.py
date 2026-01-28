"""
═══════════════════════════════════════════════════════════════════════════════
TUKOMERCIO - API FEED DE VIDEOS
Endpoint para scroll infinito de videos con badges y métricas
═══════════════════════════════════════════════════════════════════════════════
"""

from flask import Blueprint, request, jsonify
from datetime import datetime, timedelta
import random

# Crear Blueprint
videos_api = Blueprint('videos_api', __name__)

# ═══════════════════════════════════════════════════════════════════════════════
# ENDPOINT: GET /api/videos/feed
# Feed de videos con paginación, filtros y badges
# ═══════════════════════════════════════════════════════════════════════════════
@videos_api.route('/feed', methods=['GET'])
def get_video_feed():
    """
    Obtiene el feed de videos con scroll infinito.
    
    Query params:
    - page (int): Página actual (default 1)
    - limit (int): Videos por página (default 10, max 20)
    - tab (str): Tipo de feed - 'para-ti', 'tendencias', 'categoria', 'cerca', 'nuevos'
    - category (str): Filtrar por categoría de negocio
    - city (str): Filtrar por ciudad
    - sort (str): Ordenar por - 'recientes', 'vistas', 'valorados'
    """
    try:
        # Obtener parámetros
        page = request.args.get('page', 1, type=int)
        limit = min(request.args.get('limit', 10, type=int), 20)
        tab = request.args.get('tab', 'para-ti')
        category = request.args.get('category', '')
        city = request.args.get('city', '')
        sort_by = request.args.get('sort', 'recientes')
        
        offset = (page - 1) * limit
        
        # Construir query base
        # NOTA: Ajustar según tu modelo de base de datos real
        
        from db import get_db_connection  # Importar tu conexión
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Query base con JOIN a negocios y badges
        base_query = """
            SELECT 
                v.id,
                v.titulo,
                v.descripcion,
                v.video_url,
                v.thumbnail_url,
                v.duracion,
                v.calidad,
                v.vistas,
                v.likes,
                v.fecha_creacion,
                v.metrica_nombre,
                v.metrica_valor,
                v.metrica_tendencia,
                n.id as negocio_id,
                n.nombre_negocio as negocio_nombre,
                n.slug as negocio_slug,
                n.logo_url as negocio_logo,
                n.categoria as negocio_categoria,
                n.verificado as negocio_verificado,
                n.ciudad as negocio_ciudad
            FROM negocio_videos v
            JOIN negocios n ON v.negocio_id = n.id
            WHERE v.activo = true AND n.activo = true
        """
        
        params = []
        
        # Filtros
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
        elif tab == 'categoria':
            # TODO: Filtrar por categoría del usuario actual
            base_query += " ORDER BY v.fecha_creacion DESC"
        elif tab == 'cerca':
            # TODO: Ordenar por distancia geográfica
            base_query += " ORDER BY v.fecha_creacion DESC"
        else:  # para-ti (default)
            # Algoritmo simple: mezcla de recientes + populares
            base_query += " ORDER BY (v.vistas * 0.3 + v.likes * 0.5 + EXTRACT(EPOCH FROM v.fecha_creacion)/86400 * 0.2) DESC"
        
        # Paginación
        base_query += " LIMIT %s OFFSET %s"
        params.extend([limit, offset])
        
        cursor.execute(base_query, params)
        rows = cursor.fetchall()
        
        videos = []
        for row in rows:
            video_id = row[0]
            
            # Obtener badges del negocio para este video
            cursor.execute("""
                SELECT 
                    cb.id,
                    cb.nombre,
                    cb.descripcion,
                    cb.icono,
                    cb.color
                FROM negocio_badges nb
                JOIN catalogo_badges cb ON nb.badge_id = cb.id
                WHERE nb.negocio_id = %s AND nb.activo = true
                LIMIT 3
            """, [row[13]])  # negocio_id
            
            badges = []
            for badge_row in cursor.fetchall():
                badges.append({
                    'id': badge_row[0],
                    'nombre': badge_row[1],
                    'descripcion': badge_row[2],
                    'icono': badge_row[3],
                    'color': badge_row[4]
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
                    'tendencia': row[12] or 'neutral',
                    'texto': row[11] or '---'
                }
            })
        
        cursor.close()
        conn.close()
        
        return jsonify({
            'success': True,
            'data': {
                'videos': videos,
                'page': page,
                'limit': limit,
                'has_more': len(videos) >= limit
            }
        })
        
    except Exception as e:
        print(f"❌ Error en feed de videos: {e}")
        
        # Fallback: devolver datos de prueba
        return jsonify({
            'success': True,
            'data': {
                'videos': get_test_videos(),
                'page': 1,
                'limit': 10,
                'has_more': False
            }
        })


# ═══════════════════════════════════════════════════════════════════════════════
# ENDPOINT: GET /api/videos/<id>
# Obtener un video específico
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
            return jsonify({'success': False, 'error': 'Video no encontrado'}), 404
        
        # Obtener badges
        cursor.execute("""
            SELECT cb.id, cb.nombre, cb.descripcion, cb.icono, cb.color
            FROM negocio_badges nb
            JOIN catalogo_badges cb ON nb.badge_id = cb.id
            WHERE nb.negocio_id = %s AND nb.activo = true
            LIMIT 3
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
# ENDPOINT: POST /api/videos/<id>/view
# Registrar vista de video
# ═══════════════════════════════════════════════════════════════════════════════
@videos_api.route('/<int:video_id>/view', methods=['POST'])
def register_view(video_id):
    """Registra una vista del video"""
    try:
        from db import get_db_connection
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE negocio_videos 
            SET vistas = COALESCE(vistas, 0) + 1
            WHERE id = %s
        """, [video_id])
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({'success': True})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


# ═══════════════════════════════════════════════════════════════════════════════
# ENDPOINT: POST /api/videos/<id>/like
# Dar/quitar like a video
# ═══════════════════════════════════════════════════════════════════════════════
@videos_api.route('/<int:video_id>/like', methods=['POST'])
def toggle_like(video_id):
    """Toggle like en un video"""
    try:
        data = request.get_json() or {}
        action = data.get('action', 'like')  # 'like' o 'unlike'
        
        from db import get_db_connection
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        if action == 'like':
            cursor.execute("""
                UPDATE negocio_videos 
                SET likes = COALESCE(likes, 0) + 1
                WHERE id = %s
            """, [video_id])
        else:
            cursor.execute("""
                UPDATE negocio_videos 
                SET likes = GREATEST(COALESCE(likes, 0) - 1, 0)
                WHERE id = %s
            """, [video_id])
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({'success': True, 'action': action})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


# ═══════════════════════════════════════════════════════════════════════════════
# DATOS DE PRUEBA (mientras se implementa BD completa)
# ═══════════════════════════════════════════════════════════════════════════════
def get_test_videos():
    """Devuelve videos de prueba para desarrollo"""
    return [
        {
            'id': 1,
            'titulo': 'Instalación de Luces LED para Moto - Proceso Completo',
            'descripcion': 'Te mostramos cómo instalamos luces LED personalizadas en una moto deportiva.',
            'video_url': 'https://www.youtube.com/watch?v=dQw4w9WgXcQ',
            'thumbnail': None,
            'duracion': '12:45',
            'calidad': 'HD',
            'vistas': 2340,
            'likes': 187,
            'fecha': datetime.now().isoformat(),
            'negocio': {
                'id': 4,
                'nombre': 'Rodar',
                'slug': 'rodar',
                'logo_url': None,
                'categoria': 'Automotriz',
                'verificado': True,
                'ubicacion': 'Bogotá'
            },
            'badges': [
                {'id': 1, 'nombre': 'Perfeccionista', 'descripcion': '10 trabajos perfectos', 'icono': 'bi-gem', 'color': '#a855f7'},
                {'id': 2, 'nombre': 'Primera Estrella', 'descripcion': 'Primera calificación 5★', 'icono': 'bi-trophy-fill', 'color': '#f59e0b'},
                {'id': 3, 'nombre': 'Rayo Veloz', 'descripcion': 'Responde en <1h', 'icono': 'bi-lightning-charge-fill', 'color': '#10b981'}
            ],
            'metrica': {
                'nombre': 'Tasa de éxito',
                'valor': '+15%',
                'tendencia': 'up',
                'texto': '+15% arriba'
            }
        },
        {
            'id': 2,
            'titulo': 'Personalización Completa de Casco - Arte Aerografiado',
            'descripcion': 'Diseño exclusivo con aerógrafo. Cada casco es único.',
            'video_url': 'https://www.youtube.com/watch?v=jNQXAC9IVRw',
            'thumbnail': None,
            'duracion': '8:32',
            'calidad': 'HD',
            'vistas': 1856,
            'likes': 234,
            'fecha': (datetime.now() - timedelta(days=3)).isoformat(),
            'negocio': {
                'id': 4,
                'nombre': 'Rodar',
                'slug': 'rodar',
                'logo_url': None,
                'categoria': 'Automotriz',
                'verificado': True,
                'ubicacion': 'Bogotá'
            },
            'badges': [
                {'id': 1, 'nombre': 'Perfeccionista', 'descripcion': '10 trabajos perfectos', 'icono': 'bi-gem', 'color': '#a855f7'},
                {'id': 4, 'nombre': 'Sin Disputas', 'descripcion': '30 días sin problemas', 'icono': 'bi-shield-check', 'color': '#3b82f6'}
            ],
            'metrica': {
                'nombre': 'Clientes recurrentes',
                'valor': '85%',
                'tendencia': 'up',
                'texto': '85% vuelven'
            }
        },
        {
            'id': 3,
            'titulo': 'Mantenimiento de Suspensión - Tutorial Profesional',
            'descripcion': 'Mantenimiento completo de suspensión para motos de alto cilindraje.',
            'video_url': 'https://www.youtube.com/watch?v=9bZkp7q19f0',
            'thumbnail': None,
            'duracion': '15:20',
            'calidad': 'HD',
            'vistas': 3421,
            'likes': 298,
            'fecha': (datetime.now() - timedelta(days=5)).isoformat(),
            'negocio': {
                'id': 4,
                'nombre': 'Rodar',
                'slug': 'rodar',
                'logo_url': None,
                'categoria': 'Automotriz',
                'verificado': True,
                'ubicacion': 'Bogotá'
            },
            'badges': [
                {'id': 3, 'nombre': 'Rayo Veloz', 'descripcion': 'Responde en <1h', 'icono': 'bi-lightning-charge-fill', 'color': '#10b981'},
                {'id': 5, 'nombre': 'Experto', 'descripcion': '+50 trabajos', 'icono': 'bi-star-fill', 'color': '#f59e0b'}
            ],
            'metrica': {
                'nombre': 'Tiempo de entrega',
                'valor': '-2 días',
                'tendencia': 'up',
                'texto': '2 días más rápido'
            }
        }
    ]


# ═══════════════════════════════════════════════════════════════════════════════
# REGISTRAR BLUEPRINT
# En tu app.py principal, agregar:
# 
# from api.videos_api import videos_api
# app.register_blueprint(videos_api, url_prefix='/api/videos')
# ═══════════════════════════════════════════════════════════════════════════════