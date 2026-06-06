"""
Servicio de recompensas de liga (Admin Panel — Sprint A25).

Premia automáticamente al top-N de cada liga (ranking por pedidos entregados del
MES ANTERIOR). Diseñado para ejecutarse:
  - Manualmente desde el panel (botón "Ejecutar ahora").
  - Vía cron externo mensual (Render Cron / cron-job.org → POST con API key admin).

IDEMPOTENTE: usa la tabla `liga_recompensas` con UNIQUE (periodo, liga, negocio_id)
para no premiar dos veces el mismo mes/liga/negocio. Un cron que dispare varias
veces el mismo mes no duplica premios.

© 2024-2026 Carlos Eduardo Huérfano Bermúdez. Todos los derechos reservados.
"""
import logging
from sqlalchemy import text as _t

logger = logging.getLogger(__name__)


def _ranking_liga_mes_anterior(db_session, ciudad='', categoria='', limit=10):
    """Filas [(id, nombre, ciudad, categoria, logo, slug, score)] del mes anterior."""
    from src.api.gamificacion.gamificacion_api import _rango_mes_anterior
    inicio, fin, etiqueta = _rango_mes_anterior()
    sql = """
        SELECT n.id_negocio, n.nombre_negocio, n.ciudad, n.categoria,
               n.logo_url, n.slug, COUNT(p.id_pedido) AS ventas_mes
        FROM negocios n
        LEFT JOIN pedidos p ON p.negocio_id = n.id_negocio
             AND p.estado = 'entregado'
             AND p.fecha_pedido >= :ini AND p.fecha_pedido < :fin
        WHERE n.activo = true AND n.perfil_publico = true
    """
    params = {'ini': inicio, 'fin': fin, 'lim': limit}
    if ciudad:
        sql += " AND LOWER(n.ciudad) LIKE :ciudad"; params['ciudad'] = f"%{ciudad.lower()}%"
    if categoria:
        sql += " AND LOWER(n.categoria) LIKE :categoria"; params['categoria'] = f"%{categoria.lower()}%"
    sql += """
        GROUP BY n.id_negocio, n.nombre_negocio, n.ciudad, n.categoria, n.logo_url, n.slug
        HAVING COUNT(p.id_pedido) > 0
        ORDER BY ventas_mes DESC
        LIMIT :lim
    """
    filas = [tuple(f) for f in db_session.execute(_t(sql), params).fetchall()]
    periodo = f"{inicio.year:04d}-{inicio.month:02d}"
    return filas, periodo, etiqueta


def calcular_recompensas_liga(db_session, ciudad='', categoria=''):
    """
    Solo CÁLCULO (sin escribir). Devuelve el plan + metadatos.
    Útil para el dry-run/preview obligatorio antes de aplicar.
    """
    from src.models.colombia_data.ratings.config_gamificacion import (
        get_recompensas_liga, get_negocios_excluidos_ligas, construir_plan_recompensas
    )
    config = get_recompensas_liga()
    excluidos = get_negocios_excluidos_ligas()
    filas, periodo, etiqueta = _ranking_liga_mes_anterior(db_session, ciudad, categoria, limit=10)
    liga = ciudad or categoria or 'Nacional'
    plan = construir_plan_recompensas(filas, config, excluidos)
    return {
        'periodo': periodo, 'etiqueta': etiqueta, 'liga': liga,
        'config': config, 'plan': plan,
        'total_xp': sum(p['xp'] for p in plan),
        'total_tukoins': sum(p['tukoins'] for p in plan),
    }


def otorgar_recompensas_liga(db_session, ciudad='', categoria='', actor='cron'):
    """
    APLICA los premios al top-N del mes anterior. IDEMPOTENTE.
    Devuelve resumen con otorgados/omitidos (ya premiados).
    """
    from src.models.colombia_data.ratings.negocio_gamificacion import NegocioGamificacion

    calc = calcular_recompensas_liga(db_session, ciudad, categoria)
    periodo, liga, plan = calc['periodo'], calc['liga'], calc['plan']

    otorgados, omitidos = [], []
    for item in plan:
        nid = item['negocio_id']
        # Idempotencia: ¿ya se premió este periodo+liga+negocio?
        ya = db_session.execute(_t("""
            SELECT 1 FROM liga_recompensas
            WHERE periodo = :p AND liga = :l AND negocio_id = :n LIMIT 1
        """), {'p': periodo, 'l': liga, 'n': nid}).fetchone()
        if ya:
            omitidos.append({**item, 'motivo': 'ya_premiado'})
            continue

        gami = NegocioGamificacion.obtener_o_crear(nid, db_session)
        if item['xp']:
            gami.agregar_xp(item['xp'], f"Liga {liga} {periodo} — puesto {item['posicion']}")
        if item['tukoins']:
            gami.agregar_tukoins(item['tukoins'], f"Liga {liga} {periodo} — puesto {item['posicion']}",
                                 db_session=db_session)
        db_session.execute(_t("""
            INSERT INTO liga_recompensas (periodo, liga, negocio_id, posicion, xp, tukoins)
            VALUES (:p, :l, :n, :pos, :xp, :tk)
            ON CONFLICT (periodo, liga, negocio_id) DO NOTHING
        """), {'p': periodo, 'l': liga, 'n': nid, 'pos': item['posicion'],
               'xp': item['xp'], 'tk': item['tukoins']})
        otorgados.append(item)

    db_session.commit()

    # A50: campanita automática a cada ganador premiado (no crítico).
    try:
        from src.api.utils.notificaciones_service import notificar_negocio
        for item in otorgados:
            notificar_negocio(item['negocio_id'], evento='recompensa_liga', db_session=db_session)
    except Exception:
        pass
    return {
        'periodo': periodo, 'etiqueta': calc['etiqueta'], 'liga': liga,
        'otorgados': otorgados, 'omitidos': omitidos,
        'total_otorgados': len(otorgados), 'total_omitidos': len(omitidos),
        'total_xp': sum(p['xp'] for p in otorgados),
        'total_tukoins': sum(p['tukoins'] for p in otorgados),
        'actor': actor,
    }


def historial_recompensas_liga(db_session, limit=50):
    """Últimos premios otorgados (para la UI)."""
    rows = db_session.execute(_t("""
        SELECT lr.periodo, lr.liga, lr.negocio_id, n.nombre_negocio, lr.posicion,
               lr.xp, lr.tukoins, lr.otorgado_en
        FROM liga_recompensas lr
        LEFT JOIN negocios n ON n.id_negocio = lr.negocio_id
        ORDER BY lr.otorgado_en DESC, lr.posicion ASC
        LIMIT :lim
    """), {'lim': min(int(limit or 50), 200)}).fetchall()
    return [{
        'periodo': r[0], 'liga': r[1], 'negocio_id': r[2], 'nombre': r[3] or f'#{r[2]}',
        'posicion': r[4], 'xp': r[5], 'tukoins': r[6],
        'otorgado_en': r[7].isoformat() if r[7] else None,
    } for r in rows]
