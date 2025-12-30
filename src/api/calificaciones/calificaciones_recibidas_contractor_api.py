import logging
from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from sqlalchemy import and_, or_
from src.models.database import db
from src.models.usuarios import Usuario  # Relación con Usuario
from src.models.usuario_servicio import usuario_servicio  # Tabla intermedia
from src.models.colombia_data.colombia_data import Colombia  # Relación con Colombia
from src.models.colombia_data.ratings.service_ratings import ServiceRatings  # Relación con Ratings
from src.models.colombia_data.ratings.service_overall_scores import ServiceOverallScores  # Relación con Overall Scores
from src.models.etapa import Etapa  # Relación con Etapa

# Configuración del Logger
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

logger.debug("Modelo y Blueprint cargados correctamente.")

# Asignación del Blueprint
calificaciones_recibidas_contractor_bp = Blueprint('calificaciones_recibidas_contractor_bp', __name__)

@calificaciones_recibidas_contractor_bp.route('/recibidas', methods=['POST'])
@login_required
def procesar_calificaciones_contractor():
    """
    API para obtener las calificaciones recibidas por el contractor en sus servicios.
    Devuelve una lista en formato JSON con las calificaciones relacionadas.
    """
    logger.info("Procesando solicitud POST para obtener calificaciones recibidas como contractor.")

    try:
        # Consultar las calificaciones relacionadas al contractor actual
        calificaciones = ServiceRatings.query.join(Servicio).filter(
            and_(
                Servicio.id_contratante == current_user.id_usuario,
                or_(
                    ServiceRatings.calificacion_recived_contratante1.isnot(None),
                    ServiceRatings.calificacion_recived_contratante2.isnot(None),
                    ServiceRatings.calificacion_recived_contratante3.isnot(None)
                )
            )
        ).all()

        logger.debug(f"Calificaciones recibidas como contractor: {[c.id_rating for c in calificaciones]}")

        # Crear una lista con los datos a devolver
        calificaciones_data = [
            {
                "id_rating": calificacion.id_rating,
                "calificacion1": calificacion.calificacion_recived_contratante1,
                "calificacion2": calificacion.calificacion_recived_contratante2,
                "calificacion3": calificacion.calificacion_recived_contratante3,
                "comentario": calificacion.comentary_employer_hired
            }
            for calificacion in calificaciones
        ]

        # Devolver datos en formato JSON
        return jsonify({
            "calificaciones": calificaciones_data,
            "rol": "contractor"
        }), 200

    except Exception as e:
        logger.exception("Error al obtener calificaciones recibidas como contractor.")
        return jsonify({"error": "Hubo un error al cargar las calificaciones."}), 500
