"""
BizFlow Studio - API de Gestión de Negocios y Sucursales
Sistema completo para multi-tenancy (múltiples negocios por usuario)

VERSIÓN PARCHADA - Incluye soporte para:
- tiene_pagina, slug, whatsapp, tipo_pagina, logo_url
"""

import logging
from datetime import datetime
from flask import Blueprint, request, jsonify
from flask_cors import cross_origin
from flask_login import current_user, login_required
from sqlalchemy import func
from src.models.database import db
from src.models.colombia_data.negocio import Negocio
from src.models.colombia_data.sucursales import Sucursal
from src.models.colombia_data.colombia_data import Colombia
import unicodedata
import re

# Configuración del Logger
logger = logging.getLogger(__name__)

# Blueprint
negocio_api_bp = Blueprint('negocio_api_bp', __name__)


# ==========================================
# HELPERS
# ==========================================

def normalizar_texto(texto):
    """Normaliza texto removiendo acentos y convirtiendo a minúsculas."""
    if not texto:
        return ""
    texto = texto.lower().strip()
    texto = unicodedata.normalize('NFD', texto)
    texto = ''.join(c for c in texto if unicodedata.category(c) != 'Mn')
    texto = re.sub(r'[^a-z0-9\s]', '', texto)
    return texto


def generar_slug(texto):
    """Genera un slug URL-friendly desde un texto."""
    if not texto:
        return ""
    
    # Normalizar y limpiar
    slug = texto.lower().strip()
    slug = unicodedata.normalize('NFD', slug)
    slug = ''.join(c for c in slug if unicodedata.category(c) != 'Mn')  # Quitar acentos
    slug = re.sub(r'[^a-z0-9]+', '-', slug)  # Reemplazar caracteres especiales
    slug = re.sub(r'-+', '-', slug)  # Eliminar guiones múltiples
    slug = slug.strip('-')  # Quitar guiones al inicio/final
    
    return slug[:50]  # Limitar longitud


def buscar_ciudad_flexible(nombre_ciudad):
    """Busca una ciudad de forma flexible (case-insensitive, sin acentos)."""
    if not nombre_ciudad:
        return None
    
    nombre_normalizado = normalizar_texto(nombre_ciudad)
    
    # Búsqueda exacta case-insensitive
    ciudad = Colombia.query.filter(
        func.lower(Colombia.ciudad_nombre) == nombre_ciudad.strip().lower()
    ).first()
    
    if ciudad:
        return ciudad
    
    # Búsqueda parcial
    ciudad = Colombia.query.filter(
        Colombia.ciudad_nombre.ilike(f"%{nombre_ciudad.strip()}%")
    ).first()
    
    if ciudad:
        return ciudad
    
    # Búsqueda normalizada
    todas_ciudades = Colombia.query.all()
    for c in todas_ciudades:
        if normalizar_texto(c.ciudad_nombre) == nombre_normalizado:
            return c
    
    return None


def get_current_user_id():
    """Obtiene el ID del usuario actual de forma segura."""
    if current_user.is_authenticated:
        return current_user.id_usuario
    
    # Fallback: Header (para compatibilidad)
    user_id = request.headers.get('X-User-ID')
    if user_id and user_id.isdigit():
        return int(user_id)
    
    return None


def serialize_negocio(negocio, include_sucursales=False):
    """Serializa un negocio a JSON."""
    data = {
        "id": negocio.id_negocio,
        "id_negocio": negocio.id_negocio,
        "nombre": negocio.nombre_negocio,
        "nombre_negocio": negocio.nombre_negocio,
        "descripcion": negocio.descripcion,
        "direccion": negocio.direccion,
        "telefono": negocio.telefono,
        "categoria": negocio.categoria,
        "ciudad_id": negocio.ciudad_id,
        "activo": negocio.activo,
        "tiene_pagina": negocio.tiene_pagina,
        "slug": negocio.slug,
        "color_tema": negocio.color_tema,
        "whatsapp": getattr(negocio, 'whatsapp', None),
        "tipo_pagina": getattr(negocio, 'tipo_pagina', None),
        "logo_url": getattr(negocio, 'logo_url', None),
        "fecha_registro": negocio.fecha_registro.isoformat() if negocio.fecha_registro else None,
        "url_sitio": f"/sitio/{negocio.slug}" if negocio.tiene_pagina and negocio.slug else None
    }
    
    # Agregar nombre de ciudad si existe
    if negocio.ciudad:
        data["ciudad_nombre"] = negocio.ciudad.ciudad_nombre
    
    # Agregar sucursales si se solicita
    if include_sucursales:
        sucursales = Sucursal.query.filter_by(negocio_id=negocio.id_negocio, activo=True).all()
        data["sucursales"] = [serialize_sucursal(s) for s in sucursales]
        data["sucursales_count"] = len(sucursales)
    
    return data


