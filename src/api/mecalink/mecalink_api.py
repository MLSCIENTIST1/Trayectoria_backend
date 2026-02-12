# ═══════════════════════════════════════════════════════════════════════════════
# ███████╗██╗   ██╗██╗  ██╗ ██████╗ ███╗   ███╗███████╗██████╗  ██████╗██╗ ██████╗ 
# ╚══██╔══╝██║   ██║██║ ██╔╝██╔═══██╗████╗ ████║██╔════╝██╔══██╗██╔════╝██║██╔═══██╗
#    ██║   ██║   ██║█████╔╝ ██║   ██║██╔████╔██║█████╗  ██████╔╝██║     ██║██║   ██║
#    ██║   ██║   ██║██╔═██╗ ██║   ██║██║╚██╔╝██║██╔══╝  ██╔══██╗██║     ██║██║   ██║
#    ██║   ╚██████╔╝██║  ██╗╚██████╔╝██║ ╚═╝ ██║███████╗██║  ██║╚██████╗██║╚██████╔╝
#    ╚═╝    ╚═════╝ ╚═╝  ╚═╝ ╚═════╝ ╚═╝     ╚═╝╚══════╝╚═╝  ╚═╝ ╚═════╝╚═╝ ╚═════╝ 
# ═══════════════════════════════════════════════════════════════════════════════
#
# MECALINK - API de Mecánicos a Domicilio
# Extensión de TuKomercio para servicios automotrices
#
# © 2024-2026 Carlos Eduardo Huérfano Bermúdez. Todos los derechos reservados.
# ═══════════════════════════════════════════════════════════════════════════════

"""
MecaLink API v1.0

Marketplace de mecánicos a domicilio integrado en TuKomercio.

Endpoints:
- /api/mecalink/health - Health check
- /api/mecalink/buscar - Buscar mecánicos por ciudad/zona/servicio
- /api/mecalink/perfil/<id> - Perfil público de mecánico
- /api/mecalink/perfil/slug/<slug> - Perfil por slug del negocio
- /api/mecalink/mi-perfil - Ver/editar mi perfil (auth)
- /api/mecalink/mis-estadisticas - Dashboard del mecánico (auth)
- /api/mecalink/calificar/<id> - Calificar mecánico (auth)
- /api/mecalink/admin/pendientes - Listar pendientes (admin)
- /api/mecalink/admin/verificar/<id> - Verificar mecánico (admin)
"""

from flask import Blueprint, request, jsonify, g
from functools import wraps
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

# ═══════════════════════════════════════════════════════════════════════════════
# BLUEPRINT
# ═══════════════════════════════════════════════════════════════════════════════

mecalink_bp = Blueprint('mecalink', __name__)


# ═══════════════════════════════════════════════════════════════════════════════
# IMPORTACIONES LAZY (para evitar errores si el modelo no existe aún)
# ═══════════════════════════════════════════════════════════════════════════════

def get_db():
    """Obtiene la instancia de la base de datos."""
    from src.models.database import db
    return db

def get_negocio_model():
    """Obtiene el modelo Negocio."""
    from src.models.negocio import Negocio
    return Negocio

def get_mecalink_model():
    """Obtiene el modelo MecanicoMecalink."""
    try:
        from src.models.mecalink_model import MecanicoMecalink
        return MecanicoMecalink
    except ImportError:
        logger.warning("⚠️ Modelo MecanicoMecalink no encontrado")
        return None


# ═══════════════════════════════════════════════════════════════════════════════
# DECORADORES DE AUTENTICACIÓN
# ═══════════════════════════════════════════════════════════════════════════════

def require_auth(f):
    """Decorador para requerir autenticación."""
    @wraps(f)
    def decorated(*args, **kwargs):
        user_id = getattr(g, 'user_id', None) or request.headers.get('X-User-ID')
        if not user_id:
            return jsonify({"success": False, "error": "No autorizado"}), 401
        try:
            g.user_id = int(user_id)
        except (ValueError, TypeError):
            return jsonify({"success": False, "error": "ID de usuario inválido"}), 401
        return f(*args, **kwargs)
    return decorated


