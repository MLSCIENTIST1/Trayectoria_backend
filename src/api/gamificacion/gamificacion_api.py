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

PRESTIGIO_TUKOINS_BONO = 500  # bono al prestigiar (S33)


@gamificacion_bp.route('/gamificacion/bono-hoy', methods=['GET'])
def bono_hoy():
    """Bono de TuKoins activo hoy (S36). Público. Ej: domingo x2."""
    try:
        from src.models.colombia_data.ratings.negocio_gamificacion import bono_tukoins
        mult, nombre = bono_tukoins()
        return jsonify({'success': True, 'multiplicador': mult,
                        'nombre': nombre, 'activo': mult > 1}), 200
    except Exception as e:
        logger.error(f"Error en bono_hoy: {e}")
        return jsonify({'success': False, 'multiplicador': 1, 'activo': False}), 200


@gamificacion_bp.route('/gamificacion/evento-activo', methods=['GET'])
def evento_activo():
    """Evento especial activo hoy (S38). Público. Ej: Semana del Tendero XP x3."""
    try:
        from src.models.colombia_data.ratings.negocio_gamificacion import (
            evento_especial, EVENTOS_ESPECIALES
        )
        ev = evento_especial()
        return jsonify({
            'success': True,
            'activo': ev is not None,
            'evento': ({'codigo': ev['codigo'], 'nombre': ev['nombre'],
                        'icono': ev['icono'], 'xp_mult': ev['xp_mult']} if ev else None),
            'calendario': [{'codigo': e['codigo'], 'nombre': e['nombre'], 'icono': e['icono'],
                            'xp_mult': e['xp_mult']} for e in EVENTOS_ESPECIALES],
        }), 200
    except Exception as e:
        logger.error(f"Error en evento_activo: {e}")
        return jsonify({'success': False, 'activo': False, 'evento': None}), 200


@gamificacion_bp.route('/gamificacion/prestigio', methods=['POST', 'OPTIONS'])
@login_required
def prestigiar():
    """
    Reinicia el progreso del negocio a cambio de +1 estrella de prestigio (S33).
    Solo si alcanzó el nivel máximo (Leyenda). POST /api/gamificacion/prestigio
    """
    if request.method == 'OPTIONS':
        return jsonify({'ok': True}), 200
    nid = _get_nid(request.args.get('negocio_id') or (request.get_json(silent=True) or {}).get('negocio_id'))
    if not nid:
        return jsonify({'success': False, 'error': 'Negocio no encontrado'}), 404
    try:
        gami = _get_gami(nid)
        if not gami.puede_prestigiar():
            return jsonify({'success': False, 'error': 'Aún no alcanzas el nivel Leyenda'}), 400
        gami.prestigiar()
        gami.agregar_tukoins(PRESTIGIO_TUKOINS_BONO, "Bono de Prestigio", db_session=db.session)
        db.session.commit()
        return jsonify({'success': True, 'mensaje': '¡Prestigio alcanzado!',
                        'gamificacion': gami.serialize()}), 200
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error en prestigiar: {e}", exc_info=True)
        return jsonify({'success': False, 'error': 'Error interno'}), 500


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

# Recompensas de referido (S29)
REFERIDO_XP_REFERIDOR = 50      # XP personal para quien refirió
REFERIDO_TUKOINS      = 30      # TuKoins para el negocio del referidor

# Recompensa de duelo (S31)
DUELO_XP_GANADOR      = 80
DUELO_TUKOINS_GANADOR = 40


def _ventas_negocio_rango(negocio_id, desde, hasta):
    """Pedidos entregados de un negocio en [desde, hasta). Seguro."""
    from sqlalchemy import text as _t
    try:
        return int(db.session.execute(_t("""
            SELECT COUNT(*) FROM pedidos WHERE negocio_id=:nid AND estado='entregado'
              AND fecha_pedido>=:d AND fecha_pedido<:h
        """), {'nid': negocio_id, 'd': desde, 'h': hasta}).fetchone()[0] or 0)
    except Exception:
        return 0


