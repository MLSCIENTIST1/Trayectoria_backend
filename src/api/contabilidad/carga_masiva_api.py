import logging
from flask import Blueprint, request, jsonify
from flask_cors import cross_origin
from flask_login import login_required, current_user
from src.models.database import db
# Importación precisa según tu estructura de carpetas
from src.models.colombia_data.catalogo.catalogo import ProductoCatalogo

carga_masiva_bp = Blueprint('carga_masiva_service', __name__)
logger = logging.getLogger(__name__)

@carga_masiva_bp.route('/control/inventario/carga-masiva', methods=['POST'])
@cross_origin(supports_credentials=True)
@login_required
def carga_masiva_productos():
    try:
        data = request.get_json()
        productos = data.get('productos', [])
        negocio_id = data.get('negocio_id')
        # Si no llega sucursal, usamos 1 por defecto como especificaste
        sucursal_id = data.get('sucursal_id') or 1 

        if not productos:
            return jsonify({"success": False, "message": "No se recibieron datos para procesar"}), 400

        conteo_exitoso = 0
        errores = []

        # Procesamiento fila por fila para no tumbar toda la carga si una falla
        for index, p in enumerate(productos):
            try:
                # Mapeo flexible: Acepta 'nombre', 'Nombre' o 'PRODUCTO'
                nombre_prod = p.get('nombre') or p.get('Nombre') or p.get('PRODUCTO')
                precio_val = p.get('precio') or p.get('Precio') or p.get('PRECIO') or 0
                stock_val = p.get('stock') or p.get('Stock') or p.get('CANTIDAD') or 0
                sku_val = p.get('sku') or p.get('SKU') or p.get('referencia') or "SIN_SKU"

                if not nombre_prod:
                    errores.append(f"Fila {index + 1}: El nombre es obligatorio.")
                    continue

                nuevo_prod = ProductoCatalogo(
                    nombre=str(nombre_prod),
                    referencia_sku=str(sku_val),
                    descripcion=str(p.get('descripcion', '')),
                    precio=float(precio_val),
                    stock=int(stock_val),
                    categoria=str(p.get('categoria', 'General')),
                    negocio_id=int(negocio_id),
                    sucursal_id=int(sucursal_id),
                    usuario_id=current_user.id_usuario,
                    activo=True,
                    estado_publicacion=True
                )
                
                db.session.add(nuevo_prod)
                conteo_exitoso += 1

            except Exception as e:
                errores.append(f"Fila {index + 1}: Error en formato de datos ({str(e)})")

        # Guardado final en Neon DB
        db.session.commit()

        return jsonify({
            "success": True,
            "message": f"Proceso finalizado. {conteo_exitoso} productos agregados.",
            "errores": errores if errores else None
        }), 201

    except Exception as e:
        db.session.rollback()
        logger.error(f"Error crítico en carga masiva: {str(e)}")
        return jsonify({"success": False, "message": "Error interno al procesar el archivo"}), 500