def require_admin(f):
    """Decorador para requerir permisos de administrador."""
    @wraps(f)
    def decorated(*args, **kwargs):
        # TODO: Implementar verificación de admin real
        user_id = getattr(g, 'user_id', None) or request.headers.get('X-User-ID')
        if not user_id:
            return jsonify({"success": False, "error": "No autorizado"}), 401
        g.user_id = int(user_id)
        # Por ahora permitimos, luego agregar verificación
        return f(*args, **kwargs)
    return decorated


# ═══════════════════════════════════════════════════════════════════════════════
# HEALTH CHECK
# ═══════════════════════════════════════════════════════════════════════════════

@mecalink_bp.route('/health', methods=['GET'])
def mecalink_health():
    """Health check del módulo MecaLink."""
    MecanicoMecalink = get_mecalink_model()
    
    return jsonify({
        "success": True,
        "service": "MecaLink API",
        "version": "1.0.0",
        "status": "online",
        "model_loaded": MecanicoMecalink is not None,
        "description": "Marketplace de mecánicos a domicilio",
        "endpoints": {
            "buscar": "/api/mecalink/buscar",
            "perfil": "/api/mecalink/perfil/<id>",
            "mi_perfil": "/api/mecalink/mi-perfil",
            "calificar": "/api/mecalink/calificar/<id>"
        }
    })


# ═══════════════════════════════════════════════════════════════════════════════
# FUNCIÓN HELPER - Crear perfil MecaLink
# ═══════════════════════════════════════════════════════════════════════════════

def crear_perfil_mecalink(negocio_id, mecalink_data, ciudad=None):
    """
    Crea el perfil MecaLink para un negocio de tipo mecánico a domicilio.
    
    Esta función se llama desde registrar_negocio cuando la categoría es 'mecanico_domicilio'.
    
    Args:
        negocio_id (int): ID del negocio recién creado
        mecalink_data (dict): Datos específicos de MecaLink
        ciudad (str): Ciudad del negocio
    
    Returns:
        MecanicoMecalink: El perfil creado o None si hay error
    """
    MecanicoMecalink = get_mecalink_model()
    db = get_db()
    
    if not MecanicoMecalink:
        logger.error("❌ No se puede crear perfil MecaLink: modelo no disponible")
        return None
    
    try:
        perfil = MecanicoMecalink(
            negocio_id=negocio_id,
            zonas_texto=mecalink_data.get('zonas'),
            servicios=mecalink_data.get('servicios', []),
            disponibilidad_texto=mecalink_data.get('disponibilidad'),
            tiene_vehiculo=mecalink_data.get('tiene_vehiculo'),
            tiene_herramientas=mecalink_data.get('tiene_herramientas'),
            experiencia=mecalink_data.get('experiencia'),
            ciudad_operacion=ciudad
        )
        
        db.session.add(perfil)
        logger.info(f"✅ Perfil MecaLink creado para negocio {negocio_id}")
        return perfil
        
    except Exception as e:
        logger.error(f"❌ Error creando perfil MecaLink: {e}")
        return None


# ═══════════════════════════════════════════════════════════════════════════════
# ENDPOINTS PÚBLICOS - BÚSQUEDA
# ═══════════════════════════════════════════════════════════════════════════════

