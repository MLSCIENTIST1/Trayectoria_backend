"""
BizFlow Studio - API de Recuperación de Contraseña
Endpoints para solicitar y procesar reset de password
CORREGIDO: SSL puerto 465 + envío asíncrono
"""

import os
import logging
from flask import Blueprint, request, jsonify, render_template_string, current_app
from flask_mail import Mail, Message
from threading import Thread
from src.models.database import db
from src.models.usuarios import Usuario
from src.models.password_reset_token import PasswordResetToken

logger = logging.getLogger(__name__)

# ==========================================
# BLUEPRINT
# ==========================================
password_reset_bp = Blueprint('password_reset', __name__, url_prefix='/api/auth')

# ==========================================
# CONFIGURACIÓN DE MAIL (se inicializa en init_mail)
# ==========================================
mail = None


def init_mail(app):
    """
    Inicializa Flask-Mail con la aplicación.
    Llamar desde create_app() en __init__.py
    CORREGIDO: Configuración para Namecheap Private Email (SSL 465)
    """
    global mail
    
    # ==========================================
    # CONFIGURACIÓN CORREGIDA PARA NAMECHEAP
    # ==========================================
    app.config['MAIL_SERVER'] = os.environ.get('MAIL_SERVER', 'mail.privateemail.com')
    app.config['MAIL_PORT'] = int(os.environ.get('MAIL_PORT', 465))  # ← CORREGIDO: 465
    app.config['MAIL_USE_TLS'] = False  # ← CORREGIDO: False
    app.config['MAIL_USE_SSL'] = True   # ← CORREGIDO: True
    app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME', 'noreply@tukomercio.store')
    app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')
    app.config['MAIL_DEFAULT_SENDER'] = ('TuKomercio', os.environ.get('MAIL_FROM', 'noreply@tukomercio.store'))
    app.config['MAIL_TIMEOUT'] = 10
    
    # URL del frontend para el link de reset
    app.config['FRONTEND_URL'] = os.environ.get('FRONTEND_URL', 'https://trayectoria-rxdc1.web.app')
    
    mail = Mail(app)
    logger.info(f"✅ Flask-Mail inicializado: {app.config['MAIL_SERVER']}:{app.config['MAIL_PORT']} SSL=True")
    
    return mail


# ==========================================
# ENVÍO ASÍNCRONO (CRÍTICO PARA EVITAR TIMEOUT)
# ==========================================
def send_async_email(app, msg):
    """Envía email en un thread separado para no bloquear el worker de Gunicorn"""
    with app.app_context():
        try:
            mail.send(msg)
            logger.info(f"✅ Email enviado exitosamente a: {msg.recipients}")
        except Exception as e:
            logger.error(f"❌ Error enviando email: {str(e)}")


def send_email_async(msg):
    """Wrapper para enviar email de forma asíncrono"""
    app = current_app._get_current_object()
    thread = Thread(target=send_async_email, args=(app, msg))
    thread.daemon = True
    thread.start()
    return thread


