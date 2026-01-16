"""
BizFlow Studio - API de Recuperación de Contraseña
USA RESEND API con urllib (NO necesita instalar requests)
"""

import os
import json
import logging
import traceback
import urllib.request
import urllib.error
from flask import Blueprint, request, jsonify, render_template_string
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
    Inicializa configuración de email.
    Usa Resend API (HTTP) - NO SMTP (bloqueado en Render)
    """
    resend_key = os.environ.get('RESEND_API_KEY', '')
    frontend_url = os.environ.get('FRONTEND_URL', 'https://trayectoria-rxdc1.web.app')
    
    logger.info("=" * 60)
    logger.info("🚀 CONFIGURACIÓN DE EMAIL (RESEND API)")
    logger.info("=" * 60)
    logger.info(f"📧 RESEND_API_KEY: {'✅ Configurada' if resend_key else '❌ NO CONFIGURADA'}")
    logger.info(f"📧 FRONTEND_URL: {frontend_url}")
    logger.info("=" * 60)
    
    return None


# ==========================================
# ENVÍO DE EMAIL CON RESEND (urllib - sin dependencias)
# ==========================================
def send_email_resend(to_email, subject, html_content):
    """
    Envía email usando Resend API con urllib (biblioteca estándar)
    """
    api_key = os.environ.get('RESEND_API_KEY', '')
    from_email = os.environ.get('MAIL_FROM', 'noreply@tukomercio.store')
    
    logger.info("=" * 60)
    logger.info("📤 ENVIANDO EMAIL VÍA RESEND API")
    logger.info("=" * 60)
    logger.info(f"   To: {to_email}")
    logger.info(f"   From: {from_email}")
    logger.info(f"   API Key: {'✅ presente' if api_key else '❌ FALTA'}")
    
    if not api_key:
        logger.error("❌ RESEND_API_KEY no configurada!")
        return False, "RESEND_API_KEY no configurada"
    
    try:
        # Preparar datos
        data = json.dumps({
            "from": f"TuKomercio <{from_email}>",
            "to": [to_email],
            "subject": subject,
            "html": html_content
        }).encode('utf-8')
        
        # Crear request
        req = urllib.request.Request(
            "https://api.resend.com/emails",
            data=data,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            },
            method="POST"
        )
        
        # Enviar
        logger.info("📍 Enviando request a Resend API...")
        with urllib.request.urlopen(req, timeout=30) as response:
            result = json.loads(response.read().decode('utf-8'))
            logger.info(f"✅ Respuesta: {result}")
            logger.info("🎉 EMAIL ENVIADO EXITOSAMENTE")
            return True, "OK"
            
    except urllib.error.HTTPError as e:
        error_body = e.read().decode('utf-8')
        logger.error(f"❌ HTTP Error {e.code}: {error_body}")
        return False, f"HTTP {e.code}: {error_body}"
        
    except urllib.error.URLError as e:
        logger.error(f"❌ URL Error: {e.reason}")
        return False, f"URL Error: {e.reason}"
        
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
            logger.error(f"🧵 ❌ Falló: {msg}")
    
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
<head><meta charset="UTF-8"></head>
<body style="margin:0;padding:0;font-family:Arial,sans-serif;background:#f4f4f4;">
    <table style="width:100%;max-width:600px;margin:0 auto;background:#fff;">
        <tr>
            <td style="padding:40px 20px;text-align:center;background:linear-gradient(135deg,#667eea,#764ba2);">
                <h1 style="color:#fff;margin:0;">🔐 TuKomercio</h1>
                <p style="color:#e0e0e0;margin:10px 0 0;">Recuperación de Contraseña</p>
            </td>
        </tr>
        <tr>
            <td style="padding:40px 30px;">
                <h2 style="color:#333;">Hola {{ nombre }},</h2>
                <p style="color:#555;line-height:1.6;">Recibimos una solicitud para restablecer tu contraseña.</p>
                <p style="text-align:center;margin:30px 0;">
                    <a href="{{ reset_url }}" style="display:inline-block;padding:15px 40px;background:#667eea;color:#fff;text-decoration:none;border-radius:50px;font-weight:bold;">
                        Restablecer Contraseña
                    </a>
                </p>
                <p style="color:#888;font-size:14px;background:#fff3cd;padding:15px;border-radius:4px;">
                    ⚠️ Este enlace expira en 1 hora.
                </p>
                <p style="color:#888;font-size:12px;margin-top:20px;word-break:break-all;">
                    Link: {{ reset_url }}
                </p>
            </td>
        </tr>
        <tr>
            <td style="padding:20px;background:#f8f9fa;text-align:center;">
                <p style="color:#888;font-size:12px;margin:0;">© 2026 TuKomercio</p>
            </td>
        </tr>
    </table>
</body>
</html>
"""


