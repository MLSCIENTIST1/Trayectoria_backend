# ═══════════════════════════════════════════════════════════════════════════════
# TUKOMERCIO — Wompi API v1.0
# ═══════════════════════════════════════════════════════════════════════════════
#
# Endpoints:
#   GET  /api/negocio/<id>/wompi/config-pub   → público, devuelve {activo, public_key}
#   GET  /api/negocio/<id>/wompi/config       → panel tendero, claves completas
#   PUT  /api/negocio/<id>/wompi/config       → panel tendero, guarda claves
#   POST /api/negocio/<id>/wompi/session      → genera referencia + signature para widget
#
# ═══════════════════════════════════════════════════════════════════════════════

import hashlib
import time
import logging

from flask import Blueprint, request, jsonify
from src.models.database import db

logger = logging.getLogger(__name__)

wompi_bp = Blueprint('wompi_bp', __name__)

# ─── Import defensivo del modelo ─────────────────────────────────────────────
try:
    from src.models.colombia_data.contabilidad.wompi_config import WompiConfig
    _WOMPI_OK = True
except ImportError as e:
    WompiConfig = None
    _WOMPI_OK = False
    logger.error(f'❌ WompiConfig model no disponible: {e}')


# ─── Helper ───────────────────────────────────────────────────────────────────

def _get_or_create_config(negocio_id: int):
    """Devuelve (o crea vacía) la config Wompi de un negocio."""
    cfg = WompiConfig.query.filter_by(negocio_id=negocio_id).first()
    if not cfg:
        cfg = WompiConfig(negocio_id=negocio_id)
        db.session.add(cfg)
        db.session.commit()
    return cfg


def _not_available():
    return jsonify({'error': 'Módulo Wompi no disponible'}), 503


# ─────────────────────────────────────────────────────────────────────────────
# GET /api/negocio/<id>/wompi/config-pub
# Público — checkout lo llama para saber si Wompi está activo
# ─────────────────────────────────────────────────────────────────────────────
@wompi_bp.route('/negocio/<int:negocio_id>/wompi/config-pub', methods=['GET'])
def get_wompi_config_pub(negocio_id):
    """Devuelve solo public_key y activo. SIN integrity_key."""
    if not _WOMPI_OK:
        return _not_available()
    try:
        cfg = WompiConfig.query.filter_by(negocio_id=negocio_id).first()
        if not cfg:
            return jsonify({'activo': False, 'public_key': None, 'ambiente': 'test'})
        return jsonify(cfg.to_dict_public())
    except Exception as e:
        logger.error(f'Error config-pub wompi negocio {negocio_id}: {e}')
        return jsonify({'activo': False, 'public_key': None, 'ambiente': 'test'})


# ─────────────────────────────────────────────────────────────────────────────
# GET /api/negocio/<id>/wompi/config  (panel tendero)
# ─────────────────────────────────────────────────────────────────────────────
@wompi_bp.route('/negocio/<int:negocio_id>/wompi/config', methods=['GET'])
def get_wompi_config(negocio_id):
    if not _WOMPI_OK:
        return _not_available()
    try:
        cfg = _get_or_create_config(negocio_id)
        return jsonify(cfg.to_dict_admin())
    except Exception as e:
        logger.error(f'Error GET wompi config negocio {negocio_id}: {e}')
        return jsonify({'error': str(e)}), 500


# ─────────────────────────────────────────────────────────────────────────────
# PUT /api/negocio/<id>/wompi/config  (panel tendero — guarda claves)
# ─────────────────────────────────────────────────────────────────────────────
@wompi_bp.route('/negocio/<int:negocio_id>/wompi/config', methods=['PUT'])
def put_wompi_config(negocio_id):
    if not _WOMPI_OK:
        return _not_available()
    data = request.get_json() or {}
    try:
        cfg = _get_or_create_config(negocio_id)

        # Actualizar campos que vengan en el body
        if 'public_key' in data:
            cfg.public_key = (data['public_key'] or '').strip() or None
        if 'integrity_key' in data:
            cfg.integrity_key = (data['integrity_key'] or '').strip() or None
        if 'events_key' in data:
            cfg.events_key = (data['events_key'] or '').strip() or None
        if 'ambiente' in data and data['ambiente'] in ('test', 'prod'):
            cfg.ambiente = data['ambiente']
        if 'activo' in data:
            # Solo permitir activar si ya tiene claves
            quiere_activar = bool(data['activo'])
            if quiere_activar and not cfg.tiene_claves():
                return jsonify({
                    'error': 'Debes ingresar la llave pública y la llave de integridad antes de activar Wompi.'
                }), 400
            cfg.activo = quiere_activar

        db.session.commit()
        return jsonify({'success': True, 'config': cfg.to_dict_admin()})

    except Exception as e:
        db.session.rollback()
        logger.error(f'Error PUT wompi config negocio {negocio_id}: {e}')
        return jsonify({'error': str(e)}), 500


# ─────────────────────────────────────────────────────────────────────────────
# POST /api/negocio/<id>/wompi/session
# Genera referencia única + firma de integridad para el widget Wompi
#
# Body JSON:
#   { "total": 95000, "redirect_url": "https://..." }
#
# Response:
#   { "public_key", "reference", "amount_in_cents", "currency", "signature",
#     "redirect_url", "ambiente" }
# ─────────────────────────────────────────────────────────────────────────────
@wompi_bp.route('/negocio/<int:negocio_id>/wompi/session', methods=['POST'])
def crear_sesion_wompi(negocio_id):
    if not _WOMPI_OK:
        return _not_available()

    data = request.get_json() or {}
    total = data.get('total')
    redirect_url = data.get('redirect_url', '')

    if total is None:
        return jsonify({'error': 'Falta el campo "total"'}), 400

    try:
        total_num = float(total)
    except (TypeError, ValueError):
        return jsonify({'error': '"total" debe ser un número'}), 400

    if total_num <= 0:
        return jsonify({'error': 'El total debe ser mayor a cero'}), 400

    try:
        cfg = WompiConfig.query.filter_by(negocio_id=negocio_id).first()
        if not cfg or not cfg.activo or not cfg.tiene_claves():
            return jsonify({'error': 'Wompi no está configurado o activo para esta tienda'}), 404

        # Referencia única: TK-{negocio_id}-{timestamp_ms}
        reference = f'TK-{negocio_id}-{int(time.time() * 1000)}'
        amount_in_cents = int(round(total_num * 100))
        currency = 'COP'

        # Firma de integridad: SHA256(reference + amount_in_cents + currency + integrity_key)
        pre_hash = f'{reference}{amount_in_cents}{currency}{cfg.integrity_key}'
        signature = hashlib.sha256(pre_hash.encode('utf-8')).hexdigest()

        return jsonify({
            'public_key': cfg.public_key,
            'reference': reference,
            'amount_in_cents': amount_in_cents,
            'currency': currency,
            'signature': signature,
            'redirect_url': redirect_url,
            'ambiente': cfg.ambiente,
        })

    except Exception as e:
        logger.error(f'Error POST wompi/session negocio {negocio_id}: {e}')
        return jsonify({'error': str(e)}), 500