def serialize_sucursal(sucursal):
    """Serializa una sucursal a JSON."""
    return {
        "id": sucursal.id_sucursal,
        "id_sucursal": sucursal.id_sucursal,
        "nombre": sucursal.nombre_sucursal,
        "nombre_sucursal": sucursal.nombre_sucursal,
        "direccion": sucursal.direccion,
        "ciudad": sucursal.ciudad,
        "departamento": sucursal.departamento,
        "telefono": sucursal.telefono,
        "email": sucursal.email,
        "activo": sucursal.activo,
        "es_principal": sucursal.es_principal,
        "negocio_id": sucursal.negocio_id,
        "cajeros": sucursal.cajeros or [],
        "administradores": sucursal.administradores or [],
        "total_personal": sucursal.get_total_personal(),
        "fecha_registro": sucursal.fecha_registro.isoformat() if sucursal.fecha_registro else None
    }


# ==========================================
# ENDPOINTS DE NEGOCIOS
# ==========================================

@negocio_api_bp.route('/negocio/health', methods=['GET'])
def negocio_health():
    """Health check del módulo de negocios."""
    return jsonify({
        "status": "online",
        "module": "negocios_sucursales",
        "version": "2.1.0"  # Versión actualizada con parche
    }), 200


@negocio_api_bp.route('/mis_negocios', methods=['GET', 'OPTIONS'])
@cross_origin(supports_credentials=True)
def obtener_mis_negocios():
    """
    Obtiene todos los negocios del usuario autenticado.
    
    Query params:
        include_sucursales (bool): Si incluir las sucursales de cada negocio
    
    Returns:
        200: Lista de negocios
        401: No autenticado
    """
    if request.method == 'OPTIONS':
        return jsonify({"success": True}), 200
    
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({
            "success": False,
            "error": "No autenticado"
        }), 401
    
    try:
        include_sucursales = request.args.get('include_sucursales', 'false').lower() == 'true'
        
        negocios = Negocio.query.filter_by(
            usuario_id=user_id,
            activo=True
        ).order_by(Negocio.nombre_negocio).all()
        
        data = [serialize_negocio(n, include_sucursales) for n in negocios]
        
        logger.info(f"✅ Negocios obtenidos para usuario {user_id}: {len(data)}")
        
        return jsonify({
            "success": True,
            "data": data,
            "total": len(data)
        }), 200
        
    except Exception as e:
        logger.error(f"❌ Error obteniendo negocios: {e}")
        return jsonify({
            "success": False,
            "error": "Error al obtener negocios"
        }), 500


@negocio_api_bp.route('/negocio/<int:negocio_id>', methods=['GET', 'OPTIONS'])
@cross_origin(supports_credentials=True)
def obtener_negocio(negocio_id):
    """
    Obtiene un negocio específico por ID.
    
    Returns:
        200: Datos del negocio
        404: Negocio no encontrado
    """
    if request.method == 'OPTIONS':
        return jsonify({"success": True}), 200
    
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"success": False, "error": "No autenticado"}), 401
    
    try:
        negocio = Negocio.query.filter_by(
            id_negocio=negocio_id,
            usuario_id=user_id
        ).first()
        
        if not negocio:
            return jsonify({
                "success": False,
                "error": "Negocio no encontrado"
            }), 404
        
        return jsonify({
            "success": True,
            "data": serialize_negocio(negocio, include_sucursales=True)
        }), 200
        
    except Exception as e:
        logger.error(f"❌ Error obteniendo negocio: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@negocio_api_bp.route('/registrar_negocio', methods=['POST', 'OPTIONS'])
@cross_origin(supports_credentials=True)
def registrar_negocio():
    """
    Registra un nuevo negocio para el usuario autenticado.
    También crea automáticamente una sucursal principal.
    
    Request body:
        {
            "nombre_negocio": "Mi Tienda",
            "descripcion": "Descripción...",
            "direccion": "Calle 123",
            "telefono": "3001234567",
            "categoria": "tienda_ropa",
            "ciudad": "Bogotá" o ciudad_id: 37
        }
    
    Returns:
        201: Negocio creado exitosamente
        400: Datos inválidos
        401: No autenticado
    """
    if request.method == 'OPTIONS':
        return jsonify({"success": True}), 200
    
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({
            "success": False,
            "error": "Debes iniciar sesión para registrar un negocio"
        }), 401
    
    try:
        data = request.get_json()
        if not data:
            return jsonify({"success": False, "error": "No se recibieron datos"}), 400
        
        # Validar nombre del negocio
        nombre_negocio = data.get('nombre_negocio', '').strip()
        if not nombre_negocio:
            return jsonify({
                "success": False,
                "error": "El nombre del negocio es requerido"
            }), 400
        
        # Verificar si ya existe un negocio con ese nombre para este usuario
        existe = Negocio.query.filter_by(
            nombre_negocio=nombre_negocio,
            usuario_id=user_id
        ).first()
        
        if existe:
            return jsonify({
                "success": False,
                "error": f"Ya tienes un negocio llamado '{nombre_negocio}'"
            }), 409
        
        # Buscar ciudad
        ciudad_id = data.get('ciudad_id')
        if not ciudad_id and data.get('ciudad'):
            ciudad_obj = buscar_ciudad_flexible(data['ciudad'])
            if ciudad_obj:
                ciudad_id = ciudad_obj.ciudad_id
            else:
                return jsonify({
                    "success": False,
                    "error": f"Ciudad '{data['ciudad']}' no encontrada"
                }), 400
        
        if not ciudad_id:
            return jsonify({
                "success": False,
                "error": "La ciudad es requerida"
            }), 400
        
        # Crear el negocio
        nuevo_negocio = Negocio(
            nombre_negocio=nombre_negocio,
            usuario_id=user_id,
            descripcion=data.get('descripcion', ''),
            direccion=data.get('direccion', ''),
            telefono=data.get('telefono', ''),
            categoria=data.get('categoria') or data.get('tipoNegocio', 'General'),
            ciudad_id=ciudad_id
        )
        
        db.session.add(nuevo_negocio)
        db.session.flush()  # Para obtener el ID del negocio
        
        # Crear sucursal principal automáticamente
        sucursal_principal = Sucursal(
            nombre_sucursal="Principal",
            negocio_id=nuevo_negocio.id_negocio,
            direccion=data.get('direccion', ''),
            ciudad=data.get('ciudad', ''),
            telefono=data.get('telefono', ''),
            es_principal=True,
            activo=True
        )
        
        db.session.add(sucursal_principal)
        db.session.commit()
        
        logger.info(f"✅ Negocio creado: {nombre_negocio} (ID: {nuevo_negocio.id_negocio}) por usuario {user_id}")
        
        return jsonify({
            "success": True,
            "message": f"Negocio '{nombre_negocio}' registrado exitosamente",
            "data": {
                "negocio": serialize_negocio(nuevo_negocio),
                "sucursal_principal": serialize_sucursal(sucursal_principal)
            }
        }), 201
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"❌ Error registrando negocio: {e}", exc_info=True)
        return jsonify({
            "success": False,
            "error": "Error al registrar el negocio"
        }), 500


