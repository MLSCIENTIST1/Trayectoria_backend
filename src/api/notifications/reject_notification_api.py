from src.models.database import db
from src.models.usuarios import Usuario  
import logging
from flask import Blueprint, jsonify
from flask_login import login_required, current_user
from sqlalchemy.exc import SQLAlchemyError

# Configuración del Logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)

# Blueprint para rechazar notificaciones
reject_notification_bp = Blueprint('reject_notification_bp', __name__)

@reject_notification_bp.route('/reject_notification', methods=['POST'])
@login_required
def reject_notification(notification_id):
    """
    API para rechazar una notificación específica.
    Valida que el usuario autenticado esté autorizado para realizar esta acción.
    """
    logger.info(f"Procesando solicitud POST para rechazar la notificación {notification_id}.")

    try:
        # Obtener la notificación
        notification = Notification.query.get_or_404(notification_id)
        logger.debug(f"Notificación obtenida - ID: {notification.id}, Usuario: {notification.user_id}, Rechazada: {notification.is_rejected}")

        # Verificar autorización
        if notification.user_id != current_user.id_usuario:
            logger.warning(f"Acceso denegado: Usuario {current_user.id_usuario} no está autorizado para rechazar la notificación {notification_id}.")
            return jsonify({"error": "Notificación no autorizada."}), 403

        # Actualizar estado de la notificación
        notification.is_rejected = True
        db.session.commit()
        logger.info(f"Notificación {notification_id} rechazada exitosamente por el usuario {current_user.id_usuario}.")

        # Devolver confirmación en formato JSON
        return jsonify({"message": "Notificación rechazada exitosamente."}), 200

    except Exception as e:
        logger.exception(f"Error al rechazar la notificación {notification_id}.")
        db.session.rollback()
        return jsonify({"error": "Hubo un error al procesar la solicitud."}), 500