@mecalink_bp.route('/buscar', methods=['GET'])
def buscar_mecanicos():
    """
    Busca mecánicos por ciudad, zona y/o servicio.
    
    Query params:
        - ciudad: Ciudad de búsqueda (requerido)
        - zona: Zona/barrio específico (opcional)
        - servicio: Tipo de servicio requerido (opcional)
        - limit: Número máximo de resultados (default: 20, max: 50)
    
    Returns:
        Lista de mecánicos que coinciden con los criterios
    """
    MecanicoMecalink = get_mecalink_model()
    
    if not MecanicoMecalink:
        return jsonify({
            "success": False,
            "error": "Servicio MecaLink no disponible temporalmente"
        }), 503
    
    ciudad = request.args.get('ciudad', '').strip()
    zona = request.args.get('zona', '').strip()
    servicio = request.args.get('servicio', '').strip()
    
    try:
        limit = min(int(request.args.get('limit', 20)), 50)
    except ValueError:
        limit = 20
    
    if not ciudad:
        return jsonify({
            "success": False,
            "error": "Se requiere especificar la ciudad"
        }), 400
    
    try:
        # Query base: mecánicos activos en la ciudad
        query = MecanicoMecalink.query.filter(
            MecanicoMecalink.estado == 'activo',
            MecanicoMecalink.ciudad_operacion.ilike(f'%{ciudad}%')
        )
        
        # Filtrar por zona si se especifica
        if zona:
            zona_normalizada = zona.lower().strip()
            # Buscar en el array de zonas
            query = query.filter(
                MecanicoMecalink.zonas_array.any(zona_normalizada)
            )
        
        # Filtrar por servicio si se especifica
        if servicio:
            query = query.filter(
                MecanicoMecalink.servicios.any(servicio)
            )
        
        # Ordenar: verificados primero, luego por calificación
        query = query.order_by(
            MecanicoMecalink.verificado_mecalink.desc(),
            MecanicoMecalink.calificacion_promedio.desc(),
            MecanicoMecalink.total_servicios.desc()
        )
        
        mecanicos = query.limit(limit).all()
        
        return jsonify({
            "success": True,
            "count": len(mecanicos),
            "filtros": {
                "ciudad": ciudad,
                "zona": zona or None,
                "servicio": servicio or None
            },
            "mecanicos": [m.to_dict_publico() for m in mecanicos]
        })
        
    except Exception as e:
        logger.error(f"❌ Error en búsqueda de mecánicos: {e}")
        return jsonify({
            "success": False,
            "error": "Error al buscar mecánicos"
        }), 500


@mecalink_bp.route('/perfil/<int:mecanico_id>', methods=['GET'])
def obtener_perfil_publico(mecanico_id):
    """
    Obtiene el perfil público de un mecánico por ID.
    
    Args:
        mecanico_id: ID del perfil MecaLink
    
    Returns:
        Perfil público del mecánico
    """
    MecanicoMecalink = get_mecalink_model()
    
    if not MecanicoMecalink:
        return jsonify({
            "success": False,
            "error": "Servicio MecaLink no disponible"
        }), 503
    
    mecanico = MecanicoMecalink.query.get(mecanico_id)
    
    if not mecanico:
        return jsonify({
            "success": False,
            "error": "Mecánico no encontrado"
        }), 404
    
    if mecanico.estado != 'activo':
        return jsonify({
            "success": False,
            "error": "Este perfil no está disponible"
        }), 404
    
    return jsonify({
        "success": True,
        "mecanico": mecanico.to_dict_publico()
    })


@mecalink_bp.route('/perfil/slug/<slug>', methods=['GET'])
def obtener_perfil_por_slug(slug):
    """
    Obtiene el perfil público de un mecánico por el slug de su negocio.
    
    Args:
        slug: Slug del negocio
    
    Returns:
        Perfil público del mecánico con datos del negocio
    """
    MecanicoMecalink = get_mecalink_model()
    Negocio = get_negocio_model()
    
    if not MecanicoMecalink:
        return jsonify({
            "success": False,
            "error": "Servicio MecaLink no disponible"
        }), 503
    
    # Buscar el negocio por slug
    negocio = Negocio.query.filter_by(
        slug=slug, 
        categoria='mecanico_domicilio'
    ).first()
    
    if not negocio:
        return jsonify({
            "success": False,
            "error": "Mecánico no encontrado"
        }), 404
    
    # Buscar el perfil MecaLink
    mecanico = MecanicoMecalink.query.filter_by(
        negocio_id=negocio.id_negocio
    ).first()
    
    if not mecanico:
        return jsonify({
            "success": False,
            "error": "Perfil MecaLink no configurado"
        }), 404
    
    if mecanico.estado != 'activo':
        return jsonify({
            "success": False,
            "error": "Este perfil no está disponible"
        }), 404
    
    return jsonify({
        "success": True,
        "mecanico": mecanico.to_dict(include_negocio=True)
    })


