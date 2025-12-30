from src.models.database import db
from src.models.usuarios import Usuario
import logging
from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from sqlalchemy import or_

# Configuración del Logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)

# Blueprint para detalles de notificaciones
detail_notifications_bp = Blueprint('detail_notifications_bp', __name__)

@detail_notifications_bp.route('/notifications/detail_notifications', methods=['POST'])
@login_required
def detail_notifications():
    """
    API para manejar detalles de notificaciones asociadas al usuario autenticado.
    """
    logger.info(f"Procesando solicitud POST para manejar notificaciones del usuario {current_user.id_usuario}.")

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
                "id": notification.id,
                "timestamp": notification.timestamp.isoformat(),
                "message": notification.message,
                "user_id": notification.user_id,
                "sender_id": notification.sender_id,
                "is_read": notification.is_read
            }
            for notification in notifications
        ]

        # Devolver datos en formato JSON
        logger.info("Notificaciones cargadas y enviadas exitosamente.")
        return jsonify({"notifications": notifications_data}), 200

    except Exception as e:
        logger.exception("Error al recuperar notificaciones.")
        return jsonify({"error": "No se pudieron cargar las notificaciones."}), 500
