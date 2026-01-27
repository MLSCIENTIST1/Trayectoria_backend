"""
BizFlow Studio - API de Gestión de Negocios y Sucursales
Sistema completo para multi-tenancy (múltiples negocios por usuario)
ACTUALIZADO v2.4: Generación automática de QR al registrar/actualizar negocio
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
# 📱 QR AUTO-GENERATION (v2.4)
# ==========================================

QR_BASE_URL = "https://tukomercio.com"  # 🔧 Cambiar por tu dominio en producción

def auto_generar_qr_negocio(negocio, commit=True):
    """
    Genera automáticamente el QR para un negocio.
    Llamar después de crear o actualizar el negocio.
    
    Args:
        negocio: Instancia del modelo Negocio
        commit: Si hacer commit a la DB (default True)
        
    Returns:
        dict: {success, qr_data, qr_base64} o {success: False, error}
    """
    try:
        import qrcode
        import io
        import base64
    except ImportError:
        logger.warning("⚠️ qrcode no instalado. Instalar: pip install qrcode[pil]")
        return {"success": False, "error": "qrcode no disponible"}
    
    if not negocio:
        return {"success": False, "error": "Negocio no proporcionado"}
    
    try:
        # Asegurar que tiene slug
        if not negocio.slug:
            negocio.slug = generar_slug(negocio.nombre_negocio)
        
        # URL del perfil público
        qr_data = f"{QR_BASE_URL}/n/{negocio.slug}"
        
        # Generar imagen QR
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_M,
            box_size=10,
            border=2,
        )
        qr.add_data(qr_data)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Convertir a base64
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        buffer.seek(0)
        qr_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
        
        # Guardar en el negocio (si el modelo tiene el campo)
        if hasattr(negocio, 'qr_negocio_data'):
            negocio.qr_negocio_data = qr_data
        
        if hasattr(negocio, 'qr_negocio_base64'):
            negocio.qr_negocio_base64 = f"data:image/png;base64,{qr_base64}"
        
        if commit:
            db.session.commit()
        
        logger.info(f"✅ QR generado para negocio {negocio.id_negocio}: {qr_data}")
        
        return {
            "success": True,
            "qr_data": qr_data,
            "qr_base64": f"data:image/png;base64,{qr_base64}",
            "slug": negocio.slug
        }
        
    except Exception as e:
        logger.error(f"❌ Error generando QR automático: {e}")
        return {"success": False, "error": str(e)}


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
    
    slug = texto.lower().strip()
    slug = unicodedata.normalize('NFD', slug)
    slug = ''.join(c for c in slug if unicodedata.category(c) != 'Mn')
    slug = re.sub(r'[^a-z0-9]+', '-', slug)
    slug = re.sub(r'-+', '-', slug)
    slug = slug.strip('-')
    
    return slug[:50]


def buscar_ciudad_flexible(nombre_ciudad):
    """Busca una ciudad de forma flexible (case-insensitive, sin acentos)."""
    if not nombre_ciudad:
        return None
    
    nombre_normalizado = normalizar_texto(nombre_ciudad)
    
    ciudad = Colombia.query.filter(
        func.lower(Colombia.ciudad_nombre) == nombre_ciudad.strip().lower()
    ).first()
    
    if ciudad:
        return ciudad
    
    ciudad = Colombia.query.filter(
        Colombia.ciudad_nombre.ilike(f"%{nombre_ciudad.strip()}%")
    ).first()
    
    if ciudad:
        return ciudad
    
    todas_ciudades = Colombia.query.all()
    for c in todas_ciudades:
        if normalizar_texto(c.ciudad_nombre) == nombre_normalizado:
            return c
    
    return None


def get_current_user_id():
    """
    🔐 ACTUALIZADO v2.3: Obtiene el ID del usuario con DETECCIÓN DE COLISIONES.
    
    Igual que catalogo_api.py - Prioriza el header X-User-ID cuando hay
    discrepancia para evitar fugas de datos por cookies viejas.
    
    ORDEN DE PRIORIDAD:
    1. JWT Token (Authorization: Bearer xxx) - Para iframes
    2. Header X-User-ID vs Flask-Login - CON DETECCIÓN DE COLISIÓN
    3. Flask-Login solo si no hay header
    """
    
    # ==========================================
    # 1. INTENTAR JWT PRIMERO (para iframes/Designer)
    # ==========================================
    try:
        from src.auth_jwt import get_user_id_from_jwt
        jwt_user_id = get_user_id_from_jwt()
        if jwt_user_id:
            logger.debug(f"✅ Usuario autenticado via JWT: {jwt_user_id}")
            return jwt_user_id
    except ImportError:
        pass
    except Exception as e:
        logger.debug(f"⚠️ Error verificando JWT: {e}")
    
    # ==========================================
    # 2. OBTENER IDs DE AMBAS FUENTES
    # ==========================================
    header_id = request.headers.get('X-User-ID')
    session_id = None
    
    if current_user.is_authenticated:
        session_id = str(getattr(current_user, 'id_usuario', ''))
    
    logger.debug(f"🔍 [IDENTIDAD] Header X-User-ID: {header_id} | Sesión Flask: {session_id}")
    
    # ==========================================
    # 3. 🚨 DETECCIÓN DE COLISIÓN (CRÍTICO PARA SEGURIDAD)
    # ==========================================
    if header_id and session_id and header_id != session_id:
        logger.warning(f"⚠️ ¡COLISIÓN DE SESIÓN DETECTADA!")
        logger.warning(f"   Header X-User-ID: {header_id}")
        logger.warning(f"   Sesión Flask: {session_id}")
        logger.warning(f"   → Usando Header (más reciente del frontend)")
        # Priorizar el header porque viene del frontend actualizado
        # La cookie puede estar desactualizada
        return int(header_id)
    
    # ==========================================
    # 4. RETORNAR EL QUE EXISTA
    # ==========================================
    if header_id and header_id.isdigit():
        logger.debug(f"✅ Usuario via X-User-ID header: {header_id}")
        return int(header_id)
    
    if session_id:
        logger.debug(f"✅ Usuario via Flask-Login: {session_id}")
        return int(session_id)
    
    logger.warning("❌ No se encontró usuario autenticado en ninguna fuente")
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
        "fecha_registro": negocio.fecha_registro.isoformat() if negocio.fecha_registro else None,
        
        # Campos para micrositio/tienda online
        "tiene_pagina": getattr(negocio, 'tiene_pagina', False),
        "slug": getattr(negocio, 'slug', None),
        "color_tema": getattr(negocio, 'color_tema', '#4cd137'),
        "whatsapp": getattr(negocio, 'whatsapp', None),
        "tipo_pagina": getattr(negocio, 'tipo_pagina', None),
        "logo_url": getattr(negocio, 'logo_url', None),
        "url_sitio": f"/tienda/{negocio.slug}" if getattr(negocio, 'tiene_pagina', False) and getattr(negocio, 'slug', None) else None,
        
        # 🎨 Store Designer
        "config_tienda": getattr(negocio, 'config_tienda', {}) or {},
        
        # 📱 QR Data (v2.4)
        "qr_negocio_data": getattr(negocio, 'qr_negocio_data', None),
        "qr_url": f"/api/negocio/{negocio.id_negocio}/qr" if getattr(negocio, 'slug', None) else None
    }
    
    if negocio.ciudad:
        data["ciudad_nombre"] = negocio.ciudad.ciudad_nombre
    
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
        "version": "2.4.0",  # 🆕 Actualizado - QR auto-generation
        "features": ["micrositios", "tienda_online", "config_tienda", "jwt_auth", "collision_detection", "qr_auto_generation"]
    }), 200


@negocio_api_bp.route('/mis_negocios', methods=['GET', 'OPTIONS'])
@cross_origin(supports_credentials=True)
def obtener_mis_negocios():
    """Obtiene todos los negocios del usuario autenticado."""
    if request.method == 'OPTIONS':
        return jsonify({"success": True}), 200
    
    user_id = get_current_user_id()
    
    # Log detallado para debugging
    logger.info(f"📋 GET /mis_negocios - user_id resuelto: {user_id}")
    logger.info(f"   Headers: X-User-ID={request.headers.get('X-User-ID')}")
    logger.info(f"   Flask current_user.is_authenticated: {current_user.is_authenticated}")
    
    if not user_id:
        return jsonify({
            "success": False, 
            "error": "No autenticado",
            "debug": {
                "header_user_id": request.headers.get('X-User-ID'),
                "flask_authenticated": current_user.is_authenticated
            }
        }), 401
    
    try:
        include_sucursales = request.args.get('include_sucursales', 'false').lower() == 'true'
        
        negocios = Negocio.query.filter_by(
            usuario_id=user_id,
            activo=True
        ).order_by(Negocio.nombre_negocio).all()
        
        data = [serialize_negocio(n, include_sucursales) for n in negocios]
        
        logger.info(f"✅ Negocios obtenidos para usuario {user_id}: {len(data)}")
        
        # Debug: mostrar IDs de negocios encontrados
        if data:
            logger.info(f"   IDs: {[n['id_negocio'] for n in data]}")
        else:
            logger.warning(f"⚠️ Usuario {user_id} no tiene negocios registrados")
            # Verificar si el usuario existe en la BD
            all_negocios = Negocio.query.filter_by(activo=True).limit(5).all()
            logger.info(f"   Muestra de negocios en BD: {[(n.id_negocio, n.usuario_id) for n in all_negocios]}")
        
        return jsonify({
            "success": True,
            "data": data,
            "total": len(data),
            "debug_user_id": user_id  # Para debugging en frontend
        }), 200
        
    except Exception as e:
        logger.error(f"❌ Error obteniendo negocios: {e}")
        return jsonify({"success": False, "error": "Error al obtener negocios"}), 500


@negocio_api_bp.route('/negocio/<int:negocio_id>', methods=['GET', 'OPTIONS'])
@cross_origin(supports_credentials=True)
def obtener_negocio(negocio_id):
    """Obtiene un negocio específico por ID."""
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
            # Log para debugging
            logger.warning(f"⚠️ Negocio {negocio_id} no encontrado para usuario {user_id}")
            # Verificar si existe pero pertenece a otro usuario
            otro = Negocio.query.filter_by(id_negocio=negocio_id).first()
            if otro:
                logger.warning(f"   Negocio existe pero pertenece a usuario {otro.usuario_id}")
            return jsonify({"success": False, "error": "Negocio no encontrado"}), 404
        
        return jsonify({
            "success": True,
            "data": serialize_negocio(negocio, include_sucursales=True)
        }), 200
        
    except Exception as e:
        logger.error(f"❌ Error obteniendo negocio: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@negocio_api_bp.route('/negocio/slug/<string:slug>', methods=['GET', 'OPTIONS'])
@cross_origin(supports_credentials=True)
def obtener_negocio_por_slug(slug):
    """Obtiene un negocio por su slug (público, para tiendas)."""
    if request.method == 'OPTIONS':
        return jsonify({"success": True}), 200
    
    try:
        negocio = Negocio.query.filter_by(
            slug=slug,
            activo=True,
            tiene_pagina=True
        ).first()
        
        if not negocio:
            return jsonify({"success": False, "error": "Tienda no encontrada"}), 404
        
        return jsonify({
            "success": True,
            "data": {
                "id_negocio": negocio.id_negocio,
                "nombre_negocio": negocio.nombre_negocio,
                "descripcion": negocio.descripcion,
                "slug": negocio.slug,
                "color_tema": getattr(negocio, 'color_tema', '#4cd137'),
                "whatsapp": getattr(negocio, 'whatsapp', None),
                "telefono": negocio.telefono,
                "tipo_pagina": getattr(negocio, 'tipo_pagina', 'landing'),
                "logo_url": getattr(negocio, 'logo_url', None),
                "config_tienda": getattr(negocio, 'config_tienda', {}) or {}
            }
        }), 200
        
    except Exception as e:
        logger.error(f"❌ Error obteniendo negocio por slug: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@negocio_api_bp.route('/registrar_negocio', methods=['POST', 'OPTIONS'])
@cross_origin(supports_credentials=True)
def registrar_negocio():
    """
    Registra un nuevo negocio para el usuario autenticado.
    🆕 v2.4: Genera QR automáticamente al crear el negocio.
    """
    if request.method == 'OPTIONS':
        return jsonify({"success": True}), 200
    
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"success": False, "error": "Debes iniciar sesión para registrar un negocio"}), 401
    
    try:
        data = request.get_json()
        if not data:
            return jsonify({"success": False, "error": "No se recibieron datos"}), 400
        
        nombre_negocio = data.get('nombre_negocio', '').strip()
        if not nombre_negocio:
            return jsonify({"success": False, "error": "El nombre del negocio es requerido"}), 400
        
        existe = Negocio.query.filter_by(
            nombre_negocio=nombre_negocio,
            usuario_id=user_id
        ).first()
        
        if existe:
            return jsonify({"success": False, "error": f"Ya tienes un negocio llamado '{nombre_negocio}'"}), 409
        
        ciudad_id = data.get('ciudad_id')
        if not ciudad_id and data.get('ciudad'):
            ciudad_obj = buscar_ciudad_flexible(data['ciudad'])
            if ciudad_obj:
                ciudad_id = ciudad_obj.ciudad_id
            else:
                return jsonify({"success": False, "error": f"Ciudad '{data['ciudad']}' no encontrada"}), 400
        
        if not ciudad_id:
            return jsonify({"success": False, "error": "La ciudad es requerida"}), 400
        
        base_slug = generar_slug(nombre_negocio)
        slug_final = base_slug
        contador = 1
        while Negocio.query.filter_by(slug=slug_final).first():
            slug_final = f"{base_slug}-{contador}"
            contador += 1
        
        nuevo_negocio = Negocio(
            nombre_negocio=nombre_negocio,
            usuario_id=user_id,
            descripcion=data.get('descripcion', ''),
            direccion=data.get('direccion', ''),
            telefono=data.get('telefono', ''),
            categoria=data.get('categoria') or data.get('tipoNegocio', 'General'),
            ciudad_id=ciudad_id,
            slug=slug_final,
            config_tienda=data.get('config_tienda', {})
        )
        
        db.session.add(nuevo_negocio)
        db.session.flush()  # Para obtener el ID antes del commit
        
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
        
        # ==========================================
        # 🆕 GENERAR QR AUTOMÁTICAMENTE (v2.4)
        # ==========================================
        qr_result = auto_generar_qr_negocio(nuevo_negocio, commit=True)
        
        if qr_result.get('success'):
            logger.info(f"📱 QR generado automáticamente: {qr_result.get('qr_data')}")
        else:
            logger.warning(f"⚠️ QR no generado: {qr_result.get('error')}")
        
        logger.info(f"✅ Negocio creado: {nombre_negocio} (ID: {nuevo_negocio.id_negocio}, slug: {slug_final}) por usuario {user_id}")
        
        # Respuesta con datos del QR incluidos
        response_data = {
            "negocio": serialize_negocio(nuevo_negocio),
            "sucursal_principal": serialize_sucursal(sucursal_principal),
            # 🆕 QR Data
            "qr_generated": qr_result.get('success', False),
            "qr_data": qr_result.get('qr_data'),
            "qr_url": f"/api/negocio/{nuevo_negocio.id_negocio}/qr" if qr_result.get('success') else None
        }
        
        return jsonify({
            "success": True,
            "message": f"Negocio '{nombre_negocio}' registrado exitosamente",
            "data": response_data
        }), 201
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"❌ Error registrando negocio: {e}", exc_info=True)
        return jsonify({"success": False, "error": "Error al registrar el negocio"}), 500


@negocio_api_bp.route('/negocio/<int:negocio_id>', methods=['PUT', 'OPTIONS'])
@cross_origin(supports_credentials=True)
def actualizar_negocio(negocio_id):
    """
    Actualiza un negocio existente.
    🔐 Soporta autenticación via JWT (para Store Designer en iframe)
    🆕 v2.4: Regenera QR si cambia el slug
    """
    if request.method == 'OPTIONS':
        return jsonify({"success": True}), 200
    
    user_id = get_current_user_id()
    if not user_id:
        logger.warning(f"❌ PUT /negocio/{negocio_id} - No autenticado")
        return jsonify({"success": False, "error": "No autenticado"}), 401
    
    try:
        negocio = Negocio.query.filter_by(
            id_negocio=negocio_id,
            usuario_id=user_id
        ).first()
        
        if not negocio:
            return jsonify({"success": False, "error": "Negocio no encontrado"}), 404
        
        data = request.get_json()
        
        logger.info(f"📝 Actualizando negocio {negocio_id} por usuario {user_id}")
        
        # 🆕 Guardar slug anterior para detectar cambios
        slug_anterior = negocio.slug
        
        # Campos básicos
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
        
        # Campos para micrositio / tienda online
        if 'color_tema' in data:
            negocio.color_tema = data['color_tema']
        
        if 'tiene_pagina' in data:
            negocio.tiene_pagina = data['tiene_pagina']
        
        if 'slug' in data and data['slug']:
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
        
        # 🎨 CONFIG_TIENDA - STORE DESIGNER
        if 'config_tienda' in data:
            negocio.config_tienda = data['config_tienda']
            logger.info(f"🎨 Config tienda actualizada para negocio {negocio_id}")
        
        # Generar slug automático si se activa página
        if data.get('tiene_pagina') and not negocio.slug:
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
        
        # ==========================================
        # 🆕 REGENERAR QR SI CAMBIÓ EL SLUG (v2.4)
        # ==========================================
        qr_regenerated = False
        if negocio.slug and negocio.slug != slug_anterior:
            qr_result = auto_generar_qr_negocio(negocio, commit=True)
            qr_regenerated = qr_result.get('success', False)
            if qr_regenerated:
                logger.info(f"📱 QR regenerado por cambio de slug: {qr_result.get('qr_data')}")
        
        logger.info(f"✅ Negocio actualizado: {negocio.nombre_negocio}")
        
        response_data = serialize_negocio(negocio)
        response_data['qr_regenerated'] = qr_regenerated
        
        return jsonify({
            "success": True,
            "message": "Negocio actualizado exitosamente",
            "data": response_data
        }), 200
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"❌ Error actualizando negocio: {e}", exc_info=True)
        return jsonify({"success": False, "error": str(e)}), 500


@negocio_api_bp.route('/negocio/<int:negocio_id>', methods=['DELETE', 'OPTIONS'])
@cross_origin(supports_credentials=True)
def eliminar_negocio(negocio_id):
    """Desactiva un negocio (soft delete)."""
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
        
        negocio.activo = False
        Sucursal.query.filter_by(negocio_id=negocio_id).update({"activo": False})
        
        db.session.commit()
        
        logger.info(f"✅ Negocio desactivado: {negocio.nombre_negocio}")
        
        return jsonify({"success": True, "message": "Negocio eliminado"}), 200
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"❌ Error eliminando negocio: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


# ==========================================
# ENDPOINTS ESPECÍFICOS PARA STORE DESIGNER
# ==========================================

@negocio_api_bp.route('/negocio/<int:negocio_id>/config-tienda', methods=['GET', 'OPTIONS'])
@cross_origin(supports_credentials=True)
def obtener_config_tienda(negocio_id):
    """Obtiene solo la configuración del Store Designer."""
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
        
        return jsonify({
            "success": True,
            "data": {
                "negocio_id": negocio.id_negocio,
                "nombre_negocio": negocio.nombre_negocio,
                "config_tienda": getattr(negocio, 'config_tienda', {}) or {}
            }
        }), 200
        
    except Exception as e:
        logger.error(f"❌ Error obteniendo config_tienda: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@negocio_api_bp.route('/negocio/<int:negocio_id>/config-tienda', methods=['PUT', 'PATCH', 'OPTIONS'])
@cross_origin(supports_credentials=True)
def actualizar_config_tienda(negocio_id):
    """Actualiza la configuración del Store Designer."""
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
        
        if request.method == 'PUT':
            negocio.config_tienda = data
        else:
            current_config = getattr(negocio, 'config_tienda', {}) or {}
            
            def deep_merge(base, updates):
                for key, value in updates.items():
                    if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                        deep_merge(base[key], value)
                    else:
                        base[key] = value
                return base
            
            negocio.config_tienda = deep_merge(current_config, data)
        
        db.session.commit()
        
        logger.info(f"🎨 Config tienda actualizada para negocio {negocio_id}")
        
        return jsonify({
            "success": True,
            "message": "Configuración actualizada",
            "data": {
                "negocio_id": negocio.id_negocio,
                "config_tienda": negocio.config_tienda
            }
        }), 200
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"❌ Error actualizando config_tienda: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


# ==========================================
# ENDPOINTS DE SUCURSALES
# ==========================================

@negocio_api_bp.route('/negocios/<int:negocio_id>/sucursales', methods=['GET', 'OPTIONS'])
@cross_origin(supports_credentials=True)
def obtener_sucursales(negocio_id):
    """Obtiene todas las sucursales de un negocio."""
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
    """Registra una nueva sucursal para un negocio."""
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
        
        negocio = Negocio.query.filter_by(
            id_negocio=negocio_id,
            usuario_id=user_id
        ).first()
        
        if not negocio:
            return jsonify({"success": False, "error": "Negocio no encontrado"}), 404
        
        existe = Sucursal.query.filter_by(
            negocio_id=negocio_id,
            nombre_sucursal=nombre_sucursal
        ).first()
        
        if existe:
            return jsonify({
                "success": False,
                "error": f"Ya existe una sucursal llamada '{nombre_sucursal}'"
            }), 409
        
        es_primera = Sucursal.query.filter_by(negocio_id=negocio_id).count() == 0
        
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
        
        logger.info(f"✅ Sucursal creada: {nombre_sucursal}")
        
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
    """Obtiene una sucursal específica."""
    if request.method == 'OPTIONS':
        return jsonify({"success": True}), 200
    
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"success": False, "error": "No autenticado"}), 401
    
    try:
        sucursal = Sucursal.query.filter_by(id_sucursal=sucursal_id).first()
        
        if not sucursal:
            return jsonify({"success": False, "error": "Sucursal no encontrada"}), 404
        
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
    """Actualiza una sucursal existente."""
    if request.method == 'OPTIONS':
        return jsonify({"success": True}), 200
    
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"success": False, "error": "No autenticado"}), 401
    
    try:
        sucursal = Sucursal.query.filter_by(id_sucursal=sucursal_id).first()
        
        if not sucursal:
            return jsonify({"success": False, "error": "Sucursal no encontrada"}), 404
        
        negocio = Negocio.query.filter_by(
            id_negocio=sucursal.negocio_id,
            usuario_id=user_id
        ).first()
        
        if not negocio:
            return jsonify({"success": False, "error": "Acceso denegado"}), 403
        
        data = request.get_json()
        
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
    """Desactiva una sucursal (soft delete)."""
    if request.method == 'OPTIONS':
        return jsonify({"success": True}), 200
    
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"success": False, "error": "No autenticado"}), 401
    
    try:
        sucursal = Sucursal.query.filter_by(id_sucursal=sucursal_id).first()
        
        if not sucursal:
            return jsonify({"success": False, "error": "Sucursal no encontrada"}), 404
        
        negocio = Negocio.query.filter_by(
            id_negocio=sucursal.negocio_id,
            usuario_id=user_id
        ).first()
        
        if not negocio:
            return jsonify({"success": False, "error": "Acceso denegado"}), 403
        
        total_sucursales = Sucursal.query.filter_by(
            negocio_id=sucursal.negocio_id,
            activo=True
        ).count()
        
        if total_sucursales <= 1:
            return jsonify({
                "success": False,
                "error": "No puedes eliminar la única sucursal"
            }), 400
        
        sucursal.activo = False
        
        if sucursal.es_principal:
            otra_sucursal = Sucursal.query.filter(
                Sucursal.negocio_id == sucursal.negocio_id,
                Sucursal.id_sucursal != sucursal_id,
                Sucursal.activo == True
            ).first()
            
            if otra_sucursal:
                otra_sucursal.es_principal = True
        
        db.session.commit()
        
        return jsonify({"success": True, "message": "Sucursal eliminada"}), 200
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"❌ Error eliminando sucursal: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@negocio_api_bp.route('/sucursal/<int:sucursal_id>/set_principal', methods=['POST', 'OPTIONS'])
@cross_origin(supports_credentials=True)
def establecer_sucursal_principal(sucursal_id):
    """Establece una sucursal como la principal."""
    if request.method == 'OPTIONS':
        return jsonify({"success": True}), 200
    
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"success": False, "error": "No autenticado"}), 401
    
    try:
        sucursal = Sucursal.query.filter_by(id_sucursal=sucursal_id).first()
        
        if not sucursal:
            return jsonify({"success": False, "error": "Sucursal no encontrada"}), 404
        
        negocio = Negocio.query.filter_by(
            id_negocio=sucursal.negocio_id,
            usuario_id=user_id
        ).first()
        
        if not negocio:
            return jsonify({"success": False, "error": "Acceso denegado"}), 403
        
        Sucursal.query.filter_by(negocio_id=sucursal.negocio_id).update({"es_principal": False})
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
    """Agrega personal a una sucursal."""
    if request.method == 'OPTIONS':
        return jsonify({"success": True}), 200
    
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"success": False, "error": "No autenticado"}), 401
    
    try:
        sucursal = Sucursal.query.filter_by(id_sucursal=sucursal_id).first()
        
        if not sucursal:
            return jsonify({"success": False, "error": "Sucursal no encontrada"}), 404
        
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
    """Elimina personal de una sucursal."""
    if request.method == 'OPTIONS':
        return jsonify({"success": True}), 200
    
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"success": False, "error": "No autenticado"}), 401
    
    try:
        sucursal = Sucursal.query.filter_by(id_sucursal=sucursal_id).first()
        
        if not sucursal:
            return jsonify({"success": False, "error": "Sucursal no encontrada"}), 404
        
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
        
        return jsonify({"success": True, "message": "Personal eliminado"}), 200
        
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
    """Obtiene lista de ciudades para autocomplete."""
    if request.method == 'OPTIONS':
        return jsonify({"success": True}), 200
    
    try:
        termino = request.args.get('q', '').strip()
        id_param = request.args.get('id', '').strip()
        limite = int(request.args.get('limit', 50))
        
        if id_param and id_param.isdigit():
            ciudad = Colombia.query.filter_by(ciudad_id=int(id_param)).first()
            if ciudad:
                return jsonify({
                    "id": ciudad.ciudad_id,
                    "nombre": ciudad.ciudad_nombre
                }), 200
            return jsonify({"error": "Ciudad no encontrada"}), 404
        
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
# ENDPOINTS DE CONTEXTO
# ==========================================

@negocio_api_bp.route('/contexto/establecer', methods=['POST', 'OPTIONS'])
@cross_origin(supports_credentials=True)
def establecer_contexto():
    """Establece el negocio y sucursal activa."""
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
        
        negocio = Negocio.query.filter_by(
            id_negocio=negocio_id,
            usuario_id=user_id,
            activo=True
        ).first()
        
        if not negocio:
            return jsonify({"success": False, "error": "Negocio no encontrado"}), 404
        
        if not sucursal_id:
            sucursal = Sucursal.query.filter_by(
                negocio_id=negocio_id,
                es_principal=True,
                activo=True
            ).first()
            
            if sucursal:
                sucursal_id = sucursal.id_sucursal
        else:
            sucursal = Sucursal.query.filter_by(
                id_sucursal=sucursal_id,
                negocio_id=negocio_id,
                activo=True
            ).first()
            
            if not sucursal:
                return jsonify({"success": False, "error": "Sucursal no encontrada"}), 404
        
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
    """Obtiene el contexto actual."""
    if request.method == 'OPTIONS':
        return jsonify({"success": True}), 200
    
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"success": False, "error": "No autenticado"}), 401
    
    try:
        negocio_id = request.args.get('negocio_id') or request.headers.get('X-Business-ID')
        sucursal_id = request.args.get('sucursal_id') or request.headers.get('X-Branch-ID')
        
        if not negocio_id:
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
# 🔍 ENDPOINT DE DEBUG (solo en desarrollo)
# ==========================================

@negocio_api_bp.route('/debug/session', methods=['GET', 'OPTIONS'])
@cross_origin(supports_credentials=True)
def debug_session():
    """
    🔍 ENDPOINT DE DEBUG - Muestra información de la sesión actual.
    NOTA: Desactivar en producción o agregar protección.
    """
    if request.method == 'OPTIONS':
        return jsonify({"success": True}), 200
    
    header_user_id = request.headers.get('X-User-ID')
    header_business_id = request.headers.get('X-Business-ID')
    
    flask_authenticated = current_user.is_authenticated
    flask_user_id = None
    if flask_authenticated:
        flask_user_id = str(getattr(current_user, 'id_usuario', ''))
    
    resolved_user_id = get_current_user_id()
    
    # Detectar colisión
    collision_detected = False
    if header_user_id and flask_user_id and header_user_id != flask_user_id:
        collision_detected = True
    
    return jsonify({
        "success": True,
        "debug": {
            "header_x_user_id": header_user_id,
            "header_x_business_id": header_business_id,
            "flask_authenticated": flask_authenticated,
            "flask_user_id": flask_user_id,
            "resolved_user_id": resolved_user_id,
            "collision_detected": collision_detected,
            "priority": "header" if collision_detected else ("flask" if flask_authenticated else "header")
        }
    }), 200