@negocio_api_bp.route('/negocio/<int:negocio_id>', methods=['PUT', 'OPTIONS'])
@cross_origin(supports_credentials=True)
def actualizar_negocio(negocio_id):
    """
    Actualiza un negocio existente.
    
    Campos soportados:
        - nombre_negocio
        - descripcion
        - direccion
        - telefono
        - categoria
        - color_tema
        - tiene_pagina (NUEVO)
        - slug (NUEVO)
        - whatsapp (NUEVO)
        - tipo_pagina (NUEVO)
        - logo_url (NUEVO)
    """
    if request.method == 'OPTIONS':
        return jsonify({"success": True}), 200
    
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"success": False, "error": "No autenticado"}), 401
    
    try:
        negocio = Negocio.query.filter_by(
            id_negocio=negocio_id,
            usuario_id=user_id
        ).first()
        
        if not negocio:
            return jsonify({"success": False, "error": "Negocio no encontrado"}), 404
        
        data = request.get_json()
        
        # ==========================================
        # CAMPOS BÁSICOS
        # ==========================================
        if 'nombre_negocio' in data:
            negocio.nombre_negocio = data['nombre_negocio']
        if 'descripcion' in data:
            negocio.descripcion = data['descripcion']
        if 'direccion' in data:
            negocio.direccion = data['direccion']
        if 'telefono' in data:
            negocio.telefono = data['telefono']
        if 'categoria' in data:
            negocio.categoria = data['categoria']
        if 'color_tema' in data:
            negocio.color_tema = data['color_tema']
        
        # ==========================================
        # CAMPOS PARA MICROSITIO / TIENDA ONLINE
        # ==========================================
        if 'tiene_pagina' in data:
            negocio.tiene_pagina = data['tiene_pagina']
        
        if 'slug' in data:
            # Verificar que el slug no esté en uso por otro negocio
            slug_existente = Negocio.query.filter(
                Negocio.slug == data['slug'],
                Negocio.id_negocio != negocio_id
            ).first()
            
            if slug_existente:
                return jsonify({
                    "success": False, 
                    "error": f"El slug '{data['slug']}' ya está en uso"
                }), 409
            
            negocio.slug = data['slug']
        
        if 'whatsapp' in data:
            negocio.whatsapp = data['whatsapp']
        
        if 'tipo_pagina' in data:
            negocio.tipo_pagina = data['tipo_pagina']
        
        if 'logo_url' in data:
            negocio.logo_url = data['logo_url']
        
        # ==========================================
        # GENERAR SLUG AUTOMÁTICO SI SE ACTIVA PÁGINA
        # ==========================================
        if data.get('tiene_pagina') and not negocio.slug:
            # Generar slug desde el nombre
            base_slug = generar_slug(negocio.nombre_negocio)
            
            # Verificar unicidad
            slug_final = base_slug
            contador = 1
            while Negocio.query.filter(
                Negocio.slug == slug_final,
                Negocio.id_negocio != negocio_id
            ).first():
                slug_final = f"{base_slug}-{contador}"
                contador += 1
            
            negocio.slug = slug_final
        
        db.session.commit()
        
        logger.info(f"✅ Negocio actualizado: {negocio.nombre_negocio} (tiene_pagina={negocio.tiene_pagina}, slug={negocio.slug})")
        
        return jsonify({
            "success": True,
            "message": "Negocio actualizado",
            "data": serialize_negocio(negocio)
        }), 200
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"❌ Error actualizando negocio: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@negocio_api_bp.route('/negocio/<int:negocio_id>', methods=['DELETE', 'OPTIONS'])
@cross_origin(supports_credentials=True)
def eliminar_negocio(negocio_id):
    """
    Desactiva un negocio (soft delete).
    """
    if request.method == 'OPTIONS':
        return jsonify({"success": True}), 200
    
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"success": False, "error": "No autenticado"}), 401
    
    try:
        negocio = Negocio.query.filter_by(
            id_negocio=negocio_id,
            usuario_id=user_id
        ).first()
        
        if not negocio:
            return jsonify({"success": False, "error": "Negocio no encontrado"}), 404
        
        # Soft delete
        negocio.activo = False
        
        # También desactivar sucursales
        Sucursal.query.filter_by(negocio_id=negocio_id).update({"activo": False})
        
        db.session.commit()
        
        logger.info(f"✅ Negocio desactivado: {negocio.nombre_negocio}")
        
        return jsonify({
            "success": True,
            "message": "Negocio eliminado"
        }), 200
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"❌ Error eliminando negocio: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


