import cloudinary
import cloudinary.uploader
import logging
import traceback
import sys
from flask import Blueprint, request, jsonify
from flask_cors import cross_origin
from src.models.database import db
from src.models.colombia_data.catalogo.catalogo import ProductoCatalogo
from flask_login import login_required, current_user

# --- CONFIGURACIÓN DE LOGS DE ALTA VISIBILIDAD ---
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
if not logger.handlers:
    handler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter('\033[92m%(asctime)s\033[0m - \033[94m%(name)s\033[0m - \033[93m%(levelname)s\033[0m - \033[96m%(funcName)s:%(lineno)d\033[0m - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

# CONFIGURACIÓN DE CLOUDINARY
cloudinary.config(
    cloud_name="dp50v0bwj",
    api_key="966788685877863",
    api_secret="O6kBEBo3svgWozvn_dyw2J1CtBE",
    secure=True
)

# Definimos el Blueprint. El prefijo '/api' se gestiona en register_api.py
catalogo_api_bp = Blueprint('catalogo_service', __name__)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@catalogo_api_bp.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "online", "module": "catalogo"}), 200

# --- 1. RUTA PARA OBTENER EL CATÁLOGO PRIVADO (EL "INYECTOR") ---
# URL Final: /api/mis-productos
@catalogo_api_bp.route('/mis-productos', methods=['GET', 'OPTIONS'])
@cross_origin(supports_credentials=True)
@login_required
def obtener_mis_productos():
    if request.method == 'OPTIONS':
        return jsonify({"success": True}), 200

    logger.info(f"🛰️ Solicitud de catálogo privado para usuario ID: {current_user.id_usuario}")
    try:
        productos = ProductoCatalogo.query.filter_by(usuario_id=current_user.id_usuario).all()
        catalogo_data = [p.to_dict() for p in productos]
        
        logger.info(f"✅ Se enviaron {len(catalogo_data)} productos.")
        return jsonify({
            "success": True,
            "data": catalogo_data
        }), 200
    except Exception as e:
        logger.error(f"❌ Error al obtener productos: {str(e)}")
        return jsonify({"success": False, "message": "No se pudo cargar el catálogo"}), 500

# --- 2. RUTA PARA GUARDAR PRODUCTO ---
# URL Final: /api/producto/guardar
@catalogo_api_bp.route('/producto/guardar', methods=['POST', 'OPTIONS'])
@cross_origin(supports_credentials=True)
@login_required
def guardar_producto():
    if request.method == 'OPTIONS':
        return jsonify({"success": True}), 200

    logger.info("==== INICIO PROCESO GUARDAR_PRODUCTO ====")
    try:
        # 1. Extracción de datos
        nombre = request.form.get('nombre')
        precio = request.form.get('precio')
        negocio_id = request.form.get('negocio_id')
        sucursal_id = request.form.get('sucursal_id')
        descripcion = request.form.get('descripcion', '')
        categoria = request.form.get('categoria', 'General')
        stock = request.form.get('stock', 0)

        # 2. Validación
        if not all([nombre, precio, negocio_id]):
            return jsonify({"success": False, "message": "Faltan datos obligatorios"}), 400

        # 3. Imagen
        file = request.files.get('imagen_file')
        imagen_url = "https://res.cloudinary.com/dp50v0bwj/image/upload/v1704285000/default_product.png"

        if file and file.filename and allowed_file(file.filename):
            upload_result = cloudinary.uploader.upload(
                file,
                folder="productos_bizflow",
                public_id=f"prod_{negocio_id}_{current_user.id_usuario}_{nombre[:10]}"
            )
            imagen_url = upload_result['secure_url']

        # 4. Creación
        nuevo_producto = ProductoCatalogo(
            nombre=nombre,
            descripcion=descripcion,
            precio=float(precio),
            imagen_url=imagen_url,
            categoria=categoria,
            stock=int(stock),
            negocio_id=int(negocio_id),
            sucursal_id=int(sucursal_id) if (sucursal_id and sucursal_id != 'null') else None,
            usuario_id=current_user.id_usuario,
            activo=True
        )

        db.session.add(nuevo_producto)
        db.session.commit()

        logger.info("==== PRODUCTO GUARDADO CON ÉXITO ====")
        return jsonify({
            "success": True,
            "message": "Producto guardado",
            "id": nuevo_producto.id_producto,
            "url_foto": imagen_url
        }), 201

    except Exception as e:
        db.session.rollback()
        logger.error(f"FALLO: {traceback.format_exc()}")
        return jsonify({"success": False, "message": str(e)}), 500

