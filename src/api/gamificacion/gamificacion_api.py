"""
TuKomercio — API de Gamificación v1.0
Rachas · Misiones · Leaderboard · TuKoins · Tienda de Personalización

© 2024-2026 Carlos Eduardo Huérfano Bermúdez. Todos los derechos reservados.
"""

import hashlib
import logging
from datetime import date, datetime, timedelta
from flask import Blueprint, jsonify, request
from flask_login import current_user, login_required
from sqlalchemy import func, cast, Date as SADate

from src.models.database import db

logger = logging.getLogger(__name__)

gamificacion_bp = Blueprint('gamificacion', __name__)


# ─────────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────────

def _get_nid(negocio_id_param=None):
    """Resuelve negocio_id desde parámetro o usuario autenticado."""
    if negocio_id_param:
        return int(negocio_id_param)
    try:
        from src.models.colombia_data.negocio import Negocio
        n = Negocio.query.filter_by(usuario_id=current_user.id_usuario).first()
        return n.id_negocio if n else None
    except Exception:
        return None


def _get_gami(negocio_id):
    """Obtiene o crea el registro de gamificación."""
    from src.models.colombia_data.ratings.negocio_gamificacion import NegocioGamificacion
    return NegocioGamificacion.obtener_o_crear(negocio_id, db.session)


def _contar_pedidos_entregados(negocio_id, desde=None, hasta=None):
    """Cuenta pedidos con estado 'entregado' en el rango dado."""
    try:
        from src.api.compradores.pedidos_api import Pedido
    except ImportError:
        try:
            from src.models.compradores.pedido import Pedido
        except ImportError:
            return 0
    q = Pedido.query.filter(
        Pedido.negocio_id == negocio_id,
        Pedido.estado == 'entregado'
    )
    if desde:
        q = q.filter(Pedido.fecha_pedido >= desde)
    if hasta:
        q = q.filter(Pedido.fecha_pedido <= hasta)
    return q.count()


def _dias_con_ventas(negocio_id):
    """
    Devuelve lista de fechas (date) con al menos 1 pedido entregado,
    para calcular rachas.
    """
    try:
        from src.api.compradores.pedidos_api import Pedido
    except ImportError:
        try:
            from src.models.compradores.pedido import Pedido
        except ImportError:
            return []
    rows = (
        db.session.query(cast(Pedido.fecha_pedido, SADate).label('dia'))
        .filter(Pedido.negocio_id == negocio_id, Pedido.estado == 'entregado')
        .distinct()
        .order_by(cast(Pedido.fecha_pedido, SADate).desc())
        .all()
    )
    return [r.dia for r in rows]


def _racha_desde_dias(dias_desc, hoy=None):
    """
    Dada una lista de fechas DISTINTAS en orden descendente, calcula
    (racha_actual_hasta_hoy, racha_maxima_historica).
    Función PURA (hoy inyectable) → testeable sin depender del reloj.
    La racha actual cuenta si hay actividad hoy o ayer (tolerancia de 1 día).
    """
    if not dias_desc:
        return 0, 0
    if hoy is None:
        hoy = date.today()

    # Racha actual: arranca desde hoy o ayer (tolera que aún no haya actividad hoy)
    racha_actual = 0
    if dias_desc[0] == hoy:
        esperado = hoy
    elif dias_desc[0] == hoy - timedelta(days=1):
        esperado = hoy - timedelta(days=1)
    else:
        esperado = None
    if esperado is not None:
        for d in dias_desc:
            if d == esperado:
                racha_actual += 1
                esperado -= timedelta(days=1)
            elif d < esperado:
                break

    # Racha máxima histórica
    racha_max = 0
    temp = 1
    for i in range(len(dias_desc) - 1):
        if (dias_desc[i] - dias_desc[i + 1]).days == 1:
            temp += 1
        else:
            racha_max = max(racha_max, temp)
            temp = 1
    racha_max = max(racha_max, temp, racha_actual)
    return racha_actual, racha_max


def _calcular_racha_ventas(negocio_id):
    """Racha de ventas (días consecutivos con pedidos entregados)."""
    return _racha_desde_dias(_dias_con_ventas(negocio_id))


def _dias_con_productos(negocio_id):
    """Fechas distintas (desc) con al menos 1 producto creado."""
    try:
        from src.models.colombia_data.contabilidad.operaciones_y_catalogo import ProductoCatalogo
        rows = (
            db.session.query(cast(ProductoCatalogo.fecha_creacion, SADate).label('dia'))
            .filter(ProductoCatalogo.negocio_id == negocio_id)
            .distinct()
            .order_by(cast(ProductoCatalogo.fecha_creacion, SADate).desc())
            .all()
        )
        return [r.dia for r in rows]
    except Exception:
        return []


