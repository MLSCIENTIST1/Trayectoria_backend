"""
Servicio de anuncios / notificaciones masivas (Admin Panel — Sprint A33).

Permite enviar una notificación in-app (tabla `notification`) a un SEGMENTO de
usuarios filtrado por ciudad, plan y nivel de gamificación. El envío usa un único
INSERT ... SELECT (eficiente, sin N inserts). Incluye plantillas rápidas.

© 2024-2026 Carlos Eduardo Huérfano Bermúdez. Todos los derechos reservados.
"""

# Plantillas rápidas (el admin las elige y edita antes de enviar). Datos PUROS.
PLANTILLAS_ANUNCIO = [
    {'clave': 'novedad', 'titulo': '🎉 Nueva función disponible',
     'mensaje': '¡Hola! Acabamos de lanzar una nueva función en TuKomercio. Entra y descúbrela.'},
    {'clave': 'mantenimiento', 'titulo': '🛠️ Mantenimiento programado',
     'mensaje': 'Tendremos un breve mantenimiento. Puede que la plataforma no esté disponible unos minutos. Gracias por tu paciencia.'},
    {'clave': 'promo_plan', 'titulo': '🚀 Mejora tu plan',
     'mensaje': 'Lleva tu negocio al siguiente nivel con un plan superior: más productos, videos y funciones premium.'},
    {'clave': 'reactivacion', 'titulo': '👋 ¡Te extrañamos!',
     'mensaje': 'Hace un tiempo no entras a tu tienda. Vuelve y sigue vendiendo con TuKomercio.'},
    {'clave': 'felicitacion', 'titulo': '🏆 ¡Vas muy bien!',
     'mensaje': 'Tu negocio está creciendo en TuKomercio. ¡Sigue así y desbloquea nuevas insignias!'},
]


def construir_filtros_segmento(filtros):
    """
    Construye las condiciones SQL del segmento. Función PURA.
    Devuelve (conditions:list[str], params:dict). Alias esperados:
      n  = negocios,  gg = negocio_gamificacion (LEFT JOIN).
    Filtros admitidos: ciudad (str), plan (str), nivel_min (int).
    """
    filtros = filtros or {}
    conditions = ["COALESCE(n.eliminado, FALSE) = FALSE", "n.usuario_id IS NOT NULL"]
    params = {}

    ciudad = str(filtros.get('ciudad', '') or '').strip()
    if ciudad:
        conditions.append("n.ciudad ILIKE :ciudad")
        params['ciudad'] = f"%{ciudad}%"

    plan = str(filtros.get('plan', '') or '').strip()
    if plan:
        conditions.append("COALESCE(n.plan_key, 'basic') = :plan")
        params['plan'] = plan

    nivel_min = filtros.get('nivel_min')
    if nivel_min not in (None, '', 0, '0'):
        try:
            params['nivel_min'] = int(nivel_min)
            conditions.append("COALESCE(gg.nivel, 1) >= :nivel_min")
        except (TypeError, ValueError):
            pass

    return conditions, params


def _where_segmento(filtros):
    conds, params = construir_filtros_segmento(filtros)
    return "WHERE " + " AND ".join(conds), params


def contar_destinatarios(db_session, filtros):
    """Cuenta usuarios únicos del segmento (preview)."""
    from sqlalchemy import text as _t
    where, params = _where_segmento(filtros)
    sql = f"""
        SELECT COUNT(DISTINCT n.usuario_id)
        FROM negocios n
        LEFT JOIN negocio_gamificacion gg ON gg.negocio_id = n.id_negocio
        {where}
    """
    return int(db_session.execute(_t(sql), params).scalar() or 0)


def enviar_anuncio(db_session, filtros, titulo, mensaje, prioridad='media'):
    """
    Inserta una notificación por cada usuario del segmento (un solo INSERT..SELECT).
    Devuelve el número de notificaciones creadas.
    """
    from sqlalchemy import text as _t
    where, params = _where_segmento(filtros)
    params.update({
        'titulo': (titulo or 'Mensaje de TuKomercio')[:255],
        'mensaje': mensaje,
        'prioridad': prioridad if prioridad in ('alta', 'media', 'baja') else 'media',
    })
    sql = f"""
        INSERT INTO notification (user_id, type, titulo, message, prioridad, is_read, timestamp)
        SELECT DISTINCT n.usuario_id, 'anuncio', :titulo, :mensaje, :prioridad, FALSE, NOW()
        FROM negocios n
        LEFT JOIN negocio_gamificacion gg ON gg.negocio_id = n.id_negocio
        {where}
    """
    res = db_session.execute(_t(sql), params)
    db_session.commit()
    try:
        return res.rowcount if res.rowcount is not None and res.rowcount >= 0 else 0
    except Exception:
        return 0
