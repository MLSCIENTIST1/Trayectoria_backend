import logging
from flask import Blueprint, request, jsonify, session, make_response
from flask_login import login_user, current_user, logout_user, login_required
from src.models.usuarios import Usuario

# Configuración de Logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Definición del Blueprint
auth_api_bp = Blueprint('auth_api', __name__)

@auth_api_bp.route('/login', methods=['POST'])
def login_api():
    logger.info("--- Nueva solicitud de inicio de sesión ---")
    
    # 1. Si ya está autenticado, devolvemos sus datos directamente
    if current_user.is_authenticated:
        return jsonify({
            "message": "Sesión ya activa",
            "user": {
                "nombre": current_user.nombre,
                "correo": current_user.correo,
                "id": current_user.id_usuario
            }
        }), 200

    # 2. Obtener y validar datos
    data = request.get_json()
    if not data:
        return jsonify({"error": "No se proporcionaron datos"}), 400

    correo = data.get('correo', '').strip()
    # Soporte para ambos nombres de campo (front/back)
    password_input = (data.get('password') or data.get('contrasenia') or '').strip()

    if not correo or not password_input:
        return jsonify({"error": "Correo y contraseña son requeridos"}), 400

    # 3. Control de intentos fallidos
    if 'login_attempts' not in session:
        session['login_attempts'] = 0

    if session['login_attempts'] >= 5:
        logger.warning(f"Bloqueo por intentos: {correo}")
        return jsonify({"error": "Demasiados intentos. Intenta más tarde."}), 429

    try:
        # 4. Buscar usuario en DB
        usuario = Usuario.query.filter_by(correo=correo).first()
        
        if not usuario:
            session['login_attempts'] += 1
            return jsonify({"error": "Correo o contraseña incorrectos"}), 401

        if not usuario.active:
            return jsonify({"error": "Cuenta desactivada. Contacta soporte."}), 403

        # 5. Validar contraseña
        if usuario.check_password(password_input):
            # login_user crea la sesión en Flask-Login
            login_user(usuario, remember=True) 
            session['login_attempts'] = 0 
            session.permanent = True # Hace que la sesión dure lo configurado en la app
            
            logger.info(f"Login exitoso: {correo}")
            return jsonify({
                "message": "Inicio de sesión exitoso",
                "token": "session_active", # Token simbólico para localStorage
                "user": {
                    "nombre": usuario.nombre,
                    "correo": usuario.correo,
                    "id": usuario.id_usuario
                }
            }), 200
        else:
            session['login_attempts'] += 1
            return jsonify({"error": "Correo o contraseña incorrectos"}), 401

    except Exception as e:
        logger.error(f"Error crítico en login: {str(e)}", exc_info=True)
        return jsonify({"error": "Error interno del servidor"}), 500

# --- ENDPOINT PARA VALIDAR SESIÓN DESDE BIZFLOW ---

@auth_api_bp.route('/session_status', methods=['GET'])
def session_status():
    """ Verifica si el usuario sigue logueado para permitir el uso de BizFlow """
    if current_user.is_authenticated:
        return jsonify({
            "authenticated": True,
            "user": {
                "nombre": current_user.nombre,
                "correo": current_user.correo,
                "id": current_user.id_usuario
            }
        }), 200
    
    return jsonify({
        "authenticated": False, 
        "error": "Sesión expirada"
    }), 401

# --- ENDPOINT PARA CERRAR SESIÓN ---

@auth_api_bp.route('/logout', methods=['POST', 'GET'])
def logout():
    """ Cierra la sesión detectando al usuario por sesión o por JSON explícito """
    
    # 1. Intentamos obtener el correo de la sesión de Flask (Cookie)
    correo = current_user.correo if current_user.is_authenticated else None
    
    # 2. Si es Anónimo, intentamos leer el JSON que mandó el JavaScript
    if not correo:
        data = request.get_json(silent=True) or {}
        correo = data.get('usuario') # El nombre que enviamos en logout.js

    # 3. Fallback final si nada funcionó
    if not correo:
        correo = "Anónimo"

    # Proceso de cierre
    logout_user()
    session.clear()
    
    logger.info(f"Sesión cerrada para: {correo}")
    return jsonify({"message": f"Sesión de {correo} cerrada correctamente"}), 200