def _dias_con_videos(negocio_id):
    """Fechas distintas (desc) con al menos 1 video subido."""
    try:
        from src.models.colombia_data.negocio_video import NegocioVideo
        rows = (
            db.session.query(cast(NegocioVideo.created_at, SADate).label('dia'))
            .filter(NegocioVideo.negocio_id == negocio_id)
            .distinct()
            .order_by(cast(NegocioVideo.created_at, SADate).desc())
            .all()
        )
        return [r.dia for r in rows]
    except Exception:
        return []


def _calcular_racha_productos(negocio_id):
    return _racha_desde_dias(_dias_con_productos(negocio_id))


def _calcular_racha_videos(negocio_id):
    return _racha_desde_dias(_dias_con_videos(negocio_id))


def _contar_productos_creados_hoy(negocio_id):
    from src.models.colombia_data.contabilidad.operaciones_y_catalogo import ProductoCatalogo
    hoy = date.today()
    return ProductoCatalogo.query.filter(
        ProductoCatalogo.negocio_id == negocio_id,
        cast(ProductoCatalogo.fecha_creacion, SADate) == hoy
    ).count()


def _contar_videos_creados(negocio_id, desde=None):
    try:
        from src.models.colombia_data.negocio_video import NegocioVideo
        q = NegocioVideo.query.filter_by(negocio_id=negocio_id)
        if desde:
            q = q.filter(NegocioVideo.created_at >= desde)
        return q.count()
    except Exception:
        return 0


def _perfil_actualizado_hoy(negocio_id):
    from src.models.colombia_data.negocio import Negocio
    n = Negocio.query.get(negocio_id)
    if not n or not n.fecha_actualizacion:
        return False
    return n.fecha_actualizacion.date() == date.today()


def _mision_completada_hoy(negocio_id, codigo):
    from src.models.colombia_data.ratings.negocio_gamificacion import NegocioMisionCompletada
    return NegocioMisionCompletada.query.filter_by(
        negocio_id=negocio_id,
        mision_codigo=codigo,
        fecha=date.today()
    ).first() is not None


def _mision_completada_semana(negocio_id, codigo):
    from src.models.colombia_data.ratings.negocio_gamificacion import NegocioMisionCompletada
    inicio_semana = date.today() - timedelta(days=date.today().weekday())
    return NegocioMisionCompletada.query.filter(
        NegocioMisionCompletada.negocio_id == negocio_id,
        NegocioMisionCompletada.mision_codigo == codigo,
        NegocioMisionCompletada.fecha >= inicio_semana,
    ).first() is not None


def _mision_completada_mes(negocio_id, codigo):
    from src.models.colombia_data.ratings.negocio_gamificacion import NegocioMisionCompletada
    inicio_mes = date.today().replace(day=1)
    return NegocioMisionCompletada.query.filter(
        NegocioMisionCompletada.negocio_id == negocio_id,
        NegocioMisionCompletada.mision_codigo == codigo,
        NegocioMisionCompletada.fecha >= inicio_mes,
    ).first() is not None