# ═══════════════════════════════════════════════════════════════════════════════
# ENDPOINTS AUTENTICADOS - MI PERFIL
# ═══════════════════════════════════════════════════════════════════════════════

@mecalink_bp.route('/mi-perfil', methods=['GET'])
@require_auth
def obtener_mi_perfil():
    """
    Obtiene el perfil MecaLink del usuario autenticado.
    """
    MecanicoMecalink = get_mecalink_model()
    Negocio = get_negocio_model()
    
    if not MecanicoMecalink:
        return jsonify({
            "success": False,
            "error": "Servicio MecaLink no disponible"
        }), 503
    
    # Buscar negocio del usuario tipo mecánico
    negocio = Negocio.query.filter_by(
        usuario_id=g.user_id,
        categoria='mecanico_domicilio'
    ).first()
    
    if not negocio:
        return jsonify({
            "success": False,
            "error": "No tienes un perfil de mecánico registrado",
            "hint": "Crea un negocio con categoría 'mecanico_domicilio'"
        }), 404
    
    mecanico = MecanicoMecalink.query.filter_by(
        negocio_id=negocio.id_negocio
    ).first()
    
    if not mecanico:
        return jsonify({
            "success": False,
            "error": "Perfil MecaLink no encontrado para tu negocio"
        }), 404
    
    return jsonify({
        "success": True,
        "mecanico": mecanico.to_dict(include_negocio=True)
    })


@mecalink_bp.route('/mi-perfil', methods=['PUT'])
@require_auth
def actualizar_mi_perfil():
    """
    Actualiza el perfil MecaLink del usuario autenticado.
    
    Body JSON (todos opcionales):
        - zonas_texto: Zonas que cubre
        - servicios: Lista de servicios
        - disponibilidad_texto: Horarios disponibles
        - tiene_vehiculo: 'si' o 'no'
        - tiene_herramientas: 'completas', 'algunas', 'no'
        - experiencia: 'menos_1', '1_3', '3_5', '5_10', 'mas_10'
        - precios_servicios: Dict con precios por servicio
    """
    MecanicoMecalink = get_mecalink_model()
    Negocio = get_negocio_model()
    db = get_db()
    
    if not MecanicoMecalink:
        return jsonify({
            "success": False,
            "error": "Servicio MecaLink no disponible"
        }), 503
    
    data = request.get_json() or {}
    
    # Buscar negocio del usuario
    negocio = Negocio.query.filter_by(
        usuario_id=g.user_id,
        categoria='mecanico_domicilio'
    ).first()
    
    if not negocio:
        return jsonify({
            "success": False,
            "error": "No tienes un perfil de mecánico registrado"
        }), 404
    
    mecanico = MecanicoMecalink.query.filter_by(
        negocio_id=negocio.id_negocio
    ).first()
    
    if not mecanico:
        return jsonify({
            "success": False,
            "error": "Perfil MecaLink no encontrado"
        }), 404
    
    # Campos que se pueden actualizar
    campos_permitidos = [
        'zonas_texto', 'servicios', 'disponibilidad_texto',
        'tiene_vehiculo', 'tiene_herramientas', 'experiencia',
        'especialidades', 'certificaciones', 'precios_servicios'
    ]
    
    campos_actualizados = []
    
    for campo in campos_permitidos:
        if campo in data:
            valor = data[campo]
            
            if campo == 'zonas_texto':
                mecanico.zonas_texto = valor
                mecanico.zonas_array = mecanico._normalizar_zonas(valor)
            elif campo == 'tiene_vehiculo':
                mecanico.tiene_vehiculo = valor in ('si', 'true', True)
            else:
                setattr(mecanico, campo, valor)
            
            campos_actualizados.append(campo)
    
    if campos_actualizados:
        try:
            db.session.commit()
            logger.info(f"✅ Perfil MecaLink actualizado: {campos_actualizados}")
            
            return jsonify({
                "success": True,
                "message": "Perfil actualizado correctamente",
                "campos_actualizados": campos_actualizados,
                "mecanico": mecanico.to_dict()
            })
        except Exception as e:
            db.session.rollback()
            logger.error(f"❌ Error actualizando perfil MecaLink: {e}")
            return jsonify({
                "success": False,
                "error": "Error al guardar los cambios"
            }), 500
    else:
        return jsonify({
            "success": True,
            "message": "No se realizaron cambios",
            "mecanico": mecanico.to_dict()
        })


