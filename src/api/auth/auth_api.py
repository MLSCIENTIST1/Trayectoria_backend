import logging
from flask import Blueprint, request, jsonify, session
from flask_login import login_user, current_user, logout_user
from src.models.usuarios import Usuario

# Configuración de Logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Definición del Blueprint
auth_api_bp = Blueprint('auth_api', __name__)

@auth_api_bp.route('/login', methods=['POST'])
def login_api():
    logger.info("--- Nueva solicitud de inicio de sesión ---")
    
    # 1. Si ya está autenticado, devolvemos sus datos con la REDUNDANCIA
    if current_user.is_authenticated:
        return jsonify({
            "message": "Sesión ya activa",
            "user": {
                "nombre": current_user.nombre,
                "correo": current_user.correo,
                "id": current_user.id_usuario,
                "id_usuario": current_user.id_usuario # Redundancia para iFrames
            }
        }), 200

    # 2. Obtener y validar datos
    data = request.get_json()
    if not data:
        return jsonify({"error": "No se proporcionaron datos"}), 400

    correo = data.get('correo', '').strip()
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
            login_user(usuario, remember=True) 
            session['login_attempts'] = 0 
            session.permanent = True 
            
            logger.info(f"Login exitoso: {correo} (ID: {usuario.id_usuario})")
            
            # --- RESPUESTA REDUNDANTE CORREGIDA ---
            return jsonify({
                "message": "Inicio de sesión exitoso",
                "token": "session_active",
                "user": {
                    "nombre": usuario.nombre,
                    "correo": usuario.correo,
                    "id": usuario.id_usuario,         # Llave estándar para el Front
                    "id_usuario": usuario.id_usuario  # Llave explícita (Bypass de errores)
                }
            }), 200
        else:
            session['login_attempts'] += 1
            return jsonify({"error": "Correo o contraseña incorrectos"}), 401

    except Exception as e:
        logger.error(f"Error crítico en login: {str(e)}", exc_info=True)
        return jsonify({"error": "Error interno del servidor"}), 500

# Endpoint de estatus también con redundancia
@auth_api_bp.route('/session_status', methods=['GET'])
def session_status():
    if current_user.is_authenticated:
        return jsonify({
            "authenticated": True,
            "user": {
                "nombre": current_user.nombre,
                "correo": current_user.correo,
                "id": current_user.id_usuario,
                "id_usuario": current_user.id_usuario
            }
        }), 200
    return jsonify({"authenticated": False, "error": "Sesión expirada"}), 401

@auth_api_bp.route('/logout', methods=['POST', 'GET'])
def logout():
    logout_user()
    session.clear()
    response = make_response(jsonify({"message": "Sesión cerrada correctamente"}), 200)
    # Borramos la cookie de sesión de Flask explícitamente
    response.set_cookie('session', '', expires=0)
    return response