# ==========================================
# ENDPOINTS DE DIAGNÓSTICO
# ==========================================
@password_reset_bp.route('/test-smtp', methods=['GET'])
def test_smtp():
    """Verifica configuración de Resend"""
    api_key = os.environ.get('RESEND_API_KEY', '')
    from_email = os.environ.get('MAIL_FROM', 'noreply@tukomercio.store')
    frontend_url = os.environ.get('FRONTEND_URL', 'https://trayectoria-rxdc1.web.app')
    
    return jsonify({
        "service": "Resend API (HTTP)",
        "smtp_blocked": "⚠️ SMTP está bloqueado en Render, usamos HTTP",
        "config": {
            "RESEND_API_KEY": "✅ Configurada" if api_key else "❌ FALTA - Ve a resend.com",
            "MAIL_FROM": from_email,
            "FRONTEND_URL": frontend_url
        },
        "status": "✅ Listo" if api_key else "❌ Configura RESEND_API_KEY"
    }), 200


@password_reset_bp.route('/test-send/<email>', methods=['GET'])
def test_send(email):
    """Envía email de prueba"""
    logger.info(f"📧 Test de envío a: {email}")
    
    html = f"""
    <html>
    <body style="font-family:Arial;padding:20px;">
        <h1>🧪 Email de Prueba</h1>
        <p>¡La configuración está funcionando!</p>
        <p>Enviado a: <strong>{email}</strong></p>
        <hr>
        <p style="color:#888;">TuKomercio</p>
    </body>
    </html>
    """
    
    success, message = send_email_resend(email, "🧪 Test - TuKomercio", html)
    
    if success:
        return jsonify({
            "success": True,
            "message": f"✅ Email enviado a {email}"
        }), 200
    else:
        return jsonify({
            "success": False,
            "error": message
        }), 500


# ==========================================
# FORGOT PASSWORD
# ==========================================
@password_reset_bp.route('/forgot-password', methods=['POST'])
def forgot_password():
    """Solicita reset de contraseña"""
    logger.info("=" * 60)
    logger.info("📧 FORGOT-PASSWORD")
    logger.info("=" * 60)
    
    try:
        data = request.get_json()
        
        if not data or 'correo' not in data:
            return jsonify({"success": False, "message": "Correo requerido"}), 400
        
        correo = data['correo'].lower().strip()
        logger.info(f"📍 Correo: {correo}")
        
        usuario = Usuario.query.filter_by(correo=correo).first()
        
        if not usuario:
            logger.warning(f"⚠️ No encontrado: {correo}")
            return jsonify({"success": True, "message": "Si existe, recibirás un enlace."}), 200
        
        logger.info(f"📍 Usuario: {usuario.nombre}")
        
        if not usuario.active or usuario.black_list:
            return jsonify({"success": True, "message": "Si existe, recibirás un enlace."}), 200
        
        # Crear token
        token = PasswordResetToken.create_for_user(usuario.id_usuario)
        
        # URL correcta
        frontend_url = os.environ.get('FRONTEND_URL', 'https://trayectoria-rxdc1.web.app')
        reset_url = f"{frontend_url}/reset-password.html?token={token.token}"
        logger.info(f"📍 URL: {reset_url}")
        
        # Email
        html_content = render_template_string(
            EMAIL_TEMPLATE,
            nombre=usuario.nombre or correo.split('@')[0],
            reset_url=reset_url
        )
        
        send_email_async(correo, "🔐 Restablecer contraseña - TuKomercio", html_content)
        
        return jsonify({"success": True, "message": "Si existe, recibirás un enlace."}), 200
        
    except Exception as e:
        logger.error(f"❌ Error: {str(e)}")
        return jsonify({"success": False, "message": "Error interno"}), 500


# ==========================================
# VERIFY TOKEN
# ==========================================
@password_reset_bp.route('/verify-reset-token/<token>', methods=['GET'])
def verify_reset_token(token):
    """Verifica token"""
    try:
        reset_token = PasswordResetToken.get_valid_token(token)
        
        if not reset_token:
            return jsonify({"valid": False, "message": "Token inválido"}), 400
        
        usuario = Usuario.query.get(reset_token.user_id)
        return jsonify({"valid": True, "user": {"nombre": usuario.nombre if usuario else None}}), 200
        
    except Exception as e:
        return jsonify({"valid": False}), 500


# ==========================================
# RESET PASSWORD
# ==========================================
@password_reset_bp.route('/reset-password', methods=['POST'])
def reset_password():
    """Cambia la contraseña"""
    try:
        data = request.get_json()
        
        token_str = data.get('token')
        password = data.get('password')
        confirm_password = data.get('confirm_password')
        
        if not all([token_str, password, confirm_password]):
            return jsonify({"success": False, "message": "Datos incompletos"}), 400
        
        if password != confirm_password:
            return jsonify({"success": False, "message": "No coinciden"}), 400
        
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
        
        logger.info(f"✅ Contraseña cambiada: {usuario.correo}")
        
        return jsonify({"success": True, "message": "Contraseña actualizada"}), 200
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error: {e}")
        return jsonify({"success": False, "message": "Error interno"}), 500