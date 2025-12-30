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

# Blueprint para calificaciones recibidas por el contratado
calificaciones_recibidas_hiree_bp = Blueprint('calificaciones_recibidas_hiree_bp', __name__)

@calificaciones_recibidas_hiree_bp.route('/calificaciones_recibidas_hiree', methods=['POST'])
def calificaciones_recibidas_contratado():
    """
    API para obtener las calificaciones recibidas por el contratado en sus servicios.
    Devuelve una lista en formato JSON con las calificaciones relacionadas.
    """
    logger.info("Procesando solicitud GET para obtener calificaciones recibidas como contratado.")

    try:
        # Consultar las calificaciones relacionadas al contratado actual
        calificaciones = ServiceRatings.query.join(Servicio).filter(
            and_(
                Servicio.id_contratado == current_user.id_usuario,
                or_(
                    ServiceRatings.calificacion_recived_contratado1.isnot(None),
                    ServiceRatings.calificacion_recived_contratado2.isnot(None),
                    ServiceRatings.calificacion_recived_contratado3.isnot(None)
                )
            )
        ).all()

        logger.debug(f"Calificaciones recibidas como contratado: {[c.id_rating for c in calificaciones]}")

        # Crear una lista con los datos a devolver
        calificaciones_data = [
            {
                "id_rating": calificacion.id_rating,
                "calificacion1": calificacion.calificacion_recived_contratado1,
                "calificacion2": calificacion.calificacion_recived_contratado2,
                "calificacion3": calificacion.calificacion_recived_contratado3,
                "comentario": calificacion.comentary_hired_employer
            }
            for calificacion in calificaciones
        ]

        # Devolver datos en formato JSON
        logger.info("Calificaciones obtenidas con éxito. Enviando respuesta al cliente.")
        return jsonify({
            "calificaciones": calificaciones_data,
            "rol": "contratado"
        }), 200

    except Exception as e:
        logger.exception("Error al obtener calificaciones recibidas como contratado.")
        return jsonify({"error": "Hubo un error al cargar las calificaciones."}), 500

# pare
