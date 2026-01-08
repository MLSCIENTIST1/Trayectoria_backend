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
    
    user_id = request.headers.get('X-User-ID') or (current_user.id_usuario if current_user.is_authenticated else None)
    if not user_id:
        print("❌ [ERROR] Usuario no identificado")
        return jsonify({"success": False, "message": "Usuario no identificado"}), 401

    try:
        # 1. DETECCIÓN DE FORMATO SEGURA
        content_type = request.content_type or ''
        is_form = 'multipart/form-data' in content_type
        
        if is_form:
            data = request.form
            print(f"I--- Formulario detectado: {data.to_dict()}")
        else:
            data = request.get_json(silent=True) or {}
            print(f"I--- JSON detectado: {data}")

        if not data:
            return jsonify({"success": False, "message": "Cuerpo de solicitud vacío"}), 400

        negocio_id = int(data.get('negocio_id', 1))
        tipo_op = data.get('tipo', 'VENTA')
        monto_final = float(data.get('precio', 0)) if is_form else float(data.get('monto', 0))

        # 2. REGISTRAR LA TRANSACCIÓN (CONTABILIDAD)
        nueva_t = TransaccionOperativa(
            negocio_id=negocio_id,
            usuario_id=int(user_id),
            sucursal_id=int(data.get('sucursal_id', 1)),
            tipo=tipo_op,
            concepto=data.get('concepto', f"Inventario: {data.get('nombre')}" if is_form else "Operación POS"),
            monto=monto_final,
            categoria=data.get('categoria', 'General'),
            metodo_pago=data.get('metodo_pago', 'Efectivo'),
            referencia_guia=data.get('referencia_guia', '')
        )
        db.session.add(nueva_t)
        print(f"✅ [CONTABILIDAD] Transacción registrada por ${monto_final}")

        # 3. LÓGICA DE INVENTARIO (CASO A: FORMULARIO)
        if is_form:
            nombre_p = data.get('nombre')
            print(f"🔍 [BUSCA] Buscando producto: '{nombre_p}'")
            prod = ProductoCatalogo.query.filter_by(nombre=nombre_p, negocio_id=negocio_id).first()
            
            if prod:
                print(f"✨ [UPDATE] Actualizando costo/stock de: {prod.nombre}")
                if data.get('costo'): prod.costo = float(data.get('costo'))
                if data.get('precio'): prod.precio = float(data.get('precio'))
                if data.get('stock'): prod.stock = int(data.get('stock'))
            else:
                # SOLUCIÓN AL PROBLEMA: Crear si no existe
                print(f"🆕 [CREAR] Producto nuevo detectado. Insertando en Neon DB...")
                nuevo_prod = ProductoCatalogo(
                    negocio_id=negocio_id,
                    nombre=nombre_p,
                    categoria=data.get('categoria', 'General'),
                    descripcion=data.get('descripcion', ''),
                    costo=float(data.get('costo', 0)),
                    precio=float(data.get('precio', 0)),
                    stock=int(data.get('stock', 0)),
                    imagen_url=None # Se actualiza vía Cloudinary en el otro flujo si es necesario
                )
                db.session.add(nuevo_prod)
                print(f"✅ [CATÁLOGO] Producto '{nombre_p}' creado con costo {data.get('costo')}")

        # 4. LÓGICA DE INVENTARIO (CASO B: POS / ITEMS)
        elif 'items' in data:
            print(f"📦 [POS] Procesando {len(data['items'])} artículos")
            for item in data['items']:
                prod = ProductoCatalogo.query.filter_by(id_producto=int(item['id']), negocio_id=negocio_id).first()
                if prod:
                    cant = int(item.get('qty') or item.get('cantidad') or 0)
                    if tipo_op == 'VENTA':
                        prod.stock -= cant
                    elif tipo_op in ['COMPRA', 'GASTO'] and cant > 0:
                        costo_n = float(item.get('costo', 0))
                        # Cálculo PMP
                        if prod.stock > 0 and costo_n > 0:
                            prod.costo = ((prod.stock * (prod.costo or 0)) + (cant * costo_n)) / (prod.stock + cant)
                        elif costo_n > 0:
                            prod.costo = costo_n
                        prod.stock += cant

                    if prod.stock <= 5:
                        alerta = AlertaOperativa(
                            negocio_id=negocio_id, usuario_id=int(user_id),
                            tarea=f"Stock crítico: {prod.nombre} ({prod.stock} uds)",
                            prioridad="ALTA", fecha_programada=datetime.utcnow()
                        )
                        db.session.add(alerta)

        db.session.commit()
        print("🏁 [ÉXITO] Sincronización completa.")
        return jsonify({"success": True, "message": "Datos sincronizados en Neon DB"}), 201

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