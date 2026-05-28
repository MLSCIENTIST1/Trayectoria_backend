"""
TuKomercio — Servicio de Emails de Suscripción
===============================================
Envía alertas automáticas a los tenderos cuando su suscripción
está por vencer o ya venció, usando Resend API (sin SMTP).

Tipos de alerta:
  trial_7d       → quedan 7 días de trial
  trial_3d       → quedan 3 días de trial
  trial_gracia   → trial vencido, en período de gracia
  trial_vencida  → trial vencido sin renovar
  sus_7d         → suscripción paga vence en 7 días
  sus_3d         → suscripción paga vence en 3 días
  sus_gracia     → suscripción paga en período de gracia
  sus_vencida    → suscripción paga vencida

Uso:
  from src.services.suscripcion_email_service import enviar_alertas_suscripcion
  resultado = enviar_alertas_suscripcion(app)   # desde un cron/endpoint admin

Deduplicación:
  Cada alerta se guarda en suscripcion.alertas_enviadas (JSON).
  No se reenvía hasta el próximo ciclo (activar/extender limpia las claves).
"""

import os
import json
import logging
import urllib.request
import urllib.error
from datetime import datetime
from sqlalchemy.orm.attributes import flag_modified

logger = logging.getLogger(__name__)

# ─── Umbrales de alerta ────────────────────────────────────────────────────
UMBRAL_7D = 7
UMBRAL_3D = 3

# ─── From email ────────────────────────────────────────────────────────────
MAIL_FROM = os.environ.get('MAIL_FROM', 'noreply@tukomercio.store')
FRONTEND_URL = os.environ.get('FRONTEND_URL', 'https://tuko.pages.dev')


# ═══════════════════════════════════════════════════════════════════════════
# ENVÍO VÍA RESEND API
# ═══════════════════════════════════════════════════════════════════════════

def _send_email(to_email: str, subject: str, html: str) -> tuple[bool, str]:
    """Envía un email usando Resend API (urllib — sin dependencias extra)."""
    api_key = os.environ.get('RESEND_API_KEY', '')
    if not api_key:
        logger.warning('⚠️ RESEND_API_KEY no configurada — email no enviado')
        return False, 'RESEND_API_KEY no configurada'

    payload = json.dumps({
        'from': f'TuKomercio <{MAIL_FROM}>',
        'to': [to_email],
        'subject': subject,
        'html': html,
    }).encode('utf-8')

    req = urllib.request.Request(
        'https://api.resend.com/emails',
        data=payload,
        headers={
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json',
        },
        method='POST',
    )

    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            body = resp.read().decode('utf-8')
            logger.info(f'✅ Email enviado a {to_email} | {subject}')
            return True, body
    except urllib.error.HTTPError as e:
        err = e.read().decode('utf-8', errors='replace')
        logger.error(f'❌ Resend HTTP {e.code}: {err}')
        return False, err
    except Exception as e:
        logger.error(f'❌ Error enviando email: {e}')
        return False, str(e)


# ═══════════════════════════════════════════════════════════════════════════
# TEMPLATES HTML
# ═══════════════════════════════════════════════════════════════════════════

_BASE_STYLE = """
<style>
  @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@400;600;700;800&display=swap');
  body{margin:0;padding:0;background:#f0f2f5;font-family:'Outfit',Arial,sans-serif;}
  .wrap{max-width:580px;margin:32px auto;background:#fff;border-radius:16px;overflow:hidden;box-shadow:0 4px 24px rgba(0,0,0,0.10);}
  .header{padding:36px 40px 28px;text-align:center;}
  .logo{font-size:22px;font-weight:800;color:#fff;letter-spacing:-0.5px;}
  .logo span{opacity:0.7;}
  .body{padding:32px 40px;}
  .title{font-size:22px;font-weight:800;color:#1a1a2e;margin:0 0 10px;}
  .subtitle{font-size:15px;color:#555;margin:0 0 24px;line-height:1.6;}
  .dias-box{background:#f8f9ff;border-radius:12px;padding:20px 24px;margin:0 0 24px;display:flex;align-items:center;gap:16px;}
  .dias-num{font-size:44px;font-weight:800;line-height:1;}
  .dias-lbl{font-size:13px;color:#888;margin-top:2px;}
  .cta-btn{display:block;text-align:center;padding:16px 32px;border-radius:10px;font-size:16px;font-weight:700;color:#fff !important;text-decoration:none;margin:0 0 24px;}
  .info-box{background:#f8f9ff;border-radius:10px;padding:16px 20px;font-size:13px;color:#666;line-height:1.7;}
  .info-box strong{color:#1a1a2e;}
  .footer{background:#f8f9ff;padding:20px 40px;text-align:center;font-size:12px;color:#aaa;border-top:1px solid #eee;}
  .footer a{color:#888;text-decoration:none;}
  hr{border:none;border-top:1px solid #f0f0f0;margin:24px 0;}
</style>
"""

