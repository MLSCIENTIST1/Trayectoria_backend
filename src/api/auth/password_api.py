import logging
from flask import Blueprint, jsonify, request
from flask_login import login_required
import bcrypt

# Configuración del Logger (Única vez)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

if not logger.handlers:  # Verificar que no haya manejadores duplicados
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    ch.setFormatter(formatter)
    logger.addHandler(ch)

# Blueprint para manejo de contraseñas
password_bp = Blueprint('password_bp', __name__)

@password_bp.route('/password_api', methods=['POST'])
def hash_password():
    """
    API para hashear una contraseña proporcionada por el cliente utilizando bcrypt.
    Devuelve el hash en formato JSON.
    """
    logger.info("Procesando solicitud POST para hashear contraseña.")

    try:
        # Obtener la contraseña desde el body de la solicitud
        data = request.get_json()
        password = data.get('password')
        logger.debug(f"Contraseña recibida para hash: {password}")

        # Validar que la contraseña está presente
        if not password:
            logger.warning("No se proporcionó una contraseña.")
            return jsonify({"error": "No se proporcionó una contraseña."}), 400

        # Generar el hash de la contraseña
        salt = bcrypt.gensalt()
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
        logger.info("Contraseña hasheada exitosamente.")

        # Devolver el hash en formato JSON
        return jsonify({"hashed_password": hashed_password}), 200

    except Exception as e:
        logger.exception("Error al hashear la contraseña.")
        return jsonify({"error": "Hubo un problema al procesar la solicitud."}), 500
