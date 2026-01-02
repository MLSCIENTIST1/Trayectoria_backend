from src.models.database import db
from src.models.usuarios import Usuario
from flask import Blueprint, jsonify, request, session, make_response
from flask_login import login_user, login_required, current_user
import logging

# Configuración del Logger
logger = logging.getLogger(__name__)

# Blueprint para manejo de autenticación
init_sesion_bp = Blueprint('init_sesion_bp', __name__)

@init_sesion_bp.route('/ingreso', methods=['POST'])
def ingreso():
    """
    API para manejar inicio de sesión con persistencia reforzada.
    """
    logger.info("--- Solicitud de inicio de sesión recibida ---")

    # 1. Verificar si ya está autenticado
    if current_user.is_authenticated:
        logger.info(f"👤 Usuario {current_user.nombre} ya tiene sesión activa.")
        return jsonify({
            "message": f"Ya has iniciado sesión como {current_user.nombre}",
            "user_id": current_user.id_usuario
        }), 200

    # 2. Obtener y validar datos
    data = request.get_json()
    if not data:
        logger.error("❌ No se proporcionaron datos JSON.")
        return jsonify({"error": "Datos no proporcionados"}), 400

    correo = data.get('correo', '').strip()
    password_input = data.get('password') or data.get('contrasenia', '').strip()

    if not correo or not password_input:
        return jsonify({"error": "Correo y contraseña son requeridos"}), 400

    # 3. Control de intentos (Brute Force Protection)
    if 'login_attempts' not in session:
        session['login_attempts'] = 0

    if session['login_attempts'] >= 5:
        logger.warning(f"🚫 Demasiados intentos para: {correo}")
        return jsonify({"error": "Demasiados intentos. Intenta más tarde."}), 429

    try:
        # 4. Buscar usuario
        usuario = Usuario.query.filter_by(correo=correo).first()
        
        if not usuario:
            session['login_attempts'] += 1
            return jsonify({"error": "Correo o contraseña incorrectos."}), 401

        if not usuario.active:
            return jsonify({"error": "Cuenta desactivada."}), 403

        # 5. Verificación y CREACIÓN DE SESIÓN
        if usuario.check_password(password_input):
            # login_user crea la sesión en el servidor
            # remember=True es vital para que la cookie no expire al cerrar el navegador
            login_user(usuario, remember=True)
            
            # Forzamos que la cookie sea permanente y se envíe inmediatamente
            session.permanent = True
            session['login_attempts'] = 0 
            
            logger.info(f"✅ Inicio de sesión exitoso: {correo}")
            
            # Creamos la respuesta
            response = make_response(jsonify({
                "message": "Inicio de sesión exitoso.",
                "user": {
                    "id": usuario.id_usuario,
                    "nombre": usuario.nombre,
                    "correo": usuario.correo
                }
            }), 200)
            
            return response
            
        else:
            session['login_attempts'] += 1
            logger.debug(f"❌ Contraseña incorrecta para: {correo}")
            return jsonify({"error": "Correo o contraseña incorrectos."}), 401

    except Exception as e:
        logger.exception("🔥 Error crítico en proceso de login.")
        return jsonify({"error": "Error interno del servidor"}), 500

    finally:
        logger.info("--- Finalizando ejecución de API ingreso ---")