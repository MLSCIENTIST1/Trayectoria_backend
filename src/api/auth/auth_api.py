import logging
from flask import Blueprint, request, jsonify, session
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
    
    if current_user.is_authenticated:
        return jsonify({"message": f"Ya has iniciado sesión como {current_user.nombre}"}), 200

    data = request.get_json()
    if not data:
        return jsonify({"error": "No se proporcionaron datos"}), 400

    correo = data.get('correo', '').strip()
    password_input = (data.get('password') or data.get('contrasenia') or '').strip()

    if not correo or not password_input:
        return jsonify({"error": "Correo y contraseña son requeridos"}), 400

    if 'login_attempts' not in session:
        session['login_attempts'] = 0

    if session['login_attempts'] >= 5:
        return jsonify({"error": "Demasiados intentos. Intenta más tarde."}), 429

    try:
        usuario = Usuario.query.filter_by(correo=correo).first()
        
        if not usuario:
            session['login_attempts'] += 1
            return jsonify({"error": "Correo o contraseña incorrectos"}), 401

        if not usuario.active:
            return jsonify({"error": "Cuenta desactivada."}), 403

        if usuario.check_password(password_input):
            login_user(usuario)
            session['login_attempts'] = 0 
            
            return jsonify({
                "message": "Inicio de sesión exitoso",
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

# --- NUEVO ENDPOINT PARA VALIDAR SESIÓN DESDE BIZFLOW ---

@auth_api_bp.route('/session_status', methods=['GET'])
def session_status():
    """
    Verifica si el usuario tiene una sesión activa en el servidor.
    Utilizado por BF.js para proteger rutas.
    """
    if current_user.is_authenticated:
        logger.info(f"Sesión validada para el usuario: {current_user.correo}")
        return jsonify({
            "authenticated": True,
            "user": {
                "nombre": current_user.nombre,
                "correo": current_user.correo
            }
        }), 200
    else:
        logger.warning("Intento de acceso sin sesión activa.")
        return jsonify({"authenticated": False, "error": "Sesión no válida"}), 401

@auth_api_bp.route('/logout', methods=['POST'])
@login_required
def logout():
    logout_user()
    session.clear()
    return jsonify({"message": "Sesión cerrada correctamente"}), 200