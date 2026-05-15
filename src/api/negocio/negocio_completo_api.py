# ═══════════════════════════════════════════════════════════════════════════════
# TUKOMERCIO - API de Gestión de Negocios y Sucursales
# VERSIÓN 2.5 - Integración MecaLink
#
# © 2024-2026 Carlos Eduardo Huérfano Bermúdez. Todos los derechos reservados.
# ═══════════════════════════════════════════════════════════════════════════════

"""
BizFlow Studio - API de Gestión de Negocios y Sucursales
Sistema completo para multi-tenancy (múltiples negocios por usuario)

VERSIÓN 2.5:
- v2.4: Generación automática de QR al registrar/actualizar negocio
- v2.5: Integración MecaLink - Mecánicos a Domicilio
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

QR_BASE_URL = "https://tukomercio.com"

def auto_generar_qr_negocio(negocio, commit=True):
    """
    Genera automáticamente el QR para un negocio.
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
        if not negocio.slug:
            negocio.slug = generar_slug(negocio.nombre_negocio)
        
        qr_data = f"{QR_BASE_URL}/n/{negocio.slug}"
        
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_M,
            box_size=10,
            border=2,
        )
        qr.add_data(qr_data)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        buffer.seek(0)
        qr_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
        
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
# 🔧 MECALINK INTEGRATION (v2.5)
# ==========================================

