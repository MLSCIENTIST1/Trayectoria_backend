# ═══════════════════════════════════════════════════════════════════════════════
# TUKOMERCIO — Analytics API v1.0
# ═══════════════════════════════════════════════════════════════════════════════
#
# Endpoints:
#   POST /api/negocio/<id>/analytics/visita     → registra una visita (público)
#   GET  /api/negocio/<id>/analytics/resumen    → dashboard tendero
#   GET  /api/negocio/<id>/trust                → confianza pública para el comprador
#
# ═══════════════════════════════════════════════════════════════════════════════

import logging
from datetime import date, timedelta

from flask import Blueprint, request, jsonify
from sqlalchemy import func

from src.models.database import db

logger = logging.getLogger(__name__)

analytics_bp = Blueprint('analytics_bp', __name__)

# ─── Imports defensivos ───────────────────────────────────────────────────────
try:
    from src.models.colombia_data.contabilidad.tienda_visita import TiendaVisita
    _VISITA_OK = True
except ImportError as e:
    TiendaVisita = None; _VISITA_OK = False
    logger.error(f'❌ TiendaVisita no disponible: {e}')

try:
    from src.models.colombia_data.negocio import Negocio
    _NEGOCIO_OK = True
except ImportError as e:
    Negocio = None; _NEGOCIO_OK = False

try:
    from src.models.compradores.pedido import Pedido
    _PEDIDO_OK = True
except ImportError as e:
    Pedido = None; _PEDIDO_OK = False

try:
    from src.models.colombia_data.contabilidad.operaciones_y_catalogo import ProductoReview
    _REVIEW_OK = True
except ImportError as e:
    ProductoReview = None; _REVIEW_OK = False

try:
    from src.models.colombia_data.ratings.negocio_badge_obtenido import NegocioBadgeObtenido
    _BADGE_OK = True
except ImportError as e:
    NegocioBadgeObtenido = None; _BADGE_OK = False


# ─────────────────────────────────────────────────────────────────────────────
# POST /api/negocio/<id>/analytics/visita
# Público — la tienda llama esto en cada carga (fire and forget)
# ─────────────────────────────────────────────────────────────────────────────
@analytics_bp.route('/negocio/<int:negocio_id>/analytics/visita', methods=['POST'])
def registrar_visita(negocio_id):
    if not _VISITA_OK:
        return jsonify({'ok': False}), 200   # silencioso

    try:
        TiendaVisita.registrar(negocio_id)
        return jsonify({'ok': True}), 200
    except Exception as e:
        logger.error(f'Error registrando visita negocio {negocio_id}: {e}')
        return jsonify({'ok': False}), 200   # siempre 200 para no bloquear la tienda


