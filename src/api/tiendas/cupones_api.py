# ═══════════════════════════════════════════════════════════════════════════════
# TUKOMERCIO — API de Cupones de Descuento v1.0
# ═══════════════════════════════════════════════════════════════════════════════
#
# Endpoints del tendero (requieren negocio_id en ruta):
#   POST   /api/negocio/<negocio_id>/cupones          ← crear cupón
#   GET    /api/negocio/<negocio_id>/cupones          ← listar cupones
#   PUT    /api/negocio/<negocio_id>/cupones/<id>     ← editar cupón
#   DELETE /api/negocio/<negocio_id>/cupones/<id>     ← desactivar cupón
#
# Endpoint público (lo llama el checkout del comprador):
#   POST   /api/cupones/validar                       ← valida código + calcula descuento
#
# ═══════════════════════════════════════════════════════════════════════════════

import logging
from datetime import datetime, timezone, date as _date
from flask import Blueprint, request, jsonify
from flask_cors import cross_origin

from src.models.database import db
from src.models.colombia_data.contabilidad.cupones import Cupon

logger = logging.getLogger(__name__)

cupones_bp = Blueprint('cupones', __name__)


# ─────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────

def _parse_date(val):
    """Convierte string 'YYYY-MM-DD' a date, o None."""
    if not val:
        return None
    try:
        return _date.fromisoformat(str(val))
    except Exception:
        return None


def _cupon_from_data(data, cupon=None):
    """
    Rellena (o crea) un objeto Cupon desde el dict `data`.
    Si `cupon` es None se instancia uno nuevo.
    Retorna (cupon, error_str_or_None).
    """
    if cupon is None:
        cupon = Cupon()

    # Código — siempre en mayúsculas, sin espacios
    codigo = str(data.get('codigo', '')).strip().upper().replace(' ', '')
    if not codigo:
        return None, 'El campo codigo es obligatorio'
    cupon.codigo = codigo

    # Tipo
    tipo = data.get('tipo', '')
    if tipo not in ('porcentaje', 'valor_fijo'):
        return None, "tipo debe ser 'porcentaje' o 'valor_fijo'"
    cupon.tipo = tipo

    # Valor
    try:
        valor = float(data['valor'])
        if valor <= 0:
            raise ValueError()
        if tipo == 'porcentaje' and valor > 100:
            return None, 'Para porcentaje, valor no puede superar 100'
        cupon.valor = valor
    except (KeyError, TypeError, ValueError):
        return None, 'valor debe ser un número positivo'

    # Opcionales
    cupon.descripcion = str(data.get('descripcion', '') or '').strip()[:250] or None

    try:
        mc = data.get('min_compra')
        cupon.min_compra = float(mc) if mc is not None else 0
    except (TypeError, ValueError):
        cupon.min_compra = 0

    try:
        md = data.get('max_descuento')
        cupon.max_descuento = float(md) if md is not None else None
    except (TypeError, ValueError):
        cupon.max_descuento = None

    try:
        um = data.get('usos_max')
        cupon.usos_max = int(um) if um is not None else None
    except (TypeError, ValueError):
        cupon.usos_max = None

    cupon.fecha_inicio = _parse_date(data.get('fecha_inicio'))
    cupon.fecha_fin = _parse_date(data.get('fecha_fin'))

    if 'activo' in data:
        cupon.activo = bool(data['activo'])

    return cupon, None


# ─────────────────────────────────────────────────────────────
# POST — Crear cupón (tendero)
# ─────────────────────────────────────────────────────────────

@cupones_bp.route('/negocio/<int:negocio_id>/cupones', methods=['POST', 'OPTIONS'])
@cross_origin()
def crear_cupon(negocio_id):
    if request.method == 'OPTIONS':
        return jsonify({}), 200

    try:
        data = request.get_json(force=True, silent=True) or {}
        cupon, err = _cupon_from_data(data)
        if err:
            return jsonify({'success': False, 'error': err}), 400

        cupon.negocio_id = negocio_id

        # Verificar unicidad
        existente = Cupon.query.filter_by(negocio_id=negocio_id, codigo=cupon.codigo).first()
        if existente:
            return jsonify({'success': False, 'error': f"Ya existe un cupón con el código '{cupon.codigo}'"}), 409

        db.session.add(cupon)
        db.session.commit()

        logger.info(f"🎟️  Cupón creado: {cupon.codigo} negocio={negocio_id}")
        return jsonify({'success': True, 'cupon': cupon.to_dict()}), 201

    except Exception as e:
        db.session.rollback()
        logger.error(f"❌ Error creando cupón: {e}")
        return jsonify({'success': False, 'error': 'Error interno'}), 500


# ─────────────────────────────────────────────────────────────
# GET — Listar cupones (tendero)
# ─────────────────────────────────────────────────────────────

@cupones_bp.route('/negocio/<int:negocio_id>/cupones', methods=['GET', 'OPTIONS'])
@cross_origin()
def listar_cupones(negocio_id):
    if request.method == 'OPTIONS':
        return jsonify({}), 200

    try:
        solo_activos = request.args.get('activos') == '1'
        query = Cupon.query.filter_by(negocio_id=negocio_id)
        if solo_activos:
            query = query.filter_by(activo=True)
        cupones = query.order_by(Cupon.created_at.desc()).all()

        return jsonify({
            'success': True,
            'total': len(cupones),
            'cupones': [c.to_dict() for c in cupones]
        })

    except Exception as e:
        logger.error(f"❌ Error listando cupones: {e}")
        return jsonify({'success': False, 'error': 'Error interno'}), 500


