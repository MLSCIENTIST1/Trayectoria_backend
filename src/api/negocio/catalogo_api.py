# ============================================
# catalogo_api.py - VERSIÓN COMPLETA v3.0
# Conectado con Inventario PRO + BizContext
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
from src.models.colombia_data.contabilidad.operaciones_y_catalogo import ProductoCatalogo, TransaccionOperativa

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
    negocio_id = (
        request.headers.get('X-Negocio-ID') or 
        request.args.get('negocio_id') or
        request.json.get('negocio_id') if request.is_json else None
    )
    
    sucursal_id = (
        request.headers.get('X-Sucursal-ID') or 
        request.args.get('sucursal_id') or
        request.json.get('sucursal_id') if request.is_json else None
    )
    
    return {
        'negocio_id': int(negocio_id) if negocio_id else None,
        'sucursal_id': int(sucursal_id) if sucursal_id else None
    }


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
        "version": "3.0"
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
            d['id'] = p.id_producto  # El JS usa 'id' no 'id_producto'
            d['id_producto'] = p.id_producto
            d['sku'] = p.referencia_sku
            d['barcode'] = getattr(p, 'codigo_barras', '')
            d['imagenes'] = json.loads(p.imagenes) if isinstance(p.imagenes, str) else (p.imagenes or [])
            d['youtube_links'] = json.loads(p.youtube_links) if hasattr(p, 'youtube_links') and isinstance(p.youtube_links, str) else []
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
# 2. GUARDAR PRODUCTO (Crear nuevo)
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
    - imagen (file) o imagen_url
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
        
        # Validar nombre
        nombre = data.get('nombre', '').strip()
        if not nombre:
            return jsonify({"success": False, "message": "El nombre es requerido"}), 400
        
        # Procesar imagen
        imagen_url = data.get('imagen_url', '')
        file = request.files.get('imagen') or request.files.get('imagen_file')
        
        if file and file.filename:
            nombre_limpio = re.sub(r'[^a-zA-Z0-9]', '', nombre[:15])
            p_id = f"user_{user_id}_{nombre_limpio}_{int(time.time())}"
            
            upload_result = cloudinary.uploader.upload(
                file,
                folder="productos_bizflow",
                public_id=p_id,
                overwrite=True,
                resource_type="auto"
            )
            imagen_url = upload_result.get('secure_url')

        # Obtener IDs de contexto
        negocio_id = ctx['negocio_id'] or int(data.get('negocio_id', 1))
        sucursal_id = ctx['sucursal_id'] or int(data.get('sucursal_id', 1))

        # Crear producto
        nuevo_prod = ProductoCatalogo(
            nombre=nombre,
            descripcion=data.get('descripcion', ''),
            negocio_id=negocio_id,
            usuario_id=int(user_id),
            sucursal_id=sucursal_id,
            categoria=data.get('categoria', 'General'),
            costo=float(data.get('costo', 0)),
            precio=float(data.get('precio', 0)),
            stock=int(data.get('stock', 0)),
            referencia_sku=data.get('sku', ''),
            codigo_barras=data.get('barcode', ''),
            imagen_url=imagen_url or "https://via.placeholder.com/150?text=No+Image",
            imagenes=json.dumps(data.get('imagenes', [])),
            activo=True
        )
        
        # Guardar youtube_links si existe el campo
        if hasattr(nuevo_prod, 'youtube_links'):
            nuevo_prod.youtube_links = json.dumps(data.get('youtube_links', []))
        
        db.session.add(nuevo_prod)
        db.session.commit()

        # Respuesta con formato compatible con JS
        producto_dict = nuevo_prod.to_dict()
        producto_dict['id'] = nuevo_prod.id_producto
        
        logger.info(f"✅ Producto creado: {nombre} (ID: {nuevo_prod.id_producto})")

        return jsonify({
            "success": True,
            "message": "Producto creado exitosamente",
            "producto": producto_dict,
            "url": imagen_url
        }), 201

    except Exception as e:
        db.session.rollback()
        logger.error(f"❌ Error en Guardar: {traceback.format_exc()}")
        return jsonify({"success": False, "message": str(e)}), 500
    
# ============================================
# 3. ACTUALIZAR PRODUCTO (Edición completa)
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

        # Actualizar campos básicos (solo si vienen)
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
        
        if 'sku' in data:
            producto.referencia_sku = data['sku']
        
        if 'barcode' in data:
            producto.codigo_barras = data['barcode']
        
        if 'activo' in data:
            producto.activo = data['activo'] in [True, 'true', '1', 1]
        
        # Actualizar negocio/sucursal si vienen
        if 'negocio_id' in data:
            producto.negocio_id = int(data['negocio_id'])
        
        if 'sucursal_id' in data:
            producto.sucursal_id = int(data['sucursal_id'])
        
        # Manejar imágenes array
        if 'imagenes' in data:
            imagenes = data['imagenes']
            if isinstance(imagenes, str):
                try:
                    imagenes = json.loads(imagenes)
                except:
                    imagenes = []
            producto.imagenes = json.dumps(imagenes)
        
        # Manejar YouTube links
        if 'youtube_links' in data and hasattr(producto, 'youtube_links'):
            yt_links = data['youtube_links']
            if isinstance(yt_links, str):
                try:
                    yt_links = json.loads(yt_links)
                except:
                    yt_links = []
            producto.youtube_links = json.dumps(yt_links)
        
        # Subir nueva imagen principal
        file = request.files.get('imagen') or request.files.get('imagen_file')
        if file and file.filename:
            nombre_limpio = re.sub(r'[^a-zA-Z0-9]', '', producto.nombre[:15])
            p_id = f"user_{user_id}_{nombre_limpio}_{int(time.time())}"
            
            upload_result = cloudinary.uploader.upload(
                file,
                folder="productos_bizflow",
                public_id=p_id,
                overwrite=True,
                resource_type="auto"
            )
            producto.imagen_url = upload_result.get('secure_url')
        
        # Subir imágenes de galería (imagen_1, imagen_2, etc.)
        galeria_urls = []
        imagenes_actuales = json.loads(producto.imagenes) if producto.imagenes else []
        
        for i in range(1, 9):  # Hasta 8 imágenes adicionales
            file_key = f'imagen_{i}'
            if file_key in request.files:
                img_file = request.files[file_key]
                if img_file.filename:
                    nombre_limpio = re.sub(r'[^a-zA-Z0-9]', '', producto.nombre[:15])
                    img_id = f"user_{user_id}_{nombre_limpio}_gal_{i}_{int(time.time())}"
                    
                    upload_result = cloudinary.uploader.upload(
                        img_file,
                        folder="productos_bizflow/galeria",
                        public_id=img_id,
                        overwrite=True,
                        resource_type="auto"
                    )
                    galeria_urls.append(upload_result.get('secure_url'))
        
        if galeria_urls:
            producto.imagenes = json.dumps(imagenes_actuales + galeria_urls)

        db.session.commit()

        # Respuesta
        producto_dict = producto.to_dict()
        producto_dict['id'] = producto.id_producto
        producto_dict['sku'] = producto.referencia_sku
        producto_dict['barcode'] = producto.codigo_barras
        producto_dict['imagenes'] = json.loads(producto.imagenes) if producto.imagenes else []

        logger.info(f"✅ Producto {id_producto} actualizado")

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
    """
    DELETE /api/producto/eliminar/{id}
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
        
        nombre = producto.nombre
        db.session.delete(producto)
        db.session.commit()
        
        logger.info(f"✅ Producto eliminado: {nombre} (ID: {id_producto})")
        
        return jsonify({
            "success": True,
            "message": f"Producto '{nombre}' eliminado"
        }), 200
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"❌ Error eliminar: {str(e)}")
        return jsonify({"success": False, "message": str(e)}), 500


# ============================================
# 5. EDICIÓN RÁPIDA (Stock/Precio)
# ============================================

@catalogo_api_bp.route('/producto/edicion-rapida/<int:id_producto>', methods=['PATCH', 'OPTIONS'])
@cross_origin(supports_credentials=True)
def edicion_rapida(id_producto):
    """
    PATCH /api/producto/edicion-rapida/{id}
    
    Body JSON:
    - stock: nuevo stock
    - precio: nuevo precio
    - costo: nuevo costo
    
    Ideal para actualizaciones inline desde la UI.
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

        producto = ProductoCatalogo.query.filter_by(
            id_producto=id_producto,
            usuario_id=int(user_id)
        ).first()
        
        if not producto:
            return jsonify({"success": False, "message": "Producto no encontrado"}), 404

        # Guardar valores anteriores para el log
        old_stock = producto.stock
        old_precio = producto.precio

        # Solo actualizar campos enviados
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
# 6. DUPLICAR PRODUCTO
# ============================================

