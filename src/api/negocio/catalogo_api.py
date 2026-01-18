import cloudinary
import cloudinary.uploader
import logging
import traceback
import sys
import re
import time
from flask import Blueprint, request, jsonify, session
from flask_cors import cross_origin
from flask_login import current_user, logout_user

# Importaciones de modelos y base de datos
from src.models.database import db
# CORREGIDO: Import desde la ubicación correcta
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

def get_authorized_user_id():
    """
    VALIDADOR CON ESTEROIDES: Prioridad absoluta al Header para evitar 
    fugas de datos por cookies viejas de Chrome.
    """
    header_id = request.headers.get('X-User-ID')
    session_id = None
    
    if current_user.is_authenticated:
        session_id = str(getattr(current_user, 'id_usuario', ''))

    logger.debug(f"🔍 [IDENTIDAD] Header: {header_id} | Sesión: {session_id}")

    if header_id and header_id != session_id:
        logger.warning(f"⚠️ ¡COLISIÓN DETECTADA! Header {header_id} != Sesión {session_id}. Usando Header.")
        return header_id
    
    return header_id or session_id

@catalogo_api_bp.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "online", "module": "catalogo"}), 200

# --- 1. RUTA PARA OBTENER EL CATÁLOGO PRIVADO ---
@catalogo_api_bp.route('/mis-productos', methods=['GET', 'OPTIONS'])
@cross_origin(supports_credentials=True)
def obtener_mis_productos():
    if request.method == 'OPTIONS':
        return jsonify({"success": True}), 200

    user_id = get_authorized_user_id()
    if not user_id:
        logger.error("🚫 Intento de acceso sin ID de usuario.")
        return jsonify({"success": False, "message": "No autorizado"}), 401

    try:
        productos = ProductoCatalogo.query.filter_by(usuario_id=int(user_id)).all()
        
        data_final = []
        for p in productos:
            d = p.to_dict()
            d['id_producto'] = p.id_producto 
            data_final.append(d)

        logger.info(f"✅ Catálogo servido para usuario: {user_id} ({len(data_final)} productos)")
        return jsonify({
            "success": True,
            "data": data_final,
            "debug_user": user_id
        }), 200
    except Exception as e:
        logger.error(f"❌ Error en GET mis-productos: {str(e)}")
        return jsonify({"success": False, "message": str(e)}), 500

# --- 2. RUTA PARA GUARDAR PRODUCTO ---
@catalogo_api_bp.route('/catalogo/producto/guardar', methods=['POST', 'OPTIONS'])
@cross_origin(supports_credentials=True)
def guardar_producto_catalogo():
    if request.method == 'OPTIONS':
        return jsonify({"success": True}), 200

    user_id = get_authorized_user_id()
    if not user_id:
        return jsonify({"success": False, "message": "No autorizado"}), 401

    try:
        is_form = 'multipart/form-data' in (request.content_type or '')
        data = request.form if is_form else (request.get_json(silent=True) or {})
        
        # 1. PROCESAMIENTO DE IMAGEN
        imagen_url = data.get('imagen_url') 
        file = request.files.get('imagen') or request.files.get('imagen_file')
        
        if file and file.filename != '':
            nombre_prod = data.get('nombre', 'producto')
            nombre_limpio = re.sub(r'[^a-zA-Z0-9]', '', nombre_prod[:15])
            # CORREGIDO: Usar time.time() en lugar de db.func.now().cast()
            p_id = f"user_{user_id}_{nombre_limpio}_{int(time.time())}"
            
            upload_result = cloudinary.uploader.upload(
                file,
                folder="productos_bizflow",
                public_id=p_id,
                overwrite=True,
                resource_type="auto"
            )
            imagen_url = upload_result.get('secure_url')

        # 2. REGISTRO CONTABLE
        nueva_t = TransaccionOperativa(
            negocio_id=int(data.get('negocio_id', 1)),
            usuario_id=int(user_id),
            sucursal_id=int(data.get('sucursal_id', 1)),
            tipo='INGRESO', 
            monto=float(data.get('precio', 0)),
            concepto=f"Registro Catálogo: {data.get('nombre')}",
            categoria=data.get('categoria', 'General'),
            metodo_pago='N/A'
        )
        db.session.add(nueva_t)

        # 3. SINCRONIZACIÓN NEON DB
        nombre_p = data.get('nombre')
        neg_id = int(data.get('negocio_id', 1))
        
        prod = ProductoCatalogo.query.filter_by(nombre=nombre_p, negocio_id=neg_id, usuario_id=int(user_id)).first()

        if prod:
            if imagen_url: prod.imagen_url = imagen_url
            prod.costo = float(data.get('costo', 0))
            prod.precio = float(data.get('precio', 0))
            prod.stock = int(data.get('stock', 0))
            prod.categoria = data.get('categoria', 'General')
        else:
            nuevo_prod = ProductoCatalogo(
                nombre=nombre_p,
                negocio_id=neg_id,
                usuario_id=int(user_id),
                sucursal_id=int(data.get('sucursal_id', 1)),
                categoria=data.get('categoria', 'General'),
                costo=float(data.get('costo', 0)),
                precio=float(data.get('precio', 0)),
                stock=int(data.get('stock', 0)),
                imagen_url=imagen_url or "https://via.placeholder.com/150?text=No+Image",
                activo=True
            )
            db.session.add(nuevo_prod)

        db.session.commit()
        return jsonify({"success": True, "message": "Guardado exitoso", "url": imagen_url}), 201

    except Exception as e:
        db.session.rollback()
        logger.error(f"❌ Error en Guardar: {traceback.format_exc()}")
        return jsonify({"success": False, "message": str(e)}), 500