def _verificar_mision_auto(negocio_id, mision):
    """Verifica si una misión auto-detectable está cumplida."""
    codigo = mision['codigo']
    hoy = date.today()
    inicio_semana = hoy - timedelta(days=hoy.weekday())

    if codigo == 'completar_venta':
        return _contar_pedidos_entregados(negocio_id, desde=hoy) > 0
    if codigo == 'agregar_producto':
        return _contar_productos_creados_hoy(negocio_id) > 0
    if codigo == 'subir_video':
        desde_hoy = datetime.combine(hoy, datetime.min.time())
        return _contar_videos_creados(negocio_id, desde=desde_hoy) > 0
    if codigo == 'actualizar_perfil':
        return _perfil_actualizado_hoy(negocio_id)
    if codigo == 'ventas_semana_5':
        return _contar_pedidos_entregados(negocio_id, desde=inicio_semana) >= 5
    if codigo == 'videos_semana_3':
        return _contar_videos_creados(negocio_id, desde=datetime.combine(inicio_semana, datetime.min.time())) >= 3
    if codigo == 'productos_semana_5':
        from src.models.colombia_data.contabilidad.operaciones_y_catalogo import ProductoCatalogo
        return ProductoCatalogo.query.filter(
            ProductoCatalogo.negocio_id == negocio_id,
            cast(ProductoCatalogo.fecha_creacion, SADate) >= inicio_semana
        ).count() >= 5

    # ── Nuevas diarias (S14) ──
    if codigo == 'vender_3':
        return _contar_pedidos_entregados(negocio_id, desde=hoy) >= 3
    if codigo == 'dos_productos':
        return _contar_productos_creados_hoy(negocio_id) >= 2

    # ── Mensuales (S14) — mes calendario ──
    inicio_mes = hoy.replace(day=1)
    if codigo == 'ventas_mes_20':
        return _contar_pedidos_entregados(negocio_id, desde=inicio_mes) >= 20
    if codigo == 'videos_mes_8':
        return _contar_videos_creados(negocio_id, desde=datetime.combine(inicio_mes, datetime.min.time())) >= 8
    if codigo == 'productos_mes_15':
        from src.models.colombia_data.contabilidad.operaciones_y_catalogo import ProductoCatalogo
        return ProductoCatalogo.query.filter(
            ProductoCatalogo.negocio_id == negocio_id,
            cast(ProductoCatalogo.fecha_creacion, SADate) >= inicio_mes
        ).count() >= 15
    return False


