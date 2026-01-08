from flask import Blueprint, request, jsonify
from flask_cors import cross_origin
from flask_login import login_required, current_user
from src.models.database import db
from src.models.colombia_data.contabilidad.operaciones import TransaccionOperativa, AlertaOperativa
from src.models.colombia_data.catalogo.catalogo import ProductoCatalogo
from datetime import datetime
import traceback

control_api_bp = Blueprint('control_operativo', __name__)

@control_api_bp.route('/control/operacion/guardar', methods=['POST', 'OPTIONS'])
@cross_origin(supports_credentials=True)
def guardar_operacion():
    if request.method == 'OPTIONS':
        return jsonify({"success": True}), 200

    user_id = request.headers.get('X-User-ID') or (current_user.id_usuario if current_user.is_authenticated else None)
    
    if not user_id:
        return jsonify({"success": False, "message": "Usuario no identificado"}), 401

    try:
        # DETECCIÓN DE FORMATO: Soporta JSON (POS) y FormData (Interfaz Inventario)
        is_form = request.content_type and 'multipart/form-data' in request.content_type
        
        if is_form:
            data = request.form
        else:
            data = request.get_json()

        negocio_id = int(data.get('negocio_id'))
        tipo_op = data.get('tipo', 'VENTA') 

        # 1. Registrar la Transacción en el historial (TransaccionOperativa)
        nueva_t = TransaccionOperativa(
            negocio_id=negocio_id,
            usuario_id=int(user_id),
            sucursal_id=int(data.get('sucursal_id', 1)),
            tipo=tipo_op,
            concepto=data.get('concepto', 'Operación POS'),
            monto=float(data.get('monto', 0)) if not is_form else float(data.get('precio', 0)),
            categoria=data.get('categoria', 'General'),
            metodo_pago=data.get('metodo_pago', 'Efectivo'),
            referencia_guia=data.get('referencia_guia', '')
        )
        db.session.add(nueva_t)

        # 2. Lógica de Inventario (Solo para VENTA, COMPRA, GASTO)
        # CASO A: Viene del Formulario de Inventario (un solo producto nuevo/existente)
        if is_form:
            # Buscamos el producto por nombre si no hay ID disponible en el form
            nombre_p = data.get('nombre')
            prod = ProductoCatalogo.query.filter_by(nombre=nombre_p, negocio_id=negocio_id).first()
            if prod:
                if data.get('costo'):
                    prod.costo = float(data.get('costo'))
                if data.get('precio'):
                    prod.precio = float(data.get('precio'))
                if data.get('stock'):
                    prod.stock = int(data.get('stock'))

        # CASO B: Viene del POS (múltiples items en formato JSON)
        elif 'items' in data:
            for item in data['items']:
                prod = ProductoCatalogo.query.filter_by(
                    id_producto=int(item['id']), 
                    negocio_id=negocio_id
                ).first()
                
                if prod:
                    # 'qty' para ventas, 'cantidad' para compras
                    cant_operacion = int(item.get('qty') or item.get('cantidad') or 0)
                    
                    if tipo_op == 'VENTA':
                        prod.stock -= cant_operacion
                    elif tipo_op == 'COMPRA' or (tipo_op == 'GASTO' and cant_operacion > 0):
                        costo_nuevo_unidad = float(item.get('costo', 0))
                        
                        # Actualización de Costo Directo o PMP (Promedio Móvil Ponderado)
                        if prod.stock > 0 and costo_nuevo_unidad > 0:
                            valor_inventario_actual = prod.stock * (prod.costo or 0)
                            valor_compra_nueva = cant_operacion * costo_nuevo_unidad
                            nuevo_stock_total = prod.stock + cant_operacion
                            prod.costo = (valor_inventario_actual + valor_compra_nueva) / nuevo_stock_total
                        elif costo_nuevo_unidad > 0:
                            prod.costo = costo_nuevo_unidad
                        
                        prod.stock += cant_operacion

                    # Alerta de stock crítico
                    if prod.stock <= 5:
                        nueva_alerta = AlertaOperativa(
                            negocio_id=negocio_id,
                            usuario_id=int(user_id),
                            tarea=f"Stock crítico: {prod.nombre} ({prod.stock} uds.)",
                            fecha_programada=datetime.utcnow(),
                            prioridad="ALTA"
                        )
                        db.session.add(nueva_alerta)

        # Guardamos todos los cambios en Neon DB
        db.session.commit()
        return jsonify({"success": True, "message": "Producto y Costo sincronizados en Neon DB"}), 201

    except Exception as e:
        db.session.rollback()
        print(f"❌ ERROR: {traceback.format_exc()}")
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