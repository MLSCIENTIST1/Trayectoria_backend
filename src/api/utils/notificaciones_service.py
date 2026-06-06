"""
Servicio de notificaciones automáticas del sistema (Admin Panel — Sprint A50).

La campanita in-app (tabla `notification`) ahora se dispara sola en eventos clave:
cambio de plan, insignia ganada, suscripción por vencer, etc.

`construir_notificacion` es PURA y testeable; `notificar_negocio` inserta la
notificación y es a prueba de fallos (nunca rompe la operación principal).

© 2024-2026 Carlos Eduardo Huérfano Bermúdez. Todos los derechos reservados.
"""
import logging

logger = logging.getLogger(__name__)


def construir_notificacion(evento, ctx=None):
    """
    Devuelve {titulo, mensaje, prioridad} para un evento del sistema. Función PURA.
    Si el evento es desconocido → None.
    """
    ctx = ctx or {}
    plan = ctx.get('plan', '')
    badge = ctx.get('badge', '')
    dias = ctx.get('dias', '')

    plantillas = {
        'plan_cambiado': {
            'titulo': '💎 Tu plan cambió',
            'mensaje': f'Tu negocio ahora tiene el plan {plan}. ¡Aprovecha las nuevas funciones!',
            'prioridad': 'alta',
        },
        'badge_ganado': {
            'titulo': '🏅 ¡Ganaste una insignia!',
            'mensaje': f'Desbloqueaste «{badge}». Sigue así y consigue más.',
            'prioridad': 'media',
        },
        'suscripcion_por_vencer': {
            'titulo': '⏳ Tu suscripción vence pronto',
            'mensaje': f'Tu plan vence en {dias} día(s). Renueva para no perder tus funciones.',
            'prioridad': 'alta',
        },
        'recompensa_liga': {
            'titulo': '🏆 ¡Recompensa de liga!',
            'mensaje': 'Quedaste en el podio de tu liga y recibiste XP + TuKoins. ¡Felicidades!',
            'prioridad': 'media',
        },
    }
    return plantillas.get(str(evento or '').strip().lower())


def notificar_negocio(negocio_id, evento=None, ctx=None, titulo=None, mensaje=None,
                      tipo='sistema', prioridad='media', db_session=None):
    """
    Inserta una notificación in-app al dueño del negocio. A PRUEBA DE FALLOS
    (retorna False ante cualquier error, nunca lanza). Si se pasa 'evento', usa
    la plantilla pura; si no, usa titulo/mensaje directos.
    """
    try:
        from sqlalchemy import text as _t
        from src.models.database import db as _db
        sess = db_session or _db.session

        if evento:
            data = construir_notificacion(evento, ctx)
            if not data:
                return False
            titulo, mensaje, prioridad = data['titulo'], data['mensaje'], data['prioridad']
        if not mensaje:
            return False

        row = sess.execute(_t("SELECT usuario_id FROM negocios WHERE id_negocio = :n"),
                           {'n': negocio_id}).fetchone()
        if not row or not row[0]:
            return False
        sess.execute(_t("""
            INSERT INTO notification (user_id, negocio_id, type, titulo, message, prioridad, is_read, timestamp)
            VALUES (:u, :n, :t, :ti, :m, :p, FALSE, NOW())
        """), {'u': row[0], 'n': negocio_id, 't': tipo,
               'ti': (titulo or 'TuKomercio')[:255], 'm': mensaje, 'p': prioridad})
        sess.commit()
        return True
    except Exception as e:
        logger.warning(f"[notif-auto] no crítico: {e}")
        try:
            from src.models.database import db as _db
            _db.session.rollback()
        except Exception:
            pass
        return False
