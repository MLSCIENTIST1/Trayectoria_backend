# ═══════════════════════════════════════════════════════════════════════════════
# TUKOMERCIO — Equipo API v2.0 (Links por Rol)
# ═══════════════════════════════════════════════════════════════════════════════
#
# Endpoints del tendero (autenticados):
#   GET  /api/negocio/<id>/equipo/links               → los 3 links del negocio
#   POST /api/negocio/<id>/equipo/links/<rol>/regenerar → nuevo token
#   PUT  /api/negocio/<id>/equipo/links/<rol>/toggle   → activar/desactivar link
#   GET  /api/negocio/<id>/equipo                      → listar miembros
#   PUT  /api/negocio/<id>/equipo/<mid>/estado         → activar/suspender miembro
#   PUT  /api/negocio/<id>/equipo/<mid>/rol            → cambiar rol
#   DELETE /api/negocio/<id>/equipo/<mid>              → remover miembro
#
# Endpoints públicos (empleado):
#   GET  /api/invitacion/<token>          → info del link (negocio, rol)
#   POST /api/invitacion/<token>/unirse   → unirse {nombre, email?, usuario_id?}
#
# ═══════════════════════════════════════════════════════════════════════════════

import logging
from flask import Blueprint, request, jsonify
from src.models.database import db

logger = logging.getLogger(__name__)
equipo_bp = Blueprint('equipo_bp', __name__)

# ─── Imports defensivos ───────────────────────────────────────────────────────
try:
    from src.models.colombia_data.equipo import (
        LinkInvitacion, EmpleadoNegocio, ROLES, ROLES_INVITABLES
    )
    _OK = True
except ImportError as e:
    LinkInvitacion = EmpleadoNegocio = None; ROLES = {}; ROLES_INVITABLES = []
    _OK = False
    logger.error(f'❌ Equipo models no disponibles: {e}')


def _err(msg, code=400): return jsonify({'error': msg}), code
def _nav(): return _err('Módulo de equipo no disponible', 503)


# ══════════════════════════════════════════════════════════════════════════════
# LINKS — panel del tendero
# ══════════════════════════════════════════════════════════════════════════════

@equipo_bp.route('/negocio/<int:negocio_id>/equipo/links', methods=['GET'])
def get_links(negocio_id):
    """Devuelve (o crea) los 3 links de invitación del negocio."""
    if not _OK: return _nav()
    try:
        links = []
        for rol in ROLES_INVITABLES:
            link = LinkInvitacion.get_or_create(negocio_id, rol)
            links.append(link.to_dict())
        db.session.commit()
        return jsonify(links)
    except Exception as e:
        db.session.rollback()
        logger.error(f'Error get_links negocio {negocio_id}: {e}')
        return _err(str(e), 500)


@equipo_bp.route('/negocio/<int:negocio_id>/equipo/links/<string:rol>/regenerar', methods=['POST'])
def regenerar_link(negocio_id, rol):
    """Genera un nuevo token para el rol — invalida el anterior."""
    if not _OK: return _nav()
    if rol not in ROLES_INVITABLES:
        return _err(f'Rol inválido: {rol}')
    try:
        link = LinkInvitacion.get_or_create(negocio_id, rol)
        link.regenerar()
        db.session.commit()
        return jsonify({'success': True, 'link': link.to_dict()})
    except Exception as e:
        db.session.rollback()
        return _err(str(e), 500)


@equipo_bp.route('/negocio/<int:negocio_id>/equipo/links/<string:rol>/toggle', methods=['PUT'])
def toggle_link(negocio_id, rol):
    """Activa o desactiva un link (sin borrar el token)."""
    if not _OK: return _nav()
    if rol not in ROLES_INVITABLES:
        return _err(f'Rol inválido: {rol}')
    try:
        link = LinkInvitacion.get_or_create(negocio_id, rol)
        link.activo = not link.activo
        db.session.commit()
        return jsonify({'success': True, 'link': link.to_dict()})
    except Exception as e:
        db.session.rollback()
        return _err(str(e), 500)


# ══════════════════════════════════════════════════════════════════════════════
# MIEMBROS — panel del tendero
# ══════════════════════════════════════════════════════════════════════════════

@equipo_bp.route('/negocio/<int:negocio_id>/equipo', methods=['GET'])
def listar_equipo(negocio_id):
    if not _OK: return _nav()
    try:
        miembros = EmpleadoNegocio.query.filter_by(negocio_id=negocio_id)\
            .order_by(EmpleadoNegocio.unido_en).all()
        return jsonify([m.to_dict() for m in miembros])
    except Exception as e:
        return _err(str(e), 500)


@equipo_bp.route('/negocio/<int:negocio_id>/equipo/<int:mid>/estado', methods=['PUT'])
def cambiar_estado(negocio_id, mid):
    if not _OK: return _nav()
    data = request.get_json() or {}
    nuevo = (data.get('estado') or '').strip()
    if nuevo not in ('activo', 'suspendido'):
        return _err('Estado inválido. Usa "activo" o "suspendido"')
    try:
        m = EmpleadoNegocio.query.filter_by(id=mid, negocio_id=negocio_id).first()
        if not m: return _err('Miembro no encontrado', 404)
        if m.rol == 'dueno': return _err('No puedes suspender al dueño')
        m.estado = nuevo
        db.session.commit()
        return jsonify({'success': True, 'miembro': m.to_dict()})
    except Exception as e:
        db.session.rollback()
        return _err(str(e), 500)


