"""
BizFlow Studio - API de Control Operativo
Gestión de transacciones e inventario
"""

from flask import Blueprint, request, jsonify
from flask_cors import cross_origin
from flask_login import current_user
from src.models.database import db
from src.models.colombia_data.contabilidad.operaciones import TransaccionOperativa
from src.models.colombia_data.catalogo.catalogo import ProductoCatalogo
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
    
    Returns:
        int or None: ID del usuario
    """
    # Preferencia: Flask-Login session
    if current_user.is_authenticated:
        logger.info(f"✅ Usuario autenticado: {current_user.correo}")
        return current_user.id_usuario
    
    # Fallback: Header (temporal)
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
    
    Request body (JSON):
        {
            "negocio_id": 1,
            "sucursal_id": 1,
            "tipo": "VENTA",
            "concepto": "Venta de productos",
            "monto": 1000.00,
            "categoria": "Ventas",
            "metodo_pago": "Efectivo",
            "items": [
                {
                    "id_producto": 123,
                    "cantidad": 2,
                    "precio": 500
                }
            ]
        }
    
    Returns:
        201: Operación registrada exitosamente
        400: Datos inválidos
        401: No autenticado
        500: Error interno
    """
    if request.method == 'OPTIONS':
        return jsonify({"success": True}), 200
    
    logger.info("🚀 Procesando nueva operación")
    
    # 1. AUTENTICACIÓN
    user_id = get_authenticated_user_id()
    if not user_id:
        logger.warning("❌ Usuario no autenticado")
        return jsonify({
            "success": False,
            "message": "Debes iniciar sesión"
        }), 401
    
    try:
        # 2. EXTRACCIÓN DE DATOS
        content_type = request.content_type or ''
        is_form = 'multipart/form-data' in content_type
        
        # Obtener datos según el tipo de contenido
        if is_form:
            data = request.form
        else:
            data = request.get_json(silent=True)
        
        if not data:
            return jsonify({
                "success": False,
                "message": "No se recibieron datos"
            }), 400
        
        # 3. VALIDACIÓN DE DATOS REQUERIDOS
        negocio_id = data.get('negocio_id')
        if not negocio_id:
            return jsonify({
                "success": False,
                "message": "negocio_id es requerido"
            }), 400
        
        # Convertir a tipos correctos
        negocio_id = int(negocio_id)
        sucursal_id = int(data.get('sucursal_id', 1))
        tipo_op = data.get('tipo', 'VENTA').upper()
        
        # Monto según el tipo de dato
        if is_form:
            monto_final = float(data.get('precio', 0))
        else:
            monto_final = float(data.get('monto', 0))
        
        # 4. REGISTRO DE TRANSACCIÓN
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
        
        # 5. ACTUALIZACIÓN DE INVENTARIO
        
        # CASO A: Actualización manual desde formulario
        if is_form:
            nombre_producto = data.get('nombre')
            if nombre_producto:
                producto = ProductoCatalogo.query.filter_by(
                    nombre=nombre_producto,
                    negocio_id=negocio_id
                ).first()
                
                if producto:
                    # Actualizar producto existente
                    if data.get('stock') is not None:
                        producto.stock = int(data.get('stock'))
                    if data.get('costo'):
                        producto.costo = float(data.get('costo'))
                    if data.get('precio'):
                        producto.precio = float(data.get('precio'))
                    
                    logger.info(f"📦 Producto actualizado: {producto.nombre}")
                else:
                    # Crear nuevo producto
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
        
        # CASO B: Procesamiento de items (ventas POS, compras masivas)
        elif 'items' in data and isinstance(data['items'], list):
            for item in data['items']:
                # Obtener ID del producto
                id_producto = item.get('id') or item.get('id_producto')
                if not id_producto:
                    logger.warning(f"⚠️ Item sin id_producto: {item}")
                    continue
                
                # Buscar producto
                producto = ProductoCatalogo.query.filter_by(
                    id_producto=int(id_producto)
                ).first()
                
                if not producto:
                    logger.warning(f"⚠️ Producto {id_producto} no encontrado")
                    continue
                
                # Obtener cantidad
                cantidad = int(item.get('cantidad') or item.get('qty') or 0)
                if cantidad == 0:
                    continue
                
                stock_previo = producto.stock or 0
                
                # Actualizar stock según tipo de operación
                if tipo_op in ['COMPRA', 'INGRESO']:
                    # Aumentar stock
                    producto.stock = stock_previo + cantidad
                    
                    # Actualizar costo si se proporciona
                    if item.get('costo'):
                        producto.costo = float(item['costo'])
                    
                    logger.info(f"📈 {producto.nombre}: Stock {stock_previo} → {producto.stock} (+{cantidad})")
                
                elif tipo_op in ['VENTA', 'GASTO']:
                    # Reducir stock
                    nuevo_stock = stock_previo - cantidad
                    
                    # Validar que no quede negativo
                    if nuevo_stock < 0:
                        logger.warning(f"⚠️ {producto.nombre}: Stock insuficiente ({stock_previo} < {cantidad})")
                        # Opcionalmente puedes hacer rollback aquí
                        # return jsonify({"error": f"Stock insuficiente para {producto.nombre}"}), 400
                    
                    producto.stock = max(0, nuevo_stock)  # No permitir negativos
                    logger.info(f"📉 {producto.nombre}: Stock {stock_previo} → {producto.stock} (-{cantidad})")
        
        # 6. COMMIT DE CAMBIOS
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
    
    Query params:
        tipo (str): Filtrar por tipo de operación (VENTA, COMPRA, etc.)
        desde (str): Fecha de inicio (YYYY-MM-DD)
        hasta (str): Fecha de fin (YYYY-MM-DD)
        limite (int): Número máximo de resultados (default: 100)
    
    Returns:
        200: Reporte de operaciones
        401: No autenticado
        500: Error interno
    """
    if request.method == 'OPTIONS':
        return jsonify({"success": True}), 200
    
    try:
        # Autenticación (opcional para reportes - podrías requerirla)
        user_id = get_authenticated_user_id()
        if not user_id:
            logger.warning("⚠️ Acceso a reporte sin autenticación")
            # Descomentar si quieres requerir autenticación:
            # return jsonify({"error": "No autorizado"}), 401
        
        # Obtener parámetros de filtro
        tipo_filtro = request.args.get('tipo')
        limite = int(request.args.get('limite', 100))
        
        # Query base
        query = TransaccionOperativa.query.filter_by(negocio_id=negocio_id)
        
        # Aplicar filtros
        if tipo_filtro:
            query = query.filter_by(tipo=tipo_filtro.upper())
        
        # Ordenar por fecha descendente
        operaciones = query.order_by(
            TransaccionOperativa.fecha.desc()
        ).limit(limite).all()
        
        # Serializar resultados
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
    
    Returns:
        {
            "total_ventas": 10000.00,
            "total_compras": 5000.00,
            "total_gastos": 2000.00,
            "balance": 3000.00
        }
    """
    if request.method == 'OPTIONS':
        return jsonify({"success": True}), 200
    
    try:
        from sqlalchemy import func
        
        # Calcular totales por tipo
        resumen = db.session.query(
            TransaccionOperativa.tipo,
            func.sum(TransaccionOperativa.monto).label('total')
        ).filter_by(
            negocio_id=negocio_id
        ).group_by(
            TransaccionOperativa.tipo
        ).all()
        
        # Organizar resultados
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
        
        # Calcular balance
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