def _resolver_duelo_si_corresponde(duelo):
    """Si el duelo activo ya terminó, calcula ganador y premia. Idempotente."""
    from src.models.colombia_data.ratings.duelo import determinar_ganador
    if duelo.estado != 'activo' or not duelo.fecha_fin:
        return
    if datetime.utcnow() < duelo.fecha_fin:
        return  # aún en curso
    vr = _ventas_negocio_rango(duelo.retador_negocio_id, duelo.fecha_inicio, duelo.fecha_fin)
    vt = _ventas_negocio_rango(duelo.retado_negocio_id, duelo.fecha_inicio, duelo.fecha_fin)
    duelo.ventas_retador = vr
    duelo.ventas_retado = vt
    duelo.ganador_negocio_id = determinar_ganador(
        duelo.retador_negocio_id, vr, duelo.retado_negocio_id, vt)
    duelo.estado = 'finalizado'
    # Premiar al ganador (si no hay empate)
    if duelo.ganador_negocio_id:
        try:
            from src.models.colombia_data.ratings.negocio_gamificacion import NegocioGamificacion
            g = NegocioGamificacion.obtener_o_crear(duelo.ganador_negocio_id, db.session)
            g.agregar_xp(DUELO_XP_GANADOR, "Duelo ganado")
            g.agregar_tukoins(DUELO_TUKOINS_GANADOR, "Duelo ganado", db_session=db.session)
        except Exception:
            pass
    db.session.commit()


@gamificacion_bp.route('/gamificacion/duelos/retar', methods=['POST', 'OPTIONS'])
@login_required
def duelo_retar():
    """Crea un duelo pendiente contra otro negocio. Body: {rival_negocio_id}."""
    if request.method == 'OPTIONS':
        return jsonify({'ok': True}), 200
    nid = _get_nid(request.args.get('negocio_id') or (request.get_json(silent=True) or {}).get('negocio_id'))
    data = request.get_json(silent=True) or {}
    rival = data.get('rival_negocio_id')
    if not nid or not rival:
        return jsonify({'success': False, 'error': 'Falta negocio o rival'}), 400
    try:
        rival = int(rival)
    except (ValueError, TypeError):
        return jsonify({'success': False, 'error': 'Rival inválido'}), 400
    if rival == nid:
        return jsonify({'success': False, 'error': 'No puedes retarte a ti mismo'}), 400
    try:
        from src.models.colombia_data.ratings.duelo import Duelo
        # ¿ya hay un duelo en curso entre ellos?
        activo = Duelo.query.filter(
            Duelo.estado.in_(['pendiente', 'activo']),
            ((Duelo.retador_negocio_id == nid) & (Duelo.retado_negocio_id == rival)) |
            ((Duelo.retador_negocio_id == rival) & (Duelo.retado_negocio_id == nid))
        ).first()
        if activo:
            return jsonify({'success': False, 'error': 'Ya hay un duelo en curso con ese negocio'}), 409
        d = Duelo(retador_negocio_id=nid, retado_negocio_id=rival, estado='pendiente')
        db.session.add(d)
        db.session.commit()
        return jsonify({'success': True, 'duelo': d.serialize()}), 201
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error en duelo_retar: {e}", exc_info=True)
        return jsonify({'success': False, 'error': 'Error interno'}), 500


@gamificacion_bp.route('/gamificacion/duelos/<int:duelo_id>/responder', methods=['POST', 'OPTIONS'])
@login_required
def duelo_responder(duelo_id):
    """El retado acepta o rechaza. Body: {aceptar: true/false}."""
    if request.method == 'OPTIONS':
        return jsonify({'ok': True}), 200
    nid = _get_nid(request.args.get('negocio_id') or (request.get_json(silent=True) or {}).get('negocio_id'))
    aceptar = bool((request.get_json(silent=True) or {}).get('aceptar'))
    try:
        from src.models.colombia_data.ratings.duelo import Duelo
        d = Duelo.query.get(duelo_id)
        if not d or d.estado != 'pendiente':
            return jsonify({'success': False, 'error': 'Duelo no disponible'}), 404
        if d.retado_negocio_id != nid:
            return jsonify({'success': False, 'error': 'Solo el retado puede responder'}), 403
        if aceptar:
            d.aceptar()
        else:
            d.estado = 'rechazado'
        db.session.commit()
        return jsonify({'success': True, 'duelo': d.serialize()}), 200
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error en duelo_responder: {e}", exc_info=True)
        return jsonify({'success': False, 'error': 'Error interno'}), 500


