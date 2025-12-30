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

# Blueprint para eliminar servicio principal
delete_principal_service_bp = Blueprint('delete_principal_service_bp', __name__)

@delete_principal_service_bp.route('/delete_principal_service', methods=['POST'])
@login_required
def delete_principal_service():
    """
    API para eliminar el servicio principal asociado al usuario autenticado.
    """
    logger.info("Procesando solicitud DELETE para eliminar el servicio principal.")

    try:
        # Eliminar el servicio principal del usuario actual
        current_user.labor = None
        db.session.commit()
        logger.info(f"Servicio principal eliminado para el usuario con ID {current_user.id_usuario}.")
        return jsonify({"message": "Servicio principal eliminado con éxito."}), 200

    except Exception as e:
        logger.exception("Error al eliminar el servicio principal.")
        return jsonify({"error": "Hubo un problema al eliminar el servicio principal."}), 500
