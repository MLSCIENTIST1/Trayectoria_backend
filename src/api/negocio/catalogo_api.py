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


# ============================================
# catalogo_api.py - VERSIÓN v3.5 COMPLETA
# Conectado con Inventario PRO v2.4 + BizContext
# ACTUALIZADO: Soporte para Personalización de Productos
# ============================================

import cloudinary
import cloudinary.uploader
import logging
import traceback
import sys
import re
import time
import json
from datetime import datetime
from flask import Blueprint, request, jsonify
from flask_cors import cross_origin
from flask_login import current_user
from src.models.colombia_data.negocio import Negocio

from src.models.database import db
from src.models.feature_models import  check_limit, check_feature_access
from src.models.colombia_data.contabilidad.operaciones_y_catalogo import (
    ProductoCatalogo, 
    TransaccionOperativa,
    MovimientoStock,
    CategoriaProducto
)

# --- CONFIGURACIÓN DE LOGS ---
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
if not logger.handlers:
    handler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter('\033[92m%(asctime)s\033[0m - \033[94m%(name)s\033[0m - \033[93m%(levelname)s\033[0m - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

# --- CONFIGURACIÓN DE CLOUDINARY ---
cloudinary.config(
    cloud_name="dp50v0bwj",
    api_key="966788685877863",
    api_secret="O6kBEBo3svgWozvn_dyw2J1CtBE",
    secure=True
)

catalogo_api_bp = Blueprint('catalogo_api_bp', __name__)


# ============================================
# HELPERS DE AUTENTICACIÓN Y CONTEXTO
# ============================================

def get_authorized_user_id():
    """
    Obtiene el ID del usuario autenticado (Header prioritario)
    """
    try:
        header_id = request.headers.get('X-User-ID')
        session_id = None
        
        if current_user and hasattr(current_user, 'is_authenticated') and current_user.is_authenticated:
            session_id = str(getattr(current_user, 'id_usuario', ''))

        logger.debug(f"🔍 [AUTH] Header: {header_id} | Sesión: {session_id}")

        if header_id and header_id != session_id:
            logger.warning(f"⚠️ Header {header_id} != Sesión {session_id}. Usando Header.")
            return header_id
        
        return header_id or session_id
    except Exception as e:
        logger.error(f"❌ Error en get_authorized_user_id: {e}")
        return None


def get_biz_context():
    """
    Obtiene el contexto de negocio desde headers o query params.
    Compatible con BizContext.js del frontend.
    """
    negocio_id = None
    sucursal_id = None
    
    try:
        negocio_id = request.headers.get('X-Business-ID') or request.headers.get('X-Negocio-ID')
        
        if not negocio_id:
            negocio_id = request.args.get('negocio_id')
        
        if not negocio_id:
            try:
                if request.is_json and request.content_length and request.content_length > 0:
                    json_data = request.get_json(silent=True)
                    if json_data and isinstance(json_data, dict):
                        negocio_id = json_data.get('negocio_id')
            except Exception:
                pass
        
        if not negocio_id:
            try:
                if request.form:
                    negocio_id = request.form.get('negocio_id')
            except Exception:
                pass
        
        sucursal_id = request.headers.get('X-Sucursal-ID')
        
        if not sucursal_id:
            sucursal_id = request.args.get('sucursal_id')
        
        if not sucursal_id:
            try:
                if request.is_json and request.content_length and request.content_length > 0:
                    json_data = request.get_json(silent=True)
                    if json_data and isinstance(json_data, dict):
                        sucursal_id = json_data.get('sucursal_id')
            except Exception:
                pass
        
        if not sucursal_id:
            try:
                if request.form:
                    sucursal_id = request.form.get('sucursal_id')
            except Exception:
                pass
        
        result = {
            'negocio_id': None,
            'sucursal_id': None
        }
        
        if negocio_id:
            try:
                result['negocio_id'] = int(negocio_id)
            except (ValueError, TypeError):
                logger.warning(f"⚠️ negocio_id no válido: {negocio_id}")
        
        if sucursal_id:
            try:
                result['sucursal_id'] = int(sucursal_id)
            except (ValueError, TypeError):
                logger.warning(f"⚠️ sucursal_id no válido: {sucursal_id}")
        
        logger.debug(f"🏢 [BizContext] negocio_id={result['negocio_id']}, sucursal_id={result['sucursal_id']}")
        
        return result
        
    except Exception as e:
        logger.error(f"❌ Error en get_biz_context: {e}")
        return {'negocio_id': None, 'sucursal_id': None}


def parse_json_field(value, default=None):
    """
    Helper para parsear campos que pueden venir como JSON string o ya parseados.
    """
    if default is None:
        default = []
    
    if value is None:
        return default
    
    if isinstance(value, list):
        return value
    
    if isinstance(value, dict):
        return value
    
    if isinstance(value, str):
        if not value.strip():
            return default
        try:
            parsed = json.loads(value)
            if isinstance(parsed, (list, dict)):
                return parsed
            if isinstance(parsed, str):
                try:
                    return json.loads(parsed)
                except:
                    return default
            return default
        except json.JSONDecodeError:
            return default
        except Exception:
            return default
    
    return default


def procesar_badges_desde_request(data):
    """
    Procesa los badges enviados desde el frontend Inventario PRO v2.3.
    """
    badges_default = {
        'destacado': False,
        'envio_gratis': False,
        'pre_orden': False,
        'edicion_limitada': False,
        'oferta_flash': False,
        'combo': False,
        'garantia_extendida': False,
        'eco_friendly': False,
        'badge_personalizado': None
    }
    
    if not data:
        return badges_default
    
    badges_raw = data.get('badges')
    
    if badges_raw is None:
        return {
            'destacado': data.get('destacado', False) in [True, 'true', '1', 1],
            'envio_gratis': data.get('envio_gratis', False) in [True, 'true', '1', 1],
            'pre_orden': data.get('pre_orden', False) in [True, 'true', '1', 1],
            'edicion_limitada': data.get('edicion_limitada', False) in [True, 'true', '1', 1],
            'oferta_flash': data.get('oferta_flash', False) in [True, 'true', '1', 1],
            'combo': data.get('combo', False) in [True, 'true', '1', 1],
            'garantia_extendida': data.get('garantia_extendida', False) in [True, 'true', '1', 1],
            'eco_friendly': data.get('eco_friendly', False) in [True, 'true', '1', 1],
            'badge_personalizado': data.get('badge_personalizado') or None
        }
    
    if isinstance(badges_raw, str):
        try:
            badges_raw = json.loads(badges_raw)
        except:
            return badges_default
    
    if not isinstance(badges_raw, dict):
        return badges_default
    
    return {
        'destacado': bool(badges_raw.get('destacado', False)),
        'envio_gratis': bool(badges_raw.get('envio_gratis', False)),
        'pre_orden': bool(badges_raw.get('pre_orden', False)),
        'edicion_limitada': bool(badges_raw.get('edicion_limitada', False)),
        'oferta_flash': bool(badges_raw.get('oferta_flash', False)),
        'combo': bool(badges_raw.get('combo', False)),
        'garantia_extendida': bool(badges_raw.get('garantia_extendida', False)),
        'eco_friendly': bool(badges_raw.get('eco_friendly', False)),
        'badge_personalizado': badges_raw.get('badge_personalizado') or None
    }


def procesar_personalizacion_desde_request(data):
    """
    ★ v3.5 NUEVO: Procesa la configuración de personalización desde el request.
    
    El frontend envía:
    - personalizacion_activa: boolean
    - personalizacion_config: JSON string o dict con la configuración
    
    Returns:
        tuple: (activa: bool, config: dict)
    """
    # Valor por defecto de la configuración
    config_default = {
        "permite_imagen": True,
        "permite_texto": True,
        "imagen_requerida": False,
        "texto_requerido": False,
        "max_size_mb": 5,
        "formatos": ["png", "jpg", "jpeg", "pdf"],
        "max_caracteres": 100,
        "instrucciones": "Sube tu diseño en alta resolución (mínimo 300 DPI)",
        "placeholder_texto": "Escribe tu nombre o frase",
        "costo_adicional": 0
    }
    
    if not data:
        return False, config_default
    
    # Verificar si está activa
    activa = data.get('personalizacion_activa', False)
    if isinstance(activa, str):
        activa = activa.lower() in ['true', '1', 'yes', 'si']
    else:
        activa = bool(activa)
    
    # Si no está activa, retornar defaults
    if not activa:
        return False, config_default
    
    # Parsear configuración
    config_raw = data.get('personalizacion_config')
    
    if config_raw is None:
        # Intentar leer campos individuales
        config = {
            'permite_imagen': data.get('permite_imagen', True) in [True, 'true', '1', 1],
            'permite_texto': data.get('permite_texto', True) in [True, 'true', '1', 1],
            'imagen_requerida': data.get('imagen_requerida', False) in [True, 'true', '1', 1],
            'texto_requerido': data.get('texto_requerido', False) in [True, 'true', '1', 1],
            'max_size_mb': int(data.get('max_size_mb', 5) or 5),
            'formatos': data.get('formatos', ['png', 'jpg', 'jpeg', 'pdf']),
            'max_caracteres': int(data.get('max_caracteres', 100) or 100),
            'instrucciones': str(data.get('instrucciones', config_default['instrucciones']))[:500],
            'placeholder_texto': str(data.get('placeholder_texto', config_default['placeholder_texto']))[:100],
            'costo_adicional': float(data.get('costo_adicional', 0) or 0)
        }
        return True, config
    
    # Parsear JSON si viene como string
    if isinstance(config_raw, str):
        try:
            config_raw = json.loads(config_raw)
        except:
            return True, config_default
    
    if not isinstance(config_raw, dict):
        return True, config_default
    
    # Sanitizar configuración
    config = {
        'permite_imagen': bool(config_raw.get('permite_imagen', True)),
        'permite_texto': bool(config_raw.get('permite_texto', True)),
        'imagen_requerida': bool(config_raw.get('imagen_requerida', False)),
        'texto_requerido': bool(config_raw.get('texto_requerido', False)),
        'max_size_mb': min(int(config_raw.get('max_size_mb', 5) or 5), 20),
        'formatos': config_raw.get('formatos', ['png', 'jpg', 'jpeg', 'pdf']),
        'max_caracteres': min(int(config_raw.get('max_caracteres', 100) or 100), 500),
        'instrucciones': str(config_raw.get('instrucciones', ''))[:500],
        'placeholder_texto': str(config_raw.get('placeholder_texto', ''))[:100],
        'costo_adicional': max(float(config_raw.get('costo_adicional', 0) or 0), 0)
    }
    
    # Validar formatos
    formatos_validos = ['png', 'jpg', 'jpeg', 'pdf', 'svg', 'ai', 'psd', 'eps']
    config['formatos'] = [f.lower() for f in config['formatos'] if f.lower() in formatos_validos]
    if not config['formatos']:
        config['formatos'] = ['png', 'jpg', 'jpeg']
    
    return True, config


def require_auth(f):
    """Decorador para requerir autenticación"""
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        user_id = get_authorized_user_id()
        if not user_id:
            return jsonify({"success": False, "message": "No autorizado"}), 401
        return f(user_id, *args, **kwargs)
    return decorated


def safe_to_dict(obj, fallback_fields=None):
    """
    Convierte un objeto SQLAlchemy a dict de forma segura.
    """
    if obj is None:
        return None
    
    if hasattr(obj, 'to_dict'):
        try:
            return obj.to_dict()
        except Exception as e:
            logger.warning(f"⚠️ Error en to_dict(): {e}")
    
    if fallback_fields:
        result = {}
        for field in fallback_fields:
            try:
                result[field] = getattr(obj, field, None)
            except Exception:
                result[field] = None
        return result
    
    try:
        result = {}
        for key in obj.__dict__:
            if not key.startswith('_'):
                result[key] = getattr(obj, key, None)
        return result
    except Exception:
        return {}


# ============================================
# HEALTH CHECK
# ============================================

@catalogo_api_bp.route('/health', methods=['GET'])
def health_check():
    return jsonify({
        "status": "online", 
        "module": "catalogo",
        "version": "3.5",
        "cloudinary": "configured",
        "badges_support": "v2.3_json",
        "personalizacion_support": "v1.0"
    }), 200


# ============================================
# 1. OBTENER PRODUCTOS (con filtros BizContext)
# ============================================

@catalogo_api_bp.route('/inventario/productos', methods=['GET', 'OPTIONS'])
@cross_origin(supports_credentials=True)
def inventario_productos():
    """Alias para compatibilidad con Inventario PRO"""
    return obtener_mis_productos()


@catalogo_api_bp.route('/mis-productos', methods=['GET', 'OPTIONS'])
@cross_origin(supports_credentials=True)
def obtener_mis_productos():
    """
    GET /api/mis-productos
    
    Query params opcionales:
    - negocio_id: Filtrar por negocio
    - sucursal_id: Filtrar por sucursal
    - categoria: Filtrar por categoría
    - stock_filter: 'in_stock', 'low_stock', 'out_of_stock'
    - search: Búsqueda por nombre/SKU/barcode
    - sort: 'newest', 'name_asc', 'price_desc', etc.
    - personalizable: 'true' para filtrar solo personalizables
    """
    if request.method == 'OPTIONS':
        return jsonify({"success": True}), 200

    user_id = get_authorized_user_id()
    if not user_id:
        return jsonify({"success": False, "message": "No autorizado"}), 401

    try:
        ctx = get_biz_context()
        
        total_en_bd = ProductoCatalogo.query.filter_by(usuario_id=int(user_id)).count()
        logger.info(f"📦 Obteniendo productos - User: {user_id}, Negocio: {ctx['negocio_id']}, Total en BD para este usuario: {total_en_bd}")
        
        query = ProductoCatalogo.query.filter_by(usuario_id=int(user_id))

        # ★ FIX CRÍTICO: filtrar siempre por negocio_id cuando viene en la petición.
        # Antes se requería ?strict=true (nunca enviado por el frontend), lo que
        # causaba que todos los productos del usuario aparecieran en todos sus negocios.
        if ctx['negocio_id']:
            query = query.filter(
                db.or_(
                    ProductoCatalogo.negocio_id == ctx['negocio_id'],
                    ProductoCatalogo.negocio_id == None   # productos sin negocio asignado (migración)
                )
            )
            
        if ctx['sucursal_id']:
            query = query.filter_by(sucursal_id=ctx['sucursal_id'])
        
        categoria = request.args.get('categoria')
        if categoria:
            query = query.filter_by(categoria=categoria)
        
        stock_filter = request.args.get('stock_filter')
        if stock_filter == 'in_stock':
            query = query.filter(ProductoCatalogo.stock > 10)
        elif stock_filter == 'low_stock':
            query = query.filter(ProductoCatalogo.stock > 0, ProductoCatalogo.stock <= 10)
        elif stock_filter == 'out_of_stock':
            query = query.filter(ProductoCatalogo.stock == 0)
        
        # ★ v3.5: Filtro por productos personalizables
        personalizable = request.args.get('personalizable')
        if personalizable and personalizable.lower() in ['true', '1', 'yes']:
            if hasattr(ProductoCatalogo, 'personalizacion_activa'):
                query = query.filter(ProductoCatalogo.personalizacion_activa == True)
        
        search = request.args.get('search', '').strip()
        if search:
            search_term = f"%{search}%"
            query = query.filter(
                db.or_(
                    ProductoCatalogo.nombre.ilike(search_term),
                    ProductoCatalogo.referencia_sku.ilike(search_term),
                    ProductoCatalogo.codigo_barras.ilike(search_term)
                )
            )
        
        sort = request.args.get('sort', 'newest')
        if sort == 'name_asc':
            query = query.order_by(ProductoCatalogo.nombre.asc())
        elif sort == 'name_desc':
            query = query.order_by(ProductoCatalogo.nombre.desc())
        elif sort == 'price_asc':
            query = query.order_by(ProductoCatalogo.precio.asc())
        elif sort == 'price_desc':
            query = query.order_by(ProductoCatalogo.precio.desc())
        elif sort == 'stock_asc':
            query = query.order_by(ProductoCatalogo.stock.asc())
        elif sort == 'stock_desc':
            query = query.order_by(ProductoCatalogo.stock.desc())
        else:
            query = query.order_by(ProductoCatalogo.id_producto.desc())
        
        productos = query.all()
        
        data_final = []
        for p in productos:
            try:
                d = safe_to_dict(p, ['id_producto', 'nombre', 'precio', 'stock', 'categoria',
                                      'descripcion', 'imagen_url', 'referencia_sku', 'codigo_barras',
                                      'imagenes', 'videos', 'activo', 'negocio_id'])
                d['id'] = p.id_producto
                d['sku'] = p.referencia_sku
                d['barcode'] = p.codigo_barras or ''
                d['codigo_barras'] = p.codigo_barras or ''
                d['imagenes'] = parse_json_field(p.imagenes, [])
                d['videos'] = parse_json_field(p.videos, [])
                d['youtube_links'] = d['videos']
                
                # ★ v3.5: Incluir info de personalización
                d['personalizable'] = getattr(p, 'personalizacion_activa', False) or False
                d['personalizacion_activa'] = d['personalizable']
                if d['personalizable'] and hasattr(p, 'get_personalizacion_config'):
                    d['personalizacion_config'] = p.get_personalizacion_config()
                else:
                    d['personalizacion_config'] = None
                
                data_final.append(d)
            except Exception as e:
                logger.warning(f"⚠️ Error procesando producto {getattr(p, 'id_producto', '?')}: {e}")

        logger.info(f"✅ Catálogo: {len(data_final)} productos para usuario {user_id}")
        
        return jsonify({
            "success": True,
            "data": data_final,
            "total": len(data_final),
            "total_en_bd": total_en_bd,
            "context": ctx
        }), 200
        
    except Exception as e:
        logger.error(f"❌ Error en GET mis-productos: {traceback.format_exc()}")
        return jsonify({"success": False, "message": str(e)}), 500


@catalogo_api_bp.route('/mis-productos/migrar-negocio', methods=['POST', 'OPTIONS'])
@cross_origin(supports_credentials=True)
def migrar_negocio_productos():
    """
    POST /api/mis-productos/migrar-negocio
    Asigna negocio_id a todos los productos del usuario que no lo tienen.
    Body: { "negocio_id": 123 }
    """
    if request.method == 'OPTIONS':
        return jsonify({"success": True}), 200

    user_id = get_authorized_user_id()
    if not user_id:
        return jsonify({"success": False, "message": "No autorizado"}), 401

    try:
        ctx = get_biz_context()
        negocio_id = ctx['negocio_id']
        if not negocio_id:
            return jsonify({"success": False, "message": "negocio_id requerido"}), 400

        # ★ FIX: force=true DESACTIVADO permanentemente.
        # Antes reasignaba productos de OTROS negocios al activo, rompiendo
        # el aislamiento entre negocios de la misma cuenta.
        # Ahora solo migra productos SIN negocio asignado (huérfanos legacy).
        base_query = ProductoCatalogo.query.filter_by(usuario_id=int(user_id))
        productos_a_migrar = base_query.filter(
            ProductoCatalogo.negocio_id == None
        ).all()

        count = len(productos_a_migrar)
        for p in productos_a_migrar:
            p.negocio_id = negocio_id

        db.session.commit()
        logger.info(f"✅ Migración{'(force)' if force else ''}: {count} productos → negocio {negocio_id} (user {user_id})")

        return jsonify({
            "success": True,
            "migrados": count,
            "negocio_id": negocio_id,
            "message": f"{count} productos asignados al negocio correctamente"
        }), 200

    except Exception as e:
        db.session.rollback()
        logger.error(f"❌ Error en migración: {traceback.format_exc()}")
        return jsonify({"success": False, "message": str(e)}), 500


# ============================================
# 2. GUARDAR PRODUCTO (Crear nuevo) - v3.5
# ============================================

# ============================================
# 2. GUARDAR PRODUCTO (Crear nuevo) - v3.6 CON PLAN GATING
# ============================================

@catalogo_api_bp.route('/catalogo/producto/guardar', methods=['POST', 'OPTIONS'])
@cross_origin(supports_credentials=True)
def guardar_producto_catalogo():
    """
    POST /api/catalogo/producto/guardar
    
    Body (JSON o FormData):
    - nombre (requerido)
    - precio, costo, stock
    - categoria, descripcion
    - sku, barcode
    - negocio_id, sucursal_id (o via headers)
    - imagen (file) - imagen principal
    - imagen_1, imagen_2, ... (files) - galería adicional
    - youtube_links o videos (JSON string)
    - imagenes (JSON string) - URLs existentes
    - badges (JSON string) - badges manuales v2.3
    - personalizacion_activa (boolean) - v3.5
    - personalizacion_config (JSON string) - v3.5
    """
    if request.method == 'OPTIONS':
        return jsonify({"success": True}), 200

    user_id = get_authorized_user_id()
    if not user_id:
        return jsonify({"success": False, "message": "No autorizado"}), 401

    try:
        is_form = 'multipart/form-data' in (request.content_type or '')
        data = request.form.to_dict() if is_form else (request.get_json(silent=True) or {})
        ctx = get_biz_context()
        
        nombre = data.get('nombre', '').strip()
        if not nombre:
            return jsonify({"success": False, "message": "El nombre es requerido"}), 400

        # ═══ VALIDAR LÍMITE DE PRODUCTOS POR PLAN ═══
        negocio_id_check = ctx.get('negocio_id') or data.get('negocio_id')
        if negocio_id_check:
            limit_error = check_limit('crear_producto', int(negocio_id_check), ProductoCatalogo, 'negocio_id')
            if limit_error:
                return limit_error
            
        logger.info(f"📦 CREANDO PRODUCTO: {nombre} | User: {user_id} | Negocio: {ctx.get('negocio_id')}")
        
        # PROCESAR IMAGEN PRINCIPAL
        imagen_url = data.get('imagen_url', '')
        galeria_urls = []
        
        file = request.files.get('imagen') or request.files.get('imagen_file')
        if file and file.filename:
            nombre_limpio = re.sub(r'[^a-zA-Z0-9]', '', nombre[:15])
            p_id = f"user_{user_id}_{nombre_limpio}_{int(time.time())}"
            try:
                upload_result = cloudinary.uploader.upload(file, folder="productos_bizflow", public_id=p_id, overwrite=True, resource_type="auto")
                imagen_url = upload_result.get('secure_url')
                galeria_urls.append(imagen_url)
            except Exception as e:
                logger.error(f"❌ Error subiendo imagen: {e}")
        
        # PROCESAR GALERÍA
        for i in range(1, 10):
            file_key = f'imagen_{i}'
            if file_key in request.files:
                img_file = request.files[file_key]
                if img_file and img_file.filename:
                    nombre_limpio = re.sub(r'[^a-zA-Z0-9]', '', nombre[:15])
                    img_id = f"user_{user_id}_{nombre_limpio}_gal{i}_{int(time.time())}"
                    try:
                        upload_result = cloudinary.uploader.upload(img_file, folder="productos_bizflow/galeria", public_id=img_id, overwrite=True, resource_type="auto")
                        galeria_urls.append(upload_result.get('secure_url'))
                    except Exception as e:
                        logger.error(f"❌ Error subiendo galería [{i}]: {e}")
        
        # Imágenes existentes
        imagenes_existentes = parse_json_field(data.get('imagenes'), [])
        for url in imagenes_existentes:
            if url and url not in galeria_urls:
                galeria_urls.append(url)
        galeria_urls = galeria_urls[:10]
        
        # PROCESAR VIDEOS
        videos_raw = data.get('youtube_links') or data.get('videos') or '[]'
        videos = parse_json_field(videos_raw, [])
        videos = [url for url in videos if url and isinstance(url, str) and ('youtube' in url or 'youtu.be' in url or 'vimeo' in url)]
        
        # PROCESAR BADGES
        badges_data = procesar_badges_desde_request(data)
        
        # ★ v3.5: PROCESAR PERSONALIZACIÓN
        personalizacion_activa, personalizacion_config = procesar_personalizacion_desde_request(data)
        
        # CONTEXTO
        # ★ FIX: nunca asumir negocio 1 como fallback — si no llega negocio_id
        # se rechaza la petición para evitar crear productos en el negocio equivocado.
        negocio_id = ctx.get('negocio_id') or data.get('negocio_id')
        if not negocio_id:
            return jsonify({"success": False, "message": "negocio_id requerido para crear producto"}), 400
        negocio_id = int(negocio_id)
        sucursal_id = ctx.get('sucursal_id') or data.get('sucursal_id') or None
        if sucursal_id:
            sucursal_id = int(sucursal_id)

        # ═══════════════════════════════════════════════════════════════
        # ★ v3.6: VALIDAR SUB-FEATURES POR PLAN (sanitización silenciosa)
        # Si el plan no incluye la feature, limpiamos el dato sin rechazar
        # ═══════════════════════════════════════════════════════════════
        nid = int(negocio_id) if negocio_id else None
        if nid:
            # Badges manuales → requiere inv_badges_manuales (pro+)
            if not check_feature_access('inv_badges_manuales', nid):
                badges_data = {
                    'destacado': False, 'envio_gratis': False, 'pre_orden': False,
                    'edicion_limitada': False, 'oferta_flash': False, 'combo': False,
                    'garantia_extendida': False, 'eco_friendly': False,
                    'badge_personalizado': None
                }
                logger.info(f"🔒 Badges manuales bloqueados por plan")

            # Personalización → requiere inv_personalizacion (premium+)
            if not check_feature_access('inv_personalizacion', nid):
                personalizacion_activa = False
                personalizacion_config = {}
                logger.info(f"🔒 Personalización bloqueada por plan")

            # Videos → requiere inv_videos (premium+)
            if not check_feature_access('inv_videos', nid):
                videos = []
                logger.info(f"🔒 Videos bloqueados por plan")

            # Galería multi-imagen → requiere inv_galeria_multi (pro+)
            if not check_feature_access('inv_galeria_multi', nid):
                if len(galeria_urls) > 1:
                    galeria_urls = galeria_urls[:1]
                    logger.info(f"🔒 Galería limitada a 1 imagen por plan")

            # Código de barras → requiere inv_codigo_barras (pro+)
            if not check_feature_access('inv_codigo_barras', nid):
                data['barcode'] = ''
                data['codigo_barras'] = ''
                logger.info(f"🔒 Código de barras bloqueado por plan")

            # Costo de compra → requiere inv_costo_compra (pro+)
            if not check_feature_access('inv_costo_compra', nid):
                data['costo'] = '0'
                logger.info(f"🔒 Costo de compra bloqueado por plan")
        # ═══ FIN VALIDACIÓN SUB-FEATURES ═══

        # CREAR PRODUCTO
        nuevo_prod = ProductoCatalogo(
            nombre=nombre,
            precio=float(data.get('precio') or 0),
            negocio_id=negocio_id,
            usuario_id=int(user_id),
            descripcion=data.get('descripcion', ''),
            costo=float(data.get('costo') or 0),
            stock=int(data.get('stock') or 0),
            stock_minimo=int(data.get('stock_minimo') or 5),
            stock_critico=int(data.get('stock_critico') or 2),
            stock_bajo=int(data.get('stock_bajo') or 10),
            categoria=data.get('categoria', 'General'),
            referencia_sku=data.get('sku') or data.get('referencia_sku') or 'SIN_SKU',
            codigo_barras=data.get('barcode') or data.get('codigo_barras') or '',
            imagen_url=imagen_url or (galeria_urls[0] if galeria_urls else "https://via.placeholder.com/150?text=No+Image"),
            imagenes=json.dumps(galeria_urls),
            videos=json.dumps(videos),
            plan=data.get('plan', 'basic'),
            etiquetas=json.dumps(parse_json_field(data.get('etiquetas'), [])),
            sucursal_id=sucursal_id,
            activo=True,
            estado_publicacion=True,
            badges_data=json.dumps(badges_data),
            es_dropshipping=str(data.get('es_dropshipping', False)).lower() in ['true', '1', 'yes', 'si']
        )
        
        # Badges legacy
        if hasattr(nuevo_prod, 'badge_destacado'):
            nuevo_prod.badge_destacado = badges_data.get('destacado', False)
        if hasattr(nuevo_prod, 'badge_mas_vendido'):
            nuevo_prod.badge_mas_vendido = data.get('mas_vendido', False) in [True, 'true', '1', 1]
        if hasattr(nuevo_prod, 'badge_envio_gratis'):
            nuevo_prod.badge_envio_gratis = badges_data.get('envio_gratis', False)
        
        if data.get('precio_original'):
            try:
                nuevo_prod.precio_original = float(data['precio_original'])
            except:
                pass
        
        # ★ v3.5: Asignar personalización
        if hasattr(nuevo_prod, 'personalizacion_activa'):
            nuevo_prod.personalizacion_activa = personalizacion_activa
        if hasattr(nuevo_prod, 'personalizacion_config'):
            nuevo_prod.personalizacion_config = json.dumps(personalizacion_config)

        # ★ v2.5: Asignar variantes
        variantes_raw = data.get('variantes')
        if variantes_raw and hasattr(nuevo_prod, 'variantes'):
            try:
                if isinstance(variantes_raw, str):
                    variantes_obj = json.loads(variantes_raw)
                else:
                    variantes_obj = variantes_raw
                # Validar estructura mínima
                if isinstance(variantes_obj, dict) and 'tipos' in variantes_obj and isinstance(variantes_obj['tipos'], list):
                    nuevo_prod.variantes = json.dumps(variantes_obj)
                    logger.info(f"🎛️ Variantes asignadas: {len(variantes_obj['tipos'])} tipo(s)")
                else:
                    nuevo_prod.variantes = None
            except Exception as ve:
                logger.warning(f"⚠️ Error parseando variantes al crear: {ve}")
                nuevo_prod.variantes = None
        elif hasattr(nuevo_prod, 'variantes'):
            nuevo_prod.variantes = None

        db.session.add(nuevo_prod)
        db.session.commit()

        producto_dict = safe_to_dict(nuevo_prod, ['id_producto', 'nombre', 'precio', 'stock', 'categoria'])
        producto_dict['id'] = nuevo_prod.id_producto
        producto_dict['imagenes'] = galeria_urls
        producto_dict['videos'] = videos
        producto_dict['personalizable'] = personalizacion_activa
        producto_dict['personalizacion_config'] = personalizacion_config if personalizacion_activa else None
        producto_dict['es_dropshipping'] = getattr(nuevo_prod, 'es_dropshipping', False) or False
        producto_dict['variantes'] = parse_json_field(getattr(nuevo_prod, 'variantes', None), None)
        producto_dict['tiene_variantes'] = bool(producto_dict['variantes'] and producto_dict['variantes'].get('tipos'))

        logger.info(f"✅ PRODUCTO CREADO: {nombre} - ID: {nuevo_prod.id_producto} | Personalizable: {personalizacion_activa} | Dropshipping: {producto_dict['es_dropshipping']} | Variantes: {producto_dict['tiene_variantes']}")

        return jsonify({
            "success": True,
            "message": "Producto creado exitosamente",
            "producto": producto_dict,
            "url": imagen_url,
            "imagenes": galeria_urls,
            "videos": videos
        }), 201

    except Exception as e:
        db.session.rollback()
        logger.error(f"❌ Error Guardar Producto: {traceback.format_exc()}")
        return jsonify({"success": False, "message": str(e)}), 500


# ============================================
# 3. ACTUALIZAR PRODUCTO - v3.6 CON PLAN GATING
# ============================================

@catalogo_api_bp.route('/producto/actualizar/<int:id_producto>', methods=['PUT', 'PATCH', 'OPTIONS'])
@cross_origin(supports_credentials=True)
def actualizar_producto(id_producto):
    """PUT/PATCH /api/producto/actualizar/{id}"""
    if request.method == 'OPTIONS':
        return jsonify({"success": True}), 200

    user_id = get_authorized_user_id()
    if not user_id:
        return jsonify({"success": False, "message": "No autorizado"}), 401

    try:
        producto = ProductoCatalogo.query.filter_by(id_producto=id_producto, usuario_id=int(user_id)).first()
        if not producto:
            return jsonify({"success": False, "message": "Producto no encontrado"}), 404

        is_form = 'multipart/form-data' in (request.content_type or '')
        data = request.form.to_dict() if is_form else (request.get_json(silent=True) or {})
        ctx = get_biz_context()

        logger.info(f"📝 ACTUALIZANDO PRODUCTO ID: {id_producto}")

        # Campos básicos
        if 'nombre' in data:
            producto.nombre = data['nombre'].strip()
        if 'descripcion' in data:
            producto.descripcion = data['descripcion']
        if 'categoria' in data:
            producto.categoria = data['categoria']
        if 'precio' in data:
            try:
                producto.precio = float(data['precio'])
            except:
                pass
        if 'costo' in data:
            try:
                producto.costo = float(data['costo'])
            except:
                pass
        if 'stock' in data:
            try:
                producto.stock = int(data['stock'])
            except:
                pass
        if 'sku' in data or 'referencia_sku' in data:
            producto.referencia_sku = data.get('sku') or data.get('referencia_sku')
        if 'barcode' in data or 'codigo_barras' in data:
            producto.codigo_barras = data.get('barcode') or data.get('codigo_barras')
        if 'activo' in data:
            producto.activo = data['activo'] in [True, 'true', '1', 1]
        if 'estado_publicacion' in data:
            producto.estado_publicacion = data['estado_publicacion'] in [True, 'true', '1', 1]

        # Badges
        if 'badges' in data:
            badges_data = procesar_badges_desde_request(data)
            producto.badges_data = json.dumps(badges_data)
            if hasattr(producto, 'badge_destacado'):
                producto.badge_destacado = badges_data.get('destacado', False)
            if hasattr(producto, 'badge_envio_gratis'):
                producto.badge_envio_gratis = badges_data.get('envio_gratis', False)

        # ★ v3.5: Actualizar personalización
        if 'personalizacion_activa' in data or 'personalizacion_config' in data:
            personalizacion_activa, personalizacion_config = procesar_personalizacion_desde_request(data)

            if hasattr(producto, 'personalizacion_activa'):
                producto.personalizacion_activa = personalizacion_activa

            if hasattr(producto, 'personalizacion_config'):
                producto.personalizacion_config = json.dumps(personalizacion_config)

            logger.info(f"🎨 Personalización actualizada: activa={personalizacion_activa}")

        # ★ v2.5: Variantes
        if 'variantes' in data and hasattr(producto, 'variantes'):
            variantes_raw = data.get('variantes')
            if variantes_raw in (None, '', 'null', '{}'):
                producto.variantes = None
                logger.info(f"🎛️ Variantes eliminadas del producto {id_producto}")
            else:
                try:
                    if isinstance(variantes_raw, str):
                        variantes_obj = json.loads(variantes_raw)
                    else:
                        variantes_obj = variantes_raw
                    if isinstance(variantes_obj, dict) and 'tipos' in variantes_obj and isinstance(variantes_obj['tipos'], list):
                        producto.variantes = json.dumps(variantes_obj)
                        logger.info(f"🎛️ Variantes actualizadas: {len(variantes_obj['tipos'])} tipo(s)")
                    else:
                        producto.variantes = None
                except Exception as ve:
                    logger.warning(f"⚠️ Error parseando variantes al actualizar: {ve}")

        # Dropshipping
        if 'es_dropshipping' in data and hasattr(producto, 'es_dropshipping'):
            val = data['es_dropshipping']
            if isinstance(val, str):
                producto.es_dropshipping = val.lower() in ['true', '1', 'yes', 'si']
            else:
                producto.es_dropshipping = bool(val)
            logger.info(f"🚚 Dropshipping actualizado: {producto.es_dropshipping}")

        # Videos
        if 'youtube_links' in data or 'videos' in data:
            videos_raw = data.get('youtube_links') or data.get('videos') or '[]'
            videos = parse_json_field(videos_raw, [])
            producto.videos = json.dumps([url for url in videos if url and isinstance(url, str)])

        # Imágenes
        galeria_actual = parse_json_field(producto.imagenes, [])
        
        if 'imagenes' in data:
            imgs = parse_json_field(data['imagenes'], None)
            if imgs is not None:
                galeria_actual = [url for url in imgs if url and isinstance(url, str)]
        
        # Nueva imagen principal
        file = request.files.get('imagen') or request.files.get('imagen_file')
        if file and file.filename:
            nombre_limpio = re.sub(r'[^a-zA-Z0-9]', '', producto.nombre[:15])
            p_id = f"user_{user_id}_{nombre_limpio}_{int(time.time())}"
            try:
                upload_result = cloudinary.uploader.upload(file, folder="productos_bizflow", public_id=p_id, overwrite=True, resource_type="auto")
                nueva_url = upload_result.get('secure_url')
                producto.imagen_url = nueva_url
                if nueva_url not in galeria_actual:
                    galeria_actual.insert(0, nueva_url)
            except Exception as e:
                logger.error(f"❌ Error subiendo imagen: {e}")
        
        # Galería adicional
        for i in range(1, 10):
            if f'imagen_{i}' in request.files:
                img_file = request.files[f'imagen_{i}']
                if img_file and img_file.filename:
                    try:
                        nombre_limpio = re.sub(r'[^a-zA-Z0-9]', '', producto.nombre[:15])
                        img_id = f"user_{user_id}_{nombre_limpio}_gal{i}_{int(time.time())}"
                        upload_result = cloudinary.uploader.upload(img_file, folder="productos_bizflow/galeria", public_id=img_id, overwrite=True, resource_type="auto")
                        url = upload_result.get('secure_url')
                        if url not in galeria_actual:
                            galeria_actual.append(url)
                    except:
                        pass
        
        galeria_actual = galeria_actual[:10]
        producto.imagenes = json.dumps(galeria_actual)
        if galeria_actual:
            producto.imagen_url = galeria_actual[0]

        # ═══════════════════════════════════════════════════════════════
        # ★ v3.6: VALIDAR SUB-FEATURES POR PLAN (sanitización silenciosa)
        # Limpiamos datos que el plan no permite ANTES del commit
        # ═══════════════════════════════════════════════════════════════
        nid = ctx.get('negocio_id') or producto.negocio_id
        if nid:
            nid = int(nid)

            # Badges manuales → requiere inv_badges_manuales (pro+)
            if not check_feature_access('inv_badges_manuales', nid):
                producto.badges_data = json.dumps({
                    'destacado': False, 'envio_gratis': False, 'pre_orden': False,
                    'edicion_limitada': False, 'oferta_flash': False, 'combo': False,
                    'garantia_extendida': False, 'eco_friendly': False,
                    'badge_personalizado': None
                })
                if hasattr(producto, 'badge_destacado'):
                    producto.badge_destacado = False
                if hasattr(producto, 'badge_envio_gratis'):
                    producto.badge_envio_gratis = False
                logger.info(f"🔒 Badges manuales sanitizados por plan")

            # Personalización → requiere inv_personalizacion (premium+)
            if not check_feature_access('inv_personalizacion', nid):
                if hasattr(producto, 'personalizacion_activa'):
                    producto.personalizacion_activa = False
                if hasattr(producto, 'personalizacion_config'):
                    producto.personalizacion_config = json.dumps({})
                logger.info(f"🔒 Personalización sanitizada por plan")

            # Videos → requiere inv_videos (premium+)
            if not check_feature_access('inv_videos', nid):
                producto.videos = json.dumps([])
                logger.info(f"🔒 Videos sanitizados por plan")

            # Galería multi-imagen → requiere inv_galeria_multi (pro+)
            if not check_feature_access('inv_galeria_multi', nid):
                galeria_check = parse_json_field(producto.imagenes, [])
                if len(galeria_check) > 1:
                    galeria_check = galeria_check[:1]
                    producto.imagenes = json.dumps(galeria_check)
                    producto.imagen_url = galeria_check[0] if galeria_check else producto.imagen_url
                    logger.info(f"🔒 Galería limitada a 1 imagen por plan")

            # Código de barras → requiere inv_codigo_barras (pro+)
            if not check_feature_access('inv_codigo_barras', nid):
                producto.codigo_barras = ''
                logger.info(f"🔒 Código de barras sanitizado por plan")

            # Costo de compra → requiere inv_costo_compra (pro+)
            if not check_feature_access('inv_costo_compra', nid):
                producto.costo = 0
                logger.info(f"🔒 Costo de compra sanitizado por plan")
        # ═══ FIN VALIDACIÓN SUB-FEATURES ═══

        db.session.commit()

        producto_dict = safe_to_dict(producto, ['id_producto', 'nombre', 'precio', 'stock', 'categoria'])
        producto_dict['id'] = producto.id_producto
        producto_dict['imagenes'] = parse_json_field(producto.imagenes, [])
        producto_dict['videos'] = parse_json_field(producto.videos, [])
        producto_dict['personalizable'] = getattr(producto, 'personalizacion_activa', False)
        producto_dict['personalizacion_config'] = parse_json_field(getattr(producto, 'personalizacion_config', '{}'), {}) if producto_dict['personalizable'] else None
        producto_dict['es_dropshipping'] = getattr(producto, 'es_dropshipping', False) or False
        producto_dict['variantes'] = parse_json_field(getattr(producto, 'variantes', None), None)
        producto_dict['tiene_variantes'] = bool(producto_dict['variantes'] and producto_dict['variantes'].get('tipos'))

        logger.info(f"✅ Producto {id_producto} actualizado | Personalización: {producto_dict['personalizable']} | Dropshipping: {producto_dict['es_dropshipping']} | Variantes: {producto_dict['tiene_variantes']}")

        return jsonify({"success": True, "message": "Producto actualizado", "producto": producto_dict}), 200

    except Exception as e:
        db.session.rollback()
        logger.error(f"❌ Error actualizar: {traceback.format_exc()}")
        return jsonify({"success": False, "message": str(e)}), 500
# ============================================
# 4. ELIMINAR PRODUCTO
# ============================================

@catalogo_api_bp.route('/producto/eliminar/<int:id_producto>', methods=['DELETE', 'OPTIONS'])
@cross_origin(supports_credentials=True)
def eliminar_producto(id_producto):
    """DELETE /api/producto/eliminar/{id}"""
    if request.method == 'OPTIONS': 
        return jsonify({"success": True}), 200
    
    user_id = get_authorized_user_id()
    if not user_id:
        return jsonify({"success": False, "message": "No autorizado"}), 401

    try:
        producto = ProductoCatalogo.query.filter_by(id_producto=id_producto, usuario_id=int(user_id)).first()
        if not producto:
            return jsonify({"success": False, "message": "Producto no encontrado"}), 404
        
        nombre = producto.nombre
        db.session.delete(producto)
        db.session.commit()
        
        logger.info(f"🗑️ Producto eliminado: {nombre} (ID: {id_producto})")
        return jsonify({"success": True, "message": f"Producto '{nombre}' eliminado"}), 200
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"❌ Error eliminar: {str(e)}")
        return jsonify({"success": False, "message": str(e)}), 500


