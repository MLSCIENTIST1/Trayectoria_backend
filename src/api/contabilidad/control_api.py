"""
BizFlow Studio - API de Control Operativo
Gestión de transacciones e inventario
"""

from flask import Blueprint, request, jsonify
from flask_cors import cross_origin
from flask_login import current_user
from src.models.database import db
# CORREGIDO: Import desde la ubicación correcta
from src.models.colombia_data.contabilidad.operaciones_y_catalogo import TransaccionOperativa, ProductoCatalogo
import traceback
import logging

# Configuración de logs
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

control_api_bp = Blueprint('control_api_bp', __name__, url_prefix='/api')

# ==========================================
# FUNCIÓN DE AUTENTICACIÓN
# ==========================================
def get_authenticated_user_id():
    """
    Obtiene el ID del usuario autenticado de manera híbrida.
    """
    if current_user.is_authenticated:
        logger.info(f"✅ Usuario autenticado: {current_user.correo}")
        return current_user.id_usuario
    
    user_id = request.headers.get('X-User-ID')
    if user_id:
        logger.warning(f"⚠️ Usando X-User-ID: {user_id}")
        try:
            return int(user_id)
        except (ValueError, TypeError):
            logger.error(f"❌ X-User-ID inválido: {user_id}")
            return None
    
    return None

# ==========================================
# ENDPOINT 1: REGISTRAR OPERACIÓN
# ==========================================
@control_api_bp.route('/control/operacion/registrar', methods=['POST', 'OPTIONS'])
@cross_origin(supports_credentials=True)
def registrar_operacion_maestra():
    """
    Registra una operación (venta, compra, gasto, ingreso) y actualiza inventario.
    """
    if request.method == 'OPTIONS':
        return jsonify({"success": True}), 200
    
    logger.info("🚀 Procesando nueva operación")
    
    user_id = get_authenticated_user_id()
    if not user_id:
        logger.warning("❌ Usuario no autenticado")
        return jsonify({
            "success": False,
            "message": "Debes iniciar sesión"
        }), 401
    
    try:
        content_type = request.content_type or ''
        is_form = 'multipart/form-data' in content_type
        
        if is_form:
            data = request.form
        else:
            data = request.get_json(silent=True)
        
        if not data:
            return jsonify({
                "success": False,
                "message": "No se recibieron datos"
            }), 400
        
        negocio_id = data.get('negocio_id')
        if not negocio_id:
            return jsonify({
                "success": False,
                "message": "negocio_id es requerido"
            }), 400
        
        negocio_id = int(negocio_id)
        sucursal_id = int(data.get('sucursal_id', 1))
        tipo_op = data.get('tipo', 'VENTA').upper()
        
        if is_form:
            monto_final = float(data.get('precio', 0))
        else:
            monto_final = float(data.get('monto', 0))
        
        nueva_transaccion = TransaccionOperativa(
            negocio_id=negocio_id,
            usuario_id=user_id,
            sucursal_id=sucursal_id,
            tipo=tipo_op,
            concepto=data.get('concepto', f"Movimiento: {tipo_op}"),
            monto=monto_final,
            categoria=data.get('categoria', 'General'),
            metodo_pago=data.get('metodo_pago', 'Efectivo')
        )
        
        db.session.add(nueva_transaccion)
        logger.info(f"📝 Transacción registrada: {tipo_op} - ${monto_final}")
        
        # CASO A: Actualización manual desde formulario
        if is_form:
            nombre_producto = data.get('nombre')
            if nombre_producto:
                producto = ProductoCatalogo.query.filter_by(
                    nombre=nombre_producto,
                    negocio_id=negocio_id
                ).first()
                
                if producto:
                    if data.get('stock') is not None:
                        producto.stock = int(data.get('stock'))
                    if data.get('costo'):
                        producto.costo = float(data.get('costo'))
                    if data.get('precio'):
                        producto.precio = float(data.get('precio'))
                    
                    logger.info(f"📦 Producto actualizado: {producto.nombre}")
                else:
                    nuevo_producto = ProductoCatalogo(
                        negocio_id=negocio_id,
                        usuario_id=user_id,
                        nombre=nombre_producto,
                        stock=int(data.get('stock', 0)),
                        precio=float(data.get('precio', 0)),
                        costo=float(data.get('costo', 0)),
                        sucursal_id=sucursal_id
                    )
                    db.session.add(nuevo_producto)
                    logger.info(f"📦 Producto creado: {nombre_producto}")
        
        # CASO B: Procesamiento de items
        elif 'items' in data and isinstance(data['items'], list):
            for item in data['items']:
                id_producto = item.get('id') or item.get('id_producto')
                if not id_producto:
                    logger.warning(f"⚠️ Item sin id_producto: {item}")
                    continue
                
                producto = ProductoCatalogo.query.filter_by(
                    id_producto=int(id_producto)
                ).first()
                
                if not producto:
                    logger.warning(f"⚠️ Producto {id_producto} no encontrado")
                    continue
                
                cantidad = int(item.get('cantidad') or item.get('qty') or 0)
                if cantidad == 0:
                    continue
                
                stock_previo = producto.stock or 0
                
                if tipo_op in ['COMPRA', 'INGRESO']:
                    producto.stock = stock_previo + cantidad
                    if item.get('costo'):
                        producto.costo = float(item['costo'])
                    logger.info(f"📈 {producto.nombre}: Stock {stock_previo} → {producto.stock} (+{cantidad})")
                
                elif tipo_op in ['VENTA', 'GASTO']:
                    nuevo_stock = stock_previo - cantidad
                    if nuevo_stock < 0:
                        logger.warning(f"⚠️ {producto.nombre}: Stock insuficiente ({stock_previo} < {cantidad})")
                    producto.stock = max(0, nuevo_stock)
                    logger.info(f"📉 {producto.nombre}: Stock {stock_previo} → {producto.stock} (-{cantidad})")
        
        db.session.commit()
        
        logger.info(f"✅ Operación completada: {tipo_op} - ${monto_final}")
        
        return jsonify({
            "success": True,
            "message": "Transacción y stock actualizados correctamente",
            "transaccion_id": nueva_transaccion.id_transaccion,
            "tipo": tipo_op,
            "monto": monto_final
        }), 201
    
    except ValueError as e:
        db.session.rollback()
        logger.error(f"❌ Error de validación: {str(e)}")
        return jsonify({
            "success": False,
            "message": f"Datos inválidos: {str(e)}"
        }), 400
    
    except Exception as e:
        db.session.rollback()
        logger.error(f"❌ Error crítico:", exc_info=True)
        return jsonify({
            "success": False,
            "message": "Error interno del servidor",
            "error": str(e)
        }), 500

