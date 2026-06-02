# ═══════════════════════════════════════════════════════════════════════════════
# TUKOMERCIO — API de Reportes de Errores / Feedback v1.0
# ═══════════════════════════════════════════════════════════════════════════════
#
#  POST /api/feedback          — usuario envía un reporte (con sesión)
#  GET  /api/feedback          — admin lista todos los reportes
#  PUT  /api/feedback/<id>     — admin cambia estado del reporte
#
# ═══════════════════════════════════════════════════════════════════════════════

import logging
from datetime import datetime, timezone

from flask           import Blueprint, request, jsonify
from flask_cors      import cross_origin
from src.models.database import db

logger = logging.getLogger(__name__)

feedback_bp = Blueprint('feedback_bp', __name__)

# ── helpers ──────────────────────────────────────────────────────────────────

def _get_user_id():
    """Lee el id del usuario logueado (flask-login o header X-User-ID)."""
    try:
        from flask_login import current_user
        if hasattr(current_user, 'is_authenticated') and current_user.is_authenticated:
            return current_user.id_usuario
    except Exception:
        pass
    return request.headers.get('X-User-ID', type=int)


def _get_rol():
    try:
        from flask_login import current_user
        if hasattr(current_user, 'is_authenticated') and current_user.is_authenticated:
            return getattr(current_user, 'rol', None)
    except Exception:
        pass
    return None


def _is_admin():
    """Comprueba si el usuario tiene rol de admin (igual que admin_api.py)."""
    try:
        from flask_login import current_user
        if hasattr(current_user, 'is_authenticated') and current_user.is_authenticated:
            rol = getattr(current_user, 'rol', '')
            return rol in ('admin', 'superadmin')
    except Exception:
        pass
    # Fallback: cabecera X-Admin-Key (solo para pruebas internas)
    return False


TIPOS_VALIDOS  = {'bug', 'sugerencia', 'otro'}
ESTADOS_VALIDOS = {'nuevo', 'en_revision', 'resuelto'}


# ═══════════════════════════════════════════════════════════════════════════════
# POST /api/feedback  — el usuario envía un reporte
# ═══════════════════════════════════════════════════════════════════════════════
@feedback_bp.route('/api/feedback', methods=['POST', 'OPTIONS'])
@cross_origin(supports_credentials=True)
def crear_feedback():
    if request.method == 'OPTIONS':
        return jsonify({'ok': True}), 200

    user_id = _get_user_id()
    if not user_id:
        return jsonify({'success': False, 'error': 'Se requiere sesión activa para reportar'}), 401

    data = request.get_json(silent=True) or {}

    descripcion = (data.get('descripcion') or '').strip()
    if not descripcion:
        return jsonify({'success': False, 'error': 'La descripción no puede estar vacía'}), 400
    if len(descripcion) > 2000:
        return jsonify({'success': False, 'error': 'Descripción demasiado larga (máx 2000 caracteres)'}), 400

    tipo = (data.get('tipo') or 'bug').lower().strip()
    if tipo not in TIPOS_VALIDOS:
        tipo = 'otro'

    url_contexto = (data.get('url_contexto') or '').strip()[:500] or None
    negocio_id   = data.get('negocio_id')
    if negocio_id:
        try:
            negocio_id = int(negocio_id)
        except (ValueError, TypeError):
            negocio_id = None

    try:
        from src.models.colombia_data.colombia_feedbacks import Feedback

        fb = Feedback(
            usuario_id    = user_id,
            negocio_id    = negocio_id,
            rol_usuario   = _get_rol(),
            tipo_feedback = tipo,
            descripcion   = descripcion,
            url_contexto  = url_contexto,
            estado        = 'nuevo',
            fecha_envio   = datetime.now(timezone.utc),
        )
        db.session.add(fb)
        db.session.commit()

        logger.info(f"📝 Nuevo reporte #{fb.id_feedback} de usuario {user_id} — tipo: {tipo}")
        return jsonify({
            'success': True,
            'id_feedback': fb.id_feedback,
            'mensaje': '¡Gracias! Tu reporte fue enviado. Lo revisaremos pronto.'
        }), 201

    except Exception as e:
        db.session.rollback()
        logger.error(f"❌ Error guardando feedback: {e}", exc_info=True)
        return jsonify({'success': False, 'error': 'Error interno al guardar el reporte'}), 500


# ═══════════════════════════════════════════════════════════════════════════════
# GET /api/feedback  — admin lista todos los reportes
# ═══════════════════════════════════════════════════════════════════════════════
@feedback_bp.route('/api/feedback', methods=['GET'])
@cross_origin(supports_credentials=True)
def listar_feedback():
    if not _is_admin():
        return jsonify({'success': False, 'error': 'Acceso restringido'}), 403

    estado  = request.args.get('estado')      # filtro opcional
    tipo    = request.args.get('tipo')
    page    = max(1, request.args.get('page', 1, type=int))
    per_page = 50

    try:
        from src.models.colombia_data.colombia_feedbacks import Feedback

        q = Feedback.query.order_by(Feedback.fecha_envio.desc())
        if estado and estado in ESTADOS_VALIDOS:
            q = q.filter_by(estado=estado)
        if tipo and tipo in TIPOS_VALIDOS:
            q = q.filter_by(tipo_feedback=tipo)

        total   = q.count()
        items   = q.offset((page - 1) * per_page).limit(per_page).all()
        nuevos  = Feedback.query.filter_by(estado='nuevo').count()

        return jsonify({
            'success': True,
            'total': total,
            'nuevos': nuevos,
            'page': page,
            'per_page': per_page,
            'reportes': [r.serialize() for r in items],
        }), 200

    except Exception as e:
        logger.error(f"❌ Error listando feedback: {e}", exc_info=True)
        return jsonify({'success': False, 'error': 'Error interno'}), 500


# ═══════════════════════════════════════════════════════════════════════════════
# PUT /api/feedback/<id>  — admin cambia estado
# ═══════════════════════════════════════════════════════════════════════════════
@feedback_bp.route('/api/feedback/<int:feedback_id>', methods=['PUT', 'OPTIONS'])
@cross_origin(supports_credentials=True)
def actualizar_feedback(feedback_id):
    if request.method == 'OPTIONS':
        return jsonify({'ok': True}), 200

    if not _is_admin():
        return jsonify({'success': False, 'error': 'Acceso restringido'}), 403

    data   = request.get_json(silent=True) or {}
    estado = (data.get('estado') or '').lower().strip()
    if estado not in ESTADOS_VALIDOS:
        return jsonify({'success': False, 'error': f'Estado inválido. Usa: {ESTADOS_VALIDOS}'}), 400

    try:
        from src.models.colombia_data.colombia_feedbacks import Feedback

        fb = Feedback.query.get(feedback_id)
        if not fb:
            return jsonify({'success': False, 'error': 'Reporte no encontrado'}), 404

        fb.estado = estado
        db.session.commit()
        logger.info(f"✅ Reporte #{feedback_id} marcado como '{estado}'")
        return jsonify({'success': True, 'reporte': fb.serialize()}), 200

    except Exception as e:
        db.session.rollback()
        logger.error(f"❌ Error actualizando feedback: {e}", exc_info=True)
        return jsonify({'success': False, 'error': 'Error interno'}), 500