# ─────────────────────────────────────────────────────────────────────────────
# GET /api/negocio/<id>/analytics/resumen
# Panel tendero — estadísticas de visitas + pedidos + reseñas
# ─────────────────────────────────────────────────────────────────────────────
@analytics_bp.route('/negocio/<int:negocio_id>/analytics/resumen', methods=['GET'])
def resumen_analytics(negocio_id):
    hoy     = date.today()
    hace7   = hoy - timedelta(days=6)
    hace30  = hoy - timedelta(days=29)

    # ── Visitas ───────────────────────────────────────────────────────────────
    visitas = {}
    if _VISITA_OK:
        try:
            # Hoy
            fila_hoy = TiendaVisita.query.filter_by(negocio_id=negocio_id, fecha=hoy).first()
            visitas['hoy'] = fila_hoy.contador if fila_hoy else 0

            # Últimos 7 días
            v7 = db.session.query(func.sum(TiendaVisita.contador)).filter(
                TiendaVisita.negocio_id == negocio_id,
                TiendaVisita.fecha >= hace7
            ).scalar() or 0
            visitas['semana'] = int(v7)

            # Últimos 30 días
            v30 = db.session.query(func.sum(TiendaVisita.contador)).filter(
                TiendaVisita.negocio_id == negocio_id,
                TiendaVisita.fecha >= hace30
            ).scalar() or 0
            visitas['mes'] = int(v30)

            # Total histórico
            vtotal = db.session.query(func.sum(TiendaVisita.contador)).filter(
                TiendaVisita.negocio_id == negocio_id
            ).scalar() or 0
            visitas['total'] = int(vtotal)

            # Por día (últimos 30) para el gráfico
            filas = TiendaVisita.query.filter(
                TiendaVisita.negocio_id == negocio_id,
                TiendaVisita.fecha >= hace30
            ).order_by(TiendaVisita.fecha).all()
            visitas['por_dia'] = [
                {'fecha': str(f.fecha), 'n': f.contador} for f in filas
            ]
        except Exception as e:
            logger.error(f'Error visitas analytics {negocio_id}: {e}')
            visitas = {'hoy': 0, 'semana': 0, 'mes': 0, 'total': 0, 'por_dia': []}
    else:
        visitas = {'hoy': 0, 'semana': 0, 'mes': 0, 'total': 0, 'por_dia': []}

    # ── Pedidos ───────────────────────────────────────────────────────────────
    pedidos = {'hoy': 0, 'semana': 0, 'mes': 0, 'total': 0}
    if _PEDIDO_OK:
        try:
            from sqlalchemy import cast, Date as SADate
            hoy_dt  = hoy
            hace7_dt = hace7
            hace30_dt = hace30

            base = Pedido.query.filter(
                Pedido.negocio_id == negocio_id,
                Pedido.estado != 'cancelado'
            )
            pedidos['total'] = base.count()
            pedidos['mes']   = base.filter(
                func.cast(Pedido.fecha_pedido, db.Date) >= hace30_dt).count()
            pedidos['semana'] = base.filter(
                func.cast(Pedido.fecha_pedido, db.Date) >= hace7_dt).count()
            pedidos['hoy']    = base.filter(
                func.cast(Pedido.fecha_pedido, db.Date) == hoy_dt).count()
            pedidos['entregados'] = Pedido.query.filter_by(
                negocio_id=negocio_id, estado='entregado').count()
        except Exception as e:
            logger.error(f'Error pedidos analytics {negocio_id}: {e}')

    # ── Reseñas ───────────────────────────────────────────────────────────────
    resenas = {'total': 0, 'rating_promedio': None}
    if _REVIEW_OK:
        try:
            cnt = ProductoReview.query.filter_by(
                negocio_id=negocio_id, aprobado=True).count()
            avg = db.session.query(func.avg(ProductoReview.rating)).filter_by(
                negocio_id=negocio_id, aprobado=True).scalar()
            resenas['total']         = cnt
            resenas['rating_promedio'] = round(float(avg), 1) if avg else None
        except Exception as e:
            logger.error(f'Error reseñas analytics {negocio_id}: {e}')

    return jsonify({
        'negocio_id': negocio_id,
        'periodo': {'hoy': str(hoy), 'hace7': str(hace7), 'hace30': str(hace30)},
        'visitas': visitas,
        'pedidos': pedidos,
        'resenas': resenas,
    })


# ─────────────────────────────────────────────────────────────────────────────
# GET /api/negocio/<id>/trust
# Público — datos de confianza para mostrar en la tienda al comprador
# ─────────────────────────────────────────────────────────────────────────────
@analytics_bp.route('/negocio/<int:negocio_id>/trust', methods=['GET'])
def get_trust_data(negocio_id):
    """
    Devuelve indicadores de confianza para la trust strip de la tienda.
    Sin datos privados: solo métricas públicas.
    """
    trust = {
        'pedidos_completados': 0,
        'rating_promedio':     None,
        'num_resenas':         0,
        'verificado':          False,
        'num_badges':          0,
        'miembro_desde':       None,   # "Desde ene 2024"
        'visitas_totales':     0,
    }

    # Negocio base
    if _NEGOCIO_OK:
        try:
            neg = Negocio.query.filter_by(id_negocio=negocio_id).first()
            if neg:
                trust['verificado'] = bool(neg.verificado)
                if neg.fecha_registro:
                    trust['miembro_desde'] = neg.fecha_registro.strftime('%b %Y')
        except Exception as e:
            logger.error(f'Error negocio trust {negocio_id}: {e}')

    # Pedidos entregados
    if _PEDIDO_OK:
        try:
            trust['pedidos_completados'] = Pedido.query.filter_by(
                negocio_id=negocio_id, estado='entregado').count()
        except Exception as e:
            logger.error(f'Error pedidos trust {negocio_id}: {e}')

    # Reseñas y rating
    if _REVIEW_OK:
        try:
            cnt = ProductoReview.query.filter_by(
                negocio_id=negocio_id, aprobado=True).count()
            avg = db.session.query(func.avg(ProductoReview.rating)).filter_by(
                negocio_id=negocio_id, aprobado=True).scalar()
            trust['num_resenas']    = cnt
            trust['rating_promedio'] = round(float(avg), 1) if avg else None
        except Exception as e:
            logger.error(f'Error reseñas trust {negocio_id}: {e}')

    # Badges BizScore
    if _BADGE_OK:
        try:
            trust['num_badges'] = NegocioBadgeObtenido.query.filter_by(
                negocio_id=negocio_id).count()
        except Exception as e:
            logger.error(f'Error badges trust {negocio_id}: {e}')

    # Visitas totales
    if _VISITA_OK:
        try:
            v = db.session.query(func.sum(TiendaVisita.contador)).filter(
                TiendaVisita.negocio_id == negocio_id).scalar() or 0
            trust['visitas_totales'] = int(v)
        except Exception as e:
            logger.error(f'Error visitas trust {negocio_id}: {e}')

    return jsonify(trust)