# ==========================================
# ENDPOINT 2: OBTENER REPORTE
# ==========================================
@control_api_bp.route('/control/reporte/<int:negocio_id>', methods=['GET', 'OPTIONS'])
@cross_origin(supports_credentials=True)
def obtener_reporte(negocio_id):
    """
    Obtiene el reporte de transacciones de un negocio.
    """
    if request.method == 'OPTIONS':
        return jsonify({"success": True}), 200
    
    try:
        user_id = get_authenticated_user_id()
        if not user_id:
            logger.warning("⚠️ Acceso a reporte sin autenticación")
        
        tipo_filtro = request.args.get('tipo')
        limite = int(request.args.get('limite', 100))
        
        query = TransaccionOperativa.query.filter_by(negocio_id=negocio_id)
        
        if tipo_filtro:
            query = query.filter_by(tipo=tipo_filtro.upper())
        
        operaciones = query.order_by(
            TransaccionOperativa.fecha.desc()
        ).limit(limite).all()
        
        resultado = []
        for op in operaciones:
            resultado.append({
                "id": op.id_transaccion,
                "fecha": op.fecha.isoformat() if hasattr(op, 'fecha') and op.fecha else None,
                "concepto": op.concepto or "Sin concepto",
                "categoria": op.categoria or "General",
                "monto": float(op.monto),
                "tipo": op.tipo,
                "metodo_pago": op.metodo_pago or "No especificado"
            })
        
        logger.info(f"✅ Reporte generado: {len(resultado)} operaciones")
        
        return jsonify({
            "success": True,
            "operaciones": resultado,
            "total": len(resultado)
        }), 200
    
    except Exception as e:
        logger.error(f"❌ Error en obtener_reporte:", exc_info=True)
        return jsonify({
            "success": False,
            "message": "Error al generar reporte",
            "error": str(e)
        }), 500

# ==========================================
# ENDPOINT 3: RESUMEN FINANCIERO
# ==========================================
@control_api_bp.route('/control/resumen/<int:negocio_id>', methods=['GET', 'OPTIONS'])
@cross_origin(supports_credentials=True)
def obtener_resumen_financiero(negocio_id):
    """
    Obtiene un resumen financiero del negocio.
    """
    if request.method == 'OPTIONS':
        return jsonify({"success": True}), 200
    
    try:
        from sqlalchemy import func
        
        resumen = db.session.query(
            TransaccionOperativa.tipo,
            func.sum(TransaccionOperativa.monto).label('total')
        ).filter_by(
            negocio_id=negocio_id
        ).group_by(
            TransaccionOperativa.tipo
        ).all()
        
        totales = {
            "ventas": 0,
            "compras": 0,
            "gastos": 0,
            "ingresos": 0
        }
        
        for tipo, total in resumen:
            if tipo == 'VENTA':
                totales['ventas'] = float(total)
            elif tipo == 'COMPRA':
                totales['compras'] = float(total)
            elif tipo == 'GASTO':
                totales['gastos'] = float(total)
            elif tipo == 'INGRESO':
                totales['ingresos'] = float(total)
        
        balance = (totales['ventas'] + totales['ingresos']) - (totales['compras'] + totales['gastos'])
        
        return jsonify({
            "success": True,
            "resumen": {
                "total_ventas": totales['ventas'],
                "total_compras": totales['compras'],
                "total_gastos": totales['gastos'],
                "total_ingresos": totales['ingresos'],
                "balance": balance
            }
        }), 200
    
    except Exception as e:
        logger.error(f"❌ Error en resumen financiero:", exc_info=True)
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

# ==========================================
# HEALTH CHECK
# ==========================================
@control_api_bp.route('/control/health', methods=['GET'])
def control_health():
    """Health check del módulo de control"""
    return jsonify({
        "status": "online",
        "module": "control_operativo",
        "version": "2.0.0"
    }), 200