from src.models.database import db
from src.models.usuarios import Usuario
import logging
from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user

# Configuración del Logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)

# Blueprint para solicitar más detalles
request_more_details_bp = Blueprint('request_more_details_bp', __name__)

@request_more_details_bp.route('/prueba', methods=['POST'])
@login_required
def more_details(notification_id):
    """
    API para agregar un mensaje con preguntas adicionales asociado a una notificación específica.
    Valida la autorización del usuario y guarda el mensaje en la base de datos.
    """
    logger.info(f"Procesando solicitud POST para agregar detalles a la notificación {notification_id}.")

    try:
        # Obtener las preguntas desde el cuerpo de la solicitud
        data = request.get_json()
        questions = data.get('questions', '').strip()
        logger.debug(f"Pregunta recibida: {questions}")

        if not questions:
            logger.warning("No se proporcionaron preguntas en la solicitud.")
            return jsonify({"error": "Por favor, escribe una pregunta antes de enviar."}), 400

        # Verificar si la notificación existe
        notification = Notification.query.get_or_404(notification_id)
        logger.debug(f"Notificación obtenida - ID: {notification.id}, Receptor: {notification.user_id}, Remitente: {notification.sender_id}")

        # Validar que el usuario esté autorizado
        if current_user.id_usuario not in [notification.user_id, notification.sender_id]:
            logger.warning(f"Acceso denegado: Usuario {current_user.id_usuario} no está autorizado para la notificación {notification_id}.")
            return jsonify({"error": "No estás autorizado para realizar esta acción."}), 403

        # Crear el mensaje en la base de datos
        message = Message(
            notification_id=notification_id,
            sender_id=current_user.id_usuario,
            receiver_id=notification.sender_id if current_user.id_usuario == notification.user_id else notification.user_id,
            content=questions
        )
        db.session.add(message)
        db.session.commit()
        logger.info(f"Mensaje agregado exitosamente a la conversación para la notificación {notification_id}.")

        return jsonify({"message": "Mensaje enviado exitosamente."}), 200

    except Exception as e:
        logger.exception(f"Error al agregar mensaje para la notificación {notification_id}.")
        db.session.rollback()
        return jsonify({"error": "Hubo un error al procesar tu solicitud."}), 500
