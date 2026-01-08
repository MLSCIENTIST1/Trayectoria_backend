from flask import Blueprint, request, jsonify
from flask_cors import cross_origin
from flask_login import login_required, current_user
from src.models.database import db
from src.models.colombia_data.contabilidad.operaciones import TransaccionOperativa, AlertaOperativa
from src.models.colombia_data.catalogo.catalogo import ProductoCatalogo
from datetime import datetime
import traceback

control_api_bp = Blueprint('control_operativo', __name__)

@control_api_bp.route('/control/operacion/registrar', methods=['POST', 'OPTIONS'])
@cross_origin(supports_credentials=True)
def registrar_operacion_maestra():
    if request.method == 'OPTIONS':
        return jsonify({"success": True}), 200

    print("🚀 [INICIO] Recibiendo solicitud en /control/operacion/registrar")
    
    # Identificación segura del usuario
    user_id = request.headers.get('X-User-ID') or (current_user.id_usuario if current_user.is_authenticated else None)
    if not user_id:
        print("❌ [ERROR] Usuario no identificado")
        return jsonify({"success": False, "message": "Usuario no identificado"}), 401

    try:
        # 1. DETECCIÓN DE FORMATO (Formulario para inventario manual, JSON para compras/ventas)
        content_type = request.content_type or ''
        is_form = 'multipart/form-data' in content_type
        
        if is_form:
            data = request.form
        else:
            data = request.get_json(silent=True) or {}

        if not data:
            return jsonify({"success": False, "message": "Cuerpo de solicitud vacío"}), 400

        negocio_id = int(data.get('negocio_id', 1))
        tipo_op = data.get('tipo', 'VENTA').upper()
        monto_final = float(data.get('precio', 0)) if is_form else float(data.get('monto', 0))

        # 2. REGISTRAR LA TRANSACCIÓN (CONTABILIDAD)
        nueva_t = TransaccionOperativa(
            negocio_id=negocio_id,
            usuario_id=int(user_id),
            sucursal_id=int(data.get('sucursal_id', 1)),
            tipo=tipo_op,
            concepto=data.get('concepto', f"Inventario: {data.get('nombre')}" if is_form else f"Operación {tipo_op}"),
            monto=monto_final,
            categoria=data.get('categoria', 'General'),
            metodo_pago=data.get('metodo_pago', 'Efectivo'),
            referencia_guia=data.get('referencia_guia', '')
        )
        db.session.add(nueva_t)

        # 3. LÓGICA DE STOCK (CASO A: FORMULARIO - CREAR/ACTUALIZAR UNO SOLO)
        if is_form:
            nombre_p = data.get('nombre')
            prod = ProductoCatalogo.query.filter_by(nombre=nombre_p, negocio_id=negocio_id).first()
            
            if prod:
                if data.get('costo'): prod.costo = float(data.get('costo'))
                if data.get('precio'): prod.precio = float(data.get('precio'))
                if data.get('stock'): prod.stock = int(data.get('stock'))
            else:
                nuevo_prod = ProductoCatalogo(
                    negocio_id=negocio_id,
                    usuario_id=int(user_id),
                    nombre=nombre_p,
                    categoria=data.get('categoria', 'General'),
                    costo=float(data.get('costo', 0)),
                    precio=float(data.get('precio', 0)),
                    stock=int(data.get('stock', 0)),
                    sucursal_id=int(data.get('sucursal_id', 1))
                )
                db.session.add(nuevo_prod)

        # 4. LÓGICA DE STOCK (CASO B: JSON - ACTUALIZAR MÚLTIPLES PRODUCTOS)
        elif 'items' in data:
            for item in data['items']:
                prod = ProductoCatalogo.query.get(item.get('id'))
                if prod:
                    cant = int(item.get('cantidad', 0))
                    # Sumar si es COMPRA o INGRESO, Restar si es VENTA o GASTO
                    if tipo_op in ['COMPRA', 'INGRESO']:
                        prod.stock = (prod.stock or 0) + cant
                        if item.get('costo'): prod.costo = float(item['costo'])
                    elif tipo_op in ['VENTA', 'GASTO']:
                        prod.stock = (prod.stock or 0) - cant

        db.session.commit()
        print(f"🏁 [ÉXITO] Sincronización completa: {tipo_op}")
        return jsonify({"success": True, "message": "Operación registrada y stock actualizado"}), 201

    except Exception as e:
        db.session.rollback()
        print(f"❌ [CRÍTICO] Error: {traceback.format_exc()}")
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