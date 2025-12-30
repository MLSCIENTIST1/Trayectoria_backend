from src.models.database import db
from src.models.usuarios import Usuario
import logging
from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.sql import func

# Configuración del Logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)

# Blueprint para notificaciones
notifications_bp = Blueprint('notifications_bp', __name__)

@notifications_bp.route('/notifications', methods=['POST'])
@login_required
def notifications(candidato_id):
    """
    API para enviar una solicitud de contratación a un candidato.
    Valida la existencia del candidato y el servicio, previene notificaciones duplicadas y registra la solicitud.
    """
    logger.info(f"Procesando solicitud POST para el candidato con ID {candidato_id}.")

    try:
        # Buscar al candidato
        candidato = Usuario.query.get_or_404(candidato_id)
        logger.debug(f"Candidato encontrado: ID: {candidato.id_usuario}, Nombre: {candidato.nombre}")

        # Obtener mensaje del usuario y, opcionalmente, el ID del servicio
        data = request.get_json()
        user_message = data.get('mensaje')
        id_service = data.get('id_service')
        service_details = None

        if id_service:
            # Buscar información del servicio especificado
            service_details = Servicio.query.filter_by(id_servicio=id_service, id_usuario=candidato.id_usuario).first()
            if not service_details:
                logger.warning(f"El servicio con ID {id_service} no existe o no pertenece al candidato con ID {candidato_id}.")
                return jsonify({"error": "El servicio seleccionado no existe o no pertenece al candidato."}), 404

        # Generar el mensaje de notificación
        if service_details:
            notification_message = (
                f'{current_user.nombre} te ha enviado una solicitud de contratación para el servicio: {service_details.nombre_servicio}. '
                f'Mensaje: {user_message}'
            )
        else:
            notification_message = (
                f'{current_user.nombre} te ha enviado una solicitud de contratación para el puesto de {candidato.labor}. '
                f'Mensaje: {user_message}'
            )

        logger.debug(f"Mensaje de notificación generado: {notification_message}")

        # Prevenir notificaciones duplicadas
        if Notification.query.filter_by(user_id=candidato.id_usuario, message=notification_message).first():
            logger.warning(f"Ya existe una notificación con el mismo mensaje para el candidato con ID {candidato_id}.")
            return jsonify({"error": "Ya se ha enviado una solicitud de contratación a este candidato."}), 400

        # Generar un nuevo request_id
        try:
            request_id = db.session.query(func.coalesce(func.max(Notification.request_id), 0) + 1).scalar()
            logger.debug(f"Nuevo request_id generado: {request_id}")
        except SQLAlchemyError:
            logger.exception("Error al calcular el request_id.")
            return jsonify({"error": "Error interno al calcular el ID de solicitud."}), 500

        # Crear la notificación y registrar el mensaje
        new_notification = Notification.create_notification(
            user_id=candidato.id_usuario,
            sender_id=current_user.id_usuario,
            request_id=request_id,
            message=notification_message,
            params={'type': 'contract_request'},
            extra_data={"sender_id": current_user.id_usuario}
        )

        new_message = Message(
            notification_id=new_notification.id,
            sender_id=current_user.id_usuario,
            receiver_id=candidato.id_usuario,
            content=user_message
        )
        db.session.add(new_message)
        db.session.commit()

        logger.info(f"Notificación creada con ID {new_notification.id} y request_id {new_notification.request_id}")
        logger.info(f"Mensaje creado con ID {new_message.id}")

        # Respuesta exitosa
        return jsonify({"message": "Solicitud de contratación registrada correctamente."}), 200

    except SQLAlchemyError:
        logger.exception("Error al registrar la solicitud en la base de datos.")
        db.session.rollback()
        return jsonify({"error": "Error interno al registrar la solicitud de contratación."}), 500

    except Exception as e:
        logger.exception("Error general en el proceso.")
        return jsonify({"error": f"Error al enviar la solicitud: {str(e)}"}), 500
