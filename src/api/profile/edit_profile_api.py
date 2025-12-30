from src.models.database import db
from src.models.usuarios import Usuario
import logging
from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user

# Configuración del Logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)

# Blueprint para editar perfil
edit_profile_bp = Blueprint('edit_profile_bp', __name__)

@edit_profile_bp.route('/edit_profile', methods=['POST'])
@login_required
def edit_profile():
    """
    API para editar el perfil del usuario autenticado.
    Permite actualizar información como nombre, correo, etc.
    """
    logger.info(f"Procesando solicitud {request.method} para editar el perfil del usuario {current_user.id_usuario}.")

    try:
        # Obtener datos del formulario
        nombre = request.json.get('nombre', None)
        correo = request.json.get('correo', None)
        logger.debug(f"Datos recibidos para editar el perfil: nombre={nombre}, correo={correo}")

        # Validar que los datos no estén vacíos
        if not nombre or not correo:
            logger.warning("Faltan datos obligatorios para actualizar el perfil.")
            return jsonify({"error": "El nombre y el correo son obligatorios."}), 400

        # Actualizar la información del usuario
        usuario = Usuario.query.get(current_user.id_usuario)
        usuario.nombre = nombre
        usuario.correo = correo
        db.session.commit()
        logger.info("Perfil actualizado correctamente.")

        return jsonify({"message": "Perfil actualizado correctamente."}), 200

    except Exception as e:
        logger.exception("Error al actualizar el perfil.")
        db.session.rollback()
        return jsonify({"error": "Hubo un problema al actualizar el perfil."}), 500

    finally:
        logger.info("Finalizando ejecución de la API edit_profile.")
