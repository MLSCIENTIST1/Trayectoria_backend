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

# Blueprint para el chat
chat_bp = Blueprint('chat_bp', __name__)

@chat_bp.route('/chat', methods=['POST'])
@login_required
def chat(notification_id):
    """
    API para obtener la conversación de un chat asociado a una notificación específica.
    Devuelve los mensajes en formato JSON y valida el acceso del usuario.
    """
    logger.info(f"Procesando solicitud POST para el chat asociado a la notificación {notification_id}.")

    try:
        # Obtener la notificación
        notification = Notification.query.get_or_404(notification_id)
        logger.debug(f"Notificación obtenida - ID: {notification.id}, Receptor (user_id): {notification.user_id}, Remitente (sender_id): {notification.sender_id}")

        # Verificar autorización
        if current_user.id_usuario not in [notification.user_id, notification.sender_id]:
            logger.warning(f"Acceso denegado: Usuario {current_user.id_usuario} no tiene acceso a la notificación {notification.id}")
            return jsonify({"error": "No estás autorizado para ver esta conversación."}), 403

        # Obtener mensajes asociados
        messages = Message.query.filter_by(notification_id=notification_id).order_by(Message.timestamp).all()
        logger.debug(f"Mensajes encontrados: {[message.id for message in messages]}")

        # Si no hay mensajes
        if not messages:
            logger.info(f"No hay mensajes asociados a la notificación {notification_id}.")
            return jsonify({"message": "No hay mensajes en esta conversación.", "messages": []}), 200

        # Formatear los mensajes
        messages_data = [
            {
                "id": message.id,
                "timestamp": message.timestamp.isoformat(),
                "sender_id": message.sender_id,
                "content": message.content
            }
            for message in messages
        ]

        # Devolver datos en formato JSON
        logger.info(f"Conversación cargada con éxito para la notificación {notification_id}.")
        return jsonify({
            "notification_id": notification.id,
            "messages": messages_data
        }), 200

    except Exception as e:
        logger.exception(f"Error al cargar la conversación asociada a la notificación {notification_id}.")
        return jsonify({"error": "No se pudo cargar la conversación."}), 500