# ============================================
# 5. OBTENER PRODUCTO POR ID
# ============================================

@catalogo_api_bp.route('/producto/<int:id_producto>', methods=['GET', 'OPTIONS'])
@cross_origin(supports_credentials=True)
def obtener_producto(id_producto):
    """GET /api/producto/{id}"""
    if request.method == 'OPTIONS':
        return jsonify({"success": True}), 200

    user_id = get_authorized_user_id()
    if not user_id:
        return jsonify({"success": False, "message": "No autorizado"}), 401

    try:
        producto = ProductoCatalogo.query.filter_by(id_producto=id_producto, usuario_id=int(user_id)).first()
        if not producto:
            return jsonify({"success": False, "message": "Producto no encontrado"}), 404

        data = safe_to_dict(producto, ['id_producto', 'nombre', 'precio', 'stock', 'categoria', 'descripcion', 'imagen_url', 'referencia_sku', 'codigo_barras'])
        data['id'] = producto.id_producto
        data['sku'] = producto.referencia_sku
        data['barcode'] = producto.codigo_barras
        data['imagenes'] = parse_json_field(producto.imagenes, [])
        data['videos'] = parse_json_field(producto.videos, [])
        data['youtube_links'] = data['videos']
        
        # ★ v3.5: Incluir personalización
        data['personalizable'] = getattr(producto, 'personalizacion_activa', False)
        data['personalizacion_activa'] = data['personalizable']
        if data['personalizable'] and hasattr(producto, 'get_personalizacion_config'):
            data['personalizacion_config'] = producto.get_personalizacion_config()
        elif data['personalizable']:
            data['personalizacion_config'] = parse_json_field(getattr(producto, 'personalizacion_config', '{}'), {})
        else:
            data['personalizacion_config'] = None

        # Dropshipping
        data['es_dropshipping'] = getattr(producto, 'es_dropshipping', False) or False

        return jsonify({"success": True, "producto": data}), 200

    except Exception as e:
        logger.error(f"❌ Error obtener producto: {str(e)}")
        return jsonify({"success": False, "message": str(e)}), 500