# ─────────────────────────────────────────────────────────────
# PUT — Editar cupón (tendero)
# ─────────────────────────────────────────────────────────────

@cupones_bp.route('/negocio/<int:negocio_id>/cupones/<int:cupon_id>', methods=['PUT', 'OPTIONS'])
@cross_origin()
def editar_cupon(negocio_id, cupon_id):
    if request.method == 'OPTIONS':
        return jsonify({}), 200

    try:
        cupon = Cupon.query.filter_by(id=cupon_id, negocio_id=negocio_id).first()
        if not cupon:
            return jsonify({'success': False, 'error': 'Cupón no encontrado'}), 404

        data = request.get_json(force=True, silent=True) or {}
        cupon_editado, err = _cupon_from_data(data, cupon)
        if err:
            return jsonify({'success': False, 'error': err}), 400

        # Verificar unicidad si cambió el código
        if cupon.codigo != Cupon.query.get(cupon_id).codigo:
            existente = Cupon.query.filter_by(negocio_id=negocio_id, codigo=cupon.codigo).first()
            if existente and existente.id != cupon_id:
                return jsonify({'success': False, 'error': f"Ya existe un cupón con el código '{cupon.codigo}'"}), 409

        db.session.commit()
        logger.info(f"✏️  Cupón editado: {cupon.codigo} negocio={negocio_id}")
        return jsonify({'success': True, 'cupon': cupon.to_dict()})

    except Exception as e:
        db.session.rollback()
        logger.error(f"❌ Error editando cupón: {e}")
        return jsonify({'success': False, 'error': 'Error interno'}), 500


# ─────────────────────────────────────────────────────────────
# DELETE — Desactivar cupón (tendero)
# ─────────────────────────────────────────────────────────────

@cupones_bp.route('/negocio/<int:negocio_id>/cupones/<int:cupon_id>', methods=['DELETE', 'OPTIONS'])
@cross_origin()
def eliminar_cupon(negocio_id, cupon_id):
    if request.method == 'OPTIONS':
        return jsonify({}), 200

    try:
        cupon = Cupon.query.filter_by(id=cupon_id, negocio_id=negocio_id).first()
        if not cupon:
            return jsonify({'success': False, 'error': 'Cupón no encontrado'}), 404

        # Desactivar en lugar de borrar (preserva histórico de usos)
        cupon.activo = False
        db.session.commit()

        logger.info(f"🗑️  Cupón desactivado: {cupon.codigo} negocio={negocio_id}")
        return jsonify({'success': True, 'message': f"Cupón '{cupon.codigo}' desactivado"})

    except Exception as e:
        db.session.rollback()
        logger.error(f"❌ Error eliminando cupón: {e}")
        return jsonify({'success': False, 'error': 'Error interno'}), 500


# ─────────────────────────────────────────────────────────────
# POST — Validar cupón (público — lo llama el checkout)
#
#   Body: { "negocio_id": 4, "codigo": "PROMO10", "subtotal": 120000 }
#   Response: { success, descuento, nuevo_total, cupon: {...} }
# ─────────────────────────────────────────────────────────────

@cupones_bp.route('/cupones/validar', methods=['POST', 'OPTIONS'])
@cross_origin()
def validar_cupon():
    if request.method == 'OPTIONS':
        return jsonify({}), 200

    try:
        data = request.get_json(force=True, silent=True) or {}

        negocio_id = data.get('negocio_id')
        codigo = str(data.get('codigo', '')).strip().upper()
        subtotal = data.get('subtotal', 0)

        if not negocio_id or not codigo:
            return jsonify({'success': False, 'error': 'negocio_id y codigo son requeridos'}), 400

        try:
            subtotal = float(subtotal)
        except (TypeError, ValueError):
            return jsonify({'success': False, 'error': 'subtotal inválido'}), 400

        cupon = Cupon.query.filter_by(negocio_id=negocio_id, codigo=codigo).first()
        if not cupon:
            return jsonify({'success': False, 'error': 'Cupón no encontrado o no válido para esta tienda'}), 404

        valido, mensaje = cupon.es_valido(subtotal)
        if not valido:
            return jsonify({'success': False, 'error': mensaje}), 400

        descuento = cupon.calcular_descuento(subtotal)
        nuevo_total = max(0, subtotal - descuento)

        logger.info(f"✅ Cupón validado: {codigo} negocio={negocio_id} desc={descuento}")

        return jsonify({
            'success': True,
            'descuento': descuento,
            'nuevo_subtotal': nuevo_total,
            'cupon': {
                'id': cupon.id,
                'codigo': cupon.codigo,
                'tipo': cupon.tipo,
                'valor': float(cupon.valor),
                'descripcion': cupon.descripcion,
            }
        })

    except Exception as e:
        logger.error(f"❌ Error validando cupón: {e}")
        return jsonify({'success': False, 'error': 'Error interno'}), 500