@gamificacion_bp.route('/gamificacion/duelos', methods=['GET'])
@login_required
def duelos_listar():
    """Lista los duelos del negocio (resuelve los vencidos al vuelo)."""
    nid = _get_nid(request.args.get('negocio_id'))
    if not nid:
        return jsonify({'success': False, 'error': 'Negocio no encontrado'}), 404
    try:
        from src.models.colombia_data.ratings.duelo import Duelo
        duelos = Duelo.query.filter(
            (Duelo.retador_negocio_id == nid) | (Duelo.retado_negocio_id == nid)
        ).order_by(Duelo.creado_en.desc()).limit(20).all()
        # Resolver los activos vencidos
        for d in duelos:
            try:
                _resolver_duelo_si_corresponde(d)
            except Exception:
                pass
        # Nombres de los rivales (para mostrar)
        nombres = {}
        try:
            from src.models.colombia_data.negocio import Negocio
            ids = set()
            for d in duelos:
                ids.add(d.retador_negocio_id); ids.add(d.retado_negocio_id)
            for n in Negocio.query.filter(Negocio.id_negocio.in_(list(ids))).all():
                nombres[n.id_negocio] = n.nombre_negocio
        except Exception:
            pass
        out = []
        for d in duelos:
            s = d.serialize()
            soy_retador = d.retador_negocio_id == nid
            rival_id = d.retado_negocio_id if soy_retador else d.retador_negocio_id
            s['soy_retador'] = soy_retador
            s['rival_nombre'] = nombres.get(rival_id, f'Negocio #{rival_id}')
            s['mis_ventas'] = d.ventas_retador if soy_retador else d.ventas_retado
            s['ventas_rival'] = d.ventas_retado if soy_retador else d.ventas_retador
            out.append(s)
        return jsonify({'success': True, 'mi_negocio_id': nid, 'duelos': out}), 200
    except Exception as e:
        logger.error(f"Error en duelos_listar: {e}", exc_info=True)
        return jsonify({'success': False, 'error': 'Error interno', 'duelos': []}), 200


@gamificacion_bp.route('/gamificacion/referidos/mi-codigo', methods=['GET'])
@login_required
def referidos_mi_codigo():
    """Código y link de referido del usuario + estadísticas."""
    try:
        from src.models.colombia_data.ratings.referido import Referido
        uid = current_user.id_usuario
        codigo = Referido.codigo_de_usuario(uid)
        total = Referido.query.filter_by(referidor_usuario_id=uid).count()
        convertidos = Referido.query.filter_by(referidor_usuario_id=uid, convertido=True).count()
        return jsonify({
            'success': True,
            'codigo': codigo,
            'link': f"https://tukomercio.co/?ref={codigo}",
            'total_referidos': total,
            'convertidos': convertidos,
        }), 200
    except Exception as e:
        logger.error(f"Error en referidos_mi_codigo: {e}", exc_info=True)
        return jsonify({'success': False, 'error': 'Error interno'}), 500


@gamificacion_bp.route('/gamificacion/referidos/registrar', methods=['POST', 'OPTIONS'])
@login_required
def referidos_registrar():
    """
    Registra al usuario actual como referido por el código dado.
    Body: { "codigo": "TK12" }. Idempotente; evita auto-referirse y duplicados.
    """
    if request.method == 'OPTIONS':
        return jsonify({'ok': True}), 200
    try:
        from src.models.colombia_data.ratings.referido import Referido
        data = request.get_json(silent=True) or {}
        referidor_id = Referido.usuario_de_codigo(data.get('codigo'))
        yo = current_user.id_usuario

        if not referidor_id:
            return jsonify({'success': False, 'error': 'Código inválido'}), 400
        if referidor_id == yo:
            return jsonify({'success': False, 'error': 'No puedes referirte a ti mismo'}), 400
        # ¿ya fui referido por alguien? (constraint único en referido_usuario_id)
        if Referido.query.filter_by(referido_usuario_id=yo).first():
            return jsonify({'success': False, 'error': 'Ya tienes un referidor registrado'}), 409

        ref = Referido(referidor_usuario_id=referidor_id, referido_usuario_id=yo)
        db.session.add(ref)
        db.session.commit()
        return jsonify({'success': True, 'mensaje': '¡Referido registrado!'}), 201
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error en referidos_registrar: {e}", exc_info=True)
        return jsonify({'success': False, 'error': 'Error interno'}), 500


def procesar_conversion_referido(referido_usuario_id):
    """
    Llamar cuando un negocio completa una venta. Si su dueño fue referido y
    aún no se ha recompensado, marca la conversión y premia al referidor.
    Idempotente y a prueba de fallos. Retorna dict de recompensa o None.
    """
    try:
        from src.models.colombia_data.ratings.referido import Referido
        from src.models.colombia_data.ratings.usuario_gamificacion import UsuarioGamificacion
        ref = Referido.query.filter_by(
            referido_usuario_id=referido_usuario_id, recompensado=False).first()
        if not ref:
            return None

        if not ref.convertido:
            ref.convertido = True
            ref.fecha_conversion = datetime.utcnow()

        # Recompensa al referidor (XP personal + TuKoins a su primer negocio)
        gu = UsuarioGamificacion.obtener_o_crear(ref.referidor_usuario_id, db.session)
        gu.agregar_xp(REFERIDO_XP_REFERIDOR, "Referido convertido")
        try:
            from src.models.colombia_data.negocio import Negocio
            from src.models.colombia_data.ratings.negocio_gamificacion import NegocioGamificacion
            neg = Negocio.query.filter_by(usuario_id=ref.referidor_usuario_id).first()
            if neg:
                gn = NegocioGamificacion.obtener_o_crear(neg.id_negocio, db.session)
                gn.agregar_tukoins(REFERIDO_TUKOINS, "Referido convertido", db_session=db.session)
        except Exception:
            pass

        ref.recompensado = True
        db.session.commit()
        logger.info(f"🎁 Referido convertido: referidor={ref.referidor_usuario_id} premiado")
        return {'referidor_usuario_id': ref.referidor_usuario_id,
                'xp': REFERIDO_XP_REFERIDOR, 'tukoins': REFERIDO_TUKOINS}
    except Exception as e:
        logger.warning(f"[referidos] conversión no crítica: {e}")
        try:
            db.session.rollback()
        except Exception:
            pass
        return None


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


