from src.models.database import db
from src.models.usuarios import Usuario
from flask import Blueprint, jsonify, request, session
from flask_login import login_user, login_required, current_user
import logging

# Configuración del Logger
logger = logging.getLogger(__name__)

# Blueprint para manejo de autenticación
# Nota: Al registrarlo, asegúrate de que esté dentro del prefijo 'api'
init_sesion_bp = Blueprint('init_sesion_bp', __name__)

@init_sesion_bp.route('/ingreso', methods=['POST'])
def ingreso():
    """
    API para manejar inicio de sesión.
    """
    logger.info("Solicitud de inicio de sesión recibida.")

    # 1. Verificar si ya está autenticado
    if current_user.is_authenticated:
        logger.info(f"El usuario {current_user.nombre} ya está autenticado.")
        return jsonify({
            "message": f"Ya has iniciado sesión como {current_user.nombre}",
            "user_id": current_user.id_usuario
        }), 200

    # 2. Obtener y validar datos
    data = request.get_json()
    if not data:
        logger.error("No se proporcionaron datos en la solicitud.")
        return jsonify({"error": "Datos no proporcionados"}), 400

    correo = data.get('correo', '').strip()
    # Soporta ambos nombres de campo para mayor flexibilidad con el Frontend
    password_input = data.get('password') or data.get('contrasenia', '').strip()

    if not correo or not password_input:
        return jsonify({"error": "Correo y contraseña son requeridos"}), 400

    # 3. Control de intentos de inicio de sesión (Brute Force Protection)
    if 'login_attempts' not in session:
        session['login_attempts'] = 0

    if session['login_attempts'] >= 5:
        logger.warning(f"Intentos fallidos excedidos para el correo: {correo}")
        return jsonify({"error": "Has alcanzado el número máximo de intentos. Intenta más tarde."}), 429

    try:
        # 4. Buscar usuario y verificar credenciales
        usuario = Usuario.query.filter_by(correo=correo).first()
        
        if not usuario:
            session['login_attempts'] += 1
            logger.debug(f"Usuario no encontrado: {correo}")
            return jsonify({"error": "Correo o contraseña incorrectos."}), 401

        if not usuario.active:
            logger.warning(f"Intento de acceso a cuenta inactiva: {correo}")
            return jsonify({"error": "Tu cuenta está desactivada. Contacta con soporte."}), 403

        # 5. Verificación de contraseña usando el método del modelo
        if usuario.check_password(password_input):
            login_user(usuario)
            session['login_attempts'] = 0  # Reset de intentos
            session.permanent = True       # Mantener la sesión según la config
            
            logger.info(f"Inicio de sesión exitoso: {correo}")
            return jsonify({
                "message": "Inicio de sesión exitoso.",
                "user": {
                    "id": usuario.id_usuario,
                    "nombre": usuario.nombre,
                    "correo": usuario.correo
                }
            }), 200
        else:
            session['login_attempts'] += 1
            logger.debug(f"Contraseña incorrecta para: {correo}")
            return jsonify({"error": "Correo o contraseña incorrectos."}), 401

    except Exception as e:
        logger.exception("Error crítico durante la autenticación.")
        return jsonify({"error": "Error interno del servidor"}), 500

    finally:
        logger.info("Finalizando ejecución de la API ingreso.")