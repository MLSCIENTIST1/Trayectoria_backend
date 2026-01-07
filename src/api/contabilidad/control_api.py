from flask import Blueprint, request, jsonify
from flask_cors import cross_origin
from flask_login import login_required, current_user
from src.models.database import db
import traceback

# Importación ajustada a tu estructura
from src.models.colombia_data.contabilidad.operaciones import TransaccionOperativa, AlertaOperativa
from src.models.colombia_data.catalogo.catalogo import ProductoCatalogo

control_api_bp = Blueprint('control_operativo', __name__)

@control_api_bp.route('/control/operacion/guardar', methods=['POST', 'OPTIONS'])
@cross_origin(supports_credentials=True)
def guardar_operacion():
    # Manejo de Pre-flight para CORS con headers personalizados
    if request.method == 'OPTIONS':
        return jsonify({"success": True}), 200

    try:
        data = request.get_json()
        
        # --- LÓGICA X-USER-ID ---
        # 1. Intentamos obtener el ID del header personalizado enviado por el POS
        # 2. Si no está, intentamos usar current_user (flask-login)
        user_id_header = request.headers.get('X-User-ID')
        
        if user_id_header:
            final_user_id = int(user_id_header)
        elif current_user.is_authenticated:
            final_user_id = current_user.id_usuario
        else:
            return jsonify({"success": False, "message": "Identidad de usuario no encontrada (Falta X-User-ID)"}), 401

        # 1. Registro de la Transacción
        negocio_id = int(data.get('negocio_id'))
        
        nueva_t = TransaccionOperativa(
            negocio_id=negocio_id,
            usuario_id=final_user_id, # Usamos el ID validado
            sucursal_id=int(data.get('sucursal_id', 1)),
            tipo=data.get('tipo', 'VENTA'),
            concepto=data.get('concepto'),
            monto=float(data.get('monto', 0)),
            categoria=data.get('categoria', 'Venta'),
            metodo_pago=data.get('metodo_pago', 'Efectivo'),
            referencia_guia=data.get('referencia_guia', '')
        )
        
        db.session.add(nueva_t)

        # 2. Descuento de Inventario si es VENTA
        # Es vital que el negocio_id coincida para evitar descontar stock de otro negocio
        if data.get('tipo') == 'VENTA' and 'items' in data:
            for item in data['items']:
                # Buscamos el producto en el catálogo
                prod = ProductoCatalogo.query.filter_by(
                    id_producto=int(item['id']), 
                    negocio_id=negocio_id
                ).first()
                
                if prod:
                    cantidad = int(item.get('qty', 0))
                    # Descontamos stock directamente en Neon DB
                    prod.stock -= cantidad
                    
                    # Opcional: Registrar alerta si el stock baja de cierto límite
                    if prod.stock <= 5:
                        nueva_alerta = AlertaOperativa(
                            negocio_id=negocio_id,
                            mensaje=f"Stock bajo: {prod.nombre} (Quedan {prod.stock})",
                            prioridad="ALTA"
                        )
                        db.session.add(nueva_alerta)

        db.session.commit()
        
        return jsonify({
            "success": True, 
            "message": "Venta registrada y stock actualizado en Neon DB",
            "nuevo_stock_ejemplo": prod.stock if 'prod' in locals() else None
        }), 201

    except Exception as e:
        db.session.rollback()
        # El log detallado ayuda mucho en Render/Heroku
        print(f"❌ ERROR EN POS: {traceback.format_exc()}")
        return jsonify({"success": False, "message": str(e)}), 500