# ==========================================
# PLANTILLA DE EMAIL
# ==========================================
EMAIL_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Restablecer Contraseña</title>
</head>
<body style="margin: 0; padding: 0; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f4f4f4;">
    <table role="presentation" style="width: 100%; border-collapse: collapse;">
        <tr>
            <td align="center" style="padding: 40px 0;">
                <table role="presentation" style="width: 600px; border-collapse: collapse; background-color: #ffffff; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
                    <!-- Header -->
                    <tr>
                        <td style="padding: 40px 40px 20px; text-align: center; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 8px 8px 0 0;">
                            <h1 style="color: #ffffff; margin: 0; font-size: 28px;">🔐 TuKomercio</h1>
                            <p style="color: #e0e0e0; margin: 10px 0 0; font-size: 14px;">Sistema de Recuperación de Contraseña</p>
                        </td>
                    </tr>
                    
                    <!-- Body -->
                    <tr>
                        <td style="padding: 40px;">
                            <h2 style="color: #333; margin: 0 0 20px; font-size: 22px;">Hola {{ nombre }},</h2>
                            
                            <p style="color: #555; font-size: 16px; line-height: 1.6; margin: 0 0 20px;">
                                Recibimos una solicitud para restablecer la contraseña de tu cuenta asociada a <strong>{{ correo }}</strong>.
                            </p>
                            
                            <p style="color: #555; font-size: 16px; line-height: 1.6; margin: 0 0 30px;">
                                Haz clic en el siguiente botón para crear una nueva contraseña:
                            </p>
                            
                            <!-- Button -->
                            <table role="presentation" style="width: 100%; border-collapse: collapse;">
                                <tr>
                                    <td align="center">
                                        <a href="{{ reset_url }}" 
                                           style="display: inline-block; padding: 16px 40px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: #ffffff; text-decoration: none; border-radius: 50px; font-size: 16px; font-weight: bold; box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);">
                                            Restablecer Contraseña
                                        </a>
                                    </td>
                                </tr>
                            </table>
                            
                            <!-- Warning -->
                            <div style="margin-top: 30px; padding: 20px; background-color: #fff3cd; border-left: 4px solid #ffc107; border-radius: 4px;">
                                <p style="color: #856404; font-size: 14px; margin: 0;">
                                    ⚠️ <strong>Este enlace expira en 1 hora.</strong><br>
                                    Si no solicitaste este cambio, ignora este correo. Tu contraseña permanecerá igual.
                                </p>
                            </div>
                            
                            <!-- Alternative Link -->
                            <p style="color: #888; font-size: 13px; margin-top: 30px; word-break: break-all;">
                                Si el botón no funciona, copia y pega este enlace en tu navegador:<br>
                                <a href="{{ reset_url }}" style="color: #667eea;">{{ reset_url }}</a>
                            </p>
                        </td>
                    </tr>
                    
                    <!-- Footer -->
                    <tr>
                        <td style="padding: 30px 40px; background-color: #f8f9fa; border-radius: 0 0 8px 8px; text-align: center;">
                            <p style="color: #888; font-size: 12px; margin: 0;">
                                © 2026 TuKomercio - Todos los derechos reservados<br>
                                Este correo fue enviado automáticamente, por favor no respondas.
                            </p>
                        </td>
                    </tr>
                </table>
            </td>
        </tr>
    </table>