def _rango_anio(hoy=None):
    """Rango [inicio, fin) del año en curso + el año. Pura."""
    if hoy is None:
        hoy = datetime.utcnow()
    return datetime(hoy.year, 1, 1), datetime(hoy.year + 1, 1, 1), hoy.year


@gamificacion_bp.route('/gamificacion/anio-revision', methods=['GET'])
@login_required
def anio_revision():
    """
    "Tu año en TuKomercio" — resumen anual compartible (S34).
    GET /api/gamificacion/anio-revision?negocio_id=4
    """
    nid = _get_nid(request.args.get('negocio_id'))
    if not nid:
        return jsonify({'success': False, 'error': 'Negocio no encontrado'}), 404
    from sqlalchemy import text as _t
    ini, fin, anio = _rango_anio()
    p = {'nid': nid, 'ini': ini, 'fin': fin}
    data = {'anio': anio, 'ventas': 0, 'ingresos': 0.0, 'clientes': 0,
            'badges': 0, 'nivel': 1, 'nombre_nivel': '', 'prestigio': 0,
            'mejor_mes': None}

    def _scalar(sql, d=0):
        try:
            return db.session.execute(_t(sql), p).fetchone()[0] or d
        except Exception:
            return d

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

    # Mejor mes del año (más ventas)
    try:
        row = db.session.execute(_t("""
            SELECT EXTRACT(MONTH FROM fecha_pedido) AS m, COUNT(*) AS c
            FROM pedidos WHERE negocio_id=:nid AND estado='entregado'
              AND fecha_pedido>=:ini AND fecha_pedido<:fin
            GROUP BY m ORDER BY c DESC LIMIT 1
        """), p).fetchone()
        if row and row[0]:
            data['mejor_mes'] = {'mes': _MESES_ES[int(row[0])], 'ventas': int(row[1])}
    except Exception:
        pass

    try:
        gami = _get_gami(nid)
        nivel, nombre = gami.calcular_nivel()
        data['nivel'] = nivel
        data['nombre_nivel'] = nombre
        data['prestigio'] = gami.prestigio or 0
        db.session.commit()
    except Exception:
        db.session.rollback()

    return jsonify({'success': True, 'revision': data}), 200


def _rango_mes_anterior(hoy=None):
    """Rango [inicio, fin) del MES ANTERIOR + etiqueta. Pura."""
    if hoy is None:
        hoy = datetime.utcnow()
    if hoy.month == 1:
        ini = datetime(hoy.year - 1, 12, 1)
        fin = datetime(hoy.year, 1, 1)
        et = f"{_MESES_ES[12]} {hoy.year - 1}"
    else:
        ini = datetime(hoy.year, hoy.month - 1, 1)
        fin = datetime(hoy.year, hoy.month, 1)
        et = f"{_MESES_ES[hoy.month - 1]} {hoy.year}"
    return ini, fin, et


def _pct_top(posicion, total):
    """Devuelve el 'top X%' (entero 1-100) dado rango y total. Pura."""
    if not total or total <= 0 or not posicion:
        return None
    return max(1, min(100, round(posicion / total * 100)))


def _crecimiento_pct(actual, anterior):
    """% de cambio actual vs anterior. None si no hay base. Pura."""
    actual = actual or 0
    anterior = anterior or 0
    if anterior == 0:
        return None if actual == 0 else 100  # de 0 a algo = +100% (debut)
    return round((actual - anterior) / anterior * 100)


