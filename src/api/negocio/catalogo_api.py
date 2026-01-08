import cloudinary
import cloudinary.uploader
import logging
import traceback
import sys
from flask import Blueprint, request, jsonify
from flask_cors import cross_origin
from src.models.database import db
from src.models.colombia_data.catalogo.catalogo import ProductoCatalogo, TransaccionOperativa

from flask_login import current_user

# --- CONFIGURACIÓN DE LOGS ---
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
if not logger.handlers:
    handler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter('\033[92m%(asctime)s\033[0m - \033[94m%(name)s\033[0m - \033[93m%(levelname)s\033[0m - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

# CONFIGURACIÓN DE CLOUDINARY
cloudinary.config(
    cloud_name="dp50v0bwj",
    api_key="966788685877863",
    api_secret="O6kBEBo3svgWozvn_dyw2J1CtBE",
    secure=True
)

catalogo_api_bp = Blueprint('catalogo_service', __name__)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# FUNCIÓN DE VALIDACIÓN HÍBRIDA (Cookie o Header)
def get_authorized_user_id():
    if current_user.is_authenticated:
        return current_user.id_usuario
    return request.headers.get('X-User-ID')

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
        return jsonify({"success": False, "message": "No autorizado. Falta X-User-ID"}), 401

    logger.info(f"🛰️ Solicitud de catálogo para User-ID: {user_id}")
    try:
        # Filtramos por el ID obtenido
        productos = ProductoCatalogo.query.filter_by(usuario_id=int(user_id)).all()
        catalogo_data = [p.to_dict() for p in productos]
        
        return jsonify({
            "success": True,
            "data": catalogo_data
        }), 200
    except Exception as e:
        logger.error(f"❌ Error en GET mis-productos: {str(e)}")
        return jsonify({"success": False, "message": "Error al cargar catálogo"}), 500

# --- RUTA 2: GUARDAR PRODUCTO (CON CLOUDINARY) ---
@catalogo_api_bp.route('/catalogo/producto/guardar', methods=['POST', 'OPTIONS'])
@cross_origin(supports_credentials=True)
def guardar_producto_catalogo():
    if request.method == 'OPTIONS':
        return jsonify({"success": True}), 200

    user_id = get_authorized_user_id()
    if not user_id:
        return jsonify({"success": False, "message": "No autorizado"}), 401

    try:
        # Detectar si viene como FormData (con imagen) o JSON
        is_form = 'multipart/form-data' in (request.content_type or '')
        data = request.form if is_form else (request.get_json(silent=True) or {})
        
        # 1. Procesamiento de Imagen en Cloudinary
        imagen_url = data.get('imagen_url') 
        file = request.files.get('imagen') # 'imagen' coincide con el append de JS
        
        if file and file.filename != '':
            nombre_prod = data.get('nombre', 'producto')
            nombre_limpio = re.sub(r'[^a-zA-Z0-9]', '', nombre_prod[:15])
            p_id = f"inv_{user_id}_{nombre_limpio}"
            
            upload_result = cloudinary.uploader.upload(
                file,
                folder="productos_bizflow",
                public_id=p_id,
                overwrite=True
            )
            imagen_url = upload_result.get('secure_url')
# --- 2. RUTA PARA GUARDAR PRODUCTO ---
import re
import traceback
from flask import request, jsonify
from flask_cors import cross_origin

@catalogo_api_bp.route('/catalogo/producto/guardar', methods=['POST', 'OPTIONS'])
@cross_origin(supports_credentials=True)
def guardar_producto_catalogo():
    if request.method == 'OPTIONS':
        return jsonify({"success": True}), 200

    # Identificación de usuario desde el Header X-User-ID
    user_id = request.headers.get('X-User-ID')
    if not user_id:
        return jsonify({"success": False, "message": "No autorizado"}), 401

    try:
        # Detectar si es formulario (con imagen) o JSON
        is_form = 'multipart/form-data' in (request.content_type or '')
        data = request.form if is_form else (request.get_json(silent=True) or {})
        
        # 1. PROCESAMIENTO DE IMAGEN (CLOUDINARY)
        imagen_url = data.get('imagen_url') 
        file = request.files.get('imagen') or request.files.get('imagen_file')
        
        if file and file.filename != '':
            # Generar ID único para la imagen basado en el nombre del producto
            nombre_prod = data.get('nombre', 'producto')
            nombre_limpio = re.sub(r'[^a-zA-Z0-9]', '', nombre_prod[:15])
            p_id = f"inv_{user_id}_{nombre_limpio}"
            
            upload_result = cloudinary.uploader.upload(
                file,
                folder="productos_bizflow",
                public_id=p_id,
                overwrite=True,
                resource_type="auto"
            )
            imagen_url = upload_result.get('secure_url')

        # 2. REGISTRO CONTABLE (Crea una transacción inicial por la creación/ajuste)
        monto_f = float(data.get('precio', 0))
        nueva_t = TransaccionOperativa(
            negocio_id=int(data.get('negocio_id', 1)),
            usuario_id=int(user_id),
            sucursal_id=int(data.get('sucursal_id', 1)),
            tipo='INGRESO', # Se registra como ingreso de inventario
            monto=monto_f,
            concepto=f"Registro Catálogo: {data.get('nombre')}",
            categoria=data.get('categoria', 'General'),
            metodo_pago='N/A'
        )
        db.session.add(nueva_t)

        # 3. SINCRONIZACIÓN NEON DB (ProductoCatalogo)
        nombre_p = data.get('nombre')
        neg_id = int(data.get('negocio_id', 1))
        
        prod = ProductoCatalogo.query.filter_by(nombre=nombre_p, negocio_id=neg_id).first()

        if prod:
            # Actualizar producto existente
            if imagen_url: prod.imagen_url = imagen_url
            prod.costo = float(data.get('costo', 0))
            prod.precio = float(data.get('precio', 0))
            prod.stock = int(data.get('stock', 0))
            prod.categoria = data.get('categoria', 'General')
        else:
            # Crear producto nuevo
            nuevo_prod = ProductoCatalogo(
                nombre=nombre_p,
                negocio_id=neg_id,
                usuario_id=int(user_id),
                sucursal_id=int(data.get('sucursal_id', 1)),
                categoria=data.get('categoria', 'General'),
                costo=float(data.get('costo', 0)),
                precio=float(data.get('precio', 0)),
                stock=int(data.get('stock', 0)),
                imagen_url=imagen_url or "https://res.cloudinary.com/dp50v0bwj/image/upload/v1704285000/default_product.png",
                activo=True
            )
            db.session.add(nuevo_prod)

        db.session.commit()
        return jsonify({
            "success": True, 
            "message": "Producto guardado con éxito", 
            "url": imagen_url
        }), 201

    except Exception as e:
        db.session.rollback()
        print(f"❌ Error en Catálogo: {traceback.format_exc()}")
        return jsonify({"success": False, "message": str(e)}), 500
# --- 3. RUTA ELIMINAR ---
@catalogo_api_bp.route('/producto/eliminar/<int:id_producto>', methods=['DELETE', 'OPTIONS'])
@cross_origin(supports_credentials=True)
def eliminar_producto(id_producto):
    if request.method == 'OPTIONS': return jsonify({"success": True}), 200
    
    user_id = get_authorized_user_id()
    try:
        prod = ProductoCatalogo.query.filter_by(id_producto=id_producto, usuario_id=user_id).first()
        if not prod:
            return jsonify({"success": False, "message": "No encontrado"}), 404
        
        db.session.delete(prod)
        db.session.commit()
        return jsonify({"success": True}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "message": str(e)}), 500
    
    # --- 3. RUTA CATÁLOGO PÚBLICO (MODIFICADA) ---
# Cambiamos '/publico/' por '/productos/publicos/' para que coincida con el JS
@catalogo_api_bp.route('/productos/publicos/<int:negocio_id>', methods=['GET', 'OPTIONS'])
@cross_origin(supports_credentials=True)
def obtener_catalogo_publico(negocio_id):
    if request.method == 'OPTIONS': 
        return jsonify({"success": True}), 200
    try:
        # Filtramos por negocio y que el producto esté activo
        productos = ProductoCatalogo.query.filter_by(negocio_id=negocio_id, activo=True).all()
        
        # IMPORTANTE: Devolvemos el objeto con success y data para que el JS no falle
        return jsonify({
            "success": True,
            "data": [p.to_dict() for p in productos]
        }), 200
    except Exception as e:
        logger.error(f"Error en catálogo público: {str(e)}")
        return jsonify({"success": False, "message": str(e)}), 500