"""
BizFlow Studio - API de Recuperación de Contraseña
VERSIÓN CON LOGS SUPER DETALLADOS PARA DIAGNÓSTICO
"""

import os
import smtplib
import logging
import traceback
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from flask import Blueprint, request, jsonify, render_template_string, current_app
from flask_mail import Mail, Message
from threading import Thread
from src.models.database import db
from src.models.usuarios import Usuario
from src.models.password_reset_token import PasswordResetToken

# ==========================================
# LOGGING SUPER DETALLADO
# ==========================================
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# ==========================================
# BLUEPRINT
# ==========================================
password_reset_bp = Blueprint('password_reset', __name__, url_prefix='/api/auth')

# ==========================================
# CONFIGURACIÓN DE MAIL
# ==========================================
mail = None


def init_mail(app):
    """Inicializa Flask-Mail"""
    global mail
    
    logger.info("=" * 60)
    logger.info("🚀 INICIANDO CONFIGURACIÓN DE FLASK-MAIL")
    logger.info("=" * 60)
    
    # Leer variables de entorno
    mail_server = os.environ.get('MAIL_SERVER', 'mail.privateemail.com')
    mail_port = int(os.environ.get('MAIL_PORT', 465))
    mail_username = os.environ.get('MAIL_USERNAME', 'noreply@tukomercio.store')
    mail_password = os.environ.get('MAIL_PASSWORD', '')
    mail_from = os.environ.get('MAIL_FROM', 'noreply@tukomercio.store')
    
    logger.info(f"📧 MAIL_SERVER: {mail_server}")
    logger.info(f"📧 MAIL_PORT: {mail_port}")
    logger.info(f"📧 MAIL_USERNAME: {mail_username}")
    logger.info(f"📧 MAIL_PASSWORD configurada: {'✅ SÍ' if mail_password else '❌ NO'}")
    logger.info(f"📧 MAIL_PASSWORD longitud: {len(mail_password)} caracteres")
    logger.info(f"📧 MAIL_FROM: {mail_from}")
    
    # Configurar Flask
    app.config['MAIL_SERVER'] = mail_server
    app.config['MAIL_PORT'] = mail_port
    app.config['MAIL_USE_TLS'] = False
    app.config['MAIL_USE_SSL'] = True
    app.config['MAIL_USERNAME'] = mail_username
    app.config['MAIL_PASSWORD'] = mail_password
    app.config['MAIL_DEFAULT_SENDER'] = ('TuKomercio', mail_from)
    app.config['MAIL_TIMEOUT'] = 15
    app.config['MAIL_DEBUG'] = True
    
    # URL del frontend
    app.config['FRONTEND_URL'] = os.environ.get('FRONTEND_URL', 'https://trayectoria-rxdc1.web.app')
    logger.info(f"📧 FRONTEND_URL: {app.config['FRONTEND_URL']}")
    
    mail = Mail(app)
    logger.info("✅ Flask-Mail objeto creado")
    logger.info("=" * 60)
    
    return mail