@gamificacion_bp.route('/gamificacion/comparativas', methods=['GET'])
@login_required
def comparativas():
    """
    Comparaciones contextuales (S30): percentil en la ciudad + crecimiento
    vs el mes anterior. GET /api/gamificacion/comparativas?negocio_id=4
    """
    nid = _get_nid(request.args.get('negocio_id'))
    if not nid:
        return jsonify({'success': False, 'error': 'Negocio no encontrado'}), 404

    from sqlalchemy import text as _t
    ini, fin, _ = _rango_mes()
    ini_ant, fin_ant, et_ant = _rango_mes_anterior()
    out = {'percentil_ciudad': None, 'crecimiento': None}

    def _ventas(nid_, desde, hasta):
        try:
            return int(db.session.execute(_t("""
                SELECT COUNT(*) FROM pedidos WHERE negocio_id=:nid AND estado='entregado'
                  AND fecha_pedido>=:d AND fecha_pedido<:h
            """), {'nid': nid_, 'd': desde, 'h': hasta}).fetchone()[0] or 0)
        except Exception:
            return 0

    mis_ventas = _ventas(nid, ini, fin)

    # Crecimiento vs mes anterior
    ventas_ant = _ventas(nid, ini_ant, fin_ant)
    out['crecimiento'] = {
        'pct': _crecimiento_pct(mis_ventas, ventas_ant),
        'actual': mis_ventas, 'anterior': ventas_ant, 'mes_anterior': et_ant,
    }

    # Percentil en la ciudad
    try:
        from src.models.colombia_data.negocio import Negocio
        mn = Negocio.query.get(nid)
        ciudad = (getattr(mn, 'ciudad', '') or '').strip()
        if ciudad and mis_ventas >= 0:
            filas = db.session.execute(_t("""
                SELECT n.id_negocio, COUNT(p.id_pedido) AS v
                FROM negocios n
                LEFT JOIN pedidos p ON p.negocio_id = n.id_negocio
                    AND p.estado='entregado' AND p.fecha_pedido>=:d AND p.fecha_pedido<:h
                WHERE n.activo = true AND LOWER(n.ciudad) = :ciu
                GROUP BY n.id_negocio
            """), {'d': ini, 'h': fin, 'ciu': ciudad.lower()}).fetchall()
            total = len(filas)
            mejores = sum(1 for f in filas if (f[1] or 0) > mis_ventas)
            posicion = mejores + 1
            out['percentil_ciudad'] = {
                'ciudad': ciudad, 'total': total, 'posicion': posicion,
                'top_pct': _pct_top(posicion, total),
            }
    except Exception as e:
        logger.warning(f"[comparativas] percentil: {e}")

    return jsonify({'success': True, **out}), 200


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


# Unidad legible por métrica (para frasear sugerencias, S35)
_UNIDAD_METRICA = {
    'pedidos_completados': 'pedidos', 'ventas_cop': 'pesos en ventas',
    'productos_activos': 'productos', 'resenas_recibidas': 'reseñas',
    'visitas_tienda': 'visitas', 'pedidos_sin_devolucion': 'entregas limpias',
    'negocios_del_owner': 'negocios', 'videos_subidos': 'videos',
    'votos_emitidos_owner': 'votos', 'referidos_exitosos': 'referidos',
    'duelos_ganados': 'duelos',
}


def generar_sugerencias(proximos, racha_ventas=0, limite=3):
    """
    Genera sugerencias accionables a partir de los badges más cercanos y la
    racha. Función PURA → testeable. Retorna lista de {icono, texto, prioridad}.
    """
    sugerencias = []
    for p in (proximos or [])[:2]:
        unidad = _UNIDAD_METRICA.get(p.get('criterio_tipo'), 'puntos')
        falta = p.get('falta') or 0
        falta_txt = (f"${int(falta):,}".replace(',', '.')
                     if p.get('criterio_tipo') == 'ventas_cop' else int(falta))
        pct = p.get('progreso_pct') or 0
        animo = '¡vas casi!' if pct >= 70 else ('¡buen avance!' if pct >= 40 else '¡tú puedes!')
        sugerencias.append({
            'icono': p.get('icono') or 'bi-trophy',
            'texto': f"Faltan {falta_txt} {unidad} para «{p.get('nombre')}» — {animo} ({pct}%)",
            'prioridad': 'alta' if pct >= 70 else 'media',
        })
    if racha_ventas and racha_ventas >= 2:
        sugerencias.append({
            'icono': 'bi-fire',
            'texto': f"Llevas {racha_ventas} días vendiendo seguido. ¡Vende hoy para no romper tu racha! 🔥",
            'prioridad': 'media',
        })
    elif not proximos:
        sugerencias.append({
            'icono': 'bi-stars',
            'texto': "¡Vas increíble! Sigue vendiendo y subiendo productos para desbloquear más insignias.",
            'prioridad': 'baja',
        })
    return sugerencias[:limite]