@mecalink_bp.route('/mis-estadisticas', methods=['GET'])
@require_auth
def obtener_mis_estadisticas():
    """
    Obtiene las estadísticas del mecánico autenticado.
    
    Returns:
        Estadísticas: servicios, calificación, ingresos, nivel, etc.
    """
    MecanicoMecalink = get_mecalink_model()
    Negocio = get_negocio_model()
    
    if not MecanicoMecalink:
        return jsonify({
            "success": False,
            "error": "Servicio MecaLink no disponible"
        }), 503
    
    negocio = Negocio.query.filter_by(
        usuario_id=g.user_id,
        categoria='mecanico_domicilio'
    ).first()
    
    if not negocio:
        return jsonify({
            "success": False,
            "error": "No tienes un perfil de mecánico"
        }), 404
    
    mecanico = MecanicoMecalink.query.filter_by(
        negocio_id=negocio.id_negocio
    ).first()
    
    if not mecanico:
        return jsonify({
            "success": False,
            "error": "Perfil MecaLink no encontrado"
        }), 404
    
    nivel_emoji, nivel_nombre = mecanico.get_nivel_badge()
    
    # Calcular servicios para siguiente nivel
    niveles_req = {'nuevo': 11, 'activo': 51, 'experto': 200, 'elite': float('inf')}
    siguiente_nivel = niveles_req.get(mecanico.nivel, 11)
    servicios_para_subir = max(0, siguiente_nivel - mecanico.total_servicios)
    
    return jsonify({
        "success": True,
        "estadisticas": {
            "total_servicios": mecanico.total_servicios,
            "calificacion_promedio": float(mecanico.calificacion_promedio),
            "total_calificaciones": mecanico.total_calificaciones,
            "calificaciones_desglose": mecanico.calificaciones_desglose or {},
            
            "total_ingresos": float(mecanico.total_ingresos_generados),
            "total_comisiones": float(mecanico.total_comisiones_pagadas),
            "comision_porcentaje": float(mecanico.comision_porcentaje),
            
            "nivel": mecanico.nivel,
            "nivel_nombre": nivel_nombre,
            "nivel_emoji": nivel_emoji,
            "servicios_para_siguiente_nivel": servicios_para_subir if servicios_para_subir != float('inf') else 0,
            
            "verificado": mecanico.verificado_mecalink,
            "estado": mecanico.estado,
            "fecha_registro": mecanico.fecha_registro.isoformat() if mecanico.fecha_registro else None
        }
    })


# ═══════════════════════════════════════════════════════════════════════════════
# ENDPOINTS - CALIFICACIONES
# ═══════════════════════════════════════════════════════════════════════════════