# ============================================
# 6. EDICIÓN RÁPIDA (Stock/Precio)
# ============================================

@catalogo_api_bp.route('/producto/edicion-rapida/<int:id_producto>', methods=['PATCH', 'OPTIONS'])
@cross_origin(supports_credentials=True)
def edicion_rapida(id_producto):
    """PATCH /api/producto/edicion-rapida/{id}"""
    if request.method == 'OPTIONS':
        return jsonify({"success": True}), 200

    user_id = get_authorized_user_id()
    if not user_id:
        return jsonify({"success": False, "message": "No autorizado"}), 401

    try:
        data = request.get_json(silent=True)
        if not data:
            return jsonify({"success": False, "message": "No se enviaron datos"}), 400

        producto = ProductoCatalogo.query.filter_by(id_producto=id_producto, usuario_id=int(user_id)).first()
        if not producto:
            return jsonify({"success": False, "message": "Producto no encontrado"}), 404

        old_stock = producto.stock
        old_precio = producto.precio

        if 'stock' in data:
            try:
                producto.stock = int(data['stock'])
            except:
                pass
        if 'precio' in data:
            try:
                producto.precio = float(data['precio'])
            except:
                pass
        if 'costo' in data:
            try:
                producto.costo = float(data['costo'])
            except:
                pass

        db.session.commit()

        logger.info(f"⚡ Edición rápida ID:{id_producto} | Stock: {old_stock}→{producto.stock} | Precio: {old_precio}→{producto.precio}")

        return jsonify({
            "success": True,
            "message": "Actualización rápida exitosa",
            "producto": {
                "id": producto.id_producto,
                "nombre": producto.nombre,
                "stock": producto.stock,
                "precio": producto.precio,
                "costo": producto.costo
            }
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "message": str(e)}), 500