@catalogo_api_bp.route('/producto/duplicar/<int:id_producto>', methods=['POST', 'OPTIONS'])
@cross_origin(supports_credentials=True)
def duplicar_producto(id_producto):
    """
    POST /api/producto/duplicar/{id}
    
    Crea una copia del producto con:
    - Nombre + " (Copia)"
    - Stock en 0
    - Activo = False
    """
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

        # Crear copia
        duplicado = ProductoCatalogo(
            nombre=f"{original.nombre} (Copia)",
            descripcion=original.descripcion,
            negocio_id=original.negocio_id,
            usuario_id=int(user_id),
            sucursal_id=original.sucursal_id,
            categoria=original.categoria,
            costo=original.costo,
            precio=original.precio,
            stock=0,  # Stock en 0 por seguridad
            imagen_url=original.imagen_url,
            imagenes=original.imagenes,
            referencia_sku=f"{original.referencia_sku}_COPY" if original.referencia_sku else '',
            codigo_barras='',  # Barcode vacío (debe ser único)
            activo=False  # Inactivo por defecto
        )
        
        # Copiar youtube_links si existe
        if hasattr(original, 'youtube_links'):
            duplicado.youtube_links = original.youtube_links
        
        db.session.add(duplicado)
        db.session.commit()

        # Respuesta
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
# 7. SUBIR MÚLTIPLES IMÁGENES A GALERÍA
# ============================================

@catalogo_api_bp.route('/producto/<int:id_producto>/imagenes', methods=['POST', 'OPTIONS'])
@cross_origin(supports_credentials=True)
def agregar_imagenes(id_producto):
    """
    POST /api/producto/{id}/imagenes
    
    Sube múltiples imágenes a la galería del producto.
    Acepta archivos con cualquier nombre de campo.
    Máximo 10 imágenes por producto.
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

        # Cargar galería actual
        galeria_actual = []
        if producto.imagenes:
            try:
                galeria_actual = json.loads(producto.imagenes) if isinstance(producto.imagenes, str) else producto.imagenes
            except:
                galeria_actual = []

        # Subir nuevas imágenes
        nuevas_urls = []
        for key in request.files:
            file = request.files[key]
            if file.filename:
                nombre_limpio = re.sub(r'[^a-zA-Z0-9]', '', producto.nombre[:15])
                img_id = f"user_{user_id}_{nombre_limpio}_{int(time.time())}_{key}"
                
                upload_result = cloudinary.uploader.upload(
                    file,
                    folder="productos_bizflow/galeria",
                    public_id=img_id,
                    overwrite=True,
                    resource_type="auto"
                )
                nuevas_urls.append(upload_result.get('secure_url'))

        if not nuevas_urls:
            return jsonify({"success": False, "message": "No se recibieron imágenes"}), 400

        # Combinar y limitar a 10
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
# 8. ELIMINAR IMAGEN DE GALERÍA
# ============================================

@catalogo_api_bp.route('/producto/<int:id_producto>/imagenes/<int:index>', methods=['DELETE', 'OPTIONS'])
@cross_origin(supports_credentials=True)
def eliminar_imagen(id_producto, index):
    """
    DELETE /api/producto/{id}/imagenes/{index}
    
    Elimina una imagen específica de la galería por su índice.
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

        galeria = json.loads(producto.imagenes) if producto.imagenes else []
        
        if index < 0 or index >= len(galeria):
            return jsonify({"success": False, "message": "Índice de imagen inválido"}), 400
        
        imagen_eliminada = galeria.pop(index)
        producto.imagenes = json.dumps(galeria)
        
        # Si era la imagen principal, actualizar
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
# 9. AJUSTAR STOCK (Entrada/Salida/Ajuste)
# ============================================

