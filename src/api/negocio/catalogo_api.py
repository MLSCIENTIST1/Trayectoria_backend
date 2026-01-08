import cloudinary
import cloudinary.uploader
import logging
import traceback
import sys
from flask import Blueprint, request, jsonify
from flask_cors import cross_origin
from src.models.database import db
from src.models.colombia_data.catalogo.catalogo import ProductoCatalogo
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
        # Filtramos por el ID obtenido (sea de sesión o header)
        productos = ProductoCatalogo.query.filter_by(usuario_id=user_id).all()
        catalogo_data = [p.to_dict() for p in productos]
        
        return jsonify({
            "success": True,
            "data": catalogo_data
        }), 200
    except Exception as e:
        logger.error(f"❌ Error: {str(e)}")
        return jsonify({"success": False, "message": "Error al cargar catálogo"}), 500

# --- 2. RUTA PARA GUARDAR PRODUCTO ---
import re
import traceback
from flask import request, jsonify
from flask_cors import cross_origin

@catalogo_api_bp.route('/producto/guardar', methods=['POST', 'OPTIONS'])
@cross_origin(supports_credentials=True)
def guardar_producto():
    if request.method == 'OPTIONS':
        return jsonify({"success": True}), 200

    user_id = get_authorized_user_id()
    if not user_id:
        return jsonify({"success": False, "message": "No autorizado"}), 401

    try:
        # 1. Obtención de datos básicos
        nombre = request.form.get('nombre', '').strip()
        precio_raw = request.form.get('precio', '0')
        negocio_id = request.form.get('negocio_id')
        sucursal_id = request.form.get('sucursal_id')
        
        if not all([nombre, negocio_id]):
            return jsonify({"success": False, "message": "Nombre y Negocio ID son obligatorios"}), 400

        # 2. Manejo de Imagen con limpieza de public_id
        file = request.files.get('imagen_file')
        imagen_url = "https://res.cloudinary.com/dp50v0bwj/image/upload/v1704285000/default_product.png"

        if file and file.filename and allowed_file(file.filename):
            # LIMPIEZA CRÍTICA: Cloudinary no acepta espacios al final ni caracteres especiales
            # Tomamos los primeros 15 caracteres, quitamos espacios y dejamos solo letras/números
            nombre_limpio = re.sub(r'[^a-zA-Z0-9]', '', nombre[:15])
            p_id = f"prod_{negocio_id}_{user_id}_{nombre_limpio}"

            upload_result = cloudinary.uploader.upload(
                file,
                folder="productos_bizflow",
                public_id=p_id,
                overwrite=True
            )
            imagen_url = upload_result['secure_url']

        # 3. Conversión segura de valores numéricos para Neon DB
        try:
            precio_final = float(precio_raw)
        except ValueError:
            precio_final = 0.0

        try:
            stock_final = int(request.form.get('stock', 0))
        except ValueError:
            stock_final = 0

        # Manejo de sucursal_id (por defecto 1 si no es válido)
        if not sucursal_id or sucursal_id in ['null', 'undefined', '']:
            sucursal_id_final = 1
        else:
            sucursal_id_final = int(sucursal_id)

        # 4. Creación del objeto en la base de datos
        nuevo_producto = ProductoCatalogo(
            nombre=nombre,
            descripcion=request.form.get('descripcion', '').strip(),
            precio=precio_final,
            imagen_url=imagen_url,
            categoria=request.form.get('categoria', 'General').strip(),
            stock=stock_final,
            negocio_id=int(negocio_id),
            sucursal_id=sucursal_id_final,
            usuario_id=user_id,
            activo=True
        )

        db.session.add(nuevo_producto)
        db.session.commit()

        return jsonify({
            "success": True, 
            "id": nuevo_producto.id_producto, 
            "url_foto": imagen_url,
            "message": "Producto guardado con éxito"
        }), 201

    except Exception as e:
        db.session.rollback()
        logger.error(f"FALLO CRÍTICO EN GUARDAR PRODUCTO: {traceback.format_exc()}")
        return jsonify({"success": False, "message": f"Error interno: {str(e)}"}), 500
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