# ==========================================
# ENDPOINTS DE SUCURSALES
# ==========================================

@negocio_api_bp.route('/negocios/<int:negocio_id>/sucursales', methods=['GET', 'OPTIONS'])
@cross_origin(supports_credentials=True)
def obtener_sucursales(negocio_id):
    """
    Obtiene todas las sucursales de un negocio.
    """
    if request.method == 'OPTIONS':
        return jsonify({"success": True}), 200
    
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"success": False, "error": "No autenticado"}), 401
    
    try:
        # Verificar que el negocio pertenece al usuario
        negocio = Negocio.query.filter_by(
            id_negocio=negocio_id,
            usuario_id=user_id
        ).first()
        
        if not negocio:
            return jsonify({"success": False, "error": "Negocio no encontrado"}), 404
        
        sucursales = Sucursal.query.filter_by(
            negocio_id=negocio_id,
            activo=True
        ).order_by(Sucursal.es_principal.desc(), Sucursal.nombre_sucursal).all()
        
        return jsonify({
            "success": True,
            "data": [serialize_sucursal(s) for s in sucursales],
            "total": len(sucursales),
            "negocio": {
                "id": negocio.id_negocio,
                "nombre": negocio.nombre_negocio
            }
        }), 200
        
    except Exception as e:
        logger.error(f"❌ Error obteniendo sucursales: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@negocio_api_bp.route('/registrar_sucursal', methods=['POST', 'OPTIONS'])
@cross_origin(supports_credentials=True)
def registrar_sucursal():
    """
    Registra una nueva sucursal para un negocio.
    
    Request body:
        {
            "negocio_id": 1,
            "nombre_sucursal": "Sucursal Norte",
            "direccion": "Calle 100 #15-20",
            "ciudad": "Bogotá",
            "departamento": "Cundinamarca",
            "telefono": "3001234567",
            "email": "norte@minegocio.com"
        }
    """
    if request.method == 'OPTIONS':
        return jsonify({"success": True}), 200
    
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"success": False, "error": "No autenticado"}), 401
    
    try:
        data = request.get_json()
        if not data:
            return jsonify({"success": False, "error": "No se recibieron datos"}), 400
        
        negocio_id = data.get('negocio_id')
        nombre_sucursal = data.get('nombre_sucursal', '').strip()
        
        if not negocio_id:
            return jsonify({"success": False, "error": "negocio_id es requerido"}), 400
        
        if not nombre_sucursal:
            return jsonify({"success": False, "error": "nombre_sucursal es requerido"}), 400
        
        # Verificar que el negocio pertenece al usuario
        negocio = Negocio.query.filter_by(
            id_negocio=negocio_id,
            usuario_id=user_id
        ).first()
        
        if not negocio:
            return jsonify({"success": False, "error": "Negocio no encontrado"}), 404
        
        # Verificar que no existe una sucursal con ese nombre en el mismo negocio
        existe = Sucursal.query.filter_by(
            negocio_id=negocio_id,
            nombre_sucursal=nombre_sucursal
        ).first()
        
        if existe:
            return jsonify({
                "success": False,
                "error": f"Ya existe una sucursal llamada '{nombre_sucursal}' en este negocio"
            }), 409
        
        # Verificar si es la primera sucursal (será principal)
        es_primera = Sucursal.query.filter_by(negocio_id=negocio_id).count() == 0
        
        # Crear sucursal
        nueva_sucursal = Sucursal(
            nombre_sucursal=nombre_sucursal,
            negocio_id=negocio_id,
            direccion=data.get('direccion', ''),
            ciudad=data.get('ciudad', ''),
            departamento=data.get('departamento', ''),
            telefono=data.get('telefono', ''),
            email=data.get('email', ''),
            es_principal=es_primera or data.get('es_principal', False),
            activo=True
        )
        
        db.session.add(nueva_sucursal)
        db.session.commit()
        
        logger.info(f"✅ Sucursal creada: {nombre_sucursal} para negocio {negocio.nombre_negocio}")
        
        return jsonify({
            "success": True,
            "message": f"Sucursal '{nombre_sucursal}' creada exitosamente",
            "data": serialize_sucursal(nueva_sucursal)
        }), 201
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"❌ Error registrando sucursal: {e}", exc_info=True)
        return jsonify({"success": False, "error": str(e)}), 500