# ============================================
# 7. DUPLICAR PRODUCTO - v3.5 (copia personalización)
# ============================================

@catalogo_api_bp.route('/producto/duplicar/<int:id_producto>', methods=['POST', 'OPTIONS'])
@cross_origin(supports_credentials=True)
def duplicar_producto(id_producto):
    """POST /api/producto/duplicar/{id}"""
    if request.method == 'OPTIONS':
        return jsonify({"success": True}), 200

    user_id = get_authorized_user_id()
    if not user_id:
        return jsonify({"success": False, "message": "No autorizado"}), 401

    try:
        original = ProductoCatalogo.query.filter_by(id_producto=id_producto, usuario_id=int(user_id)).first()
        if not original:
            return jsonify({"success": False, "message": "Producto no encontrado"}), 404

        duplicado = ProductoCatalogo(
            nombre=f"{original.nombre} (Copia)",
            precio=original.precio,
            negocio_id=original.negocio_id,
            usuario_id=int(user_id),
            descripcion=original.descripcion,
            costo=original.costo,
            stock=0,
            categoria=original.categoria,
            referencia_sku=f"{original.referencia_sku}_COPY" if original.referencia_sku else 'SIN_SKU',
            codigo_barras='',
            imagen_url=original.imagen_url,
            imagenes=original.imagenes,
            videos=original.videos,
            sucursal_id=original.sucursal_id,
            activo=False,
            badges_data=original.badges_data if hasattr(original, 'badges_data') else None
        )
        
        # Copiar badges legacy
        if hasattr(duplicado, 'badge_destacado') and hasattr(original, 'badge_destacado'):
            duplicado.badge_destacado = original.badge_destacado
        if hasattr(duplicado, 'badge_mas_vendido') and hasattr(original, 'badge_mas_vendido'):
            duplicado.badge_mas_vendido = original.badge_mas_vendido
        if hasattr(duplicado, 'badge_envio_gratis') and hasattr(original, 'badge_envio_gratis'):
            duplicado.badge_envio_gratis = original.badge_envio_gratis
        
        # ★ v3.5: Copiar personalización
        if hasattr(original, 'personalizacion_activa') and hasattr(duplicado, 'personalizacion_activa'):
            duplicado.personalizacion_activa = original.personalizacion_activa
        if hasattr(original, 'personalizacion_config') and hasattr(duplicado, 'personalizacion_config'):
            duplicado.personalizacion_config = original.personalizacion_config
        
        db.session.add(duplicado)
        db.session.commit()

        producto_dict = safe_to_dict(duplicado, ['id_producto', 'nombre', 'precio', 'stock', 'categoria'])
        producto_dict['id'] = duplicado.id_producto
        producto_dict['personalizable'] = getattr(duplicado, 'personalizacion_activa', False)

        logger.info(f"📋 Producto duplicado: {original.nombre} → {duplicado.nombre}")

        return jsonify({"success": True, "message": "Producto duplicado", "producto": producto_dict}), 201

    except Exception as e:
        db.session.rollback()
        logger.error(f"❌ Error duplicar: {str(e)}")
        return jsonify({"success": False, "message": str(e)}), 500


# ============================================
# 8. TOGGLE ACTIVO/INACTIVO
# ============================================

@catalogo_api_bp.route('/producto/<int:id_producto>/toggle-activo', methods=['POST', 'PATCH', 'OPTIONS'])
@cross_origin(supports_credentials=True)
def toggle_activo(id_producto):
    """POST/PATCH /api/producto/{id}/toggle-activo"""
    if request.method == 'OPTIONS':
        return jsonify({"success": True}), 200

    user_id = get_authorized_user_id()
    if not user_id:
        return jsonify({"success": False, "message": "No autorizado"}), 401

    try:
        producto = ProductoCatalogo.query.filter_by(id_producto=id_producto, usuario_id=int(user_id)).first()
        if not producto:
            return jsonify({"success": False, "message": "Producto no encontrado"}), 404

        data = request.get_json(silent=True) or {}
        
        if 'activo' in data:
            producto.activo = data['activo'] in [True, 'true', '1', 1]
        else:
            producto.activo = not producto.activo
        
        db.session.commit()

        return jsonify({
            "success": True,
            "message": f"Producto {'activado' if producto.activo else 'desactivado'}",
            "producto": {"id": producto.id_producto, "nombre": producto.nombre, "activo": producto.activo}
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "message": str(e)}), 500


# ============================================
# 9. AJUSTAR STOCK
# ============================================

@catalogo_api_bp.route('/producto/<int:id_producto>/stock', methods=['POST', 'OPTIONS'])
@cross_origin(supports_credentials=True)
def ajustar_stock(id_producto):
    """POST /api/producto/{id}/stock"""
    if request.method == 'OPTIONS':
        return jsonify({"success": True}), 200

    user_id = get_authorized_user_id()
    if not user_id:
        return jsonify({"success": False, "message": "No autorizado"}), 401

    try:
        data = request.get_json(silent=True)
        if not data:
            return jsonify({"success": False, "message": "No se enviaron datos"}), 400

        tipo = data.get('tipo', 'entrada').lower()
        cantidad = int(data.get('cantidad', 0))
        nota = data.get('nota', '').strip() or data.get('motivo', '').strip()

        if cantidad <= 0 and tipo != 'ajuste':
            return jsonify({"success": False, "message": "Cantidad debe ser mayor a 0"}), 400

        if tipo not in ['entrada', 'salida', 'ajuste']:
            return jsonify({"success": False, "message": "Tipo inválido"}), 400

        producto = ProductoCatalogo.query.filter_by(id_producto=id_producto, usuario_id=int(user_id)).first()
        if not producto:
            return jsonify({"success": False, "message": "Producto no encontrado"}), 404

        stock_anterior = producto.stock
        
        if tipo == 'entrada':
            nuevo_stock = stock_anterior + cantidad
            cantidad_movimiento = cantidad
        elif tipo == 'salida':
            if cantidad > stock_anterior:
                return jsonify({"success": False, "message": "Stock insuficiente"}), 400
            nuevo_stock = stock_anterior - cantidad
            cantidad_movimiento = -cantidad
        else:
            nuevo_stock = cantidad
            cantidad_movimiento = cantidad - stock_anterior

        producto.stock = nuevo_stock
        
        try:
            movimiento = MovimientoStock(
                producto_id=id_producto,
                usuario_id=int(user_id),
                negocio_id=producto.negocio_id,
                sucursal_id=producto.sucursal_id,
                tipo=tipo,
                cantidad=cantidad_movimiento,
                stock_anterior=stock_anterior,
                stock_nuevo=nuevo_stock,
                nota=nota or f"{'Entrada' if tipo == 'entrada' else 'Salida' if tipo == 'salida' else 'Ajuste'} de inventario"
            )
            db.session.add(movimiento)
        except Exception as e:
            logger.warning(f"⚠️ No se pudo registrar movimiento: {e}")

        db.session.commit()

        logger.info(f"📦 Stock ajustado: Producto {id_producto} | {stock_anterior} → {nuevo_stock} ({tipo})")

        return jsonify({
            "success": True,
            "message": f"Stock actualizado: {stock_anterior} → {nuevo_stock}",
            "producto": {
                "id": producto.id_producto,
                "nombre": producto.nombre,
                "stock_anterior": stock_anterior,
                "stock_nuevo": nuevo_stock,
                "tipo": tipo
            }
        }), 200

    except Exception as e:
        db.session.rollback()
        logger.error(f"❌ Error ajustar stock: {traceback.format_exc()}")
        return jsonify({"success": False, "message": str(e)}), 500


# ============================================
# 10. HISTORIAL DE MOVIMIENTOS
# ============================================

@catalogo_api_bp.route('/producto/<int:id_producto>/movimientos', methods=['GET', 'OPTIONS'])
@cross_origin(supports_credentials=True)
def obtener_movimientos(id_producto):
    """GET /api/producto/{id}/movimientos"""
    if request.method == 'OPTIONS':
        return jsonify({"success": True}), 200

    user_id = get_authorized_user_id()
    if not user_id:
        return jsonify({"success": False, "message": "No autorizado"}), 401

    try:
        producto = ProductoCatalogo.query.filter_by(id_producto=id_producto, usuario_id=int(user_id)).first()
        if not producto:
            return jsonify({"success": False, "message": "Producto no encontrado"}), 404

        try:
            movimientos = MovimientoStock.query.filter_by(producto_id=id_producto).order_by(MovimientoStock.fecha.desc()).limit(100).all()
            total_entradas = sum(m.cantidad for m in movimientos if m.tipo == 'entrada')
            total_salidas = abs(sum(m.cantidad for m in movimientos if m.tipo == 'salida'))
            
            return jsonify({
                "success": True,
                "producto": {"id": producto.id_producto, "nombre": producto.nombre, "stock_actual": producto.stock},
                "resumen": {"total_entradas": total_entradas, "total_salidas": total_salidas, "total_movimientos": len(movimientos)},
                "movimientos": [safe_to_dict(m, ['id', 'tipo', 'cantidad', 'stock_anterior', 'stock_nuevo', 'fecha', 'nota']) for m in movimientos]
            }), 200
        except Exception as e:
            logger.warning(f"⚠️ Error obteniendo movimientos: {e}")
            return jsonify({
                "success": True,
                "producto": {"id": producto.id_producto, "nombre": producto.nombre, "stock_actual": producto.stock},
                "resumen": {"total_entradas": 0, "total_salidas": 0, "total_movimientos": 0},
                "movimientos": []
            }), 200

    except Exception as e:
        logger.error(f"❌ Error obtener movimientos: {str(e)}")
        return jsonify({"success": False, "message": str(e)}), 500


# ============================================
# 11. ALERTAS DE STOCK
# ============================================

@catalogo_api_bp.route('/stock/alertas', methods=['GET', 'OPTIONS'])
@cross_origin(supports_credentials=True)
def obtener_alertas_stock():
    """GET /api/stock/alertas"""
    if request.method == 'OPTIONS':
        return jsonify({"success": True}), 200

    user_id = get_authorized_user_id()
    if not user_id:
        return jsonify({"success": False, "message": "No autorizado"}), 401

    try:
        ctx = get_biz_context()
        
        query = ProductoCatalogo.query.filter_by(usuario_id=int(user_id), activo=True)
        
        if ctx.get('negocio_id'):
            query = query.filter_by(negocio_id=ctx['negocio_id'])
        
        query = query.filter(ProductoCatalogo.stock <= ProductoCatalogo.stock_bajo)
        productos = query.order_by(ProductoCatalogo.stock.asc()).all()
        
        alertas = []
        for p in productos:
            try:
                nivel = p.nivel_stock() if hasattr(p, 'nivel_stock') else ('critico' if p.stock <= getattr(p, 'stock_critico', 2) else 'bajo')
                alertas.append({
                    "id": p.id_producto,
                    "producto": {
                        "id": p.id_producto,
                        "nombre": p.nombre,
                        "sku": p.referencia_sku,
                        "stock": p.stock,
                        "imagen_url": p.imagen_url
                    },
                    "tipo": 'critical' if nivel == 'critico' else 'warning',
                    "message": f"{'Sin stock' if p.stock == 0 else 'Stock crítico' if nivel == 'critico' else 'Stock bajo'}: {p.stock} unidades",
                    "fecha": datetime.utcnow().isoformat()
                })
            except Exception as e:
                logger.warning(f"⚠️ Error procesando alerta: {e}")

        return jsonify({
            "success": True,
            "total": len(alertas),
            "criticos": len([a for a in alertas if a['tipo'] == 'critical']),
            "bajos": len([a for a in alertas if a['tipo'] == 'warning']),
            "alertas": alertas
        }), 200

    except Exception as e:
        logger.error(f"❌ Error alertas stock: {str(e)}")
        return jsonify({"success": False, "message": str(e)}), 500


