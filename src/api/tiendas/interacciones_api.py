# ═══════════════════════════════════════════════════════════════════════════════
# TUKOMERCIO — Interacciones sociales de tienda (Seguir / Like) v1.0
# ═══════════════════════════════════════════════════════════════════════════════
# © 2024-2026 Carlos Eduardo Huérfano Bermúdez. Todos los derechos reservados.
#   C.C.: 1.064.986.917 — Bogotá D.C., Colombia | carlos-5100@hotmail.com
#   Código CONFIDENCIAL y SECRETO COMERCIAL. Prohibida su copia sin autorización.
# ═══════════════════════════════════════════════════════════════════════════════
#
# Endpoints (un comprador interactúa con un negocio — NO requiere ser dueño):
#   GET  /api/negocio/<id>/social   → {ok, seguidores, likes, siguiendo, liked}  (público)
#   POST /api/negocio/<id>/seguir   → toggle seguir → {ok, siguiendo, seguidores}
#   POST /api/negocio/<id>/like     → toggle like   → {ok, liked, likes}
#
# Auth híbrida (patrón del repo): Flask-Login → header X-User-ID. Sin usuario en los
# POST → 401 {requiere_login:true}. A prueba de fallos: nunca rompe la tienda.
# ═══════════════════════════════════════════════════════════════════════════════

import logging
from datetime import datetime

from flask import Blueprint, request, jsonify
from sqlalchemy import text

from src.models.database import db

logger = logging.getLogger(__name__)

interacciones_bp = Blueprint('interacciones_bp', __name__)

_TIPOS = ('seguir', 'like')


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


def _contar(negocio_id, tipo):
    """Cuenta interacciones de un tipo para un negocio. 0 ante cualquier fallo."""
    try:
        row = db.session.execute(text(
            "SELECT COUNT(*) FROM negocio_interacciones "
            "WHERE negocio_id = :nid AND tipo = :tipo"
        ), {'nid': negocio_id, 'tipo': tipo}).scalar()
        return int(row or 0)
    except Exception as e:
        logger.error(f'Error contando {tipo} de negocio {negocio_id}: {e}')
        db.session.rollback()
        return 0


def _existe(negocio_id, usuario_id, tipo):
    """¿El usuario ya tiene esta interacción con el negocio?"""
    try:
        row = db.session.execute(text(
            "SELECT 1 FROM negocio_interacciones "
            "WHERE negocio_id = :nid AND usuario_id = :uid AND tipo = :tipo LIMIT 1"
        ), {'nid': negocio_id, 'uid': usuario_id, 'tipo': tipo}).first()
        return row is not None
    except Exception as e:
        logger.error(f'Error verificando {tipo} de negocio {negocio_id}: {e}')
        db.session.rollback()
        return False


def _toggle(negocio_id, tipo):
    """Lógica común de seguir/like: alterna y devuelve (activo, conteo)."""
    usuario_id = _get_user_id()
    if not usuario_id:
        return None, None  # sin usuario → el endpoint responde 401

    try:
        if _existe(negocio_id, usuario_id, tipo):
            # Ya existía → quitar (des-seguir / quitar like)
            db.session.execute(text(
                "DELETE FROM negocio_interacciones "
                "WHERE negocio_id = :nid AND usuario_id = :uid AND tipo = :tipo"
            ), {'nid': negocio_id, 'uid': usuario_id, 'tipo': tipo})
            db.session.commit()
            activo = False
        else:
            # No existía → crear (timestamp desde Python: portable PG/SQLite)
            db.session.execute(text(
                "INSERT INTO negocio_interacciones (negocio_id, usuario_id, tipo, created_at) "
                "VALUES (:nid, :uid, :tipo, :ts)"
            ), {'nid': negocio_id, 'uid': usuario_id, 'tipo': tipo, 'ts': datetime.utcnow()})
            db.session.commit()
            activo = True
            if tipo == 'seguir':
                _notificar_nuevo_seguidor(negocio_id, usuario_id)
            # Gamificación: el negocio puede ganar badges sociales (seguidores / me_gusta)
            _verificar_badges_sociales(negocio_id)
        return activo, _contar(negocio_id, tipo)
    except Exception as e:
        db.session.rollback()
        logger.error(f'Error en toggle {tipo} negocio {negocio_id}: {e}')
        # Devolvemos el estado actual sin romper
        return _existe(negocio_id, usuario_id, tipo), _contar(negocio_id, tipo)


def _notificar_nuevo_seguidor(negocio_id, usuario_id):
    """Bonus, fail-safe: avisa al dueño del negocio de un nuevo seguidor.
    Usa el tipo 'seguidor_nuevo' ya definido en el catálogo de notificaciones.
    Si algo falla, se ignora silenciosamente (nunca rompe el seguir)."""
    try:
        from src.models.colombia_data.negocio import Negocio
        from src.models.notification import Notification
        neg = Negocio.query.filter_by(id_negocio=negocio_id).first()
        if not neg or not getattr(neg, 'usuario_id', None):
            return
        notif = Notification(
            user_id=neg.usuario_id,
            negocio_id=negocio_id,
            sender_id=usuario_id,
            type='seguidor_nuevo',
            titulo='¡Nuevo seguidor!',
            message='Alguien empezó a seguir tu negocio.',
        )
        db.session.add(notif)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        logger.debug(f'Notificación de nuevo seguidor omitida: {e}')


def _verificar_badges_sociales(negocio_id):
    """Fail-safe: tras un nuevo seguidor/like, revisa si el negocio desbloqueó
    badges sociales (Primer Seguidor, Influencer, Sensación Viral, …). Si algo
    falla, se ignora (nunca rompe el seguir/like)."""
    try:
        from src.api.utils.badge_verification_service import BadgeVerificationService
        BadgeVerificationService.verificar_badges(negocio_id)
    except Exception as e:
        logger.debug(f'Verificación de badges sociales omitida: {e}')


# ── endpoints ────────────────────────────────────────────────────────────────
@interacciones_bp.route('/negocio/<int:negocio_id>/social', methods=['GET'])
def get_social(negocio_id):
    """Conteos públicos + estado del usuario actual (si lo hay)."""
    usuario_id = _get_user_id()
    siguiendo = _existe(negocio_id, usuario_id, 'seguir') if usuario_id else False
    liked     = _existe(negocio_id, usuario_id, 'like')   if usuario_id else False
    return jsonify({
        'ok': True,
        'seguidores': _contar(negocio_id, 'seguir'),
        'likes':      _contar(negocio_id, 'like'),
        'siguiendo':  siguiendo,
        'liked':      liked,
    })


@interacciones_bp.route('/negocio/<int:negocio_id>/seguir', methods=['POST'])
def toggle_seguir(negocio_id):
    activo, conteo = _toggle(negocio_id, 'seguir')
    if activo is None:
        return jsonify({'ok': False, 'requiere_login': True,
                        'error': 'Inicia sesión para seguir este negocio'}), 401
    return jsonify({'ok': True, 'siguiendo': activo, 'seguidores': conteo})


@interacciones_bp.route('/negocio/<int:negocio_id>/like', methods=['POST'])
def toggle_like(negocio_id):
    activo, conteo = _toggle(negocio_id, 'like')
    if activo is None:
        return jsonify({'ok': False, 'requiere_login': True,
                        'error': 'Inicia sesión para dar me gusta'}), 401
    return jsonify({'ok': True, 'liked': activo, 'likes': conteo})