# --- 3. RUTA ELIMINAR ---
@catalogo_api_bp.route('/producto/eliminar/<int:id_producto>', methods=['DELETE', 'OPTIONS'])
@cross_origin(supports_credentials=True)
def eliminar_producto(id_producto):
    if request.method == 'OPTIONS': 
        return jsonify({"success": True}), 200
    
    user_id = get_authorized_user_id()
    if not user_id:
        return jsonify({"success": False, "message": "No autorizado"}), 401

    try:
        prod = ProductoCatalogo.query.filter_by(id_producto=id_producto, usuario_id=int(user_id)).first()
        if not prod:
            return jsonify({"success": False, "message": "Producto no encontrado o no pertenece al usuario"}), 404
        
        db.session.delete(prod)
        db.session.commit()
        return jsonify({"success": True}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "message": str(e)}), 500

# --- 4. RUTA CATÁLOGO PÚBLICO ---
@catalogo_api_bp.route('/productos/publicos/<int:negocio_id>', methods=['GET', 'OPTIONS'])
@cross_origin(supports_credentials=True)
def obtener_catalogo_publico(negocio_id):
    if request.method == 'OPTIONS': 
        return jsonify({"success": True}), 200
    try:
        productos = ProductoCatalogo.query.filter_by(negocio_id=negocio_id, activo=True).all()
        return jsonify({"success": True, "data": [p.to_dict() for p in productos]}), 200
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500
    
# ==========================================
# AGREGAR ESTO A: src/api/negocio/catalogo_api.py
# ==========================================

@catalogo_api_bp.route('/producto/actualizar/<int:id_producto>', methods=['PUT', 'PATCH', 'OPTIONS'])
@cross_origin(supports_credentials=True)
def actualizar_producto(id_producto):
    """
    Actualizar producto existente - Soporta edición parcial
    """
    if request.method == 'OPTIONS':
        return jsonify({"success": True}), 200

    user_id = get_authorized_user_id()
    if not user_id:
        return jsonify({"success": False, "message": "No autorizado"}), 401

    try:
        # Buscar producto
        producto = ProductoCatalogo.query.filter_by(
            id_producto=id_producto,
            usuario_id=int(user_id)
        ).first()
        
        if not producto:
            return jsonify({
                "success": False, 
                "message": "Producto no encontrado"
            }), 404

        # Obtener datos
        is_form = 'multipart/form-data' in (request.content_type or '')
        data = request.form if is_form else (request.get_json(silent=True) or {})

        # Actualizar campos (solo si vienen en el request)
        if 'nombre' in data:
            producto.nombre = data['nombre']
        
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
        
        if 'referencia_sku' in data:
            producto.referencia_sku = data['referencia_sku']
        
        if 'activo' in data:
            producto.activo = data['activo'] in [True, 'true', '1', 1]
        
        if 'plan' in data:
            producto.plan = data['plan']
        
        if 'etiquetas' in data:
            producto.etiquetas = data['etiquetas']
        
        # Manejo de múltiples imágenes
        if 'imagenes' in data:
            # Si viene como JSON array
            producto.imagenes = data['imagenes']
        
        # Subir nueva imagen principal
        file = request.files.get('imagen') or request.files.get('imagen_file')
        if file and file.filename != '':
            nombre_prod = producto.nombre
            nombre_limpio = re.sub(r'[^a-zA-Z0-9]', '', nombre_prod[:15])
            p_id = f"user_{user_id}_{nombre_limpio}_{int(time.time())}"
            
            upload_result = cloudinary.uploader.upload(
                file,
                folder="productos_bizflow",
                public_id=p_id,
                overwrite=True,
                resource_type="auto"
            )
            producto.imagen_url = upload_result.get('secure_url')
        
        # Subir galería de imágenes (múltiples)
        galeria_urls = []
        for i in range(1, 6):  # Soportar hasta 5 imágenes adicionales
            file_key = f'imagen_{i}'
            if file_key in request.files:
                img_file = request.files[file_key]
                if img_file.filename != '':
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
            # Guardar como JSON en campo imagenes
            producto.imagenes = galeria_urls

        db.session.commit()

        logger.info(f"✅ Producto {id_producto} actualizado por usuario {user_id}")

        return jsonify({
            "success": True,
            "message": "Producto actualizado correctamente",
            "producto": producto.to_dict()
        }), 200

    except ValueError as e:
        db.session.rollback()
        logger.error(f"❌ Error de validación: {str(e)}")
        return jsonify({
            "success": False,
            "message": f"Datos inválidos: {str(e)}"
        }), 400
    
    except Exception as e:
        db.session.rollback()
        logger.error(f"❌ Error al actualizar: {traceback.format_exc()}")
        return jsonify({
            "success": False,
            "message": str(e)
        }), 500