# ============================================
# 12. ESTADÍSTICAS DE INVENTARIO - v3.5
# ============================================

@catalogo_api_bp.route('/inventario/estadisticas', methods=['GET', 'OPTIONS'])
@cross_origin(supports_credentials=True)
def estadisticas_inventario():
    """GET /api/inventario/estadisticas"""
    if request.method == 'OPTIONS':
        return jsonify({"success": True}), 200

    user_id = get_authorized_user_id()
    if not user_id:
        return jsonify({"success": False, "message": "No autorizado"}), 401

    try:
        ctx = get_biz_context()
        
        query = ProductoCatalogo.query.filter_by(usuario_id=int(user_id))
        if ctx.get('negocio_id'):
            query = query.filter_by(negocio_id=ctx['negocio_id'])
        
        productos = query.all()
        
        total = len(productos)
        stock_bajo_threshold = 10
        en_stock = len([p for p in productos if p.stock > stock_bajo_threshold])
        stock_bajo = len([p for p in productos if 0 < p.stock <= stock_bajo_threshold])
        sin_stock = len([p for p in productos if p.stock == 0])
        
        # ★ v3.5: Contar personalizables
        personalizables = len([p for p in productos if getattr(p, 'personalizacion_activa', False)])

        # Dropshipping: excluir stock virtual de la valorización real
        dropshipping_count = len([p for p in productos if getattr(p, 'es_dropshipping', False)])
        productos_fisicos = [p for p in productos if not getattr(p, 'es_dropshipping', False)]

        valor_total = sum((p.precio * p.stock) for p in productos_fisicos)
        costo_total = sum((p.costo * p.stock) for p in productos_fisicos)

        categorias = {}
        for p in productos:
            cat = p.categoria or 'Sin categoría'
            categorias[cat] = categorias.get(cat, 0) + 1

        return jsonify({
            "success": True,
            "stats": {
                "total": total,
                "en_stock": en_stock,
                "stock_bajo": stock_bajo,
                "sin_stock": sin_stock,
                "personalizables": personalizables,
                "dropshipping": dropshipping_count,
                "valor_inventario": round(valor_total, 2),
                "costo_inventario": round(costo_total, 2),
                "ganancia_potencial": round(valor_total - costo_total, 2)
            },
            "categorias": categorias,
            "context": ctx
        }), 200

    except Exception as e:
        logger.error(f"❌ Error estadísticas: {str(e)}")
        return jsonify({"success": False, "message": str(e)}), 500


# ============================================
# 13-16. CATEGORÍAS (sin cambios mayores)
# ============================================

@catalogo_api_bp.route('/categorias', methods=['GET', 'OPTIONS'])
@cross_origin(supports_credentials=True)
def listar_categorias():
    """GET /api/categorias - Público si se pasa negocio_id, autenticado si no"""
    if request.method == 'OPTIONS':
        response = jsonify({"success": True})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,X-User-ID,X-Business-ID,X-Negocio-ID,X-Sucursal-ID')
        response.headers.add('Access-Control-Allow-Methods', 'GET,OPTIONS')
        return response, 200

    try:
        # ★ FIX: Intentar auth pero NO fallar si no hay token
        user_id = None
        try:
            user_id = get_authorized_user_id()
        except Exception:
            pass

        # Obtener negocio_id de múltiples fuentes
        negocio_id = (
            request.args.get('negocio_id') or 
            request.headers.get('X-Business-ID') or
            request.headers.get('X-Negocio-ID')
        )
        
        # Si hay usuario autenticado, intentar obtener del contexto también
        if not negocio_id and user_id:
            ctx = get_biz_context()
            negocio_id = ctx.get('negocio_id')
        
        if not negocio_id:
            return jsonify({"success": False, "message": "negocio_id es requerido", "categorias": []}), 400
        
        negocio_id = int(negocio_id)
        categorias_list = []
        
        # ★ FIX: Consultar SIN filtrar por usuario_id (las categorías son del negocio)
        try:
            query = CategoriaProducto.query.filter_by(negocio_id=negocio_id)
            
            # Si hay usuario autenticado, filtrar por usuario también (panel admin)
            if user_id:
                query = query.filter_by(usuario_id=int(user_id))
            
            # Solo mostrar activas en acceso público
            if not user_id and hasattr(CategoriaProducto, 'activo'):
                query = query.filter(CategoriaProducto.activo == True)
            
            categorias_db = query.order_by(
                CategoriaProducto.orden.asc() if hasattr(CategoriaProducto, 'orden') else CategoriaProducto.id_categoria.asc(),
                CategoriaProducto.id_categoria.asc()
            ).all()
        except Exception as e:
            logger.error(f"❌ Error consultando categorias_producto: {e}")
            categorias_db = []
        
        # Contar productos por categoría
        productos_por_cat = {}
        try:
            prod_query = ProductoCatalogo.query.filter_by(
                negocio_id=negocio_id,
                activo=True
            )
            if user_id:
                prod_query = prod_query.filter_by(usuario_id=int(user_id))
            
            productos = prod_query.all()
            
            for p in productos:
                cat_nombre = p.categoria or 'Sin categoría'
                productos_por_cat[cat_nombre] = productos_por_cat.get(cat_nombre, 0) + 1
        except Exception as e:
            productos = []
        
        for cat in categorias_db:
            try:
                cat_dict = {
                    'id': getattr(cat, 'id_categoria', None),
                    'id_categoria': getattr(cat, 'id_categoria', None),
                    'nombre': getattr(cat, 'nombre', 'Sin nombre'),
                    'icono': getattr(cat, 'icono', '📦') or '📦',
                    'color': getattr(cat, 'color', '#6366f1') or '#6366f1',
                    'orden': getattr(cat, 'orden', 0) or 0,
                    'activo': getattr(cat, 'activo', True) if getattr(cat, 'activo', True) is not None else True,
                    'count': productos_por_cat.get(getattr(cat, 'nombre', ''), 0),
                    'featured': bool(getattr(cat, 'featured', False)),
                    'source': 'database'
                }
                categorias_list.append(cat_dict)
            except Exception as e:
                continue
        
        # Fallback: generar categorías de los productos si no hay en BD
        if not categorias_list and productos:
            categorias_de_productos = set()
            for p in productos:
                if p.categoria:
                    categorias_de_productos.add(p.categoria)
            
            for idx, nombre in enumerate(sorted(categorias_de_productos)):
                categorias_list.append({
                    'id': None,
                    'id_categoria': None,
                    'nombre': nombre,
                    'icono': '📦',
                    'color': '#6b7280',
                    'orden': idx,
                    'activo': True,
                    'count': productos_por_cat.get(nombre, 0),
                    'featured': False,
                    'source': 'productos'
                })

        return jsonify({
            "success": True,
            "total": len(categorias_list),
            "categorias": categorias_list,
            "source": "database" if any(c.get('source') == 'database' for c in categorias_list) else "productos"
        }), 200

    except Exception as e:
        logger.error(f"❌ Error en GET /categorias: {traceback.format_exc()}")
        return jsonify({"success": False, "message": str(e), "categorias": []}), 500


@catalogo_api_bp.route('/categorias', methods=['POST'])
@cross_origin(supports_credentials=True)
def crear_categoria():
    """POST /api/categorias"""
    user_id = get_authorized_user_id()
    if not user_id:
        return jsonify({"success": False, "message": "No autorizado"}), 401

    try:
        data = request.get_json(silent=True)
        if not data:
            return jsonify({"success": False, "message": "No se enviaron datos JSON válidos"}), 400
        
        nombre = (data.get('nombre') or data.get('name', '')).strip()
        if not nombre:
            return jsonify({"success": False, "message": "El nombre es requerido"}), 400
        
        ctx = get_biz_context()
        negocio_id = data.get('negocio_id') or ctx.get('negocio_id')
        
        if not negocio_id:
            return jsonify({"success": False, "message": "negocio_id es requerido"}), 400
        limit_error = check_limit('crear_categoria', negocio_id, CategoriaProducto, 'negocio_id')
        if limit_error:
            return limit_error
        
        negocio_id = int(negocio_id)
        user_id_int = int(user_id)
        
        try:
            existente = CategoriaProducto.query.filter_by(
                negocio_id=negocio_id,
                usuario_id=user_id_int,
                nombre=nombre
            ).first()
            
            if existente:
                return jsonify({
                    "success": False, 
                    "message": f"Ya existe una categoría con el nombre '{nombre}'",
                    "categoria": {'id': existente.id_categoria, 'nombre': existente.nombre}
                }), 409
        except Exception:
            pass
        
        max_orden = 0
        try:
            result = db.session.query(db.func.max(CategoriaProducto.orden)).filter_by(
                negocio_id=negocio_id,
                usuario_id=user_id_int
            ).scalar()
            max_orden = result or 0
        except Exception:
            pass
        
        nueva_categoria = CategoriaProducto(
            nombre=nombre,
            icono=data.get('icono') or data.get('icon') or '📦',
            color=data.get('color') or '#6366f1',
            negocio_id=negocio_id,
            usuario_id=user_id_int,
            orden=max_orden + 1,
            activo=True
        )
        
        if hasattr(nueva_categoria, 'featured'):
            nueva_categoria.featured = data.get('featured', False) in [True, 'true', '1', 1]
        
        db.session.add(nueva_categoria)
        db.session.commit()
        
        cat_dict = {
            'id': nueva_categoria.id_categoria,
            'id_categoria': nueva_categoria.id_categoria,
            'nombre': nueva_categoria.nombre,
            'icono': nueva_categoria.icono,
            'color': nueva_categoria.color,
            'orden': getattr(nueva_categoria, 'orden', 0),
            'activo': getattr(nueva_categoria, 'activo', True)
        }

        return jsonify({
            "success": True,
            "message": f"Categoría '{nombre}' creada",
            "categoria": cat_dict,
            "id": nueva_categoria.id_categoria
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "message": str(e)}), 500


@catalogo_api_bp.route('/categorias/<int:id_categoria>', methods=['PUT', 'PATCH', 'OPTIONS'])
@cross_origin(supports_credentials=True)
def actualizar_categoria(id_categoria):
    """PUT/PATCH /api/categorias/{id}"""
    if request.method == 'OPTIONS':
        return jsonify({"success": True}), 200

    user_id = get_authorized_user_id()
    if not user_id:
        return jsonify({"success": False, "message": "No autorizado"}), 401

    try:
        categoria = CategoriaProducto.query.filter_by(id_categoria=id_categoria, usuario_id=int(user_id)).first()
        if not categoria:
            return jsonify({"success": False, "message": "Categoría no encontrada"}), 404

        data = request.get_json(silent=True)
        if not data:
            return jsonify({"success": False, "message": "No se enviaron datos"}), 400
        
        nombre_anterior = categoria.nombre
        productos_afectados = 0
        
        if 'nombre' in data or 'name' in data:
            nuevo_nombre = (data.get('nombre') or data.get('name', '')).strip()
            if nuevo_nombre and nuevo_nombre != nombre_anterior:
                categoria.nombre = nuevo_nombre
                try:
                    productos_afectados = ProductoCatalogo.query.filter_by(
                        usuario_id=int(user_id), 
                        categoria=nombre_anterior
                    ).update({'categoria': nuevo_nombre})
                except Exception:
                    pass
        
        if 'icono' in data or 'icon' in data:
            categoria.icono = data.get('icono') or data.get('icon')
        if 'color' in data:
            categoria.color = data['color']
        if 'orden' in data:
            try:
                categoria.orden = int(data['orden'])
            except:
                pass
        if 'activo' in data:
            categoria.activo = data['activo'] in [True, 'true', '1', 1]
        if 'featured' in data:
            if hasattr(categoria, 'featured'):
                categoria.featured = data['featured'] in [True, 'true', '1', 1]

        db.session.commit()
        
        cat_dict = {
            'id': categoria.id_categoria,
            'id_categoria': categoria.id_categoria,
            'nombre': categoria.nombre,
            'icono': getattr(categoria, 'icono', '📦'),
            'color': getattr(categoria, 'color', '#6366f1'),
            'orden': getattr(categoria, 'orden', 0),
            'activo': getattr(categoria, 'activo', True)
        }

        return jsonify({
            "success": True, 
            "message": "Categoría actualizada", 
            "categoria": cat_dict,
            "productos_afectados": productos_afectados
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "message": str(e)}), 500


@catalogo_api_bp.route('/categorias/<int:id_categoria>', methods=['DELETE', 'OPTIONS'])
@cross_origin(supports_credentials=True)
def eliminar_categoria(id_categoria):
    """DELETE /api/categorias/{id}"""
    if request.method == 'OPTIONS':
        return jsonify({"success": True}), 200

    user_id = get_authorized_user_id()
    if not user_id:
        return jsonify({"success": False, "message": "No autorizado"}), 401

    try:
        categoria = CategoriaProducto.query.filter_by(id_categoria=id_categoria, usuario_id=int(user_id)).first()
        if not categoria:
            return jsonify({"success": False, "message": "Categoría no encontrada"}), 404

        nombre = categoria.nombre
        productos_afectados = 0
        
        try:
            productos_afectados = ProductoCatalogo.query.filter_by(
                usuario_id=int(user_id), 
                categoria=nombre
            ).update({'categoria': ''})
        except Exception:
            pass
        
        db.session.delete(categoria)
        db.session.commit()

        return jsonify({
            "success": True, 
            "message": f"Categoría '{nombre}' eliminada", 
            "productos_afectados": productos_afectados
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "message": str(e)}), 500