@gamificacion_bp.route('/gamificacion/sugerencias', methods=['GET'])
@login_required
def sugerencias():
    """
    Sugerencias inteligentes: qué hacer para tu próximo logro (S35).
    GET /api/gamificacion/sugerencias?negocio_id=4
    """
    nid = _get_nid(request.args.get('negocio_id'))
    if not nid:
        return jsonify({'success': False, 'error': 'Negocio no encontrado'}), 404
    try:
        from src.api.utils.badge_verification_service import BadgeVerificationService
        proximos = BadgeVerificationService.progreso_proximos_badges(nid, limite=4)
        try:
            racha, _ = _calcular_racha_ventas(nid)
        except Exception:
            racha = 0
        return jsonify({'success': True,
                        'sugerencias': generar_sugerencias(proximos, racha)}), 200
    except Exception as e:
        logger.error(f"Error en sugerencias: {e}", exc_info=True)
        return jsonify({'success': False, 'error': 'Error interno', 'sugerencias': []}), 200


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


@gamificacion_bp.route('/creador/<int:usuario_id>', methods=['GET'])
def perfil_creador(usuario_id):
    """
    Perfil PÚBLICO del creador/emprendedor (S37): nivel personal, sus negocios
    públicos, insignias y prestigio. Solo datos públicos (no email/teléfono).
    GET /api/creador/123
    """
    from sqlalchemy import text as _t
    try:
        from src.models.usuarios import Usuario
        u = Usuario.query.get(usuario_id)
        if not u:
            return jsonify({'success': False, 'error': 'Creador no encontrado'}), 404

        data = {
            'usuario_id': usuario_id,
            'nombre': getattr(u, 'nombre', 'Creador'),
            'desde': u.created_at.year if getattr(u, 'created_at', None) else None,
            'nivel': 1, 'nombre_nivel': '🌱 Aprendiz', 'xp_personal': 0,
            'negocios': [], 'badges': [], 'prestigio_total': 0, 'referidos': 0,
        }

        # Gamificación personal (S8)
        try:
            from src.models.colombia_data.ratings.usuario_gamificacion import UsuarioGamificacion
            gu = UsuarioGamificacion.query.filter_by(usuario_id=usuario_id).first()
            if gu:
                niv, nom = gu.calcular_nivel()
                data['nivel'] = niv; data['nombre_nivel'] = nom
                data['xp_personal'] = gu.xp_personal
        except Exception:
            pass

        # Negocios públicos del creador
        try:
            from src.models.colombia_data.negocio import Negocio
            negs = Negocio.query.filter_by(usuario_id=usuario_id, activo=True).all()
            for n in negs:
                if getattr(n, 'perfil_publico', True):
                    data['negocios'].append({
                        'nombre': n.nombre_negocio, 'slug': n.slug,
                        'logo_url': getattr(n, 'logo_url', None),
                        'ciudad': getattr(n, 'ciudad', None),
                    })
        except Exception:
            pass

        # Prestigio total (suma de sus negocios) + insignias destacadas
        try:
            data['prestigio_total'] = int(db.session.execute(_t("""
                SELECT COALESCE(SUM(g.prestigio),0) FROM negocio_gamificacion g
                JOIN negocios n ON n.id_negocio = g.negocio_id
                WHERE n.usuario_id = :uid
            """), {'uid': usuario_id}).fetchone()[0] or 0)
        except Exception:
            pass
        try:
            rows = db.session.execute(_t("""
                SELECT DISTINCT b.nombre, b.icono, b.color_primario, b.nivel
                FROM negocio_badges_obtenidos o
                JOIN negocio_badges b ON b.id = o.badge_id
                JOIN negocios n ON n.id_negocio = o.negocio_id
                WHERE n.usuario_id = :uid AND (o.activo IS TRUE OR o.activo IS NULL)
                  AND (b.es_secreto IS FALSE OR b.es_secreto IS NULL)
                ORDER BY b.nivel DESC LIMIT 12
            """), {'uid': usuario_id}).fetchall()
            data['badges'] = [{'nombre': r[0], 'icono': r[1] or 'bi-award-fill',
                               'color': r[2] or '#fbbf24', 'nivel': r[3] or 1} for r in rows]
        except Exception:
            pass
        try:
            data['referidos'] = int(db.session.execute(_t("""
                SELECT COUNT(*) FROM referidos WHERE referidor_usuario_id=:uid AND convertido=true
            """), {'uid': usuario_id}).fetchone()[0] or 0)
        except Exception:
            pass

        return jsonify({'success': True, 'creador': data}), 200
    except Exception as e:
        logger.error(f"Error en perfil_creador: {e}", exc_info=True)
        return jsonify({'success': False, 'error': 'Error interno'}), 500


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