@negocio_api_bp.route('/sucursal/<int:sucursal_id>', methods=['GET', 'OPTIONS'])
@cross_origin(supports_credentials=True)
def obtener_sucursal(sucursal_id):
    """
    Obtiene una sucursal específica.
    """
    if request.method == 'OPTIONS':
        return jsonify({"success": True}), 200
    
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"success": False, "error": "No autenticado"}), 401
    
    try:
        sucursal = Sucursal.query.filter_by(id_sucursal=sucursal_id).first()
        
        if not sucursal:
            return jsonify({"success": False, "error": "Sucursal no encontrada"}), 404
        
        # Verificar que el negocio pertenece al usuario
        negocio = Negocio.query.filter_by(
            id_negocio=sucursal.negocio_id,
            usuario_id=user_id
        ).first()
        
        if not negocio:
            return jsonify({"success": False, "error": "Acceso denegado"}), 403
        
        return jsonify({
            "success": True,
            "data": serialize_sucursal(sucursal)
        }), 200
        
    except Exception as e:
        logger.error(f"❌ Error obteniendo sucursal: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@negocio_api_bp.route('/sucursal/<int:sucursal_id>', methods=['PUT', 'OPTIONS'])
@cross_origin(supports_credentials=True)
def actualizar_sucursal(sucursal_id):
    """
    Actualiza una sucursal existente.
    """
    if request.method == 'OPTIONS':
        return jsonify({"success": True}), 200
    
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"success": False, "error": "No autenticado"}), 401
    
    try:
        sucursal = Sucursal.query.filter_by(id_sucursal=sucursal_id).first()
        
        if not sucursal:
            return jsonify({"success": False, "error": "Sucursal no encontrada"}), 404
        
        # Verificar permisos
        negocio = Negocio.query.filter_by(
            id_negocio=sucursal.negocio_id,
            usuario_id=user_id
        ).first()
        
        if not negocio:
            return jsonify({"success": False, "error": "Acceso denegado"}), 403
        
        data = request.get_json()
        
        # Actualizar campos
        if 'nombre_sucursal' in data:
            sucursal.nombre_sucursal = data['nombre_sucursal']
        if 'direccion' in data:
            sucursal.direccion = data['direccion']
        if 'ciudad' in data:
            sucursal.ciudad = data['ciudad']
        if 'departamento' in data:
            sucursal.departamento = data['departamento']
        if 'telefono' in data:
            sucursal.telefono = data['telefono']
        if 'email' in data:
            sucursal.email = data['email']
        if 'cajeros' in data:
            sucursal.cajeros = data['cajeros']
        if 'administradores' in data:
            sucursal.administradores = data['administradores']
        
        db.session.commit()
        
        logger.info(f"✅ Sucursal actualizada: {sucursal.nombre_sucursal}")
        
        return jsonify({
            "success": True,
            "message": "Sucursal actualizada",
            "data": serialize_sucursal(sucursal)
        }), 200
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"❌ Error actualizando sucursal: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@negocio_api_bp.route('/sucursal/<int:sucursal_id>', methods=['DELETE', 'OPTIONS'])
@cross_origin(supports_credentials=True)
def eliminar_sucursal(sucursal_id):
    """
    Desactiva una sucursal (soft delete).
    No se puede eliminar la sucursal principal si es la única.
    """
    if request.method == 'OPTIONS':
        return jsonify({"success": True}), 200
    
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"success": False, "error": "No autenticado"}), 401
    
    try:
        sucursal = Sucursal.query.filter_by(id_sucursal=sucursal_id).first()
        
        if not sucursal:
            return jsonify({"success": False, "error": "Sucursal no encontrada"}), 404
        
        # Verificar permisos
        negocio = Negocio.query.filter_by(
            id_negocio=sucursal.negocio_id,
            usuario_id=user_id
        ).first()
        
        if not negocio:
            return jsonify({"success": False, "error": "Acceso denegado"}), 403
        
        # No permitir eliminar la única sucursal
        total_sucursales = Sucursal.query.filter_by(
            negocio_id=sucursal.negocio_id,
            activo=True
        ).count()
        
        if total_sucursales <= 1:
            return jsonify({
                "success": False,
                "error": "No puedes eliminar la única sucursal del negocio"
            }), 400
        
        # Soft delete
        sucursal.activo = False
        
        # Si era la principal, asignar otra como principal
        if sucursal.es_principal:
            otra_sucursal = Sucursal.query.filter(
                Sucursal.negocio_id == sucursal.negocio_id,
                Sucursal.id_sucursal != sucursal_id,
                Sucursal.activo == True
            ).first()
            
            if otra_sucursal:
                otra_sucursal.es_principal = True
        
        db.session.commit()
        
        logger.info(f"✅ Sucursal desactivada: {sucursal.nombre_sucursal}")
        
        return jsonify({
            "success": True,
            "message": "Sucursal eliminada"
        }), 200
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"❌ Error eliminando sucursal: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@negocio_api_bp.route('/sucursal/<int:sucursal_id>/set_principal', methods=['POST', 'OPTIONS'])
@cross_origin(supports_credentials=True)
def establecer_sucursal_principal(sucursal_id):
    """
    Establece una sucursal como la principal del negocio.
    """
    if request.method == 'OPTIONS':
        return jsonify({"success": True}), 200
    
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"success": False, "error": "No autenticado"}), 401
    
    try:
        sucursal = Sucursal.query.filter_by(id_sucursal=sucursal_id).first()
        
        if not sucursal:
            return jsonify({"success": False, "error": "Sucursal no encontrada"}), 404
        
        # Verificar permisos
        negocio = Negocio.query.filter_by(
            id_negocio=sucursal.negocio_id,
            usuario_id=user_id
        ).first()
        
        if not negocio:
            return jsonify({"success": False, "error": "Acceso denegado"}), 403
        
        # Quitar principal de todas las sucursales del negocio
        Sucursal.query.filter_by(negocio_id=sucursal.negocio_id).update({"es_principal": False})
        
        # Establecer esta como principal
        sucursal.es_principal = True
        
        db.session.commit()
        
        return jsonify({
            "success": True,
            "message": f"'{sucursal.nombre_sucursal}' es ahora la sucursal principal"
        }), 200
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"❌ Error estableciendo sucursal principal: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


