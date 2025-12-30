import logging
from flask import Blueprint, request, jsonify, session
from flask_login import login_user, current_user
from src.models.usuarios import Usuario

# Configuración de Logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)

# Definición del Blueprint
auth_api_bp = Blueprint('auth_api', __name__)

@auth_api_bp.route('/login', methods=['POST'])
def login_api():
    logger.info("Solicitud de inicio de sesión recibida.")
    
    # Verificar si el usuario ya está autenticado
    if current_user.is_authenticated:
        logger.info(f"El usuario {current_user.nombre} ya está autenticado.")
        return jsonify({"message": f"Ya has iniciado sesión como {current_user.nombre}"}), 200

    # Obtener datos de la solicitud JSON
    data = request.get_json()
    logger.debug(f"Datos recibidos en la solicitud: {data}")
    
    if not data:
        logger.error("No se proporcionaron datos en la solicitud.")
        return jsonify({"error": "Datos no proporcionados"}), 400

    # Extraer campos del JSON
    correo = data.get('correo', '').strip()
    password_input = data.get('password', '').strip()
    logger.debug(f"Datos procesados: correo={correo}, password_input={'*' * len(password_input)}")

    # Manejo de intentos fallidos
    if 'login_attempts' not in session:
        logger.debug("Inicializando contador de intentos de inicio de sesión.")
        session['login_attempts'] = 0

    if session['login_attempts'] >= 5:
        logger.warning("Intentos fallidos excedidos para inicio de sesión.")
        return jsonify({"error": "Has alcanzado el número máximo de intentos. Intenta más tarde."}), 429

    try:
        # Buscar al usuario en la base de datos
        logger.info(f"Buscando usuario con correo: {correo}")
        usuario = Usuario.query.filter_by(correo=correo).first()
        
        if not usuario:
            logger.warning(f"No se encontró un usuario con el correo: {correo}")
            session['login_attempts'] += 1
            logger.debug(f"Número de intentos de inicio de sesión actualizados: {session['login_attempts']}")
            return jsonify({"error": "Correo o contraseña incorrectos."}), 401

        # Verificar si la cuenta está activa
        if not usuario.active:
            logger.info(f"Usuario {correo} desactivado.")
            return jsonify({"error": "Tu cuenta está desactivada. Contacta con soporte para reactivarla."}), 403

        # Verificar la contraseña
        logger.info("Verificando contraseña del usuario...")
        if usuario.check_password(password_input):
            logger.info(f"Inicio de sesión exitoso para el usuario: {correo}")
            login_user(usuario)
            session['login_attempts'] = 0  # Reiniciar intentos fallidos
            logger.debug("Intentos de inicio de sesión reiniciados.")
            return jsonify({"message": "Inicio de sesión exitoso."}), 200
        else:
            logger.warning(f"Contraseña incorrecta para el usuario {correo}.")
            session['login_attempts'] += 1
            logger.debug(f"Número de intentos de inicio de sesión actualizados: {session['login_attempts']}")
            return jsonify({"error": "Correo o contraseña incorrectos."}), 401

    except Exception as e:
        logger.error(f"Error durante la autenticación: {e}", exc_info=True)
        return jsonify({"error": "Error interno del servidor"}), 500