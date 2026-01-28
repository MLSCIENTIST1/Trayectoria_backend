"""
═══════════════════════════════════════════════════════════════════════════════
API PERFIL PÚBLICO NEGOCIO - BizScore
Endpoint: GET /api/negocio/perfil-publico/<slug>
Ubicación: src/api/profile/perfil_publico_negocio_api.py
═══════════════════════════════════════════════════════════════════════════════
"""

print("=" * 70)
print("🎯 PERFIL_PUBLICO_NEGOCIO_API: INICIANDO CARGA DEL MÓDULO")
print("=" * 70)

# ==========================================
# IMPORTS CON LOGS DETALLADOS
# ==========================================

try:
    print("🔄 [1/7] Importando Flask...")
    from flask import Blueprint, jsonify, request
    print("✅ [1/7] Flask importado correctamente")
except Exception as e:
    print(f"❌ [1/7] ERROR importando Flask: {e}")
    import traceback
    traceback.print_exc()
    raise

try:
    print("🔄 [2/7] Importando flask_cors...")
    from flask_cors import cross_origin
    print("✅ [2/7] flask_cors importado correctamente")
except Exception as e:
    print(f"❌ [2/7] ERROR importando flask_cors: {e}")
    import traceback
    traceback.print_exc()
    raise

try:
    print("🔄 [3/7] Importando sqlalchemy...")
    from sqlalchemy import func, desc
    print("✅ [3/7] sqlalchemy importado correctamente")
except Exception as e:
    print(f"❌ [3/7] ERROR importando sqlalchemy: {e}")
    import traceback
    traceback.print_exc()
    raise

try:
    print("🔄 [4/7] Importando datetime...")
    from datetime import datetime, timedelta
    print("✅ [4/7] datetime importado correctamente")
except Exception as e:
    print(f"❌ [4/7] ERROR importando datetime: {e}")
    import traceback
    traceback.print_exc()
    raise

try:
    print("🔄 [5/7] Importando Negocio desde src.models.colombia_data...")
    from src.models.colombia_data import Negocio
    print("✅ [5/7] Negocio importado correctamente")
except Exception as e:
    print(f"❌ [5/7] ERROR importando Negocio: {e}")
    import traceback
    traceback.print_exc()
    raise

try:
    print("🔄 [6/7] Importando Sucursal desde src.models.colombia_data...")
    from src.models.colombia_data import Sucursal
    print("✅ [6/7] Sucursal importado correctamente")
except Exception as e:
    print(f"❌ [6/7] ERROR importando Sucursal: {e}")
    import traceback
    traceback.print_exc()
    raise

try:
    print("🔄 [7/7] Importando db desde src.models...")
    from src.models import db
    print("✅ [7/7] db importado correctamente")
except Exception as e:
    print(f"❌ [7/7] ERROR importando db: {e}")
    import traceback
    traceback.print_exc()
    raise

print("=" * 70)
print("🎯 PERFIL_PUBLICO_NEGOCIO_API: TODOS LOS IMPORTS EXITOSOS")
print("=" * 70)

# ==========================================
# CREAR BLUEPRINT
# ==========================================
print("🔄 Creando Blueprint 'perfil_publico_negocio'...")
perfil_publico_negocio_bp = Blueprint('perfil_publico_negocio', __name__)
print(f"✅ Blueprint creado: nombre='{perfil_publico_negocio_bp.name}'")


