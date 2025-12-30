import logging
from flask import Blueprint, jsonify
from flask_login import logout_user

# Configuración del Logger (Única vez)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

if not logger.handlers:  # Asegurar que no haya duplicados en los manejadores
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    ch.setFormatter(formatter)
    logger.addHandler(ch)

# Blueprint para cierre de sesión
close_sesion_bp = Blueprint('close_sesion_bp', __name__)  # Nombre modificado para mantener consistencia con convenciones

# Definición del Blueprint
@close_sesion_bp.route('/logout', methods=['POST'])  # Cambié la ruta a un nombre más descriptivo
def logout():
    """
    API para cerrar la sesión del usuario autenticado.
    Devuelve una confirmación en formato JSON.
    """
    logger.info("Procesando solicitud POST para cerrar sesión.")

    try:
        # Cerrar la sesión del usuario
        logout_user()
        logger.info("La sesión se ha cerrado exitosamente.")
        return jsonify({"message": "La sesión se ha cerrado exitosamente."}), 200

    except Exception as e:
        logger.exception("Error al cerrar la sesión.")
        return jsonify({"error": "Hubo un problema al cerrar la sesión."}), 500
