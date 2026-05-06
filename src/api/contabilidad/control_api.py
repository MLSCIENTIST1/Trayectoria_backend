# ═══════════════════════════════════════════════════════════════════════════════
# ███████╗██╗   ██╗██╗  ██╗ ██████╗ ███╗   ███╗███████╗██████╗  ██████╗██╗ ██████╗ 
# ╚══██╔══╝██║   ██║██║ ██╔╝██╔═══██╗████╗ ████║██╔════╝██╔══██╗██╔════╝██║██╔═══██╗
#    ██║   ██║   ██║█████╔╝ ██║   ██║██╔████╔██║█████╗  ██████╔╝██║     ██║██║   ██║
#    ██║   ██║   ██║██╔═██╗ ██║   ██║██║╚██╔╝██║██╔══╝  ██╔══██╗██║     ██║██║   ██║
#    ██║   ╚██████╔╝██║  ██╗╚██████╔╝██║ ╚═╝ ██║███████╗██║  ██║╚██████╗██║╚██████╔╝
#    ╚═╝    ╚═════╝ ╚═╝  ╚═╝ ╚═════╝ ╚═╝     ╚═╝╚══════╝╚═╝  ╚═╝ ╚═════╝╚═╝ ╚═════╝ 
# ═══════════════════════════════════════════════════════════════════════════════
#
# TUKOMERCIO - Plataforma de Comercio Electrónico, Gamificación y Gestión Empresarial
# Anteriormente conocido como: Trayectoria / BizFlow Studio
#
# ═══════════════════════════════════════════════════════════════════════════════
# AVISO DE PROPIEDAD INTELECTUAL Y DERECHOS DE AUTOR
# ═══════════════════════════════════════════════════════════════════════════════
#
# © 2024-2026 Carlos Eduardo Huérfano Bermúdez. Todos los derechos reservados.
#
# TITULAR DE DERECHOS:
#   Nombre:     Carlos Eduardo Huérfano Bermúdez
#   C.C.:       1.064.986.917 (Cereté, Córdoba, Colombia)
#   Contacto:   carlos-5100@hotmail.com | +57 322 818 8375
#   Ubicación:  Bogotá D.C., Colombia
#
# INFORMACIÓN DEL PROYECTO:
#   Nombre:     TuKomercio
#   Inicio:     Julio 24, 2024
#   Repositorio: github.com/routeres (routeres@gmail.com)
#
# ═══════════════════════════════════════════════════════════════════════════════
# TÉRMINOS DE USO Y RESTRICCIONES
# ═══════════════════════════════════════════════════════════════════════════════
#
# Este código fuente es CONFIDENCIAL y constituye un SECRETO COMERCIAL.
#
# QUEDA ESTRICTAMENTE PROHIBIDO sin autorización ESCRITA del titular:
#
#   1. Copiar, reproducir o duplicar este código, total o parcialmente
#   2. Modificar, adaptar o crear obras derivadas
#   3. Distribuir, publicar, sublicenciar o transferir a terceros
#   4. Usar para desarrollo de productos competidores
#   5. Realizar ingeniería inversa, descompilar o desensamblar
#   6. Remover o alterar este aviso de propiedad intelectual
#
# El acceso a este código NO otorga ninguna licencia implícita o explícita.
#
# ═══════════════════════════════════════════════════════════════════════════════
# PROTECCIÓN LEGAL
# ═══════════════════════════════════════════════════════════════════════════════
#
# Este software está protegido por:
#
#   • Ley 23 de 1982 - Derechos de Autor (Colombia)
#   • Ley 1915 de 2018 - Modernización Derechos de Autor (Colombia)
#   • Decisión Andina 351 de 1993 - Régimen Común sobre Derecho de Autor
#   • Convenio de Berna para la Protección de Obras Literarias y Artísticas
#   • Tratado OMPI sobre Derecho de Autor (WCT)
#   • Acuerdo ADPIC/TRIPS - Organización Mundial del Comercio
#
# SANCIONES POR INFRACCIÓN:
#   • Civiles: Indemnización por daños y perjuicios (Art. 57, Ley 23/1982)
#   • Penales: Prisión de 4 a 8 años y multa (Art. 271, Código Penal Colombiano)
#
# ═══════════════════════════════════════════════════════════════════════════════
# JURISDICCIÓN
# ═══════════════════════════════════════════════════════════════════════════════
#
# Cualquier disputa será resuelta exclusivamente por los tribunales de
# Bogotá D.C., Colombia, bajo las leyes de la República de Colombia.
#
# ═══════════════════════════════════════════════════════════════════════════════
#
# Para solicitar autorización de uso: carlos-5100@hotmail.com
#
# ═══════════════════════════════════════════════════════════════════════════════


