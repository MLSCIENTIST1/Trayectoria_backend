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
API PERFIL PÚBLICO NEGOCIO - BizScore
Endpoint: GET /api/negocio/perfil-publico/<slug>
Ubicación: src/api/profile/perfil_publico_negocio_api.py

VERSIÓN 2.1 - Integrado con MetricasService
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

# ✅ IMPORTAR METRICAS SERVICE
try:
    from src.api.utils.metricas_service import MetricasService
    print("✅ MetricasService importado")
except Exception as e:
    print(f"⚠️ MetricasService no disponible: {e}")
    MetricasService = None

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
        
        # ✅ ESTADÍSTICAS REALES desde MetricasService
        stats = obtener_estadisticas_reales(id_negocio)
        
        # ✅ ETAPAS REALES desde service_ratings
        etapas = obtener_etapas_reales(id_negocio)
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
                         'horario': getattr(negocio, 'horario', None),
                         'horario_atencion': getattr(negocio, 'horario_atencion', None),
                         'redes_sociales': getattr(negocio, 'redes_sociales', None),
                         'video_portafolio': getattr(negocio, 'video_portafolio', None),
                         'sitio_web': getattr(negocio, 'sitio_web', None),
                         'ciudad': getattr(negocio, 'ciudad', None),
                         'direccion': negocio.direccion,
                         'micrositio_activo': getattr(negocio, 'tiene_pagina', False),
                     },
                'config': {
                    'color_primario': negocio.color_tema or '#a855f7',
                    'color_secundario': '#22d3ee',
                    'mostrar_estadisticas': stats.get('total_contratos', 0) > 0,
                    'mostrar_videos': len(videos) > 0,
                    'mostrar_resenas': False,  # Pendiente
                    'badges_destacados': [],
                    'video_destacado_id': None
                },
                'score': {
                    **bizscore,
                    'total_contratos': stats.get('total_contratos', 0),
                    'tasa_exito': stats.get('tasa_exito', 0),
                    'clientes_recurrentes': stats.get('clientes_recurrentes', 0),
                    'satisfaccion': stats.get('satisfaccion', 0),
                    'entregas_anticipadas': stats.get('entregas_anticipadas', 0)
                },
                'estadisticas': stats,
                'etapas': etapas,
                'badges': badges,
                'videos': videos,
                'resenas': resenas
            }
        }
        
        print(f"   ✅ Respuesta: {len(badges)} badges, {len(videos)} videos, {stats.get('total_contratos', 0)} contratos")
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

def obtener_estadisticas_reales(id_negocio):
    """
    ✅ NUEVO v2.1: Obtiene estadísticas REALES usando MetricasService.
    """
    if not MetricasService:
        print("   ⚠️ MetricasService no disponible, usando placeholder")
        return obtener_estadisticas_placeholder()
    
    try:
        # Obtener métricas calculadas
        metricas = MetricasService.calcular_metricas_negocio(id_negocio)
        
        # Extraer valores raw
        tasa_exito_raw = metricas.get('tasa_exito', {}).get('valor_raw', 0) or 0
        satisfaccion_raw = metricas.get('satisfaccion', {}).get('valor_raw', 0) or 0
        proyectos_raw = metricas.get('proyectos_completados', {}).get('valor_raw', 0) or 0
        recurrentes_raw = metricas.get('clientes_recurrentes', {}).get('valor_raw', 0) or 0
        entregas_raw = metricas.get('entregas_anticipadas', {}).get('valor_raw', 0) or 0
        
        # Calcular total de contratos (completados + en progreso)
        # Por ahora usamos proyectos_completados como total
        total_contratos = proyectos_raw
        
        stats = {
            'total_contratos': total_contratos,
            'contratos_exitosos': proyectos_raw,
            'tasa_exito': tasa_exito_raw,
            'disputas': 0,  # TODO: implementar contador de disputas
            'sin_disputas': True,
            'clientes_recurrentes': recurrentes_raw,
            'tasa_recomendacion': int(satisfaccion_raw * 20) if satisfaccion_raw else 0,  # Convertir 5★ a %
            'tiempo_promedio_dias': 1 if proyectos_raw > 0 else None,  # Basado en entregas mismo día
            'entregas_anticipadas': entregas_raw,
            'satisfaccion': satisfaccion_raw,
            # ✅ Campos para "Estadísticas de Confiabilidad" del frontend
            'cumplimiento': tasa_exito_raw,
            'tiempo_promedio': 1 if proyectos_raw > 0 else 0,
            'recomendacion': int(satisfaccion_raw * 20) if satisfaccion_raw else 0,
            # Valores formateados para UI
            'metricas_formateadas': {
                'tasa_exito': metricas.get('tasa_exito', {}).get('valor', '---'),
                'satisfaccion': metricas.get('satisfaccion', {}).get('valor', '---'),
                'proyectos': metricas.get('proyectos_completados', {}).get('valor', '---'),
                'recurrentes': metricas.get('clientes_recurrentes', {}).get('valor', '---'),
                'entregas': metricas.get('entregas_anticipadas', {}).get('valor', '---')
            }
        }
        
        print(f"   ✅ Estadísticas reales: {total_contratos} contratos, {tasa_exito_raw}% éxito, {recurrentes_raw}% recurrentes")
        return stats
        
    except Exception as e:
        print(f"   ⚠️ Error obteniendo estadísticas reales: {e}")
        import traceback
        traceback.print_exc()
        return obtener_estadisticas_placeholder()


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
    """Estadísticas placeholder cuando MetricasService no está disponible."""
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


