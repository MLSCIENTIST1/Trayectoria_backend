"""
═══════════════════════════════════════════════════════════════════════════════
API PERFIL PÚBLICO NEGOCIO - BizScore
Endpoint: GET /api/negocio/perfil-publico/<slug>
Ubicación: src/api/profile/perfil_publico_negocio_api.py

VERSIÓN 2.0 - Solo datos reales
═══════════════════════════════════════════════════════════════════════════════
"""

print("=" * 70)
print("🎯 PERFIL_PUBLICO_NEGOCIO_API: INICIANDO CARGA DEL MÓDULO")
print("=" * 70)

# ==========================================
# IMPORTS
# ==========================================
from flask import Blueprint, jsonify, request
from flask_cors import cross_origin
from sqlalchemy import func, desc
from datetime import datetime, timedelta

# Modelos base
from src.models.colombia_data import Negocio, Sucursal
from src.models import db

# Modelos opcionales (pueden no existir las tablas)
try:
    from src.models.colombia_data.negocio_video import NegocioVideo
    print("✅ NegocioVideo importado")
except Exception as e:
    print(f"⚠️ NegocioVideo no disponible: {e}")
    NegocioVideo = None

try:
    from src.models.colombia_data.ratings.negocio_badge import NegocioBadge
    from src.models.colombia_data.ratings.negocio_badge_obtenido import NegocioBadgeObtenido
    print("✅ Badges importados")
except Exception as e:
    print(f"⚠️ Badges no disponibles: {e}")
    NegocioBadge = None
    NegocioBadgeObtenido = None

print("✅ Todos los imports completados")

# ==========================================
# CREAR BLUEPRINT
# ==========================================
perfil_publico_negocio_bp = Blueprint('perfil_publico_negocio', __name__)
print(f"✅ Blueprint creado: {perfil_publico_negocio_bp.name}")


# ═══════════════════════════════════════════════════════════════════════════════
# ENDPOINT PRINCIPAL: GET /api/negocio/perfil-publico/<slug>
# ═══════════════════════════════════════════════════════════════════════════════
@perfil_publico_negocio_bp.route('/api/negocio/perfil-publico/<slug>', methods=['GET'])
@cross_origin()
def get_perfil_publico(slug):
    """
    Obtiene todos los datos del perfil público de un negocio.
    """
    print(f"🎯 GET /api/negocio/perfil-publico/{slug}")
    
    try:
        # 1. BUSCAR NEGOCIO
        negocio = Negocio.query.filter_by(slug=slug, activo=True).first()
        
        if not negocio:
            return jsonify({
                'success': False,
                'error': 'Negocio no encontrado',
                'code': 'NOT_FOUND'
            }), 404

        id_negocio = negocio.id_negocio
        print(f"   ✅ Negocio: {negocio.nombre_negocio} (ID: {id_negocio})")

        # 2. SUCURSAL PRINCIPAL
        sucursal_principal = Sucursal.query.filter_by(
            negocio_id=id_negocio,
            es_principal=True,
            activo=True
        ).first()

        if not sucursal_principal:
            sucursal_principal = Sucursal.query.filter_by(
                negocio_id=id_negocio,
                activo=True
            ).first()

        # 3. OBTENER DATOS REALES
        badges = obtener_badges_negocio(id_negocio)
        videos = obtener_videos_negocio(id_negocio)
        
        # 4. PLACEHOLDERS (pendientes de implementar)
        stats = obtener_estadisticas_placeholder()
        etapas = obtener_etapas_placeholder()
        bizscore = calcular_bizscore(stats, etapas)
        resenas = obtener_resenas_placeholder()
        
        # 5. CONSTRUIR RESPUESTA
        response = {
            'success': True,
            'data': {
                'negocio': {
                    'id': id_negocio,
                    'nombre': negocio.nombre_negocio,
                    'slug': negocio.slug,
                    'descripcion': negocio.descripcion or '',
                    'categoria': negocio.categoria or 'General',
                    'logo_url': negocio.logo_url,
                    'ubicacion': get_ubicacion(negocio, sucursal_principal),
                    'verificado': getattr(negocio, 'verificado', False),
                    'fecha_registro': negocio.fecha_registro.isoformat() if negocio.fecha_registro else None,
                    'whatsapp': get_whatsapp(negocio, sucursal_principal),
                    'telefono': get_telefono(negocio, sucursal_principal),
                    'email': getattr(negocio, 'email', None),
                    'tiempo_respuesta_minutos': None,
                    'horario': getattr(negocio, 'horario', None)
                },
                'config': {
                    'color_primario': negocio.color_tema or '#a855f7',
                    'color_secundario': '#22d3ee',
                    'mostrar_estadisticas': False,  # Pendiente
                    'mostrar_videos': len(videos) > 0,
                    'mostrar_resenas': False,  # Pendiente
                    'badges_destacados': [],
                    'video_destacado_id': None
                },
                'score': bizscore,
                'estadisticas': stats,
                'etapas': etapas,
                'badges': badges,
                'videos': videos,
                'resenas': resenas
            }
        }
        
        print(f"   ✅ Respuesta: {len(badges)} badges, {len(videos)} videos")
        return jsonify(response), 200
        
    except Exception as e:
        print(f"   ❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': 'Error interno del servidor',
            'code': 'INTERNAL_ERROR',
            'detail': str(e)
        }), 500