def crear_perfil_mecalink(negocio_id, mecalink_data, ciudad=None):
    """
    Crea el perfil MecaLink para un negocio de tipo mecánico a domicilio.
    
    Esta función se llama desde registrar_negocio cuando la categoría es 'mecanico_domicilio'.
    
    Args:
        negocio_id (int): ID del negocio recién creado
        mecalink_data (dict): Datos específicos de MecaLink
        ciudad (str): Ciudad del negocio
    
    Returns:
        dict: {success: True/False, perfil: MecanicoMecalink o None, error: str}
    """
    try:
        from src.models.mecalink_model import MecanicoMecalink
    except ImportError:
        logger.warning("⚠️ Modelo MecanicoMecalink no disponible")
        return {"success": False, "error": "Módulo MecaLink no instalado", "perfil": None}
    
    try:
        perfil = MecanicoMecalink(
            negocio_id=negocio_id,
            zonas_texto=mecalink_data.get('zonas'),
            servicios=mecalink_data.get('servicios', []),
            disponibilidad_texto=mecalink_data.get('disponibilidad'),
            tiene_vehiculo=mecalink_data.get('tiene_vehiculo') in ('si', 'true', True, '1'),
            tiene_herramientas=mecalink_data.get('tiene_herramientas', 'algunas'),
            experiencia=mecalink_data.get('experiencia', 'menos_1'),
            ciudad_operacion=ciudad
        )
        
        db.session.add(perfil)
        logger.info(f"🔧 Perfil MecaLink creado para negocio {negocio_id}")
        
        return {"success": True, "perfil": perfil, "error": None}
        
    except Exception as e:
        logger.error(f"❌ Error creando perfil MecaLink: {e}")
        return {"success": False, "perfil": None, "error": str(e)}


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
    🔐 Obtiene el ID del usuario con DETECCIÓN DE COLISIONES.
    """
    
    # 1. INTENTAR JWT PRIMERO (para iframes/Designer)
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
    
    # 2. OBTENER IDs DE AMBAS FUENTES
    header_id = request.headers.get('X-User-ID')
    session_id = None
    
    if current_user.is_authenticated:
        session_id = str(getattr(current_user, 'id_usuario', ''))
    
    logger.debug(f"🔍 [IDENTIDAD] Header X-User-ID: {header_id} | Sesión Flask: {session_id}")
    
    # 3. DETECCIÓN DE COLISIÓN
    if header_id and session_id and header_id != session_id:
        logger.warning(f"⚠️ ¡COLISIÓN DE SESIÓN DETECTADA!")
        logger.warning(f"   Header X-User-ID: {header_id}")
        logger.warning(f"   Sesión Flask: {session_id}")
        logger.warning(f"   → Usando Header (más reciente del frontend)")
        return int(header_id)
    
    # 4. RETORNAR EL QUE EXISTA
    if header_id and header_id.isdigit():
        logger.debug(f"✅ Usuario via X-User-ID header: {header_id}")
        return int(header_id)
    
    if session_id:
        logger.debug(f"✅ Usuario via Flask-Login: {session_id}")
        return int(session_id)
    
    logger.warning("❌ No se encontró usuario autenticado en ninguna fuente")
    return None


_TUKO_BASE = 'https://tuko.pages.dev'

# ══════════════════════════════════════════════════════════════════════
# REGISTRO DE PLANTILLAS — Backend
#
# ✅ PARA AGREGAR UNA PLANTILLA NUEVA:
#    Agregar una línea aquí: 'tipo': '/tienda/plantillas/<tipo>/'
#    El tipo DEBE coincidir con lo que guarda el frontend en tipo_pagina.
#    También registrar en plantillas_registry.js del frontend.
# ══════════════════════════════════════════════════════════════════════
_PLANTILLAS_RUTAS = {
    'taller':      '/tienda/plantillas/taller/',
    'restaurante': '/tienda/plantillas/restaurante/',
    'catalogo':    '/tienda/plantillas/catalogo/',
    'groove':      '/tienda/plantillas/groove/',
    'verde':       '/tienda/plantillas/verde/',
    'prueba':      '/tienda/plantillas/prueba/',
    # ── Agregar nuevas plantillas aquí ──────────────────────────────
    # 'nueva':     '/tienda/plantillas/nueva/',
}


def _build_site_url(negocio):
    """
    Devuelve la URL pública limpia del micrositio.

    Formato:  https://tuko.pages.dev/tienda/{slug}
    El router r.html resuelve automáticamente qué plantilla mostrar.
    El parámetro ?slug= ya no es necesario ni visible para el usuario.
    """
    if not getattr(negocio, 'tiene_pagina', False):
        return None
    slug = getattr(negocio, 'slug', None)
    if not slug:
        return None
    return f'{_TUKO_BASE}/tienda/{slug}'


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
        "url_sitio": _build_site_url(negocio),
        "perfil_publico": getattr(negocio, 'perfil_publico', True),

        # Store Designer
        "config_tienda": getattr(negocio, 'config_tienda', {}) or {},

        # QR Data
        "qr_negocio_data": getattr(negocio, 'qr_negocio_data', None),
        "qr_url": f"/api/negocio/{negocio.id_negocio}/qr" if getattr(negocio, 'slug', None) else None
    }
    
    if negocio.ciudad_rel and hasattr(negocio.ciudad_rel, 'ciudad_nombre'):
        data["ciudad_nombre"] = negocio.ciudad_rel.ciudad_nombre
    else:
        data["ciudad_nombre"] = negocio.ciudad
    
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
        "version": "2.5.0",
        "features": ["micrositios", "tienda_online", "config_tienda", "jwt_auth", "collision_detection", "qr_auto_generation", "mecalink_integration"]
    }), 200


@negocio_api_bp.route('/mis_negocios', methods=['GET', 'OPTIONS'])
@cross_origin(supports_credentials=True)
def obtener_mis_negocios():
    """Obtiene todos los negocios del usuario autenticado."""
    if request.method == 'OPTIONS':
        return jsonify({"success": True}), 200
    
    user_id = get_current_user_id()
    
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
        
        if data:
            logger.info(f"   IDs: {[n['id_negocio'] for n in data]}")
        else:
            logger.warning(f"⚠️ Usuario {user_id} no tiene negocios registrados")
            all_negocios = Negocio.query.filter_by(activo=True).limit(5).all()
            logger.info(f"   Muestra de negocios en BD: {[(n.id_negocio, n.usuario_id) for n in all_negocios]}")
        
        return jsonify({
            "success": True,
            "data": data,
            "total": len(data),
            "debug_user_id": user_id
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
            logger.warning(f"⚠️ Negocio {negocio_id} no encontrado para usuario {user_id}")
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


@negocio_api_bp.route('/negocio/slug/<string:slug>/manifest.json', methods=['GET'])
@cross_origin()
def manifest_pwa(slug):
    """
    [PWA] Genera manifest.json dinámico para la tienda de un negocio.
    Permite que cada tienda se instale como app con su propio nombre y color.
    """
    print(f"[PWA] 🗂️ manifest.json solicitado para slug='{slug}'")
    try:
        negocio = Negocio.query.filter_by(slug=slug, activo=True, tiene_pagina=True).first()
        if not negocio:
            print(f"[PWA] ⚠️ Negocio no encontrado para slug='{slug}'")
            return jsonify({"error": "Tienda no encontrada"}), 404

        nombre    = negocio.nombre_negocio or slug
        color     = getattr(negocio, 'color_tema', '#2563eb') or '#2563eb'
        logo_url  = getattr(negocio, 'logo_url', None) or ''
        desc      = getattr(negocio, 'descripcion', '') or f'Tienda online de {nombre}'
        short_name = nombre[:14]  # max 14 chars recomendado para launchers

        # Icono: si hay logo_url usarlo, sino iconos genéricos
        if logo_url:
            icons = [
                {"src": logo_url, "sizes": "any", "type": "image/png", "purpose": "any maskable"}
            ]
        else:
            icons = [
                {"src": "/assets/icons/pwa-192.png", "sizes": "192x192", "type": "image/png", "purpose": "any maskable"},
                {"src": "/assets/icons/pwa-512.png",  "sizes": "512x512",  "type": "image/png"}
            ]

        # start_url apunta a la URL real según tipo_pagina
        start_url = _build_site_url(negocio) or f'https://tuko.pages.dev/tienda/?slug={slug}'

        manifest = {
            "name":             nombre,
            "short_name":       short_name,
            "description":      desc,
            "start_url":        start_url,
            "scope":            "https://tuko.pages.dev/",
            "display":          "standalone",
            "background_color": "#ffffff",
            "theme_color":      color,
            "orientation":      "portrait-primary",
            "lang":             "es",
            "categories":       ["shopping"],
            "icons":            icons
        }

        import json as _json
        from flask import make_response as _mr
        resp = _mr(_json.dumps(manifest, ensure_ascii=False, indent=2))
        resp.headers['Content-Type']  = 'application/manifest+json; charset=utf-8'
        resp.headers['Cache-Control'] = 'public, max-age=3600'
        print(f"[PWA] ✅ manifest.json generado para '{nombre}' (color={color})")
        return resp

    except Exception as e:
        logger.error(f"[PWA] ❌ Error generando manifest para slug='{slug}': {e}")
        return jsonify({"error": "Error generando manifest"}), 500


@negocio_api_bp.route('/registrar_negocio', methods=['POST', 'OPTIONS'])
@cross_origin(supports_credentials=True)
def registrar_negocio():
    """
    Registra un nuevo negocio para el usuario autenticado.
    
    v2.4: Genera QR automáticamente al crear el negocio.
    v2.5: Si categoría es 'mecanico_domicilio', crea perfil MecaLink.
    
    Body JSON adicional para MecaLink:
    {
        "categoria": "mecanico_domicilio",
        "mecalink_data": {
            "zonas": "Usme, Ciudad Bolívar, Tunjuelito",
            "servicios": ["cambio_aceite", "diagnostico_scanner"],
            "disponibilidad": "Lunes a Sábado 7am-6pm",
            "tiene_vehiculo": "si",
            "tiene_herramientas": "completas",
            "experiencia": "3_5"
        }
    }
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
        ciudad_nombre = data.get('ciudad', '')
        
        if not ciudad_id and ciudad_nombre:
            ciudad_obj = buscar_ciudad_flexible(ciudad_nombre)
            if ciudad_obj:
                ciudad_id = ciudad_obj.ciudad_id
            else:
                return jsonify({"success": False, "error": f"Ciudad '{ciudad_nombre}' no encontrada"}), 400
        
        if not ciudad_id:
            return jsonify({"success": False, "error": "La ciudad es requerida"}), 400
        
        base_slug = generar_slug(nombre_negocio)
        slug_final = base_slug
        contador = 1
        while Negocio.query.filter_by(slug=slug_final).first():
            slug_final = f"{base_slug}-{contador}"
            contador += 1
        # ★ FIX: Heredar plan del usuario (el más alto de sus otros negocios)
        plan_heredado = 'basic'
        try:
            mejor_negocio = Negocio.query.filter_by(
                usuario_id=user_id, activo=True
            ).filter(
                Negocio.plan_key.isnot(None)
            ).first()
            
            if mejor_negocio and mejor_negocio.plan_key:
                plan_heredado = mejor_negocio.plan_key
                logger.info(f"📋 Plan heredado de negocio existente: {plan_heredado}")
        except Exception as e:
            logger.warning(f"⚠️ Error heredando plan: {e}")
        # Crear el negocio
        nuevo_negocio = Negocio(
            nombre_negocio=nombre_negocio,
            usuario_id=user_id,
            descripcion=data.get('descripcion', ''),
            direccion=data.get('direccion', ''),
            telefono=data.get('telefono', ''),
            categoria=data.get('categoria') or data.get('tipoNegocio', 'General'),
            ciudad_id=ciudad_id,
            ciudad=ciudad_nombre,
            slug=slug_final,
            config_tienda=data.get('config_tienda', {}),
            whatsapp=data.get('whatsapp', ''),
            plan_key=plan_heredado
        )
        
        db.session.add(nuevo_negocio)
        db.session.flush()  # Para obtener el ID antes del commit
        
        # Crear sucursal principal
        sucursal_principal = Sucursal(
            nombre_sucursal="Principal",
            negocio_id=nuevo_negocio.id_negocio,
            direccion=data.get('direccion', ''),
            ciudad=ciudad_nombre,
            telefono=data.get('telefono', ''),
            es_principal=True,
            activo=True
        )
        
        db.session.add(sucursal_principal)
        
        # ==========================================
        # 🔧 INTEGRACIÓN MECALINK (v2.5)
        # ==========================================
        mecalink_result = None
        categoria = data.get('categoria', '').lower()
        
        if categoria == 'mecanico_domicilio' and data.get('mecalink_data'):
            logger.info(f"🔧 Detectada categoría mecánico a domicilio - Creando perfil MecaLink")
            
            mecalink_result = crear_perfil_mecalink(
                negocio_id=nuevo_negocio.id_negocio,
                mecalink_data=data['mecalink_data'],
                ciudad=ciudad_nombre
            )
            
            if mecalink_result['success']:
                logger.info(f"🔧 Perfil MecaLink creado exitosamente")
            else:
                logger.warning(f"⚠️ Error creando perfil MecaLink: {mecalink_result.get('error')}")
        
        db.session.commit()
        
        # ==========================================
        # 📱 GENERAR QR AUTOMÁTICAMENTE (v2.4)
        # ==========================================
        qr_result = auto_generar_qr_negocio(nuevo_negocio, commit=True)
        
        if qr_result.get('success'):
            logger.info(f"📱 QR generado automáticamente: {qr_result.get('qr_data')}")
        else:
            logger.warning(f"⚠️ QR no generado: {qr_result.get('error')}")
        
        logger.info(f"✅ Negocio creado: {nombre_negocio} (ID: {nuevo_negocio.id_negocio}, slug: {slug_final}) por usuario {user_id}")
        
        # Construir respuesta
        response_data = {
            "negocio": serialize_negocio(nuevo_negocio),
            "sucursal_principal": serialize_sucursal(sucursal_principal),
            "qr_generated": qr_result.get('success', False),
            "qr_data": qr_result.get('qr_data'),
            "qr_url": f"/api/negocio/{nuevo_negocio.id_negocio}/qr" if qr_result.get('success') else None
        }
        
        # 🔧 Agregar datos de MecaLink si aplica
        if mecalink_result:
            response_data["mecalink"] = {
                "created": mecalink_result['success'],
                "error": mecalink_result.get('error'),
                "perfil_id": mecalink_result['perfil'].id if mecalink_result.get('perfil') else None
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
    v2.4: Regenera QR si cambia el slug
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
        
        slug_anterior = negocio.slug

        # ══════════════════════════════════════════════════════════════
        # FASE 1 — Campos críticos (tienen_pagina, slug, etc.)
        # Estos DEBEN guardarse aunque tipo_pagina falle.
        # Guardamos tipo_pagina en variable aparte para el commit-2.
        # ══════════════════════════════════════════════════════════════

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

        if 'logo_url' in data:
            negocio.logo_url = data['logo_url']

        # CONFIG_TIENDA - STORE DESIGNER
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

        # ── COMMIT 1: Campos críticos ──────────────────────────────
        db.session.commit()
        logger.info(
            f"✅ Negocio {negocio_id} commit-1 OK — "
            f"tiene_pagina={negocio.tiene_pagina!r}  "
            f"slug={negocio.slug!r}"
        )

        # ══════════════════════════════════════════════════════════════
        # FASE 2 — tipo_pagina (columna que puede no existir en BD)
        # Si falla, la tienda sigue siendo accesible (commit-1 ya pasó).
        # ══════════════════════════════════════════════════════════════
        tipo_pagina_saved = True
        tipo_pagina_err = None

        if 'tipo_pagina' in data:
            _tp_nuevo = data['tipo_pagina']
            _tp_anterior = negocio.tipo_pagina
            logger.info(f"🎨 Intentando guardar tipo_pagina negocio {negocio_id}: '{_tp_anterior}' → '{_tp_nuevo}'")
            try:
                negocio.tipo_pagina = _tp_nuevo
                db.session.commit()
                logger.info(f"✅ tipo_pagina guardado OK: {negocio.tipo_pagina!r}")
            except Exception as tipo_err:
                db.session.rollback()
                tipo_pagina_saved = False
                tipo_pagina_err = str(tipo_err)
                logger.error(
                    f"❌ No se pudo guardar tipo_pagina='{_tp_nuevo}' para negocio {negocio_id}: {tipo_err}"
                )
                logger.error(
                    "   ⚠️  La tienda SÍ está accesible (commit-1 ya pasó). "
                    "La columna tipo_pagina posiblemente no existe en la BD. "
                    "Verificar run.py repair block al iniciar."
                )
                # Restaurar valor local para que el JSON devuelto sea correcto
                negocio.tipo_pagina = _tp_anterior

        logger.info(
            f"✅ Negocio {negocio_id} actualizado — "
            f"tipo_pagina={negocio.tipo_pagina!r}  "
            f"tiene_pagina={negocio.tiene_pagina!r}  "
            f"slug={negocio.slug!r}  "
            f"tipo_pagina_saved={tipo_pagina_saved}"
        )

        # REGENERAR QR SI CAMBIÓ EL SLUG
        qr_regenerated = False
        if negocio.slug and negocio.slug != slug_anterior:
            qr_result = auto_generar_qr_negocio(negocio, commit=True)
            qr_regenerated = qr_result.get('success', False)
            if qr_regenerated:
                logger.info(f"📱 QR regenerado por cambio de slug: {qr_result.get('qr_data')}")

        logger.info(f"✅ Negocio actualizado: {negocio.nombre_negocio}")

        response_data = serialize_negocio(negocio)
        response_data['qr_regenerated'] = qr_regenerated
        # Devolver info de diagnóstico al frontend
        if not tipo_pagina_saved:
            response_data['tipo_pagina_warning'] = (
                f"tipo_pagina no pudo guardarse en BD: {tipo_pagina_err}"
            )

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
# 🚚 ENDPOINTS DE CONFIGURACIÓN DE ENVÍOS (v2.7)
# ==========================================

@negocio_api_bp.route('/negocio/<int:negocio_id>/config-envios', methods=['GET', 'OPTIONS'])
@cross_origin(supports_credentials=True)
def obtener_config_envios(negocio_id):
    """
    Obtiene la configuración de envíos del negocio.

    Estructura devuelta:
    {
      "success": true,
      "data": {
        "negocio_id": 42,
        "nombre_negocio": "Mi Tienda",
        "config_envios": {
          "pickup": {"activo": false, "direccion": null, "coordenadas": null, "instrucciones": null},
          "flete_gratis_desde": null,
          "tarifas": {}
        }
      }
    }
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

        config = getattr(negocio, 'config_envios', None) or {}

        # Estructura base garantizada
        config.setdefault('pickup', {
            'activo': False,
            'direccion': None,
            'coordenadas': None,
            'instrucciones': None
        })
        config.setdefault('flete_gratis_desde', None)
        config.setdefault('tarifas', {})

        return jsonify({
            "success": True,
            "data": {
                "negocio_id": negocio.id_negocio,
                "nombre_negocio": negocio.nombre_negocio,
                "config_envios": config
            }
        }), 200

    except Exception as e:
        logger.error(f"❌ Error obteniendo config_envios negocio {negocio_id}: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@negocio_api_bp.route('/negocio/<int:negocio_id>/config-envios', methods=['PATCH', 'OPTIONS'])
@cross_origin(supports_credentials=True)
def actualizar_config_envios(negocio_id):
    """
    Actualiza la configuración de envíos del negocio (merge profundo).

    Payloads aceptados (parciales o completos):

    ① Cambiar pickup completo:
       {"pickup": {"activo": true, "direccion": "Cra 7 #45-67", "coordenadas": {...}}}

    ② Agregar / actualizar tarifa de ciudad + cantidad + transportadora:
       {"tarifas": {"Bogotá": {"1": {"Servientrega": {"precio": 8000, "dias": "1-2"}}}}}

    ③ Actualizar flete gratis:
       {"flete_gratis_desde": 200000}

    ④ Todo junto:
       {"pickup": {...}, "flete_gratis_desde": 150000, "tarifas": {...}}
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

        data = request.get_json(silent=True)
        if not data:
            return jsonify({"success": False, "error": "Body JSON requerido"}), 400

        current_config = dict(getattr(negocio, 'config_envios', None) or {})

        def deep_merge(base, updates):
            for key, value in updates.items():
                if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                    deep_merge(base[key], value)
                else:
                    base[key] = value
            return base

        negocio.config_envios = deep_merge(current_config, data)

        # Forzar flag de cambio en columna JSONB (SQLAlchemy no detecta mutaciones internas)
        from sqlalchemy.orm.attributes import flag_modified
        flag_modified(negocio, 'config_envios')

        db.session.commit()

        logger.info(f"🚚 config_envios actualizada para negocio {negocio_id}")

        return jsonify({
            "success": True,
            "message": "Configuración de envíos actualizada",
            "data": {
                "negocio_id": negocio.id_negocio,
                "config_envios": negocio.config_envios
            }
        }), 200

    except Exception as e:
        db.session.rollback()
        logger.error(f"❌ Error actualizando config_envios negocio {negocio_id}: {e}")
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
# 🔍 ENDPOINT DE DEBUG
# ==========================================

@negocio_api_bp.route('/debug/session', methods=['GET', 'OPTIONS'])
@cross_origin(supports_credentials=True)
def debug_session():
    """🔍 ENDPOINT DE DEBUG - Muestra información de la sesión actual."""
    if request.method == 'OPTIONS':
        return jsonify({"success": True}), 200
    
    header_user_id = request.headers.get('X-User-ID')
    header_business_id = request.headers.get('X-Business-ID')
    
    flask_authenticated = current_user.is_authenticated
    flask_user_id = None
    if flask_authenticated:
        flask_user_id = str(getattr(current_user, 'id_usuario', ''))
    
    resolved_user_id = get_current_user_id()
    
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