@catalogo_api_bp.route('/producto/<int:id_producto>/stock', methods=['POST', 'OPTIONS'])
@cross_origin(supports_credentials=True)
def ajustar_stock(id_producto):
    """
    POST /api/producto/{id}/stock
    
    Body JSON:
    - tipo: 'entrada' | 'salida' | 'ajuste'
    - cantidad: número positivo
    - nota: descripción opcional
    
    Registra el movimiento en historial.
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
        nota = data.get('nota', '').strip()

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
        
        # Calcular nuevo stock
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

        # Actualizar producto
        producto.stock = nuevo_stock
        
        # Registrar movimiento (si existe la tabla)
        try:
            from src.models.colombia_data.contabilidad.operaciones_y_catalogo import MovimientoStock
            
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
        except ImportError:
            # Tabla no existe aún, solo actualizar stock
            logger.warning("⚠️ Tabla MovimientoStock no existe, solo se actualizó stock")

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
# 10. HISTORIAL DE MOVIMIENTOS DE STOCK
# ============================================

@catalogo_api_bp.route('/producto/<int:id_producto>/movimientos', methods=['GET', 'OPTIONS'])
@cross_origin(supports_credentials=True)
def obtener_movimientos(id_producto):
    """
    GET /api/producto/{id}/movimientos
    
    Retorna el historial de movimientos de stock del producto.
    """
    if request.method == 'OPTIONS':
        return jsonify({"success": True}), 200

    user_id = get_authorized_user_id()
    if not user_id:
        return jsonify({"success": False, "message": "No autorizado"}), 401

    try:
        # Verificar que el producto pertenece al usuario
        producto = ProductoCatalogo.query.filter_by(
            id_producto=id_producto,
            usuario_id=int(user_id)
        ).first()
        
        if not producto:
            return jsonify({"success": False, "message": "Producto no encontrado"}), 404

        try:
            from src.models.colombia_data.contabilidad.operaciones_y_catalogo import MovimientoStock
            
            movimientos = MovimientoStock.query.filter_by(
                producto_id=id_producto
            ).order_by(MovimientoStock.fecha.desc()).limit(100).all()
            
            # Calcular resumen
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
            
        except ImportError:
            # Tabla no existe
            return jsonify({
                "success": True,
                "producto": {
                    "id": producto.id_producto,
                    "nombre": producto.nombre,
                    "stock_actual": producto.stock
                },
                "resumen": {
                    "total_entradas": 0,
                    "total_salidas": 0,
                    "total_movimientos": 0
                },
                "movimientos": [],
                "message": "Historial no disponible"
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
    """
    GET /api/stock/alertas
    
    Query params:
    - negocio_id: filtrar por negocio
    - tipo: 'critical' | 'warning' | 'all'
    
    Retorna productos con stock bajo o crítico.
    """
    if request.method == 'OPTIONS':
        return jsonify({"success": True}), 200

    user_id = get_authorized_user_id()
    if not user_id:
        return jsonify({"success": False, "message": "No autorizado"}), 401

    try:
        ctx = get_biz_context()
        tipo_alerta = request.args.get('tipo', 'all')
        
        # Query base
        query = ProductoCatalogo.query.filter_by(
            usuario_id=int(user_id),
            activo=True
        )
        
        if ctx['negocio_id']:
            query = query.filter_by(negocio_id=ctx['negocio_id'])
        
        # Filtrar por nivel de alerta
        if tipo_alerta == 'critical':
            query = query.filter(ProductoCatalogo.stock <= ProductoCatalogo.stock_critico)
        elif tipo_alerta == 'warning':
            query = query.filter(
                ProductoCatalogo.stock > ProductoCatalogo.stock_critico,
                ProductoCatalogo.stock <= ProductoCatalogo.stock_bajo
            )
        else:  # all
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
# 12. ACTUALIZAR UMBRALES DE ALERTA
# ============================================

@catalogo_api_bp.route('/producto/<int:id_producto>/umbrales', methods=['PATCH', 'OPTIONS'])
@cross_origin(supports_credentials=True)
def actualizar_umbrales(id_producto):
    """
    PATCH /api/producto/{id}/umbrales
    
    Body JSON:
    - stock_critico: número
    - stock_bajo: número
    - stock_minimo: número
    """
    if request.method == 'OPTIONS':
        return jsonify({"success": True}), 200

    user_id = get_authorized_user_id()
    if not user_id:
        return jsonify({"success": False, "message": "No autorizado"}), 401

    try:
        data = request.get_json()
        
        producto = ProductoCatalogo.query.filter_by(
            id_producto=id_producto,
            usuario_id=int(user_id)
        ).first()
        
        if not producto:
            return jsonify({"success": False, "message": "Producto no encontrado"}), 404

        if 'stock_critico' in data:
            producto.stock_critico = int(data['stock_critico'])
        
        if 'stock_bajo' in data:
            producto.stock_bajo = int(data['stock_bajo'])
        
        if 'stock_minimo' in data:
            producto.stock_minimo = int(data['stock_minimo'])

        db.session.commit()

        return jsonify({
            "success": True,
            "message": "Umbrales actualizados",
            "producto": {
                "id": producto.id_producto,
                "stock_critico": producto.stock_critico,
                "stock_bajo": producto.stock_bajo,
                "stock_minimo": producto.stock_minimo
            }
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "message": str(e)}), 500


# ============================================
# 13. ESTADÍSTICAS DE INVENTARIO
# ============================================

@catalogo_api_bp.route('/inventario/estadisticas', methods=['GET', 'OPTIONS'])
@cross_origin(supports_credentials=True)
def estadisticas_inventario():
    """
    GET /api/inventario/estadisticas
    
    Retorna estadísticas generales del inventario.
    Compatible con el panel de stats del JS.
    """
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
        
        # Categorías más usadas
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
# 14. LISTAR CATEGORÍAS
# ============================================

@catalogo_api_bp.route('/categorias', methods=['GET', 'OPTIONS'])
@cross_origin(supports_credentials=True)
def listar_categorias():
    """
    GET /api/categorias
    
    Retorna todas las categorías del usuario con conteo de productos.
    Compatible con el sistema de chips del JS.
    """
    if request.method == 'OPTIONS':
        return jsonify({"success": True}), 200

    user_id = get_authorized_user_id()
    if not user_id:
        return jsonify({"success": False, "message": "No autorizado"}), 401

    try:
        ctx = get_biz_context()
        
        # Intentar cargar de tabla CategoriaProducto
        categorias_custom = []
        try:
            from src.models.colombia_data.contabilidad.operaciones_y_catalogo import CategoriaProducto
            
            query = CategoriaProducto.query.filter_by(usuario_id=int(user_id))
            if ctx['negocio_id']:
                query = query.filter_by(negocio_id=ctx['negocio_id'])
            
            categorias_custom = query.all()
        except ImportError:
            pass
        
        # Obtener categorías únicas de productos existentes
        query_productos = ProductoCatalogo.query.filter_by(usuario_id=int(user_id))
        if ctx['negocio_id']:
            query_productos = query_productos.filter_by(negocio_id=ctx['negocio_id'])
        
        productos = query_productos.all()
        
        # Contar productos por categoría
        conteo = {}
        for p in productos:
            cat = p.categoria or 'Sin categoría'
            conteo[cat] = conteo.get(cat, 0) + 1
        
        # Combinar categorías custom con las detectadas
        categorias_dict = {}
        
        # Primero las custom (tienen icono y color)
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
        
        # Agregar categorías detectadas que no están en custom
        iconos_default = {
            'Electrónica': '📱', 'Ropa': '👕', 'Hogar': '🏠', 
            'Accesorios': '🎁', 'Alimentos': '🍔', 'Bebidas': '🥤',
            'Salud': '💊', 'Belleza': '💄', 'Deportes': '⚽',
            'Juguetes': '🧸', 'Mascotas': '🐕', 'Oficina': '📎',
            'General': '📦', 'Sin categoría': '📁'
        }
        
        colores_default = [
            '#6366f1', '#ec4899', '#10b981', '#f59e0b', 
            '#8b5cf6', '#ef4444', '#06b6d4', '#84cc16'
        ]
        
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
            "total_productos": sum(c['count'] for c in categorias_list),
            "categorias": categorias_list
        }), 200

    except Exception as e:
        logger.error(f"❌ Error listar categorías: {str(e)}")
        return jsonify({"success": False, "message": str(e)}), 500


# ============================================
# 15. CREAR CATEGORÍA
# ============================================

@catalogo_api_bp.route('/categorias', methods=['POST', 'OPTIONS'])
@cross_origin(supports_credentials=True)
def crear_categoria():
    """
    POST /api/categorias
    
    Body JSON:
    - nombre (requerido)
    - icono: emoji (default: 📦)
    - color: hex color (default: #6366f1)
    """
    if request.method == 'OPTIONS':
        return jsonify({"success": True}), 200

    user_id = get_authorized_user_id()
    if not user_id:
        return jsonify({"success": False, "message": "No autorizado"}), 401

    try:
        data = request.get_json()
        nombre = data.get('nombre', '').strip() or data.get('name', '').strip()
        
        if not nombre:
            return jsonify({"success": False, "message": "El nombre es requerido"}), 400

        ctx = get_biz_context()
        negocio_id = ctx['negocio_id'] or int(data.get('negocio_id', 1))

        try:
            from src.models.colombia_data.contabilidad.operaciones_y_catalogo import CategoriaProducto
            
            # Verificar si ya existe
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
            
        except ImportError:
            # Tabla no existe, solo validar que no hay problema
            return jsonify({
                "success": True,
                "message": "Categoría registrada (sin persistencia)",
                "categoria": {
                    "id": None,
                    "name": nombre,
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
# 16. ACTUALIZAR CATEGORÍA
# ============================================

@catalogo_api_bp.route('/categorias/<int:id_categoria>', methods=['PUT', 'PATCH', 'OPTIONS'])
@cross_origin(supports_credentials=True)
def actualizar_categoria(id_categoria):
    """
    PUT/PATCH /api/categorias/{id}
    
    Body JSON:
    - nombre
    - icono
    - color
    """
    if request.method == 'OPTIONS':
        return jsonify({"success": True}), 200

    user_id = get_authorized_user_id()
    if not user_id:
        return jsonify({"success": False, "message": "No autorizado"}), 401

    try:
        from src.models.colombia_data.contabilidad.operaciones_y_catalogo import CategoriaProducto
        
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

        # Si cambió el nombre, actualizar productos
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

    except ImportError:
        return jsonify({"success": False, "message": "Tabla de categorías no disponible"}), 501
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "message": str(e)}), 500


# ============================================
# 17. ELIMINAR CATEGORÍA
# ============================================

@catalogo_api_bp.route('/categorias/<int:id_categoria>', methods=['DELETE', 'OPTIONS'])
@cross_origin(supports_credentials=True)
def eliminar_categoria(id_categoria):
    """
    DELETE /api/categorias/{id}
    
    Elimina la categoría. Los productos quedan sin categoría.
    """
    if request.method == 'OPTIONS':
        return jsonify({"success": True}), 200

    user_id = get_authorized_user_id()
    if not user_id:
        return jsonify({"success": False, "message": "No autorizado"}), 401

    try:
        from src.models.colombia_data.contabilidad.operaciones_y_catalogo import CategoriaProducto
        
        categoria = CategoriaProducto.query.filter_by(
            id_categoria=id_categoria,
            usuario_id=int(user_id)
        ).first()
        
        if not categoria:
            return jsonify({"success": False, "message": "Categoría no encontrada"}), 404

        nombre = categoria.nombre
        
        # Quitar categoría de productos
        productos_afectados = ProductoCatalogo.query.filter_by(
            usuario_id=int(user_id),
            categoria=nombre
        ).update({'categoria': ''})
        
        db.session.delete(categoria)
        db.session.commit()

        logger.info(f"🗑️ Categoría eliminada: {nombre} ({productos_afectados} productos afectados)")

        return jsonify({
            "success": True,
            "message": f"Categoría '{nombre}' eliminada",
            "productos_afectados": productos_afectados
        }), 200

    except ImportError:
        return jsonify({"success": False, "message": "Tabla de categorías no disponible"}), 501
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "message": str(e)}), 500


# ============================================
# 18. IMPORTACIÓN MASIVA CSV/JSON
# ============================================

@catalogo_api_bp.route('/productos/importar', methods=['POST', 'OPTIONS'])
@cross_origin(supports_credentials=True)
def importar_productos():
    """
    POST /api/productos/importar
    
    Acepta:
    - Archivo CSV (multipart/form-data con campo 'archivo')
    - JSON array en body
    
    Campos esperados:
    nombre, sku, barcode, categoria, precio, costo, stock, descripcion
    """
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
        
        # Detectar tipo de entrada
        if 'archivo' in request.files:
            # CSV Upload
            archivo = request.files['archivo']
            if not archivo.filename:
                return jsonify({"success": False, "message": "No se seleccionó archivo"}), 400
            
            import csv
            import io
            
            contenido = archivo.read().decode('utf-8-sig')
            reader = csv.DictReader(io.StringIO(contenido))
            
            for row in reader:
                # Normalizar nombres de columnas
                productos_data.append({
                    'nombre': row.get('nombre') or row.get('name') or row.get('producto', ''),
                    'sku': row.get('sku') or row.get('codigo') or row.get('code', ''),
                    'barcode': row.get('barcode') or row.get('codigo_barras', ''),
                    'categoria': row.get('categoria') or row.get('category', 'General'),
                    'precio': row.get('precio') or row.get('price', 0),
                    'costo': row.get('costo') or row.get('cost', 0),
                    'stock': row.get('stock') or row.get('cantidad') or row.get('quantity', 0),
                    'descripcion': row.get('descripcion') or row.get('description', '')
                })
        else:
            # JSON Body
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

        # Procesar e importar
        importados = 0
        errores = []
        productos_creados = []

        for idx, prod in enumerate(productos_data):
            try:
                nombre = str(prod.get('nombre', '')).strip()
                if not nombre:
                    errores.append({"fila": idx + 1, "error": "Nombre vacío"})
                    continue
                
                nuevo = ProductoCatalogo(
                    nombre=nombre,
                    descripcion=str(prod.get('descripcion', '')),
                    precio=float(prod.get('precio', 0)),
                    costo=float(prod.get('costo', 0)),
                    stock=int(prod.get('stock', 0)),
                    categoria=str(prod.get('categoria', 'General')),
                    referencia_sku=str(prod.get('sku', '')),
                    codigo_barras=str(prod.get('barcode', '')),
                    negocio_id=negocio_id,
                    usuario_id=int(user_id),
                    sucursal_id=sucursal_id,
                    imagen_url="https://via.placeholder.com/150?text=Import",
                    activo=True
                )
                
                db.session.add(nuevo)
                importados += 1
                productos_creados.append(nombre)
                
            except Exception as e:
                errores.append({"fila": idx + 1, "error": str(e)})

        db.session.commit()

        logger.info(f"📥 Importación: {importados} productos creados, {len(errores)} errores")

        return jsonify({
            "success": True,
            "message": f"{importados} productos importados",
            "importados": importados,
            "errores": len(errores),
            "detalle_errores": errores[:20],  # Limitar errores en respuesta
            "productos": productos_creados[:50]  # Limitar lista
        }), 201

    except Exception as e:
        db.session.rollback()
        logger.error(f"❌ Error importar: {traceback.format_exc()}")
        return jsonify({"success": False, "message": str(e)}), 500


# ============================================
# 19. EXPORTAR PRODUCTOS CSV/JSON
# ============================================

@catalogo_api_bp.route('/productos/exportar', methods=['GET', 'POST', 'OPTIONS'])
@cross_origin(supports_credentials=True)
def exportar_productos():
    """
    GET/POST /api/productos/exportar
    
    Query params o Body:
    - formato: 'csv' | 'json' (default: csv)
    - filtro: 'all' | 'in_stock' | 'low_stock' | 'out_stock'
    - campos: lista de campos a exportar (opcional)
    """
    if request.method == 'OPTIONS':
        return jsonify({"success": True}), 200

    user_id = get_authorized_user_id()
    if not user_id:
        return jsonify({"success": False, "message": "No autorizado"}), 401

    try:
        ctx = get_biz_context()
        
        # Obtener parámetros
        if request.method == 'POST':
            params = request.get_json() or {}
        else:
            params = request.args.to_dict()
        
        formato = params.get('formato', 'csv').lower()
        filtro = params.get('filtro', 'all')
        campos = params.get('campos', [
            'nombre', 'sku', 'barcode', 'categoria', 
            'precio', 'costo', 'stock', 'descripcion'
        ])
        
        if isinstance(campos, str):
            campos = [c.strip() for c in campos.split(',')]

        # Query productos
        query = ProductoCatalogo.query.filter_by(usuario_id=int(user_id))
        
        if ctx['negocio_id']:
            query = query.filter_by(negocio_id=ctx['negocio_id'])
        
        # Aplicar filtro
        if filtro == 'in_stock':
            query = query.filter(ProductoCatalogo.stock > 10)
        elif filtro == 'low_stock':
            query = query.filter(ProductoCatalogo.stock > 0, ProductoCatalogo.stock <= 10)
        elif filtro == 'out_stock':
            query = query.filter(ProductoCatalogo.stock == 0)
        
        productos = query.all()

        # Mapeo de campos
        campo_map = {
            'nombre': lambda p: p.nombre,
            'sku': lambda p: p.referencia_sku or '',
            'barcode': lambda p: p.codigo_barras or '',
            'categoria': lambda p: p.categoria or '',
            'precio': lambda p: p.precio,
            'costo': lambda p: p.costo,
            'stock': lambda p: p.stock,
            'descripcion': lambda p: p.descripcion or '',
            'imagen_url': lambda p: p.imagen_url or '',
            'activo': lambda p: p.activo
        }

        # Generar datos
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
        
        else:  # CSV
            import io
            import csv
            
            output = io.StringIO()
            writer = csv.DictWriter(output, fieldnames=campos)
            writer.writeheader()
            writer.writerows(datos)
            
            csv_content = output.getvalue()

            return jsonify({
                "success": True,
                "total": len(datos),
                "formato": "csv",
                "contenido": csv_content,
                "filename": f"productos_{datetime.now().strftime('%Y%m%d')}.csv"
            }), 200

    except Exception as e:
        logger.error(f"❌ Error exportar: {str(e)}")
        return jsonify({"success": False, "message": str(e)}), 500


# ============================================
# 20. PLANTILLA DE IMPORTACIÓN
# ============================================

@catalogo_api_bp.route('/productos/plantilla', methods=['GET', 'OPTIONS'])
@cross_origin(supports_credentials=True)
def descargar_plantilla():
    """
    GET /api/productos/plantilla
    
    Query params:
    - formato: 'csv' | 'json'
    
    Retorna plantilla con ejemplos para importación.
    """
    if request.method == 'OPTIONS':
        return jsonify({"success": True}), 200

    formato = request.args.get('formato', 'csv').lower()
    
    ejemplos = [
        {
            "nombre": "Producto Ejemplo 1",
            "sku": "SKU-001",
            "barcode": "7501234567890",
            "categoria": "Electrónica",
            "precio": "99900",
            "costo": "50000",
            "stock": "25",
            "descripcion": "Descripción del producto"
        },
        {
            "nombre": "Producto Ejemplo 2",
            "sku": "SKU-002",
            "barcode": "7509876543210",
            "categoria": "Ropa",
            "precio": "45000",
            "costo": "20000",
            "stock": "50",
            "descripcion": "Otra descripción"
        }
    ]

    if formato == 'json':
        return jsonify({
            "success": True,
            "plantilla": ejemplos,
            "campos_requeridos": ["nombre"],
            "campos_opcionales": ["sku", "barcode", "categoria", "precio", "costo", "stock", "descripcion"]
        }), 200
    
    else:  # CSV
        import io
        import csv
        
        output = io.StringIO()
        campos = ['nombre', 'sku', 'barcode', 'categoria', 'precio', 'costo', 'stock', 'descripcion']
        writer = csv.DictWriter(output, fieldnames=campos)
        writer.writeheader()
        writer.writerows(ejemplos)
        
        return jsonify({
            "success": True,
            "contenido": output.getvalue(),
            "filename": "plantilla_productos.csv"
        }), 200


# ============================================
# 21. CATÁLOGO PÚBLICO (Sin autenticación)
# ============================================

@catalogo_api_bp.route('/productos/publicos/<int:negocio_id>', methods=['GET', 'OPTIONS'])
@cross_origin(supports_credentials=True)
def catalogo_publico(negocio_id):
    """
    GET /api/productos/publicos/{negocio_id}
    
    Retorna productos activos y publicados de un negocio.
    NO requiere autenticación - para tiendas públicas.
    
    Query params:
    - categoria: filtrar por categoría
    - search: buscar por nombre
    - limit: límite de resultados (default: 50)
    """
    if request.method == 'OPTIONS':
        return jsonify({"success": True}), 200

    try:
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
        
        # Límite
        limit = min(int(request.args.get('limit', 50)), 200)
        
        productos = query.order_by(ProductoCatalogo.nombre.asc()).limit(limit).all()
        
        # Datos públicos (sin costos ni info sensible)
        datos_publicos = []
        for p in productos:
            datos_publicos.append({
                "id": p.id_producto,
                "nombre": p.nombre,
                "descripcion": p.descripcion,
                "precio": p.precio,
                "categoria": p.categoria,
                "imagen_url": p.imagen_url,
                "imagenes": json.loads(p.imagenes) if p.imagenes else [],
                "sku": p.referencia_sku,
                "en_stock": p.stock > 0,
                "disponible": p.stock > 0
            })

        # Obtener categorías disponibles
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
# 22. BUSCAR POR CÓDIGO DE BARRAS
# ============================================

@catalogo_api_bp.route('/producto/buscar-codigo', methods=['GET', 'OPTIONS'])
@cross_origin(supports_credentials=True)
def buscar_por_codigo():
    """
    GET /api/producto/buscar-codigo?codigo={barcode|sku}
    
    Busca producto por código de barras o SKU.
    Útil para escáner de barras.
    """
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
        
        # Buscar por barcode o SKU
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
# 23. BÚSQUEDA GLOBAL DE PRODUCTOS
# ============================================

@catalogo_api_bp.route('/productos/buscar', methods=['GET', 'OPTIONS'])
@cross_origin(supports_credentials=True)
def buscar_productos():
    """
    GET /api/productos/buscar?q={término}
    
    Búsqueda inteligente en nombre, SKU, barcode, categoría y descripción.
    """
    if request.method == 'OPTIONS':
        return jsonify({"success": True}), 200

    user_id = get_authorized_user_id()
    if not user_id:
        return jsonify({"success": False, "message": "No autorizado"}), 401

    try:
        q = request.args.get('q', '').strip()
        
        if len(q) < 2:
            return jsonify({
                "success": True,
                "productos": [],
                "message": "Término muy corto"
            }), 200

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

        resultados = []
        for p in productos:
            resultados.append({
                "id": p.id_producto,
                "nombre": p.nombre,
                "sku": p.referencia_sku,
                "barcode": p.codigo_barras,
                "categoria": p.categoria,
                "precio": p.precio,
                "stock": p.stock,
                "imagen_url": p.imagen_url
            })

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
# 24. AGREGAR VIDEOS/YOUTUBE A PRODUCTO
# ============================================

@catalogo_api_bp.route('/producto/<int:id_producto>/videos', methods=['POST', 'OPTIONS'])
@cross_origin(supports_credentials=True)
def agregar_video(id_producto):
    """
    POST /api/producto/{id}/videos
    
    Body JSON:
    - url: URL de YouTube
    - title: título opcional
    
    O array de videos:
    - videos: [{url, title}, ...]
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

        data = request.get_json()
        
        # Cargar videos actuales
        videos_actuales = []
        if producto.videos:
            try:
                videos_actuales = json.loads(producto.videos) if isinstance(producto.videos, str) else producto.videos
            except:
                videos_actuales = []

        # Helper para extraer YouTube ID
        def extraer_youtube_id(url):
            import re
            patterns = [
                r'(?:youtube\.com\/watch\?v=|youtu\.be\/|youtube\.com\/embed\/)([^&\s?]+)',
                r'youtube\.com\/shorts\/([^&\s?]+)'
            ]
            for pattern in patterns:
                match = re.search(pattern, url)
                if match:
                    return match.group(1)
            return None

        # Procesar nuevos videos
        nuevos_videos = []
        
        if 'videos' in data:
            # Array de videos
            for v in data['videos']:
                url = v.get('url', '')
                video_id = extraer_youtube_id(url)
                if video_id:
                    nuevos_videos.append({
                        "url": url,
                        "videoId": video_id,
                        "title": v.get('title', f'Video {len(videos_actuales) + len(nuevos_videos) + 1}'),
                        "thumbnail": f"https://img.youtube.com/vi/{video_id}/mqdefault.jpg"
                    })
        elif 'url' in data:
            # Video individual
            url = data['url']
            video_id = extraer_youtube_id(url)
            if video_id:
                nuevos_videos.append({
                    "url": url,
                    "videoId": video_id,
                    "title": data.get('title', f'Video {len(videos_actuales) + 1}'),
                    "thumbnail": f"https://img.youtube.com/vi/{video_id}/mqdefault.jpg"
                })

        if not nuevos_videos:
            return jsonify({"success": False, "message": "URL de YouTube no válida"}), 400

        # Verificar duplicados
        ids_existentes = {v.get('videoId') for v in videos_actuales}
        videos_unicos = [v for v in nuevos_videos if v['videoId'] not in ids_existentes]

        if not videos_unicos:
            return jsonify({"success": False, "message": "Videos ya agregados"}), 400

        # Combinar y guardar (máximo 10 videos)
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
# 25. ELIMINAR VIDEO DE PRODUCTO
# ============================================

@catalogo_api_bp.route('/producto/<int:id_producto>/videos/<int:index>', methods=['DELETE', 'OPTIONS'])
@cross_origin(supports_credentials=True)
def eliminar_video(id_producto, index):
    """
    DELETE /api/producto/{id}/videos/{index}
    
    Elimina un video por su índice en el array.
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

        videos = json.loads(producto.videos) if producto.videos else []
        
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
# 26. OBTENER PRODUCTO POR ID
# ============================================

@catalogo_api_bp.route('/producto/<int:id_producto>', methods=['GET', 'OPTIONS'])
@cross_origin(supports_credentials=True)
def obtener_producto(id_producto):
    """
    GET /api/producto/{id}
    
    Retorna un producto específico con todos sus detalles.
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

        # Construir respuesta completa
        data = producto.to_dict()
        data['id'] = producto.id_producto
        data['sku'] = producto.referencia_sku
        data['barcode'] = producto.codigo_barras
        
        # Parsear JSON fields
        data['imagenes'] = json.loads(producto.imagenes) if producto.imagenes and isinstance(producto.imagenes, str) else (producto.imagenes or [])
        data['videos'] = json.loads(producto.videos) if producto.videos and isinstance(producto.videos, str) else (producto.videos or [])
        data['youtube_links'] = data['videos']  # Alias para compatibilidad JS
        data['etiquetas'] = json.loads(producto.etiquetas) if producto.etiquetas and isinstance(producto.etiquetas, str) else (producto.etiquetas or [])

        # Obtener movimientos recientes si existe la tabla
        try:
            from src.models.colombia_data.contabilidad.operaciones_y_catalogo import MovimientoStock
            
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
# 27. ACTUALIZACIÓN MASIVA DE PRECIOS
# ============================================

@catalogo_api_bp.route('/productos/actualizar-precios', methods=['POST', 'OPTIONS'])
@cross_origin(supports_credentials=True)
def actualizar_precios_masivo():
    """
    POST /api/productos/actualizar-precios
    
    Body JSON:
    - tipo: 'porcentaje' | 'valor_fijo'
    - operacion: 'aumentar' | 'disminuir'
    - valor: número
    - categoria: filtrar por categoría (opcional)
    - productos: [ids] lista específica (opcional)
    """
    if request.method == 'OPTIONS':
        return jsonify({"success": True}), 200

    user_id = get_authorized_user_id()
    if not user_id:
        return jsonify({"success": False, "message": "No autorizado"}), 401

    try:
        data = request.get_json()
        
        tipo = data.get('tipo', 'porcentaje')  # porcentaje | valor_fijo
        operacion = data.get('operacion', 'aumentar')  # aumentar | disminuir
        valor = float(data.get('valor', 0))
        categoria = data.get('categoria')
        ids_especificos = data.get('productos', [])
        
        if valor <= 0:
            return jsonify({"success": False, "message": "El valor debe ser mayor a 0"}), 400

        ctx = get_biz_context()
        
        # Query base
        query = ProductoCatalogo.query.filter_by(usuario_id=int(user_id))
        
        if ctx['negocio_id']:
            query = query.filter_by(negocio_id=ctx['negocio_id'])
        
        if categoria:
            query = query.filter_by(categoria=categoria)
        
        if ids_especificos:
            query = query.filter(ProductoCatalogo.id_producto.in_(ids_especificos))
        
        productos = query.all()
        
        if not productos:
            return jsonify({"success": False, "message": "No hay productos para actualizar"}), 404

        actualizados = 0
        cambios = []
        
        for p in productos:
            precio_anterior = p.precio
            
            if tipo == 'porcentaje':
                factor = valor / 100
                cambio = p.precio * factor
            else:  # valor_fijo
                cambio = valor
            
            if operacion == 'aumentar':
                p.precio = round(p.precio + cambio, 2)
            else:
                p.precio = max(0, round(p.precio - cambio, 2))
            
            cambios.append({
                "id": p.id_producto,
                "nombre": p.nombre,
                "precio_anterior": precio_anterior,
                "precio_nuevo": p.precio
            })
            actualizados += 1

        db.session.commit()

        logger.info(f"💰 Precios actualizados: {actualizados} productos ({operacion} {valor}{'%' if tipo == 'porcentaje' else ''})")

        return jsonify({
            "success": True,
            "message": f"{actualizados} precios actualizados",
            "actualizados": actualizados,
            "tipo": tipo,
            "operacion": operacion,
            "valor": valor,
            "cambios": cambios[:50]  # Limitar respuesta
        }), 200

    except Exception as e:
        db.session.rollback()
        logger.error(f"❌ Error actualizar precios: {str(e)}")
        return jsonify({"success": False, "message": str(e)}), 500


# ============================================
# 28. ACTUALIZACIÓN MASIVA DE STOCK
# ============================================

@catalogo_api_bp.route('/productos/actualizar-stock', methods=['POST', 'OPTIONS'])
@cross_origin(supports_credentials=True)
def actualizar_stock_masivo():
    """
    POST /api/productos/actualizar-stock
    
    Body JSON:
    - productos: [{id, stock}, {id, stock}, ...]
    
    O para ajuste global:
    - tipo: 'entrada' | 'salida' | 'establecer'
    - cantidad: número
    - categoria: filtrar (opcional)
    """
    if request.method == 'OPTIONS':
        return jsonify({"success": True}), 200

    user_id = get_authorized_user_id()
    if not user_id:
        return jsonify({"success": False, "message": "No autorizado"}), 401

    try:
        data = request.get_json()
        ctx = get_biz_context()
        
        actualizados = 0
        cambios = []

        # Modo 1: Lista específica de productos
        if 'productos' in data:
            for item in data['productos']:
                prod_id = item.get('id')
                nuevo_stock = int(item.get('stock', 0))
                
                producto = ProductoCatalogo.query.filter_by(
                    id_producto=prod_id,
                    usuario_id=int(user_id)
                ).first()
                
                if producto:
                    stock_anterior = producto.stock
                    producto.stock = max(0, nuevo_stock)
                    
                    cambios.append({
                        "id": producto.id_producto,
                        "nombre": producto.nombre,
                        "stock_anterior": stock_anterior,
                        "stock_nuevo": producto.stock
                    })
                    actualizados += 1

        # Modo 2: Ajuste global
        elif 'tipo' in data:
            tipo = data.get('tipo')
            cantidad = int(data.get('cantidad', 0))
            categoria = data.get('categoria')
            
            query = ProductoCatalogo.query.filter_by(usuario_id=int(user_id))
            
            if ctx['negocio_id']:
                query = query.filter_by(negocio_id=ctx['negocio_id'])
            
            if categoria:
                query = query.filter_by(categoria=categoria)
            
            productos = query.all()
            
            for p in productos:
                stock_anterior = p.stock
                
                if tipo == 'entrada':
                    p.stock += cantidad
                elif tipo == 'salida':
                    p.stock = max(0, p.stock - cantidad)
                elif tipo == 'establecer':
                    p.stock = cantidad
                
                cambios.append({
                    "id": p.id_producto,
                    "nombre": p.nombre,
                    "stock_anterior": stock_anterior,
                    "stock_nuevo": p.stock
                })
                actualizados += 1
        
        else:
            return jsonify({"success": False, "message": "Formato inválido"}), 400

        db.session.commit()

        logger.info(f"📦 Stock masivo: {actualizados} productos actualizados")

        return jsonify({
            "success": True,
            "message": f"{actualizados} productos actualizados",
            "actualizados": actualizados,
            "cambios": cambios[:50]
        }), 200

    except Exception as e:
        db.session.rollback()
        logger.error(f"❌ Error stock masivo: {str(e)}")
        return jsonify({"success": False, "message": str(e)}), 500


# ============================================
# 29. DASHBOARD / RESUMEN INVENTARIO
# ============================================

@catalogo_api_bp.route('/inventario/dashboard', methods=['GET', 'OPTIONS'])
@cross_origin(supports_credentials=True)
def dashboard_inventario():
    """
    GET /api/inventario/dashboard
    
    Retorna resumen completo para el dashboard:
    - Estadísticas generales
    - Top productos
    - Alertas de stock
    - Movimientos recientes
    - Distribución por categoría
    """
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
        
        # ========== ESTADÍSTICAS GENERALES ==========
        total = len(productos)
        activos = len([p for p in productos if p.activo])
        en_stock = len([p for p in productos if p.stock > p.stock_bajo])
        stock_bajo = len([p for p in productos if 0 < p.stock <= p.stock_bajo])
        stock_critico = len([p for p in productos if 0 < p.stock <= p.stock_critico])
        sin_stock = len([p for p in productos if p.stock == 0])
        
        valor_inventario = sum((p.precio * p.stock) for p in productos)
        costo_inventario = sum((p.costo * p.stock) for p in productos)
        unidades_totales = sum(p.stock for p in productos)
        
        # ========== PRODUCTOS CON MAYOR VALOR ==========
        top_valor = sorted(productos, key=lambda p: p.precio * p.stock, reverse=True)[:5]
        top_valor_data = [{
            "id": p.id_producto,
            "nombre": p.nombre,
            "precio": p.precio,
            "stock": p.stock,
            "valor": p.precio * p.stock,
            "imagen_url": p.imagen_url
        } for p in top_valor]
        
        # ========== PRODUCTOS CON MAYOR STOCK ==========
        top_stock = sorted(productos, key=lambda p: p.stock, reverse=True)[:5]
        top_stock_data = [{
            "id": p.id_producto,
            "nombre": p.nombre,
            "stock": p.stock,
            "imagen_url": p.imagen_url
        } for p in top_stock]
        
        # ========== ALERTAS ==========
        alertas = []
        for p in productos:
            if p.stock == 0:
                alertas.append({
                    "id": p.id_producto,
                    "nombre": p.nombre,
                    "tipo": "critical",
                    "mensaje": "Sin stock",
                    "stock": 0
                })
            elif p.stock <= p.stock_critico:
                alertas.append({
                    "id": p.id_producto,
                    "nombre": p.nombre,
                    "tipo": "critical",
                    "mensaje": f"Stock crítico: {p.stock}",
                    "stock": p.stock
                })
            elif p.stock <= p.stock_bajo:
                alertas.append({
                    "id": p.id_producto,
                    "nombre": p.nombre,
                    "tipo": "warning",
                    "mensaje": f"Stock bajo: {p.stock}",
                    "stock": p.stock
                })
        
        alertas = sorted(alertas, key=lambda a: a['stock'])[:10]
        
        # ========== DISTRIBUCIÓN POR CATEGORÍA ==========
        categorias = {}
        for p in productos:
            cat = p.categoria or 'Sin categoría'
            if cat not in categorias:
                categorias[cat] = {"count": 0, "valor": 0, "unidades": 0}
            categorias[cat]["count"] += 1
            categorias[cat]["valor"] += p.precio * p.stock
            categorias[cat]["unidades"] += p.stock
        
        distribucion = [
            {"categoria": k, **v} 
            for k, v in sorted(categorias.items(), key=lambda x: x[1]["count"], reverse=True)
        ]
        
        # ========== MOVIMIENTOS RECIENTES ==========
        movimientos_recientes = []
        try:
            from src.models.colombia_data.contabilidad.operaciones_y_catalogo import MovimientoStock
            
            movs = MovimientoStock.query.filter_by(
                usuario_id=int(user_id)
            ).order_by(MovimientoStock.fecha.desc()).limit(10).all()
            
            for m in movs:
                producto = ProductoCatalogo.query.get(m.producto_id)
                movimientos_recientes.append({
                    "id": m.id_movimiento,
                    "producto_id": m.producto_id,
                    "producto_nombre": producto.nombre if producto else "Eliminado",
                    "tipo": m.tipo,
                    "cantidad": m.cantidad,
                    "fecha": m.fecha.isoformat() if m.fecha else None
                })
        except:
            pass

        return jsonify({
            "success": True,
            "fecha_consulta": datetime.utcnow().isoformat(),
            "context": ctx,
            
            "estadisticas": {
                "total_productos": total,
                "productos_activos": activos,
                "en_stock": en_stock,
                "stock_bajo": stock_bajo,
                "stock_critico": stock_critico,
                "sin_stock": sin_stock,
                "unidades_totales": unidades_totales,
                "valor_inventario": round(valor_inventario, 2),
                "costo_inventario": round(costo_inventario, 2),
                "ganancia_potencial": round(valor_inventario - costo_inventario, 2)
            },
            
            "top_valor": top_valor_data,
            "top_stock": top_stock_data,
            
            "alertas": {
                "total": len(alertas),
                "criticas": len([a for a in alertas if a['tipo'] == 'critical']),
                "advertencias": len([a for a in alertas if a['tipo'] == 'warning']),
                "lista": alertas
            },
            
            "distribucion_categorias": distribucion,
            "movimientos_recientes": movimientos_recientes
            
        }), 200

    except Exception as e:
        logger.error(f"❌ Error dashboard: {traceback.format_exc()}")
        return jsonify({"success": False, "message": str(e)}), 500


# ============================================
# 30. ACTIVAR/DESACTIVAR PRODUCTO
# ============================================

@catalogo_api_bp.route('/producto/<int:id_producto>/toggle-activo', methods=['POST', 'PATCH', 'OPTIONS'])
@cross_origin(supports_credentials=True)
def toggle_activo(id_producto):
    """
    POST/PATCH /api/producto/{id}/toggle-activo
    
    Alterna el estado activo del producto.
    Body opcional: { "activo": true/false }
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
    
    
