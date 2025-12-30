from src.models.database import db
from src.models.usuarios import Usuario
from flask import Blueprint, jsonify, request, session
from flask_login import login_user, login_required, current_user
import logging

# Configuración del Logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)

# Blueprint para manejo de autenticación
init_sesion_bp= Blueprint('init_sesion_bp', __name__)

@init_sesion_bp.route('/ingreso', methods=['POST'])
def ingreso():
    """
    API para manejar inicio de sesión.
    """
    logger.info("Solicitud de inicio de sesión recibida.")

    if current_user.is_authenticated:
        logger.info(f"El usuario {current_user.nombre} ya está autenticado.")
        return jsonify({"message": f"Ya has iniciado sesión como {current_user.nombre}"}), 200

    data = request.get_json()
    if not data:
        logger.error("No se proporcionaron datos en la solicitud.")
        return jsonify({"error": "Datos no proporcionados"}), 400

    correo = data.get('correo', '').strip()
    password_input = data.get('password', '').strip()

    if 'login_attempts' not in session:
        session['login_attempts'] = 0

    if session['login_attempts'] >= 5:
        logger.warning("Intentos fallidos excedidos para inicio de sesión.")
        return jsonify({"error": "Has alcanzado el número máximo de intentos. Intenta más tarde."}), 429

    try:
        usuario = Usuario.query.filter_by(correo=correo).first()
        if not usuario:
            session['login_attempts'] += 1
            return jsonify({"error": "Correo o contraseña incorrectos."}), 401

        if not usuario.active:
            return jsonify({"error": "Tu cuenta está desactivada. Contacta con soporte."}), 403

        if usuario.check_password(password_input):
            login_user(usuario)
            session['login_attempts'] = 0
            return jsonify({"message": "Inicio de sesión exitoso."}), 200
        else:
            session['login_attempts'] += 1
            return jsonify({"error": "Correo o contraseña incorrectos."}), 401

    except Exception as e:
        logger.exception("Error durante la autenticación.")
        return jsonify({"error": "Error interno del servidor"}), 500

    finally:
        logger.info("Finalizando ejecución de la API login.")