</body>
</html>
"""


# ==========================================
# ENDPOINTS
# ==========================================

@password_reset_bp.route('/forgot-password', methods=['POST'])
def forgot_password():
    """
    Solicita un token de reset de contraseña.
    Envía un email con el link de recuperación.
    
    Body JSON:
        - correo (str): Email del usuario
        
    Returns:
        JSON con mensaje de éxito (siempre, por seguridad)
    """
    global mail
    
    try:
        data = request.get_json()
        
        if not data or 'correo' not in data:
            return jsonify({
                "success": False,
                "message": "El correo electrónico es requerido"
            }), 400
        
        correo = data['correo'].lower().strip()
        logger.info(f"📧 Solicitud de reset para: {correo}")
        
        # Buscar usuario
        usuario = Usuario.query.filter_by(correo=correo).first()
        
        # IMPORTANTE: Siempre responder con éxito para no revelar si el email existe
        if not usuario:
            logger.warning(f"Intento de reset para correo no existente: {correo}")
            return jsonify({
                "success": True,
                "message": "Si el correo existe en nuestro sistema, recibirás un enlace de recuperación."
            }), 200
        
        # Verificar que el usuario esté activo
        if not usuario.active or usuario.black_list:
            logger.warning(f"Intento de reset para usuario inactivo/bloqueado: {correo}")
            return jsonify({
                "success": True,
                "message": "Si el correo existe en nuestro sistema, recibirás un enlace de recuperación."
            }), 200
        
        # Crear token
        token = PasswordResetToken.create_for_user(usuario.id_usuario)
        
        # Construir URL de reset
        frontend_url = os.environ.get('FRONTEND_URL', 'https://trayectoria-rxdc1.web.app')
        reset_url = f"{frontend_url}/reset-password.html?token={token.token}"
        
        # Renderizar email
        html_content = render_template_string(
            EMAIL_TEMPLATE,
            nombre=usuario.nombre or correo.split('@')[0],
            correo=usuario.correo,
            reset_url=reset_url
        )
        
        # Enviar email
        if mail:
            try:
                msg = Message(
                    subject="🔐 Restablecer tu contraseña - TuKomercio",
                    recipients=[usuario.correo],
                    html=html_content
                )
                
                # ✅ ENVÍO ASÍNCRONO - NO BLOQUEA EL WORKER
                send_email_async(msg)
                logger.info(f"✅ Email de reset encolado para: {correo}")
                
            except Exception as email_error:
                logger.error(f"❌ Error preparando email para {correo}: {email_error}")
                # No revelar el error al usuario
                return jsonify({
                    "success": False,
                    "message": "Error al procesar la solicitud. Intenta nuevamente."
                }), 500
        else:
            logger.error("❌ Flask-Mail no está inicializado")
            return jsonify({
                "success": False,
                "message": "Servicio de correo no disponible temporalmente."
            }), 503
        
        # Respuesta inmediata (no espera el envío del email)
        return jsonify({
            "success": True,
            "message": "Si el correo existe en nuestro sistema, recibirás un enlace de recuperación."
        }), 200
        
    except Exception as e:
        logger.error(f"❌ Error en forgot_password: {e}", exc_info=True)
        return jsonify({
            "success": False,
            "message": "Error interno del servidor"
        }), 500


@password_reset_bp.route('/verify-reset-token/<token>', methods=['GET'])
def verify_reset_token(token):
    """
    Verifica si un token de reset es válido.
    El frontend llama esto al cargar la página de reset.
    
    Args:
        token (str): Token de reset
        
    Returns:
        JSON indicando si el token es válido
    """
    try:
        reset_token = PasswordResetToken.get_valid_token(token)
        
        if not reset_token:
            return jsonify({
                "valid": False,
                "message": "El enlace ha expirado o es inválido. Solicita uno nuevo."
            }), 400
        
        # Obtener info del usuario (sin datos sensibles)
        usuario = Usuario.query.get(reset_token.user_id)
        
        return jsonify({
            "valid": True,
            "message": "Token válido",
            "user": {
                "nombre": usuario.nombre if usuario else None,
                "correo_parcial": _mask_email(usuario.correo) if usuario else None
            }
        }), 200
        
    except Exception as e:
        logger.error(f"❌ Error verificando token: {e}", exc_info=True)
        return jsonify({
            "valid": False,
            "message": "Error al verificar el token"
        }), 500


@password_reset_bp.route('/reset-password', methods=['POST'])
def reset_password():
    """
    Procesa el cambio de contraseña.
    
    Body JSON:
        - token (str): Token de reset
        - password (str): Nueva contraseña
        - confirm_password (str): Confirmación de contraseña
        
    Returns:
        JSON con resultado de la operación
    """
    try:
        data = request.get_json()
        
        # Validaciones
        if not data:
            return jsonify({
                "success": False,
                "message": "Datos requeridos"
            }), 400
        
        token_str = data.get('token')
        password = data.get('password')
        confirm_password = data.get('confirm_password')
        
        if not token_str:
            return jsonify({
                "success": False,
                "message": "Token requerido"
            }), 400
        
        if not password or not confirm_password:
            return jsonify({
                "success": False,
                "message": "La contraseña y su confirmación son requeridas"
            }), 400
        
        if password != confirm_password:
            return jsonify({
                "success": False,
                "message": "Las contraseñas no coinciden"
            }), 400
        
        if len(password) < 6:
            return jsonify({
                "success": False,
                "message": "La contraseña debe tener al menos 6 caracteres"
            }), 400
        
        # Verificar token
        reset_token = PasswordResetToken.get_valid_token(token_str)
        
        if not reset_token:
            return jsonify({
                "success": False,
                "message": "El enlace ha expirado o es inválido. Solicita uno nuevo."
            }), 400
        
        # Obtener usuario
        usuario = Usuario.query.get(reset_token.user_id)
        
        if not usuario:
            return jsonify({
                "success": False,
                "message": "Usuario no encontrado"
            }), 404
        
        # Actualizar contraseña
        usuario.set_password(password)
        
        # Marcar token como usado
        reset_token.mark_as_used()
        
        # Guardar cambios
        db.session.commit()
        
        logger.info(f"✅ Contraseña actualizada para: {usuario.correo}")
        
        return jsonify({
            "success": True,
            "message": "Contraseña actualizada exitosamente. Ya puedes iniciar sesión."
        }), 200
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"❌ Error reseteando contraseña: {e}", exc_info=True)
        return jsonify({
            "success": False,
            "message": "Error al actualizar la contraseña"
        }), 500


# ==========================================
# UTILIDADES
# ==========================================

def _mask_email(email):
    """
    Enmascara un email para mostrar parcialmente.
    ejemplo@gmail.com -> ej***@gmail.com
    """
    if not email or '@' not in email:
        return None
    
    local, domain = email.split('@')
    
    if len(local) <= 2:
        masked_local = local[0] + '***'
    else:
        masked_local = local[:2] + '***'
    
    return f"{masked_local}@{domain}"