@mecalink_bp.route('/calificar/<int:mecanico_id>', methods=['POST'])
@require_auth
def calificar_mecanico(mecanico_id):
    """
    Permite a un usuario calificar a un mecánico después de un servicio.
    
    Body JSON:
        - calificacion (int, requerido): Calificación general 1-5
        - puntualidad (int, opcional): 1-5
        - calidad (int, opcional): 1-5
        - precio (int, opcional): 1-5
        - comunicacion (int, opcional): 1-5
        - comentario (str, opcional): Comentario del servicio
    """
    MecanicoMecalink = get_mecalink_model()
    db = get_db()
    
    if not MecanicoMecalink:
        return jsonify({
            "success": False,
            "error": "Servicio MecaLink no disponible"
        }), 503
    
    data = request.get_json() or {}
    
    mecanico = MecanicoMecalink.query.get(mecanico_id)
    
    if not mecanico:
        return jsonify({
            "success": False,
            "error": "Mecánico no encontrado"
        }), 404
    
    # Validar calificación
    calificacion = data.get('calificacion')
    if calificacion is None:
        return jsonify({
            "success": False,
            "error": "Se requiere la calificación"
        }), 400
    
    try:
        calificacion = int(calificacion)
        if not (1 <= calificacion <= 5):
            raise ValueError()
    except (ValueError, TypeError):
        return jsonify({
            "success": False,
            "error": "La calificación debe ser un número entre 1 y 5"
        }), 400
    
    # Construir desglose de calificaciones
    desglose = {}
    for campo in ['puntualidad', 'calidad', 'precio', 'comunicacion']:
        if campo in data:
            try:
                valor = int(data[campo])
                if 1 <= valor <= 5:
                    desglose[campo] = valor
            except (ValueError, TypeError):
                pass
    
    try:
        # Agregar calificación
        mecanico.agregar_calificacion(calificacion, desglose if desglose else None)
        
        # TODO: Guardar comentario en tabla separada si se necesita
        comentario = data.get('comentario', '').strip()
        
        db.session.commit()
        
        logger.info(f"✅ Calificación registrada: mecánico {mecanico_id}, cal: {calificacion}")
        
        return jsonify({
            "success": True,
            "message": "¡Gracias por tu calificación!",
            "nueva_calificacion_promedio": float(mecanico.calificacion_promedio),
            "total_calificaciones": mecanico.total_calificaciones
        })
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"❌ Error registrando calificación: {e}")
        return jsonify({
            "success": False,
            "error": "Error al registrar la calificación"
        }), 500


# ═══════════════════════════════════════════════════════════════════════════════
# ENDPOINTS ADMIN
# ═══════════════════════════════════════════════════════════════════════════════

@mecalink_bp.route('/admin/pendientes', methods=['GET'])
@require_admin
def listar_pendientes():
    """
    Lista mecánicos pendientes de verificación.
    Solo accesible para administradores.
    """
    MecanicoMecalink = get_mecalink_model()
    
    if not MecanicoMecalink:
        return jsonify({
            "success": False,
            "error": "Servicio MecaLink no disponible"
        }), 503
    
    try:
        pendientes = MecanicoMecalink.query.filter_by(
            estado='pendiente'
        ).order_by(
            MecanicoMecalink.fecha_registro.desc()
        ).all()
        
        return jsonify({
            "success": True,
            "count": len(pendientes),
            "mecanicos": [m.to_dict(include_negocio=True) for m in pendientes]
        })
        
    except Exception as e:
        logger.error(f"❌ Error listando pendientes: {e}")
        return jsonify({
            "success": False,
            "error": "Error al obtener mecánicos pendientes"
        }), 500


