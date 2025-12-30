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

# Blueprint para baja lógica del usuario
logic_delete_user_bp = Blueprint('logic_delete_user_bp', __name__)

@logic_delete_user_bp.route('/logic_delete_user', methods=['POST'])
@login_required
def logic_delete_user():
    """
    API para realizar la baja lógica de un usuario autenticado.
    Marca el usuario como inactivo en la base de datos.
    """
    logger.info(f"Procesando solicitud POST para baja lógica del usuario {current_user.id_usuario}.")

    try:
        # Información del usuario actual antes del cambio
        logger.debug(f"Usuario actual - ID: {current_user.id_usuario}, Estado activo antes del cambio: {current_user.active}")

        # Marcar al usuario como inactivo
        current_user.active = False
        logger.debug(f"Estado del usuario actualizado a inactivo (active=False).")

        # Guardar cambios en la base de datos
        db.session.commit()
        logger.info(f"Usuario con ID {current_user.id_usuario} marcado como inactivo en la base de datos.")

        # Devolver confirmación en formato JSON
        return jsonify({"message": "El perfil ha sido desactivado correctamente. Si deseas reactivarlo, contacta con soporte."}), 200

    except Exception as e:
        # Depurar errores
        logger.exception("Error al realizar la baja lógica del usuario.")

        # Revertir cambios en caso de error
        db.session.rollback()
        return jsonify({"error": "Hubo un problema al desactivar tu cuenta. Inténtalo de nuevo."}), 500
