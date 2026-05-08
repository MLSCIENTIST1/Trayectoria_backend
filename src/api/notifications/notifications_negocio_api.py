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
TUKOMERCIO - API de Notificaciones para Negocios v2.2
Endpoints para la campanita de BizFlow Studio
★ NUEVO v2.1: Descuento de stock al aprobar, reversión al rechazar
★ NUEVO v2.2: Race-condition fix (with_for_update), SSE stream, auto stock_bajo
Ubicación: src/api/notifications/notifications_negocio_api.py
"""

import logging
import json
import time
from flask import Blueprint, jsonify, request, Response, stream_with_context
from flask_cors import cross_origin
from src.models.database import db
from src.models.notification import Notification
from src.models.compradores.pedido import Pedido

# ★ ACTUALIZADO v2.1: Importar también MovimientoStock y ProductoCatalogo
try:
    from src.models.colombia_data.contabilidad.operaciones_y_catalogo import (
        TransaccionOperativa,
        MovimientoStock,
        ProductoCatalogo
    )
    TIENE_TRANSACCIONES = True
except ImportError:
    TIENE_TRANSACCIONES = False
    logging.warning("⚠️ Modelos contables no disponibles")

logger = logging.getLogger(__name__)

notifications_negocio_bp = Blueprint('notifications_negocio_bp', __name__, url_prefix='/api/notifications')


# ==========================================
# HELPER: Obtener User ID
# ==========================================
def get_user_id():
    """Obtiene el user_id del header o sesión."""
    try:
        from flask_login import current_user
        if hasattr(current_user, 'is_authenticated') and current_user.is_authenticated:
            return current_user.id_usuario
    except:
        pass
    return request.headers.get('X-User-ID', type=int)


# ==========================================
# CONTADOR PARA CAMPANITA
# ==========================================
@notifications_negocio_bp.route('/negocio/<int:negocio_id>/count', methods=['GET'])
@cross_origin()
def get_count_no_leidas(negocio_id):
    """
    GET /api/notifications/negocio/{id}/count
    """
    try:
        count = Notification.contar_no_leidas(negocio_id=negocio_id)
        return jsonify({"success": True, "count": count}), 200
    except Exception as e:
        logger.error(f"Error al contar notificaciones: {e}")
        return jsonify({"success": False, "count": 0}), 200


# ==========================================
# LISTAR NOTIFICACIONES
# ==========================================
@notifications_negocio_bp.route('/negocio/<int:negocio_id>', methods=['GET'])
@cross_origin()
def get_notificaciones_negocio(negocio_id):
    """
    GET /api/notifications/negocio/{id}?limit=20
    """
    try:
        limite = request.args.get('limit', 20, type=int)
        limite = request.args.get('limite', limite, type=int)
        solo_no_leidas = request.args.get('solo_no_leidas', 'false').lower() == 'true'
        categoria = request.args.get('categoria', None)

        if categoria:
            notificaciones = Notification.obtener_por_categoria(
                negocio_id=negocio_id, categoria=categoria, limite=limite
            )
        else:
            notificaciones = Notification.obtener_recientes(
                negocio_id=negocio_id, limite=limite, solo_no_leidas=solo_no_leidas
            )

        count_no_leidas = Notification.contar_no_leidas(negocio_id=negocio_id)

        notifs_list = []
        for n in notificaciones:
            notif_dict = n.to_dict_mini()
            notif_dict['referencia_id'] = n.referencia_id
            notif_dict['referencia_tipo'] = n.referencia_tipo
            notif_dict['extra_data'] = n.extra_data
            if n.type == 'nuevo_pedido' and n.referencia_id:
                notif_dict['pedido_id'] = n.referencia_id
            notifs_list.append(notif_dict)

        return jsonify({
            "success": True,
            "notifications": notifs_list,
            "notificaciones": notifs_list,
            "count_no_leidas": count_no_leidas,
            "total": len(notifs_list)
        }), 200

    except Exception as e:
        logger.error(f"Error al obtener notificaciones: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


# ==========================================
# DETALLE DE NOTIFICACIÓN
# ==========================================
@notifications_negocio_bp.route('/negocio/<int:negocio_id>/detalle/<int:notif_id>', methods=['GET'])
@cross_origin()
def get_notificacion_detalle(negocio_id, notif_id):
    try:
        notificacion = Notification.query.filter_by(id=notif_id, negocio_id=negocio_id).first()
        if not notificacion:
            return jsonify({"success": False, "error": "Notificación no encontrada"}), 404
        return jsonify({"success": True, "notificacion": notificacion.to_dict()}), 200
    except Exception as e:
        logger.error(f"Error al obtener detalle: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


# ==========================================
# MARCAR COMO LEÍDAS
# ==========================================
@notifications_negocio_bp.route('/negocio/<int:negocio_id>/marcar-leida/<int:notif_id>', methods=['POST'])
@cross_origin()
def marcar_leida(negocio_id, notif_id):
    try:
        notificacion = Notification.query.filter_by(id=notif_id, negocio_id=negocio_id).first()
        if not notificacion:
            return jsonify({"success": False, "error": "Notificación no encontrada"}), 404
        notificacion.marcar_leida()
        db.session.commit()
        count = Notification.contar_no_leidas(negocio_id=negocio_id)
        return jsonify({"success": True, "message": "Notificación marcada como leída", "count_no_leidas": count}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "error": str(e)}), 500


@notifications_negocio_bp.route('/negocio/<int:negocio_id>/marcar-todas-leidas', methods=['POST'])
@cross_origin()
def marcar_todas_leidas(negocio_id):
    try:
        count = Notification.marcar_todas_leidas(negocio_id=negocio_id)
        db.session.commit()
        return jsonify({"success": True, "message": f"{count} notificaciones marcadas como leídas", "count_no_leidas": 0}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "error": str(e)}), 500


# ==========================================
# ELIMINAR NOTIFICACIONES
# ==========================================
@notifications_negocio_bp.route('/negocio/<int:negocio_id>/eliminar/<int:notif_id>', methods=['DELETE'])
@cross_origin()
def eliminar_notificacion(negocio_id, notif_id):
    try:
        notificacion = Notification.query.filter_by(id=notif_id, negocio_id=negocio_id).first()
        if not notificacion:
            return jsonify({"success": False, "error": "Notificación no encontrada"}), 404
        db.session.delete(notificacion)
        db.session.commit()
        count = Notification.contar_no_leidas(negocio_id=negocio_id)
        return jsonify({"success": True, "message": "Notificación eliminada", "count_no_leidas": count}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "error": str(e)}), 500


@notifications_negocio_bp.route('/negocio/<int:negocio_id>/limpiar', methods=['DELETE'])
@cross_origin()
def limpiar_leidas(negocio_id):
    try:
        count = Notification.query.filter_by(negocio_id=negocio_id, is_read=True).delete()
        db.session.commit()
        return jsonify({"success": True, "message": f"{count} notificaciones eliminadas"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "error": str(e)}), 500


# ==========================================
# ★★★ APROBAR PEDIDO ★★★
# ==========================================
@notifications_negocio_bp.route('/negocio/<int:negocio_id>/aprobar-pedido/<int:pedido_id>', methods=['POST'])
@cross_origin()
def aprobar_pedido(negocio_id, pedido_id):
    """
    POST /api/notifications/negocio/{id}/aprobar-pedido/{pedido_id}
    1. Cambia estado a 'confirmado'
    2. Registra TransaccionOperativa de VENTA
    ★ NUEVO: 3. Descuenta stock por producto
    4. Marca notificación como leída
    """
    try:
        user_id = get_user_id()

        # ★ v2.2: with_for_update() previene race condition de doble-aprobación
        pedido = Pedido.query.filter_by(
            id_pedido=pedido_id, negocio_id=negocio_id
        ).with_for_update().first()

        if not pedido:
            return jsonify({"success": False, "error": "Pedido no encontrado"}), 404

        if pedido.estado != 'pendiente':
            return jsonify({"success": False, "error": f"El pedido ya está en estado: {pedido.estado}"}), 400

        # 1. CAMBIAR ESTADO
        estado_anterior = pedido.estado
        pedido.cambiar_estado('confirmado', usuario_id=user_id, comentario='Aprobado desde notificaciones')
        logger.info(f"✅ Pedido {pedido.codigo_pedido} aprobado")

        # 2. REGISTRAR TRANSACCIÓN DE VENTA
        transaccion_id = None
        if TIENE_TRANSACCIONES:
            try:
                productos_desc = ', '.join([
                    f"{p.get('nombre', 'Producto')} x{p.get('cantidad', 1)}"
                    for p in (pedido.productos or [])[:3]
                ])
                if len(pedido.productos or []) > 3:
                    productos_desc += f" (+{len(pedido.productos) - 3} más)"

                transaccion = TransaccionOperativa(
                    negocio_id=negocio_id,
                    usuario_id=user_id,
                    sucursal_id=pedido.sucursal_id or 1,
                    tipo='VENTA',
                    concepto=f"Pedido #{pedido.codigo_pedido} - {pedido.cliente_nombre}",
                    monto=float(pedido.total),
                    categoria='Ventas Online',
                    metodo_pago=pedido.metodo_pago or 'Efectivo'
                )
                db.session.add(transaccion)
                db.session.flush()
                transaccion_id = transaccion.id_transaccion
                logger.info(f"💰 Transacción registrada: ${pedido.total}")
            except Exception as e:
                logger.error(f"⚠️ Error registrando transacción: {e}")

        # ★ NUEVO v2.1: 3. DESCONTAR STOCK
        if TIENE_TRANSACCIONES:
            try:
                for item in (pedido.productos or []):
                    producto_id = item.get('id') or item.get('id_producto')
                    cantidad = item.get('cantidad', 1)
                    if not producto_id:
                        continue
                    # ★ v2.2: with_for_update() bloquea fila para evitar doble-descuento
                    producto = ProductoCatalogo.query.filter_by(
                        id_producto=producto_id
                    ).with_for_update().first()
                    if not producto:
                        continue
                    stock_anterior = producto.stock
                    producto.stock = max(0, producto.stock - cantidad)
                    movimiento = MovimientoStock(
                        producto_id=producto_id,
                        usuario_id=user_id or 1,
                        negocio_id=negocio_id,
                        sucursal_id=pedido.sucursal_id or 1,
                        tipo='SALIDA',
                        cantidad=cantidad,
                        stock_anterior=stock_anterior,
                        stock_nuevo=producto.stock,
                        nota=f"Pedido #{pedido.codigo_pedido} confirmado"
                    )
                    db.session.add(movimiento)
                    logger.info(f"📦 Stock {producto.nombre}: {stock_anterior} → {producto.stock}")
                    # ★ v2.2: Auto-alerta stock bajo
                    try:
                        umbral = getattr(producto, 'stock_minimo', None) or 5
                        if producto.stock <= umbral:
                            Notification.crear_notificacion_stock_bajo(
                                negocio_id=negocio_id,
                                producto=producto
                            )
                            logger.info(f"⚠️ Alerta stock bajo creada: {producto.nombre} ({producto.stock} restantes)")
                    except Exception as se:
                        logger.warning(f"⚠️ No se pudo crear alerta stock_bajo: {se}")
            except Exception as e:
                logger.error(f"⚠️ Error descontando stock: {e}")

        # 4. MARCAR NOTIFICACIÓN COMO LEÍDA
        notif_original = Notification.query.filter_by(
            negocio_id=negocio_id, referencia_tipo='pedido',
            referencia_id=pedido_id, type='nuevo_pedido'
        ).first()
        if notif_original:
            notif_original.marcar_leida()

        # 5. CREAR NOTIFICACIÓN DE CONFIRMACIÓN
        try:
            Notification.crear_notificacion_cambio_estado_pedido(
                pedido=pedido, estado_anterior=estado_anterior
            )
        except Exception as e:
            logger.warning(f"⚠️ No se pudo crear notificación de confirmación: {e}")

        # 6. COMMIT
        db.session.commit()

        return jsonify({
            "success": True,
            "message": f"Pedido #{pedido.codigo_pedido} aprobado exitosamente",
            "pedido": {
                "id": pedido.id_pedido,
                "codigo": pedido.codigo_pedido,
                "estado": pedido.estado,
                "total": float(pedido.total),
                "cliente": pedido.cliente_nombre
            },
            "transaccion_id": transaccion_id,
            "count_no_leidas": Notification.contar_no_leidas(negocio_id=negocio_id)
        }), 200

    except Exception as e:
        db.session.rollback()
        logger.error(f"❌ Error aprobando pedido: {e}", exc_info=True)
        return jsonify({"success": False, "error": str(e)}), 500


# ==========================================
# ★★★ RECHAZAR PEDIDO ★★★
# ==========================================
@notifications_negocio_bp.route('/negocio/<int:negocio_id>/rechazar-pedido/<int:pedido_id>', methods=['POST'])
@cross_origin()
def rechazar_pedido(negocio_id, pedido_id):
    """
    POST /api/notifications/negocio/{id}/rechazar-pedido/{pedido_id}
    Body: { "motivo": "Sin stock disponible" }
    ★ NUEVO v2.1: Si estaba confirmado, revierte transacción y devuelve stock
    """
    try:
        user_id = get_user_id()
        data = request.get_json() or {}
        motivo = data.get('motivo', 'Rechazado por el vendedor')

        pedido = Pedido.query.filter_by(id_pedido=pedido_id, negocio_id=negocio_id).first()

        if not pedido:
            return jsonify({"success": False, "error": "Pedido no encontrado"}), 404

        if pedido.estado not in ['pendiente', 'confirmado']:
            return jsonify({"success": False, "error": f"No se puede cancelar pedido en estado: {pedido.estado}"}), 400

        # 1. CANCELAR EL PEDIDO
        estado_anterior = pedido.estado
        pedido.cancelar(motivo=motivo, usuario_id=user_id)
        logger.info(f"❌ Pedido {pedido.codigo_pedido} rechazado: {motivo}")

        # ★ NUEVO v2.1: REVERTIR SI YA ESTABA CONFIRMADO
        if estado_anterior == 'confirmado' and TIENE_TRANSACCIONES:
            try:
                contra = TransaccionOperativa(
                    negocio_id=negocio_id,
                    usuario_id=user_id or 1,
                    sucursal_id=pedido.sucursal_id or 1,
                    tipo='DEVOLUCION',
                    concepto=f"Cancelación Pedido #{pedido.codigo_pedido} - {pedido.cliente_nombre}",
                    monto=float(pedido.total),
                    categoria='Devoluciones',
                    metodo_pago=pedido.metodo_pago or 'Efectivo',
                    notas=f"Motivo: {motivo}"
                )
                db.session.add(contra)
            except Exception as e:
                logger.error(f"⚠️ Error en contra-transacción: {e}")

            try:
                for item in (pedido.productos or []):
                    producto_id = item.get('id') or item.get('id_producto')
                    cantidad = item.get('cantidad', 1)
                    if not producto_id:
                        continue
                    producto = ProductoCatalogo.query.get(producto_id)
                    if not producto:
                        continue
                    stock_anterior = producto.stock
                    producto.stock = producto.stock + cantidad
                    movimiento = MovimientoStock(
                        producto_id=producto_id,
                        usuario_id=user_id or 1,
                        negocio_id=negocio_id,
                        sucursal_id=pedido.sucursal_id or 1,
                        tipo='ENTRADA',
                        cantidad=cantidad,
                        stock_anterior=stock_anterior,
                        stock_nuevo=producto.stock,
                        nota=f"Devolución por cancelación Pedido #{pedido.codigo_pedido}"
                    )
                    db.session.add(movimiento)
                    logger.info(f"📦 Stock revertido {producto.nombre}: {stock_anterior} → {producto.stock}")
            except Exception as e:
                logger.error(f"⚠️ Error devolviendo stock: {e}")

        # 2. MARCAR NOTIFICACIÓN COMO LEÍDA
        notif_original = Notification.query.filter_by(
            negocio_id=negocio_id, referencia_tipo='pedido',
            referencia_id=pedido_id, type='nuevo_pedido'
        ).first()
        if notif_original:
            notif_original.marcar_leida()

        # 3. CREAR NOTIFICACIÓN DE CANCELACIÓN
        try:
            Notification.crear_notificacion_cambio_estado_pedido(
                pedido=pedido, estado_anterior=estado_anterior
            )
        except Exception as e:
            logger.warning(f"⚠️ No se pudo crear notificación: {e}")

        # 4. COMMIT
        db.session.commit()

        return jsonify({
            "success": True,
            "message": f"Pedido #{pedido.codigo_pedido} rechazado",
            "pedido": {
                "id": pedido.id_pedido,
                "codigo": pedido.codigo_pedido,
                "estado": pedido.estado,
                "motivo": motivo
            },
            "count_no_leidas": Notification.contar_no_leidas(negocio_id=negocio_id)
        }), 200

    except Exception as e:
        db.session.rollback()
        logger.error(f"❌ Error rechazando pedido: {e}", exc_info=True)
        return jsonify({"success": False, "error": str(e)}), 500


# ==========================================
# LISTAR PEDIDOS PENDIENTES
# ==========================================
@notifications_negocio_bp.route('/negocio/<int:negocio_id>/pedidos-pendientes', methods=['GET'])
@cross_origin()
def listar_pedidos_pendientes(negocio_id):
    try:
        pedidos = Pedido.query.filter_by(
            negocio_id=negocio_id, estado='pendiente'
        ).order_by(Pedido.fecha_pedido.desc()).limit(50).all()

        return jsonify({
            "success": True,
            "pedidos": [p.to_dict_lista() for p in pedidos],
            "total": len(pedidos)
        }), 200

    except Exception as e:
        logger.error(f"Error listando pedidos: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


# ==========================================
# OBTENER DETALLE DE PEDIDO
# ==========================================
@notifications_negocio_bp.route('/negocio/<int:negocio_id>/pedido/<int:pedido_id>', methods=['GET'])
@cross_origin()
def obtener_pedido_detalle(negocio_id, pedido_id):
    try:
        pedido = Pedido.query.filter_by(id_pedido=pedido_id, negocio_id=negocio_id).first()
        if not pedido:
            return jsonify({"success": False, "error": "Pedido no encontrado"}), 404
        return jsonify({"success": True, "pedido": pedido.to_dict(include_historial=True)}), 200
    except Exception as e:
        logger.error(f"Error obteniendo pedido: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


# ==========================================
# CREAR NOTIFICACIÓN (TESTING)
# ==========================================
@notifications_negocio_bp.route('/negocio/<int:negocio_id>/crear', methods=['POST'])
@cross_origin()
def crear_notificacion_manual(negocio_id):
    try:
        data = request.get_json()
        if not data:
            return jsonify({"success": False, "error": "Datos requeridos"}), 400

        notif = Notification.crear_notificacion_generica(
            negocio_id=negocio_id,
            user_id=data.get('user_id'),
            tipo=data.get('tipo', 'sistema'),
            titulo=data.get('titulo', 'Notificación'),
            mensaje=data.get('mensaje', ''),
            referencia_tipo=data.get('referencia_tipo'),
            referencia_id=data.get('referencia_id'),
            action_url=data.get('action_url'),
            prioridad=data.get('prioridad', 'media'),
            extra_data=data.get('extra_data')
        )
        db.session.commit()
        return jsonify({"success": True, "message": "Notificación creada", "notificacion": notif.to_dict_mini()}), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "error": str(e)}), 500


# ==========================================
# ESTADÍSTICAS
# ==========================================
@notifications_negocio_bp.route('/negocio/<int:negocio_id>/stats', methods=['GET'])
@cross_origin()
def get_estadisticas(negocio_id):
    try:
        from sqlalchemy import func

        total = Notification.query.filter_by(negocio_id=negocio_id).count()
        no_leidas = Notification.contar_no_leidas(negocio_id=negocio_id)

        por_tipo = db.session.query(
            Notification.type, func.count(Notification.id)
        ).filter_by(negocio_id=negocio_id).group_by(Notification.type).all()

        tipos_count = {tipo: count for tipo, count in por_tipo}

        pedidos_pendientes = Pedido.query.filter_by(
            negocio_id=negocio_id, estado='pendiente'
        ).count()

        return jsonify({
            "success": True,
            "stats": {
                "total": total,
                "no_leidas": no_leidas,
                "leidas": total - no_leidas,
                "por_tipo": tipos_count,
                "pedidos_pendientes": pedidos_pendientes
            }
        }), 200

    except Exception as e:
        logger.error(f"Error en estadísticas: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


# ==========================================
# ★★★ SSE STREAM — Tiempo Real ★★★
# ==========================================
@notifications_negocio_bp.route('/negocio/<int:negocio_id>/stream', methods=['GET'])
@cross_origin()
def stream_notificaciones(negocio_id):
    """
    GET /api/notifications/negocio/{id}/stream
    Server-Sent Events — actualiza campanita en tiempo real sin polling.
    Nota: en Render con workers sync, usa max 1-2 conexiones simultáneas.
    El frontend hace fallback a polling si SSE no está disponible.
    """
    def event_generator():
        last_count = -1
        last_pendientes = -1
        heartbeat = 0

        while True:
            try:
                count = Notification.contar_no_leidas(negocio_id=negocio_id)
                pendientes = Pedido.query.filter_by(
                    negocio_id=negocio_id, estado='pendiente'
                ).count()

                if count != last_count or pendientes != last_pendientes:
                    last_count = count
                    last_pendientes = pendientes
                    payload = json.dumps({
                        "count": count,
                        "pedidos_pendientes": pendientes,
                        "negocio_id": negocio_id
                    })
                    yield f"data: {payload}\n\n"
                else:
                    heartbeat += 1
                    if heartbeat % 6 == 0:  # cada ~30s enviar heartbeat
                        yield f": heartbeat\n\n"

                time.sleep(5)

            except GeneratorExit:
                logger.info(f"SSE cerrado: negocio {negocio_id}")
                break
            except Exception as e:
                logger.error(f"SSE error negocio {negocio_id}: {e}")
                yield f"data: {json.dumps({'error': 'stream_error'})}\n\n"
                break

    headers = {
        'Cache-Control': 'no-cache',
        'X-Accel-Buffering': 'no',  # Nginx / Render: deshabilita buffer
        'Connection': 'keep-alive',
        'Access-Control-Allow-Origin': '*'
    }
    return Response(
        stream_with_context(event_generator()),
        mimetype='text/event-stream',
        headers=headers
    )