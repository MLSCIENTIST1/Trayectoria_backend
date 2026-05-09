# ═══════════════════════════════════════════════════════════════════════════════
# TUKOMERCIO — Equipo API v1.0
# ═══════════════════════════════════════════════════════════════════════════════
#
# Endpoints:
#   GET    /api/negocio/<id>/equipo              → listar miembros
#   POST   /api/negocio/<id>/equipo/invitar      → invitar nuevo miembro
#   PUT    /api/negocio/<id>/equipo/<mid>/rol    → cambiar rol
#   PUT    /api/negocio/<id>/equipo/<mid>/estado → activar/suspender
#   DELETE /api/negocio/<id>/equipo/<mid>        → remover miembro
#   GET    /api/invitacion/<token>               → verificar token (público)
#   POST   /api/invitacion/<token>/aceptar       → aceptar invitación (público)
#
# ═══════════════════════════════════════════════════════════════════════════════

import logging
from datetime import datetime, timezone, timedelta

from flask import Blueprint, request, jsonify
from src.models.database import db

logger = logging.getLogger(__name__)

equipo_bp = Blueprint('equipo_bp', __name__)

# ─── Imports defensivos ───────────────────────────────────────────────────────
try:
    from src.models.colombia_data.equipo import EmpleadoNegocio, ROLES
    _EQUIPO_OK = True
except ImportError as e:
    EmpleadoNegocio = None; ROLES = {}; _EQUIPO_OK = False
    logger.error(f'❌ EmpleadoNegocio no disponible: {e}')

try:
    from src.models.colombia_data.negocio import Negocio
    _NEG_OK = True
except ImportError:
    Negocio = None; _NEG_OK = False

try:
    from src.models.usuarios import Usuario
    _USR_OK = True
except ImportError:
    Usuario = None; _USR_OK = False


def _err(msg, code=400):
    return jsonify({'error': msg}), code

def _not_avail():
    return _err('Módulo de equipo no disponible', 503)


# ─────────────────────────────────────────────────────────────────────────────
# GET /api/negocio/<id>/equipo
# ─────────────────────────────────────────────────────────────────────────────
@equipo_bp.route('/negocio/<int:negocio_id>/equipo', methods=['GET'])
def listar_equipo(negocio_id):
    if not _EQUIPO_OK: return _not_avail()
    try:
        miembros = EmpleadoNegocio.query.filter_by(negocio_id=negocio_id)\
            .order_by(EmpleadoNegocio.invitado_en).all()
        return jsonify([m.to_dict() for m in miembros])
    except Exception as e:
        logger.error(f'Error GET equipo {negocio_id}: {e}')
        return _err(str(e), 500)


# ─────────────────────────────────────────────────────────────────────────────
# POST /api/negocio/<id>/equipo/invitar
# Body: { email, rol, nombre_display? }
# ─────────────────────────────────────────────────────────────────────────────
@equipo_bp.route('/negocio/<int:negocio_id>/equipo/invitar', methods=['POST'])
def invitar_miembro(negocio_id):
    if not _EQUIPO_OK: return _not_avail()
    data = request.get_json() or {}

    email = (data.get('email') or '').strip().lower()
    rol   = (data.get('rol')   or 'vendedor').strip()
    nombre_display = (data.get('nombre_display') or '').strip() or None

    if not email:
        return _err('El email es requerido')
    if rol not in ROLES:
        return _err(f'Rol inválido. Opciones: {", ".join(ROLES.keys())}')
    if rol == 'dueno':
        return _err('No puedes invitar a alguien como dueño')

    try:
        # Verificar que el negocio existe
        if _NEG_OK:
            neg = Negocio.query.filter_by(id_negocio=negocio_id).first()
            if not neg:
                return _err('Negocio no encontrado', 404)

        # Verificar duplicado
        existente = EmpleadoNegocio.query.filter_by(
            negocio_id=negocio_id, email=email).first()
        if existente:
            if existente.estado == 'suspendido':
                # Reactivar
                existente.estado = 'pendiente'
                existente.rol    = rol
                existente.token_invitacion = EmpleadoNegocio.generar_token()
                existente.token_expira     = datetime.now(timezone.utc) + timedelta(days=7)
                db.session.commit()
                return jsonify({'success': True, 'miembro': existente.to_dict(),
                                'token': existente.token_invitacion,
                                'nuevo': False})
            return _err('Este email ya tiene una invitación en este negocio')

        # Si el email ya tiene cuenta → vincular directamente como pendiente
        usuario_id = None
        if _USR_OK:
            usr = Usuario.query.filter_by(correo=email).first()
            if usr:
                usuario_id = usr.id_usuario

        token = EmpleadoNegocio.generar_token()
        miembro = EmpleadoNegocio(
            negocio_id       = negocio_id,
            email            = email,
            nombre_display   = nombre_display,
            rol              = rol,
            estado           = 'pendiente',
            usuario_id       = usuario_id,
            token_invitacion = token,
            token_expira     = datetime.now(timezone.utc) + timedelta(days=7),
        )
        db.session.add(miembro)
        db.session.commit()

        return jsonify({
            'success': True,
            'miembro': miembro.to_dict(),
            'token': token,   # el dueño usa esto para generar el link de invitación
            'nuevo': True
        }), 201

    except Exception as e:
        db.session.rollback()
        logger.error(f'Error invitar miembro negocio {negocio_id}: {e}')
        return _err(str(e), 500)


