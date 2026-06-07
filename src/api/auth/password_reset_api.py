# ═══════════════════════════════════════════════════════════════════════════════
# ███████╗██╗   ██╗██╗  ██╗ ██████╗ ███╗   ███╗███████╗██████╗  ██████╗██╗ ██████╗ 
# ╚══██╔══╝██║   ██║██║ ██╔╝██╔═══██╗████╗ ████║██╔════╝██╔══██╗██╔════╝██║██╔═══██╗
#    ██║   ██║   ██║█████╔╝ ██║   ██║██╔████╔██║█████╗  ██████╔╝██║     ██║██║   ██║
#    ██║   ██║   ██║██╔═██╗ ██║   ██║██║╚██╔╝██║██╔══╝  ██╔══██╗██║     ██║██║   ██║
#    ██║   ╚██████╔╝██║  ██╗╚██████╔╝██║ ╚═╝ ██║███████╗██║  ██║╚██████╗██║╚██████╔╝
#    ╚═╝    ╚═════╝ ╚═╝  ╚═╝ ╚═════╝ ╚═╝     ╚═╝╚══════╝╚═╝  ╚═╝ ╚═════╝╚═╝ ╚═════╝ 
# ═══════════════════════════════════════════════════════════════════════════════
#
# TUKOMERCIO - Plataforma de Comercio Electrónico, Gamificación y Gestión Empresarial
# Anteriormente conocido como: Trayectoria / BizFlow Studio
#
# ═══════════════════════════════════════════════════════════════════════════════
# AVISO DE PROPIEDAD INTELECTUAL Y DERECHOS DE AUTOR
# ═══════════════════════════════════════════════════════════════════════════════
#
# © 2024-2026 Carlos Eduardo Huérfano Bermúdez. Todos los derechos reservados.
#
# TITULAR DE DERECHOS:
#   Nombre:     Carlos Eduardo Huérfano Bermúdez
#   C.C.:       1.064.986.917 (Cereté, Córdoba, Colombia)
#   Contacto:   carlos-5100@hotmail.com | +57 322 818 8375
#   Ubicación:  Bogotá D.C., Colombia
#
# INFORMACIÓN DEL PROYECTO:
#   Nombre:     TuKomercio
#   Inicio:     Julio 24, 2024
#   Repositorio: github.com/routeres (routeres@gmail.com)
#
# ═══════════════════════════════════════════════════════════════════════════════
# TÉRMINOS DE USO Y RESTRICCIONES
# ═══════════════════════════════════════════════════════════════════════════════
#
# Este código fuente es CONFIDENCIAL y constituye un SECRETO COMERCIAL.
#
# QUEDA ESTRICTAMENTE PROHIBIDO sin autorización ESCRITA del titular:
#
#   1. Copiar, reproducir o duplicar este código, total o parcialmente
#   2. Modificar, adaptar o crear obras derivadas
#   3. Distribuir, publicar, sublicenciar o transferir a terceros
#   4. Usar para desarrollo de productos competidores
#   5. Realizar ingeniería inversa, descompilar o desensamblar
#   6. Remover o alterar este aviso de propiedad intelectual
#
# El acceso a este código NO otorga ninguna licencia implícita o explícita.
#
# ═══════════════════════════════════════════════════════════════════════════════
# PROTECCIÓN LEGAL
# ═══════════════════════════════════════════════════════════════════════════════
#
# Este software está protegido por:
#
#   • Ley 23 de 1982 - Derechos de Autor (Colombia)
#   • Ley 1915 de 2018 - Modernización Derechos de Autor (Colombia)
#   • Decisión Andina 351 de 1993 - Régimen Común sobre Derecho de Autor
#   • Convenio de Berna para la Protección de Obras Literarias y Artísticas
#   • Tratado OMPI sobre Derecho de Autor (WCT)
#   • Acuerdo ADPIC/TRIPS - Organización Mundial del Comercio
#
# SANCIONES POR INFRACCIÓN:
#   • Civiles: Indemnización por daños y perjuicios (Art. 57, Ley 23/1982)
#   • Penales: Prisión de 4 a 8 años y multa (Art. 271, Código Penal Colombiano)
#
# ═══════════════════════════════════════════════════════════════════════════════
# JURISDICCIÓN
# ═══════════════════════════════════════════════════════════════════════════════
#
# Cualquier disputa será resuelta exclusivamente por los tribunales de
# Bogotá D.C., Colombia, bajo las leyes de la República de Colombia.
#
# ═══════════════════════════════════════════════════════════════════════════════
#
# Para solicitar autorización de uso: carlos-5100@hotmail.com
#
# ═══════════════════════════════════════════════════════════════════════════════


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
from flask import Blueprint, request, jsonify, render_template_string, make_response
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