# ==========================================
# ENDPOINTS DE PERSONAL
# ==========================================

@negocio_api_bp.route('/sucursal/<int:sucursal_id>/personal', methods=['POST', 'OPTIONS'])
@cross_origin(supports_credentials=True)
def agregar_personal(sucursal_id):
    """
    Agrega personal (cajero o administrador) a una sucursal.
    
    Request body:
        {
            "tipo": "cajero" | "administrador",
            "nombre": "Juan Pérez",
            "identificacion": "123456789",
            "telefono": "3001234567",
            "email": "juan@email.com"
        }
    """
    if request.method == 'OPTIONS':
        return jsonify({"success": True}), 200
    
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"success": False, "error": "No autenticado"}), 401
    
    try:
        sucursal = Sucursal.query.filter_by(id_sucursal=sucursal_id).first()
        
        if not sucursal:
            return jsonify({"success": False, "error": "Sucursal no encontrada"}), 404
        
        # Verificar permisos
        negocio = Negocio.query.filter_by(
            id_negocio=sucursal.negocio_id,
            usuario_id=user_id
        ).first()
        
        if not negocio:
            return jsonify({"success": False, "error": "Acceso denegado"}), 403
        
        data = request.get_json()
        
        tipo = data.get('tipo', 'cajero').lower()
        nombre = data.get('nombre', '').strip()
        identificacion = data.get('identificacion', '').strip()
        
        if not nombre or not identificacion:
            return jsonify({
                "success": False,
                "error": "Nombre e identificación son requeridos"
            }), 400
        
        extra_data = {
            "telefono": data.get('telefono', ''),
            "email": data.get('email', ''),
            "fecha_ingreso": datetime.utcnow().isoformat()
        }
        
        if tipo == 'administrador':
            sucursal.agregar_administrador(nombre, identificacion, **extra_data)
        else:
            sucursal.agregar_cajero(nombre, identificacion, **extra_data)
        
        db.session.commit()
        
        return jsonify({
            "success": True,
            "message": f"{tipo.title()} agregado exitosamente",
            "data": serialize_sucursal(sucursal)
        }), 201
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"❌ Error agregando personal: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@negocio_api_bp.route('/sucursal/<int:sucursal_id>/personal/<identificacion>', methods=['DELETE', 'OPTIONS'])
@cross_origin(supports_credentials=True)
def eliminar_personal(sucursal_id, identificacion):
    """
    Elimina personal de una sucursal.
    
    Query params:
        tipo: "cajero" | "administrador"
    """
    if request.method == 'OPTIONS':
        return jsonify({"success": True}), 200
    
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"success": False, "error": "No autenticado"}), 401
    
    try:
        sucursal = Sucursal.query.filter_by(id_sucursal=sucursal_id).first()
        
        if not sucursal:
            return jsonify({"success": False, "error": "Sucursal no encontrada"}), 404
        
        # Verificar permisos
        negocio = Negocio.query.filter_by(
            id_negocio=sucursal.negocio_id,
            usuario_id=user_id
        ).first()
        
        if not negocio:
            return jsonify({"success": False, "error": "Acceso denegado"}), 403
        
        tipo = request.args.get('tipo', 'cajero').lower()
        
        if tipo == 'administrador':
            sucursal.remover_administrador(identificacion)
        else:
            sucursal.remover_cajero(identificacion)
        
        db.session.commit()
        
        return jsonify({
            "success": True,
            "message": "Personal eliminado"
        }), 200
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"❌ Error eliminando personal: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


