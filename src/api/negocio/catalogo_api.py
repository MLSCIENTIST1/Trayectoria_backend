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

catalogo_api_bp = Blueprint('catalogo_service', __name__)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@catalogo_api_bp.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "online", "module": "catalogo"}), 200

# --- 1. RUTA PARA GUARDAR PRODUCTO (CON TELEMETRÍA PESADA) ---
@catalogo_api_bp.route('/producto/guardar', methods=['POST', 'OPTIONS'])
@catalogo_api_bp.route('/api/producto/guardar', methods=['POST', 'OPTIONS'])
@cross_origin(supports_credentials=True)
@login_required
def guardar_producto():
    if request.method == 'OPTIONS':
        logger.info("Pre-vuelo CORS (OPTIONS) gestionado.")
        return jsonify({"success": True}), 200

    logger.info("==== INICIO PROCESO GUARDAR_PRODUCTO ====")
    try:
        logger.debug(f"HEADERS RECIBIDOS: {request.headers}")
        logger.debug(f"FORMULARIO RECIBIDO: {request.form}")
        logger.debug(f"ARCHIVOS RECIBIDOS: {request.files}")

        # 1. Extracción de datos
        logger.info("Paso 1: Extrayendo datos del formulario...")
        nombre = request.form.get('nombre')
        precio = request.form.get('precio')
        negocio_id = request.form.get('negocio_id')
        sucursal_id = request.form.get('sucursal_id')
        descripcion = request.form.get('descripcion', '')
        categoria = request.form.get('categoria', 'General')
        stock = request.form.get('stock', 0)
        logger.debug(f"  - Nombre: {nombre}")
        logger.debug(f"  - Precio: {precio}")
        logger.debug(f"  - Negocio ID: {negocio_id}")
        logger.debug(f"  - Sucursal ID: {sucursal_id}")
        logger.debug(f"  - Categoría: {categoria}")
        logger.debug(f"  - Stock: {stock}")

        # 2. Validación de campos críticos
        logger.info("Paso 2: Validando campos críticos...")
        if not all([nombre, precio, negocio_id]):
            logger.warning("Validación fallida: Faltan datos obligatorios.")
            return jsonify({"success": False, "message": "Faltan datos obligatorios"}), 400
        logger.info("  - Validación OK.")

        # 3. Procesamiento de imagen
        logger.info("Paso 3: Procesando imagen...")
        file = request.files.get('imagen_file')
        imagen_url = "https://res.cloudinary.com/dp50v0bwj/image/upload/v1704285000/default_product.png"

        if file and file.filename and allowed_file(file.filename):
            logger.info(f"  - Archivo detectado: '{file.filename}'. Subiendo a Cloudinary...")
            upload_result = cloudinary.uploader.upload(
                file,
                folder="productos_bizflow",
                public_id=f"prod_{negocio_id}_{current_user.id_usuario}_{nombre[:10]}"
            )
            imagen_url = upload_result['secure_url']
            logger.info(f"  - Subida exitosa. URL: {imagen_url}")
        elif file:
            logger.warning(f"  - Archivo '{file.filename}' no permitido.")
        else:
            logger.info("  - No se proporcionó archivo. Usando imagen por defecto.")

        # 4. Creación del objeto de Base de Datos
        logger.info("Paso 4: Creando objeto ProductoCatalogo para la BD...")
        nuevo_producto = ProductoCatalogo(
            nombre=nombre,
            descripcion=descripcion,
            precio=float(precio),  # Asegurando que el precio sea float
            imagen_url=imagen_url,
            categoria=categoria,
            stock=int(stock),      # Asegurando que el stock sea int
            negocio_id=int(negocio_id),
            sucursal_id=int(sucursal_id) if sucursal_id else None,
            usuario_id=current_user.id_usuario,
            activo=True
        )
        logger.debug(f"  - Objeto creado: {nuevo_producto}")

        # 5. Inserción en Base de Datos
        logger.info("Paso 5: Guardando en la base de datos...")
        db.session.add(nuevo_producto)
        db.session.commit()
        logger.info("  - Commit exitoso a la base de datos!")

        logger.info("==== PROCESO COMPLETADO EXITOSAMENTE ====")
        return jsonify({
            "success": True,
            "message": "Producto guardado exitosamente",
            "id": nuevo_producto.id_producto,
            "url_foto": imagen_url
        }), 201

    except Exception as e:
        # ¡¡¡AQUÍ ESTÁ LA CAJA NEGRA!!!
        logger.error("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        logger.error("!!      ERROR CRÍTICO INESPERADO (500)      !!")
        logger.error("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        
        # Imprimir el traceback completo en la consola del servidor
        detailed_error = traceback.format_exc()
        logger.error(f"\n--- TRACEBACK COMPLETO ---\n{detailed_error}\n---------------------------")
        
        # Intentar revertir la sesión de la BD
        try:
            db.session.rollback()
            logger.warning("Rollback de la base de datos ejecutado.")
        except Exception as dbe:
            logger.error(f"FALLO CRÍTICO: No se pudo hacer rollback de la BD. Error: {dbe}")

        # Devolver una respuesta de error clara
        return jsonify({
            "success": False, 
            "message": "Error interno del servidor. Contacte al administrador.",
            "error_type": str(type(e).__name__),
            "details": str(e)
        }), 500


# El resto de las rutas permanece igual...
@catalogo_api_bp.route('/publico/<int:negocio_id>', methods=['GET', 'OPTIONS'])
@catalogo_api_bp.route('/api/publico/<int:negocio_id>', methods=['GET', 'OPTIONS'])
@cross_origin(supports_credentials=True)
def obtener_catalogo_publico(negocio_id):
    if request.method == 'OPTIONS': return jsonify({"success": True}), 200
    try:
        productos = ProductoCatalogo.query.filter_by(negocio_id=negocio_id, activo=True).all()
        return jsonify([p.to_dict() for p in productos]), 200
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

@catalogo_api_bp.route('/producto/eliminar/<int:id_producto>', methods=['DELETE', 'OPTIONS'])
@catalogo_api_bp.route('/api/producto/eliminar/<int:id_producto>', methods=['DELETE', 'OPTIONS'])
@cross_origin(supports_credentials=True)
@login_required
def eliminar_producto(id_producto):
    if request.method == 'OPTIONS': return jsonify({"success": True}), 200
    try:
        prod = ProductoCatalogo.query.filter_by(id_producto=id_producto, usuario_id=current_user.id_usuario).first()
        if not prod:
            return jsonify({"success": False, "message": "Producto no encontrado"}), 404
        db.session.delete(prod)
        db.session.commit()
        return jsonify({"success": True, "message": "Producto eliminado"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "message": str(e)}), 500
