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
import hmac
import time
import logging

import requests as http_requests
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


# ─────────────────────────────────────────────────────────────────────────────
# GET /api/negocio/<id>/wompi/verify?tx_id=WOMPI_TRANSACTION_ID
# Consulta el estado real de una transacción Wompi (PSE, Nequi async).
# Llamado desde pago-exitoso.html para mostrar el estado correcto.
# ─────────────────────────────────────────────────────────────────────────────
@wompi_bp.route('/negocio/<int:negocio_id>/wompi/verify', methods=['GET'])
def verify_wompi_transaction(negocio_id):
    """Consulta una transacción en la API de Wompi y devuelve su estado."""
    if not _WOMPI_OK:
        return _not_available()

    tx_id = request.args.get('tx_id', '').strip()
    if not tx_id:
        return jsonify({'error': 'Falta el parámetro tx_id'}), 400

    try:
        cfg = WompiConfig.query.filter_by(negocio_id=negocio_id).first()
        if not cfg or not cfg.public_key:
            return jsonify({'error': 'Wompi no configurado para esta tienda'}), 404

        base = ('https://sandbox.wompi.co/v1'
                if cfg.ambiente == 'test'
                else 'https://production.wompi.co/v1')

        resp = http_requests.get(
            f'{base}/transactions/{tx_id}',
            headers={'Authorization': f'Bearer {cfg.public_key}'},
            timeout=10
        )
        if not resp.ok:
            logger.warning(f'Wompi verify tx {tx_id}: HTTP {resp.status_code}')
            return jsonify({'status': 'ERROR', 'detail': 'No se pudo consultar a Wompi'}), 502

        tx_data = resp.json().get('data', {})
        return jsonify({
            'status':    tx_data.get('status', 'UNKNOWN'),
            'reference': tx_data.get('reference'),
            'amount':    tx_data.get('amount_in_cents', 0) / 100,
            'currency':  tx_data.get('currency', 'COP'),
        })

    except Exception as e:
        logger.error(f'Error verify wompi tx {tx_id}: {e}')
        return jsonify({'error': str(e)}), 500


# ─────────────────────────────────────────────────────────────────────────────
# POST /api/wompi/webhook
# Recibe eventos asíncronos de Wompi (PSE, Nequi, pagos pendientes).
# Valida X-Event-Checksum y actualiza el estado del pedido.
#
# Wompi envía:
#   POST con body JSON:
#   {
#     "event": "transaction.updated",
#     "data": { "transaction": { "id", "status", "reference",
#                                "amount_in_cents", "currency",
#                                "payment_method_type", ... } },
#     "sent_at": "..."
#   }
#
# Checksum header: X-Event-Checksum
#   sha256( tx.id + tx.status + tx.reference + tx.amount_in_cents
#           + tx.currency + tx.payment_method_type + events_key )
# ─────────────────────────────────────────────────────────────────────────────
@wompi_bp.route('/wompi/webhook', methods=['POST'])
def wompi_webhook():
    """Webhook global de Wompi — actualiza estado de pedidos tras pago async."""
    if not _WOMPI_OK:
        # Devolver 200 para que Wompi no reintente indefinidamente
        return jsonify({'ok': False, 'reason': 'módulo no disponible'}), 200

    payload = request.get_json(silent=True) or {}
    event   = payload.get('event', '')
    tx      = (payload.get('data') or {}).get('transaction') or {}

    if not tx:
        logger.warning('Wompi webhook: payload sin transaction')
        return jsonify({'ok': True}), 200  # ignorar eventos vacíos

    # ── Extraer negocio_id desde la referencia (TK-{negocio_id}-{ts}) ──────
    reference = tx.get('reference', '')
    negocio_id = None
    if reference.startswith('TK-'):
        partes = reference.split('-')
        if len(partes) >= 3:
            try:
                negocio_id = int(partes[1])
            except ValueError:
                pass

    if not negocio_id:
        logger.warning(f'Wompi webhook: referencia no parseable "{reference}"')
        return jsonify({'ok': True}), 200

    # ── Validar checksum (A-SEC-2: OBLIGATORIO; sin firma válida NO se procesa) ──
    checksum_header = request.headers.get('X-Event-Checksum', '')
    cfg = WompiConfig.query.filter_by(negocio_id=negocio_id).first()
    if not (cfg and cfg.events_key) or not checksum_header:
        # Sin clave de eventos configurada o sin firma → no podemos confiar en el evento.
        logger.warning(f'Wompi webhook RECHAZADO (sin firma verificable) negocio {negocio_id}')
        return jsonify({'ok': False, 'reason': 'firma_requerida'}), 401
    pre = (
        str(tx.get('id', ''))
        + str(tx.get('status', ''))
        + str(tx.get('reference', ''))
        + str(tx.get('amount_in_cents', ''))
        + str(tx.get('currency', ''))
        + str(tx.get('payment_method_type', ''))
        + cfg.events_key
    )
    expected = hashlib.sha256(pre.encode('utf-8')).hexdigest()
    if not hmac.compare_digest(expected, checksum_header):
        logger.warning(f'Wompi webhook: checksum inválido para negocio {negocio_id}')
        return jsonify({'ok': False, 'reason': 'checksum inválido'}), 401

    # ── Actualizar pedido ───────────────────────────────────────────────────
    try:
        from src.models.compradores.pedido import Pedido

        pedido = Pedido.query.filter_by(
            negocio_id=negocio_id,
            referencia_pago=reference
        ).first()

        if not pedido:
            # PSE/Nequi: el pedido aún no existe; Wompi reintentará
            logger.info(f'Wompi webhook: pedido con ref "{reference}" no encontrado (aún no creado)')
            return jsonify({'ok': True}), 200

        status = tx.get('status', '')
        if status == 'APPROVED':
            # A-SEC-2: el monto pagado debe coincidir con el total del pedido (evita replay/parcial).
            try:
                pagado_cents = int(tx.get('amount_in_cents') or 0)
                esperado_cents = int(round(float(pedido.total or 0) * 100))
            except (TypeError, ValueError):
                pagado_cents, esperado_cents = -1, -2
            if pagado_cents != esperado_cents:
                logger.error(f'🚨 Wompi webhook: monto no coincide pedido {pedido.codigo_pedido} '
                             f'(pagado {pagado_cents} vs esperado {esperado_cents}) — NO se marca pagado')
                return jsonify({'ok': False, 'reason': 'monto_no_coincide'}), 400
            if pedido.estado_pago == 'pagado':
                return jsonify({'ok': True, 'idempotente': True}), 200   # ya procesado
            pedido.estado_pago = 'pagado'
            pedido.estado = 'confirmado'
        elif status == 'DECLINED':
            pedido.estado_pago = 'fallido'
        elif status == 'VOIDED':
            pedido.estado_pago = 'anulado'
        # PENDING: no cambiar — ya está en pendiente

        db.session.commit()
        logger.info(f'✅ Wompi webhook procesado: pedido {pedido.codigo_pedido} → {status}')

    except Exception as e:
        db.session.rollback()
        logger.error(f'Error procesando webhook Wompi: {e}')
        # Devolver 200 de todas formas para evitar retries infinitos
        return jsonify({'ok': False, 'reason': str(e)}), 200

    return jsonify({'ok': True}), 200


# ═══ A-SEC-2: tenant isolation ═══
from src.api.utils.seguridad import crear_guard_tenant as _guard_tenant
wompi_bp.before_request(_guard_tenant(
    publicos={"get_wompi_config_pub", "crear_sesion_wompi", "verify_wompi_transaction", "wompi_webhook"},
))
