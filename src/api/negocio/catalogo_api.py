# ============================================
# catalogo_api.py - VERSIÓN CORREGIDA v3.1
# Conectado con Inventario PRO + BizContext
# CORREGIDO: Múltiples imágenes + YouTube videos
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

from src.models.database import db
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
    """Obtiene el ID del usuario autenticado (Header prioritario)"""
    header_id = request.headers.get('X-User-ID')
    session_id = None
    
    if current_user.is_authenticated:
        session_id = str(getattr(current_user, 'id_usuario', ''))

    logger.debug(f"🔍 [AUTH] Header: {header_id} | Sesión: {session_id}")

    if header_id and header_id != session_id:
        logger.warning(f"⚠️ Header {header_id} != Sesión {session_id}. Usando Header.")
        return header_id
    
    return header_id or session_id


def get_biz_context():
    """
    Obtiene el contexto de negocio desde headers o query params.
    Compatible con BizContext.js del frontend.
    """
    # Intentar obtener de headers primero
    negocio_id = request.headers.get('X-Business-ID') or request.headers.get('X-Negocio-ID')
    
    # Si no está en headers, buscar en query params
    if not negocio_id:
        negocio_id = request.args.get('negocio_id')
    
    # Si no está en query, buscar en body JSON
    if not negocio_id and request.is_json:
        negocio_id = request.json.get('negocio_id')
    
    # Si es form data
    if not negocio_id and request.form:
        negocio_id = request.form.get('negocio_id')
    
    sucursal_id = (
        request.headers.get('X-Sucursal-ID') or 
        request.args.get('sucursal_id') or
        (request.json.get('sucursal_id') if request.is_json else None) or
        (request.form.get('sucursal_id') if request.form else None)
    )
    
    return {
        'negocio_id': int(negocio_id) if negocio_id else None,
        'sucursal_id': int(sucursal_id) if sucursal_id else None
    }


def parse_json_field(value, default=None):
    """
    Helper para parsear campos que pueden venir como JSON string o ya parseados.
    Evita el problema de doble encoding.
    """
    if default is None:
        default = []
    
    if value is None:
        return default
    
    if isinstance(value, list):
        return value
    
    if isinstance(value, str):
        # Intentar parsear como JSON
        try:
            parsed = json.loads(value)
            # Si el resultado es una lista, retornarla
            if isinstance(parsed, list):
                return parsed
            # Si es un string (doble encoding), intentar parsear de nuevo
            if isinstance(parsed, str):
                try:
                    return json.loads(parsed)
                except:
                    return default
            return default
        except json.JSONDecodeError:
            # No es JSON válido, retornar default
            return default
    
    return default


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


# ============================================
# HEALTH CHECK
# ============================================

