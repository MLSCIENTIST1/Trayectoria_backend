from src.models.database import db
from src.models.usuarios import Usuario
import logging
from flask import Blueprint, jsonify, request
from flask_login import login_required

# Configuración del Logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)

# Blueprint para crear contratos
create_contract_bp = Blueprint('create-contract-bp', __name__)

@create_contract_bp.route('/prueba', methods=['POST'])
@login_required
def create_contract():
    """
    API para crear un contrato basado en notificación.
    """
    try:
        # Obtener datos de la solicitud
        notification_id = request.json.get('notification_id')

        notification = Notification.query.get_or_404(notification_id)

        # Depuración inicial
        logger.debug(f"Creando contrato desde notificación ID: {notification.id}")
        logger.debug(f"Notificación - User ID (Receptor): {notification.user_id}, Sender ID (Remitente): {notification.sender_id}")

        # Validar remitente
        sender = db.session.query(current_user.__class__).get(notification.sender_id)
        if not sender:
            logger.error(f"No se encontró el remitente con ID {notification.sender_id}.")
            return jsonify({"error": f"No se encontró el remitente con ID {notification.sender_id}."}), 404

        # Crear contrato como servicio
        servicio = Servicio(
            nombre_servicio=notification.message,
            fecha_solicitud=notification.timestamp.date(),
            fecha_aceptacion=datetime.utcnow().date(),
            fecha_inicio=datetime.utcnow().date(),
            fecha_fin=(datetime.utcnow().replace(year=datetime.utcnow().year + 1)).date(),
            nombre_contratante=sender.nombre,
            id_contratante=sender.id_usuario,
            id_usuario=current_user.id_usuario
        )
        logger.debug(f"Servicio preparado para guardar: {servicio}")

        # Guardar servicio en la base de datos
        db.session.add(servicio)
        db.session.commit()
        logger.info(f"Contrato creado exitosamente: {servicio}")

        # Respuesta JSON
        return jsonify({"message": "Contrato creado exitosamente.", "servicio_id": servicio.id_servicio}), 200

    except Exception as e:
        logger.exception("Error al crear contrato.")
        db.session.rollback()
        return jsonify({"error": "Hubo un problema al crear el contrato."}), 500
