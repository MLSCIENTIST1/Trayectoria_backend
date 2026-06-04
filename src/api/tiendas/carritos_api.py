# ═══════════════════════════════════════════════════════════════════════════════
# TUKOMERCIO — Carritos Abandonados API v1.1
# ═══════════════════════════════════════════════════════════════════════════════
#
# Endpoints públicos (checkout.js):
#   POST /api/negocio/<id>/carrito/guardar     → upsert carrito (fire-and-forget)
#   POST /api/negocio/<id>/carrito/recuperado  → marcar como convertido
#
# Endpoints del tendero (panel):
#   GET  /api/negocio/<id>/carritos/resumen    → totales y valor perdido
#   GET  /api/negocio/<id>/carritos            → lista (?estado=, ?page=)
#   PUT  /api/negocio/<id>/carrito/<cid>/estado → ignorado | abandonado
#
# NOTA: Los modelos se importan de forma LAZY (primer request, no en startup).
# Esto evita que CarritoAbandonado quede en el SQLAlchemy mapper registry
# durante db.create_all() y cause conflictos que rompan otras rutas.
#
# ═══════════════════════════════════════════════════════════════════════════════

import logging
from flask import Blueprint, request, jsonify

logger = logging.getLogger(__name__)
carritos_bp = Blueprint('carritos_bp', __name__)

# ─── Estado lazy de módulo ────────────────────────────────────────────────────
_db  = None
_CA  = None   # alias para CarritoAbandonado
_OK  = None   # None = no intentado; True = OK; False = falló


def _load():
    """Carga los modelos la primera vez que se llama un endpoint."""
    global _db, _CA, _OK
    if _OK is not None:
        return _OK
    try:
        from src.models.database import db as _db_mod
        from src.models.colombia_data.contabilidad.carrito_abandonado import (
            CarritoAbandonado as _CAmod
        )
        _db = _db_mod
        _CA = _CAmod
        _OK = True
    except Exception as e:
        logger.error(f'❌ CarritoAbandonado no disponible: {e}')
        _OK = False
    return _OK


def _err(msg, code=400): return jsonify({'error': msg}), code
def _nav(): return _err('Módulo de carritos no disponible', 503)


# ══════════════════════════════════════════════════════════════════════════════
# ENDPOINTS PÚBLICOS — llamados desde checkout.js
# ══════════════════════════════════════════════════════════════════════════════

@carritos_bp.route('/negocio/<int:negocio_id>/carrito/guardar', methods=['POST'])
def guardar_carrito(negocio_id):
    """
    Fire-and-forget: guarda o actualiza el carrito de un comprador.
    Siempre devuelve 200 para no bloquear el flujo de compra.
    """
    if not _load():
        return jsonify({'ok': False}), 200
    try:
        data     = request.get_json(silent=True) or {}
        telefono = (data.get('telefono') or '').strip()
        if not telefono:
            return jsonify({'ok': False}), 200

        productos = data.get('productos') or []
        if not productos:
            return jsonify({'ok': False}), 200

        total  = float(data.get('total') or 0)
        nombre = (data.get('nombre') or '').strip() or None
        correo = (data.get('correo')  or '').strip().lower() or None

        _CA.upsert(negocio_id=negocio_id, telefono=telefono,
                   productos=productos, total=total, nombre=nombre, correo=correo)
        _db.session.commit()
        return jsonify({'ok': True}), 200

    except Exception as e:
        try: _db.session.rollback()
        except Exception: pass
        logger.error(f'Error guardar_carrito negocio {negocio_id}: {e}')
        return jsonify({'ok': False}), 200


@carritos_bp.route('/negocio/<int:negocio_id>/carrito/recuperado', methods=['POST'])
def marcar_recuperado(negocio_id):
    """
    Llamado desde checkout.js cuando el pedido se completa.
    Body: { telefono, pedido_id? }
    """
    if not _load():
        return jsonify({'ok': False}), 200
    try:
        data      = request.get_json(silent=True) or {}
        telefono  = (data.get('telefono') or '').strip()
        pedido_id = data.get('pedido_id')
        if not telefono:
            return jsonify({'ok': False}), 200

        _CA.marcar_recuperado(negocio_id, telefono, pedido_id)
        _db.session.commit()
        return jsonify({'ok': True}), 200

    except Exception as e:
        try: _db.session.rollback()
        except Exception: pass
        logger.error(f'Error marcar_recuperado negocio {negocio_id}: {e}')
        return jsonify({'ok': False}), 200


