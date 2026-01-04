from flask import Blueprint, request, jsonify
from flask_cors import cross_origin
from flask_login import login_required, current_user
from src.models.database import db
# Importación ajustada a la nueva carpeta
from src.models.colombia_data.contabilidad.operaciones import TransaccionOperativa, AlertaOperativa
from src.models.colombia_data.catalogo.catalogo import ProductoCatalogo

control_api_bp = Blueprint('control_operativo', __name__)

@control_api_bp.route('/control/operacion/guardar', methods=['POST'])
@cross_origin(supports_credentials=True)
@login_required
def guardar_operacion():
    try:
        data = request.get_json()
        
        # 1. Registro de la Transacción
        nueva_t = TransaccionOperativa(
            negocio_id=int(data.get('negocio_id')),
            usuario_id=current_user.id_usuario,
            sucursal_id=data.get('sucursal_id', 1),
            tipo=data.get('tipo'),
            concepto=data.get('concepto'),
            monto=float(data.get('monto')),
            categoria=data.get('categoria'),
            metodo_pago=data.get('metodo_pago'),
            referencia_guia=data.get('referencia_guia')
        )
        
        # 2. Descuento de Inventario si es Venta
        if data.get('tipo') == 'VENTA' and 'items' in data:
            for item in data['items']:
                # item['id'] debe ser el id_producto
                prod = ProductoCatalogo.query.filter_by(
                    id_producto=item['id'], 
                    negocio_id=data['negocio_id']
                ).first()
                if prod:
                    prod.stock -= int(item['qty'])

        db.session.add(nueva_t)
        db.session.commit()
        
        return jsonify({"success": True, "message": "Movimiento contable registrado"}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "message": str(e)}), 500