def _html_wrap(header_color: str, header_icon: str, content: str) -> str:
    return f"""<!DOCTYPE html>
<html lang="es">
<head><meta charset="UTF-8">{_BASE_STYLE}</head>
<body>
<div class="wrap">
  <div class="header" style="background:{header_color};">
    <div class="logo">Tu<span>Komercio</span></div>
    <div style="font-size:40px;margin-top:12px;">{header_icon}</div>
  </div>
  <div class="body">{content}</div>
  <div class="footer">
    TuKomercio &bull; Plataforma para tenderos colombianos<br>
    <a href="{FRONTEND_URL}">tukomercio.com</a> &bull;
    <a href="mailto:soporte@tukomercio.com">soporte@tukomercio.com</a><br><br>
    Si no deseas recibir estos avisos, escríbenos al correo de soporte.
  </div>
</div>
</body></html>"""


def _tpl_trial_7d(nombre: str, dias: int, fecha_fin: str) -> str:
    content = f"""
    <p class="title">¡Tu prueba gratuita casi termina!</p>
    <p class="subtitle">Hola <strong>{nombre}</strong>, tienes <strong>{dias} días</strong>
    restantes de tu primer mes gratis en TuKomercio. ¡No dejes que se vaya sin elegir tu plan!</p>
    <div class="dias-box" style="border-left:4px solid #6366f1;">
      <div>
        <div class="dias-num" style="color:#6366f1;">{dias}</div>
        <div class="dias-lbl">días restantes</div>
      </div>
      <div style="font-size:13px;color:#555;">
        Tu prueba gratuita vence el <strong>{fecha_fin}</strong>.<br>
        Activa tu plan antes de esa fecha para no perder ninguna venta.
      </div>
    </div>
    <a href="{FRONTEND_URL}" class="cta-btn" style="background:linear-gradient(90deg,#6366f1,#a855f7);">
      Ver planes y activar mi suscripción →
    </a>
    <div class="info-box">
      <strong>¿Qué pasa si no activo?</strong><br>
      Tendrás 3 días de gracia adicionales. Después de eso, tu tienda quedará pausada
      temporalmente hasta que actives un plan.
    </div>
    """
    return _html_wrap('linear-gradient(135deg,#6366f1,#a855f7)', '🎁', content)


def _tpl_trial_3d(nombre: str, dias: int, fecha_fin: str) -> str:
    content = f"""
    <p class="title">⚠️ Solo quedan {dias} día{'s' if dias != 1 else ''} de prueba</p>
    <p class="subtitle">Hola <strong>{nombre}</strong>, tu período de prueba gratuito
    vence muy pronto. ¡Es hora de activar tu plan para seguir vendiendo!</p>
    <div class="dias-box" style="border-left:4px solid #f59e0b;">
      <div>
        <div class="dias-num" style="color:#f59e0b;">{dias}</div>
        <div class="dias-lbl">día{'s' if dias != 1 else ''} restante{'s' if dias != 1 else ''}</div>
      </div>
      <div style="font-size:13px;color:#555;">
        Fecha límite: <strong>{fecha_fin}</strong>.<br>
        Activa ahora — toma menos de 2 minutos.
      </div>
    </div>
    <a href="{FRONTEND_URL}" class="cta-btn" style="background:linear-gradient(90deg,#f59e0b,#ef4444);">
      ¡Activar mi plan AHORA! →
    </a>
    <div class="info-box">
      <strong>Planes desde $0 el primer mes.</strong><br>
      Tenemos el plan perfecto para tu negocio. No pierdas tus clientes y ventas.
    </div>
    """
    return _html_wrap('linear-gradient(135deg,#f59e0b,#ef4444)', '⏰', content)