# ═══════════════════════════════════════════════════════════════════════════════
# FUNCIONES DE DATOS REALES
# ═══════════════════════════════════════════════════════════════════════════════

def obtener_badges_negocio(id_negocio):
    """Obtiene los badges del negocio desde la BD."""
    if not NegocioBadgeObtenido:
        return []
    
    try:
        badges_obtenidos = NegocioBadgeObtenido.query.filter_by(
            negocio_id=id_negocio,
            activo=True
        ).order_by(
            NegocioBadgeObtenido.es_favorito.desc(),
            NegocioBadgeObtenido.fecha_obtencion.desc()
        ).all()
        
        badges = []
        for bo in badges_obtenidos:
            if bo.badge:
                badges.append({
                    'codigo': bo.badge.codigo,
                    'nombre': bo.badge.nombre,
                    'descripcion': bo.badge.descripcion,
                    'icono': bo.badge.icono,
                    'color': bo.badge.color_primario,
                    'color_fondo': bo.badge.color_fondo,
                    'nivel': bo.badge.nivel,
                    'categoria': bo.badge.categoria,
                    'especial': bo.badge.es_exclusivo or bo.badge.nivel >= 4,
                    'fecha_obtencion': bo.fecha_obtencion.isoformat() if bo.fecha_obtencion else None,
                    'es_favorito': bo.es_favorito
                })
        
        return badges
        
    except Exception as e:
        print(f"   ⚠️ Error badges: {e}")
        return []


def obtener_videos_negocio(id_negocio):
    """Obtiene los videos del negocio desde la BD."""
    if not NegocioVideo:
        return []
    
    try:
        videos_db = NegocioVideo.query.filter_by(
            negocio_id=id_negocio,
            visible=True
        ).order_by(
            NegocioVideo.destacado.desc(),
            NegocioVideo.orden.asc(),
            NegocioVideo.fecha_creacion.desc()
        ).limit(10).all()
        
        videos = []
        for v in videos_db:
            videos.append({
                'id': v.id,
                'titulo': v.titulo,
                'descripcion': v.descripcion,
                'thumbnail_url': v.url_thumbnail,
                'video_url': v.url_video,
                'duracion': v.get_duracion_formateada(),
                'vistas': v.vistas or 0,
                'likes': v.likes or 0,
                'fecha': v.fecha_creacion.isoformat() if v.fecha_creacion else None,
                'calidad': v.calidad,
                'destacado': v.destacado,
                'metrica': {
                    'nombre': v.metrica_nombre,
                    'valor': v.metrica_valor,
                    'tendencia': v.metrica_tendencia,
                    'icono': v.metrica_icono,
                    'color': v.metrica_color
                } if v.metrica_nombre else None,
                'badges': []
            })
        
        return videos
        
    except Exception as e:
        print(f"   ⚠️ Error videos: {e}")
        return []


# ═══════════════════════════════════════════════════════════════════════════════
# FUNCIONES AUXILIARES
# ═══════════════════════════════════════════════════════════════════════════════