# Retos temáticos mensuales (S28) — rotan automáticamente cada mes
RETOS_MENSUALES = [
    {'codigo': 'rey_ventas', 'nombre': 'Rey de las Ventas', 'icono': '👑',
     'descripcion': 'Quien más pedidos entregue este mes', 'metrica': 'ventas_mes',
     'unidad': 'ventas'},
    {'codigo': 'productivo', 'nombre': 'El Más Productivo', 'icono': '⚙️',
     'descripcion': 'Quien agregue más productos este mes', 'metrica': 'productos_mes',
     'unidad': 'productos'},
    {'codigo': 'rey_catalogo', 'nombre': 'Rey del Catálogo', 'icono': '📚',
     'descripcion': 'Quien tenga el catálogo más grande', 'metrica': 'productos_activos',
     'unidad': 'productos'},
]


def _reto_del_mes(hoy=None):
    """Devuelve el reto activo del mes (rotación determinista). Pura."""
    if hoy is None:
        hoy = datetime.utcnow()
    idx = (hoy.year * 12 + (hoy.month - 1)) % len(RETOS_MENSUALES)
    return RETOS_MENSUALES[idx]


def _ranking_por_metrica(metrica, inicio, fin, limit, ciudad='', categoria=''):
    """Filas [(id,nombre,ciudad,categoria,logo,slug,score)] según la métrica del reto."""
    from sqlalchemy import text as _t
    params = {'ini': inicio, 'fin': fin, 'lim': limit}
    filtros = " AND n.activo = true AND n.perfil_publico = true"
    if ciudad:
        filtros += " AND LOWER(n.ciudad) LIKE :ciudad"; params['ciudad'] = f"%{ciudad.lower()}%"
    if categoria:
        filtros += " AND LOWER(n.categoria) LIKE :categoria"; params['categoria'] = f"%{categoria.lower()}%"

    base_cols = "n.id_negocio, n.nombre_negocio, n.ciudad, n.categoria, n.logo_url, n.slug"
    if metrica == 'ventas_mes':
        sql = f"""SELECT {base_cols}, COUNT(p.id_pedido) AS score
            FROM negocios n LEFT JOIN pedidos p ON p.negocio_id = n.id_negocio
                AND p.estado='entregado' AND p.fecha_pedido>=:ini AND p.fecha_pedido<:fin
            WHERE 1=1 {filtros}
            GROUP BY {base_cols} HAVING COUNT(p.id_pedido) > 0
            ORDER BY score DESC LIMIT :lim"""
    elif metrica == 'productos_mes':
        sql = f"""SELECT {base_cols}, COUNT(pc.id_producto) AS score
            FROM negocios n LEFT JOIN productos_catalogo pc ON pc.negocio_id = n.id_negocio
                AND pc.fecha_creacion>=:ini AND pc.fecha_creacion<:fin
            WHERE 1=1 {filtros}
            GROUP BY {base_cols} HAVING COUNT(pc.id_producto) > 0
            ORDER BY score DESC LIMIT :lim"""
    else:  # productos_activos (acumulado, no usa rango)
        sql = f"""SELECT {base_cols}, COUNT(pc.id_producto) AS score
            FROM negocios n LEFT JOIN productos_catalogo pc ON pc.negocio_id = n.id_negocio
                AND pc.activo = true
            WHERE 1=1 {filtros}
            GROUP BY {base_cols} HAVING COUNT(pc.id_producto) > 0
            ORDER BY score DESC LIMIT :lim"""
    return [tuple(r) for r in db.session.execute(_t(sql), params).fetchall()]


@gamificacion_bp.route('/gamificacion/reto-mes', methods=['GET'])
def reto_mes():
    """
    Reto temático del mes (S28) + su ranking. Rota automáticamente cada mes.
    GET /api/gamificacion/reto-mes
    """
    try:
        reto = _reto_del_mes()
        inicio, fin, etiqueta = _rango_mes()
        filas = _ranking_por_metrica(reto['metrica'], inicio, fin, 10)
        mi_id = None
        if current_user.is_authenticated:
            try:
                from src.models.colombia_data.negocio import Negocio
                mn = Negocio.query.filter_by(usuario_id=current_user.id_usuario).first()
                mi_id = mn.id_negocio if mn else None
            except Exception:
                pass
        data = _armar_ranking(filas, mi_id)
        return jsonify({'success': True, 'mes': etiqueta, 'reto': reto, **data}), 200
    except Exception as e:
        logger.error(f"Error en reto_mes: {e}", exc_info=True)
        return jsonify({'success': False, 'error': 'Error interno', 'ranking': []}), 200