# ─────────────────────────────────────────────────────────────────────────────
# PUT /api/negocio/<id>/equipo/<mid>/rol
# Body: { rol }
# ─────────────────────────────────────────────────────────────────────────────
@equipo_bp.route('/negocio/<int:negocio_id>/equipo/<int:miembro_id>/rol', methods=['PUT'])
def cambiar_rol(negocio_id, miembro_id):
    if not _EQUIPO_OK: return _not_avail()
    data = request.get_json() or {}
    nuevo_rol = (data.get('rol') or '').strip()

    if nuevo_rol not in ROLES:
        return _err(f'Rol inválido: {nuevo_rol}')
    if nuevo_rol == 'dueno':
        return _err('No puedes asignar el rol de dueño')

    try:
        m = EmpleadoNegocio.query.filter_by(
            id=miembro_id, negocio_id=negocio_id).first()
        if not m: return _err('Miembro no encontrado', 404)
        if m.rol == 'dueno': return _err('No puedes cambiar el rol del dueño')

        m.rol = nuevo_rol
        db.session.commit()
        return jsonify({'success': True, 'miembro': m.to_dict()})
    except Exception as e:
        db.session.rollback()
        return _err(str(e), 500)


# ─────────────────────────────────────────────────────────────────────────────
# PUT /api/negocio/<id>/equipo/<mid>/estado
# Body: { estado }  → 'activo' | 'suspendido'
# ─────────────────────────────────────────────────────────────────────────────
@equipo_bp.route('/negocio/<int:negocio_id>/equipo/<int:miembro_id>/estado', methods=['PUT'])
def cambiar_estado(negocio_id, miembro_id):
    if not _EQUIPO_OK: return _not_avail()
    data = request.get_json() or {}
    nuevo_estado = (data.get('estado') or '').strip()

    if nuevo_estado not in ('activo', 'suspendido'):
        return _err('Estado inválido. Usa "activo" o "suspendido"')

    try:
        m = EmpleadoNegocio.query.filter_by(
            id=miembro_id, negocio_id=negocio_id).first()
        if not m: return _err('Miembro no encontrado', 404)
        if m.rol == 'dueno': return _err('No puedes suspender al dueño')

        m.estado = nuevo_estado
        db.session.commit()
        return jsonify({'success': True, 'miembro': m.to_dict()})
    except Exception as e:
        db.session.rollback()
        return _err(str(e), 500)


# ─────────────────────────────────────────────────────────────────────────────
# DELETE /api/negocio/<id>/equipo/<mid>
# ─────────────────────────────────────────────────────────────────────────────
@equipo_bp.route('/negocio/<int:negocio_id>/equipo/<int:miembro_id>', methods=['DELETE'])
def remover_miembro(negocio_id, miembro_id):
    if not _EQUIPO_OK: return _not_avail()
    try:
        m = EmpleadoNegocio.query.filter_by(
            id=miembro_id, negocio_id=negocio_id).first()
        if not m: return _err('Miembro no encontrado', 404)
        if m.rol == 'dueno': return _err('No puedes remover al dueño del negocio')

        db.session.delete(m)
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        return _err(str(e), 500)