def _elegir_misiones_diarias(negocio_id):
    """
    Elige 3 misiones diarias usando hash del día para rotación determinista.
    Siempre las mismas 3 misiones en el mismo día para el mismo negocio.
    """
    from src.models.colombia_data.ratings.negocio_gamificacion import POOL_MISIONES_DIARIAS
    seed_str = f"{negocio_id}-{date.today().isoformat()}"
    seed = int(hashlib.md5(seed_str.encode()).hexdigest(), 16)
    n = len(POOL_MISIONES_DIARIAS)
    indices = sorted(set([seed % n, (seed // n) % n, (seed // n // n) % n]))
    # Garantizar que sean 3 diferentes
    todos = list(range(n))
    seleccionados = []
    for i in [(seed + j) % n for j in range(n)]:
        if todos[i] not in [x for x in seleccionados] and len(seleccionados) < 3:
            seleccionados.append(todos[i])
    return [POOL_MISIONES_DIARIAS[i] for i in seleccionados]


def _registrar_mision_completada(negocio_id, gami, mision, tipo='diaria'):
    """Registra la misión, suma XP y TuKoins. Idempotente."""
    from src.models.colombia_data.ratings.negocio_gamificacion import NegocioMisionCompletada
    if tipo == 'diaria':
        ya = _mision_completada_hoy(negocio_id, mision['codigo'])
    elif tipo == 'mensual':
        ya = _mision_completada_mes(negocio_id, mision['codigo'])
    else:
        ya = _mision_completada_semana(negocio_id, mision['codigo'])
    if ya:
        return False

    registro = NegocioMisionCompletada(
        negocio_id=negocio_id,
        gamificacion_id=gami.id,
        mision_codigo=mision['codigo'],
        fecha=date.today(),
        xp_ganado=mision['xp'],
        tukoins_ganados=mision['tukoins'],
        tipo=tipo,
    )
    db.session.add(registro)
    gami.agregar_xp(mision['xp'], f"Misión: {mision['nombre']}")
    gami.agregar_tukoins(mision['tukoins'], f"Misión: {mision['nombre']}", db_session=db.session)
    return True


# ─────────────────────────────────────────────────────────────────
# ENDPOINTS
# ─────────────────────────────────────────────────────────────────

@gamificacion_bp.route('/gamificacion/usuario', methods=['GET'])
@login_required
def gamificacion_usuario():
    """
    Estado de gamificación PERSONAL del usuario logueado (S8).
    GET /api/gamificacion/usuario
    Mide la trayectoria del creador a través de todos sus negocios.
    """
    try:
        from src.models.colombia_data.ratings.usuario_gamificacion import UsuarioGamificacion
        uid = current_user.id_usuario
        gu = UsuarioGamificacion.obtener_o_crear(uid, db.session)
        # Asegura que la racha refleje la actividad de hoy al consultar
        if gu.actualizar_racha_login():
            db.session.commit()
        return jsonify({'success': True, 'usuario': gu.serialize()}), 200
    except Exception as e:
        logger.error(f"Error en gamificacion_usuario: {e}", exc_info=True)
        return jsonify({'success': False, 'error': 'Error interno'}), 500


_MESES_ES = ['', 'enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio',
             'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre']


def _rango_mes(hoy=None):
    """Devuelve (inicio_mes, fin_exclusivo, etiqueta) del mes de 'hoy'.
    Función pura (hoy inyectable) → testeable."""
    if hoy is None:
        hoy = datetime.utcnow()
    inicio = datetime(hoy.year, hoy.month, 1)
    if hoy.month == 12:
        fin = datetime(hoy.year + 1, 1, 1)
    else:
        fin = datetime(hoy.year, hoy.month + 1, 1)
    etiqueta = f"{_MESES_ES[hoy.month]} {hoy.year}"
    return inicio, fin, etiqueta


@gamificacion_bp.route('/gamificacion/resumen-mensual', methods=['GET'])
@login_required
def resumen_mensual():
    """
    "Tu mes en números" — resumen compartible del mes actual del negocio.
    GET /api/gamificacion/resumen-mensual?negocio_id=4
    """
    nid = _get_nid(request.args.get('negocio_id'))
    if not nid:
        return jsonify({'success': False, 'error': 'Negocio no encontrado'}), 404

    from sqlalchemy import text as _t
    inicio, fin, etiqueta = _rango_mes()
    params = {'nid': nid, 'ini': inicio, 'fin': fin}
    data = {'mes': etiqueta, 'ventas': 0, 'ingresos': 0.0,
            'clientes': 0, 'badges': 0, 'misiones': 0, 'nivel': 1, 'nombre_nivel': ''}

    def _scalar(sql, default=0):
        try:
            return db.session.execute(_t(sql), params).fetchone()[0] or default
        except Exception:
            return default

    data['ventas']   = int(_scalar(
        "SELECT COUNT(*) FROM pedidos WHERE negocio_id=:nid AND estado='entregado' "
        "AND fecha_pedido>=:ini AND fecha_pedido<:fin"))
    data['ingresos'] = float(_scalar(
        "SELECT COALESCE(SUM(COALESCE(subtotal,0)-COALESCE(descuento,0)),0) FROM pedidos "
        "WHERE negocio_id=:nid AND estado='entregado' AND fecha_pedido>=:ini AND fecha_pedido<:fin", 0.0))
    data['clientes'] = int(_scalar(
        "SELECT COUNT(DISTINCT comprador_id) FROM pedidos WHERE negocio_id=:nid "
        "AND estado='entregado' AND fecha_pedido>=:ini AND fecha_pedido<:fin AND comprador_id IS NOT NULL"))
    data['badges']   = int(_scalar(
        "SELECT COUNT(*) FROM negocio_badges_obtenidos WHERE negocio_id=:nid "
        "AND fecha_obtencion>=:ini AND fecha_obtencion<:fin"))
    data['misiones'] = int(_scalar(
        "SELECT COUNT(*) FROM negocio_misiones_completadas WHERE negocio_id=:nid "
        "AND fecha>=:ini AND fecha<:fin", 0))

    try:
        gami = _get_gami(nid)
        nivel, nombre = gami.calcular_nivel()
        data['nivel'] = nivel
        data['nombre_nivel'] = nombre
        db.session.commit()
    except Exception:
        db.session.rollback()

    return jsonify({'success': True, 'resumen': data}), 200


def _merge_eventos(listas, limite=15):
    """
    Fusiona varias listas de eventos (cada uno con clave 'ts' ordenable) en
    un único feed ordenado por fecha desc. Función PURA → testeable.
    """
    todos = []
    for lst in listas:
        todos.extend(lst or [])
    todos.sort(key=lambda e: e.get('ts', 0), reverse=True)
    return todos[:limite]


@gamificacion_bp.route('/gamificacion/feed-logros', methods=['GET'])
@login_required
def feed_logros():
    """
    Timeline de logros recientes del negocio (S23): insignias ganadas +
    misiones completadas, fusionadas y ordenadas por fecha.
    GET /api/gamificacion/feed-logros?negocio_id=4
    """
    nid = _get_nid(request.args.get('negocio_id'))
    if not nid:
        return jsonify({'success': False, 'error': 'Negocio no encontrado'}), 404

    from sqlalchemy import text as _t
    eventos_badges, eventos_mis = [], []

    # Insignias ganadas
    try:
        rows = db.session.execute(_t("""
            SELECT b.nombre, b.icono, b.color_primario, o.fecha_obtencion
            FROM negocio_badges_obtenidos o
            JOIN negocio_badges b ON b.id = o.badge_id
            WHERE o.negocio_id = :nid AND (o.activo IS TRUE OR o.activo IS NULL)
            ORDER BY o.fecha_obtencion DESC LIMIT 12
        """), {'nid': nid}).fetchall()
        for r in rows:
            f = r[3]
            eventos_badges.append({
                'tipo': 'badge', 'icono': r[1] or 'bi-award-fill',
                'color': r[2] or '#fbbf24',
                'titulo': f'Ganaste la insignia «{r[0]}»',
                'fecha': f.isoformat() if f else None,
                'ts': f.timestamp() if f else 0,
            })
    except Exception as e:
        logger.warning(f"[feed] badges: {e}")

    # Misiones completadas (mapea código → nombre/ícono con los pools)
    try:
        from src.models.colombia_data.ratings.negocio_gamificacion import (
            POOL_MISIONES_DIARIAS, POOL_MISIONES_SEMANALES, POOL_MISIONES_MENSUALES
        )
        mp = {m['codigo']: m for m in
              (POOL_MISIONES_DIARIAS + POOL_MISIONES_SEMANALES + POOL_MISIONES_MENSUALES)}
        rows = db.session.execute(_t("""
            SELECT mision_codigo, fecha, xp_ganado
            FROM negocio_misiones_completadas
            WHERE negocio_id = :nid
            ORDER BY fecha DESC LIMIT 12
        """), {'nid': nid}).fetchall()
        for r in rows:
            m = mp.get(r[0], {})
            f = r[1]  # date
            # date → datetime medianoche para ordenar junto a los badges
            ts = datetime(f.year, f.month, f.day).timestamp() if f else 0
            eventos_mis.append({
                'tipo': 'mision', 'icono': 'bi-check-circle-fill', 'color': '#10b981',
                'titulo': f"Misión completada: {m.get('nombre', r[0])}",
                'detalle': f"+{r[2] or 0} XP",
                'fecha': f.isoformat() if f else None, 'ts': ts,
            })
    except Exception as e:
        logger.warning(f"[feed] misiones: {e}")

    feed = _merge_eventos([eventos_badges, eventos_mis], limite=15)
    return jsonify({'success': True, 'feed': feed}), 200


@gamificacion_bp.route('/gamificacion/proximos-badges', methods=['GET'])
@login_required
def proximos_badges():
    """
    Insignias más cercanas a desbloquear, con progreso (S22).
    GET /api/gamificacion/proximos-badges?negocio_id=4
    """
    nid = _get_nid(request.args.get('negocio_id'))
    if not nid:
        return jsonify({'success': False, 'error': 'Negocio no encontrado'}), 404
    try:
        from src.api.utils.badge_verification_service import BadgeVerificationService
        proximos = BadgeVerificationService.progreso_proximos_badges(nid, limite=4)
        return jsonify({'success': True, 'proximos': proximos}), 200
    except Exception as e:
        logger.error(f"Error en proximos_badges: {e}", exc_info=True)
        return jsonify({'success': False, 'error': 'Error interno', 'proximos': []}), 200


@gamificacion_bp.route('/gamificacion/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    """
    Endpoint principal — devuelve TODO el estado de gamificación en una sola llamada.
    GET /api/gamificacion/dashboard?negocio_id=4
    """
    negocio_id = request.args.get('negocio_id') or (request.get_json() or {}).get('negocio_id')
    nid = _get_nid(negocio_id)
    if not nid:
        return jsonify({'error': 'Negocio no encontrado'}), 404

    try:
        from src.models.colombia_data.ratings.negocio_gamificacion import (
            POOL_MISIONES_DIARIAS, POOL_MISIONES_SEMANALES, POOL_MISIONES_MENSUALES
        )

        gami = _get_gami(nid)
        gami.actualizar_racha_actividad()

        # ── Auto-completar misiones diarias detectadas ──────────
        misiones_hoy = _elegir_misiones_diarias(nid)
        for m in misiones_hoy:
            if m['auto'] and _verificar_mision_auto(nid, m):
                _registrar_mision_completada(nid, gami, m, 'diaria')

        # ── Auto-completar misiones semanales ───────────────────
        for m in POOL_MISIONES_SEMANALES:
            if m['auto'] and _verificar_mision_auto(nid, m):
                _registrar_mision_completada(nid, gami, m, 'semanal')

        # ── Auto-completar misiones mensuales (S14) ──────────────
        for m in POOL_MISIONES_MENSUALES:
            if m['auto'] and _verificar_mision_auto(nid, m):
                _registrar_mision_completada(nid, gami, m, 'mensual')

        db.session.commit()

        # ── Rachas ───────────────────────────────────────────────
        racha_ventas_actual, racha_ventas_max = _calcular_racha_ventas(nid)
        racha_prod_actual, racha_prod_max = _calcular_racha_productos(nid)
        racha_vid_actual, racha_vid_max = _calcular_racha_videos(nid)

        # ── Estado de misiones de hoy ────────────────────────────
        misiones_estado = []
        for m in misiones_hoy:
            completada = _mision_completada_hoy(nid, m['codigo'])
            misiones_estado.append({**m, 'completada': completada})

        misiones_semanales_estado = []
        for m in POOL_MISIONES_SEMANALES:
            completada = _mision_completada_semana(nid, m['codigo'])
            misiones_semanales_estado.append({**m, 'completada': completada})

        misiones_mensuales_estado = []
        for m in POOL_MISIONES_MENSUALES:
            completada = _mision_completada_mes(nid, m['codigo'])
            misiones_mensuales_estado.append({**m, 'completada': completada})

        misiones_completadas_hoy = sum(1 for m in misiones_estado if m['completada'])
        bonus_completado = misiones_completadas_hoy == 3

        return jsonify({
            'gamificacion':         gami.serialize(),
            'rachas': {
                'ventas': {
                    'actual': racha_ventas_actual,
                    'max':    racha_ventas_max,
                    'icono':  '🔥',
                    'nombre': 'Racha de ventas',
                },
                'actividad': {
                    'actual': gami.racha_actividad_dias,
                    'max':    gami.racha_actividad_max,
                    'icono':  '📅',
                    'nombre': 'Racha de actividad',
                },
                'productos': {
                    'actual': racha_prod_actual,
                    'max':    racha_prod_max,
                    'icono':  '📦',
                    'nombre': 'Racha de productos',
                },
                'videos': {
                    'actual': racha_vid_actual,
                    'max':    racha_vid_max,
                    'icono':  '🎬',
                    'nombre': 'Racha de videos',
                },
            },
            'misiones': {
                'diarias':  misiones_estado,
                'semanales': misiones_semanales_estado,
                'mensuales': misiones_mensuales_estado,
                'completadas_hoy': misiones_completadas_hoy,
                'total_hoy': len(misiones_hoy),
                'bonus_desbloqueado': bonus_completado,
            },
        })

    except Exception as e:
        import traceback; traceback.print_exc()
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@gamificacion_bp.route('/gamificacion/misiones/completar', methods=['POST'])
@login_required
def completar_mision_manual():
    """
    Marca como completada una misión manual (compartir_redes, responder_cliente, etc.)
    POST /api/gamificacion/misiones/completar
    { "negocio_id": 4, "mision_codigo": "compartir_redes" }
    """
    data = request.get_json() or {}
    nid = _get_nid(data.get('negocio_id'))
    codigo = data.get('mision_codigo', '').strip()
    if not nid or not codigo:
        return jsonify({'error': 'negocio_id y mision_codigo requeridos'}), 400

    try:
        from src.models.colombia_data.ratings.negocio_gamificacion import (
            POOL_MISIONES_DIARIAS, POOL_MISIONES_SEMANALES, POOL_MISIONES_MENSUALES
        )

        # Buscar la misión en los pools
        pool = POOL_MISIONES_DIARIAS + POOL_MISIONES_SEMANALES + POOL_MISIONES_MENSUALES
        mision = next((m for m in pool if m['codigo'] == codigo), None)
        if not mision:
            return jsonify({'error': 'Misión no reconocida'}), 404
        if mision.get('auto'):
            return jsonify({'error': 'Esta misión se completa automáticamente'}), 400

        gami = _get_gami(nid)
        tipo = mision['tipo']
        nueva = _registrar_mision_completada(nid, gami, mision, tipo)
        db.session.commit()

        if not nueva:
            return jsonify({'ok': False, 'mensaje': 'Ya completada hoy'})

        return jsonify({
            'ok': True,
            'xp_ganado': mision['xp'],
            'tukoins_ganados': mision['tukoins'],
            'xp_total': gami.xp_total,
            'nivel': gami.nivel,
            'tukoins': gami.tukoins,
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@gamificacion_bp.route('/gamificacion/leaderboard', methods=['GET'])
def leaderboard():
    """
    Ranking de negocios por ventas.
    GET /api/gamificacion/leaderboard?categoria=Automotriz&ciudad=Bogota&limit=10
    Público — no requiere autenticación.
    """
    categoria = request.args.get('categoria', '').strip()
    ciudad    = request.args.get('ciudad', '').strip()
    limit     = min(int(request.args.get('limit', 10)), 50)

    try:
        from src.models.colombia_data.negocio import Negocio
        from src.models.colombia_data.contabilidad.operaciones_y_catalogo import ProductoCatalogo
        from sqlalchemy import desc

        # Suma de total_ventas por negocio
        q = (
            db.session.query(
                Negocio.id_negocio,
                Negocio.nombre_negocio,
                Negocio.categoria,
                Negocio.ciudad,
                Negocio.logo_url,
                Negocio.slug,
                func.coalesce(func.sum(ProductoCatalogo.total_ventas), 0).label('ventas_totales'),
            )
            .outerjoin(ProductoCatalogo, ProductoCatalogo.negocio_id == Negocio.id_negocio)
            .filter(Negocio.activo == True, Negocio.perfil_publico == True)
        )

        if categoria:
            q = q.filter(func.lower(Negocio.categoria).contains(categoria.lower()))
        if ciudad:
            q = q.filter(func.lower(Negocio.ciudad).contains(ciudad.lower()))

        q = q.group_by(
            Negocio.id_negocio, Negocio.nombre_negocio, Negocio.categoria,
            Negocio.ciudad, Negocio.logo_url, Negocio.slug
        ).order_by(desc('ventas_totales')).limit(limit)

        resultados = q.all()

        # negocio actual (si está autenticado)
        mi_posicion = None
        if current_user.is_authenticated:
            try:
                mi_neg = Negocio.query.filter_by(usuario_id=current_user.id_usuario).first()
                if mi_neg:
                    todos_ids = [r.id_negocio for r in resultados]
                    if mi_neg.id_negocio in todos_ids:
                        mi_posicion = todos_ids.index(mi_neg.id_negocio) + 1
            except Exception:
                pass

        medallas = ['🥇', '🥈', '🥉']
        ranking = []
        for i, r in enumerate(resultados):
            ranking.append({
                'posicion':      i + 1,
                'medalla':       medallas[i] if i < 3 else '',
                'negocio_id':    r.id_negocio,
                'nombre':        r.nombre_negocio,
                'categoria':     r.categoria,
                'ciudad':        r.ciudad,
                'logo_url':      r.logo_url,
                'slug':          r.slug,
                'ventas_totales': int(r.ventas_totales),
            })

        return jsonify({
            'ranking':       ranking,
            'mi_posicion':   mi_posicion,
            'filtro':        {'categoria': categoria, 'ciudad': ciudad},
            'total_mostrado': len(ranking),
        })

    except Exception as e:
        import traceback; traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@gamificacion_bp.route('/gamificacion/tukoins/<int:negocio_id>', methods=['GET'])
@login_required
def tukoins_detalle(negocio_id):
    """Balance e historial de TuKoins."""
    try:
        from src.models.colombia_data.ratings.negocio_gamificacion import TuKoinTransaccion
        gami = _get_gami(negocio_id)
        ultimas = (TuKoinTransaccion.query
                   .filter_by(negocio_id=negocio_id)
                   .order_by(TuKoinTransaccion.fecha.desc())
                   .limit(20).all())
        return jsonify({
            'balance':  gami.tukoins,
            'historial': [t.serialize() for t in ultimas],
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@gamificacion_bp.route('/gamificacion/tienda', methods=['GET'])
@login_required
def tienda_catalogo():
    """Catálogo de la tienda de personalización."""
    negocio_id = request.args.get('negocio_id')
    nid = _get_nid(negocio_id)

    try:
        from src.models.colombia_data.ratings.negocio_gamificacion import (
            TiendaItem, TiendaCompra, seed_tienda_items
        )

        # Sembrar/actualizar catálogo de items (idempotente — incluye nuevos)
        seed_tienda_items(db.session)

        items = TiendaItem.query.filter_by(activo=True).order_by(TiendaItem.precio_tukoins).all()

        # Ítems ya comprados por este negocio
        comprados_ids = set()
        if nid:
            compras = TiendaCompra.query.filter_by(negocio_id=nid, activo=True).all()
            comprados_ids = {c.item_id for c in compras}

        gami = _get_gami(nid) if nid else None
        mi_nivel = gami.nivel if gami else 1
        mis_tukoins = gami.tukoins if gami else 0

        catalogo = []
        for item in items:
            d = item.serialize()
            d['ya_comprado'] = item.id in comprados_ids
            d['puedo_comprar'] = (
                mis_tukoins >= item.precio_tukoins
                and mi_nivel >= item.nivel_requerido
                and item.id not in comprados_ids
            )
            catalogo.append(d)

        return jsonify({
            'items':       catalogo,
            'mis_tukoins': mis_tukoins,
            'mi_nivel':    mi_nivel,
        })

    except Exception as e:
        import traceback; traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@gamificacion_bp.route('/gamificacion/tienda/comprar', methods=['POST'])
@login_required
def tienda_comprar():
    """
    Compra un ítem de la tienda.
    POST /api/gamificacion/tienda/comprar
    { "negocio_id": 4, "item_codigo": "marco_fuego" }
    """
    data = request.get_json() or {}
    nid = _get_nid(data.get('negocio_id'))
    item_codigo = data.get('item_codigo', '').strip()

    if not nid or not item_codigo:
        return jsonify({'error': 'negocio_id e item_codigo requeridos'}), 400

    try:
        from src.models.colombia_data.ratings.negocio_gamificacion import (
            TiendaItem, TiendaCompra
        )

        item = TiendaItem.query.filter_by(codigo=item_codigo, activo=True).first()
        if not item:
            return jsonify({'error': 'Ítem no encontrado'}), 404

        gami = _get_gami(nid)

        # Verificar nivel
        if gami.nivel < item.nivel_requerido:
            return jsonify({
                'error': f'Necesitas nivel {item.nivel_requerido} para comprar este ítem'
            }), 403

        # Verificar TuKoins suficientes
        if gami.tukoins < item.precio_tukoins:
            faltantes = item.precio_tukoins - gami.tukoins
            return jsonify({
                'error': f'Te faltan {faltantes} TuKoins'
            }), 402

        # Verificar que no lo tenga ya
        ya = TiendaCompra.query.filter_by(negocio_id=nid, item_id=item.id, activo=True).first()
        if ya:
            return jsonify({'error': 'Ya tienes este ítem'}), 409

        # Descontar TuKoins y registrar compra
        gami.agregar_tukoins(-item.precio_tukoins, f"Compra: {item.nombre}", db_session=db.session)
        compra = TiendaCompra(
            negocio_id=nid,
            item_id=item.id,
            tukoins_gastados=item.precio_tukoins,
        )
        db.session.add(compra)
        db.session.commit()

        return jsonify({
            'ok': True,
            'item':        item.serialize(),
            'tukoins_gastados': item.precio_tukoins,
            'tukoins_restantes': gami.tukoins,
        })

    except Exception as e:
        db.session.rollback()
        import traceback; traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@gamificacion_bp.route('/gamificacion/mis-items/<int:negocio_id>', methods=['GET'])
@login_required
def mis_items(negocio_id):
    """Ítems comprados por el negocio (para aplicar personalizaciones)."""
    try:
        from src.models.colombia_data.ratings.negocio_gamificacion import TiendaCompra
        compras = (TiendaCompra.query
                   .filter_by(negocio_id=negocio_id, activo=True)
                   .all())
        return jsonify({'items': [c.serialize() for c in compras]})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@gamificacion_bp.route('/gamificacion/xp/ganar', methods=['POST'])
@login_required
def ganar_xp():
    """
    Endpoint interno para que otros módulos sumen XP al negocio.
    POST /api/gamificacion/xp/ganar
    { "negocio_id": 4, "xp": 20, "tukoins": 10, "motivo": "Venta completada" }
    """
    data = request.get_json() or {}
    nid  = _get_nid(data.get('negocio_id'))
    xp   = int(data.get('xp', 0))
    tukoins = int(data.get('tukoins', 0))
    motivo  = data.get('motivo', 'Acción completada')

    if not nid or xp <= 0:
        return jsonify({'error': 'negocio_id y xp > 0 requeridos'}), 400

    try:
        gami = _get_gami(nid)
        subio = gami.agregar_xp(xp, motivo)
        if tukoins > 0:
            gami.agregar_tukoins(tukoins, motivo, db_session=db.session)
        db.session.commit()
        return jsonify({
            'ok':         True,
            'xp_total':   gami.xp_total,
            'nivel':      gami.nivel,
            'subio_nivel': subio,
            'tukoins':    gami.tukoins,
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