# ==========================================
# ENVÍO DIRECTO CON SMTPLIB (MÁS CONTROL)
# ==========================================
def send_email_direct(to_email, subject, html_content):
    """
    Envía email directamente con smtplib para tener control total y logs detallados
    """
    logger.info("=" * 60)
    logger.info("📤 INICIANDO ENVÍO DIRECTO DE EMAIL")
    logger.info("=" * 60)
    
    # Obtener configuración
    server = os.environ.get('MAIL_SERVER', 'mail.privateemail.com')
    port = int(os.environ.get('MAIL_PORT', 465))
    username = os.environ.get('MAIL_USERNAME', 'noreply@tukomercio.store')
    password = os.environ.get('MAIL_PASSWORD', '')
    from_email = os.environ.get('MAIL_FROM', 'noreply@tukomercio.store')
    
    logger.info(f"📍 Paso 1: Configuración cargada")
    logger.info(f"   - Server: {server}")
    logger.info(f"   - Port: {port}")
    logger.info(f"   - Username: {username}")
    logger.info(f"   - Password length: {len(password)}")
    logger.info(f"   - From: {from_email}")
    logger.info(f"   - To: {to_email}")
    
    if not password:
        logger.error("❌ ERROR: MAIL_PASSWORD está vacío!")
        return False, "MAIL_PASSWORD no configurado"
    
    try:
        # Crear mensaje
        logger.info(f"📍 Paso 2: Creando mensaje MIME...")
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = f"TuKomercio <{from_email}>"
        msg['To'] = to_email
        
        html_part = MIMEText(html_content, 'html', 'utf-8')
        msg.attach(html_part)
        logger.info(f"   ✅ Mensaje creado correctamente")
        
        # Conectar al servidor
        logger.info(f"📍 Paso 3: Conectando a {server}:{port} con SSL...")
        smtp = smtplib.SMTP_SSL(server, port, timeout=15)
        logger.info(f"   ✅ Conexión SSL establecida")
        
        # Debug SMTP
        logger.info(f"📍 Paso 4: Habilitando debug SMTP...")
        smtp.set_debuglevel(1)
        
        # EHLO
        logger.info(f"📍 Paso 5: Enviando EHLO...")
        smtp.ehlo()
        logger.info(f"   ✅ EHLO exitoso")
        
        # Login
        logger.info(f"📍 Paso 6: Autenticando como {username}...")
        smtp.login(username, password)
        logger.info(f"   ✅ Autenticación exitosa!")
        
        # Enviar
        logger.info(f"📍 Paso 7: Enviando email a {to_email}...")
        result = smtp.sendmail(from_email, [to_email], msg.as_string())
        logger.info(f"   ✅ Email enviado! Resultado: {result}")
        
        # Cerrar
        logger.info(f"📍 Paso 8: Cerrando conexión...")
        smtp.quit()
        logger.info(f"   ✅ Conexión cerrada")
        
        logger.info("=" * 60)
        logger.info("🎉 EMAIL ENVIADO EXITOSAMENTE")
        logger.info("=" * 60)
        return True, "OK"
        
    except smtplib.SMTPAuthenticationError as e:
        logger.error("=" * 60)
        logger.error("❌ ERROR DE AUTENTICACIÓN SMTP")
        logger.error(f"   Código: {e.smtp_code}")
        logger.error(f"   Mensaje: {e.smtp_error}")
        logger.error("   → Verifica usuario y contraseña en Namecheap")
        logger.error("=" * 60)
        return False, f"Auth error: {e.smtp_error}"
        
    except smtplib.SMTPConnectError as e:
        logger.error("=" * 60)
        logger.error("❌ ERROR DE CONEXIÓN SMTP")
        logger.error(f"   Error: {str(e)}")
        logger.error("   → El servidor no responde o el puerto está bloqueado")
        logger.error("=" * 60)
        return False, f"Connection error: {str(e)}"
        
    except smtplib.SMTPRecipientsRefused as e:
        logger.error("=" * 60)
        logger.error("❌ DESTINATARIO RECHAZADO")
        logger.error(f"   Error: {str(e)}")
        logger.error("=" * 60)
        return False, f"Recipient refused: {str(e)}"
        
    except smtplib.SMTPException as e:
        logger.error("=" * 60)
        logger.error("❌ ERROR SMTP GENERAL")
        logger.error(f"   Tipo: {type(e).__name__}")
        logger.error(f"   Error: {str(e)}")
        logger.error("=" * 60)
        return False, f"SMTP error: {str(e)}"
        
    except Exception as e:
        logger.error("=" * 60)
        logger.error("❌ ERROR INESPERADO")
        logger.error(f"   Tipo: {type(e).__name__}")
        logger.error(f"   Error: {str(e)}")
        logger.error(f"   Traceback:")
        logger.error(traceback.format_exc())
        logger.error("=" * 60)
        return False, f"Error: {str(e)}"