# ══════════════════════════════════════════════════════════════════════════════
# ENDPOINTS DEL TENDERO — panel
# ══════════════════════════════════════════════════════════════════════════════

@carritos_bp.route('/negocio/<int:negocio_id>/carritos/resumen', methods=['GET'])
def resumen_carritos(negocio_id):
    """Cards del encabezado del panel."""
    if not _load(): return _nav()
    try:
        from sqlalchemy import func

        tots = _db.session.query(
            _CA.estado,
            func.count(_CA.id).label('qty'),
            func.sum(_CA.total_estimado).label('valor'),
        ).filter(_CA.negocio_id == negocio_id)\
         .group_by(_CA.estado).all()

        mapa = {r.estado: {'qty': r.qty, 'valor': float(r.valor or 0)} for r in tots}

        total_ab  = mapa.get('abandonado', {}).get('qty', 0)
        valor_ab  = mapa.get('abandonado', {}).get('valor', 0.0)
        total_rec = mapa.get('recuperado', {}).get('qty', 0)
        valor_rec = mapa.get('recuperado', {}).get('valor', 0.0)
        total_ig  = mapa.get('ignorado',   {}).get('qty', 0)
        total_todo = total_ab + total_rec + total_ig

        return jsonify({
            'abandonados':       total_ab,
            'valor_abandonado':  valor_ab,
            'recuperados':       total_rec,
            'valor_recuperado':  valor_rec,
            'ignorados':         total_ig,
            'tasa_recuperacion': round(total_rec / total_todo * 100, 1) if total_todo else 0,
        })
    except Exception as e:
        logger.error(f'Error resumen_carritos negocio {negocio_id}: {e}')
        return _err(str(e), 500)


@carritos_bp.route('/negocio/<int:negocio_id>/carritos', methods=['GET'])
def listar_carritos(negocio_id):
    """Lista paginada. ?estado=abandonado|recuperado|ignorado|todos  ?page=1"""
    if not _load(): return _nav()

    estado = request.args.get('estado', 'abandonado')
    page   = max(1, int(request.args.get('page', 1)))
    PER    = 20

    try:
        q = _CA.query.filter_by(negocio_id=negocio_id)
        if estado != 'todos':
            q = q.filter_by(estado=estado)
        q = q.order_by(_CA.updated_at.desc())

        total = q.count()
        items = q.offset((page - 1) * PER).limit(PER).all()

        return jsonify({
            'carritos':    [c.to_dict() for c in items],
            'total':       total,
            'page':        page,
            'per_page':    PER,
            'total_pages': max(1, (total + PER - 1) // PER),
        })
    except Exception as e:
        logger.error(f'Error listar_carritos negocio {negocio_id}: {e}')
        return _err(str(e), 500)


@carritos_bp.route('/negocio/<int:negocio_id>/carrito/<int:carrito_id>/estado', methods=['PUT'])
def actualizar_estado(negocio_id, carrito_id):
    """El tendero marca un carrito como ignorado o lo restaura a abandonado."""
    if not _load(): return _nav()
    data   = request.get_json() or {}
    nuevo  = (data.get('estado') or '').strip()
    if nuevo not in ('ignorado', 'abandonado'):
        return _err('Estado inválido. Usa: ignorado | abandonado')
    try:
        c = _CA.query.filter_by(id=carrito_id, negocio_id=negocio_id).first()
        if not c: return _err('Carrito no encontrado', 404)
        if c.estado == 'recuperado':
            return _err('No se puede modificar un carrito recuperado')
        c.estado = nuevo
        _db.session.commit()
        return jsonify({'success': True, 'carrito': c.to_dict()})
    except Exception as e:
        try: _db.session.rollback()
        except Exception: pass
        return _err(str(e), 500)


# ═══ A-SEC-2: tenant isolation ═══
from src.api.utils.seguridad import crear_guard_tenant as _guard_tenant
carritos_bp.before_request(_guard_tenant(publicos={"guardar_carrito", "marcar_recuperado"}))
