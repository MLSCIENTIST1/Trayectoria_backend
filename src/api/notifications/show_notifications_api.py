from src.models.database import db
from src.models.usuarios import Usuario
import logging
from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from sqlalchemy import or_
from src.models.notification import Notification

# Configuración del Logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)

# Blueprint para mostrar notificaciones
show_notifications_bp = Blueprint('show_notifications_bp', __name__)

@show_notifications_bp.route('/show_notifications', methods=['POST'])
@login_required
def show_notifications():
    """
    API para mostrar notificaciones asociadas al usuario autenticado.
    En el método POST, confirma la recepción de la solicitud y muestra notificaciones en formato JSON.
    """
    logger.info(f"Procesando solicitud {request.method} para mostrar notificaciones del usuario {current_user.id_usuario}.")

    try:
        # Obtener notificaciones donde el usuario es receptor o remitente
        notifications = Notification.query.filter(
            or_(
                Notification.user_id == current_user.id_usuario,  # Receptor
                Notification.sender_id == current_user.id_usuario  # Remitente
            )
        ).order_by(Notification.timestamp.desc()).all()
        logger.debug(f"Notificaciones obtenidas para el usuario {current_user.id_usuario}: {[n.id for n in notifications]}")

        # Marcar como leídas las notificaciones donde el usuario es receptor
        Notification.query.filter_by(user_id=current_user.id_usuario, is_read=False).update({'is_read': True})
        db.session.commit()
        logger.debug("Notificaciones no leídas marcadas como leídas.")

        # Formatear las notificaciones
        notifications_data = [
            {
                'id': notification.id,
                'message': notification.message,
                'timestamp': str(notification.timestamp),
                'is_read': notification.is_read
            }
            for notification in notifications
        ]

        return jsonify({
            "notificaciones": notifications_data,
            "message": "Notificaciones obtenidas correctamente."
        }), 200

    except Exception as e:
        logger.exception("Error al obtener notificaciones.")
        db.session.rollback()
        return jsonify({"error": "Hubo un problema al procesar las notificaciones."}), 500

    finally:
        # Bloque que siempre se ejecuta
        logger.info("Finalizando la ejecución del método show_notifications.")