FRONTEND_URL_DEFAULT = 'https://tukomercio.co'  # ← dominio producción

_CORS_HEADERS = 'Content-Type, Authorization, Accept, X-User-ID, X-Business-ID, X-Session-FP, Cache-Control, Pragma'

def _cors_json(data, status=200):
    """Retorna JSON con headers CORS correctos para los endpoints de reset."""
    r = make_response(jsonify(data), status)
    origin = request.headers.get('Origin', '*')
    r.headers['Access-Control-Allow-Origin']      = origin
    r.headers['Access-Control-Allow-Credentials'] = 'true'
    r.headers['Access-Control-Allow-Headers']     = _CORS_HEADERS
    return r

def init_mail(app):
    """
    Inicializa configuración de email.
    Usa Resend API (HTTP) - NO SMTP (bloqueado en Render)
    """
    resend_key = os.environ.get('RESEND_API_KEY', '')
    frontend_url = os.environ.get('FRONTEND_URL', FRONTEND_URL_DEFAULT)

    logger.info("=" * 60)
    logger.info("🚀 CONFIGURACIÓN DE EMAIL (RESEND API)")
    logger.info("=" * 60)
    logger.info(f"📧 RESEND_API_KEY: {'✅ Configurada' if resend_key else '❌ NO CONFIGURADA — emails NO se enviarán'}")
    logger.info(f"📧 FRONTEND_URL:   {frontend_url}")
    if not resend_key:
        logger.critical("🚨 CRÍTICO: Define RESEND_API_KEY en las env vars de Render")
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
        # ★ FIX (F19): incluir User-Agent y Accept. Sin User-Agent, urllib manda
        #   'Python-urllib/x.y' y Cloudflare (frente a api.resend.com) bloquea la
        #   petición con HTTP 403 / error 1010 → NINGÚN correo se enviaba.
        req = urllib.request.Request(
            "https://api.resend.com/emails",
            data=data,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
                "Accept": "application/json",
                "User-Agent": "TuKomercio/1.0 (+https://tukomercio.co)"
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
    """
    Envía email de forma SÍNCRONA.
    Se eliminó el thread daemon porque en Render el worker puede ser reciclado
    antes de que el thread termine, causando que el email nunca se envíe.
    Resend API responde en <500ms — el overhead es aceptable.
    """
    logger.info(f"📤 Enviando email a {to_email}...")
    success, msg = send_email_resend(to_email, subject, html_content)
    if success:
        logger.info(f"✅ Email enviado exitosamente a {to_email}")
    else:
        logger.error(f"❌ Falló envío a {to_email}: {msg}")
    return success, msg


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
    frontend_url = os.environ.get('FRONTEND_URL', FRONTEND_URL_DEFAULT)

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
@password_reset_bp.route('/forgot-password', methods=['POST', 'OPTIONS'])
def forgot_password():
    """Solicita reset de contraseña vía Resend API."""
    if request.method == 'OPTIONS':
        r = make_response('', 204)
        r.headers['Access-Control-Allow-Origin']      = request.headers.get('Origin', '*')
        r.headers['Access-Control-Allow-Methods']     = 'POST, OPTIONS'
        r.headers['Access-Control-Allow-Headers']     = _CORS_HEADERS
        r.headers['Access-Control-Allow-Credentials'] = 'true'
        r.headers['Access-Control-Max-Age']           = '3600'
        return r

    logger.info("📧 FORGOT-PASSWORD recibido")
    try:
        data = request.get_json() or {}

        if 'correo' not in data:
            return _cors_json({"success": False, "message": "Correo requerido"}, 400)

        correo = data['correo'].lower().strip()
        logger.info(f"📍 Correo solicitado: {correo}")

        # Respuesta genérica siempre (no revelar si el correo existe)
        _ok = lambda: _cors_json({"success": True, "message": "Si existe, recibirás un enlace en los próximos minutos."}, 200)

        # A-SEC-1: rate limiting para evitar abuso/enumeración del reset
        import time as _time
        from src.api.utils.seguridad import (
            esta_bloqueado, registrar_fallo, registrar_evento_seguridad, UMBRAL_INTENTOS,
        )
        _ip = (request.headers.get('X-Forwarded-For', '') or request.remote_addr or '').split(',')[0].strip()
        _ahora = _time.time()
        _bloq, _restante = esta_bloqueado(_ip, f"reset:{correo}", _ahora)
        if _bloq:
            logger.warning(f"🚫 Reset bloqueado por intentos: {correo} (ip {_ip})")
            registrar_evento_seguridad('login', 'reset_bloqueado',
                                       {'motivo': 'demasiadas_solicitudes'}, ip=_ip, email=correo)
            return _cors_json({"success": True, "message": "Si existe, recibirás un enlace en los próximos minutos."}, 200)
        # Cada solicitud cuenta para el umbral (5 en 15 min)
        registrar_fallo(_ip, f"reset:{correo}", _ahora)

        usuario = Usuario.query.filter_by(correo=correo).first()

        if not usuario:
            logger.warning(f"⚠️ Correo no encontrado: {correo}")
            return _ok()

        if not usuario.active or usuario.black_list:
            logger.warning(f"⚠️ Cuenta inactiva/bloqueada: {correo}")
            return _ok()

        if not os.environ.get('RESEND_API_KEY'):
            logger.critical("🚨 RESEND_API_KEY no configurada en Render — email NO se enviará")
            return _ok()

        # Crear token y URL
        token = PasswordResetToken.create_for_user(usuario.id_usuario)
        frontend_url = os.environ.get('FRONTEND_URL', FRONTEND_URL_DEFAULT)
        reset_url = f"{frontend_url}/reset_password.html?token={token.token}"
        logger.info(f"📍 Reset URL: {reset_url}")

        _nombre = usuario.nombre or correo.split('@')[0]
        _subject = "🔐 Restablecer contraseña - TuKomercio"
        html_content = render_template_string(EMAIL_TEMPLATE, nombre=_nombre, reset_url=reset_url)

        # A46: si hay una plantilla editada desde el panel, úsala (fallback seguro al template fijo).
        try:
            from src.models.colombia_data.config_plataforma import get_email_plantilla, render_email
            _pl = get_email_plantilla('recuperar_password')
            if _pl and _pl.get('editada'):
                _vars = {'nombre': _nombre, 'reset_url': reset_url}
                html_content = render_email(_pl['html'], _vars)
                _subject = render_email(_pl.get('subject') or _subject, _vars)
        except Exception:
            pass

        # Construir y enviar email (síncrono — Resend <500ms en Render)
        success, msg = send_email_async(correo, _subject, html_content)
        if not success:
            logger.error(f"❌ Fallo Resend para {correo}: {msg}")

        return _ok()

    except Exception as e:
        logger.error(f"❌ Error forgot_password: {e}")
        return _cors_json({"success": False, "message": "Error interno"}, 500)


# ==========================================
# VERIFY TOKEN
# ==========================================
@password_reset_bp.route('/verify-reset-token/<token>', methods=['GET', 'OPTIONS'])
def verify_reset_token(token):
    """Verifica si el token de reset es válido y no ha expirado."""
    if request.method == 'OPTIONS':
        r = make_response('', 204)
        r.headers['Access-Control-Allow-Origin']      = request.headers.get('Origin', '*')
        r.headers['Access-Control-Allow-Methods']     = 'GET, OPTIONS'
        r.headers['Access-Control-Allow-Headers']     = _CORS_HEADERS
        r.headers['Access-Control-Allow-Credentials'] = 'true'
        r.headers['Access-Control-Max-Age']           = '3600'
        return r
    try:
        reset_token = PasswordResetToken.get_valid_token(token)
        if not reset_token:
            return _cors_json({"valid": False, "message": "Token inválido o expirado"}, 400)
        usuario = Usuario.query.get(reset_token.user_id)
        return _cors_json({"valid": True, "user": {"nombre": usuario.nombre if usuario else None}}, 200)
    except Exception as e:
        logger.error(f"❌ verify_reset_token error: {e}")
        return _cors_json({"valid": False, "message": "Error interno"}, 500)


# ==========================================
# RESET PASSWORD
# ==========================================
@password_reset_bp.route('/reset-password', methods=['POST', 'OPTIONS'])
def reset_password():
    """Cambia la contraseña usando el token válido."""
    if request.method == 'OPTIONS':
        r = make_response('', 204)
        r.headers['Access-Control-Allow-Origin']      = request.headers.get('Origin', '*')
        r.headers['Access-Control-Allow-Methods']     = 'POST, OPTIONS'
        r.headers['Access-Control-Allow-Headers']     = _CORS_HEADERS
        r.headers['Access-Control-Allow-Credentials'] = 'true'
        r.headers['Access-Control-Max-Age']           = '3600'
        return r
    logger.info("=" * 60)
    logger.info("🔐 RESET-PASSWORD: Iniciando cambio de contraseña")
    logger.info("=" * 60)
    
    try:
        data = request.get_json()
        logger.info(f"📍 Datos recibidos: token={data.get('token', '')[:20]}...")
        
        token_str = data.get('token')
        password = data.get('password')
        confirm_password = data.get('confirm_password')
        
        if not all([token_str, password, confirm_password]):
            return _cors_json({"success": False, "message": "Datos incompletos"}, 400)

        if password != confirm_password:
            return _cors_json({"success": False, "message": "Las contraseñas no coinciden"}, 400)

        if len(password) < 6:
            return _cors_json({"success": False, "message": "Mínimo 6 caracteres"}, 400)

        reset_token = PasswordResetToken.get_valid_token(token_str)
        if not reset_token:
            logger.warning("❌ Token inválido o expirado")
            return _cors_json({"success": False, "message": "El enlace es inválido o ya expiró"}, 400)

        user_id = getattr(reset_token, 'user_id', None) or getattr(reset_token, 'usuario_id', None)
        usuario  = Usuario.query.get(user_id)

        if not usuario:
            return _cors_json({"success": False, "message": "Usuario no encontrado"}, 404)

        logger.info(f"📍 Cambiando contraseña de: {usuario.correo}")
        usuario.set_password(password)
        reset_token.mark_as_used()

        try:
            from datetime import datetime
            usuario.last_login  = None
            usuario.updated_at  = datetime.utcnow()
        except Exception:
            pass

        db.session.commit()
        logger.info(f"✅ Contraseña cambiada exitosamente: {usuario.correo}")
        return _cors_json({"success": True, "message": "¡Contraseña actualizada! Ya puedes iniciar sesión."}, 200)

    except Exception as e:
        db.session.rollback()
        logger.error(f"❌ Error reset_password: {type(e).__name__}: {e}")
        logger.error(traceback.format_exc())
        return _cors_json({"success": False, "message": "Error interno del servidor"}, 500)