from src.models.database import db
from src.models.usuarios import Usuario
import logging
from flask import Blueprint, jsonify
from flask_login import login_required, current_user
from sqlalchemy import and_, or_

# Configuración del Logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)

# Blueprint para el dashboard
dashboard_main_bp = Blueprint('dashboard_main_bp', __name__)

@dashboard_main_bp.route('/dashboard_main', methods=['POST'])
@login_required
def dashboard():
    """
    API para obtener estadísticas del usuario actual en el dashboard.
    Proporciona el conteo de contratos y calificaciones recibidas como contratante y contratado.
    """
    logger.info(f"Procesando solicitud GET para el dashboard del usuario {current_user.id_usuario}.")

    try:
        # Contar contratos vigentes donde el usuario es contratante
        contract_count_contratante = Servicio.query.filter_by(id_contratante=current_user.id_usuario).count()
        logger.debug(f"Cantidad de contratos actuales como contratante: {contract_count_contratante}")

        # Contar contratos vigentes donde el usuario es contratado
        contract_count_contratado = Servicio.query.filter_by(id_contratado=current_user.id_usuario).count()
        logger.debug(f"Cantidad de contratos actuales como contratado: {contract_count_contratado}")

        # Calificaciones recibidas como contratante
        calification_count_contratante = ServiceRatings.query.filter(
            and_(
                ServiceRatings.usuario_id == current_user.id_usuario,
                or_(
                    ServiceRatings.calificacion_recived_contratante1.isnot(None),
                    ServiceRatings.calificacion_recived_contratante2.isnot(None),
                    ServiceRatings.calificacion_recived_contratante3.isnot(None)
                )
            )
        ).count()
        logger.debug(f"Cantidad de calificaciones recibidas como contratante: {calification_count_contratante}")

        # Calificaciones recibidas como contratado
        calification_count_contratado = ServiceRatings.query.filter(
            and_(
                ServiceRatings.usuario_id == current_user.id_usuario,
                or_(
                    ServiceRatings.calificacion_recived_contratado1.isnot(None),
                    ServiceRatings.calificacion_recived_contratado2.isnot(None),
                    ServiceRatings.calificacion_recived_contratado3.isnot(None)
                )
            )
        ).count()
        logger.debug(f"Cantidad de calificaciones recibidas como contratado: {calification_count_contratado}")

        # Devolver datos en formato JSON
        logger.info("Estadísticas del dashboard obtenidas correctamente.")
        return jsonify({
            "contract_count_contratante": contract_count_contratante,
            "contract_count_contratado": contract_count_contratado,
            "calification_count_contratante": calification_count_contratante,
            "calification_count_contratado": calification_count_contratado
        }), 200

    except Exception as e:
        logger.exception("Error al cargar el dashboard.")
        return jsonify({"error": "Hubo un error al cargar los datos del dashboard."}), 500
