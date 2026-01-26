"""
TUKOMERCIO - API de Notificaciones para Negocios v2.0
Endpoints para la campanita de BizFlow Studio
★ INCLUYE: Aprobar/Rechazar pedidos con registro de transacción
Ubicación: src/api/notifications/notifications_negocio_api.py
"""

import logging
from flask import Blueprint, jsonify, request
from flask_cors import cross_origin
from src.models.database import db
from src.models.notification import Notification
from src.models.compradores.pedido import Pedido

# Importar modelo de transacciones para registrar ventas
try:
    from src.models.colombia_data.contabilidad.operaciones_y_catalogo import TransaccionOperativa
    TIENE_TRANSACCIONES = True
except ImportError:
    TIENE_TRANSACCIONES = False
    logging.warning("⚠️ Modelo TransaccionOperativa no disponible")

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
    Retorna cantidad de notificaciones no leídas.
    """
    try:
        count = Notification.contar_no_leidas(negocio_id=negocio_id)
        return jsonify({
            "success": True,
            "count": count
        }), 200
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
    Lista notificaciones del negocio.
    """
    try:
        limite = request.args.get('limit', 20, type=int)
        limite = request.args.get('limite', limite, type=int)
        solo_no_leidas = request.args.get('solo_no_leidas', 'false').lower() == 'true'
        categoria = request.args.get('categoria', None)
        
        if categoria:
            notificaciones = Notification.obtener_por_categoria(
                negocio_id=negocio_id,
                categoria=categoria,
                limite=limite
            )
        else:
            notificaciones = Notification.obtener_recientes(
                negocio_id=negocio_id,
                limite=limite,
                solo_no_leidas=solo_no_leidas
            )
        
        count_no_leidas = Notification.contar_no_leidas(negocio_id=negocio_id)
        
        # Enriquecer con datos del pedido si es de tipo pedido
        notifs_list = []
        for n in notificaciones:
            notif_dict = n.to_dict_mini()
            
            # Agregar referencia_id y extra_data para pedidos
            notif_dict['referencia_id'] = n.referencia_id
            notif_dict['referencia_tipo'] = n.referencia_tipo
            notif_dict['extra_data'] = n.extra_data
            
            # Agregar ID del pedido si es notificación de pedido
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
    """
    GET /api/notifications/negocio/{id}/detalle/{notif_id}
    """
    try:
        notificacion = Notification.query.filter_by(
            id=notif_id,
            negocio_id=negocio_id
        ).first()
        
        if not notificacion:
            return jsonify({"success": False, "error": "Notificación no encontrada"}), 404
        
        return jsonify({
            "success": True,
            "notificacion": notificacion.to_dict()
        }), 200
        
    except Exception as e:
        logger.error(f"Error al obtener detalle: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


# ==========================================
# MARCAR COMO LEÍDAS
# ==========================================
@notifications_negocio_bp.route('/negocio/<int:negocio_id>/marcar-leida/<int:notif_id>', methods=['POST'])
@cross_origin()
def marcar_leida(negocio_id, notif_id):
    """Marca una notificación como leída."""
    try:
        notificacion = Notification.query.filter_by(
            id=notif_id,
            negocio_id=negocio_id
        ).first()
        
        if not notificacion:
            return jsonify({"success": False, "error": "Notificación no encontrada"}), 404
        
        notificacion.marcar_leida()
        db.session.commit()
        
        count = Notification.contar_no_leidas(negocio_id=negocio_id)
        
        return jsonify({
            "success": True,
            "message": "Notificación marcada como leída",
            "count_no_leidas": count
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "error": str(e)}), 500


@notifications_negocio_bp.route('/negocio/<int:negocio_id>/marcar-todas-leidas', methods=['POST'])
@cross_origin()
def marcar_todas_leidas(negocio_id):
    """Marca todas las notificaciones como leídas."""
    try:
        count = Notification.marcar_todas_leidas(negocio_id=negocio_id)
        db.session.commit()
        
        return jsonify({
            "success": True,
            "message": f"{count} notificaciones marcadas como leídas",
            "count_no_leidas": 0
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "error": str(e)}), 500


# ==========================================
# ELIMINAR NOTIFICACIONES
# ==========================================
@notifications_negocio_bp.route('/negocio/<int:negocio_id>/eliminar/<int:notif_id>', methods=['DELETE'])
@cross_origin()
def eliminar_notificacion(negocio_id, notif_id):
    """Elimina una notificación."""
    try:
        notificacion = Notification.query.filter_by(
            id=notif_id,
            negocio_id=negocio_id
        ).first()
        
        if not notificacion:
            return jsonify({"success": False, "error": "Notificación no encontrada"}), 404
        
        db.session.delete(notificacion)
        db.session.commit()
        
        count = Notification.contar_no_leidas(negocio_id=negocio_id)
        
        return jsonify({
            "success": True,
            "message": "Notificación eliminada",
            "count_no_leidas": count
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "error": str(e)}), 500


@notifications_negocio_bp.route('/negocio/<int:negocio_id>/limpiar', methods=['DELETE'])
@cross_origin()
def limpiar_leidas(negocio_id):
    """Elimina todas las notificaciones leídas."""
    try:
        count = Notification.query.filter_by(
            negocio_id=negocio_id,
            is_read=True
        ).delete()
        db.session.commit()
        
        return jsonify({
            "success": True,
            "message": f"{count} notificaciones eliminadas"
        }), 200
        
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
    Aprueba un pedido pendiente.
    
    POST /api/notifications/negocio/{id}/aprobar-pedido/{pedido_id}
    
    Acciones:
    1. Cambia estado del pedido a 'confirmado'
    2. Registra transacción de venta (TransaccionOperativa)
    3. Marca notificación como leída
    """
    try:
        user_id = get_user_id()
        
        # Buscar el pedido
        pedido = Pedido.query.filter_by(
            id_pedido=pedido_id,
            negocio_id=negocio_id
        ).first()
        
        if not pedido:
            return jsonify({"success": False, "error": "Pedido no encontrado"}), 404
        
        if pedido.estado != 'pendiente':
            return jsonify({
                "success": False, 
                "error": f"El pedido ya está en estado: {pedido.estado}"
            }), 400
        
        # ==========================================
        # 1. CAMBIAR ESTADO DEL PEDIDO
        # ==========================================
        estado_anterior = pedido.estado
        pedido.cambiar_estado('confirmado', usuario_id=user_id, comentario='Aprobado desde notificaciones')
        
        logger.info(f"✅ Pedido {pedido.codigo_pedido} aprobado")
        
        # ==========================================
        # 2. REGISTRAR TRANSACCIÓN DE VENTA
        # ==========================================
        transaccion_id = None
        if TIENE_TRANSACCIONES:
            try:
                # Descripción con productos
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
                # No fallar por esto
        
        # ==========================================
        # 3. MARCAR NOTIFICACIÓN COMO LEÍDA
        # ==========================================
        notif_original = Notification.query.filter_by(
            negocio_id=negocio_id,
            referencia_tipo='pedido',
            referencia_id=pedido_id,
            type='nuevo_pedido'
        ).first()
        
        if notif_original:
            notif_original.marcar_leida()
        
        # ==========================================
        # 4. CREAR NOTIFICACIÓN DE CONFIRMACIÓN
        # ==========================================
        try:
            Notification.crear_notificacion_cambio_estado_pedido(
                pedido=pedido,
                estado_anterior=estado_anterior
            )
        except Exception as e:
            logger.warning(f"⚠️ No se pudo crear notificación de confirmación: {e}")
        
        # ==========================================
        # 5. COMMIT
        # ==========================================
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
    Rechaza/Cancela un pedido pendiente.
    
    POST /api/notifications/negocio/{id}/rechazar-pedido/{pedido_id}
    Body: { "motivo": "Sin stock disponible" }
    """
    try:
        user_id = get_user_id()
        data = request.get_json() or {}
        motivo = data.get('motivo', 'Rechazado por el vendedor')
        
        # Buscar el pedido
        pedido = Pedido.query.filter_by(
            id_pedido=pedido_id,
            negocio_id=negocio_id
        ).first()
        
        if not pedido:
            return jsonify({"success": False, "error": "Pedido no encontrado"}), 404
        
        if pedido.estado not in ['pendiente', 'confirmado']:
            return jsonify({
                "success": False, 
                "error": f"No se puede cancelar pedido en estado: {pedido.estado}"
            }), 400
        
        # ==========================================
        # 1. CANCELAR EL PEDIDO
        # ==========================================
        estado_anterior = pedido.estado
        pedido.cancelar(motivo=motivo, usuario_id=user_id)
        
        logger.info(f"❌ Pedido {pedido.codigo_pedido} rechazado: {motivo}")
        
        # ==========================================
        # 2. MARCAR NOTIFICACIÓN COMO LEÍDA
        # ==========================================
        notif_original = Notification.query.filter_by(
            negocio_id=negocio_id,
            referencia_tipo='pedido',
            referencia_id=pedido_id,
            type='nuevo_pedido'
        ).first()
        
        if notif_original:
            notif_original.marcar_leida()
        
        # ==========================================
        # 3. CREAR NOTIFICACIÓN DE CANCELACIÓN
        # ==========================================
        try:
            Notification.crear_notificacion_cambio_estado_pedido(
                pedido=pedido,
                estado_anterior=estado_anterior
            )
        except Exception as e:
            logger.warning(f"⚠️ No se pudo crear notificación: {e}")
        
        # ==========================================
        # 4. COMMIT
        # ==========================================
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
    """
    GET /api/notifications/negocio/{id}/pedidos-pendientes
    Lista todos los pedidos pendientes.
    """
    try:
        pedidos = Pedido.query.filter_by(
            negocio_id=negocio_id,
            estado='pendiente'
        ).order_by(
            Pedido.fecha_pedido.desc()
        ).limit(50).all()
        
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
    """
    GET /api/notifications/negocio/{id}/pedido/{pedido_id}
    Obtiene detalle completo de un pedido.
    """
    try:
        pedido = Pedido.query.filter_by(
            id_pedido=pedido_id,
            negocio_id=negocio_id
        ).first()
        
        if not pedido:
            return jsonify({"success": False, "error": "Pedido no encontrado"}), 404
        
        return jsonify({
            "success": True,
            "pedido": pedido.to_dict(include_historial=True)
        }), 200
        
    except Exception as e:
        logger.error(f"Error obteniendo pedido: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


# ==========================================
# CREAR NOTIFICACIÓN (TESTING)
# ==========================================
@notifications_negocio_bp.route('/negocio/<int:negocio_id>/crear', methods=['POST'])
@cross_origin()
def crear_notificacion_manual(negocio_id):
    """Crea una notificación manualmente (testing)."""
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
        
        return jsonify({
            "success": True,
            "message": "Notificación creada",
            "notificacion": notif.to_dict_mini()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "error": str(e)}), 500


# ==========================================
# ESTADÍSTICAS
# ==========================================
@notifications_negocio_bp.route('/negocio/<int:negocio_id>/stats', methods=['GET'])
@cross_origin()
def get_estadisticas(negocio_id):
    """Obtiene estadísticas de notificaciones."""
    try:
        from sqlalchemy import func
        
        total = Notification.query.filter_by(negocio_id=negocio_id).count()
        no_leidas = Notification.contar_no_leidas(negocio_id=negocio_id)
        
        por_tipo = db.session.query(
            Notification.type,
            func.count(Notification.id)
        ).filter_by(
            negocio_id=negocio_id
        ).group_by(
            Notification.type
        ).all()
        
        tipos_count = {tipo: count for tipo, count in por_tipo}
        
        # Contar pedidos pendientes
        pedidos_pendientes = Pedido.query.filter_by(
            negocio_id=negocio_id,
            estado='pendiente'
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