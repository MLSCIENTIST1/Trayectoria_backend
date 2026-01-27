"""
═══════════════════════════════════════════════════════════════════════════════
API PERFIL PÚBLICO NEGOCIO - BizScore
Endpoint: GET /api/negocio/perfil-publico/<slug>
Ubicación: src/api/profile/perfil_publico_negocio_api.py
═══════════════════════════════════════════════════════════════════════════════
"""

from flask import Blueprint, jsonify, request
from flask_cors import cross_origin
from sqlalchemy import func, desc
from datetime import datetime, timedelta

from src.models.colombia_data import Negocio
from src.models.colombia_data import Sucursal
from src.models import db

# Crear Blueprint
perfil_publico_negocio_bp = Blueprint('perfil_publico_negocio', __name__)


# ═══════════════════════════════════════════════════════════════════════════════
# ENDPOINT PRINCIPAL: GET /api/negocio/perfil-publico/<slug>
# ═══════════════════════════════════════════════════════════════════════════════
@perfil_publico_negocio_bp.route('/api/negocio/perfil-publico/<slug>', methods=['GET'])
@cross_origin()
def get_perfil_publico(slug):
    """
    Obtiene todos los datos del perfil público de un negocio.
    
    Args:
        slug: Identificador único del negocio en la URL
        
    Returns:
        JSON con: negocio, score, badges, etapas, videos, reseñas, contacto
    """
    try:
        # ─────────────────────────────────────────────────────────────
        # 1. BUSCAR NEGOCIO POR SLUG
        # ─────────────────────────────────────────────────────────────
        negocio = Negocio.query.filter_by(slug=slug, activo=True).first()
        
        if not negocio:
            return jsonify({
                'success': False,
                'error': 'Negocio no encontrado',
                'code': 'NOT_FOUND'
            }), 404

        id_negocio = negocio.id_negocio

        # ─────────────────────────────────────────────────────────────
        # 2. OBTENER SUCURSAL PRINCIPAL (para datos de contacto)
        # ─────────────────────────────────────────────────────────────
        sucursal_principal = Sucursal.query.filter_by(
            id_negocio=id_negocio,
            es_principal=True,
            activo=True
        ).first()
        
        # Si no hay principal, tomar la primera activa
        if not sucursal_principal:
            sucursal_principal = Sucursal.query.filter_by(
                id_negocio=id_negocio,
                activo=True
            ).first()

        # ─────────────────────────────────────────────────────────────
        # 3. CALCULAR ESTADÍSTICAS (simuladas por ahora)
        # ─────────────────────────────────────────────────────────────
        stats = calcular_estadisticas_simuladas(id_negocio)
        
        # ─────────────────────────────────────────────────────────────
        # 4. OBTENER CALIFICACIONES POR ETAPA (simuladas)
        # ─────────────────────────────────────────────────────────────
        etapas = obtener_etapas_simuladas()
        
        # ─────────────────────────────────────────────────────────────
        # 5. CALCULAR BIZSCORE
        # ─────────────────────────────────────────────────────────────
        bizscore = calcular_bizscore(stats, etapas)
        
        # ─────────────────────────────────────────────────────────────
        # 6. OBTENER BADGES (simulados)
        # ─────────────────────────────────────────────────────────────
        badges = obtener_badges_simulados(negocio)
        
        # ─────────────────────────────────────────────────────────────
        # 7. OBTENER VIDEOS (simulados)
        # ─────────────────────────────────────────────────────────────
        videos = obtener_videos_simulados()
        
        # ─────────────────────────────────────────────────────────────
        # 8. OBTENER RESEÑAS (simuladas)
        # ─────────────────────────────────────────────────────────────
        resenas = obtener_resenas_simuladas()
        
        # ─────────────────────────────────────────────────────────────
        # 9. CONSTRUIR RESPUESTA
        # ─────────────────────────────────────────────────────────────
        response = {
            'success': True,
            'data': {
                'negocio': {
                    'id': id_negocio,
                    'nombre': negocio.nombre,
                    'slug': negocio.slug,
                    'descripcion': getattr(negocio, 'descripcion', None) or negocio.nombre,
                    'categoria': getattr(negocio, 'categoria', None) or 'Comercio',
                    'logo_url': getattr(negocio, 'logo_url', None),
                    'ubicacion': get_ubicacion(negocio, sucursal_principal),
                    'verificado': getattr(negocio, 'verificado', False),
                    'fecha_registro': negocio.fecha_creacion.isoformat() if hasattr(negocio, 'fecha_creacion') and negocio.fecha_creacion else None,
                    'whatsapp': get_whatsapp(negocio, sucursal_principal),
                    'telefono': get_telefono(negocio, sucursal_principal),
                    'email': getattr(negocio, 'email', None),
                    'tiempo_respuesta_minutos': 45,
                    'horario': getattr(negocio, 'horario', None) or 'Lun-Vie: 8am-6pm, Sáb: 9am-2pm'
                },
                'config': {
                    'color_primario': '#a855f7',
                    'color_secundario': '#22d3ee',
                    'mostrar_estadisticas': True,
                    'mostrar_videos': True,
                    'mostrar_resenas': True,
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
        
        return jsonify(response), 200
        
    except Exception as e:
        print(f"Error en get_perfil_publico: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': 'Error interno del servidor',
            'code': 'INTERNAL_ERROR',
            'detail': str(e)
        }), 500


# ═══════════════════════════════════════════════════════════════════════════════
# FUNCIONES AUXILIARES PARA OBTENER DATOS DEL NEGOCIO
# ═══════════════════════════════════════════════════════════════════════════════

def get_ubicacion(negocio, sucursal):
    """Obtiene la ubicación del negocio."""
    if sucursal:
        ciudad = getattr(sucursal, 'ciudad', None)
        direccion = getattr(sucursal, 'direccion', None)
        if ciudad:
            return f"{ciudad}, Colombia"
        if direccion:
            return direccion
    
    # Fallback al negocio
    ciudad = getattr(negocio, 'ciudad', None)
    if ciudad:
        return f"{ciudad}, Colombia"
    
    return "Colombia"


def get_whatsapp(negocio, sucursal):
    """Obtiene el WhatsApp del negocio."""
    # Primero de sucursal
    if sucursal:
        whatsapp = getattr(sucursal, 'whatsapp', None) or getattr(sucursal, 'telefono', None)
        if whatsapp:
            return whatsapp
    
    # Luego del negocio
    return getattr(negocio, 'whatsapp', None) or getattr(negocio, 'telefono', None)


def get_telefono(negocio, sucursal):
    """Obtiene el teléfono del negocio."""
    if sucursal:
        telefono = getattr(sucursal, 'telefono', None)
        if telefono:
            return telefono
    
    return getattr(negocio, 'telefono', None)


# ═══════════════════════════════════════════════════════════════════════════════
# FUNCIONES SIMULADAS (mientras se implementan los modelos reales)
# ═══════════════════════════════════════════════════════════════════════════════

def calcular_estadisticas_simuladas(id_negocio):
    """Estadísticas simuladas - reemplazar con datos reales."""
    return {
        'total_contratos': 127,
        'contratos_exitosos': 124,
        'tasa_exito': 98,
        'disputas': 0,
        'sin_disputas': True,
        'clientes_recurrentes': 34,
        'tasa_recomendacion': 96,
        'tiempo_promedio_dias': 4.2
    }


def obtener_etapas_simuladas():
    """Etapas de calificación simuladas."""
    return [
        {
            'numero': 1,
            'codigo': 'contratacion',
            'nombre': 'Contratación',
            'descripcion': 'Claridad, respuesta y acuerdos',
            'color': '#a855f7',
            'score': 95,
            'total_calificaciones': 127,
            'criterios': [
                {'codigo': 'claridad', 'nombre': 'Claridad', 'puntuacion': 96},
                {'codigo': 'respuesta', 'nombre': 'Respuesta', 'puntuacion': 94},
                {'codigo': 'acuerdos', 'nombre': 'Acuerdos', 'puntuacion': 95}
            ]
        },
        {
            'numero': 2,
            'codigo': 'ejecucion',
            'nombre': 'Ejecución',
            'descripcion': 'Cumplimiento, calidad y comunicación',
            'color': '#22d3ee',
            'score': 92,
            'total_calificaciones': 125,
            'criterios': [
                {'codigo': 'cumplimiento', 'nombre': 'Cumplimiento', 'puntuacion': 94},
                {'codigo': 'calidad', 'nombre': 'Calidad', 'puntuacion': 91},
                {'codigo': 'comunicacion', 'nombre': 'Comunicación', 'puntuacion': 92}
            ]
        },
        {
            'numero': 3,
            'codigo': 'finalizacion',
            'nombre': 'Finalización',
            'descripcion': 'Entrega, completitud y satisfacción',
            'color': '#10b981',
            'score': 89,
            'total_calificaciones': 124,
            'criterios': [
                {'codigo': 'entrega', 'nombre': 'Entrega', 'puntuacion': 90},
                {'codigo': 'completitud', 'nombre': 'Completitud', 'puntuacion': 88},
                {'codigo': 'satisfaccion', 'nombre': 'Satisfacción', 'puntuacion': 89}
            ]
        },
        {
            'numero': 4,
            'codigo': 'post_servicio',
            'nombre': 'Post-Servicio',
            'descripcion': 'Durabilidad, garantía y seguimiento',
            'color': '#f59e0b',
            'score': 85,
            'total_calificaciones': 98,
            'criterios': [
                {'codigo': 'durabilidad', 'nombre': 'Durabilidad', 'puntuacion': 86},
                {'codigo': 'garantia', 'nombre': 'Garantía', 'puntuacion': 84},
                {'codigo': 'seguimiento', 'nombre': 'Seguimiento', 'puntuacion': 85}
            ]
        }
    ]


def calcular_bizscore(stats, etapas):
    """Calcula el BizScore."""
    promedio_etapas = sum(e['score'] for e in etapas) / len(etapas) if etapas else 0
    score_etapas = promedio_etapas * 0.40
    score_exito = stats['tasa_exito'] * 0.25
    score_recomendacion = stats['tasa_recomendacion'] * 0.20
    score_disputas = 10 if stats['sin_disputas'] else max(0, 10 - (stats['disputas'] * 2))
    score_recurrentes = min(5, stats['clientes_recurrentes'] * 0.5)
    
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


def obtener_badges_simulados(negocio):
    """Badges simulados."""
    badges = [
        {
            'codigo': 'verificado',
            'nombre': 'Verificado',
            'descripcion': 'Identidad verificada por TuKomercio',
            'icono': 'bi-patch-check-fill',
            'color': '#3b82f6',
            'nivel': 2,
            'especial': False
        },
        {
            'codigo': 'rayo_veloz',
            'nombre': 'Rayo Veloz',
            'descripcion': 'Responde en menos de 1 hora',
            'icono': 'bi-lightning-charge-fill',
            'color': '#10b981',
            'nivel': 2,
            'especial': False
        },
        {
            'codigo': 'top_5',
            'nombre': 'Top 5%',
            'descripcion': 'Entre los mejores de su categoría',
            'icono': 'bi-award-fill',
            'color': '#f59e0b',
            'nivel': 4,
            'especial': True
        },
        {
            'codigo': 'sin_disputas',
            'nombre': 'Récord Limpio',
            'descripcion': '50+ contratos sin disputas',
            'icono': 'bi-shield-check',
            'color': '#10b981',
            'nivel': 3,
            'especial': False
        }
    ]
    return badges


def obtener_videos_simulados():
    """Videos simulados."""
    return [
        {
            'id': 1,
            'titulo': 'Nuestro proceso de trabajo',
            'descripcion': 'Conoce cómo trabajamos y por qué somos diferentes',
            'thumbnail_url': 'https://images.unsplash.com/photo-1492144534655-ae79c964c9d7?w=800&h=450&fit=crop',
            'video_url': 'https://www.youtube.com/embed/dQw4w9WgXcQ',
            'duracion': '3:45',
            'vistas': 1250,
            'likes': 89,
            'fecha': datetime.now().isoformat(),
            'calidad': 'HD',
            'destacado': True,
            'badges': [
                {'nombre': 'Popular', 'icono': 'bi-star-fill', 'color': '#f59e0b'}
            ],
            'metrica': None
        }
    ]


def obtener_resenas_simuladas():
    """Reseñas simuladas."""
    return {
        'promedio': 4.8,
        'total': 127,
        'distribucion': {
            5: 99,
            4: 19,
            3: 6,
            2: 2,
            1: 1
        },
        'lista': [
            {
                'id': 1,
                'autor': {
                    'nombre': 'Cliente Satisfecho',
                    'avatar_url': None,
                    'ubicacion': 'Bogotá',
                    'es_recurrente': True
                },
                'puntuacion': 5,
                'comentario': 'Excelente servicio, muy profesionales. Totalmente recomendado.',
                'fecha': datetime.now().isoformat(),
                'servicio_tipo': 'Servicio completo',
                'verificada': True,
                'respuesta': {
                    'texto': '¡Muchas gracias por tu confianza! Siempre a la orden.',
                    'fecha': datetime.now().isoformat()
                },
                'util_count': 12
            }
        ]
    }


# ═══════════════════════════════════════════════════════════════════════════════
# ENDPOINT: Lista de negocios con perfil público
# ═══════════════════════════════════════════════════════════════════════════════
@perfil_publico_negocio_bp.route('/api/negocios/publicos', methods=['GET'])
@cross_origin()
def listar_negocios_publicos():
    """Lista negocios con perfil público activo."""
    try:
        negocios = Negocio.query.filter_by(activo=True).limit(20).all()
        
        resultado = []
        for negocio in negocios:
            resultado.append({
                'id': negocio.id_negocio,
                'nombre': negocio.nombre,
                'slug': negocio.slug,
                'logo_url': getattr(negocio, 'logo_url', None),
                'categoria': getattr(negocio, 'categoria', 'Comercio')
            })
        
        return jsonify({
            'success': True,
            'data': resultado
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500