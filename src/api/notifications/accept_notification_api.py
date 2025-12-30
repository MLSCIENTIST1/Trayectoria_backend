from src.models.database import db
from src.models.usuarios import Usuario
import logging
from flask import Blueprint, jsonify
from flask_login import login_required, current_user

# Configuración del Logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)

# Blueprint para aceptar notificaciones
accept_notification_bp = Blueprint('accept_notification_bp', __name__)

@accept_notification_bp.route('/accept_notification', methods=['POST'])
@login_required
def accept_notification(notification_id):
    """
    API para aceptar una notificación y crear un servicio asociado.
    Valida la autorización del usuario y actualiza el estado de la notificación y el servicio.
    """
    logger.info(f"Procesando solicitud POST para aceptar la notificación {notification_id}.")

    try:
        # Obtener la notificación
        notification = Notification.query.get_or_404(notification_id)
        logger.debug(f"Notificación obtenida - ID: {notification.id}, Usuario: {notification.user_id}, Aceptada: {notification.is_accepted}")

        # Verificar que el usuario esté autorizado
        if notification.user_id != current_user.id_usuario:
            logger.warning(f"Acceso denegado: Usuario {current_user.id_usuario} no está autorizado para aceptar la notificación {notification_id}.")
            return jsonify({"error": "Notificación no autorizada."}), 403

        # Validar si ya fue aceptada
        if notification.is_accepted:
            logger.info(f"Notificación {notification_id} ya aceptada previamente.")
            return jsonify({"message": "Ya has aceptado esta solicitud."}), 200

        # Marcar notificación como aceptada
        notification.is_accepted = True
        logger.debug(f"Notificación {notification_id} marcada como aceptada.")

        # Crear servicio desde la notificación
        servicio = create_service_from_notification(notification)
        servicio.id_contratado = current_user.id_usuario
        db.session.add(servicio)
        db.session.commit()
        logger.info(f"Servicio registrado y aceptado con éxito: {servicio}")

        # Devolver respuesta exitosa
        return jsonify({"message": f"Solicitud aceptada y servicio registrado con ID {servicio.id_servicio}."}), 200

    except Exception as e:
        logger.exception(f"Error al aceptar la notificación {notification_id}.")
        db.session.rollback()
        return jsonify({"error": "Hubo un error al procesar tu solicitud."}), 500