# ==========================================
# ENVÍO ASÍNCRONO CON LOGS
# ==========================================
def send_async_email_direct(to_email, subject, html_content):
    """Envía email en un thread separado con logs detallados"""
    logger.info(f"🧵 Creando thread para envío a {to_email}...")
    
    def _send():
        logger.info(f"🧵 Thread iniciado para {to_email}")
        success, message = send_email_direct(to_email, subject, html_content)
        if success:
            logger.info(f"🧵 Thread completado exitosamente para {to_email}")
        else:
            logger.error(f"🧵 Thread falló para {to_email}: {message}")
    
    thread = Thread(target=_send)
    thread.daemon = True
    thread.start()
    logger.info(f"🧵 Thread lanzado (daemon=True)")
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
                <p style="color: #888; font-size: 12px; margin: 0;">
                    © 2026 TuKomercio
                </p>
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
    """Diagnóstico completo de SMTP"""
    logger.info("=" * 60)
    logger.info("🔧 TEST-SMTP: Iniciando diagnóstico")
    logger.info("=" * 60)
    
    server = os.environ.get('MAIL_SERVER', 'mail.privateemail.com')
    port = int(os.environ.get('MAIL_PORT', 465))
    username = os.environ.get('MAIL_USERNAME', 'noreply@tukomercio.store')
    password = os.environ.get('MAIL_PASSWORD', '')
    
    result = {
        "config": {
            "server": server,
            "port": port,
            "username": username,
            "password_set": bool(password),
            "password_length": len(password),
            "password_preview": f"{password[:3]}***{password[-2:]}" if len(password) > 5 else "***"
        },
        "tests": []
    }
    
    # Test 1: Variables de entorno
    result["tests"].append({
        "step": "1. Variables de entorno",
        "status": "✅ OK" if password else "❌ MAIL_PASSWORD vacío"
    })
    
    if not password:
        result["status"] = "❌ FALLO: MAIL_PASSWORD no está configurado en Render"
        return jsonify(result), 200
    
    # Test 2: Conexión
    try:
        logger.info(f"🔌 Conectando a {server}:{port}...")
        smtp = smtplib.SMTP_SSL(server, port, timeout=15)
        result["tests"].append({
            "step": "2. Conexión SSL",
            "status": "✅ OK"
        })
        logger.info("✅ Conexión exitosa")
    except Exception as e:
        result["tests"].append({
            "step": "2. Conexión SSL",
            "status": f"❌ FALLO: {str(e)}"
        })
        result["status"] = f"❌ FALLO en conexión: {str(e)}"
        return jsonify(result), 200
    
    # Test 3: Autenticación
    try:
        logger.info(f"🔑 Autenticando como {username}...")
        smtp.login(username, password)
        result["tests"].append({
            "step": "3. Autenticación",
            "status": "✅ OK"
        })
        logger.info("✅ Autenticación exitosa")
    except smtplib.SMTPAuthenticationError as e:
        result["tests"].append({
            "step": "3. Autenticación",
            "status": f"❌ FALLO: {e.smtp_error.decode() if isinstance(e.smtp_error, bytes) else e.smtp_error}"
        })
        result["status"] = "❌ FALLO: Credenciales incorrectas"
        smtp.quit()
        return jsonify(result), 200
    except Exception as e:
        result["tests"].append({
            "step": "3. Autenticación",
            "status": f"❌ FALLO: {str(e)}"
        })
        result["status"] = f"❌ FALLO en auth: {str(e)}"
        smtp.quit()
        return jsonify(result), 200
    
    # Test 4: Cerrar
    smtp.quit()
    result["tests"].append({
        "step": "4. Cerrar conexión",
        "status": "✅ OK"
    })
    
    result["status"] = "✅ TODO OK - SMTP listo para enviar emails"
    
    logger.info("=" * 60)
    logger.info("✅ TEST-SMTP: Diagnóstico completado exitosamente")
    logger.info("=" * 60)
    
    return jsonify(result), 200