# Eventos de comunidad (S32): un badge se considera "destacado" (digno de
# aparecer en el feed de la comunidad) si es de nivel Oro o superior.
NIVEL_EVENTO_DESTACADO = 3


def _es_evento_destacado(nivel):
    """True si el badge merece anunciarse en el feed de comunidad. Pura."""
    return (nivel or 0) >= NIVEL_EVENTO_DESTACADO


def _titulo_evento_comunidad(nombre_negocio, nombre_badge):
    """Texto del evento de comunidad. Pura."""
    return f"🏆 {nombre_negocio} ganó «{nombre_badge}»"


@gamificacion_bp.route('/gamificacion/eventos-comunidad', methods=['GET'])
def eventos_comunidad():
    """
    Feed de logros destacados (Oro+) de TODA la comunidad (S32).
    Prueba social: ver a otros ganando inspira. Público.
    GET /api/gamificacion/eventos-comunidad
    """
    from sqlalchemy import text as _t
    try:
        rows = db.session.execute(_t("""
            SELECT n.nombre_negocio, n.slug, b.nombre, b.icono, b.color_primario,
                   b.nivel, o.fecha_obtencion
            FROM negocio_badges_obtenidos o
            JOIN negocio_badges b ON b.id = o.badge_id
            JOIN negocios n ON n.id_negocio = o.negocio_id
            WHERE b.nivel >= :niv
              AND (o.activo IS TRUE OR o.activo IS NULL)
              AND (b.es_secreto IS FALSE OR b.es_secreto IS NULL)
              AND n.activo = true AND n.perfil_publico = true
            ORDER BY o.fecha_obtencion DESC
            LIMIT 15
        """), {'niv': NIVEL_EVENTO_DESTACADO}).fetchall()
        eventos = []
        for r in rows:
            f = r[6]
            eventos.append({
                'negocio': r[0], 'slug': r[1],
                'titulo': _titulo_evento_comunidad(r[0], r[2]),
                'badge': r[2], 'icono': r[3] or 'bi-award-fill',
                'color': r[4] or '#fbbf24', 'nivel': r[5] or 3,
                'fecha': f.isoformat() if f else None,
            })
        return jsonify({'success': True, 'eventos': eventos}), 200
    except Exception as e:
        logger.error(f"Error en eventos_comunidad: {e}", exc_info=True)
        return jsonify({'success': False, 'error': 'Error interno', 'eventos': []}), 200


def _armar_ranking(filas, mi_negocio_id=None):
    """
    Función PURA. Recibe filas [(id, nombre, ciudad, categoria, logo, slug, score)]
    YA ordenadas desc por score, y devuelve {ranking, mi_posicion}.
    """
    medallas = ['🥇', '🥈', '🥉']
    ranking = []
    mi_posicion = None
    for i, f in enumerate(filas):
        pos = i + 1
        if mi_negocio_id is not None and f[0] == mi_negocio_id:
            mi_posicion = pos
        ranking.append({
            'posicion': pos, 'medalla': medallas[i] if i < 3 else '',
            'negocio_id': f[0], 'nombre': f[1], 'ciudad': f[2],
            'categoria': f[3], 'logo_url': f[4], 'slug': f[5],
            'puntaje': int(f[6] or 0),
        })
    return {'ranking': ranking, 'mi_posicion': mi_posicion}


@gamificacion_bp.route('/gamificacion/ligas', methods=['GET'])
def ligas():
    """
    Liga MENSUAL competitiva (S26/S27): ranking por pedidos entregados en el
    mes actual. Resetea cada mes. Filtros opcionales por ciudad y categoría.
    GET /api/gamificacion/ligas?ciudad=Bogota&categoria=ropa&limit=10
    Público.
    """
    from sqlalchemy import text as _t
    ciudad    = request.args.get('ciudad', '').strip()
    categoria = request.args.get('categoria', '').strip()
    limit     = min(int(request.args.get('limit', 10)), 50)
    inicio, fin, etiqueta = _rango_mes()

    try:
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
        filas = db.session.execute(_t(sql), params).fetchall()

        mi_id = None
        if current_user.is_authenticated:
            try:
                from src.models.colombia_data.negocio import Negocio
                mn = Negocio.query.filter_by(usuario_id=current_user.id_usuario).first()
                mi_id = mn.id_negocio if mn else None
            except Exception:
                pass

        data = _armar_ranking([tuple(f) for f in filas], mi_id)
        liga = ciudad or categoria or 'Nacional'
        return jsonify({'success': True, 'mes': etiqueta, 'liga': liga, **data}), 200
    except Exception as e:
        logger.error(f"Error en ligas: {e}", exc_info=True)
        return jsonify({'success': False, 'error': 'Error interno', 'ranking': []}), 200


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
