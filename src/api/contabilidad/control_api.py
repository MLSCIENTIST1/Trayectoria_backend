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

    print("🚀 [INICIO] Recibiendo solicitud en /guardar_operacion")
    
    # Identificación de Usuario
    user_id = request.headers.get('X-User-ID') or (current_user.id_usuario if current_user.is_authenticated else None)
    if not user_id:
        print("❌ [ERROR] Usuario no identificado")
        return jsonify({"success": False, "message": "Usuario no identificado"}), 401

    try:
        # DETECCIÓN DE FORMATO SEGURA (Evita el Error 415)
        content_type = request.content_type or ''
        is_form = 'multipart/form-data' in content_type
        
        print(f"I--- Tipo de Contenido: {content_type}")
        print(f"I--- ¿Es FormData?: {is_form}")

        if is_form:
            data = request.form
            print(f"I--- Datos recibidos (Form): {data.to_dict()}")
        else:
            # get_json(silent=True) evita que Flask lance error 415 automáticamente
            data = request.get_json(silent=True) or {}
            print(f"I--- Datos recibidos (JSON): {data}")

        if not data:
            print("⚠️ [WARN] No se detectaron datos en el cuerpo de la solicitud")
            return jsonify({"success": False, "message": "Cuerpo de solicitud vacío o inválido"}), 400

        negocio_id = int(data.get('negocio_id', 1))
        tipo_op = data.get('tipo', 'VENTA')
        print(f"I--- Operación: {tipo_op} | Negocio: {negocio_id} | Usuario: {user_id}")

        # 1. Registrar la Transacción en el historial (TransaccionOperativa)
        monto_final = float(data.get('precio', 0)) if is_form else float(data.get('monto', 0))
        
        nueva_t = TransaccionOperativa(
            negocio_id=negocio_id,
            usuario_id=int(user_id),
            sucursal_id=int(data.get('sucursal_id', 1)),
            tipo=tipo_op,
            concepto=data.get('concepto', 'Operación POS' if not is_form else f"Inventario: {data.get('nombre')}"),
            monto=monto_final,
            categoria=data.get('categoria', 'General'),
            metodo_pago=data.get('metodo_pago', 'Efectivo'),
            referencia_guia=data.get('referencia_guia', '')
        )
        db.session.add(nueva_t)
        print(f"✅ [DB] Transacción preparada: {monto_final}")

        # 2. Lógica de Inventario
        # CASO A: Formulario de Inventario (Un solo producto)
        if is_form:
            nombre_p = data.get('nombre')
            print(f"🔍 [BUSCA] Buscando producto por nombre: {nombre_p}")
            prod = ProductoCatalogo.query.filter_by(nombre=nombre_p, negocio_id=negocio_id).first()
            
            if prod:
                print(f"✨ [UPDATE] Actualizando producto existente: {prod.nombre}")
                if data.get('costo'): prod.costo = float(data.get('costo'))
                if data.get('precio'): prod.precio = float(data.get('precio'))
                if data.get('stock'): prod.stock = int(data.get('stock'))
            else:
                print("ℹ️ [INFO] El producto no existe en el catálogo, solo se registró la transacción.")

        # CASO B: Viene del POS (Múltiples items)
        elif 'items' in data:
            print(f"📦 [ITEMS] Procesando {len(data['items'])} artículos del POS")
            for item in data['items']:
                prod = ProductoCatalogo.query.filter_by(
                    id_producto=int(item['id']), 
                    negocio_id=negocio_id
                ).first()
                
                if prod:
                    cant_operacion = int(item.get('qty') or item.get('cantidad') or 0)
                    print(f"   > Item: {prod.nombre} | Cant: {cant_operacion}")
                    
                    if tipo_op == 'VENTA':
                        prod.stock -= cant_operacion
                    elif tipo_op in ['COMPRA', 'GASTO'] and cant_operacion > 0:
                        costo_nuevo_unidad = float(item.get('costo', 0))
                        
                        # Promedio Móvil Ponderado
                        if prod.stock > 0 and costo_nuevo_unidad > 0:
                            valor_actual = prod.stock * (prod.costo or 0)
                            valor_nuevo = cant_operacion * costo_nuevo_unidad
                            prod.costo = (valor_actual + valor_nuevo) / (prod.stock + cant_operacion)
                            print(f"   > Nuevo Costo Ponderado: {prod.costo}")
                        elif costo_nuevo_unidad > 0:
                            prod.costo = costo_nuevo_unidad
                        
                        prod.stock += cant_operacion

                    # Alerta de stock crítico
                    if prod.stock <= 5:
                        print(f"🚨 [ALERTA] Stock bajo para {prod.nombre}: {prod.stock}")
                        nueva_alerta = AlertaOperativa(
                            negocio_id=negocio_id,
                            usuario_id=int(user_id),
                            tarea=f"Stock crítico: {prod.nombre} ({prod.stock} uds.)",
                            fecha_programada=datetime.utcnow(),
                            prioridad="ALTA"
                        )
                        db.session.add(nueva_alerta)

        # 3. Commit Final
        db.session.commit()
        print("🏁 [ÉXITO] Sincronización completa en Neon DB")
        return jsonify({"success": True, "message": "Producto y Costo sincronizados en Neon DB"}), 201

    except Exception as e:
        db.session.rollback()
        print(f"❌ [CRÍTICO] Error en guardar_operacion: {str(e)}")
        print(traceback.format_exc())
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