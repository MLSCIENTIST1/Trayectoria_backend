"""
BizFlow Studio - API de Recuperación de Contraseña
SOLUCIÓN: Usa Resend API (HTTP) en lugar de SMTP (bloqueado en Render)

Instalar: pip install resend
Variable de entorno: RESEND_API_KEY=re_xxxxxxxxx
"""

import os
import logging
import traceback
import requests
from flask import Blueprint, request, jsonify, render_template_string, current_app
from threading import Thread
from src.models.database import db
from src.models.usuarios import Usuario
from src.models.password_reset_token import PasswordResetToken

# ==========================================
# LOGGING
# ==========================================
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# ==========================================
# BLUEPRINT
# ==========================================
password_reset_bp = Blueprint('password_reset', __name__, url_prefix='/api/auth')


def init_mail(app):
    """
    Inicializa la configuración de email.
    Ya no usa Flask-Mail, usa Resend API.
    """
    resend_key = os.environ.get('RESEND_API_KEY', '')
    
    logger.info("=" * 60)
    logger.info("🚀 CONFIGURACIÓN DE EMAIL (RESEND API)")
    logger.info("=" * 60)
    logger.info(f"📧 RESEND_API_KEY configurada: {'✅ SÍ' if resend_key else '❌ NO'}")
    logger.info(f"📧 FRONTEND_URL: {os.environ.get('FRONTEND_URL', 'https://trayectoria-rxdc1.web.app')}")
    logger.info("=" * 60)
    
    return None  # No necesitamos objeto mail


# ==========================================
# ENVÍO DE EMAIL CON RESEND (HTTP API)
# ==========================================
def send_email_resend(to_email, subject, html_content):
    """
    Envía email usando Resend API (HTTP - no bloqueado)
    """
    api_key = os.environ.get('RESEND_API_KEY', '')
    from_email = os.environ.get('MAIL_FROM', 'noreply@tukomercio.store')
    
    logger.info("=" * 60)
    logger.info(f"📤 ENVIANDO EMAIL VÍA RESEND API")
    logger.info("=" * 60)
    logger.info(f"   To: {to_email}")
    logger.info(f"   From: {from_email}")
    logger.info(f"   Subject: {subject}")
    logger.info(f"   API Key presente: {'✅' if api_key else '❌'}")
    
    if not api_key:
        logger.error("❌ RESEND_API_KEY no está configurada!")
        return False, "RESEND_API_KEY no configurada"
    
    try:
        response = requests.post(
            "https://api.resend.com/emails",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            },
            json={
                "from": f"TuKomercio <{from_email}>",
                "to": [to_email],
                "subject": subject,
                "html": html_content
            },
            timeout=30
        )
        
        logger.info(f"📍 Response status: {response.status_code}")
        logger.info(f"📍 Response body: {response.text}")
        
        if response.status_code == 200:
            logger.info("✅ Email enviado exitosamente!")
            return True, "OK"
        else:
            error_msg = response.json().get('message', response.text)
            logger.error(f"❌ Error de Resend: {error_msg}")
            return False, error_msg
            
    except requests.exceptions.Timeout:
        logger.error("❌ Timeout conectando a Resend API")
        return False, "Timeout"
    except Exception as e:
        logger.error(f"❌ Error: {type(e).__name__}: {str(e)}")
        logger.error(traceback.format_exc())
        return False, str(e)


def send_email_async(to_email, subject, html_content):
    """Envía email en background thread"""
    def _send():
        logger.info(f"🧵 Thread iniciado para {to_email}")
        success, msg = send_email_resend(to_email, subject, html_content)
        if success:
            logger.info(f"🧵 ✅ Email enviado a {to_email}")
        else:
            logger.error(f"🧵 ❌ Falló envío a {to_email}: {msg}")
    
    thread = Thread(target=_send)
    thread.daemon = True
    thread.start()
    logger.info(f"🧵 Thread lanzado para {to_email}")