def _tpl_trial_gracia(nombre: str, dias_gracia: int) -> str:
    content = f"""
    <p class="title">Tu prueba gratuita ha vencido</p>
    <p class="subtitle">Hola <strong>{nombre}</strong>, tu mes de prueba gratis terminó.
    Tienes <strong>{dias_gracia} días de gracia</strong> para activar tu plan antes
    de que tu tienda quede pausada.</p>
    <div class="dias-box" style="border-left:4px solid #ea580c;">
      <div>
        <div class="dias-num" style="color:#ea580c;">{dias_gracia}</div>
        <div class="dias-lbl">días de gracia</div>
      </div>
      <div style="font-size:13px;color:#555;">
        Tu tienda <strong>sigue visible</strong> durante la gracia.<br>
        Activa tu plan para no interrumpir el servicio.
      </div>
    </div>
    <a href="{FRONTEND_URL}" class="cta-btn" style="background:linear-gradient(90deg,#ea580c,#f97316);">
      Activar mi plan antes de que cierre →
    </a>
    <div class="info-box">
      <strong>¿Tienes preguntas?</strong><br>
      Escríbenos a <a href="mailto:soporte@tukomercio.com">soporte@tukomercio.com</a>
      y te ayudamos a elegir el mejor plan para tu negocio.
    </div>
    """
    return _html_wrap('linear-gradient(135deg,#ea580c,#f97316)', '🕐', content)


def _tpl_trial_vencida(nombre: str) -> str:
    content = f"""
    <p class="title">Tu tienda está temporalmente pausada</p>
    <p class="subtitle">Hola <strong>{nombre}</strong>, tu prueba gratuita y el período
    de gracia han terminado. Tu tienda está pausada en este momento.</p>
    <div class="dias-box" style="border-left:4px solid #dc2626;">
      <div style="font-size:36px;">🔴</div>
      <div style="font-size:13px;color:#555;">
        Tus productos <strong>no están visibles</strong> para los compradores.<br>
        Activa tu plan para reactivar tu tienda al instante.
      </div>
    </div>
    <a href="{FRONTEND_URL}" class="cta-btn" style="background:linear-gradient(90deg,#dc2626,#ef4444);">
      Reactivar mi tienda ahora →
    </a>
    <div class="info-box">
      <strong>Tus datos están seguros.</strong><br>
      Todo tu catálogo, clientes y pedidos siguen guardados.
      Activa tu plan y vuelves a aparecer en minutos.
    </div>
    """
    return _html_wrap('linear-gradient(135deg,#dc2626,#ef4444)', '🔴', content)


def _tpl_sus_7d(nombre: str, dias: int, fecha_fin: str) -> str:
    content = f"""
    <p class="title">Tu suscripción vence en {dias} días</p>
    <p class="subtitle">Hola <strong>{nombre}</strong>, tu suscripción a TuKomercio
    vence el <strong>{fecha_fin}</strong>. Renuévala para no interrumpir tu servicio.</p>
    <div class="dias-box" style="border-left:4px solid #059669;">
      <div>
        <div class="dias-num" style="color:#059669;">{dias}</div>
        <div class="dias-lbl">días restantes</div>
      </div>
      <div style="font-size:13px;color:#555;">
        Vencimiento: <strong>{fecha_fin}</strong>.<br>
        Renueva con anticipación para no perder ventas.
      </div>
    </div>
    <a href="{FRONTEND_URL}" class="cta-btn" style="background:linear-gradient(90deg,#059669,#10b981);">
      Renovar mi suscripción →
    </a>
    <div class="info-box">
      <strong>Renovación automática desactivada.</strong><br>
      Recuerda renovar manualmente para mantener tu tienda activa sin interrupciones.
    </div>
    """
    return _html_wrap('linear-gradient(135deg,#059669,#10b981)', '✅', content)


def _tpl_sus_3d(nombre: str, dias: int, fecha_fin: str) -> str:
    content = f"""
    <p class="title">⚠️ ¡{dias} día{'s' if dias != 1 else ''} para renovar!</p>
    <p class="subtitle">Hola <strong>{nombre}</strong>, tu suscripción vence
    el <strong>{fecha_fin}</strong>. ¡Renueva ya para no perder ninguna venta!</p>
    <div class="dias-box" style="border-left:4px solid #f59e0b;">
      <div>
        <div class="dias-num" style="color:#f59e0b;">{dias}</div>
        <div class="dias-lbl">día{'s' if dias != 1 else ''}</div>
      </div>
      <div style="font-size:13px;color:#555;">
        Si no renuevas, tendrás <strong>3 días de gracia</strong> antes de que
        tu tienda quede pausada.
      </div>
    </div>
    <a href="{FRONTEND_URL}" class="cta-btn" style="background:linear-gradient(90deg,#f59e0b,#ea580c);">
      ¡Renovar mi plan AHORA! →
    </a>
    """
    return _html_wrap('linear-gradient(135deg,#f59e0b,#ea580c)', '⏰', content)