# ==========================================
# ENDPOINTS DE CIUDADES
# ==========================================

@negocio_api_bp.route('/ciudades', methods=['GET', 'OPTIONS'])
@cross_origin(supports_credentials=True)
def get_ciudades():
    """
    Obtiene lista de ciudades para autocomplete.
    
    Query params:
        q: Término de búsqueda
        id: ID específico de ciudad
        limit: Límite de resultados (default: 50)
    """
    if request.method == 'OPTIONS':
        return jsonify({"success": True}), 200
    
    try:
        termino = request.args.get('q', '').strip()
        id_param = request.args.get('id', '').strip()
        limite = int(request.args.get('limit', 50))
        
        # Búsqueda por ID
        if id_param and id_param.isdigit():
            ciudad = Colombia.query.filter_by(ciudad_id=int(id_param)).first()
            if ciudad:
                return jsonify({
                    "id": ciudad.ciudad_id,
                    "nombre": ciudad.ciudad_nombre
                }), 200
            return jsonify({"error": "Ciudad no encontrada"}), 404
        
        # Búsqueda por término
        query = Colombia.query
        
        if termino:
            query = query.filter(Colombia.ciudad_nombre.ilike(f"%{termino}%"))
        
        ciudades = query.order_by(Colombia.ciudad_nombre).limit(limite).all()
        
        return jsonify([{
            "id": c.ciudad_id,
            "nombre": c.ciudad_nombre
        } for c in ciudades]), 200
        
    except Exception as e:
        logger.error(f"❌ Error obteniendo ciudades: {e}")
        return jsonify({"error": str(e)}), 500


# ==========================================
# ENDPOINTS DE CONTEXTO (NEGOCIO/SUCURSAL ACTIVA)
# ==========================================