# ==========================================
# ENDPOINT: EDICIÓN RÁPIDA (stock, precio)
# ==========================================

@catalogo_api_bp.route('/producto/edicion-rapida/<int:id_producto>', methods=['PATCH', 'OPTIONS'])
@cross_origin(supports_credentials=True)
def edicion_rapida(id_producto):
    """
    Edición ultra-rápida de campos específicos (stock, precio)
    """
    if request.method == 'OPTIONS':
        return jsonify({"success": True}), 200

    user_id = get_authorized_user_id()
    if not user_id:
        return jsonify({"success": False, "message": "No autorizado"}), 401

    try:
        data = request.get_json()
        if not data:
            return jsonify({
                "success": False,
                "message": "No se enviaron datos"
            }), 400

        producto = ProductoCatalogo.query.filter_by(
            id_producto=id_producto,
            usuario_id=int(user_id)
        ).first()
        
        if not producto:
            return jsonify({
                "success": False,
                "message": "Producto no encontrado"
            }), 404

        # Solo actualizar campos enviados
        if 'stock' in data:
            producto.stock = int(data['stock'])
        
        if 'precio' in data:
            producto.precio = float(data['precio'])
        
        if 'costo' in data:
            producto.costo = float(data['costo'])

        db.session.commit()

        return jsonify({
            "success": True,
            "message": "Actualización rápida exitosa",
            "producto": {
                "id": producto.id_producto,
                "stock": producto.stock,
                "precio": producto.precio,
                "costo": producto.costo
            }
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({
            "success": False,
            "message": str(e)
        }), 500


# ==========================================
# ENDPOINT: SUBIR MÚLTIPLES IMÁGENES
# ==========================================

@catalogo_api_bp.route('/producto/<int:id_producto>/imagenes', methods=['POST', 'OPTIONS'])
@cross_origin(supports_credentials=True)
def agregar_imagenes(id_producto):
    """
    Agregar múltiples imágenes a un producto (galería)
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
            return jsonify({
                "success": False,
                "message": "Producto no encontrado"
            }), 404

        galeria_actual = producto.imagenes if producto.imagenes else []
        if isinstance(galeria_actual, str):
            import json
            try:
                galeria_actual = json.loads(galeria_actual)
            except:
                galeria_actual = []

        # Subir nuevas imágenes
        nuevas_urls = []
        for key in request.files:
            file = request.files[key]
            if file.filename != '':
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

        # Combinar con galería existente
        galeria_completa = galeria_actual + nuevas_urls
        
        # Limitar a 10 imágenes máximo
        galeria_completa = galeria_completa[:10]
        
        producto.imagenes = galeria_completa
        db.session.commit()

        return jsonify({
            "success": True,
            "message": f"{len(nuevas_urls)} imágenes agregadas",
            "imagenes": galeria_completa
        }), 201

    except Exception as e:
        db.session.rollback()
        logger.error(f"❌ Error al agregar imágenes: {traceback.format_exc()}")
        return jsonify({
            "success": False,
            "message": str(e)
        }), 500


# ==========================================
# ENDPOINT: DUPLICAR PRODUCTO
# ==========================================

@catalogo_api_bp.route('/producto/duplicar/<int:id_producto>', methods=['POST', 'OPTIONS'])
@cross_origin(supports_credentials=True)
def duplicar_producto(id_producto):
    """
    Duplicar un producto existente
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
            return jsonify({
                "success": False,
                "message": "Producto no encontrado"
            }), 404

        # Crear copia
        duplicado = ProductoCatalogo(
            nombre=f"{original.nombre} (Copia)",
            negocio_id=original.negocio_id,
            usuario_id=int(user_id),
            sucursal_id=original.sucursal_id,
            categoria=original.categoria,
            descripcion=original.descripcion,
            costo=original.costo,
            precio=original.precio,
            stock=0,  # Stock en 0 por seguridad
            imagen_url=original.imagen_url,
            imagenes=original.imagenes,
            referencia_sku=f"{original.referencia_sku}_COPY" if original.referencia_sku else None,
            activo=False,  # Inactivo por defecto
            plan=original.plan
        )
        
        db.session.add(duplicado)
        db.session.commit()

        return jsonify({
            "success": True,
            "message": "Producto duplicado correctamente",
            "producto": duplicado.to_dict()
        }), 201

    except Exception as e:
        db.session.rollback()
        logger.error(f"❌ Error al duplicar: {str(e)}")
        return jsonify({
            "success": False,
            "message": str(e)
        }), 500