"""
BizFlow Studio - API de Control Operativo
Gestión de transacciones e inventario
"""

from flask import Blueprint, request, jsonify
from flask_cors import cross_origin
from flask_login import current_user
from src.models.database import db
# CORREGIDO: Import desde la ubicación correcta
from src.models.colombia_data.contabilidad.operaciones_y_catalogo import TransaccionOperativa, ProductoCatalogo, MovimientoStock
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
        db.session.flush()  # ← persiste la transacción en la sesión antes de tocar productos
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
        
        # CASO B: Procesamiento de items (JSON con lista de productos)
        elif 'items' in data and isinstance(data['items'], list):
            items_actualizados = []

            for item in data['items']:
                id_producto = item.get('id_producto') or item.get('id')
                if not id_producto:
                    logger.warning(f"⚠️ Item sin id_producto: {item}")
                    continue

                try:
                    id_producto = int(id_producto)
                except (ValueError, TypeError):
                    logger.warning(f"⚠️ id_producto inválido: {id_producto}")
                    continue

                # Forzar recarga fresca desde la BD (evita caché de sesión)
                producto = db.session.query(ProductoCatalogo).filter(
                    ProductoCatalogo.id_producto == id_producto
                ).with_for_update().first()

                if not producto:
                    logger.warning(f"⚠️ Producto {id_producto} no encontrado en BD")
                    continue

                cantidad = int(item.get('cantidad') or item.get('qty') or 0)
                if cantidad <= 0:
                    logger.warning(f"⚠️ Cantidad inválida ({cantidad}) para producto {id_producto}")
                    continue

                stock_previo = producto.stock if producto.stock is not None else 0

                if tipo_op in ['COMPRA', 'INGRESO']:
                    stock_nuevo = stock_previo + cantidad
                    if item.get('costo'):
                        producto.costo = float(item['costo'])
                    logger.info(f"📈 COMPRA {producto.nombre}: {stock_previo} → {stock_nuevo} (+{cantidad})")

                elif tipo_op in ['VENTA', 'GASTO']:
                    stock_nuevo = max(0, stock_previo - cantidad)
                    if stock_previo < cantidad:
                        logger.warning(f"⚠️ {producto.nombre}: Stock insuficiente ({stock_previo} < {cantidad})")
                    logger.info(f"📉 VENTA {producto.nombre}: {stock_previo} → {stock_nuevo} (-{cantidad})")

                else:
                    logger.warning(f"⚠️ Tipo de operación desconocido: {tipo_op}")
                    continue

                # Actualizar stock directamente en la columna
                producto.stock = stock_nuevo
                db.session.flush()  # ← persiste el cambio antes del siguiente item

                # Registrar MovimientoStock para auditoría
                mov = MovimientoStock(
                    producto_id=producto.id_producto,
                    usuario_id=user_id,
                    negocio_id=negocio_id,
                    sucursal_id=sucursal_id,
                    tipo=tipo_op,
                    cantidad=cantidad,
                    stock_anterior=stock_previo,
                    stock_nuevo=stock_nuevo,
                    nota=f"{tipo_op} registrada desde Órdenes de Compra | Ref: {data.get('concepto', '')}"
                )
                db.session.add(mov)

                items_actualizados.append({
                    'id_producto': producto.id_producto,
                    'nombre':      producto.nombre,
                    'stock_antes': stock_previo,
                    'stock_ahora': stock_nuevo,
                    'cantidad':    cantidad,
                })
        
        db.session.commit()

        logger.info(f"✅ Operación completada: {tipo_op} - ${monto_final}")

        return jsonify({
            "success": True,
            "message": "Transacción y stock actualizados correctamente",
            "transaccion_id": nueva_transaccion.id_transaccion,
            "tipo": tipo_op,
            "monto": monto_final,
            # Devuelve los productos actualizados para que el frontend pueda confirmar
            "items_actualizados": items_actualizados if 'items_actualizados' in locals() else []
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
                "metodo_pago": op.metodo_pago or "No especificado",
                "anulada": getattr(op, 'anulada', False) or False,
                "motivo_anulacion": getattr(op, 'motivo_anulacion', None),
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
        ).filter(
            TransaccionOperativa.negocio_id == negocio_id,
            (TransaccionOperativa.anulada == False) | (TransaccionOperativa.anulada.is_(None))
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
# ENDPOINT 4: ANULAR TRANSACCIÓN
# ==========================================
@control_api_bp.route('/control/transaccion/<int:transaccion_id>/anular', methods=['PATCH', 'OPTIONS'])
@cross_origin(supports_credentials=True)
def anular_transaccion(transaccion_id):
    """
    Anula una transacción operativa sin eliminarla.
    Principio contable: nunca se borra, se anula con motivo.
    """
    if request.method == 'OPTIONS':
        return jsonify({"success": True}), 200

    user_id = get_authenticated_user_id()
    if not user_id:
        return jsonify({"success": False, "message": "Debes iniciar sesión"}), 401

    try:
        data = request.get_json(silent=True) or {}
        motivo = (data.get('motivo') or '').strip()
        if not motivo:
            return jsonify({"success": False, "message": "El motivo de anulación es obligatorio"}), 400

        transaccion = TransaccionOperativa.query.filter_by(id_transaccion=transaccion_id).first()
        if not transaccion:
            return jsonify({"success": False, "message": "Transacción no encontrada"}), 404

        # Verificar que el negocio coincida (seguridad)
        negocio_id = data.get('negocio_id')
        if negocio_id and transaccion.negocio_id != int(negocio_id):
            return jsonify({"success": False, "message": "Sin acceso a esta transacción"}), 403

        if getattr(transaccion, 'anulada', False):
            return jsonify({"success": False, "message": "Esta transacción ya está anulada"}), 409

        # Soft migration: agregar columna si no existe
        try:
            from sqlalchemy import text
            db.session.execute(text(
                "ALTER TABLE transacciones_operativas ADD COLUMN IF NOT EXISTS anulada BOOLEAN NOT NULL DEFAULT FALSE"
            ))
            db.session.execute(text(
                "ALTER TABLE transacciones_operativas ADD COLUMN IF NOT EXISTS motivo_anulacion VARCHAR(255)"
            ))
            db.session.commit()
        except Exception:
            db.session.rollback()

        transaccion.anulada = True
        transaccion.motivo_anulacion = motivo
        db.session.commit()

        logger.info(f"🚫 Transacción {transaccion_id} anulada. Motivo: {motivo}")

        return jsonify({
            "success": True,
            "message": "Ingreso anulado correctamente",
            "id": transaccion_id,
            "motivo": motivo
        }), 200

    except Exception as e:
        db.session.rollback()
        logger.error(f"❌ Error al anular transacción:", exc_info=True)
        return jsonify({"success": False, "message": "Error al anular", "error": str(e)}), 500


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