@catalogo_api_bp.route('/health', methods=['GET'])
def health_check():
    return jsonify({
        "status": "online", 
        "module": "catalogo",
        "version": "3.1",
        "cloudinary": "configured"
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
    """
    if request.method == 'OPTIONS':
        return jsonify({"success": True}), 200

    user_id = get_authorized_user_id()
    if not user_id:
        return jsonify({"success": False, "message": "No autorizado"}), 401

    try:
        ctx = get_biz_context()
        
        logger.info(f"📦 Obteniendo productos - User: {user_id}, Negocio: {ctx['negocio_id']}")
        
        # Query base
        query = ProductoCatalogo.query.filter_by(usuario_id=int(user_id))
        
        # Filtro por negocio (BizContext)
        if ctx['negocio_id']:
            query = query.filter_by(negocio_id=ctx['negocio_id'])
            
        # Filtro por sucursal
        if ctx['sucursal_id']:
            query = query.filter_by(sucursal_id=ctx['sucursal_id'])
        
        # Filtro por categoría
        categoria = request.args.get('categoria')
        if categoria:
            query = query.filter_by(categoria=categoria)
        
        # Filtro por stock
        stock_filter = request.args.get('stock_filter')
        if stock_filter == 'in_stock':
            query = query.filter(ProductoCatalogo.stock > 10)
        elif stock_filter == 'low_stock':
            query = query.filter(ProductoCatalogo.stock > 0, ProductoCatalogo.stock <= 10)
        elif stock_filter == 'out_of_stock':
            query = query.filter(ProductoCatalogo.stock == 0)
        
        # Búsqueda
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
        
        # Ordenamiento
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
        else:  # newest
            query = query.order_by(ProductoCatalogo.id_producto.desc())
        
        productos = query.all()
        
        # Transformar a formato compatible con JS
        data_final = []
        for p in productos:
            d = p.to_dict()
            # Asegurar aliases para JS
            d['id'] = p.id_producto
            d['sku'] = p.referencia_sku
            d['barcode'] = p.codigo_barras or ''
            d['codigo_barras'] = p.codigo_barras or ''
            # Parsear campos JSON
            d['imagenes'] = parse_json_field(p.imagenes, [])
            d['videos'] = parse_json_field(p.videos, [])
            d['youtube_links'] = d['videos']  # Alias para compatibilidad JS
            data_final.append(d)

        logger.info(f"✅ Catálogo: {len(data_final)} productos para usuario {user_id}")
        
        return jsonify({
            "success": True,
            "data": data_final,
            "total": len(data_final),
            "context": ctx
        }), 200
        
    except Exception as e:
        logger.error(f"❌ Error en GET mis-productos: {traceback.format_exc()}")
        return jsonify({"success": False, "message": str(e)}), 500


# ============================================
# 2. GUARDAR PRODUCTO (Crear nuevo) - CORREGIDO
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
    - youtube_links o videos (JSON string) - videos de YouTube
    - imagenes (JSON string) - URLs de imágenes existentes
    """
    if request.method == 'OPTIONS':
        return jsonify({"success": True}), 200

    user_id = get_authorized_user_id()
    if not user_id:
        return jsonify({"success": False, "message": "No autorizado"}), 401

    try:
        # Detectar tipo de contenido
        is_form = 'multipart/form-data' in (request.content_type or '')
        data = request.form.to_dict() if is_form else (request.get_json(silent=True) or {})
        ctx = get_biz_context()
        
        # Validar nombre
        nombre = data.get('nombre', '').strip()
        if not nombre:
            return jsonify({"success": False, "message": "El nombre es requerido"}), 400
        
        logger.info(f"📦 ═══════════════════════════════════════")
        logger.info(f"📦 CREANDO PRODUCTO: {nombre}")
        logger.info(f"📦 User ID: {user_id}")
        logger.info(f"📦 Negocio ID: {ctx['negocio_id']}")
        logger.info(f"📋 Campos recibidos: {list(data.keys())}")
        logger.info(f"📁 Archivos recibidos: {list(request.files.keys())}")
        
        # ========================================
        # 1. PROCESAR IMAGEN PRINCIPAL
        # ========================================
        imagen_url = data.get('imagen_url', '')
        galeria_urls = []
        
        file = request.files.get('imagen') or request.files.get('imagen_file')
        
        if file and file.filename:
            logger.info(f"📷 Subiendo imagen principal: {file.filename}")
            nombre_limpio = re.sub(r'[^a-zA-Z0-9]', '', nombre[:15])
            p_id = f"user_{user_id}_{nombre_limpio}_{int(time.time())}"
            
            try:
                upload_result = cloudinary.uploader.upload(
                    file,
                    folder="productos_bizflow",
                    public_id=p_id,
                    overwrite=True,
                    resource_type="auto"
                )
                imagen_url = upload_result.get('secure_url')
                galeria_urls.append(imagen_url)
                logger.info(f"✅ Imagen principal subida: {imagen_url}")
            except Exception as e:
                logger.error(f"❌ Error subiendo imagen principal: {e}")
        
        # ========================================
        # 2. PROCESAR GALERÍA DE IMÁGENES
        # ========================================
        for i in range(1, 10):  # imagen_1 hasta imagen_9
            file_key = f'imagen_{i}'
            if file_key in request.files:
                img_file = request.files[file_key]
                if img_file and img_file.filename:
                    logger.info(f"📷 Subiendo imagen galería [{i}]: {img_file.filename}")
                    nombre_limpio = re.sub(r'[^a-zA-Z0-9]', '', nombre[:15])
                    img_id = f"user_{user_id}_{nombre_limpio}_gal{i}_{int(time.time())}"
                    
                    try:
                        upload_result = cloudinary.uploader.upload(
                            img_file,
                            folder="productos_bizflow/galeria",
                            public_id=img_id,
                            overwrite=True,
                            resource_type="auto"
                        )
                        url = upload_result.get('secure_url')
                        galeria_urls.append(url)
                        logger.info(f"✅ Imagen galería [{i}] subida: {url}")
                    except Exception as e:
                        logger.error(f"❌ Error subiendo imagen galería [{i}]: {e}")
        
        # Agregar imágenes existentes (URLs que vienen del frontend)
        imagenes_existentes = parse_json_field(data.get('imagenes'), [])
        if imagenes_existentes:
            logger.info(f"📷 Imágenes existentes recibidas: {len(imagenes_existentes)}")
            # No duplicar URLs que ya están en galeria_urls
            for url in imagenes_existentes:
                if url and url not in galeria_urls:
                    galeria_urls.append(url)
        
        # Limitar a 10 imágenes máximo
        galeria_urls = galeria_urls[:10]
        logger.info(f"📷 Total imágenes en galería: {len(galeria_urls)}")
        
        # ========================================
        # 3. PROCESAR YOUTUBE/VIDEOS
        # ========================================
        # El frontend puede enviar como 'youtube_links' o 'videos'
        videos_raw = data.get('youtube_links') or data.get('videos') or '[]'
        videos = parse_json_field(videos_raw, [])
        
        # Filtrar solo URLs válidas
        videos = [url for url in videos if url and isinstance(url, str) and ('youtube' in url or 'youtu.be' in url)]
        
        logger.info(f"🎥 Videos de YouTube: {len(videos)}")
        if videos:
            logger.info(f"🎥 URLs: {videos}")
        
        # ========================================
        # 4. OBTENER IDs DE CONTEXTO
        # ========================================
        negocio_id = ctx['negocio_id'] or int(data.get('negocio_id') or 1)
        sucursal_id = ctx['sucursal_id'] or int(data.get('sucursal_id') or 1)
        
        # ========================================
        # 5. CREAR PRODUCTO
        # ========================================
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
            estado_publicacion=True
        )
        
        db.session.add(nuevo_prod)
        db.session.commit()

        # ========================================
        # 6. PREPARAR RESPUESTA
        # ========================================
        producto_dict = nuevo_prod.to_dict()
        producto_dict['id'] = nuevo_prod.id_producto
        producto_dict['imagenes'] = galeria_urls
        producto_dict['videos'] = videos
        producto_dict['youtube_links'] = videos  # Alias para JS
        
        logger.info(f"✅ ═══════════════════════════════════════")
        logger.info(f"✅ PRODUCTO CREADO: {nombre}")
        logger.info(f"✅ ID: {nuevo_prod.id_producto}")
        logger.info(f"✅ Imágenes: {len(galeria_urls)}")
        logger.info(f"✅ Videos: {len(videos)}")
        logger.info(f"✅ ═══════════════════════════════════════")

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
        logger.error(f"❌ Error en Guardar Producto: {traceback.format_exc()}")
        return jsonify({"success": False, "message": str(e)}), 500


# ============================================
# 3. ACTUALIZAR PRODUCTO (Edición completa) - CORREGIDO
# ============================================

@catalogo_api_bp.route('/producto/actualizar/<int:id_producto>', methods=['PUT', 'PATCH', 'OPTIONS'])
@cross_origin(supports_credentials=True)
def actualizar_producto(id_producto):
    """
    PUT/PATCH /api/producto/actualizar/{id}
    
    Actualiza cualquier campo del producto.
    Solo actualiza los campos que vengan en el request.
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

        is_form = 'multipart/form-data' in (request.content_type or '')
        data = request.form.to_dict() if is_form else (request.get_json(silent=True) or {})

        logger.info(f"📝 ═══════════════════════════════════════")
        logger.info(f"📝 ACTUALIZANDO PRODUCTO ID: {id_producto}")
        logger.info(f"📋 Campos recibidos: {list(data.keys())}")
        logger.info(f"📁 Archivos recibidos: {list(request.files.keys())}")

        # ========================================
        # ACTUALIZAR CAMPOS BÁSICOS
        # ========================================
        if 'nombre' in data:
            producto.nombre = data['nombre'].strip()
        
        if 'descripcion' in data:
            producto.descripcion = data['descripcion']
        
        if 'categoria' in data:
            producto.categoria = data['categoria']
        
        if 'precio' in data:
            producto.precio = float(data['precio'])
        
        if 'costo' in data:
            producto.costo = float(data['costo'])
        
        if 'stock' in data:
            producto.stock = int(data['stock'])
        
        if 'sku' in data or 'referencia_sku' in data:
            producto.referencia_sku = data.get('sku') or data.get('referencia_sku')
        
        if 'barcode' in data or 'codigo_barras' in data:
            producto.codigo_barras = data.get('barcode') or data.get('codigo_barras')
        
        if 'activo' in data:
            producto.activo = data['activo'] in [True, 'true', '1', 1]
        
        if 'estado_publicacion' in data:
            producto.estado_publicacion = data['estado_publicacion'] in [True, 'true', '1', 1]
        
        if 'negocio_id' in data:
            producto.negocio_id = int(data['negocio_id'])
        
        if 'sucursal_id' in data:
            producto.sucursal_id = int(data['sucursal_id'])
        
        if 'stock_minimo' in data:
            producto.stock_minimo = int(data['stock_minimo'])
        
        if 'stock_critico' in data:
            producto.stock_critico = int(data['stock_critico'])
        
        if 'stock_bajo' in data:
            producto.stock_bajo = int(data['stock_bajo'])

        # ========================================
        # PROCESAR VIDEOS/YOUTUBE
        # ========================================
        if 'youtube_links' in data or 'videos' in data:
            videos_raw = data.get('youtube_links') or data.get('videos') or '[]'
            videos = parse_json_field(videos_raw, [])
            # Filtrar URLs válidas de YouTube
            videos = [url for url in videos if url and isinstance(url, str)]
            producto.videos = json.dumps(videos)
            logger.info(f"🎥 Videos actualizados: {len(videos)}")

        # ========================================
        # PROCESAR IMÁGENES EXISTENTES
        # ========================================
        galeria_actual = parse_json_field(producto.imagenes, [])
        
        if 'imagenes' in data:
            imagenes_nuevas = parse_json_field(data['imagenes'], [])
            # Combinar con las actuales si son diferentes
            for url in imagenes_nuevas:
                if url and url not in galeria_actual:
                    galeria_actual.append(url)
        
        # ========================================
        # SUBIR NUEVA IMAGEN PRINCIPAL
        # ========================================
        file = request.files.get('imagen') or request.files.get('imagen_file')
        if file and file.filename:
            logger.info(f"📷 Subiendo nueva imagen principal: {file.filename}")
            nombre_limpio = re.sub(r'[^a-zA-Z0-9]', '', producto.nombre[:15])
            p_id = f"user_{user_id}_{nombre_limpio}_{int(time.time())}"
            
            try:
                upload_result = cloudinary.uploader.upload(
                    file,
                    folder="productos_bizflow",
                    public_id=p_id,
                    overwrite=True,
                    resource_type="auto"
                )
                nueva_url = upload_result.get('secure_url')
                producto.imagen_url = nueva_url
                
                # Agregar a galería si no existe
                if nueva_url not in galeria_actual:
                    galeria_actual.insert(0, nueva_url)
                
                logger.info(f"✅ Imagen principal actualizada: {nueva_url}")
            except Exception as e:
                logger.error(f"❌ Error subiendo imagen principal: {e}")
        
        # ========================================
        # SUBIR IMÁGENES DE GALERÍA ADICIONALES
        # ========================================
        for i in range(1, 10):
            file_key = f'imagen_{i}'
            if file_key in request.files:
                img_file = request.files[file_key]
                if img_file and img_file.filename:
                    logger.info(f"📷 Subiendo imagen galería [{i}]: {img_file.filename}")
                    nombre_limpio = re.sub(r'[^a-zA-Z0-9]', '', producto.nombre[:15])
                    img_id = f"user_{user_id}_{nombre_limpio}_gal{i}_{int(time.time())}"
                    
                    try:
                        upload_result = cloudinary.uploader.upload(
                            img_file,
                            folder="productos_bizflow/galeria",
                            public_id=img_id,
                            overwrite=True,
                            resource_type="auto"
                        )
                        url = upload_result.get('secure_url')
                        galeria_actual.append(url)
                        logger.info(f"✅ Imagen galería [{i}] subida: {url}")
                    except Exception as e:
                        logger.error(f"❌ Error subiendo imagen galería [{i}]: {e}")
        
        # Limitar a 10 imágenes y guardar
        galeria_actual = galeria_actual[:10]
        producto.imagenes = json.dumps(galeria_actual)
        
        # Actualizar imagen_url si está vacía pero hay galería
        if not producto.imagen_url and galeria_actual:
            producto.imagen_url = galeria_actual[0]

        db.session.commit()

        # Preparar respuesta
        producto_dict = producto.to_dict()
        producto_dict['id'] = producto.id_producto
        producto_dict['imagenes'] = galeria_actual
        producto_dict['videos'] = parse_json_field(producto.videos, [])
        producto_dict['youtube_links'] = producto_dict['videos']

        logger.info(f"✅ Producto {id_producto} actualizado correctamente")
        logger.info(f"✅ Imágenes: {len(galeria_actual)}, Videos: {len(producto_dict['videos'])}")

        return jsonify({
            "success": True,
            "message": "Producto actualizado",
            "producto": producto_dict
        }), 200

    except ValueError as e:
        db.session.rollback()
        return jsonify({"success": False, "message": f"Datos inválidos: {str(e)}"}), 400
    
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
        producto = ProductoCatalogo.query.filter_by(
            id_producto=id_producto, 
            usuario_id=int(user_id)
        ).first()
        
        if not producto:
            return jsonify({"success": False, "message": "Producto no encontrado"}), 404
        
        nombre = producto.nombre
        db.session.delete(producto)
        db.session.commit()
        
        logger.info(f"🗑️ Producto eliminado: {nombre} (ID: {id_producto})")
        
        return jsonify({
            "success": True,
            "message": f"Producto '{nombre}' eliminado"
        }), 200
        
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
        producto = ProductoCatalogo.query.filter_by(
            id_producto=id_producto,
            usuario_id=int(user_id)
        ).first()
        
        if not producto:
            return jsonify({"success": False, "message": "Producto no encontrado"}), 404

        # Construir respuesta completa
        data = producto.to_dict()
        data['id'] = producto.id_producto
        data['sku'] = producto.referencia_sku
        data['barcode'] = producto.codigo_barras
        data['imagenes'] = parse_json_field(producto.imagenes, [])
        data['videos'] = parse_json_field(producto.videos, [])
        data['youtube_links'] = data['videos']
        data['etiquetas'] = parse_json_field(producto.etiquetas, [])

        # Obtener movimientos recientes
        try:
            movimientos = MovimientoStock.query.filter_by(
                producto_id=id_producto
            ).order_by(MovimientoStock.fecha.desc()).limit(5).all()
            data['movimientos_recientes'] = [m.to_dict() for m in movimientos]
        except:
            data['movimientos_recientes'] = []

        return jsonify({
            "success": True,
            "producto": data
        }), 200

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
        data = request.get_json()
        if not data:
            return jsonify({"success": False, "message": "No se enviaron datos"}), 400

        producto = ProductoCatalogo.query.filter_by(
            id_producto=id_producto,
            usuario_id=int(user_id)
        ).first()
        
        if not producto:
            return jsonify({"success": False, "message": "Producto no encontrado"}), 404

        old_stock = producto.stock
        old_precio = producto.precio

        if 'stock' in data:
            producto.stock = int(data['stock'])
        
        if 'precio' in data:
            producto.precio = float(data['precio'])
        
        if 'costo' in data:
            producto.costo = float(data['costo'])

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
# 7. DUPLICAR PRODUCTO
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
        original = ProductoCatalogo.query.filter_by(
            id_producto=id_producto,
            usuario_id=int(user_id)
        ).first()
        
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
            activo=False
        )
        
        db.session.add(duplicado)
        db.session.commit()

        producto_dict = duplicado.to_dict()
        producto_dict['id'] = duplicado.id_producto

        logger.info(f"📋 Producto duplicado: {original.nombre} → {duplicado.nombre}")

        return jsonify({
            "success": True,
            "message": "Producto duplicado",
            "producto": producto_dict
        }), 201

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
        producto = ProductoCatalogo.query.filter_by(
            id_producto=id_producto,
            usuario_id=int(user_id)
        ).first()
        
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
            "producto": {
                "id": producto.id_producto,
                "nombre": producto.nombre,
                "activo": producto.activo
            }
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
    """
    POST /api/producto/{id}/stock
    
    Body: { tipo: 'entrada'|'salida'|'ajuste', cantidad: N, nota: '' }
    """
    if request.method == 'OPTIONS':
        return jsonify({"success": True}), 200

    user_id = get_authorized_user_id()
    if not user_id:
        return jsonify({"success": False, "message": "No autorizado"}), 401

    try:
        data = request.get_json()
        if not data:
            return jsonify({"success": False, "message": "No se enviaron datos"}), 400

        tipo = data.get('tipo', 'entrada').lower()
        cantidad = int(data.get('cantidad', 0))
        nota = data.get('nota', '').strip() or data.get('motivo', '').strip()

        if cantidad <= 0 and tipo != 'ajuste':
            return jsonify({"success": False, "message": "Cantidad debe ser mayor a 0"}), 400

        if tipo not in ['entrada', 'salida', 'ajuste']:
            return jsonify({"success": False, "message": "Tipo inválido"}), 400

        producto = ProductoCatalogo.query.filter_by(
            id_producto=id_producto,
            usuario_id=int(user_id)
        ).first()
        
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
        else:  # ajuste
            nuevo_stock = cantidad
            cantidad_movimiento = cantidad - stock_anterior

        producto.stock = nuevo_stock
        
        # Registrar movimiento
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
        producto = ProductoCatalogo.query.filter_by(
            id_producto=id_producto,
            usuario_id=int(user_id)
        ).first()
        
        if not producto:
            return jsonify({"success": False, "message": "Producto no encontrado"}), 404

        try:
            movimientos = MovimientoStock.query.filter_by(
                producto_id=id_producto
            ).order_by(MovimientoStock.fecha.desc()).limit(100).all()
            
            total_entradas = sum(m.cantidad for m in movimientos if m.tipo == 'entrada')
            total_salidas = abs(sum(m.cantidad for m in movimientos if m.tipo == 'salida'))
            
            return jsonify({
                "success": True,
                "producto": {
                    "id": producto.id_producto,
                    "nombre": producto.nombre,
                    "stock_actual": producto.stock
                },
                "resumen": {
                    "total_entradas": total_entradas,
                    "total_salidas": total_salidas,
                    "total_movimientos": len(movimientos)
                },
                "movimientos": [m.to_dict() for m in movimientos]
            }), 200
            
        except Exception as e:
            logger.warning(f"⚠️ Error obteniendo movimientos: {e}")
            return jsonify({
                "success": True,
                "producto": {
                    "id": producto.id_producto,
                    "nombre": producto.nombre,
                    "stock_actual": producto.stock
                },
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
        
        query = ProductoCatalogo.query.filter_by(
            usuario_id=int(user_id),
            activo=True
        )
        
        if ctx['negocio_id']:
            query = query.filter_by(negocio_id=ctx['negocio_id'])
        
        # Productos con stock bajo o crítico
        query = query.filter(ProductoCatalogo.stock <= ProductoCatalogo.stock_bajo)
        productos = query.order_by(ProductoCatalogo.stock.asc()).all()
        
        alertas = []
        for p in productos:
            nivel = p.nivel_stock()
            alertas.append({
                "id": p.id_producto,
                "producto": {
                    "id": p.id_producto,
                    "nombre": p.nombre,
                    "sku": p.referencia_sku,
                    "stock": p.stock,
                    "stock_critico": p.stock_critico,
                    "stock_bajo": p.stock_bajo,
                    "imagen_url": p.imagen_url
                },
                "tipo": 'critical' if nivel == 'critico' else 'warning',
                "message": f"{'Sin stock' if p.stock == 0 else 'Stock crítico' if nivel == 'critico' else 'Stock bajo'}: {p.stock} unidades",
                "fecha": datetime.utcnow().isoformat()
            })

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
# 12. ESTADÍSTICAS DE INVENTARIO
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
        
        if ctx['negocio_id']:
            query = query.filter_by(negocio_id=ctx['negocio_id'])
        
        productos = query.all()
        
        total = len(productos)
        en_stock = len([p for p in productos if p.stock > p.stock_bajo])
        stock_bajo = len([p for p in productos if 0 < p.stock <= p.stock_bajo])
        sin_stock = len([p for p in productos if p.stock == 0])
        
        valor_total = sum((p.precio * p.stock) for p in productos)
        costo_total = sum((p.costo * p.stock) for p in productos)
        
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
# 13. LISTAR CATEGORÍAS
# ============================================

@catalogo_api_bp.route('/categorias', methods=['GET', 'OPTIONS'])
@cross_origin(supports_credentials=True)
def listar_categorias():
    """GET /api/categorias"""
    if request.method == 'OPTIONS':
        return jsonify({"success": True}), 200

    user_id = get_authorized_user_id()
    if not user_id:
        return jsonify({"success": False, "message": "No autorizado"}), 401

    try:
        ctx = get_biz_context()
        
        # Categorías personalizadas
        categorias_custom = []
        try:
            query = CategoriaProducto.query.filter_by(usuario_id=int(user_id))
            if ctx['negocio_id']:
                query = query.filter_by(negocio_id=ctx['negocio_id'])
            categorias_custom = query.all()
        except:
            pass
        
        # Categorías de productos existentes
        query_productos = ProductoCatalogo.query.filter_by(usuario_id=int(user_id))
        if ctx['negocio_id']:
            query_productos = query_productos.filter_by(negocio_id=ctx['negocio_id'])
        
        productos = query_productos.all()
        
        conteo = {}
        for p in productos:
            cat = p.categoria or 'Sin categoría'
            conteo[cat] = conteo.get(cat, 0) + 1
        
        categorias_dict = {}
        
        for cat in categorias_custom:
            categorias_dict[cat.nombre] = {
                "id": cat.id_categoria,
                "name": cat.nombre,
                "nombre": cat.nombre,
                "icon": cat.icono,
                "icono": cat.icono,
                "color": cat.color,
                "count": conteo.get(cat.nombre, 0),
                "productos": conteo.get(cat.nombre, 0),
                "custom": True
            }
        
        iconos_default = {
            'Electrónica': '📱', 'Ropa': '👕', 'Hogar': '🏠', 
            'Accesorios': '🎁', 'Alimentos': '🍔', 'Bebidas': '🥤',
            'General': '📦', 'Sin categoría': '📁'
        }
        
        colores_default = ['#6366f1', '#ec4899', '#10b981', '#f59e0b', '#8b5cf6', '#ef4444', '#06b6d4']
        
        idx = 0
        for cat_nombre, cantidad in conteo.items():
            if cat_nombre not in categorias_dict:
                categorias_dict[cat_nombre] = {
                    "id": None,
                    "name": cat_nombre,
                    "nombre": cat_nombre,
                    "icon": iconos_default.get(cat_nombre, '📦'),
                    "icono": iconos_default.get(cat_nombre, '📦'),
                    "color": colores_default[idx % len(colores_default)],
                    "count": cantidad,
                    "productos": cantidad,
                    "custom": False
                }
                idx += 1

        categorias_list = list(categorias_dict.values())
        categorias_list.sort(key=lambda x: x['count'], reverse=True)

        return jsonify({
            "success": True,
            "total": len(categorias_list),
            "categorias": categorias_list
        }), 200

    except Exception as e:
        logger.error(f"❌ Error listar categorías: {str(e)}")
        return jsonify({"success": False, "message": str(e)}), 500


# ============================================
# 14. CREAR CATEGORÍA
# ============================================

@catalogo_api_bp.route('/categorias', methods=['POST', 'OPTIONS'])
@cross_origin(supports_credentials=True)
def crear_categoria():
    """POST /api/categorias"""
    if request.method == 'OPTIONS':
        return jsonify({"success": True}), 200

    user_id = get_authorized_user_id()
    if not user_id:
        return jsonify({"success": False, "message": "No autorizado"}), 401

    try:
        data = request.get_json()
        nombre = (data.get('nombre') or data.get('name', '')).strip()
        
        if not nombre:
            return jsonify({"success": False, "message": "El nombre es requerido"}), 400

        ctx = get_biz_context()
        negocio_id = ctx['negocio_id'] or int(data.get('negocio_id', 1))

        try:
            existente = CategoriaProducto.query.filter_by(
                usuario_id=int(user_id),
                negocio_id=negocio_id,
                nombre=nombre
            ).first()
            
            if existente:
                return jsonify({"success": False, "message": "Esta categoría ya existe"}), 400
            
            nueva_cat = CategoriaProducto(
                usuario_id=int(user_id),
                negocio_id=negocio_id,
                nombre=nombre,
                icono=data.get('icono') or data.get('icon', '📦'),
                color=data.get('color', '#6366f1')
            )
            
            db.session.add(nueva_cat)
            db.session.commit()

            logger.info(f"✅ Categoría creada: {nombre}")

            return jsonify({
                "success": True,
                "message": "Categoría creada",
                "categoria": nueva_cat.to_dict()
            }), 201
            
        except Exception as e:
            logger.error(f"Error creando categoría: {e}")
            return jsonify({
                "success": True,
                "message": "Categoría registrada",
                "categoria": {
                    "id": None,
                    "nombre": nombre,
                    "icon": data.get('icono', '📦'),
                    "color": data.get('color', '#6366f1')
                }
            }), 201

    except Exception as e:
        db.session.rollback()
        logger.error(f"❌ Error crear categoría: {str(e)}")
        return jsonify({"success": False, "message": str(e)}), 500


# ============================================
# 15. ACTUALIZAR CATEGORÍA
# ============================================

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
        categoria = CategoriaProducto.query.filter_by(
            id_categoria=id_categoria,
            usuario_id=int(user_id)
        ).first()
        
        if not categoria:
            return jsonify({"success": False, "message": "Categoría no encontrada"}), 404

        data = request.get_json()
        nombre_anterior = categoria.nombre
        
        if 'nombre' in data or 'name' in data:
            nuevo_nombre = data.get('nombre') or data.get('name')
            categoria.nombre = nuevo_nombre.strip()
        
        if 'icono' in data or 'icon' in data:
            categoria.icono = data.get('icono') or data.get('icon')
        
        if 'color' in data:
            categoria.color = data['color']

        if nombre_anterior != categoria.nombre:
            ProductoCatalogo.query.filter_by(
                usuario_id=int(user_id),
                categoria=nombre_anterior
            ).update({'categoria': categoria.nombre})

        db.session.commit()

        return jsonify({
            "success": True,
            "message": "Categoría actualizada",
            "categoria": categoria.to_dict()
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "message": str(e)}), 500


# ============================================
# 16. ELIMINAR CATEGORÍA
# ============================================

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
        categoria = CategoriaProducto.query.filter_by(
            id_categoria=id_categoria,
            usuario_id=int(user_id)
        ).first()
        
        if not categoria:
            return jsonify({"success": False, "message": "Categoría no encontrada"}), 404

        nombre = categoria.nombre
        
        productos_afectados = ProductoCatalogo.query.filter_by(
            usuario_id=int(user_id),
            categoria=nombre
        ).update({'categoria': ''})
        
        db.session.delete(categoria)
        db.session.commit()

        logger.info(f"🗑️ Categoría eliminada: {nombre}")

        return jsonify({
            "success": True,
            "message": f"Categoría '{nombre}' eliminada",
            "productos_afectados": productos_afectados
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "message": str(e)}), 500


# ============================================
# 17. AGREGAR IMÁGENES A GALERÍA
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
        producto = ProductoCatalogo.query.filter_by(
            id_producto=id_producto,
            usuario_id=int(user_id)
        ).first()
        
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
                    upload_result = cloudinary.uploader.upload(
                        file,
                        folder="productos_bizflow/galeria",
                        public_id=img_id,
                        overwrite=True,
                        resource_type="auto"
                    )
                    nuevas_urls.append(upload_result.get('secure_url'))
                except Exception as e:
                    logger.error(f"Error subiendo {key}: {e}")

        if not nuevas_urls:
            return jsonify({"success": False, "message": "No se recibieron imágenes"}), 400

        galeria_completa = galeria_actual + nuevas_urls
        galeria_completa = galeria_completa[:10]
        
        producto.imagenes = json.dumps(galeria_completa)
        db.session.commit()

        logger.info(f"📷 {len(nuevas_urls)} imágenes agregadas a producto {id_producto}")

        return jsonify({
            "success": True,
            "message": f"{len(nuevas_urls)} imágenes agregadas",
            "imagenes": galeria_completa,
            "total": len(galeria_completa)
        }), 201

    except Exception as e:
        db.session.rollback()
        logger.error(f"❌ Error agregar imágenes: {traceback.format_exc()}")
        return jsonify({"success": False, "message": str(e)}), 500


# ============================================
# 18. ELIMINAR IMAGEN DE GALERÍA
# ============================================

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
        producto = ProductoCatalogo.query.filter_by(
            id_producto=id_producto,
            usuario_id=int(user_id)
        ).first()
        
        if not producto:
            return jsonify({"success": False, "message": "Producto no encontrado"}), 404

        galeria = parse_json_field(producto.imagenes, [])
        
        if index < 0 or index >= len(galeria):
            return jsonify({"success": False, "message": "Índice de imagen inválido"}), 400
        
        imagen_eliminada = galeria.pop(index)
        producto.imagenes = json.dumps(galeria)
        
        if index == 0 and galeria:
            producto.imagen_url = galeria[0]
        elif index == 0:
            producto.imagen_url = "https://via.placeholder.com/150?text=No+Image"
        
        db.session.commit()

        return jsonify({
            "success": True,
            "message": "Imagen eliminada",
            "imagenes": galeria
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "message": str(e)}), 500


# ============================================
# 19. AGREGAR VIDEO YOUTUBE
# ============================================

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
        producto = ProductoCatalogo.query.filter_by(
            id_producto=id_producto,
            usuario_id=int(user_id)
        ).first()
        
        if not producto:
            return jsonify({"success": False, "message": "Producto no encontrado"}), 404

        data = request.get_json()
        videos_actuales = parse_json_field(producto.videos, [])

        def extraer_youtube_id(url):
            patterns = [
                r'(?:youtube\.com\/watch\?v=|youtu\.be\/|youtube\.com\/embed\/)([^&\s?]+)',
                r'youtube\.com\/shorts\/([^&\s?]+)'
            ]
            for pattern in patterns:
                match = re.search(pattern, url)
                if match:
                    return match.group(1)
            return None

        nuevos_videos = []
        
        if 'videos' in data:
            for v in data['videos']:
                url = v.get('url', '') if isinstance(v, dict) else v
                if url and ('youtube' in url or 'youtu.be' in url):
                    nuevos_videos.append(url)
        elif 'url' in data:
            url = data['url']
            if url and ('youtube' in url or 'youtu.be' in url):
                nuevos_videos.append(url)

        if not nuevos_videos:
            return jsonify({"success": False, "message": "No se recibieron URLs válidas de YouTube"}), 400

        # Evitar duplicados
        videos_unicos = [v for v in nuevos_videos if v not in videos_actuales]
        
        if not videos_unicos:
            return jsonify({"success": False, "message": "Videos ya agregados"}), 400

        todos_videos = videos_actuales + videos_unicos
        todos_videos = todos_videos[:10]
        
        producto.videos = json.dumps(todos_videos)
        db.session.commit()

        logger.info(f"🎥 {len(videos_unicos)} videos agregados a producto {id_producto}")

        return jsonify({
            "success": True,
            "message": f"{len(videos_unicos)} video(s) agregado(s)",
            "videos": todos_videos,
            "total": len(todos_videos)
        }), 201

    except Exception as e:
        db.session.rollback()
        logger.error(f"❌ Error agregar video: {str(e)}")
        return jsonify({"success": False, "message": str(e)}), 500


# ============================================
# 20. ELIMINAR VIDEO
# ============================================

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
        producto = ProductoCatalogo.query.filter_by(
            id_producto=id_producto,
            usuario_id=int(user_id)
        ).first()
        
        if not producto:
            return jsonify({"success": False, "message": "Producto no encontrado"}), 404

        videos = parse_json_field(producto.videos, [])
        
        if index < 0 or index >= len(videos):
            return jsonify({"success": False, "message": "Índice de video inválido"}), 400
        
        video_eliminado = videos.pop(index)
        producto.videos = json.dumps(videos)
        db.session.commit()

        return jsonify({
            "success": True,
            "message": "Video eliminado",
            "video_eliminado": video_eliminado,
            "videos": videos
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "message": str(e)}), 500


# ============================================
# 21. BUSCAR POR CÓDIGO
# ============================================

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
        
        if ctx['negocio_id']:
            query = query.filter_by(negocio_id=ctx['negocio_id'])
        
        producto = query.filter(
            db.or_(
                ProductoCatalogo.codigo_barras == codigo,
                ProductoCatalogo.referencia_sku == codigo,
                ProductoCatalogo.referencia_sku.ilike(codigo)
            )
        ).first()
        
        if not producto:
            return jsonify({
                "success": False,
                "encontrado": False,
                "message": "Producto no encontrado",
                "codigo": codigo
            }), 404

        producto_dict = producto.to_dict()
        producto_dict['id'] = producto.id_producto

        return jsonify({
            "success": True,
            "encontrado": True,
            "producto": producto_dict
        }), 200

    except Exception as e:
        logger.error(f"❌ Error buscar código: {str(e)}")
        return jsonify({"success": False, "message": str(e)}), 500


# ============================================
# 22. BÚSQUEDA GLOBAL
# ============================================

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
        
        if ctx['negocio_id']:
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
            "id": p.id_producto,
            "nombre": p.nombre,
            "sku": p.referencia_sku,
            "barcode": p.codigo_barras,
            "categoria": p.categoria,
            "precio": p.precio,
            "stock": p.stock,
            "imagen_url": p.imagen_url
        } for p in productos]

        return jsonify({
            "success": True,
            "termino": q,
            "total": len(resultados),
            "productos": resultados
        }), 200

    except Exception as e:
        logger.error(f"❌ Error buscar: {str(e)}")
        return jsonify({"success": False, "message": str(e)}), 500


# ============================================
# 23. IMPORTAR PRODUCTOS
# ============================================

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
        negocio_id = ctx['negocio_id'] or 1
        sucursal_id = ctx['sucursal_id'] or 1
        
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
            data = request.get_json()
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

        logger.info(f"📥 Importación: {importados} productos, {len(errores)} errores")

        return jsonify({
            "success": True,
            "message": f"{importados} productos importados",
            "importados": importados,
            "errores": len(errores),
            "detalle_errores": errores[:20]
        }), 201

    except Exception as e:
        db.session.rollback()
        logger.error(f"❌ Error importar: {traceback.format_exc()}")
        return jsonify({"success": False, "message": str(e)}), 500


# ============================================
# 24. EXPORTAR PRODUCTOS
# ============================================

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
        
        params = request.get_json() if request.method == 'POST' else request.args.to_dict()
        
        formato = params.get('formato', 'csv').lower()
        filtro = params.get('filtro', 'all')
        campos = params.get('campos', ['nombre', 'sku', 'codigo_barras', 'categoria', 'precio', 'costo', 'stock'])
        
        if isinstance(campos, str):
            campos = [c.strip() for c in campos.split(',')]

        query = ProductoCatalogo.query.filter_by(usuario_id=int(user_id))
        
        if ctx['negocio_id']:
            query = query.filter_by(negocio_id=ctx['negocio_id'])
        
        if filtro == 'in_stock':
            query = query.filter(ProductoCatalogo.stock > 10)
        elif filtro == 'low_stock':
            query = query.filter(ProductoCatalogo.stock > 0, ProductoCatalogo.stock <= 10)
        elif filtro == 'out_stock':
            query = query.filter(ProductoCatalogo.stock == 0)
        
        productos = query.all()

        campo_map = {
            'nombre': lambda p: p.nombre,
            'sku': lambda p: p.referencia_sku or '',
            'codigo_barras': lambda p: p.codigo_barras or '',
            'categoria': lambda p: p.categoria or '',
            'precio': lambda p: p.precio,
            'costo': lambda p: p.costo,
            'stock': lambda p: p.stock,
            'descripcion': lambda p: p.descripcion or ''
        }

        datos = []
        for p in productos:
            fila = {}
            for campo in campos:
                if campo in campo_map:
                    fila[campo] = campo_map[campo](p)
            datos.append(fila)

        if formato == 'json':
            return jsonify({
                "success": True,
                "total": len(datos),
                "formato": "json",
                "datos": datos
            }), 200
        else:
            import io
            import csv
            
            output = io.StringIO()
            writer = csv.DictWriter(output, fieldnames=campos)
            writer.writeheader()
            writer.writerows(datos)
            
            return jsonify({
                "success": True,
                "total": len(datos),
                "formato": "csv",
                "contenido": output.getvalue(),
                "filename": f"productos_{datetime.now().strftime('%Y%m%d')}.csv"
            }), 200

    except Exception as e:
        logger.error(f"❌ Error exportar: {str(e)}")
        return jsonify({"success": False, "message": str(e)}), 500


# ============================================
# 25. CATÁLOGO PÚBLICO (Sin auth)
# ============================================

@catalogo_api_bp.route('/productos/publicos/<int:negocio_id>', methods=['GET', 'OPTIONS'])
@cross_origin(supports_credentials=True)
def catalogo_publico(negocio_id):
    """GET /api/productos/publicos/{negocio_id}"""
    if request.method == 'OPTIONS':
        return jsonify({"success": True}), 200

    try:
        query = ProductoCatalogo.query.filter_by(
            negocio_id=negocio_id,
            activo=True,
            estado_publicacion=True
        )
        
        categoria = request.args.get('categoria')
        if categoria:
            query = query.filter_by(categoria=categoria)
        
        search = request.args.get('search', '').strip()
        if search:
            query = query.filter(ProductoCatalogo.nombre.ilike(f"%{search}%"))
        
        limit = min(int(request.args.get('limit', 50)), 200)
        
        productos = query.order_by(ProductoCatalogo.nombre.asc()).limit(limit).all()
        
        datos_publicos = [{
            "id": p.id_producto,
            "nombre": p.nombre,
            "descripcion": p.descripcion,
            "precio": p.precio,
            "categoria": p.categoria,
            "imagen_url": p.imagen_url,
            "imagenes": parse_json_field(p.imagenes, []),
            "videos": parse_json_field(p.videos, []),
            "sku": p.referencia_sku,
            "en_stock": p.stock > 0
        } for p in productos]

        categorias = db.session.query(ProductoCatalogo.categoria).filter_by(
            negocio_id=negocio_id,
            activo=True,
            estado_publicacion=True
        ).distinct().all()

        return jsonify({
            "success": True,
            "negocio_id": negocio_id,
            "total": len(datos_publicos),
            "categorias": [c[0] for c in categorias if c[0]],
            "productos": datos_publicos
        }), 200

    except Exception as e:
        logger.error(f"❌ Error catálogo público: {str(e)}")
        return jsonify({"success": False, "message": str(e)}), 500


# ============================================
# FIN DEL ARCHIVO - catalogo_api.py v3.1
# ============================================