@mecalink_bp.route('/admin/verificar/<int:mecanico_id>', methods=['POST'])
@require_admin
def verificar_mecanico(mecanico_id):
    """
    Verifica un mecánico y lo activa en la red MecaLink.
    Solo accesible para administradores.
    """
    MecanicoMecalink = get_mecalink_model()
    db = get_db()
    
    if not MecanicoMecalink:
        return jsonify({
            "success": False,
            "error": "Servicio MecaLink no disponible"
        }), 503
    
    mecanico = MecanicoMecalink.query.get(mecanico_id)
    
    if not mecanico:
        return jsonify({
            "success": False,
            "error": "Mecánico no encontrado"
        }), 404
    
    try:
        mecanico.verificar()
        db.session.commit()
        
        nombre_negocio = mecanico.negocio.nombre_negocio if mecanico.negocio else f"ID {mecanico_id}"
        
        logger.info(f"✅ Mecánico verificado: {nombre_negocio}")
        
        return jsonify({
            "success": True,
            "message": f"Mecánico '{nombre_negocio}' verificado y activado",
            "mecanico": mecanico.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"❌ Error verificando mecánico: {e}")
        return jsonify({
            "success": False,
            "error": "Error al verificar mecánico"
        }), 500


@mecalink_bp.route('/admin/suspender/<int:mecanico_id>', methods=['POST'])
@require_admin
def suspender_mecanico(mecanico_id):
    """
    Suspende un mecánico de la red MecaLink.
    Solo accesible para administradores.
    """
    MecanicoMecalink = get_mecalink_model()
    db = get_db()
    
    if not MecanicoMecalink:
        return jsonify({
            "success": False,
            "error": "Servicio MecaLink no disponible"
        }), 503
    
    data = request.get_json() or {}
    motivo = data.get('motivo', 'Sin motivo especificado')
    
    mecanico = MecanicoMecalink.query.get(mecanico_id)
    
    if not mecanico:
        return jsonify({
            "success": False,
            "error": "Mecánico no encontrado"
        }), 404
    
    try:
        mecanico.suspender(motivo)
        db.session.commit()
        
        logger.info(f"⚠️ Mecánico suspendido: {mecanico_id} - {motivo}")
        
        return jsonify({
            "success": True,
            "message": "Mecánico suspendido",
            "mecanico": mecanico.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"❌ Error suspendiendo mecánico: {e}")
        return jsonify({
            "success": False,
            "error": "Error al suspender mecánico"
        }), 500


# ═══════════════════════════════════════════════════════════════════════════════
# ENDPOINT PARA LISTAR SERVICIOS DISPONIBLES
# ═══════════════════════════════════════════════════════════════════════════════

@mecalink_bp.route('/servicios', methods=['GET'])
def listar_servicios_disponibles():
    """
    Lista los tipos de servicios disponibles en MecaLink.
    Útil para el frontend al mostrar filtros o formularios.
    """
    servicios = [
        {"codigo": "cambio_aceite", "nombre": "Cambio de aceite", "emoji": "🛢️"},
        {"codigo": "diagnostico_scanner", "nombre": "Diagnóstico con escáner", "emoji": "🔍"},
        {"codigo": "revision_electrica", "nombre": "Revisión eléctrica", "emoji": "⚡"},
        {"codigo": "cambio_bateria", "nombre": "Cambio de batería", "emoji": "🔋"},
        {"codigo": "cambio_pastillas", "nombre": "Cambio pastillas de freno", "emoji": "🛞"},
        {"codigo": "revision_previaje", "nombre": "Revisión pre-viaje", "emoji": "🚗"},
        {"codigo": "auxilio_varamiento", "nombre": "Auxilio por varamiento", "emoji": "🆘"},
        {"codigo": "otro_servicio", "nombre": "Otro servicio", "emoji": "🔧"}
    ]
    
    return jsonify({
        "success": True,
        "servicios": servicios
    })


# ═══════════════════════════════════════════════════════════════════════════════
# FIN DEL MÓDULO
# ═══════════════════════════════════════════════════════════════════════════════

logger.info("🔧 MecaLink API cargada correctamente")