# ==========================================
# ENDPOINT DE PRUEBA DE ENVÍO REAL
# ==========================================
@password_reset_bp.route('/test-send/<email>', methods=['GET'])
def test_send(email):
    """
    Envía un email de prueba real.
    Uso: /api/auth/test-send/tu@email.com
    """
    logger.info("=" * 60)
    logger.info(f"📧 TEST-SEND: Enviando email de prueba a {email}")
    logger.info("=" * 60)
    
    html_content = f"""
    <html>
    <body style="font-family: Arial; padding: 20px;">
        <h1>🧪 Email de Prueba</h1>
        <p>Si ves este email, la configuración SMTP está funcionando correctamente.</p>
        <p>Enviado a: <strong>{email}</strong></p>
        <p>Fecha: <strong>{__import__('datetime').datetime.now()}</strong></p>
        <hr>
        <p style="color: #888;">TuKomercio - Sistema de emails</p>
    </body>
    </html>
    """
    
    # Enviar de forma SÍNCRONA para ver el resultado inmediato
    success, message = send_email_direct(email, "🧪 Test de Email - TuKomercio", html_content)
    
    if success:
        return jsonify({
            "success": True,
            "message": f"✅ Email enviado a {email}",
            "check": "Revisa tu bandeja de entrada y spam"
        }), 200
    else:
        return jsonify({
            "success": False,
            "message": f"❌ Error: {message}",
            "hint": "Revisa los logs de Render para más detalles"
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
        logger.info(f"📍 Datos recibidos: {data}")
        
        if not data or 'correo' not in data:
            logger.warning("❌ Correo no proporcionado")
            return jsonify({
                "success": False,
                "message": "El correo electrónico es requerido"
            }), 400
        
        correo = data['correo'].lower().strip()
        logger.info(f"📍 Correo solicitado: {correo}")
        
        # Buscar usuario
        logger.info(f"📍 Buscando usuario en BD...")
        usuario = Usuario.query.filter_by(correo=correo).first()
        
        if not usuario:
            logger.warning(f"⚠️ Usuario no encontrado: {correo}")
            return jsonify({
                "success": True,
                "message": "Si el correo existe, recibirás un enlace."
            }), 200
        
        logger.info(f"📍 Usuario encontrado: ID={usuario.id_usuario}, Nombre={usuario.nombre}")
        
        # Verificar estado
        if not usuario.active or usuario.black_list:
            logger.warning(f"⚠️ Usuario inactivo/bloqueado: {correo}")
            return jsonify({
                "success": True,
                "message": "Si el correo existe, recibirás un enlace."
            }), 200
        
        # Crear token
        logger.info(f"📍 Creando token de reset...")
        token = PasswordResetToken.create_for_user(usuario.id_usuario)
        logger.info(f"📍 Token creado: {token.token[:20]}...")
        
        # URL de reset
        frontend_url = os.environ.get('FRONTEND_URL', 'https://trayectoria-rxdc1.web.app')
        reset_url = f"{frontend_url}/reset-password.html?token={token.token}"
        logger.info(f"📍 Reset URL: {reset_url}")
        
        # Preparar email
        logger.info(f"📍 Renderizando template de email...")
        html_content = render_template_string(
            EMAIL_TEMPLATE,
            nombre=usuario.nombre or correo.split('@')[0],
            correo=usuario.correo,
            reset_url=reset_url
        )
        logger.info(f"📍 Template renderizado ({len(html_content)} caracteres)")
        
        # Enviar email de forma asíncrona
        logger.info(f"📍 Enviando email asíncrono a {correo}...")
        send_async_email_direct(
            to_email=correo,
            subject="🔐 Restablecer tu contraseña - TuKomercio",
            html_content=html_content
        )
        
        logger.info(f"✅ Solicitud procesada para: {correo}")
        
        return jsonify({
            "success": True,
            "message": "Si el correo existe, recibirás un enlace de recuperación."
        }), 200
        
    except Exception as e:
        logger.error(f"❌ Error en forgot_password: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({
            "success": False,
            "message": "Error interno del servidor"
        }), 500


# ==========================================
# OTROS ENDPOINTS (verify, reset)
# ==========================================
@password_reset_bp.route('/verify-reset-token/<token>', methods=['GET'])
def verify_reset_token(token):
    """Verifica si un token es válido"""
    try:
        reset_token = PasswordResetToken.get_valid_token(token)
        
        if not reset_token:
            return jsonify({"valid": False, "message": "Token inválido o expirado"}), 400
        
        usuario = Usuario.query.get(reset_token.user_id)
        
        return jsonify({
            "valid": True,
            "user": {"nombre": usuario.nombre if usuario else None}
        }), 200
        
    except Exception as e:
        logger.error(f"Error verificando token: {e}")
        return jsonify({"valid": False, "message": "Error"}), 500


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
            return jsonify({"success": False, "message": "Token inválido o expirado"}), 400
        
        usuario = Usuario.query.get(reset_token.user_id)
        
        if not usuario:
            return jsonify({"success": False, "message": "Usuario no encontrado"}), 404
        
        usuario.set_password(password)
        reset_token.mark_as_used()
        db.session.commit()
        
        logger.info(f"✅ Contraseña actualizada para: {usuario.correo}")
        
        return jsonify({
            "success": True,
            "message": "Contraseña actualizada exitosamente"
        }), 200
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error en reset_password: {e}")
        return jsonify({"success": False, "message": "Error interno"}), 500