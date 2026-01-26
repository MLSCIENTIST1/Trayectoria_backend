"""
TUKOMERCIO - API de Notificaciones para Negocios
Endpoints para la campanita de BizFlow Studio
"""

import logging
from flask import Blueprint, jsonify, request
from src.models.database import db
from src.models.notification import Notification

# Logger
logger = logging.getLogger(__name__)

# Blueprint
notifications_negocio_bp = Blueprint('notifications_negocio_bp', __name__, url_prefix='/api/notifications')


# ==========================================
# ENDPOINTS PARA CAMPANITA
# ==========================================

@notifications_negocio_bp.route('/negocio/<int:negocio_id>/count', methods=['GET'])
def get_count_no_leidas(negocio_id):
    """
    Obtiene el contador de notificaciones no leídas para la campanita.
    
    GET /api/notifications/negocio/1/count
    Response: { "count": 5 }
    """
    try:
        count = Notification.contar_no_leidas(negocio_id=negocio_id)
        return jsonify({
            "success": True,
            "count": count
        }), 200
    except Exception as e:
        logger.error(f"Error al contar notificaciones: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@notifications_negocio_bp.route('/negocio/<int:negocio_id>', methods=['GET'])
def get_notificaciones_negocio(negocio_id):
    """
    Lista notificaciones de un negocio para el dropdown de la campanita.
    
    GET /api/notifications/negocio/1?limite=20&solo_no_leidas=false
    """
    try:
        limite = request.args.get('limite', 20, type=int)
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
        
        # Contador de no leídas
        count_no_leidas = Notification.contar_no_leidas(negocio_id=negocio_id)
        
        return jsonify({
            "success": True,
            "notificaciones": [n.to_dict_mini() for n in notificaciones],
            "count_no_leidas": count_no_leidas,
            "total": len(notificaciones)
        }), 200
        
    except Exception as e:
        logger.error(f"Error al obtener notificaciones: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@notifications_negocio_bp.route('/negocio/<int:negocio_id>/detalle/<int:notif_id>', methods=['GET'])
def get_notificacion_detalle(negocio_id, notif_id):
    """
    Obtiene el detalle completo de una notificación.
    
    GET /api/notifications/negocio/1/detalle/123
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
def marcar_leida(negocio_id, notif_id):
    """
    Marca una notificación específica como leída.
    
    POST /api/notifications/negocio/1/marcar-leida/123
    """
    try:
        notificacion = Notification.query.filter_by(
            id=notif_id,
            negocio_id=negocio_id
        ).first()
        
        if not notificacion:
            return jsonify({"success": False, "error": "Notificación no encontrada"}), 404
        
        notificacion.marcar_leida()
        db.session.commit()
        
        # Retornar nuevo contador
        count = Notification.contar_no_leidas(negocio_id=negocio_id)
        
        return jsonify({
            "success": True,
            "message": "Notificación marcada como leída",
            "count_no_leidas": count
        }), 200
        
    except Exception as e:
        logger.error(f"Error al marcar como leída: {e}")
        db.session.rollback()
        return jsonify({"success": False, "error": str(e)}), 500


@notifications_negocio_bp.route('/negocio/<int:negocio_id>/marcar-todas-leidas', methods=['POST'])
def marcar_todas_leidas(negocio_id):
    """
    Marca todas las notificaciones del negocio como leídas.
    
    POST /api/notifications/negocio/1/marcar-todas-leidas
    """
    try:
        count = Notification.marcar_todas_leidas(negocio_id=negocio_id)
        db.session.commit()
        
        return jsonify({
            "success": True,
            "message": f"{count} notificaciones marcadas como leídas",
            "count_no_leidas": 0
        }), 200
        
    except Exception as e:
        logger.error(f"Error al marcar todas como leídas: {e}")
        db.session.rollback()
        return jsonify({"success": False, "error": str(e)}), 500


# ==========================================
# ELIMINAR NOTIFICACIONES
# ==========================================

@notifications_negocio_bp.route('/negocio/<int:negocio_id>/eliminar/<int:notif_id>', methods=['DELETE'])
def eliminar_notificacion(negocio_id, notif_id):
    """
    Elimina una notificación específica.
    
    DELETE /api/notifications/negocio/1/eliminar/123
    """
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
        logger.error(f"Error al eliminar notificación: {e}")
        db.session.rollback()
        return jsonify({"success": False, "error": str(e)}), 500


@notifications_negocio_bp.route('/negocio/<int:negocio_id>/limpiar', methods=['DELETE'])
def limpiar_leidas(negocio_id):
    """
    Elimina todas las notificaciones leídas del negocio.
    
    DELETE /api/notifications/negocio/1/limpiar
    """
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
        logger.error(f"Error al limpiar notificaciones: {e}")
        db.session.rollback()
        return jsonify({"success": False, "error": str(e)}), 500


# ==========================================
# CREAR NOTIFICACIÓN (PARA TESTING/ADMIN)
# ==========================================

@notifications_negocio_bp.route('/negocio/<int:negocio_id>/crear', methods=['POST'])
def crear_notificacion_manual(negocio_id):
    """
    Crea una notificación manualmente (útil para testing).
    
    POST /api/notifications/negocio/1/crear
    Body: {
        "tipo": "sistema",
        "titulo": "Prueba",
        "mensaje": "Esto es una prueba",
        "prioridad": "media"
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"success": False, "error": "Datos requeridos"}), 400
        
        # Obtener user_id del negocio (dueño) - esto depende de tu estructura
        # Por ahora lo hacemos opcional
        user_id = data.get('user_id')
        
        notif = Notification.crear_notificacion_generica(
            negocio_id=negocio_id,
            user_id=user_id,
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
        logger.error(f"Error al crear notificación: {e}")
        db.session.rollback()
        return jsonify({"success": False, "error": str(e)}), 500


# ==========================================
# ESTADÍSTICAS
# ==========================================

@notifications_negocio_bp.route('/negocio/<int:negocio_id>/stats', methods=['GET'])
def get_estadisticas(negocio_id):
    """
    Obtiene estadísticas de notificaciones del negocio.
    
    GET /api/notifications/negocio/1/stats
    """
    try:
        from sqlalchemy import func
        
        # Total
        total = Notification.query.filter_by(negocio_id=negocio_id).count()
        
        # No leídas
        no_leidas = Notification.contar_no_leidas(negocio_id=negocio_id)
        
        # Por tipo
        por_tipo = db.session.query(
            Notification.type,
            func.count(Notification.id)
        ).filter_by(
            negocio_id=negocio_id
        ).group_by(
            Notification.type
        ).all()
        
        tipos_count = {tipo: count for tipo, count in por_tipo}
        
        return jsonify({
            "success": True,
            "stats": {
                "total": total,
                "no_leidas": no_leidas,
                "leidas": total - no_leidas,
                "por_tipo": tipos_count
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Error al obtener estadísticas: {e}")
        return jsonify({"success": False, "error": str(e)}), 500