def _tpl_sus_gracia(nombre: str, dias_gracia: int) -> str:
    content = f"""
    <p class="title">Tu suscripción ha vencido — período de gracia</p>
    <p class="subtitle">Hola <strong>{nombre}</strong>, tu suscripción venció.
    Tienes <strong>{dias_gracia} días</strong> para renovar antes de que
    tu tienda sea pausada.</p>
    <div class="dias-box" style="border-left:4px solid #ea580c;">
      <div>
        <div class="dias-num" style="color:#ea580c;">{dias_gracia}</div>
        <div class="dias-lbl">días de gracia</div>
      </div>
      <div style="font-size:13px;color:#555;">
        Tu tienda sigue activa durante la gracia.<br>
        <strong>Renueva ahora</strong> para no arriesgar tus ventas.
      </div>
    </div>
    <a href="{FRONTEND_URL}" class="cta-btn" style="background:linear-gradient(90deg,#ea580c,#dc2626);">
      Renovar antes de que cierren →
    </a>
    """
    return _html_wrap('linear-gradient(135deg,#ea580c,#dc2626)', '🕐', content)


def _tpl_sus_vencida(nombre: str) -> str:
    content = f"""
    <p class="title">Tu tienda está pausada</p>
    <p class="subtitle">Hola <strong>{nombre}</strong>, tu suscripción venció
    y el período de gracia terminó. Tu tienda no está visible en este momento.</p>
    <div class="dias-box" style="border-left:4px solid #dc2626;">
      <div style="font-size:36px;">⏸️</div>
      <div style="font-size:13px;color:#555;">
        Renueva tu suscripción para volver a aparecer en TuKomercio
        y seguir recibiendo pedidos.
      </div>
    </div>
    <a href="{FRONTEND_URL}" class="cta-btn" style="background:linear-gradient(90deg,#dc2626,#ef4444);">
      Renovar y reactivar mi tienda →
    </a>
    <div class="info-box">
      <strong>Tus datos siguen guardados.</strong><br>
      Catálogo, clientes y pedidos están a salvo.
      Renueva y estarás activo en minutos.
    </div>
    """
    return _html_wrap('linear-gradient(135deg,#dc2626,#ef4444)', '🔴', content)


# ═══════════════════════════════════════════════════════════════════════════
# LÓGICA PRINCIPAL
# ═══════════════════════════════════════════════════════════════════════════

def _get_email_negocio(sus) -> str | None:
    """Obtiene el email del tendero: primero el del negocio, luego el del usuario."""
    try:
        negocio = sus.negocio
        if not negocio:
            return None
        # Preferir email del negocio si está configurado
        if negocio.email:
            return negocio.email
        # Fallback: correo del usuario dueño
        if negocio.dueno and negocio.dueno.correo:
            return negocio.dueno.correo
        return None
    except Exception as e:
        logger.warning(f'⚠️ No se pudo obtener email del negocio {sus.negocio_id}: {e}')
        return None


def _ya_enviado(sus, clave: str) -> bool:
    """Retorna True si ese tipo de alerta ya fue enviada en este ciclo."""
    alertas = sus.alertas_enviadas or {}
    return bool(alertas.get(clave))


def _marcar_enviado(sus, clave: str):
    """Marca la alerta como enviada con la fecha/hora actual."""
    alertas = dict(sus.alertas_enviadas or {})
    alertas[clave] = datetime.utcnow().isoformat()
    sus.alertas_enviadas = alertas
    flag_modified(sus, 'alertas_enviadas')


