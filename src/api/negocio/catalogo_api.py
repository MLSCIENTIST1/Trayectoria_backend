import cloudinary
import cloudinary.uploader
from flask import Blueprint, request, jsonify
from flask_cors import cross_origin
from src.models.database import db
from src.models.colombia_data.catalogo.catalogo import ProductoCatalogo
from flask_login import login_required, current_user

# CONFIGURACIÓN DE CLOUDINARY
cloudinary.config( 
    cloud_name = "dp50v0bwj", 
    api_key = "966788685877863", 
    api_secret = "O6kBEBo3svgWozvn_dyw2J1CtBE",
    secure = True
)

catalogo_api_bp = Blueprint('catalogo_service', __name__)

# Extensiones permitidas para validación de imágenes
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# --- 0. RUTA DE SALUD (Para el Monitor de Telemetría) ---
@catalogo_api_bp.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "online", "module": "catalogo"}), 200

# --- 1. RUTA PARA GUARDAR PRODUCTO ---
@catalogo_api_bp.route('/producto/guardar', methods=['POST', 'OPTIONS'])
@catalogo_api_bp.route('/api/producto/guardar', methods=['POST', 'OPTIONS'])
@cross_origin(supports_credentials=True)
@login_required
def guardar_producto():
    if request.method == 'OPTIONS':
        return jsonify({"success": True}), 200
    try:
        # Extraemos datos del Formulario
        nombre = request.form.get('nombre')
        precio = request.form.get('precio')
        negocio_id = request.form.get('negocio_id')
        sucursal_id = request.form.get('sucursal_id')
        descripcion = request.form.get('descripcion', '')
        categoria = request.form.get('categoria', 'General')
        stock = request.form.get('stock', 0)

        # Validación de campos críticos
        if not nombre or not precio or not negocio_id:
            return jsonify({"success": False, "message": "Faltan datos obligatorios"}), 400

        # Procesar Archivo del Dispositivo
        file = request.files.get('imagen_file')
        
        # Imagen por defecto
        imagen_url = "https://res.cloudinary.com/dp50v0bwj/image/upload/v1704285000/default_product.png"

        if file and allowed_file(file.filename):
            # Subida directa a Cloudinary
            upload_result = cloudinary.uploader.upload(
                file, 
                folder="productos_bizflow",
                public_id=f"prod_{negocio_id}_{current_user.id_usuario}_{nombre[:10]}"
            )
            imagen_url = upload_result['secure_url']

        # Creación del objeto para la Base de Datos
        nuevo_producto = ProductoCatalogo(
            nombre=nombre,
            descripcion=descripcion,
            precio=precio,
            imagen_url=imagen_url,
            categoria=categoria,
            stock=int(stock),
            negocio_id=int(negocio_id),
            sucursal_id=int(sucursal_id),
            usuario_id=current_user.id_usuario,
            activo=True
        )

        db.session.add(nuevo_producto)
        db.session.commit()

        return jsonify({
            "success": True, 
            "message": "Producto e imagen guardados exitosamente",
            "id": nuevo_producto.id_producto,
            "url_foto": imagen_url
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "message": f"Error en servidor: {str(e)}"}), 500

# --- 2. RUTA PARA OBTENER CATÁLOGO PÚBLICO ---
@catalogo_api_bp.route('/publico/<int:negocio_id>', methods=['GET', 'OPTIONS'])
@catalogo_api_bp.route('/api/publico/<int:negocio_id>', methods=['GET', 'OPTIONS'])
@cross_origin(supports_credentials=True)
def obtener_catalogo_publico(negocio_id):
    if request.method == 'OPTIONS':
        return jsonify({"success": True}), 200
    try:
        productos = ProductoCatalogo.query.filter_by(
            negocio_id=negocio_id, 
            activo=True
        ).all()
        return jsonify([p.to_dict() for p in productos]), 200
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

# --- 3. RUTA PARA ELIMINAR PRODUCTO ---
@catalogo_api_bp.route('/producto/eliminar/<int:id_producto>', methods=['DELETE', 'OPTIONS'])
@catalogo_api_bp.route('/api/producto/eliminar/<int:id_producto>', methods=['DELETE', 'OPTIONS'])
@cross_origin(supports_credentials=True)
@login_required
def eliminar_producto(id_producto):
    if request.method == 'OPTIONS':
        return jsonify({"success": True}), 200
    try:
        # Seguridad: solo el dueño puede borrarlo
        prod = ProductoCatalogo.query.filter_by(
            id_producto=id_producto,
            usuario_id=current_user.id_usuario
        ).first()

        if not prod:
            return jsonify({"success": False, "message": "Producto no encontrado"}), 404

        db.session.delete(prod)
        db.session.commit()
        
        return jsonify({"success": True, "message": "Producto eliminado"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "message": str(e)}), 500
