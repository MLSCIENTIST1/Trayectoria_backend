"""
Servicio de Web Push real (Admin Panel — Sprint A51).

Notificaciones que llegan AUNQUE la app esté cerrada (Push API + Service Worker).
Requiere claves VAPID (env) y la librería `pywebpush`. Si falta cualquiera de las
dos, el envío se omite en silencio (la campanita in-app sigue funcionando).

Helpers PUROS: construir_payload_push, _es_suscripcion_muerta, vapid_disponible.

© 2024-2026 Carlos Eduardo Huérfano Bermúdez. Todos los derechos reservados.
"""
import os
import json
import logging

logger = logging.getLogger(__name__)


def vapid_config():
    """Lee la config VAPID del entorno."""
    return {
        'public':  os.environ.get('VAPID_PUBLIC_KEY', '').strip(),
        'private': os.environ.get('VAPID_PRIVATE_KEY', '').strip(),
        'subject': os.environ.get('VAPID_SUBJECT', 'mailto:soporte@tukomercio.co').strip(),
    }


def vapid_disponible(cfg=None, lib_ok=None):
    """¿Está todo listo para enviar push? Función PURA (cfg + presencia de librería)."""
    cfg = cfg or {}
    if not (cfg.get('public') and cfg.get('private')):
        return False
    if lib_ok is None:
        try:
            import pywebpush  # noqa: F401
            lib_ok = True
        except Exception:
            lib_ok = False
    return bool(lib_ok)


def construir_payload_push(titulo, mensaje, url='/'):
    """Construye el payload JSON que recibe el Service Worker. Función PURA."""
    return {
        'title': (titulo or 'TuKomercio')[:120],
        'body': (mensaje or '')[:300],
        'url': url or '/',
        'tag': 'tukomercio',
    }


def _es_suscripcion_muerta(status_code):
    """True si el endpoint de push ya no existe (debe eliminarse). Función PURA."""
    return status_code in (404, 410)


def enviar_push_a_usuario(user_id, titulo, mensaje, url='/'):
    """
    Envía web push a todas las suscripciones del usuario. A PRUEBA DE FALLOS:
    devuelve el nº de envíos exitosos (0 si VAPID/pywebpush no están). Nunca lanza.
    """
    try:
        cfg = vapid_config()
        if not vapid_disponible(cfg):
            return 0
        from pywebpush import webpush, WebPushException
        from sqlalchemy import text as _t
        from src.models.database import db as _db

        subs = _db.session.execute(_t(
            "SELECT endpoint, p256dh, auth FROM push_subscriptions WHERE user_id = :u"),
            {'u': user_id}).fetchall()
        if not subs:
            return 0
        payload = json.dumps(construir_payload_push(titulo, mensaje, url))
        enviados = 0
        for s in subs:
            try:
                webpush(
                    subscription_info={'endpoint': s[0], 'keys': {'p256dh': s[1], 'auth': s[2]}},
                    data=payload,
                    vapid_private_key=cfg['private'],
                    vapid_claims={'sub': cfg['subject']},
                )
                enviados += 1
            except WebPushException as we:
                code = getattr(getattr(we, 'response', None), 'status_code', None)
                if _es_suscripcion_muerta(code):
                    try:
                        _db.session.execute(_t("DELETE FROM push_subscriptions WHERE endpoint = :e"), {'e': s[0]})
                        _db.session.commit()
                    except Exception:
                        _db.session.rollback()
            except Exception as e:
                logger.warning(f"[push] envío fallido: {e}")
        return enviados
    except Exception as e:
        logger.warning(f"[push] no crítico: {e}")
        return 0
