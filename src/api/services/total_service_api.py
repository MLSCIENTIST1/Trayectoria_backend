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

# Blueprint para calcular el total de servicios
total_service_bp = Blueprint('total_service_bp', __name__)

@total_service_bp.route('/total_service', methods=['POST'])
@login_required
def calcular_total_servicios():
    """
    API para calcular el número total de servicios de un usuario.
    Incluye el servicio principal y los servicios adicionales.
    Devuelve el total en formato JSON.
    """
    logger.info(f"Procesando solicitud POST para calcular el total de servicios del usuario {current_user.id_usuario}.")

    try:
        # Inicializar contador con el servicio principal
        total_services = 1 if current_user.labor else 0
        logger.debug(f"Servicio principal incluido en el total: {'Sí' if total_services > 0 else 'No'}")

        # Contar servicios adicionales
        additional_services = Servicio.query.filter_by(id_usuario=current_user.id_usuario).count()
        total_services += additional_services
        logger.debug(f"Servicios adicionales calculados: {additional_services}")

        # Devolver datos en formato JSON
        logger.info("Total de servicios calculados con éxito.")
        return jsonify({"total_services": total_services}), 200

    except SQLAlchemyError as e:
        logger.error(f"Error en la base de datos al calcular el total de servicios: {e}")
        return jsonify({"error": "Hubo un problema al calcular el total de servicios."}), 500

    except Exception as e:
        logger.exception("Error inesperado al calcular el total de servicios.")
        return jsonify({"error": "Hubo un problema inesperado."}), 500
