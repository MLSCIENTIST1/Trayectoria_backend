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

# Blueprint para calificar al contratado
rate_hiree_bp = Blueprint('rate_hiree_bp', __name__)

@rate_hiree_bp.route('/rate_hiree', methods=['POST'])
def rate_contratado(servicio_id):
    """
    API para permitir que un contratado califique un servicio,
    validando que el usuario tenga permiso y que las calificaciones sean válidas.
    """
    logger.info(f"Procesando solicitud POST para calificar como contratado el servicio con ID: {servicio_id}")

    try:
        # Obtener el servicio
        servicio = Servicio.query.get_or_404(servicio_id)
        logger.debug(f"Servicio encontrado: {servicio}")

        # Validar que el usuario es el contratado
        if servicio.id_contratado != current_user.id_usuario:
            logger.warning(f"El usuario {current_user.id_usuario} no tiene permisos para calificar el servicio {servicio_id}.")
            return jsonify({"error": "No tienes permisos para calificar como contratado."}), 403

        # Obtener datos del formulario
        cal1 = request.json.get('cal_contratado1', type=int)
        cal2 = request.json.get('cal_contratado2', type=int)
        cal3 = request.json.get('cal_contratado3', type=int)
        comentario = request.json.get('comentario_contratado', type=str)
        logger.debug(f"Datos recibidos: cal1={cal1}, cal2={cal2}, cal3={cal3}, comentario={comentario}")

        # Validar valores
        if not (1 <= cal1 <= 10 and 1 <= cal2 <= 10 and 1 <= cal3 <= 10):
            logger.warning("Las calificaciones recibidas no están en el rango válido (1-10).")
            return jsonify({"error": "Las calificaciones deben estar entre 1 y 10."}), 400

        # Crear o actualizar la calificación
        calificacion = ServiceRatings.query.filter_by(servicio_id=servicio.id_servicio, usuario_id=current_user.id_usuario).first()
        if not calificacion:
            calificacion = ServiceRatings(
                servicio_id=servicio.id_servicio,
                usuario_id=current_user.id_usuario,
                calificacion_recived_contratado1=cal1,
                calificacion_recived_contratado2=cal2,
                calificacion_recived_contratado3=cal3,
                comentary_hired_employer=comentario
            )
            db.session.add(calificacion)
            logger.info("Nueva calificación creada con éxito.")
        else:
            calificacion.calificacion_recived_contratado1 = cal1
            calificacion.calificacion_recived_contratado2 = cal2
            calificacion.calificacion_recived_contratado3 = cal3
            calificacion.comentary_hired_employer = comentario
            logger.info("Calificación existente actualizada con éxito.")

        # Guardar cambios en la base de datos
        db.session.commit()
        logger.info("Cambios guardados en la base de datos.")
        return jsonify({"message": "Calificación como contratado guardada correctamente."}), 200

    except Exception as e:
        logger.exception("Error al procesar la calificación como contratado.")
        db.session.rollback()
        return jsonify({"error": "Hubo un error al procesar la calificación."}), 500

# pare