@negocio_api_bp.route('/contexto/establecer', methods=['POST', 'OPTIONS'])
@cross_origin(supports_credentials=True)
def establecer_contexto():
    """
    Establece el negocio y sucursal activa para la sesión.
    Esto afecta qué datos se muestran en el dashboard.
    
    Request body:
        {
            "negocio_id": 1,
            "sucursal_id": 1  // opcional
        }
    """
    if request.method == 'OPTIONS':
        return jsonify({"success": True}), 200
    
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"success": False, "error": "No autenticado"}), 401
    
    try:
        data = request.get_json()
        negocio_id = data.get('negocio_id')
        sucursal_id = data.get('sucursal_id')
        
        if not negocio_id:
            return jsonify({"success": False, "error": "negocio_id es requerido"}), 400
        
        # Verificar que el negocio pertenece al usuario
        negocio = Negocio.query.filter_by(
            id_negocio=negocio_id,
            usuario_id=user_id,
            activo=True
        ).first()
        
        if not negocio:
            return jsonify({"success": False, "error": "Negocio no encontrado"}), 404
        
        # Si no se especifica sucursal, usar la principal
        if not sucursal_id:
            sucursal = Sucursal.query.filter_by(
                negocio_id=negocio_id,
                es_principal=True,
                activo=True
            ).first()
            
            if sucursal:
                sucursal_id = sucursal.id_sucursal
        else:
            # Verificar que la sucursal pertenece al negocio
            sucursal = Sucursal.query.filter_by(
                id_sucursal=sucursal_id,
                negocio_id=negocio_id,
                activo=True
            ).first()
            
            if not sucursal:
                return jsonify({"success": False, "error": "Sucursal no encontrada"}), 404
        
        logger.info(f"✅ Contexto establecido: Negocio {negocio_id}, Sucursal {sucursal_id}")
        
        return jsonify({
            "success": True,
            "message": "Contexto establecido",
            "contexto": {
                "negocio": serialize_negocio(negocio),
                "sucursal": serialize_sucursal(sucursal) if sucursal else None
            }
        }), 200
        
    except Exception as e:
        logger.error(f"❌ Error estableciendo contexto: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@negocio_api_bp.route('/contexto/actual', methods=['GET', 'OPTIONS'])
@cross_origin(supports_credentials=True)
def obtener_contexto_actual():
    """
    Obtiene el contexto actual basado en localStorage del frontend.
    El frontend debe enviar negocio_id y sucursal_id como query params o headers.
    """
    if request.method == 'OPTIONS':
        return jsonify({"success": True}), 200
    
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"success": False, "error": "No autenticado"}), 401
    
    try:
        negocio_id = request.args.get('negocio_id') or request.headers.get('X-Business-ID')
        sucursal_id = request.args.get('sucursal_id') or request.headers.get('X-Branch-ID')
        
        if not negocio_id:
            # Devolver el primer negocio del usuario
            negocio = Negocio.query.filter_by(
                usuario_id=user_id,
                activo=True
            ).first()
        else:
            negocio = Negocio.query.filter_by(
                id_negocio=int(negocio_id),
                usuario_id=user_id,
                activo=True
            ).first()
        
        if not negocio:
            return jsonify({
                "success": True,
                "contexto": None,
                "message": "No hay negocios registrados"
            }), 200
        
        # Obtener sucursal
        if sucursal_id:
            sucursal = Sucursal.query.filter_by(
                id_sucursal=int(sucursal_id),
                negocio_id=negocio.id_negocio,
                activo=True
            ).first()
        else:
            sucursal = Sucursal.query.filter_by(
                negocio_id=negocio.id_negocio,
                es_principal=True,
                activo=True
            ).first()
        
        return jsonify({
            "success": True,
            "contexto": {
                "negocio": serialize_negocio(negocio),
                "sucursal": serialize_sucursal(sucursal) if sucursal else None
            }
        }), 200
        
    except Exception as e:
        logger.error(f"❌ Error obteniendo contexto: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


# ==========================================
# ENDPOINTS DE CONFIGURACIÓN DE PÁGINA/MICROSITIO
# ==========================================

@negocio_api_bp.route('/configuracion-pagina/<int:negocio_id>', methods=['GET', 'OPTIONS'])
@cross_origin(supports_credentials=True)
def obtener_configuracion_pagina(negocio_id):
    """
    Obtiene la configuración del micrositio de un negocio.
    """
    if request.method == 'OPTIONS':
        return jsonify({"success": True}), 200
    
    try:
        negocio = Negocio.query.filter_by(id_negocio=negocio_id).first()
        
        if not negocio:
            return jsonify({"success": False, "error": "Negocio no encontrado"}), 404
        
        return jsonify({
            "success": True,
            "data": {
                "tiene_pagina": negocio.tiene_pagina,
                "plantilla_id": negocio.plantilla_id,
                "slug": negocio.slug,
                "color_tema": negocio.color_tema,
                "whatsapp": getattr(negocio, 'whatsapp', None),
                "tipo_pagina": getattr(negocio, 'tipo_pagina', None),
                "logo_url": getattr(negocio, 'logo_url', None),
                "url": f"/sitio/{negocio.slug}" if negocio.slug else None
            }
        }), 200
        
    except Exception as e:
        logger.error(f"❌ Error obteniendo configuración: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@negocio_api_bp.route('/publicar-pagina', methods=['POST', 'OPTIONS'])
@cross_origin(supports_credentials=True)
def publicar_pagina():
    """
    Activa o actualiza el micrositio de un negocio.
    
    Request body:
        {
            "negocio_id": 1,
            "plantilla_id": "p1",
            "color_tema": "#4cd137"
        }
    """
    if request.method == 'OPTIONS':
        return jsonify({"success": True}), 200
    
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"success": False, "error": "No autenticado"}), 401
    
    try:
        data = request.get_json()
        negocio_id = data.get('negocio_id')
        
        if not negocio_id:
            return jsonify({"success": False, "error": "negocio_id es requerido"}), 400
        
        negocio = Negocio.query.filter_by(
            id_negocio=negocio_id,
            usuario_id=user_id
        ).first()
        
        if not negocio:
            return jsonify({"success": False, "error": "Negocio no encontrado"}), 404
        
        # Activar página
        negocio.tiene_pagina = True
        
        if 'plantilla_id' in data:
            negocio.plantilla_id = data['plantilla_id']
        
        if 'color_tema' in data:
            negocio.color_tema = data['color_tema']
        
        # Generar slug si no existe
        if not negocio.slug:
            base_slug = generar_slug(negocio.nombre_negocio)
            slug_final = base_slug
            contador = 1
            while Negocio.query.filter(
                Negocio.slug == slug_final,
                Negocio.id_negocio != negocio_id
            ).first():
                slug_final = f"{base_slug}-{contador}"
                contador += 1
            negocio.slug = slug_final
        
        db.session.commit()
        
        return jsonify({
            "success": True,
            "message": "Página publicada exitosamente",
            "url": f"/sitio/{negocio.slug}"
        }), 200
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"❌ Error publicando página: {e}")
        return jsonify({"success": False, "error": str(e)}), 500