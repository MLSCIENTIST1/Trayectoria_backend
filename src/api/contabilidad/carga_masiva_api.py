"""
BizFlow Studio - API de Carga Masiva
Importación de productos desde CSV/Excel
"""

import logging
from flask import Blueprint, request, jsonify
from flask_cors import cross_origin
from flask_login import login_required, current_user
from src.models.database import db
# CORREGIDO: Import desde la ubicación correcta
from src.models.colombia_data.contabilidad.operaciones_y_catalogo import ProductoCatalogo

carga_masiva_bp = Blueprint('carga_masiva_service', __name__)
logger = logging.getLogger(__name__)


@carga_masiva_bp.route('/control/inventario/carga-masiva', methods=['POST'])
@cross_origin(supports_credentials=True)
@login_required
def carga_masiva_productos():
    """
    Endpoint para carga masiva de productos desde CSV/Excel.
    
    Request body (JSON):
        {
            "negocio_id": 1,
            "sucursal_id": 1,
            "productos": [
                {
                    "nombre": "Producto 1",
                    "precio": 100,
                    "stock": 10,
                    "sku": "SKU001",
                    "categoria": "General"
                },
                ...
            ]
        }
    
    Returns:
        201: Productos cargados exitosamente
        400: Datos inválidos
        500: Error interno
    """
    try:
        data = request.get_json()
        productos = data.get('productos', [])
        negocio_id = data.get('negocio_id')
        sucursal_id = data.get('sucursal_id') or 1

        if not productos:
            return jsonify({
                "success": False, 
                "message": "No se recibieron datos para procesar"
            }), 400

        if not negocio_id:
            return jsonify({
                "success": False,
                "message": "negocio_id es requerido"
            }), 400

        conteo_exitoso = 0
        errores = []

        # Procesamiento fila por fila
        for index, p in enumerate(productos):
            try:
                # Mapeo flexible de campos
                nombre_prod = p.get('nombre') or p.get('Nombre') or p.get('PRODUCTO')
                precio_val = p.get('precio') or p.get('Precio') or p.get('PRECIO') or 0
                stock_val = p.get('stock') or p.get('Stock') or p.get('CANTIDAD') or 0
                sku_val = p.get('sku') or p.get('SKU') or p.get('referencia') or "SIN_SKU"
                costo_val = p.get('costo') or p.get('Costo') or p.get('COSTO') or 0
                categoria_val = p.get('categoria') or p.get('Categoria') or p.get('CATEGORIA') or 'General'
                descripcion_val = p.get('descripcion') or p.get('Descripcion') or p.get('DESCRIPCION') or ''

                if not nombre_prod:
                    errores.append(f"Fila {index + 1}: El nombre es obligatorio.")
                    continue

                # Verificar si el producto ya existe (por nombre + negocio)
                producto_existente = ProductoCatalogo.query.filter_by(
                    nombre=str(nombre_prod),
                    negocio_id=int(negocio_id)
                ).first()

                if producto_existente:
                    # Actualizar producto existente
                    producto_existente.precio = float(precio_val)
                    producto_existente.stock = int(stock_val)
                    producto_existente.costo = float(costo_val)
                    producto_existente.categoria = str(categoria_val)
                    producto_existente.referencia_sku = str(sku_val)
                    if descripcion_val:
                        producto_existente.descripcion = str(descripcion_val)
                    
                    logger.info(f"📝 Producto actualizado: {nombre_prod}")
                else:
                    # Crear nuevo producto
                    nuevo_prod = ProductoCatalogo(
                        nombre=str(nombre_prod),
                        precio=float(precio_val),
                        negocio_id=int(negocio_id),
                        usuario_id=current_user.id_usuario,
                        referencia_sku=str(sku_val),
                        descripcion=str(descripcion_val),
                        costo=float(costo_val),
                        stock=int(stock_val),
                        categoria=str(categoria_val),
                        sucursal_id=int(sucursal_id),
                        activo=True,
                        estado_publicacion=True
                    )
                    db.session.add(nuevo_prod)
                    logger.info(f"📦 Producto creado: {nombre_prod}")
                
                conteo_exitoso += 1

            except ValueError as ve:
                errores.append(f"Fila {index + 1}: Error en formato numérico ({str(ve)})")
            except Exception as e:
                errores.append(f"Fila {index + 1}: Error en formato de datos ({str(e)})")

        # Commit final
        db.session.commit()

        logger.info(f"✅ Carga masiva completada: {conteo_exitoso} productos procesados")

        return jsonify({
            "success": True,
            "message": f"Proceso finalizado. {conteo_exitoso} productos agregados/actualizados.",
            "total_procesados": conteo_exitoso,
            "errores": errores if errores else None
        }), 201

    except Exception as e:
        db.session.rollback()
        logger.error(f"❌ Error crítico en carga masiva: {str(e)}")
        return jsonify({
            "success": False, 
            "message": "Error interno al procesar el archivo",
            "error": str(e)
        }), 500


@carga_masiva_bp.route('/control/inventario/carga-masiva/template', methods=['GET'])
@cross_origin(supports_credentials=True)
def obtener_template():
    """
    Devuelve la estructura esperada para la carga masiva.
    """
    return jsonify({
        "success": True,
        "template": {
            "campos_requeridos": ["nombre", "precio"],
            "campos_opcionales": ["stock", "sku", "costo", "categoria", "descripcion"],
            "ejemplo": {
                "nombre": "Producto Ejemplo",
                "precio": 100.00,
                "stock": 10,
                "sku": "SKU001",
                "costo": 50.00,
                "categoria": "General",
                "descripcion": "Descripción del producto"
            },
            "formatos_aceptados": ["JSON", "CSV (próximamente)"]
        }
    }), 200


@carga_masiva_bp.route('/control/inventario/health', methods=['GET'])
def carga_masiva_health():
    """Health check del módulo de carga masiva"""
    return jsonify({
        "status": "online",
        "module": "carga_masiva",
        "version": "1.0.0"
    }), 200