@catalogo_api_bp.route('/categorias/reordenar', methods=['POST', 'OPTIONS'])
@cross_origin(supports_credentials=True)
def reordenar_categorias():
    """POST /api/categorias/reordenar"""
    if request.method == 'OPTIONS':
        return jsonify({"success": True}), 200

    user_id = get_authorized_user_id()
    if not user_id:
        return jsonify({"success": False, "message": "No autorizado"}), 401

    try:
        data = request.get_json(silent=True)
        if not data or 'orden' not in data:
            return jsonify({"success": False, "message": "Se requiere lista de orden"}), 400
        
        actualizados = 0
        
        for item in data['orden']:
            cat_id = item.get('id') or item.get('id_categoria')
            nuevo_orden = item.get('orden', 0)
            
            if cat_id:
                try:
                    categoria = CategoriaProducto.query.filter_by(
                        id_categoria=int(cat_id),
                        usuario_id=int(user_id)
                    ).first()
                    
                    if categoria and hasattr(categoria, 'orden'):
                        categoria.orden = nuevo_orden
                        actualizados += 1
                except Exception:
                    pass
        
        db.session.commit()

        return jsonify({
            "success": True,
            "message": f"{actualizados} categorías reordenadas",
            "actualizados": actualizados
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "message": str(e)}), 500


# ============================================
# 17-24. IMÁGENES, VIDEOS, BÚSQUEDA, IMPORT/EXPORT
# ============================================

@catalogo_api_bp.route('/producto/<int:id_producto>/imagenes', methods=['POST', 'OPTIONS'])
@cross_origin(supports_credentials=True)
def agregar_imagenes(id_producto):
    """POST /api/producto/{id}/imagenes"""
    if request.method == 'OPTIONS':
        return jsonify({"success": True}), 200

    user_id = get_authorized_user_id()
    if not user_id:
        return jsonify({"success": False, "message": "No autorizado"}), 401

    try:
        producto = ProductoCatalogo.query.filter_by(id_producto=id_producto, usuario_id=int(user_id)).first()
        if not producto:
            return jsonify({"success": False, "message": "Producto no encontrado"}), 404

        galeria_actual = parse_json_field(producto.imagenes, [])
        nuevas_urls = []
        
        for key in request.files:
            file = request.files[key]
            if file.filename:
                nombre_limpio = re.sub(r'[^a-zA-Z0-9]', '', producto.nombre[:15])
                img_id = f"user_{user_id}_{nombre_limpio}_{int(time.time())}_{key}"
                try:
                    upload_result = cloudinary.uploader.upload(file, folder="productos_bizflow/galeria", public_id=img_id, overwrite=True, resource_type="auto")
                    nuevas_urls.append(upload_result.get('secure_url'))
                except Exception as e:
                    logger.error(f"Error subiendo {key}: {e}")

        if not nuevas_urls:
            return jsonify({"success": False, "message": "No se recibieron imágenes"}), 400

        galeria_completa = galeria_actual + nuevas_urls
        galeria_completa = galeria_completa[:10]
        
        producto.imagenes = json.dumps(galeria_completa)
        db.session.commit()

        return jsonify({"success": True, "message": f"{len(nuevas_urls)} imágenes agregadas", "imagenes": galeria_completa}), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "message": str(e)}), 500


@catalogo_api_bp.route('/producto/<int:id_producto>/imagenes/<int:index>', methods=['DELETE', 'OPTIONS'])
@cross_origin(supports_credentials=True)
def eliminar_imagen(id_producto, index):
    """DELETE /api/producto/{id}/imagenes/{index}"""
    if request.method == 'OPTIONS':
        return jsonify({"success": True}), 200

    user_id = get_authorized_user_id()
    if not user_id:
        return jsonify({"success": False, "message": "No autorizado"}), 401

    try:
        producto = ProductoCatalogo.query.filter_by(id_producto=id_producto, usuario_id=int(user_id)).first()
        if not producto:
            return jsonify({"success": False, "message": "Producto no encontrado"}), 404

        galeria = parse_json_field(producto.imagenes, [])
        
        if index < 0 or index >= len(galeria):
            return jsonify({"success": False, "message": "Índice de imagen inválido"}), 400
        
        galeria.pop(index)
        producto.imagenes = json.dumps(galeria)
        
        if index == 0 and galeria:
            producto.imagen_url = galeria[0]
        elif index == 0:
            producto.imagen_url = "https://via.placeholder.com/150?text=No+Image"
        
        db.session.commit()

        return jsonify({"success": True, "message": "Imagen eliminada", "imagenes": galeria}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "message": str(e)}), 500


@catalogo_api_bp.route('/producto/<int:id_producto>/videos', methods=['POST', 'OPTIONS'])
@cross_origin(supports_credentials=True)
def agregar_video(id_producto):
    """POST /api/producto/{id}/videos"""
    if request.method == 'OPTIONS':
        return jsonify({"success": True}), 200

    user_id = get_authorized_user_id()
    if not user_id:
        return jsonify({"success": False, "message": "No autorizado"}), 401

    try:
        producto = ProductoCatalogo.query.filter_by(id_producto=id_producto, usuario_id=int(user_id)).first()
        if not producto:
            return jsonify({"success": False, "message": "Producto no encontrado"}), 404

        data = request.get_json(silent=True) or {}
        videos_actuales = parse_json_field(producto.videos, [])
        nuevos_videos = []
        
        if 'videos' in data:
            for v in data['videos']:
                url = v.get('url', '') if isinstance(v, dict) else v
                if url and ('youtube' in url or 'youtu.be' in url or 'vimeo' in url):
                    nuevos_videos.append(url)
        elif 'url' in data:
            url = data['url']
            if url and ('youtube' in url or 'youtu.be' in url or 'vimeo' in url):
                nuevos_videos.append(url)

        if not nuevos_videos:
            return jsonify({"success": False, "message": "No se recibieron URLs válidas"}), 400

        videos_unicos = [v for v in nuevos_videos if v not in videos_actuales]
        
        if not videos_unicos:
            return jsonify({"success": False, "message": "Videos ya agregados"}), 400

        todos_videos = videos_actuales + videos_unicos
        todos_videos = todos_videos[:10]
        
        producto.videos = json.dumps(todos_videos)
        db.session.commit()

        return jsonify({"success": True, "message": f"{len(videos_unicos)} video(s) agregado(s)", "videos": todos_videos}), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "message": str(e)}), 500


@catalogo_api_bp.route('/producto/<int:id_producto>/videos/<int:index>', methods=['DELETE', 'OPTIONS'])
@cross_origin(supports_credentials=True)
def eliminar_video(id_producto, index):
    """DELETE /api/producto/{id}/videos/{index}"""
    if request.method == 'OPTIONS':
        return jsonify({"success": True}), 200

    user_id = get_authorized_user_id()
    if not user_id:
        return jsonify({"success": False, "message": "No autorizado"}), 401

    try:
        producto = ProductoCatalogo.query.filter_by(id_producto=id_producto, usuario_id=int(user_id)).first()
        if not producto:
            return jsonify({"success": False, "message": "Producto no encontrado"}), 404

        videos = parse_json_field(producto.videos, [])
        
        if index < 0 or index >= len(videos):
            return jsonify({"success": False, "message": "Índice de video inválido"}), 400
        
        videos.pop(index)
        producto.videos = json.dumps(videos)
        db.session.commit()

        return jsonify({"success": True, "message": "Video eliminado", "videos": videos}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "message": str(e)}), 500


@catalogo_api_bp.route('/producto/buscar-codigo', methods=['GET', 'OPTIONS'])
@cross_origin(supports_credentials=True)
def buscar_por_codigo():
    """GET /api/producto/buscar-codigo?codigo={barcode|sku}"""
    if request.method == 'OPTIONS':
        return jsonify({"success": True}), 200

    user_id = get_authorized_user_id()
    if not user_id:
        return jsonify({"success": False, "message": "No autorizado"}), 401

    try:
        codigo = request.args.get('codigo', '').strip()
        
        if not codigo:
            return jsonify({"success": False, "message": "Código requerido"}), 400

        ctx = get_biz_context()
        query = ProductoCatalogo.query.filter_by(usuario_id=int(user_id))
        
        if ctx.get('negocio_id'):
            query = query.filter_by(negocio_id=ctx['negocio_id'])
        
        producto = query.filter(
            db.or_(
                ProductoCatalogo.codigo_barras == codigo,
                ProductoCatalogo.referencia_sku == codigo,
                ProductoCatalogo.referencia_sku.ilike(codigo)
            )
        ).first()
        
        if not producto:
            return jsonify({"success": False, "encontrado": False, "message": "Producto no encontrado"}), 404

        producto_dict = safe_to_dict(producto, ['id_producto', 'nombre', 'precio', 'stock', 'categoria'])
        producto_dict['id'] = producto.id_producto

        return jsonify({"success": True, "encontrado": True, "producto": producto_dict}), 200

    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500


@catalogo_api_bp.route('/productos/buscar', methods=['GET', 'OPTIONS'])
@cross_origin(supports_credentials=True)
def buscar_productos():
    """GET /api/productos/buscar?q={término}"""
    if request.method == 'OPTIONS':
        return jsonify({"success": True}), 200

    user_id = get_authorized_user_id()
    if not user_id:
        return jsonify({"success": False, "message": "No autorizado"}), 401

    try:
        q = request.args.get('q', '').strip()
        
        if len(q) < 2:
            return jsonify({"success": True, "productos": [], "message": "Término muy corto"}), 200

        ctx = get_biz_context()
        termino = f"%{q}%"
        
        query = ProductoCatalogo.query.filter_by(usuario_id=int(user_id))
        
        if ctx.get('negocio_id'):
            query = query.filter_by(negocio_id=ctx['negocio_id'])
        
        productos = query.filter(
            db.or_(
                ProductoCatalogo.nombre.ilike(termino),
                ProductoCatalogo.referencia_sku.ilike(termino),
                ProductoCatalogo.codigo_barras.ilike(termino),
                ProductoCatalogo.categoria.ilike(termino),
                ProductoCatalogo.descripcion.ilike(termino)
            )
        ).limit(20).all()

        resultados = [{
            "id": p.id_producto, "nombre": p.nombre, "sku": p.referencia_sku,
            "barcode": p.codigo_barras, "categoria": p.categoria,
            "precio": p.precio, "stock": p.stock, "imagen_url": p.imagen_url,
            "personalizable": getattr(p, 'personalizacion_activa', False)
        } for p in productos]

        return jsonify({"success": True, "termino": q, "total": len(resultados), "productos": resultados}), 200

    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500


@catalogo_api_bp.route('/productos/importar', methods=['POST', 'OPTIONS'])
@cross_origin(supports_credentials=True)
def importar_productos():
    """POST /api/productos/importar"""
    if request.method == 'OPTIONS':
        return jsonify({"success": True}), 200

    user_id = get_authorized_user_id()
    if not user_id:
        return jsonify({"success": False, "message": "No autorizado"}), 401

    try:
        ctx = get_biz_context()
        negocio_id = ctx.get('negocio_id') or 1
        sucursal_id = ctx.get('sucursal_id') or 1
        
        productos_data = []
        
        if 'archivo' in request.files:
            import csv
            import io
            
            archivo = request.files['archivo']
            if not archivo.filename:
                return jsonify({"success": False, "message": "No se seleccionó archivo"}), 400
            
            contenido = archivo.read().decode('utf-8-sig')
            reader = csv.DictReader(io.StringIO(contenido))
            
            for row in reader:
                productos_data.append({
                    'nombre': row.get('nombre') or row.get('name') or row.get('producto', ''),
                    'sku': row.get('sku') or row.get('codigo', ''),
                    'barcode': row.get('barcode') or row.get('codigo_barras', ''),
                    'categoria': row.get('categoria') or row.get('category', 'General'),
                    'precio': row.get('precio') or row.get('price', 0),
                    'costo': row.get('costo') or row.get('cost', 0),
                    'stock': row.get('stock') or row.get('cantidad', 0),
                    'descripcion': row.get('descripcion') or row.get('description', '')
                })
        else:
            data = request.get_json(silent=True)
            if not data:
                return jsonify({"success": False, "message": "No se enviaron datos"}), 400
            
            if isinstance(data, list):
                productos_data = data
            elif 'productos' in data:
                productos_data = data['productos']
            else:
                return jsonify({"success": False, "message": "Formato inválido"}), 400

        if not productos_data:
            return jsonify({"success": False, "message": "No hay productos para importar"}), 400

        importados = 0
        errores = []

        for idx, prod in enumerate(productos_data):
            try:
                nombre = str(prod.get('nombre', '')).strip()
                if not nombre:
                    errores.append({"fila": idx + 1, "error": "Nombre vacío"})
                    continue
                
                nuevo = ProductoCatalogo(
                    nombre=nombre,
                    precio=float(prod.get('precio', 0)),
                    negocio_id=negocio_id,
                    usuario_id=int(user_id),
                    descripcion=str(prod.get('descripcion', '')),
                    costo=float(prod.get('costo', 0)),
                    stock=int(prod.get('stock', 0)),
                    categoria=str(prod.get('categoria', 'General')),
                    referencia_sku=str(prod.get('sku', '')),
                    codigo_barras=str(prod.get('barcode', '')),
                    sucursal_id=sucursal_id,
                    imagen_url="https://via.placeholder.com/150?text=Import",
                    activo=True
                )
                
                db.session.add(nuevo)
                importados += 1
                
            except Exception as e:
                errores.append({"fila": idx + 1, "error": str(e)})

        db.session.commit()

        return jsonify({
            "success": True,
            "message": f"{importados} productos importados",
            "importados": importados,
            "errores": len(errores),
            "detalle_errores": errores[:20]
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "message": str(e)}), 500