# ─────────────────────────────────────────────────────────────────────────────
# GET /api/invitacion/<token>
# Público — el empleado abre este endpoint para ver la invitación
# ─────────────────────────────────────────────────────────────────────────────
@equipo_bp.route('/invitacion/<string:token>', methods=['GET'])
def ver_invitacion(token):
    if not _EQUIPO_OK: return _not_avail()
    try:
        m = EmpleadoNegocio.query.filter_by(token_invitacion=token).first()
        if not m:
            return _err('Invitación no encontrada o ya fue usada', 404)

        if m.token_expira and datetime.now(timezone.utc) > m.token_expira:
            return _err('Esta invitación ha expirado. Pide al dueño que te invite nuevamente.', 410)

        if m.estado == 'activo':
            return _err('Esta invitación ya fue aceptada', 409)

        # Datos del negocio para mostrar al empleado
        nombre_negocio = m.negocio.nombre_negocio if m.negocio else f'Negocio #{m.negocio_id}'
        rol_info = m.rol_info()

        return jsonify({
            'valida': True,
            'email': m.email,
            'nombre_display': m.nombre_display,
            'rol': m.rol,
            'rol_label': rol_info['label'],
            'rol_icon':  rol_info['icon'],
            'negocio_id': m.negocio_id,
            'nombre_negocio': nombre_negocio,
        })
    except Exception as e:
        logger.error(f'Error ver invitación {token}: {e}')
        return _err(str(e), 500)


# ─────────────────────────────────────────────────────────────────────────────
# POST /api/invitacion/<token>/aceptar
# Body: { usuario_id }  (el empleado envía su ID de sesión)
# ─────────────────────────────────────────────────────────────────────────────
@equipo_bp.route('/invitacion/<string:token>/aceptar', methods=['POST'])
def aceptar_invitacion(token):
    if not _EQUIPO_OK: return _not_avail()
    data = request.get_json() or {}
    usuario_id = data.get('usuario_id')

    try:
        m = EmpleadoNegocio.query.filter_by(token_invitacion=token).first()
        if not m:
            return _err('Invitación no encontrada', 404)
        if m.token_expira and datetime.now(timezone.utc) > m.token_expira:
            return _err('Invitación expirada', 410)
        if m.estado == 'activo':
            return _err('Invitación ya aceptada', 409)

        if usuario_id:
            m.usuario_id = usuario_id

        m.estado        = 'activo'
        m.aceptado_en   = datetime.now(timezone.utc)
        m.token_invitacion = None   # invalidar el token una vez usado

        db.session.commit()
        return jsonify({
            'success': True,
            'negocio_id': m.negocio_id,
            'rol': m.rol,
            'miembro': m.to_dict()
        })

    except Exception as e:
        db.session.rollback()
        logger.error(f'Error aceptar invitación {token}: {e}')
        return _err(str(e), 500)


# ─────────────────────────────────────────────────────────────────────────────
# GET /api/usuario/<uid>/negocios-equipo
# Qué negocios tiene acceso este usuario (para el bizContext multi-negocio)
# ─────────────────────────────────────────────────────────────────────────────
@equipo_bp.route('/usuario/<int:usuario_id>/negocios-equipo', methods=['GET'])
def negocios_del_empleado(usuario_id):
    if not _EQUIPO_OK: return _not_avail()
    try:
        memberships = EmpleadoNegocio.query.filter_by(
            usuario_id=usuario_id, estado='activo').all()
        return jsonify([{
            'negocio_id':    m.negocio_id,
            'nombre_negocio': m.negocio.nombre_negocio if m.negocio else '',
            'rol':           m.rol,
            'rol_label':     m.rol_info()['label'],
            'rol_icon':      m.rol_info()['icon'],
        } for m in memberships])
    except Exception as e:
        return _err(str(e), 500)
