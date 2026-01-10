"""
BizFlow Studio - API de Negocios
Modernizado con sistema de autenticación unificado
"""

import logging
import sys
from flask import Blueprint, jsonify, request
from flask_login import current_user
from flask_cors import cross_origin

# Importar el decorador de autenticación del nuevo sistema
# Si ya creaste auth_system.py, descomenta la siguiente línea:
# from src.api.auth.auth_system import require_active_session

from src.models.colombia_data.negocio import Negocio
from src.models.colombia_data.colombia_data import Colombia 
from src.models.colombia_data.sucursales import Sucursal 
from src.models.database import db

# Configuración de logs
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)  # Cambié a INFO para reducir ruido

negocio_api_bp = Blueprint('negocio_api_bp', __name__, url_prefix='/api')

# ==========================================
# FUNCIÓN DE AUTENTICACIÓN HÍBRIDA
# ==========================================
def get_authenticated_user_id():
    """
    Obtiene el ID del usuario autenticado de manera híbrida:
    1. PREFERENCIA: current_user (sesión Flask-Login)
    2. FALLBACK: Header X-User-ID (para compatibilidad temporal)
    
    Returns:
        int or None: ID del usuario autenticado
    """
    # Opción 1: Usuario autenticado vía Flask-Login (RECOMENDADO)
    if current_user.is_authenticated:
        logger.info(f"✅ Usuario autenticado vía sesión: {current_user.correo}")
        return current_user.id_usuario
    
    # Opción 2: Fallback a header (TEMPORAL - para migración gradual)
    user_id = request.headers.get('X-User-ID')
    if user_id:
        logger.warning(f"⚠️ Usuario identificado por header X-User-ID: {user_id} (migrar a sesión)")
        try:
            return int(user_id)
        except (ValueError, TypeError):
            logger.error(f"❌ X-User-ID inválido: {user_id}")
            return None
    
    logger.warning("❌ No se pudo identificar al usuario (sin sesión ni header)")
    return None

# ==========================================
# ENDPOINT 1: CIUDADES (PÚBLICO)
# ==========================================
@negocio_api_bp.route('/ciudades', methods=['GET', 'OPTIONS'])
@cross_origin(supports_credentials=True)
def get_ciudades():
    """
    Obtiene lista de ciudades de Colombia con búsqueda.
    Endpoint PÚBLICO (no requiere autenticación).
    
    Query params:
        q (str): Término de búsqueda
    
    Returns:
        200: Lista de ciudades
    """
    if request.method == 'OPTIONS':
        return jsonify({"success": True}), 200
    
    try:
        termino = request.args.get('q', '').strip()
        
        # Query base
        query = Colombia.query.with_entities(
            Colombia.ciudad_id, 
            Colombia.ciudad_nombre
        )
        
        # Filtrar por término de búsqueda
        if termino:
            query = query.filter(
                Colombia.ciudad_nombre.ilike(f"%{termino}%")
            )
        
        # Limitar resultados
        ciudades_db = query.limit(20).all()
        
        # Serializar
        resultado = [
            {
                "id": c.ciudad_id, 
                "nombre": c.ciudad_nombre
            } 
            for c in ciudades_db
        ]
        
        logger.info(f"✅ Ciudades encontradas: {len(resultado)} (término: '{termino}')")
        return jsonify(resultado), 200
    
    except Exception as e:
        logger.error(f"❌ Error en /ciudades: {str(e)}", exc_info=True)
        return jsonify({"error": "Error al buscar ciudades"}), 500

# ==========================================
# ENDPOINT 2: CONFIGURACIÓN DE PÁGINA
# ==========================================
@negocio_api_bp.route('/configuracion-pagina/<int:negocio_id>', methods=['GET', 'OPTIONS'])
@cross_origin(supports_credentials=True)
# TODO: Agregar @require_active_session cuando migres completamente
def obtener_configuracion_pagina(negocio_id):
    """
    Obtiene la configuración de micrositio de un negocio.
    Requiere autenticación.
    """
    if request.method == 'OPTIONS':
        return jsonify({"success": True}), 200
    
    try:
        # Obtener usuario autenticado
        user_id = get_authenticated_user_id()
        if not user_id:
            return jsonify({
                "success": False, 
                "error": "No autorizado. Inicia sesión."
            }), 401
        
        # Buscar negocio del usuario
        negocio = Negocio.query.filter_by(
            id_negocio=negocio_id, 
            usuario_id=user_id
        ).first()
        
        if not negocio:
            logger.warning(f"❌ Negocio {negocio_id} no encontrado para usuario {user_id}")
            return jsonify({
                "success": False, 
                "error": "Negocio no encontrado o acceso denegado"
            }), 404
        
        # Respuesta
        return jsonify({
            "success": True,
            "has_page": getattr(negocio, 'tiene_pagina', False),
            "slug": getattr(negocio, 'slug', None),
            "plantilla_id": getattr(negocio, 'plantilla_id', None)
        }), 200
    
    except Exception as e:
        logger.error(f"❌ Error en /configuracion-pagina: {str(e)}", exc_info=True)
        return jsonify({"success": False, "error": "Error interno"}), 500

