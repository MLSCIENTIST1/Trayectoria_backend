from src.models.database import db
from src.models.usuarios import Usuario
from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from sqlalchemy.exc import SQLAlchemyError
import logging
from src.models.servicio import Servicio

# Configuración del Logger (solo una vez, evitando duplicaciones)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Configuración del StreamHandler
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)

# Definición del Blueprint
count_total_service_bp = Blueprint('count_total_service_bp', __name__)

@count_total_service_bp .route('/dashboard/total_services', methods=['GET'])
@login_required
def calcular_total_servicios():
    """
    API para calcular el número total de servicios asociados al usuario autenticado.
    Devuelve el conteo en formato JSON.
    """
    try:
        # Inicializa el contador con el servicio principal
        total_services = 1 if current_user.labor else 0

        # Contar servicios adicionales (usando el modelo Servicio directamente)
        additional_services = Servicio.query.filter_by(id_usuario=current_user.id_usuario).count()
        total_services += additional_services

        logger.info(f"Total de servicios calculados para el usuario {current_user.id_usuario}: {total_services}")
        return jsonify({"total_services": total_services}), 200

    except SQLAlchemyError as e:
        logger.exception("Error al calcular el total de servicios.")
        return jsonify({"error": "Hubo un problema al calcular el total de servicios."}), 500