# --- 3. RUTA CATÁLOGO PÚBLICO ---
# URL Final: /api/publico/<negocio_id>
@catalogo_api_bp.route('/publico/<int:negocio_id>', methods=['GET', 'OPTIONS'])
@cross_origin(supports_credentials=True)
def obtener_catalogo_publico(negocio_id):
    if request.method == 'OPTIONS': return jsonify({"success": True}), 200
    try:
        productos = ProductoCatalogo.query.filter_by(negocio_id=negocio_id, activo=True).all()
        return jsonify([p.to_dict() for p in productos]), 200
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

# --- 4. RUTA ELIMINAR ---
# URL Final: /api/producto/eliminar/<id_producto>
@catalogo_api_bp.route('/producto/eliminar/<int:id_producto>', methods=['DELETE', 'OPTIONS'])
@cross_origin(supports_credentials=True)
@login_required
def eliminar_producto(id_producto):
    if request.method == 'OPTIONS': return jsonify({"success": True}), 200
    try:
        prod = ProductoCatalogo.query.filter_by(id_producto=id_producto, usuario_id=current_user.id_usuario).first()
        if not prod:
            return jsonify({"success": False, "message": "Producto no encontrado o permisos insuficientes"}), 404
        db.session.delete(prod)
        db.session.commit()
        return jsonify({"success": True, "message": "Producto eliminado exitosamente"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "message": str(e)}), 500import cloudinary
import cloudinary.uploader
import logging
import traceback
import sys
from flask import Blueprint, request, jsonify
from flask_cors import cross_origin
from src.models.database import db
from src.models.colombia_data.catalogo.catalogo import ProductoCatalogo
from flask_login import login_required, current_user

# --- CONFIGURACIÓN DE LOGS DE ALTA VISIBILIDAD ---
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
if not logger.handlers:
    handler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter('\033[92m%(asctime)s\033[0m - \033[94m%(name)s\033[0m - \033[93m%(levelname)s\033[0m - \033[96m%(funcName)s:%(lineno)d\033[0m - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

# CONFIGURACIÓN DE CLOUDINARY
cloudinary.config(
    cloud_name="dp50v0bwj",
    api_key="966788685877863",
    api_secret="O6kBEBo3svgWozvn_dyw2J1CtBE",
    secure=True
)

# Definimos el Blueprint. El prefijo '/api' se gestiona en register_api.py
catalogo_api_bp = Blueprint('catalogo_service', __name__)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@catalogo_api_bp.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "online", "module": "catalogo"}), 200

# --- 1. RUTA PARA OBTENER EL CATÁLOGO PRIVADO (EL "INYECTOR") ---
# URL Final: /api/mis-productos
@catalogo_api_bp.route('/mis-productos', methods=['GET', 'OPTIONS'])
@cross_origin(supports_credentials=True)
@login_required
def obtener_mis_productos():
    if request.method == 'OPTIONS':
        return jsonify({"success": True}), 200

    logger.info(f"🛰️ Solicitud de catálogo privado para usuario ID: {current_user.id_usuario}")
    try:
        productos = ProductoCatalogo.query.filter_by(usuario_id=current_user.id_usuario).all()
        catalogo_data = [p.to_dict() for p in productos]
        
        logger.info(f"✅ Se enviaron {len(catalogo_data)} productos.")
        return jsonify({
            "success": True,
            "data": catalogo_data
        }), 200
    except Exception as e:
        logger.error(f"❌ Error al obtener productos: {str(e)}")
        return jsonify({"success": False, "message": "No se pudo cargar el catálogo"}), 500

