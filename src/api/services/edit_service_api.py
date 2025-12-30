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

# Blueprint para la edición de servicios
edit_service_bp = Blueprint('edit_service_bp', __name__)

@edit_service_bp.route('/edit_service', methods=['POST'])
@login_required
def edit_service_page():
    """
    API para obtener los servicios principales y adicionales asociados al usuario actual.
    Devuelve los datos en formato JSON.
    """
    logger.info("Procesando solicitud POST para cargar la página de edición de servicios.")

    try:
        # Servicio principal del usuario
        principal_service = current_user.labor

        # Otros servicios asociados al usuario
        other_services = Servicio.query.filter_by(id_usuario=current_user.id_usuario).all()

        logger.debug(f"Servicios adicionales encontrados: {[s.nombre_servicio for s in other_services]}")

        # Construir los datos a devolver
        principal_service_data = {
            "id_servicio": principal_service.id_servicio if principal_service else None,
            "nombre_servicio": principal_service.nombre_servicio if principal_service else None,
            "descripcion": principal_service.descripcion if principal_service else None,
            "categoria": principal_service.categoria if principal_service else None,
            "precio": principal_service.precio if principal_service else None
        } if principal_service else None

        other_services_data = [
            {
                "id_servicio": service.id_servicio,
                "nombre_servicio": service.nombre_servicio,
                "descripcion": service.descripcion,
                "categoria": service.categoria,
                "precio": service.precio
            }
            for service in other_services
        ]

        logger.info("Datos procesados correctamente. Enviando respuesta al cliente.")
        return jsonify({
            "principal_service": principal_service_data,
            "other_services": other_services_data
        }), 200

    except Exception as e:
        logger.exception("Error al cargar la página de edición de servicios.")
        return jsonify({"error": "Hubo un error al cargar los servicios."}), 500