def _procesar_una_suscripcion(sus, db_session) -> list[dict]:
    """
    Evalúa qué alertas deben enviarse para una suscripción y las envía.
    Devuelve lista de resultados: [{clave, email, ok, detalle}].
    """
    resultados = []
    estado     = sus.estado_actual
    dias       = sus.dias_restantes or 0
    es_trial   = sus.es_trial
    fecha_ven  = sus.fecha_vencimiento

    fecha_str  = (
        fecha_ven.strftime('%d/%m/%Y') if fecha_ven else '—'
    )
    nombre = sus.negocio.nombre_negocio if sus.negocio else f'Negocio #{sus.negocio_id}'
    email  = _get_email_negocio(sus)

    if not email:
        logger.warning(f'⚠️ Sin email para negocio {sus.negocio_id} — saltando')
        return resultados

    dias_gracia_act = sus.dias_restantes if estado == 'gracia' else (sus.dias_gracia or 3)

    # ── Definir qué alert debe dispararse ─────────────────────────────
    pendientes: list[tuple[str, str, str]] = []  # (clave, subject, html)

    if es_trial:
        if estado == 'trial' and dias <= UMBRAL_7D and not _ya_enviado(sus, 'trial_7d'):
            pendientes.append((
                'trial_7d',
                f'⏳ Quedan {dias} días de tu prueba gratuita en TuKomercio',
                _tpl_trial_7d(nombre, dias, fecha_str),
            ))
        if estado == 'trial' and dias <= UMBRAL_3D and not _ya_enviado(sus, 'trial_3d'):
            pendientes.append((
                'trial_3d',
                f'🚨 ¡Solo {dias} día{"s" if dias != 1 else ""} de prueba gratis! — TuKomercio',
                _tpl_trial_3d(nombre, dias, fecha_str),
            ))
        if estado == 'gracia' and not _ya_enviado(sus, 'trial_gracia'):
            pendientes.append((
                'trial_gracia',
                '🕐 Tu prueba gratuita venció — período de gracia activo',
                _tpl_trial_gracia(nombre, dias_gracia_act),
            ))
        if estado == 'vencida' and not _ya_enviado(sus, 'trial_vencida'):
            pendientes.append((
                'trial_vencida',
                '🔴 Tu tienda está pausada — activa tu plan en TuKomercio',
                _tpl_trial_vencida(nombre),
            ))
    else:
        # Suscripción paga
        if estado == 'activa' and dias <= UMBRAL_7D and not _ya_enviado(sus, 'sus_7d'):
            pendientes.append((
                'sus_7d',
                f'⏳ Tu suscripción TuKomercio vence en {dias} días',
                _tpl_sus_7d(nombre, dias, fecha_str),
            ))
        if estado == 'activa' and dias <= UMBRAL_3D and not _ya_enviado(sus, 'sus_3d'):
            pendientes.append((
                'sus_3d',
                f'🚨 ¡{dias} día{"s" if dias != 1 else ""} para renovar tu suscripción!',
                _tpl_sus_3d(nombre, dias, fecha_str),
            ))
        if estado == 'gracia' and not _ya_enviado(sus, 'sus_gracia'):
            pendientes.append((
                'sus_gracia',
                '🕐 Tu suscripción venció — período de gracia activo',
                _tpl_sus_gracia(nombre, dias_gracia_act),
            ))
        if estado == 'vencida' and not _ya_enviado(sus, 'sus_vencida'):
            pendientes.append((
                'sus_vencida',
                '🔴 Tu tienda está pausada — renueva en TuKomercio',
                _tpl_sus_vencida(nombre),
            ))

    # ── Enviar ────────────────────────────────────────────────────────
    for clave, subject, html in pendientes:
        ok, detalle = _send_email(email, subject, html)
        if ok:
            _marcar_enviado(sus, clave)
            db_session.add(sus)
        resultados.append({
            'negocio_id': sus.negocio_id,
            'negocio':    nombre,
            'email':      email,
            'alerta':     clave,
            'ok':         ok,
            'detalle':    detalle[:120] if detalle else None,
        })

    return resultados


def enviar_alertas_suscripcion(app=None) -> dict:
    """
    Función principal del cron de alertas.

    Puede llamarse:
      • desde un endpoint admin (app ya corriendo)
      • desde un script externo pasando la app Flask

    Retorna:
      {
        total_revisadas: int,
        total_emails_enviados: int,
        total_errores: int,
        detalle: [ {negocio_id, alerta, ok, ...} ],
      }
    """
    from src.models.database import db
    from src.models.colombia_data.suscripcion_negocio import SuscripcionNegocio

    logger.info('=' * 60)
    logger.info('📧 CRON ALERTAS SUSCRIPCIÓN — INICIANDO')
    logger.info('=' * 60)

    def _run():
        suscripciones = SuscripcionNegocio.query.all()
        logger.info(f'📋 Total suscripciones a revisar: {len(suscripciones)}')

        todos_resultados = []
        for sus in suscripciones:
            try:
                res = _procesar_una_suscripcion(sus, db.session)
                todos_resultados.extend(res)
            except Exception as e:
                logger.error(f'❌ Error procesando suscripción {sus.id}: {e}', exc_info=True)

        # Commit de todos los marcadores de alertas_enviadas
        try:
            db.session.commit()
            logger.info('✅ Commit de alertas_enviadas OK')
        except Exception as e:
            logger.error(f'❌ Error en commit: {e}')
            db.session.rollback()

        enviados = [r for r in todos_resultados if r['ok']]
        errores  = [r for r in todos_resultados if not r['ok']]

        logger.info(f'📧 Emails enviados: {len(enviados)} | Errores: {len(errores)}')
        logger.info('=' * 60)

        return {
            'total_revisadas':        len(suscripciones),
            'total_emails_enviados':  len(enviados),
            'total_errores':          len(errores),
            'detalle':                todos_resultados,
            'ejecutado_en':           datetime.utcnow().isoformat(),
        }

    if app:
        with app.app_context():
            return _run()
    else:
        return _run()
