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
    # 1. Manejo de Pre-flight (CORS)
    if request.method == 'OPTIONS':
        return jsonify({"success": True}), 200

    # 2. Identificación de Usuario (X-User-ID o Sesión)
    user_id = request.headers.get('X-User-ID')
    if not user_id and current_user.is_authenticated:
        user_id = current_user.id_usuario
    
    if not user_id:
        return jsonify({"success": False, "message": "Usuario no identificado"}), 401

    try:
        data = request.get_json()
        negocio_id = int(data.get('negocio_id'))
        sucursal_id = int(data.get('sucursal_id', 1))

        # 3. Registrar la Transacción (Venta/Gasto)
        nueva_t = TransaccionOperativa(
            negocio_id=negocio_id,
            usuario_id=int(user_id),
            sucursal_id=sucursal_id,
            tipo=data.get('tipo', 'VENTA'),
            concepto=data.get('concepto', 'Venta POS'),
            monto=float(data.get('monto', 0)),
            categoria=data.get('categoria', 'Ventas'),
            metodo_pago=data.get('metodo_pago', 'Efectivo'),
            referencia_guia=data.get('referencia_guia', '')
        )
        db.session.add(nueva_t)

        # 4. Procesar Items y Actualizar Inventario en Neon DB
        if data.get('tipo') == 'VENTA' and 'items' in data:
            for item in data['items']:
                # Buscamos el producto por ID y Negocio
                prod = ProductoCatalogo.query.filter_by(
                    id_producto=int(item['id']), 
                    negocio_id=negocio_id
                ).first()
                
                if prod:
                    cantidad_vendida = int(item.get('qty', 0))
                    prod.stock -= cantidad_vendida
                    
                    # 5. Generar Alerta si el stock es bajo (CORREGIDO: 'tarea' en lugar de 'mensaje')
                    if prod.stock <= 5:
                        nueva_alerta = AlertaOperativa(
                            negocio_id=negocio_id,
                            usuario_id=int(user_id),
                            tarea=f"Stock crítico: {prod.nombre} (Quedan {prod.stock} unidades)", # <--- AQUÍ ESTABA EL ERROR
                            fecha_programada=datetime.utcnow(),
                            prioridad="ALTA"
                        )
                        db.session.add(nueva_alerta)

        # 6. Confirmar todos los cambios en la DB
        db.session.commit()
        
        return jsonify({
            "success": True, 
            "message": "Operación registrada y stock actualizado con éxito"
        }), 201

    except Exception as e:
        db.session.rollback()
        # Log detallado para Render
        print(f"❌ ERROR EN POS: {traceback.format_exc()}")
        return jsonify({
            "success": False, 
            "message": f"Error interno: {str(e)}"
        }), 500