# ==========================================
# PLANTILLA DE EMAIL
# ==========================================
EMAIL_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
</head>
<body style="margin: 0; padding: 0; font-family: Arial, sans-serif; background-color: #f4f4f4;">
    <table style="width: 100%; max-width: 600px; margin: 0 auto; background-color: #ffffff;">
        <tr>
            <td style="padding: 40px 20px; text-align: center; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);">
                <h1 style="color: #ffffff; margin: 0;">🔐 TuKomercio</h1>
                <p style="color: #e0e0e0; margin: 10px 0 0;">Recuperación de Contraseña</p>
            </td>
        </tr>
        <tr>
            <td style="padding: 40px 30px;">
                <h2 style="color: #333;">Hola {{ nombre }},</h2>
                <p style="color: #555; line-height: 1.6;">
                    Recibimos una solicitud para restablecer tu contraseña.
                </p>
                <p style="text-align: center; margin: 30px 0;">
                    <a href="{{ reset_url }}" 
                       style="display: inline-block; padding: 15px 40px; background: #667eea; color: #fff; text-decoration: none; border-radius: 50px; font-weight: bold;">
                        Restablecer Contraseña
                    </a>
                </p>
                <p style="color: #888; font-size: 14px; background: #fff3cd; padding: 15px; border-radius: 4px;">
                    ⚠️ Este enlace expira en 1 hora.
                </p>
                <p style="color: #888; font-size: 12px; margin-top: 20px; word-break: break-all;">
                    Link: {{ reset_url }}
                </p>
            </td>
        </tr>
        <tr>
            <td style="padding: 20px; background-color: #f8f9fa; text-align: center;">
                <p style="color: #888; font-size: 12px; margin: 0;">© 2026 TuKomercio</p>
            </td>
        </tr>
    </table>
