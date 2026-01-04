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

# Definimos el Blueprint
catalogo_api_bp = Blueprint('catalogo_service', __name__)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# --- 1. RUTA: OBTENER CATÁLOGO (GET) ---
# Endpoint: /api/mis-productos
@catalogo_api_bp.route('/mis-productos', methods=['GET', 'OPTIONS'])
@cross_origin(supports_credentials=True)
@login_required
def obtener_mis_productos():
    if request.method == 'OPTIONS':
        return jsonify({"success": True}), 200

    try:
        logger.info(f"🛰️ Buscando productos para usuario: {current_user.id_usuario}")
        productos = ProductoCatalogo.query.filter_by(usuario_id=current_user.id_usuario).all()
        # El método .to_dict() debe existir en tu modelo
        catalogo_data = [p.to_dict() for p in productos]
        
        return jsonify({
            "success": True,
            "data": catalogo_data
        }), 200
    except Exception as e:
        logger.error(f"❌ Error en GET /mis-productos: {str(e)}")
        return jsonify({"success": False, "message": "Error interno al cargar catálogo"}), 500

# --- 2. RUTA: GUARDAR PRODUCTO (POST) ---
# Endpoint: /api/producto/guardar
@catalogo_api_bp.route('/producto/guardar', methods=['POST', 'OPTIONS'])
@cross_origin(supports_credentials=True)
@login_required
def guardar_producto():
    if request.method == 'OPTIONS':
        return jsonify({"success": True}), 200

    logger.info("🎬 Iniciando guardado de nuevo producto...")
    try:
        # Extracción de datos (pueden venir por Form o JSON, pero usamos Form por la imagen)
        nombre = request.form.get('nombre')
        precio = request.form.get('precio')
        negocio_id = request.form.get('negocio_id')
        sucursal_id = request.form.get('sucursal_id')
        
        # Validaciones mínimas
        if not nombre or not precio or not negocio_id:
            logger.warning("⚠️ Intento de guardado con datos incompletos")
            return jsonify({"success": False, "message": "Nombre, precio y negocio_id son requeridos"}), 400

        # Manejo de Imagen con Cloudinary
        file = request.files.get('imagen_file')
        imagen_url = "https://res.cloudinary.com/dp50v0bwj/image/upload/v1704285000/default_product.png"

        if file and file.filename != '' and allowed_file(file.filename):
            logger.info(f"📸 Subiendo imagen a Cloudinary: {file.filename}")
            upload_result = cloudinary.uploader.upload(
                file,
                folder="productos_bizflow",
                public_id=f"prod_{negocio_id}_{current_user.id_usuario}_{nombre[:10].replace(' ', '_')}"
            )
            imagen_url = upload_result.get('secure_url')

        # Creación en Neon DB
        nuevo_producto = ProductoCatalogo(
            nombre=nombre,
            descripcion=request.form.get('descripcion', ''),
            precio=float(precio),
            imagen_url=imagen_url,
            categoria=request.form.get('categoria', 'General'),
            stock=int(request.form.get('stock', 0)),
            negocio_id=int(negocio_id),
            sucursal_id=int(sucursal_id) if (sucursal_id and sucursal_id != 'null') else None,
            usuario_id=current_user.id_usuario,
            activo=True
        )

        db.session.add(nuevo_producto)
        db.session.commit()

        logger.info(f"✅ Producto '{nombre}' guardado con ID: {nuevo_producto.id_producto}")
        return jsonify({
            "success": True, 
            "message": "Producto guardado correctamente",
            "id": nuevo_producto.id_producto,
            "url_foto": imagen_url
        }), 201

    except Exception as e:
        db.session.rollback()
        logger.error(f"❌ FALLO CRÍTICO EN POST: {traceback.format_exc()}")
        return jsonify({"success": False, "message": str(e)}), 500

# --- 3. RUTA: ELIMINAR (DELETE) ---
# Endpoint: /api/producto/eliminar/<id>
@catalogo_api_bp.route('/producto/eliminar/<int:id_producto>', methods=['DELETE', 'OPTIONS'])
@cross_origin(supports_credentials=True)
@login_required
def eliminar_producto(id_producto):
    if request.method == 'OPTIONS':
        return jsonify({"success": True}), 200
        
    try:
        # Verificamos que el producto pertenezca al usuario para evitar borrados malintencionados
        prod = ProductoCatalogo.query.filter_by(id_producto=id_producto, usuario_id=current_user.id_usuario).first()
        
        if not prod:
            return jsonify({"success": False, "message": "Producto no encontrado"}), 404
            
        db.session.delete(prod)
        db.session.commit()
        logger.info(f"🗑️ Producto ID {id_producto} eliminado.")
        return jsonify({"success": True, "message": "Eliminado correctamente"}), 200
    except Exception as e:
        db.session.rollback()
        logger.error(f"❌ Error al eliminar: {str(e)}")
        return jsonify({"success": False, "message": "No se pudo eliminar"}), 500