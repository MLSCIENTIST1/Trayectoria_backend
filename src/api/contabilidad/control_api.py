from flask import Blueprint, request, jsonify
from flask_cors import cross_origin
from flask_login import current_user
from src.models.database import db
from src.models.colombia_data.contabilidad.operaciones import TransaccionOperativa
from src.models.colombia_data.catalogo.catalogo import ProductoCatalogo
import traceback
import logging
import sys

# Configuración de logs para Render
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
if not logger.handlers:
    handler = logging.StreamHandler(sys.stdout)
    logger.addHandler(handler)

control_api_bp = Blueprint('control_api_bp', __name__)

@control_api_bp.route('/control/operacion/registrar', methods=['POST', 'OPTIONS'])
@cross_origin(supports_credentials=True)
def registrar_operacion_maestra():
    if request.method == 'OPTIONS':
        return jsonify({"success": True}), 200

    logger.info("🚀 [INICIO] Recibiendo solicitud de operación")
    
    # 1. Identificación del usuario
    user_id = request.headers.get('X-User-ID') or (current_user.id_usuario if current_user.is_authenticated else None)
    if not user_id:
        return jsonify({"success": False, "message": "Usuario no identificado"}), 401

    try:
        # 2. Extracción de datos
        content_type = request.content_type or ''
        is_form = 'multipart/form-data' in content_type
        data = request.form if is_form else (request.get_json(silent=True) or {})

        if not data:
            return jsonify({"success": False, "message": "No se recibieron datos"}), 400

        negocio_id = int(data.get('negocio_id', 1))
        sucursal_id = int(data.get('sucursal_id', 1))
        tipo_op = data.get('tipo', 'VENTA').upper()
        monto_final = float(data.get('precio', 0)) if is_form else float(data.get('monto', 0))

        # 3. Registro de Transacción (Tabla Operaciones)
        nueva_t = TransaccionOperativa(
            negocio_id=negocio_id,
            usuario_id=int(user_id),
            sucursal_id=sucursal_id,
            tipo=tipo_op,
            concepto=data.get('concepto', f"Movimiento: {tipo_op}"),
            monto=monto_final,
            categoria=data.get('categoria', 'General'),
            metodo_pago=data.get('metodo_pago', 'Efectivo')
        )
        db.session.add(nueva_t)

        # 4. LÓGICA DE STOCK (Sincronización con productos_catalogo)
        
        # CASO A: Actualización Manual (Formulario de Inventario)
        if is_form:
            nombre_p = data.get('nombre')
            prod = ProductoCatalogo.query.filter_by(nombre=nombre_p, negocio_id=negocio_id).first()
            if prod:
                if data.get('stock') is not None: prod.stock = int(data.get('stock'))
                if data.get('costo'): prod.costo = float(data.get('costo'))
                if data.get('precio'): prod.precio = float(data.get('precio'))
            else:
                # Si el producto no existe, se crea
                nuevo_prod = ProductoCatalogo(
                    negocio_id=negocio_id, usuario_id=int(user_id),
                    nombre=nombre_p, stock=int(data.get('stock', 0)),
                    precio=float(data.get('precio', 0)), sucursal_id=sucursal_id
                )
                db.session.add(nuevo_prod)

        # CASO B: Procesamiento masivo por ID (Ventas POS / Compras)
        elif 'items' in data:
            for item in data['items']:
                # IMPORTANTE: Buscamos por la columna id_producto explícitamente
                id_target = item.get('id') or item.get('id_producto')
                if not id_target: continue

                # Cambiamos .get() por filter_by para asegurar que use id_producto
                prod = ProductoCatalogo.query.filter_by(id_producto=int(id_target)).first()
                
                if prod:
                    cant = int(item.get('cantidad') or item.get('qty') or 0)
                    stock_previo = prod.stock or 0

                    if tipo_op in ['COMPRA', 'INGRESO']:
                        prod.stock = stock_previo + cant
                        if item.get('costo'): prod.costo = float(item['costo'])
                    elif tipo_op in ['VENTA', 'GASTO']:
                        prod.stock = stock_previo - cant
                    
                    logger.info(f"✅ DB Update: {prod.nombre} | Stock: {stock_previo} -> {prod.stock}")
                else:
                    logger.warning(f"⚠️ Producto con ID {id_target} no encontrado en DB.")

        db.session.commit()
        logger.info(f"🏁 [ÉXITO] Operación {tipo_op} guardada.")
        return jsonify({"success": True, "message": "Transacción y stock actualizados"}), 201

    except Exception as e:
        db.session.rollback()
        logger.error(f"❌ [ERROR] {traceback.format_exc()}")
        return jsonify({"success": False, "message": str(e)}), 500

@control_api_bp.route('/control/reporte/<int:negocio_id>', methods=['GET', 'OPTIONS'])
@cross_origin(supports_credentials=True)
def obtener_reporte(negocio_id):
    if request.method == 'OPTIONS':
        return jsonify({"success": True}), 200
        
    try:
        # 1. Consultamos las transacciones del negocio ordenadas por fecha
        operaciones = TransaccionOperativa.query.filter_by(negocio_id=negocio_id)\
            .order_by(TransaccionOperativa.fecha.desc()).all()
        
        # 2. Construimos la respuesta mapeando al formato del Frontend
        resultado = []
        for op in operaciones:
            data = op.to_dict()
            resultado.append({
                "fecha": data["fecha"],
                "concepto": data["concepto"] or "Sin concepto",
                "categoria": data["categoria"] or "General",
                "monto": data["monto"],
                "tipo": data["tipo"],
                "metodo_pago": data["metodo"]
            })
        
        return jsonify({
            "success": True,
            "operaciones": resultado
        }), 200

    except Exception as e:
        print("❌ Error crítico en obtener_reporte:")
        print(traceback.format_exc())
        return jsonify({
            "success": False, 
            "message": "Error interno del servidor",
            "error_detail": str(e)
        }), 500