# ==========================================
# ENDPOINT 3: PUBLICAR PÁGINA
# ==========================================
@negocio_api_bp.route('/publicar-pagina', methods=['POST', 'OPTIONS'])
@cross_origin(supports_credentials=True)
def publicar_pagina():
    """
    Publica/actualiza el micrositio de un negocio.
    """
    if request.method == 'OPTIONS':
        return jsonify({"success": True}), 200
    
    try:
        user_id = get_authenticated_user_id()
        if not user_id:
            return jsonify({"success": False, "error": "No autorizado"}), 401
        
        data = request.get_json()
        if not data:
            return jsonify({"success": False, "error": "Datos requeridos"}), 400
        
        negocio_id = data.get('id_negocio')
        plantilla_id = data.get('plantilla_id')
        
        # Validar negocio
        negocio = Negocio.query.filter_by(
            id_negocio=negocio_id, 
            usuario_id=user_id
        ).first()
        
        if not negocio:
            return jsonify({"success": False, "error": "Acceso denegado"}), 403
        
        # Actualizar configuración
        negocio.tiene_pagina = True
        negocio.plantilla_id = plantilla_id
        
        # Generar slug si no existe
        if not negocio.slug:
            negocio.slug = negocio.nombre_negocio.lower()\
                .replace(" ", "-")\
                .replace("á", "a").replace("é", "e").replace("í", "i")\
                .replace("ó", "o").replace("ú", "u")
        
        db.session.commit()
        
        logger.info(f"✅ Página publicada: {negocio.slug}")
        return jsonify({
            "success": True, 
            "slug": negocio.slug
        }), 200
    
    except Exception as e:
        db.session.rollback()
        logger.error(f"❌ Error en /publicar-pagina: {str(e)}", exc_info=True)
        return jsonify({"success": False, "error": str(e)}), 500

# ==========================================
# ENDPOINT 4: REGISTRAR NEGOCIO
# ==========================================
@negocio_api_bp.route('/registrar_negocio', methods=['POST', 'OPTIONS'])
@cross_origin(supports_credentials=True)
def registrar_negocio():
    """
    Registra un nuevo negocio para el usuario autenticado.
    """
    if request.method == 'OPTIONS':
        return jsonify({"success": True}), 200
    
    try:
        user_id = get_authenticated_user_id()
        if not user_id:
            return jsonify({
                "success": False, 
                "error": "Debes iniciar sesión para crear un negocio"
            }), 401
        
        data = request.get_json()
        if not data:
            return jsonify({"success": False, "error": "Datos requeridos"}), 400
        
        # Validar campos requeridos
        nombre = data.get('nombre_negocio')
        if not nombre:
            return jsonify({
                "success": False, 
                "error": "El nombre del negocio es requerido"
            }), 400
        
        # Crear negocio
        nuevo_negocio = Negocio(
            nombre_negocio=nombre,
            categoria=data.get('tipo_negocio') or data.get('categoria', 'General'),
            descripcion=data.get('descripcion', ''),
            direccion=data.get('direccion', ''),
            ciudad_id=int(data.get('ciudad_id')) if data.get('ciudad_id') else None,
            telefono=data.get('telefono', ''),
            usuario_id=user_id
        )
        
        db.session.add(nuevo_negocio)
        db.session.commit()
        
        logger.info(f"✅ Negocio creado: {nuevo_negocio.nombre_negocio} (ID: {nuevo_negocio.id_negocio})")
        
        return jsonify({
            "status": "success",
            "success": True,
            "id": nuevo_negocio.id_negocio,
            "nombre": nuevo_negocio.nombre_negocio
        }), 201
    
    except Exception as e:
        db.session.rollback()
        logger.error(f"❌ Error en /registrar_negocio: {str(e)}", exc_info=True)
        return jsonify({"error": str(e)}), 500