@catalogo_api_bp.route('/productos/exportar', methods=['GET', 'POST', 'OPTIONS'])
@cross_origin(supports_credentials=True)
def exportar_productos():
    """GET/POST /api/productos/exportar"""
    if request.method == 'OPTIONS':
        return jsonify({"success": True}), 200

    user_id = get_authorized_user_id()
    if not user_id:
        return jsonify({"success": False, "message": "No autorizado"}), 401

    try:
        ctx = get_biz_context()
        params = request.get_json(silent=True) if request.method == 'POST' else request.args.to_dict()
        params = params or {}
        
        formato = params.get('formato', 'csv').lower()
        filtro = params.get('filtro', 'all')
        campos = params.get('campos', ['nombre', 'sku', 'codigo_barras', 'categoria', 'precio', 'costo', 'stock'])
        
        if isinstance(campos, str):
            campos = [c.strip() for c in campos.split(',')]

        query = ProductoCatalogo.query.filter_by(usuario_id=int(user_id))
        
        if ctx.get('negocio_id'):
            query = query.filter_by(negocio_id=ctx['negocio_id'])
        
        if filtro == 'in_stock':
            query = query.filter(ProductoCatalogo.stock > 10)
        elif filtro == 'low_stock':
            query = query.filter(ProductoCatalogo.stock > 0, ProductoCatalogo.stock <= 10)
        elif filtro == 'out_stock':
            query = query.filter(ProductoCatalogo.stock == 0)
        
        productos = query.all()

        campo_map = {
            'nombre': lambda p: p.nombre, 'sku': lambda p: p.referencia_sku or '',
            'codigo_barras': lambda p: p.codigo_barras or '', 'categoria': lambda p: p.categoria or '',
            'precio': lambda p: p.precio, 'costo': lambda p: p.costo,
            'stock': lambda p: p.stock, 'descripcion': lambda p: p.descripcion or '',
            'personalizable': lambda p: 'Si' if getattr(p, 'personalizacion_activa', False) else 'No'
        }

        datos = []
        for p in productos:
            fila = {}
            for campo in campos:
                if campo in campo_map:
                    fila[campo] = campo_map[campo](p)
            datos.append(fila)

        if formato == 'json':
            return jsonify({"success": True, "total": len(datos), "formato": "json", "datos": datos}), 200
        else:
            import io
            import csv
            
            output = io.StringIO()
            writer = csv.DictWriter(output, fieldnames=campos)
            writer.writeheader()
            writer.writerows(datos)
            
            return jsonify({
                "success": True, "total": len(datos), "formato": "csv",
                "contenido": output.getvalue(),
                "filename": f"productos_{datetime.now().strftime('%Y%m%d')}.csv"
            }), 200

    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500


# ============================================
# 25. CATÁLOGO PÚBLICO (Sin auth) - v3.5
# ============================================

@catalogo_api_bp.route('/productos/publicos/<int:negocio_id>', methods=['GET', 'OPTIONS'])
@cross_origin(supports_credentials=True)
def catalogo_publico(negocio_id):
    """
    GET /api/productos/publicos/{negocio_id}
 
    Params:
    - categoria: filtrar por categoría
    - search: búsqueda por nombre
    - personalizable: 'true' solo personalizables
    - sort: newest | price_asc | price_desc | name_asc
    - limit: productos por página (default 50, max 2000)
    - offset: desde qué producto empezar (para paginación)
    - pagina: número de página (alternativa a offset, empieza en 1)
    """
    if request.method == 'OPTIONS':
        return jsonify({"success": True}), 200
 
    try:
        logger.info(f"🛍️ Catálogo público negocio: {negocio_id}")
 
        query = ProductoCatalogo.query.filter_by(
            negocio_id=negocio_id,
            activo=True,
            estado_publicacion=True
        )
 
        # Filtros
        categoria = request.args.get('categoria')
        if categoria:
            query = query.filter_by(categoria=categoria)
 
        search = request.args.get('search', '').strip()
        if search:
            query = query.filter(ProductoCatalogo.nombre.ilike(f"%{search}%"))
 
        personalizable = request.args.get('personalizable')
        if personalizable and personalizable.lower() in ['true', '1', 'yes']:
            if hasattr(ProductoCatalogo, 'personalizacion_activa'):
                query = query.filter(ProductoCatalogo.personalizacion_activa == True)
 
        # Ordenamiento
        sort = request.args.get('sort', 'newest')
        if sort == 'price_asc':
            query = query.order_by(ProductoCatalogo.precio.asc())
        elif sort == 'price_desc':
            query = query.order_by(ProductoCatalogo.precio.desc())
        elif sort == 'name_asc':
            query = query.order_by(ProductoCatalogo.nombre.asc())
        else:
            query = query.order_by(ProductoCatalogo.id_producto.desc())
 
        # Total ANTES de paginar (para el frontend saber cuántos hay)
        total = query.count()
 
        # Paginación — cap subido a 2000 para soportar catálogos medianos
        # con scroll infinito en frontend (la tienda pagina en chunks de 36).
        limit  = min(int(request.args.get('limit', 50)), 2000)
        pagina = int(request.args.get('pagina', 1))
        offset = int(request.args.get('offset', (pagina - 1) * limit))
 
        productos = query.offset(offset).limit(limit).all()
 
        datos_publicos = []
        for p in productos:
            try:
                campos = {
                    "id":            p.id_producto,
                    "id_producto":   p.id_producto,
                    "nombre":        p.nombre,
                    "descripcion":   p.descripcion,
                    "precio":        float(p.precio) if p.precio else 0,
                    "precio_original": float(p.precio_original) if getattr(p, 'precio_original', None) else None,
                    "categoria":     p.categoria,
                    "imagen_url":    p.imagen_url,
                    "imagenes":      parse_json_field(p.imagenes, []),
                    "videos":        parse_json_field(p.videos, []),
                    "sku":           p.referencia_sku,
                    "stock":         p.stock,
                    "en_stock":      (p.stock or 0) > 0,
                    "activo":        True,
                    "total_ventas":  getattr(p, 'total_ventas', 0) or 0,
                    "ventas_30_dias": getattr(p, 'ventas_30_dias', 0) or 0,
                    "visitas_7_dias": getattr(p, 'visitas_7_dias', 0) or 0,
                }
 
                # Badges
                if hasattr(p, 'badges_data') and p.badges_data:
                    try:
                        campos['badges'] = json.loads(p.badges_data) if isinstance(p.badges_data, str) else p.badges_data
                    except:
                        campos['badges'] = {}
                else:
                    campos['badges'] = {}
 
                campos['destacado']   = getattr(p, 'badge_destacado', False)
                campos['envio_gratis'] = getattr(p, 'badge_envio_gratis', False)
 
                # Descuento
                try:
                    precio_orig = getattr(p, 'precio_original', None)
                    precio_act  = float(p.precio) if p.precio else 0
                    if precio_orig and float(precio_orig) > precio_act > 0:
                        campos['tiene_descuento']       = True
                        campos['descuento_porcentaje']  = round(((float(precio_orig) - precio_act) / float(precio_orig)) * 100)
                    else:
                        campos['tiene_descuento']       = False
                        campos['descuento_porcentaje']  = 0
                except:
                    campos['tiene_descuento']      = False
                    campos['descuento_porcentaje'] = 0
 
                # Personalización
                campos['personalizable']        = getattr(p, 'personalizacion_activa', False) or False
                campos['personalizacion_activa'] = campos['personalizable']
 
                if campos['personalizable']:
                    if hasattr(p, 'get_personalizacion_config'):
                        config = p.get_personalizacion_config()
                    else:
                        config = parse_json_field(getattr(p, 'personalizacion_config', '{}'), {})
                        defaults = {
                            "permite_imagen": True, "permite_texto": True,
                            "imagen_requerida": False, "texto_requerido": False,
                            "max_size_mb": 5, "formatos": ["png", "jpg", "jpeg", "pdf"],
                            "max_caracteres": 100,
                            "instrucciones": "Sube tu diseño en alta resolución",
                            "placeholder_texto": "Escribe tu nombre o frase",
                            "costo_adicional": 0
                        }
                        for k, v in defaults.items():
                            if k not in config:
                                config[k] = v
 
                    costo_pers = config.get('costo_adicional', 0) or 0
                    campos['personalizacion_config']       = config
                    campos['costo_personalizacion']        = float(costo_pers)
                    campos['precio_con_personalizacion']   = campos['precio'] + float(costo_pers)
                else:
                    campos['personalizacion_config']     = None
                    campos['costo_personalizacion']      = 0
                    campos['precio_con_personalizacion'] = campos['precio']

                # ★ v2.5: Variantes
                variantes_data = parse_json_field(getattr(p, 'variantes', None), None)
                campos['variantes']       = variantes_data
                campos['tiene_variantes'] = bool(variantes_data and variantes_data.get('tipos'))

                datos_publicos.append(campos)
 
            except Exception as e:
                logger.warning(f"⚠️ Error procesando producto {getattr(p, 'id_producto', '?')}: {e}")
 
        # Categorías disponibles
        try:
            cats = db.session.query(ProductoCatalogo.categoria).filter_by(
                negocio_id=negocio_id, activo=True, estado_publicacion=True
            ).distinct().all()
            categorias_list = [c[0] for c in cats if c[0]]
        except:
            categorias_list = []
 
        paginas_totales = (total + limit - 1) // limit if limit > 0 else 1
 
        logger.info(f"✅ Catálogo público: {len(datos_publicos)}/{total} productos | página {pagina}/{paginas_totales}")
 
        return jsonify({
            "success":        True,
            "negocio_id":     negocio_id,
            "total":          total,
            "limit":          limit,
            "offset":         offset,
            "pagina":         pagina,
            "paginas_totales": paginas_totales,
            "hay_mas":        (offset + limit) < total,
            "categorias":     categorias_list,
            "productos":      datos_publicos
        }), 200
 
    except Exception as e:
        logger.error(f"❌ Error catálogo público: {traceback.format_exc()}")
        return jsonify({"success": False, "message": str(e)}), 500
# ============================================
# 26-27. BADGES ENDPOINTS
# ============================================

@catalogo_api_bp.route('/producto/<int:id_producto>/badges', methods=['PATCH', 'PUT', 'OPTIONS'])
@cross_origin(supports_credentials=True)
def actualizar_badges_producto(id_producto):
    """PATCH/PUT /api/producto/{id}/badges"""
    if request.method == 'OPTIONS':
        return jsonify({"success": True}), 200

    user_id = get_authorized_user_id()
    if not user_id:
        return jsonify({"success": False, "message": "No autorizado"}), 401

    try:
        producto = ProductoCatalogo.query.filter_by(id_producto=id_producto, usuario_id=int(user_id)).first()
        if not producto:
            return jsonify({"success": False, "message": "Producto no encontrado"}), 404

        data = request.get_json(silent=True)
        if not data:
            return jsonify({"success": False, "message": "No se enviaron datos"}), 400

        if hasattr(producto, 'set_badges_manuales'):
            producto.set_badges_manuales(data)
        else:
            badges_data = {
                'destacado': data.get('destacado', False) in [True, 'true', '1', 1],
                'envio_gratis': data.get('envio_gratis', False) in [True, 'true', '1', 1],
                'pre_orden': data.get('pre_orden', False) in [True, 'true', '1', 1],
                'edicion_limitada': data.get('edicion_limitada', False) in [True, 'true', '1', 1],
                'oferta_flash': data.get('oferta_flash', False) in [True, 'true', '1', 1],
                'combo': data.get('combo', False) in [True, 'true', '1', 1],
                'garantia_extendida': data.get('garantia_extendida', False) in [True, 'true', '1', 1],
                'eco_friendly': data.get('eco_friendly', False) in [True, 'true', '1', 1],
                'badge_personalizado': data.get('badge_personalizado') or None
            }
            producto.badges_data = json.dumps(badges_data)
            
            if hasattr(producto, 'badge_destacado'):
                producto.badge_destacado = badges_data['destacado']
            if hasattr(producto, 'badge_envio_gratis'):
                producto.badge_envio_gratis = badges_data['envio_gratis']
        
        if 'precio_original' in data:
            try:
                producto.precio_original = float(data['precio_original']) if data['precio_original'] else None
            except:
                producto.precio_original = None

        db.session.commit()

        return jsonify({
            "success": True,
            "message": "Badges actualizados",
            "producto": {
                "id": producto.id_producto,
                "nombre": producto.nombre,
                "badges_data": parse_json_field(producto.badges_data, {})
            }
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "message": str(e)}), 500


@catalogo_api_bp.route('/productos/badges/masivo', methods=['PATCH', 'PUT', 'OPTIONS'])
@cross_origin(supports_credentials=True)
def actualizar_badges_masivo():
    """PATCH/PUT /api/productos/badges/masivo"""
    if request.method == 'OPTIONS':
        return jsonify({"success": True}), 200

    user_id = get_authorized_user_id()
    if not user_id:
        return jsonify({"success": False, "message": "No autorizado"}), 401

    try:
        data = request.get_json(silent=True)
        if not data:
            return jsonify({"success": False, "message": "No se enviaron datos"}), 400

        producto_ids = data.get('productos', [])
        badges_update = data.get('badges', {})
        
        if not producto_ids:
            return jsonify({"success": False, "message": "No se especificaron productos"}), 400

        productos = ProductoCatalogo.query.filter(
            ProductoCatalogo.id_producto.in_(producto_ids),
            ProductoCatalogo.usuario_id == int(user_id)
        ).all()
        
        if not productos:
            return jsonify({"success": False, "message": "No se encontraron productos"}), 404

        actualizados = 0
        for producto in productos:
            try:
                badges_actuales = parse_json_field(producto.badges_data, {})
                
                for key, value in badges_update.items():
                    if key == 'badge_personalizado':
                        badges_actuales[key] = value or None
                    elif key in ['destacado', 'envio_gratis', 'pre_orden', 'edicion_limitada', 
                               'oferta_flash', 'combo', 'garantia_extendida', 'eco_friendly']:
                        badges_actuales[key] = value in [True, 'true', '1', 1]
                
                producto.badges_data = json.dumps(badges_actuales)
                
                if 'destacado' in badges_update and hasattr(producto, 'badge_destacado'):
                    producto.badge_destacado = badges_update['destacado'] in [True, 'true', '1', 1]
                if 'envio_gratis' in badges_update and hasattr(producto, 'badge_envio_gratis'):
                    producto.badge_envio_gratis = badges_update['envio_gratis'] in [True, 'true', '1', 1]
                
                actualizados += 1
            except Exception:
                pass

        db.session.commit()

        return jsonify({
            "success": True,
            "message": f"{actualizados} productos actualizados",
            "actualizados": actualizados
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "message": str(e)}), 500


# ============================================
# ★ 28. PERSONALIZACIÓN ENDPOINTS - v3.5 NUEVO
# ============================================