def obtener_etapas_reales(id_negocio):
    """
    Obtiene los promedios de cada etapa desde service_ratings.
    """
    try:
        from sqlalchemy import text
        
        result = db.session.execute(text("""
            SELECT 
                AVG(sr.promedio_etapa1) as etapa1,
                AVG(sr.promedio_etapa2) as etapa2,
                AVG(sr.promedio_etapa3) as etapa3,
                AVG(sr.promedio_etapa4) as etapa4,
                AVG(sr.promedio_global) as global_score,
                COUNT(*) as total_calificaciones
            FROM service_ratings sr
            JOIN servicio s ON sr.servicio_id = s.id_servicio
            WHERE s.negocio_contratado_id = :negocio_id
              AND sr.promedio_global IS NOT NULL
        """), {'negocio_id': id_negocio})
        
        row = result.fetchone()
        
        if not row or not row[5]:  # Sin calificaciones
            return []
        
        etapas = []
        
        # Etapa 1 - Comunicación
        if row[0]:
            score1 = round(float(row[0]) * 20)  # Convertir 5 a 100
            etapas.append({
                'nombre': 'Comunicación',
                'descripcion': 'Claridad y rapidez en la comunicación',
                'score': score1,
                'total_calificaciones': row[5],
                'icono': 'bi-chat-dots'
            })
        
        # Etapa 2 - Puntualidad (si tiene datos)
        if row[1]:
            score2 = round(float(row[1]) * 20)
            etapas.append({
                'nombre': 'Puntualidad',
                'descripcion': 'Cumplimiento de tiempos acordados',
                'score': score2,
                'total_calificaciones': row[5],
                'icono': 'bi-clock'
            })
        
        # Etapa 3 - Calidad del trabajo
        if row[2]:
            score3 = round(float(row[2]) * 20)
            etapas.append({
                'nombre': 'Calidad del trabajo',
                'descripcion': 'Resultado final del servicio',
                'score': score3,
                'total_calificaciones': row[5],
                'icono': 'bi-star'
            })
        
        # Etapa 4 - Precio justo (si tiene datos)
        if row[3]:
            score4 = round(float(row[3]) * 20)
            etapas.append({
                'nombre': 'Precio justo',
                'descripcion': 'Relación calidad-precio',
                'score': score4,
                'total_calificaciones': row[5],
                'icono': 'bi-currency-dollar'
            })
        
        print(f"   ✅ Etapas calculadas: {len(etapas)} etapas, {row[5]} calificaciones")
        return etapas
        
    except Exception as e:
        print(f"   ⚠️ Error obteniendo etapas: {e}")
        import traceback
        traceback.print_exc()
        return []


def obtener_etapas_placeholder():
    """Fallback si falla obtener_etapas_reales."""
    return []


def calcular_bizscore(stats, etapas):
    """Calcula el BizScore basado en estadísticas reales."""
    total_contratos = stats.get('total_contratos', 0)
    
    # Si no hay contratos, no hay score
    if total_contratos == 0:
        return {
            'valor': 0,
            'nivel': 'Sin actividad',
            'percentil': 0
        }
    
    # Calcular score basado en métricas reales
    tasa_exito = stats.get('tasa_exito', 0)
    satisfaccion = stats.get('satisfaccion', 0)
    recurrentes = stats.get('clientes_recurrentes', 0)
    entregas = stats.get('entregas_anticipadas', 0)
    
    # Pesos para cada métrica
    score_exito = tasa_exito * 0.30  # 30% del score
    score_satisfaccion = (satisfaccion / 5 * 100) * 0.30 if satisfaccion else 0  # 30%
    score_recurrentes = min(recurrentes, 50) * 0.20  # 20% (max 50% recurrentes = 10 puntos)
    score_entregas = entregas * 0.10  # 10%
    score_volumen = min(total_contratos, 100) * 0.10  # 10% (max 100 contratos = 10 puntos)
    
    score_total = round(score_exito + score_satisfaccion + score_recurrentes + score_entregas + score_volumen, 0)
    score_total = min(100, max(0, score_total))
    
    # Determinar nivel
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
    elif score_total >= 40:
        nivel = 'En Desarrollo'
        percentil = 30
    else:
        nivel = 'Iniciando'
        percentil = 15
    
    return {
        'valor': int(score_total),
        'nivel': nivel,
        'percentil': percentil,
        'descripcion': f'Basado en {total_contratos} contratos completados'
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
print("🎯 PERFIL_PUBLICO_NEGOCIO_API v2.1 CARGADO - Con MetricasService")
print("=" * 70)