# ==========================================
# ENDPOINT 5: MIS NEGOCIOS
# ==========================================
@negocio_api_bp.route('/mis_negocios', methods=['GET', 'OPTIONS'])
@cross_origin(supports_credentials=True)
def obtener_mis_negocios():
    """
    Obtiene todos los negocios del usuario autenticado.
    """
    if request.method == 'OPTIONS':
        return jsonify({"success": True}), 200
    
    try:
        user_id = get_authenticated_user_id()
        if not user_id:
            return jsonify({
                "error": "unauthorized",
                "message": "Debes iniciar sesión"
            }), 401
        
        # Obtener negocios del usuario
        negocios = Negocio.query.filter_by(usuario_id=user_id).all()
        
        logger.info(f"✅ Negocios encontrados para usuario {user_id}: {len(negocios)}")
        
        return jsonify([n.serialize() for n in negocios]), 200
    
    except Exception as e:
        logger.error(f"❌ Error en /mis_negocios: {str(e)}", exc_info=True)
        return jsonify({"error": str(e)}), 500

# ==========================================
# ENDPOINT 6: REGISTRAR SUCURSAL
# ==========================================
@negocio_api_bp.route('/registrar_sucursal', methods=['POST', 'OPTIONS'])
@cross_origin(supports_credentials=True)
def registrar_sucursal():
    """
    Registra una nueva sucursal para un negocio.
    """
    if request.method == 'OPTIONS':
        return jsonify({"success": True}), 200
    
    try:
        user_id = get_authenticated_user_id()
        if not user_id:
            return jsonify({"error": "No autorizado"}), 401
        
        data = request.get_json()
        negocio_id = data.get('negocio_id')
        
        # Validar que el negocio pertenezca al usuario
        negocio = Negocio.query.filter_by(
            id_negocio=negocio_id, 
            usuario_id=user_id
        ).first()
        
        if not negocio:
            return jsonify({"error": "Negocio no encontrado o acceso denegado"}), 403
        
        # Crear sucursal
        nueva_sucursal = Sucursal(
            nombre_sucursal=data.get('nombre_sucursal'),
            direccion=data.get('direccion', ''),
            telefono=data.get('telefono', ''),
            ciudad=data.get('ciudadSucursal') or data.get('ciudad', ''),
            departamento=data.get('departamento', ''),
            codigo_postal=data.get('codigo_postal', ''),
            activo=data.get('activo', True),
            es_principal=data.get('es_principal', False),
            negocio_id=int(negocio_id)
        )
        
        db.session.add(nueva_sucursal)
        db.session.commit()
        
        logger.info(f"✅ Sucursal creada: {nueva_sucursal.nombre_sucursal}")
        
        return jsonify({
            "status": "success",
            "id": nueva_sucursal.id_sucursal
        }), 201
    
    except Exception as e:
        db.session.rollback()
        logger.error(f"❌ Error en /registrar_sucursal: {str(e)}", exc_info=True)
        return jsonify({"error": str(e)}), 500

# ==========================================
# ENDPOINT 7: OBTENER SUCURSALES
# ==========================================
@negocio_api_bp.route('/negocios/<int:negocio_id>/sucursales', methods=['GET', 'OPTIONS'])
@cross_origin(supports_credentials=True)
def obtener_sucursales(negocio_id):
    """
    Obtiene todas las sucursales de un negocio.
    """
    if request.method == 'OPTIONS':
        return jsonify({"success": True}), 200
    
    try:
        user_id = get_authenticated_user_id()
        if not user_id:
            return jsonify({
                "error": "No autorizado",
                "message": "Debes iniciar sesión"
            }), 401
        
        # Validar acceso al negocio
        negocio = Negocio.query.filter_by(
            id_negocio=negocio_id, 
            usuario_id=user_id
        ).first()
        
        if not negocio:
            return jsonify({"error": "Acceso denegado"}), 403
        
        # Obtener sucursales
        sucursales = Sucursal.query.filter_by(negocio_id=negocio_id).all()
        
        logger.info(f"✅ Sucursales encontradas: {len(sucursales)}")
        
        return jsonify([s.to_dict() for s in sucursales]), 200
    
    except Exception as e:
        logger.error(f"❌ Error en /obtener_sucursales: {str(e)}", exc_info=True)
        return jsonify({"error": "Error al obtener sucursales"}), 500

# ==========================================
# HEALTH CHECK
# ==========================================
@negocio_api_bp.route('/negocio/health', methods=['GET'])
def negocio_health():
    """Health check del módulo de negocios"""
    return jsonify({
        "status": "online",
        "module": "negocios",
        "version": "2.0.0"
    }), 200