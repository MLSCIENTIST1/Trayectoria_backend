import cloudinary
import cloudinary.uploader
import logging
from flask import Blueprint, request, jsonify
from flask_cors import cross_origin
from src.models.database import db
from src.models.colombia_data.catalogo.catalogo import ProductoCatalogo
from flask_login import current_user

# Configuración de Logger para depuración en Render
logger = logging.getLogger(__name__)

# CONFIGURACIÓN DE CLOUDINARY
cloudinary.config( 
    cloud_name = "dp50v0bwj", 
    api_key = "966788685877863", 
    api_secret = "O6kBEBo3svgWozvn_dyw2J1CtBE",
    secure = True
)

catalogo_api_bp = Blueprint('catalogo_service', __name__)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# --- 0. RUTA DE SALUD ---
@catalogo_api_bp.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "online", "module": "catalogo"}), 200

# --- 1. RUTA PARA GUARDAR PRODUCTO ---
@catalogo_api_bp.route('/producto/guardar', methods=['POST', 'OPTIONS'])
@catalogo_api_bp.route('/api/producto/guardar', methods=['POST', 'OPTIONS'])
@cross_origin(supports_credentials=True)
def guardar_producto():
    if request.method == 'OPTIONS':
        return jsonify({"success": True}), 200
        
    try:
        # --- LÓGICA DE IDENTIFICACIÓN REFORZADA ---
        # Prioridad 1: Sesión activa (current_user)
        # Prioridad 2: ID enviado manualmente desde el frontend (localStorage)
        user_id = None
        if current_user.is_authenticated:
            user_id = current_user.id_usuario
            logger.info(f"✅ Usuario identificado por sesión: {user_id}")
        else:
            user_id = request.form.get('usuario_id')
            if user_id:
                logger.info(f"🔑 Usuario identificado por ID manual: {user_id}")

        if not user_id:
            logger.warning("❌ Intento de acceso no autorizado (Sin ID de usuario)")
            return jsonify({"success": False, "message": "Sesión no válida o falta usuario_id"}), 401

        # Extraemos datos del Formulario
        nombre = request.form.get('nombre')
        precio = request.form.get('precio')
        negocio_id = request.form.get('negocio_id')
        sucursal_id = request.form.get('sucursal_id')
        descripcion = request.form.get('descripcion', '')
        categoria = request.form.get('categoria', 'General')
        stock = request.form.get('stock', 0)

        # Validación estricta
        if not nombre or not precio or not negocio_id:
            return jsonify({"success": False, "message": "Nombre, precio y negocio son obligatorios"}), 400

        # Procesar Imagen
        file = request.files.get('imagen_file')
        imagen_url = "https://res.cloudinary.com/dp50v0bwj/image/upload/v1704285000/default_product.png"

        if file and allowed_file(file.filename):
            try:
                upload_result = cloudinary.uploader.upload(
                    file, 
                    folder="productos_bizflow",
                    public_id=f"prod_{negocio_id}_{user_id}_{nombre[:10].replace(' ', '_')}"
                )
                imagen_url = upload_result['secure_url']
            except Exception as e:
                logger.error(f"⚠️ Error subiendo a Cloudinary: {str(e)}")
                # Si falla Cloudinary, seguimos con la imagen por defecto para no bloquear al usuario

        # Crear instancia del modelo
        nuevo_producto = ProductoCatalogo(
            nombre=nombre,
            descripcion=descripcion,
            precio=float(precio),
            imagen_url=imagen_url,
            categoria=categoria,
            stock=int(stock),
            negocio_id=int(negocio_id),
            sucursal_id=int(sucursal_id) if sucursal_id else None,
            usuario_id=int(user_id),
            activo=True
        )

        db.session.add(nuevo_producto)
        db.session.commit()

        return jsonify({
            "success": True, 
            "message": "Producto guardado con éxito",
            "id": nuevo_producto.id_producto,
            "url_foto": imagen_url
        }), 201

    except Exception as e:
        db.session.rollback()
        logger.error(f"🔥 Error crítico en guardar_producto: {str(e)}")
        return jsonify({"success": False, "message": f"Error interno: {str(e)}"}), 500

# --- 2. RUTA PARA OBTENER CATÁLOGO ---
@catalogo_api_bp.route('/publico/<int:negocio_id>', methods=['GET', 'OPTIONS'])
@catalogo_api_bp.route('/api/publico/<int:negocio_id>', methods=['GET', 'OPTIONS'])
@cross_origin(supports_credentials=True)
def obtener_catalogo_publico(negocio_id):
    if request.method == 'OPTIONS':
        return jsonify({"success": True}), 200
    try:
        productos = ProductoCatalogo.query.filter_by(negocio_id=negocio_id, activo=True).all()
        # Asegúrate de que tu modelo tenga el método to_dict()
        return jsonify([p.to_dict() for p in productos]), 200
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

# --- 3. RUTA PARA ELIMINAR ---
@catalogo_api_bp.route('/producto/eliminar/<int:id_producto>', methods=['DELETE', 'OPTIONS'])
@catalogo_api_bp.route('/api/producto/eliminar/<int:id_producto>', methods=['DELETE', 'OPTIONS'])
@cross_origin(supports_credentials=True)
def eliminar_producto(id_producto):
    if request.method == 'OPTIONS':
        return jsonify({"success": True}), 200
    try:
        user_id = current_user.id_usuario if current_user.is_authenticated else request.args.get('usuario_id')
        
        prod = ProductoCatalogo.query.filter_by(id_producto=id_producto, usuario_id=user_id).first()

        if not prod:
            return jsonify({"success": False, "message": "Producto no encontrado o permisos insuficientes"}), 404

        db.session.delete(prod)
        db.session.commit()
        return jsonify({"success": True, "message": "Producto eliminado correctamente"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "message": str(e)}), 500