# ═══════════════════════════════════════════════════════════════════════════════
# ENDPOINT PRINCIPAL: GET /api/negocio/perfil-publico/<slug>
# ═══════════════════════════════════════════════════════════════════════════════
@perfil_publico_negocio_bp.route('/api/negocio/perfil-publico/<slug>', methods=['GET'])
@cross_origin()
def get_perfil_publico(slug):
    """
    Obtiene todos los datos del perfil público de un negocio.
    """
    print(f"🎯 GET /api/negocio/perfil-publico/{slug} - Iniciando...")
    
    try:
        # 1. BUSCAR NEGOCIO POR SLUG
        print(f"   🔍 Buscando negocio con slug='{slug}'...")
        negocio = Negocio.query.filter_by(slug=slug, activo=True).first()
        
        if not negocio:
            print(f"   ❌ Negocio no encontrado con slug='{slug}'")
            return jsonify({
                'success': False,
                'error': 'Negocio no encontrado',
                'code': 'NOT_FOUND'
            }), 404

        id_negocio = negocio.id_negocio
        print(f"   ✅ Negocio encontrado: id={id_negocio}, nombre='{negocio.nombre_negocio}'")

        # 2. OBTENER SUCURSAL PRINCIPAL
        print(f"   🔍 Buscando sucursal principal...")
        sucursal_principal = Sucursal.query.filter_by(
            id_negocio=id_negocio,
            es_principal=True,
            activo=True
        ).first()
        
        if not sucursal_principal:
            sucursal_principal = Sucursal.query.filter_by(
                id_negocio=id_negocio,
                activo=True
            ).first()
        
        if sucursal_principal:
            print(f"   ✅ Sucursal encontrada: id={sucursal_principal.id_sucursal}")
        else:
            print(f"   ⚠️ No se encontró sucursal para el negocio")

        # 3. CALCULAR DATOS
        print(f"   📊 Calculando estadísticas...")
        stats = calcular_estadisticas_simuladas(id_negocio)
        etapas = obtener_etapas_simuladas()
        bizscore = calcular_bizscore(stats, etapas)
        badges = obtener_badges_simulados(negocio)
        videos = obtener_videos_simulados()
        resenas = obtener_resenas_simuladas()
        
        # 4. CONSTRUIR RESPUESTA
        print(f"   📦 Construyendo respuesta...")
        response = {
            'success': True,
            'data': {
                'negocio': {
                    'id': id_negocio,
                    'nombre': negocio.nombre_negocio,
                    'slug': negocio.slug,
                    'descripcion': negocio.descripcion or negocio.nombre_negocio,
                    'categoria': negocio.categoria or 'Comercio',
                    'logo_url': negocio.logo_url,
                    'ubicacion': get_ubicacion(negocio, sucursal_principal),
                    'verificado': getattr(negocio, 'verificado', False),
                    'fecha_registro': negocio.fecha_registro.isoformat() if negocio.fecha_registro else None,
                    'whatsapp': get_whatsapp(negocio, sucursal_principal),
                    'telefono': get_telefono(negocio, sucursal_principal),
                    'email': getattr(negocio, 'email', None),
                    'tiempo_respuesta_minutos': 45,
                    'horario': getattr(negocio, 'horario', None) or 'Lun-Vie: 8am-6pm, Sáb: 9am-2pm'
                },
                'config': {
                    'color_primario': negocio.color_tema or '#a855f7',
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
        
        print(f"   ✅ Respuesta construida exitosamente para '{negocio.nombre_negocio}'")
        return jsonify(response), 200
        
    except Exception as e:
        print(f"   ❌ ERROR en get_perfil_publico: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': 'Error interno del servidor',
            'code': 'INTERNAL_ERROR',
            'detail': str(e)
        }), 500


# ═══════════════════════════════════════════════════════════════════════════════
# FUNCIONES AUXILIARES
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
    
    # Intentar desde relación ciudad del negocio
    if negocio.ciudad:
        ciudad_nombre = getattr(negocio.ciudad, 'ciudad_nombre', None)
        if ciudad_nombre:
            return f"{ciudad_nombre}, Colombia"
    
    # Fallback a dirección del negocio
    if negocio.direccion:
        return negocio.direccion
    
    return "Colombia"


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
# FUNCIONES SIMULADAS
# ═══════════════════════════════════════════════════════════════════════════════

def calcular_estadisticas_simuladas(id_negocio):
    """Estadísticas simuladas."""
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
    return [
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
    print("🎯 GET /api/negocios/publicos - Iniciando...")
    
    try:
        negocios = Negocio.query.filter_by(activo=True, perfil_publico=True).limit(20).all()
        print(f"   ✅ Encontrados {len(negocios)} negocios")
        
        resultado = []
        for negocio in negocios:
            resultado.append({
                'id': negocio.id_negocio,
                'nombre': negocio.nombre_negocio,
                'slug': negocio.slug,
                'logo_url': negocio.logo_url,
                'categoria': negocio.categoria or 'Comercio'
            })
        
        return jsonify({
            'success': True,
            'data': resultado
        }), 200
        
    except Exception as e:
        print(f"   ❌ ERROR: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# ═══════════════════════════════════════════════════════════════════════════════
# FIN DEL MÓDULO
# ═══════════════════════════════════════════════════════════════════════════════
print("=" * 70)
print("🎯 PERFIL_PUBLICO_NEGOCIO_API: MÓDULO CARGADO COMPLETAMENTE")
print(f"🎯 Blueprint registrado: {perfil_publico_negocio_bp.name}")
print(f"🎯 Rutas definidas: /api/negocio/perfil-publico/<slug>, /api/negocios/publicos")
print("=" * 70)