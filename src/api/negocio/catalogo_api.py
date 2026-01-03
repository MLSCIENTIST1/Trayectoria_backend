from flask import Blueprint, request, jsonify
from src.models.database import db
from src.models.colombia_data.catalogo.producto import Producto
from flask_login import login_required, current_user

# Definición del Blueprint
catalogo_api_bp = Blueprint('catalogo_api', __name__)

# 1. RUTA PARA GUARDAR/INYECTAR PRODUCTO (Desde BizFlow Studio)
@catalogo_api_bp.route('/producto/guardar', methods=['POST'])
@login_required
def guardar_producto():
    try:
        data = request.get_json()
        
        # Validar campos mínimos
        if not data.get('nombre') or not data.get('precio'):
            return jsonify({"success": False, "message": "Faltan datos obligatorios"}), 400

        nuevo_producto = Producto(
            nombre=data['nombre'],
            descripcion=data.get('descripcion', ''),
            precio=data['precio'],
            imagen_url=data.get('img', ''),
            categoria=data.get('categoria', 'General'),
            stock_disponible=data.get('stock', 0),
            # Vinculación automática con el contexto de seguridad
            usuario_id=current_user.id_usuario,
            negocio_id=data['negocio_id'],
            sucursal_id=data['sucursal_id'],
            referencia_sku=data.get('sku', '')
        )

        db.session.add(nuevo_producto)
        db.session.commit()

        return jsonify({
            "success": True, 
            "message": "Producto inyectado correctamente a la base de datos",
            "id": nuevo_producto.id_producto
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "message": str(e)}), 500

# 2. RUTA PARA OBTENER CATÁLOGO POR NEGOCIO (Para Rodar.html)
@catalogo_api_bp.route('/publico/<int:negocio_id>', methods=['GET'])
def obtener_catalogo_publico(negocio_id):
    try:
        # Solo traemos los productos activos del negocio solicitado
        productos = Producto.query.filter_by(
            negocio_id=negocio_id, 
            estado_publicacion=True
        ).all()
        
        # Usamos el método serialize() que definimos en el modelo producto.py
        return jsonify([p.serialize() for p in productos]), 200

    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

# 3. RUTA PARA ELIMINAR PRODUCTO (Gestión)
@catalogo_api_bp.route('/producto/eliminar/<int:id_producto>', methods=['DELETE'])
@login_required
def eliminar_producto(id_producto):
    try:
        # Verificamos que el producto exista y pertenezca al usuario logueado
        prod = Producto.query.filter_by(
            id_producto=id_producto, 
            usuario_id=current_user.id_usuario
        ).first()

        if not prod:
            return jsonify({"success": False, "message": "Producto no encontrado o sin permisos"}), 404

        db.session.delete(prod)
        db.session.commit()
        
        return jsonify({"success": True, "message": "Producto eliminado"}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "message": str(e)}), 500