def get_ubicacion(negocio, sucursal):
    """Obtiene la ubicación del negocio."""
    if sucursal:
        if sucursal.ciudad:
            return f"{sucursal.ciudad}, Colombia"
        if sucursal.direccion:
            return sucursal.direccion
    
    if negocio.ciudad:
        ciudad_nombre = getattr(negocio.ciudad, 'ciudad_nombre', None)
        if ciudad_nombre:
            return f"{ciudad_nombre}, Colombia"
    
    if negocio.direccion:
        return negocio.direccion
    
    return None


def get_whatsapp(negocio, sucursal):
    """Obtiene el WhatsApp del negocio."""
    if sucursal:
        whatsapp = getattr(sucursal, 'whatsapp', None) or getattr(sucursal, 'telefono', None)
        if whatsapp:
            return whatsapp
    return negocio.whatsapp or negocio.telefono


def get_telefono(negocio, sucursal):
    """Obtiene el teléfono del negocio."""
    if sucursal:
        telefono = getattr(sucursal, 'telefono', None)
        if telefono:
            return telefono
    return negocio.telefono


# ═══════════════════════════════════════════════════════════════════════════════
# PLACEHOLDERS (pendientes de implementar con datos reales)
# ═══════════════════════════════════════════════════════════════════════════════

def obtener_estadisticas_placeholder():
    """Estadísticas - TODO: conectar con service_ratings."""
    return {
        'total_contratos': 0,
        'contratos_exitosos': 0,
        'tasa_exito': 0,
        'disputas': 0,
        'sin_disputas': True,
        'clientes_recurrentes': 0,
        'tasa_recomendacion': 0,
        'tiempo_promedio_dias': None
    }


def obtener_etapas_placeholder():
    """Etapas - TODO: conectar con service_qualifiers."""
    return []


def calcular_bizscore(stats, etapas):
    """Calcula el BizScore."""
    if not etapas:
        return {
            'valor': 0,
            'nivel': 'Sin calificaciones',
            'percentil': 0
        }
    
    promedio_etapas = sum(e.get('score', 0) for e in etapas) / len(etapas)
    score_etapas = promedio_etapas * 0.40
    score_exito = stats.get('tasa_exito', 0) * 0.25
    score_recomendacion = stats.get('tasa_recomendacion', 0) * 0.20
    score_disputas = 10 if stats.get('sin_disputas', True) else max(0, 10 - (stats.get('disputas', 0) * 2))
    score_recurrentes = min(5, stats.get('clientes_recurrentes', 0) * 0.5)
    
    score_total = round(score_etapas + score_exito + score_recomendacion + score_disputas + score_recurrentes, 0)
    score_total = min(100, max(0, score_total))
    
    if score_total >= 90:
        nivel = 'Excelente'
        percentil = 95
    elif score_total >= 80:
        nivel = 'Muy Bueno'
        percentil = 85
    elif score_total >= 70:
        nivel = 'Bueno'
        percentil = 70
    elif score_total >= 60:
        nivel = 'Regular'
        percentil = 50
    else:
        nivel = 'En Desarrollo'
        percentil = 30
    
    return {
        'valor': int(score_total),
        'nivel': nivel,
        'percentil': percentil
    }


def obtener_resenas_placeholder():
    """Reseñas - TODO: conectar con service_ratings."""
    return {
        'promedio': 0,
        'total': 0,
        'distribucion': {5: 0, 4: 0, 3: 0, 2: 0, 1: 0},
        'lista': []
    }


# ═══════════════════════════════════════════════════════════════════════════════
# ENDPOINT: Lista de negocios con perfil público
# ═══════════════════════════════════════════════════════════════════════════════
@perfil_publico_negocio_bp.route('/api/negocios/publicos', methods=['GET'])
@cross_origin()
def listar_negocios_publicos():
    """Lista negocios con perfil público activo."""
    try:
        negocios = Negocio.query.filter_by(activo=True, perfil_publico=True).limit(20).all()
        
        resultado = []
        for negocio in negocios:
            resultado.append({
                'id': negocio.id_negocio,
                'nombre': negocio.nombre_negocio,
                'slug': negocio.slug,
                'logo_url': negocio.logo_url,
                'categoria': negocio.categoria or 'General'
            })
        
        return jsonify({'success': True, 'data': resultado}), 200
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


# ═══════════════════════════════════════════════════════════════════════════════
print("=" * 70)
print("🎯 PERFIL_PUBLICO_NEGOCIO_API v2.0 CARGADO - Solo datos reales")
print("=" * 70)