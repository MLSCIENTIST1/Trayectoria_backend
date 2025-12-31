import logging
from flask import Blueprint, request, jsonify, session
from flask_login import login_user, current_user
from src.models.usuarios import Usuario

# Configuración de Logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Definición del Blueprint
auth_api_bp = Blueprint('auth_api', __name__)

@auth_api_bp.route('/login', methods=['POST'])
def login_api():
    logger.info("--- Nueva solicitud de inicio de sesión ---")
    
    # 1. Verificar si el usuario ya está autenticado
    if current_user.is_authenticated:
        return jsonify({"message": f"Ya has iniciado sesión como {current_user.nombre}"}), 200

    # 2. Obtener y validar datos JSON
    data = request.get_json()
    if not data:
        return jsonify({"error": "No se proporcionaron datos"}), 400

    correo = data.get('correo', '').strip()
    # Aceptamos ambos nombres para evitar errores entre front y back
    password_input = (data.get('password') or data.get('contrasenia') or '').strip()

    if not correo or not password_input:
        return jsonify({"error": "Correo y contraseña son requeridos"}), 400

    # 3. Manejo de intentos fallidos (Seguridad)
    if 'login_attempts' not in session:
        session['login_attempts'] = 0

    if session['login_attempts'] >= 5:
        logger.warning(f"Bloqueo temporal por intentos fallidos: {correo}")
        return jsonify({"error": "Demasiados intentos. Intenta más tarde."}), 429

    try:
        # 4. Buscar usuario
        usuario = Usuario.query.filter_by(correo=correo).first()
        
        if not usuario:
            logger.warning(f"Usuario no encontrado: {correo}")
            session['login_attempts'] += 1
            return jsonify({"error": "Correo o contraseña incorrectos"}), 401

        if not usuario.active:
            return jsonify({"error": "Cuenta desactivada. Contacta a soporte."}), 403

        # 5. VERIFICACIÓN DE BCRYPT (Aquí ocurre la magia)
        # El método check_password de tu modelo hace el bcrypt.checkpw internamente
        if usuario.check_password(password_input):
            logger.info(f"Login exitoso: {correo}")
            login_user(usuario)
            session['login_attempts'] = 0  # Reiniciar contador
            
            return jsonify({
                "message": "Inicio de sesión exitoso",
                "user": {
                    "nombre": usuario.nombre,
                    "correo": usuario.correo,
                    "id": usuario.id_usuario
                }
            }), 200
        else:
            logger.warning(f"Contraseña incorrecta para: {correo}")
            session['login_attempts'] += 1
            return jsonify({"error": "Correo o contraseña incorrectos"}), 401

    except Exception as e:
        logger.error(f"Error crítico en login: {str(e)}", exc_info=True)
        return jsonify({"error": "Error interno del servidor"}), 500