# --- 2. RUTA PARA GUARDAR PRODUCTO ---
# URL Final: /api/producto/guardar
@catalogo_api_bp.route('/producto/guardar', methods=['POST', 'OPTIONS'])
@cross_origin(supports_credentials=True)
@login_required
def guardar_producto():
    if request.method == 'OPTIONS':
        return jsonify({"success": True}), 200

    logger.info("==== INICIO PROCESO GUARDAR_PRODUCTO ====")
    try:
        # 1. Extracción de datos
        nombre = request.form.get('nombre')
        precio = request.form.get('precio')
        negocio_id = request.form.get('negocio_id')
        sucursal_id = request.form.get('sucursal_id')
        descripcion = request.form.get('descripcion', '')
        categoria = request.form.get('categoria', 'General')
        stock = request.form.get('stock', 0)

        # 2. Validación
        if not all([nombre, precio, negocio_id]):
            return jsonify({"success": False, "message": "Faltan datos obligatorios"}), 400

        # 3. Imagen
        file = request.files.get('imagen_file')
        imagen_url = "https://res.cloudinary.com/dp50v0bwj/image/upload/v1704285000/default_product.png"

        if file and file.filename and allowed_file(file.filename):
            upload_result = cloudinary.uploader.upload(
                file,
                folder="productos_bizflow",
                public_id=f"prod_{negocio_id}_{current_user.id_usuario}_{nombre[:10]}"
            )
            imagen_url = upload_result['secure_url']

        # 4. Creación
        nuevo_producto = ProductoCatalogo(
            nombre=nombre,
            descripcion=descripcion,
            precio=float(precio),
            imagen_url=imagen_url,
            categoria=categoria,
            stock=int(stock),
            negocio_id=int(negocio_id),
            sucursal_id=int(sucursal_id) if (sucursal_id and sucursal_id != 'null') else None,
            usuario_id=current_user.id_usuario,
            activo=True
        )

        db.session.add(nuevo_producto)
        db.session.commit()

        logger.info("==== PRODUCTO GUARDADO CON ÉXITO ====")
        return jsonify({
            "success": True,
            "message": "Producto guardado",
            "id": nuevo_producto.id_producto,
            "url_foto": imagen_url
        }), 201

    except Exception as e:
        db.session.rollback()
        logger.error(f"FALLO: {traceback.format_exc()}")
        return jsonify({"success": False, "message": str(e)}), 500

# --- 3. RUTA CATÁLOGO PÚBLICO ---
# URL Final: /api/publico/<negocio_id>
@catalogo_api_bp.route('/publico/<int:negocio_id>', methods=['GET', 'OPTIONS'])
@cross_origin(supports_credentials=True)
def obtener_catalogo_publico(negocio_id):
    if request.method == 'OPTIONS': return jsonify({"success": True}), 200
    try:
        productos = ProductoCatalogo.query.filter_by(negocio_id=negocio_id, activo=True).all()
        return jsonify([p.to_dict() for p in productos]), 200
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

# --- 4. RUTA ELIMINAR ---
# URL Final: /api/producto/eliminar/<id_producto>
@catalogo_api_bp.route('/producto/eliminar/<int:id_producto>', methods=['DELETE', 'OPTIONS'])
@cross_origin(supports_credentials=True)
@login_required
def eliminar_producto(id_producto):
    if request.method == 'OPTIONS': return jsonify({"success": True}), 200
    try:
        prod = ProductoCatalogo.query.filter_by(id_producto=id_producto, usuario_id=current_user.id_usuario).first()
        if not prod:
            return jsonify({"success": False, "message": "Producto no encontrado o permisos insuficientes"}), 404
        db.session.delete(prod)
        db.session.commit()
        return jsonify({"success": True, "message": "Producto eliminado exitosamente"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "message": str(e)}), 500