@equipo_bp.route('/negocio/<int:negocio_id>/equipo/<int:mid>/rol', methods=['PUT'])
def cambiar_rol(negocio_id, mid):
    if not _OK: return _nav()
    data = request.get_json() or {}
    nuevo_rol = (data.get('rol') or '').strip()
    if nuevo_rol not in ROLES or nuevo_rol == 'dueno':
        return _err(f'Rol inválido: {nuevo_rol}')
    try:
        m = EmpleadoNegocio.query.filter_by(id=mid, negocio_id=negocio_id).first()
        if not m: return _err('Miembro no encontrado', 404)
        if m.rol == 'dueno': return _err('No puedes cambiar el rol del dueño')
        m.rol = nuevo_rol
        db.session.commit()
        return jsonify({'success': True, 'miembro': m.to_dict()})
    except Exception as e:
        db.session.rollback()
        return _err(str(e), 500)


@equipo_bp.route('/negocio/<int:negocio_id>/equipo/<int:mid>', methods=['DELETE'])
def remover_miembro(negocio_id, mid):
    if not _OK: return _nav()
    try:
        m = EmpleadoNegocio.query.filter_by(id=mid, negocio_id=negocio_id).first()
        if not m: return _err('Miembro no encontrado', 404)
        if m.rol == 'dueno': return _err('No puedes remover al dueño')
        db.session.delete(m)
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        return _err(str(e), 500)


# ══════════════════════════════════════════════════════════════════════════════
# INVITACIÓN — endpoints públicos (el empleado los usa)
# ══════════════════════════════════════════════════════════════════════════════

@equipo_bp.route('/invitacion/<string:token>', methods=['GET'])
def ver_invitacion(token):
    """El empleado verifica el link antes de unirse."""
    if not _OK: return _nav()
    try:
        link = LinkInvitacion.query.filter_by(token=token).first()
        if not link:
            return _err('Link de invitación no encontrado o inválido', 404)
        if not link.activo:
            return _err('Este link de invitación está desactivado. Contacta al dueño del negocio.', 410)

        nombre_negocio = link.negocio.nombre_negocio if link.negocio else f'Negocio #{link.negocio_id}'
        info = link.rol_info()

        return jsonify({
            'valida':         True,
            'negocio_id':     link.negocio_id,
            'nombre_negocio': nombre_negocio,
            'rol':            link.rol,
            'rol_label':      info['label'],
            'rol_icon':       info['icon'],
            'rol_color':      info['color'],
            'rol_desc':       info['desc'],
        })
    except Exception as e:
        logger.error(f'Error ver_invitacion {token}: {e}')
        return _err(str(e), 500)


@equipo_bp.route('/invitacion/<string:token>/unirse', methods=['POST'])
def unirse(token):
    """
    El empleado acepta la invitación.
    Body: { nombre, email? (opcional), usuario_id? (si tiene cuenta) }
    """
    if not _OK: return _nav()
    data = request.get_json() or {}
    nombre     = (data.get('nombre') or '').strip()
    email      = (data.get('email')  or '').strip().lower() or None
    usuario_id = data.get('usuario_id')

    if not nombre:
        return _err('Por favor escribe tu nombre para unirte')

    try:
        link = LinkInvitacion.query.filter_by(token=token).first()
        if not link:
            return _err('Link de invitación no válido', 404)
        if not link.activo:
            return _err('Este link está desactivado. Pide al dueño que lo reactive.', 410)

        # Crear miembro
        miembro = EmpleadoNegocio(
            negocio_id = link.negocio_id,
            usuario_id = int(usuario_id) if usuario_id else None,
            link_id    = link.id,
            nombre     = nombre,
            email      = email,
            rol        = link.rol,
            estado     = 'activo',
        )
        db.session.add(miembro)

        # Incrementar usos del link
        link.usos += 1

        db.session.commit()

        return jsonify({
            'success':    True,
            'negocio_id': link.negocio_id,
            'rol':        link.rol,
            'miembro':    miembro.to_dict(),
        }), 201

    except Exception as e:
        db.session.rollback()
        logger.error(f'Error unirse {token}: {e}')
        return _err(str(e), 500)


# ── Extra: qué negocios tiene este usuario como miembro del equipo ────────────
@equipo_bp.route('/usuario/<int:usuario_id>/negocios-equipo', methods=['GET'])
def negocios_del_empleado(usuario_id):
    if not _OK: return _nav()
    try:
        ms = EmpleadoNegocio.query.filter_by(usuario_id=usuario_id, estado='activo').all()
        return jsonify([{
            'negocio_id':    m.negocio_id,
            'nombre_negocio': m.negocio.nombre_negocio if m.negocio else '',
            'rol':           m.rol,
            'rol_label':     m.rol_info()['label'],
            'rol_icon':      m.rol_info()['icon'],
        } for m in ms])
    except Exception as e:
        return _err(str(e), 500)
