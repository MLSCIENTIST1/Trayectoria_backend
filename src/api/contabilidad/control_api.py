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
        data = request.get_json()
        negocio_id = int(data.get('negocio_id'))
        tipo_op = data.get('tipo', 'VENTA') # VENTA o COMPRA o GASTO

        # 1. Registrar la Transacción
        nueva_t = TransaccionOperativa(
            negocio_id=negocio_id,
            usuario_id=int(user_id),
            sucursal_id=int(data.get('sucursal_id', 1)),
            tipo=tipo_op,
            concepto=data.get('concepto', 'Operación POS'),
            monto=float(data.get('monto', 0)),
            categoria=data.get('categoria', 'General'),
            metodo_pago=data.get('metodo_pago', 'Efectivo'),
            referencia_guia=data.get('referencia_guia', '')
        )
        db.session.add(nueva_t)

        # 2. Lógica de Inventario (Solo para VENTA y COMPRA)
        if tipo_op in ['VENTA', 'COMPRA', 'GASTO'] and 'items' in data:
            for item in data['items']:
                prod = ProductoCatalogo.query.filter_by(
                    id_producto=int(item['id']), 
                    negocio_id=negocio_id
                ).first()
                
                if prod:
                    # Obtenemos cantidad (soportando 'qty' de venta o 'cantidad' de compra)
                    cant = int(item.get('qty') or item.get('cantidad') or 0)
                    
                    if tipo_op == 'VENTA':
                        prod.stock -= cant
                    elif tipo_op == 'COMPRA' or (tipo_op == 'GASTO' and cant > 0):
                        prod.stock += cant # Incremento de inventario
                        # Opcional: Actualizar costo si viene en el item
                        if item.get('costo'):
                            prod.costo = float(item['costo'])

                    # Alerta de stock (Solo si terminó en bajo stock)
                    if prod.stock <= 5:
                        nueva_alerta = AlertaOperativa(
                            negocio_id=negocio_id,
                            usuario_id=int(user_id),
                            tarea=f"Stock crítico: {prod.nombre} ({prod.stock} uds.)",
                            fecha_programada=datetime.utcnow(),
                            prioridad="ALTA"
                        )
                        db.session.add(nueva_alerta)

        db.session.commit()
        return jsonify({"success": True, "message": "Sincronizado con Neon DB"}), 201

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
        # 1. Consultamos las transacciones del negocio. 
        # IMPORTANTE: Se cambió 'fecha_registro' por 'fecha' para coincidir con tu modelo.
        operaciones = TransaccionOperativa.query.filter_by(negocio_id=negocio_id)\
            .order_by(TransaccionOperativa.fecha.desc()).all()
        
        # 2. Construimos la respuesta. 
        # Aprovechamos el método 'to_dict' que ya definiste en tu modelo.
        # Solo ajustamos los nombres de los campos para que tu HTML no sufra cambios.
        resultado = []
        for op in operaciones:
            data = op.to_dict()
            resultado.append({
                "fecha": data["fecha"],
                "concepto": data["concepto"] or "Sin concepto",
                "categoria": data["categoria"] or "General",
                "monto": data["monto"], # to_dict ya hace el cast a float
                "tipo": data["tipo"],
                "metodo_pago": data["metodo"] # 'metodo' en el dict -> 'metodo_pago' para el frontend
            })
        
        return jsonify({
            "success": True,
            "operaciones": resultado
        }), 200

    except Exception as e:
        # Esto te permitirá ver el error exacto en los logs de Render si algo más falla
        print("❌ Error crítico en obtener_reporte:")
        print(traceback.format_exc())
        return jsonify({
            "success": False, 
            "message": "Error interno del servidor",
            "error_detail": str(e)
        }), 500