</body>
</html>
"""


# ==========================================
# ENDPOINT DE DIAGNÓSTICO
# ==========================================
@password_reset_bp.route('/test-smtp', methods=['GET'])
def test_smtp():
    """Verifica configuración de Resend"""
    api_key = os.environ.get('RESEND_API_KEY', '')
    from_email = os.environ.get('MAIL_FROM', 'noreply@tukomercio.store')
    frontend_url = os.environ.get('FRONTEND_URL', '')
    
    result = {
        "service": "Resend API (HTTP)",
        "config": {
            "RESEND_API_KEY": "✅ Configurada" if api_key else "❌ NO CONFIGURADA",
            "api_key_preview": f"{api_key[:10]}..." if len(api_key) > 10 else "N/A",
            "MAIL_FROM": from_email,
            "FRONTEND_URL": frontend_url
        },
        "status": "✅ Listo para enviar" if api_key else "❌ Falta RESEND_API_KEY"
    }
    
    return jsonify(result), 200


@password_reset_bp.route('/test-send/<email>', methods=['GET'])
def test_send(email):
    """Envía email de prueba"""
    logger.info(f"📧 Test de envío a: {email}")
    
    html = f"""
    <html>
    <body style="font-family: Arial; padding: 20px;">
        <h1>🧪 Email de Prueba</h1>
        <p>¡La configuración de email está funcionando!</p>
        <p>Enviado a: <strong>{email}</strong></p>
        <hr>
        <p style="color: #888;">TuKomercio</p>
    </body>
    </html>
    """
    
    success, message = send_email_resend(email, "🧪 Test - TuKomercio", html)
    
    if success:
        return jsonify({
            "success": True,
            "message": f"✅ Email enviado a {email}",
            "hint": "Revisa tu bandeja de entrada y spam"
        }), 200
    else:
        return jsonify({
            "success": False,
            "error": message,
            "hint": "Verifica RESEND_API_KEY y que el dominio esté verificado en Resend"
        }), 500


# ==========================================
# ENDPOINT PRINCIPAL: FORGOT PASSWORD
# ==========================================
@password_reset_bp.route('/forgot-password', methods=['POST'])
def forgot_password():
    """Solicita reset de contraseña"""
    logger.info("=" * 60)
    logger.info("📧 FORGOT-PASSWORD: Nueva solicitud")
    logger.info("=" * 60)
    
    try:
        data = request.get_json()
        
        if not data or 'correo' not in data:
            return jsonify({
                "success": False,
                "message": "El correo electrónico es requerido"
            }), 400
        
        correo = data['correo'].lower().strip()
        logger.info(f"📍 Correo: {correo}")
        
        # Buscar usuario
        usuario = Usuario.query.filter_by(correo=correo).first()
        
        if not usuario:
            logger.warning(f"⚠️ Usuario no encontrado: {correo}")
            return jsonify({
                "success": True,
                "message": "Si el correo existe, recibirás un enlace."
            }), 200
        
        logger.info(f"📍 Usuario encontrado: {usuario.nombre}")
        
        if not usuario.active or usuario.black_list:
            return jsonify({
                "success": True,
                "message": "Si el correo existe, recibirás un enlace."
            }), 200
        
        # Crear token
        token = PasswordResetToken.create_for_user(usuario.id_usuario)
        logger.info(f"📍 Token creado")
        
        # URL de reset
        frontend_url = os.environ.get('FRONTEND_URL', 'https://trayectoria-rxdc1.web.app')
        reset_url = f"{frontend_url}/reset-password.html?token={token.token}"
        
        # Preparar y enviar email
        html_content = render_template_string(
            EMAIL_TEMPLATE,
            nombre=usuario.nombre or correo.split('@')[0],
            correo=usuario.correo,
            reset_url=reset_url
        )
        
        send_email_async(correo, "🔐 Restablecer tu contraseña - TuKomercio", html_content)
        
        logger.info(f"✅ Solicitud procesada para: {correo}")
        
        return jsonify({
            "success": True,
            "message": "Si el correo existe, recibirás un enlace de recuperación."
        }), 200
        
    except Exception as e:
        logger.error(f"❌ Error: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({
            "success": False,
            "message": "Error interno del servidor"
        }), 500


# ==========================================
# OTROS ENDPOINTS
# ==========================================
@password_reset_bp.route('/verify-reset-token/<token>', methods=['GET'])
def verify_reset_token(token):
    """Verifica si un token es válido"""
    try:
        reset_token = PasswordResetToken.get_valid_token(token)
        
        if not reset_token:
            return jsonify({"valid": False, "message": "Token inválido"}), 400
        
        usuario = Usuario.query.get(reset_token.user_id)
        
        return jsonify({
            "valid": True,
            "user": {"nombre": usuario.nombre if usuario else None}
        }), 200
        
    except Exception as e:
        logger.error(f"Error: {e}")
        return jsonify({"valid": False}), 500


@password_reset_bp.route('/reset-password', methods=['POST'])
def reset_password():
    """Procesa el cambio de contraseña"""
    try:
        data = request.get_json()
        
        token_str = data.get('token')
        password = data.get('password')
        confirm_password = data.get('confirm_password')
        
        if not all([token_str, password, confirm_password]):
            return jsonify({"success": False, "message": "Datos incompletos"}), 400
        
        if password != confirm_password:
            return jsonify({"success": False, "message": "Las contraseñas no coinciden"}), 400
        
        if len(password) < 6:
            return jsonify({"success": False, "message": "Mínimo 6 caracteres"}), 400
        
        reset_token = PasswordResetToken.get_valid_token(token_str)
        
        if not reset_token:
            return jsonify({"success": False, "message": "Token inválido"}), 400
        
        usuario = Usuario.query.get(reset_token.user_id)
        
        if not usuario:
            return jsonify({"success": False, "message": "Usuario no encontrado"}), 404
        
        usuario.set_password(password)
        reset_token.mark_as_used()
        db.session.commit()
        
        logger.info(f"✅ Contraseña actualizada: {usuario.correo}")
        
        return jsonify({
            "success": True,
            "message": "Contraseña actualizada"
        }), 200
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error: {e}")
        return jsonify({"success": False, "message": "Error interno"}), 500