@catalogo_api_bp.route('/producto/<int:id_producto>/personalizacion', methods=['PATCH', 'PUT', 'OPTIONS'])
@cross_origin(supports_credentials=True)
def actualizar_personalizacion_producto(id_producto):
    """
    PATCH/PUT /api/producto/{id}/personalizacion
    
    ★ v3.5 NUEVO: Actualiza la configuración de personalización de un producto
    
    Body JSON:
    {
        "personalizacion_activa": true,
        "personalizacion_config": {
            "permite_imagen": true,
            "permite_texto": true,
            "imagen_requerida": false,
            "texto_requerido": false,
            "max_size_mb": 5,
            "formatos": ["png", "jpg", "jpeg", "pdf"],
            "max_caracteres": 100,
            "instrucciones": "Sube tu diseño en alta resolución",
            "placeholder_texto": "Escribe tu nombre o frase",
            "costo_adicional": 5000
        }
    }
    """
    if request.method == 'OPTIONS':
        return jsonify({"success": True}), 200

    user_id = get_authorized_user_id()
    if not user_id:
        return jsonify({"success": False, "message": "No autorizado"}), 401

    try:
        producto = ProductoCatalogo.query.filter_by(id_producto=id_producto, usuario_id=int(user_id)).first()
        if not producto:
            return jsonify({"success": False, "message": "Producto no encontrado"}), 404

        data = request.get_json(silent=True)
        if not data:
            return jsonify({"success": False, "message": "No se enviaron datos"}), 400

        logger.info(f"🎨 Actualizando personalización de producto {id_producto}")

        personalizacion_activa, personalizacion_config = procesar_personalizacion_desde_request(data)
        
        if hasattr(producto, 'personalizacion_activa'):
            producto.personalizacion_activa = personalizacion_activa
        
        if hasattr(producto, 'personalizacion_config'):
            producto.personalizacion_config = json.dumps(personalizacion_config)
        
        # Usar método del modelo si existe
        if hasattr(producto, 'set_personalizacion_config') and personalizacion_activa:
            producto.set_personalizacion_config(personalizacion_config)

        db.session.commit()

        logger.info(f"✅ Personalización actualizada: activa={personalizacion_activa}")

        return jsonify({
            "success": True,
            "message": f"Personalización {'activada' if personalizacion_activa else 'desactivada'}",
            "producto": {
                "id": producto.id_producto,
                "nombre": producto.nombre,
                "personalizable": personalizacion_activa,
                "personalizacion_config": personalizacion_config if personalizacion_activa else None
            }
        }), 200

    except Exception as e:
        db.session.rollback()
        logger.error(f"❌ Error actualizando personalización: {traceback.format_exc()}")
        return jsonify({"success": False, "message": str(e)}), 500


@catalogo_api_bp.route('/producto/<int:id_producto>/personalizacion/toggle', methods=['POST', 'OPTIONS'])
@cross_origin(supports_credentials=True)
def toggle_personalizacion_producto(id_producto):
    """
    POST /api/producto/{id}/personalizacion/toggle
    
    ★ v3.5 NUEVO: Activa/desactiva personalización de un producto
    """
    if request.method == 'OPTIONS':
        return jsonify({"success": True}), 200

    user_id = get_authorized_user_id()
    if not user_id:
        return jsonify({"success": False, "message": "No autorizado"}), 401

    try:
        producto = ProductoCatalogo.query.filter_by(id_producto=id_producto, usuario_id=int(user_id)).first()
        if not producto:
            return jsonify({"success": False, "message": "Producto no encontrado"}), 404

        # Toggle
        estado_actual = getattr(producto, 'personalizacion_activa', False) or False
        nuevo_estado = not estado_actual
        
        if hasattr(producto, 'personalizacion_activa'):
            producto.personalizacion_activa = nuevo_estado
        
        # Si se activa y no tiene config, establecer defaults
        if nuevo_estado and hasattr(producto, 'personalizacion_config'):
            config_actual = parse_json_field(getattr(producto, 'personalizacion_config', '{}'), {})
            if not config_actual:
                config_default = {
                    "permite_imagen": True,
                    "permite_texto": True,
                    "imagen_requerida": False,
                    "texto_requerido": False,
                    "max_size_mb": 5,
                    "formatos": ["png", "jpg", "jpeg", "pdf"],
                    "max_caracteres": 100,
                    "instrucciones": "Sube tu diseño en alta resolución (mínimo 300 DPI)",
                    "placeholder_texto": "Escribe tu nombre o frase",
                    "costo_adicional": 0
                }
                producto.personalizacion_config = json.dumps(config_default)

        db.session.commit()

        logger.info(f"🎨 Personalización toggle: Producto {id_producto} -> {nuevo_estado}")

        return jsonify({
            "success": True,
            "message": f"Personalización {'activada' if nuevo_estado else 'desactivada'}",
            "producto": {
                "id": producto.id_producto,
                "nombre": producto.nombre,
                "personalizable": nuevo_estado
            }
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "message": str(e)}), 500
# ============================================
# ★ 29. REGISTRAR VISTA DE PRODUCTO (PÚBLICO)
# ============================================

@catalogo_api_bp.route('/producto/<int:id_producto>/vista', methods=['POST', 'OPTIONS'])
@cross_origin(supports_credentials=True)
def registrar_vista_producto(id_producto):
    """
    POST /api/producto/{id}/vista
    
    ★ NUEVO: Registra una vista del producto (endpoint PÚBLICO, sin auth)
    Incrementa visitas_7_dias en ProductoCatalogo y registra en ProductoEstadisticas
    
    Se llama desde el frontend cuando alguien abre el detalle del producto.
    """
    if request.method == 'OPTIONS':
        return jsonify({"success": True}), 200

    try:
        producto = ProductoCatalogo.query.filter_by(id_producto=id_producto, activo=True).first()
        if not producto:
            return jsonify({"success": False, "message": "Producto no encontrado"}), 404

        # Incrementar contador en el producto
        producto.visitas_7_dias = (producto.visitas_7_dias or 0) + 1
        
        # Registrar en estadísticas diarias
        try:
            from datetime import date
            hoy = date.today()
            
            estadistica = ProductoEstadisticas.query.filter_by(
                producto_id=id_producto,
                fecha=hoy
            ).first()
            
            if estadistica:
                estadistica.visitas = (estadistica.visitas or 0) + 1
            else:
                estadistica = ProductoEstadisticas(
                    producto_id=id_producto,
                    negocio_id=producto.negocio_id,
                    fecha=hoy,
                    visitas=1,
                    agregados_carrito=0,
                    compras=0,
                    ingresos=0
                )
                db.session.add(estadistica)
        except Exception as e:
            logger.warning(f"⚠️ No se pudo registrar estadística diaria: {e}")
        
        db.session.commit()
        
        logger.debug(f"👁️ Vista registrada: Producto {id_producto} | Total: {producto.visitas_7_dias}")
        
        return jsonify({
            "success": True,
            "visitas": producto.visitas_7_dias
        }), 200

    except Exception as e:
        db.session.rollback()
        logger.error(f"❌ Error registrando vista: {str(e)}")
        return jsonify({"success": False, "message": str(e)}), 500


@catalogo_api_bp.route('/producto/<int:id_producto>/estadisticas', methods=['GET', 'OPTIONS'])
@cross_origin(supports_credentials=True)
def obtener_estadisticas_producto(id_producto):
    """
    GET /api/producto/{id}/estadisticas
    
    ★ NUEVO: Obtiene estadísticas de un producto (requiere auth)
    """
    if request.method == 'OPTIONS':
        return jsonify({"success": True}), 200

    user_id = get_authorized_user_id()
    if not user_id:
        return jsonify({"success": False, "message": "No autorizado"}), 401

    try:
        producto = ProductoCatalogo.query.filter_by(
            id_producto=id_producto, 
            usuario_id=int(user_id)
        ).first()
        
        if not producto:
            return jsonify({"success": False, "message": "Producto no encontrado"}), 404

        # Obtener estadísticas de los últimos 30 días
        from datetime import date, timedelta
        fecha_inicio = date.today() - timedelta(days=30)
        
        estadisticas = ProductoEstadisticas.query.filter(
            ProductoEstadisticas.producto_id == id_producto,
            ProductoEstadisticas.fecha >= fecha_inicio
        ).order_by(ProductoEstadisticas.fecha.desc()).all()
        
        # Calcular totales
        total_visitas = sum(e.visitas or 0 for e in estadisticas)
        total_carrito = sum(e.agregados_carrito or 0 for e in estadisticas)
        total_compras = sum(e.compras or 0 for e in estadisticas)
        total_ingresos = sum(float(e.ingresos or 0) for e in estadisticas)
        
        return jsonify({
            "success": True,
            "producto_id": id_producto,
            "producto_nombre": producto.nombre,
            "resumen": {
                "visitas_7_dias": producto.visitas_7_dias or 0,
                "visitas_30_dias": total_visitas,
                "agregados_carrito_30_dias": total_carrito,
                "compras_30_dias": total_compras,
                "ingresos_30_dias": round(total_ingresos, 2),
                "tasa_conversion": round((total_compras / total_visitas * 100), 1) if total_visitas > 0 else 0
            },
            "diario": [e.to_dict() for e in estadisticas]
        }), 200

    except Exception as e:
        logger.error(f"❌ Error obteniendo estadísticas: {str(e)}")
        return jsonify({"success": False, "message": str(e)}), 500

@catalogo_api_bp.route('/personalizacion/upload', methods=['POST', 'OPTIONS'])
@cross_origin(supports_credentials=True)
def upload_personalizacion():
    """
    POST /api/personalizacion/upload
    
    ★ v3.5 NUEVO: Sube una imagen de personalización del CLIENTE a Cloudinary
    
    Este endpoint es para que los CLIENTES de la tienda suban sus diseños.
    NO requiere autenticación (es público).
    
    FormData:
    - archivo: El archivo a subir (imagen/PDF)
    - negocio_id: ID del negocio
    - producto_id: ID del producto (opcional)
    - cliente_nombre: Nombre del cliente (opcional)
    """
    if request.method == 'OPTIONS':
        return jsonify({"success": True}), 200

    try:
        # Obtener archivo
        archivo = request.files.get('archivo') or request.files.get('file') or request.files.get('imagen')
        
        if not archivo or not archivo.filename:
            return jsonify({"success": False, "message": "No se recibió archivo"}), 400
        
        # Validar extensión
        extension = archivo.filename.rsplit('.', 1)[-1].lower() if '.' in archivo.filename else ''
        formatos_permitidos = ['png', 'jpg', 'jpeg', 'pdf', 'svg']
        
        if extension not in formatos_permitidos:
            return jsonify({
                "success": False, 
                "message": f"Formato no permitido. Usa: {', '.join(formatos_permitidos)}"
            }), 400
        
        # Validar tamaño (máximo 20MB)
        archivo.seek(0, 2)  # Ir al final
        size_mb = archivo.tell() / (1024 * 1024)
        archivo.seek(0)  # Volver al inicio
        
        if size_mb > 20:
            return jsonify({
                "success": False, 
                "message": f"Archivo muy grande ({size_mb:.1f}MB). Máximo: 20MB"
            }), 400
        
        # Datos adicionales
        negocio_id = request.form.get('negocio_id', 'unknown')
        producto_id = request.form.get('producto_id', 'general')
        cliente_nombre = request.form.get('cliente_nombre', 'cliente')
        
        # Limpiar nombre para public_id
        cliente_limpio = re.sub(r'[^a-zA-Z0-9]', '', cliente_nombre[:20])
        timestamp = int(time.time())
        
        public_id = f"pers_{negocio_id}_{producto_id}_{cliente_limpio}_{timestamp}"
        
        # Subir a Cloudinary
        try:
            upload_result = cloudinary.uploader.upload(
                archivo,
                folder=f"personalizaciones/{negocio_id}",
                public_id=public_id,
                overwrite=True,
                resource_type="auto",
                tags=[f"negocio_{negocio_id}", f"producto_{producto_id}", "personalizacion"]
            )
            
            url = upload_result.get('secure_url')
            public_id_final = upload_result.get('public_id')
            
            logger.info(f"✅ Personalización subida: {url}")
            
            return jsonify({
                "success": True,
                "message": "Archivo subido exitosamente",
                "url": url,
                "public_id": public_id_final,
                "formato": extension,
                "size_mb": round(size_mb, 2),
                "negocio_id": negocio_id,
                "producto_id": producto_id
            }), 201
            
        except Exception as e:
            logger.error(f"❌ Error subiendo a Cloudinary: {e}")
            return jsonify({
                "success": False, 
                "message": f"Error subiendo archivo: {str(e)}"
            }), 500

    except Exception as e:
        logger.error(f"❌ Error en upload personalización: {traceback.format_exc()}")
        return jsonify({"success": False, "message": str(e)}), 500


@catalogo_api_bp.route('/productos/personalizables/<int:negocio_id>', methods=['GET', 'OPTIONS'])
@cross_origin(supports_credentials=True)
def obtener_productos_personalizables(negocio_id):
    """
    GET /api/productos/personalizables/{negocio_id}
    
    ★ v3.5 NUEVO: Lista todos los productos personalizables de un negocio
    Endpoint público para la tienda
    """
    if request.method == 'OPTIONS':
        return jsonify({"success": True}), 200

    try:
        query = ProductoCatalogo.query.filter_by(
            negocio_id=negocio_id, 
            activo=True, 
            estado_publicacion=True
        )
        
        # Filtrar solo personalizables
        if hasattr(ProductoCatalogo, 'personalizacion_activa'):
            query = query.filter(ProductoCatalogo.personalizacion_activa == True)
        else:
            return jsonify({
                "success": True,
                "total": 0,
                "productos": [],
                "message": "Personalización no habilitada en este sistema"
            }), 200
        
        productos = query.order_by(ProductoCatalogo.id_producto.desc()).all()
        
        datos = []
        for p in productos:
            try:
                config = None
                if hasattr(p, 'get_personalizacion_config'):
                    config = p.get_personalizacion_config()
                else:
                    config = parse_json_field(getattr(p, 'personalizacion_config', '{}'), {})
                
                costo_pers = config.get('costo_adicional', 0) if config else 0
                
                datos.append({
                    "id": p.id_producto,
                    "nombre": p.nombre,
                    "descripcion": p.descripcion,
                    "precio": float(p.precio or 0),
                    "precio_con_personalizacion": float(p.precio or 0) + float(costo_pers),
                    "costo_personalizacion": float(costo_pers),
                    "categoria": p.categoria,
                    "imagen_url": p.imagen_url,
                    "imagenes": parse_json_field(p.imagenes, []),
                    "en_stock": (p.stock or 0) > 0,
                    "personalizacion_config": config
                })
            except Exception as e:
                logger.warning(f"⚠️ Error procesando producto {getattr(p, 'id_producto', '?')}: {e}")

        return jsonify({
            "success": True,
            "negocio_id": negocio_id,
            "total": len(datos),
            "productos": datos
        }), 200

    except Exception as e:
        logger.error(f"❌ Error obteniendo personalizables: {traceback.format_exc()}")
        return jsonify({"success": False, "message": str(e)}), 500


# ============================================
# FIN DEL ARCHIVO - catalogo_api.py v3.5
# Soporte completo para:
# - badges_data JSON (v2.3)
# - Personalización de productos (v2.4)
# ============================================