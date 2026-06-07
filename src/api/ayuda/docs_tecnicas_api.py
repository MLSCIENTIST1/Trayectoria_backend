"""
Documentación Maestra de la plataforma — API (Fase 1).

Sirve y administra la documentación TÉCNICA (cómo está construida la plataforma)
guardada en `plataforma_kb` con `tipo='tecnico'`. CONFIDENCIAL.

Modelo de acceso (decidido con Carlos):
  - TODO detrás de login (nada público en la web).
  - 3 niveles (`nivel_acceso`): publico | admin | superadmin.
  - `superadmin` = lo más sensible (seguridad/infra/credenciales) → STEP-UP:
    aunque seas admin, hay que re-ingresar usuario+contraseña de un SuperAdmin
    (sesión de desbloqueo corta, ~30 min) para verlo.

url_prefix: /api/admin/docs   (todo requiere permiso 'documentacion')
  POST /unlock {email,password}     → desbloqueo step-up de SuperAdmin
  POST /lock                        → re-bloquear
  GET  /estado                      → ¿desbloqueado? + niveles visibles
  GET  /secciones                   → taxonomía (árbol vacío) para el visor
  GET  /arbol                       → árbol real (áreas → entradas) filtrado por nivel
  GET  /entrada/<clave>             → una entrada (respeta nivel)
  GET  /buscar?q=                   → búsqueda (respeta nivel)
  POST /entrada                     → crear
  PUT  /entrada/<id>                → editar
  DELETE /entrada/<id>              → eliminar

© 2024-2026 Carlos Eduardo Huérfano Bermúdez. Confidencial.
"""
import time
import logging
from flask import Blueprint, jsonify, request, session, g
from sqlalchemy import text
from src.models.database import db
from src.models.colombia_data.plataforma_kb import PlataformaKB
from src.api.admin_api import requiere_permiso, registrar_auditoria, is_admin, get_current_user_email

logger = logging.getLogger(__name__)
docs_tecnicas_bp = Blueprint('docs_tecnicas', __name__, url_prefix='/api/admin/docs')

NIVELES_VALIDOS = ('publico', 'admin', 'superadmin')
UNLOCK_TTL = 1800          # 30 min de desbloqueo step-up
_UNLOCK_KEY = 'docs_superadmin_unlocked_at'

# Taxonomía oficial de secciones (orden + ícono Bootstrap para el visor en árbol)
SECCIONES_DOC = [
    {'area': 'glosario',     'titulo': 'Glosario (para no técnicos)', 'icono': 'bi-book-half', 'orden': 0},
    {'area': 'arquitectura', 'titulo': 'Arquitectura general', 'icono': 'bi-diagram-3-fill', 'orden': 1},
    {'area': 'backend',      'titulo': 'Backend (Flask)',       'icono': 'bi-hdd-stack-fill', 'orden': 2},
    {'area': 'base-datos',   'titulo': 'Base de datos',         'icono': 'bi-database-fill',  'orden': 3},
    {'area': 'frontend',     'titulo': 'Frontend',              'icono': 'bi-window-fullscreen', 'orden': 4},
    {'area': 'auth',         'titulo': 'Autenticación y sesiones', 'icono': 'bi-shield-lock-fill', 'orden': 5},
    {'area': 'panel',        'titulo': 'Panel de administración', 'icono': 'bi-sliders', 'orden': 6},
    {'area': 'gamificacion', 'titulo': 'Gamificación',          'icono': 'bi-trophy-fill', 'orden': 7},
    {'area': 'ecommerce',    'titulo': 'E-commerce y pedidos',  'icono': 'bi-bag-check-fill', 'orden': 8},
    {'area': 'integraciones','titulo': 'Integraciones',         'icono': 'bi-plug-fill', 'orden': 9},
    {'area': 'seguridad',    'titulo': 'Seguridad',             'icono': 'bi-shield-shaded', 'orden': 10},
    {'area': 'despliegue',   'titulo': 'Despliegue / DevOps',   'icono': 'bi-cloud-arrow-up-fill', 'orden': 11},
    {'area': 'operacion',    'titulo': 'Operación',             'icono': 'bi-gear-wide-connected', 'orden': 12},
    {'area': 'ui-map',       'titulo': 'Mapa de UI / botones',  'icono': 'bi-grid-3x3-gap-fill', 'orden': 13},
    {'area': 'negocio',      'titulo': 'Negocio y planes',      'icono': 'bi-cash-coin', 'orden': 14},
    {'area': 'flujos',       'titulo': 'Flujos de datos',       'icono': 'bi-arrow-left-right', 'orden': 15},
    {'area': 'errores',      'titulo': 'Errores y respuestas',  'icono': 'bi-exclamation-triangle-fill', 'orden': 16},
    {'area': 'terceros',     'titulo': 'Servicios de terceros', 'icono': 'bi-box-arrow-up-right', 'orden': 17},
    {'area': 'respaldo',     'titulo': 'Respaldo y recuperación', 'icono': 'bi-cloud-download-fill', 'orden': 18},
    {'area': 'pruebas',      'titulo': 'Pruebas (tests)',       'icono': 'bi-check2-square', 'orden': 19},
    {'area': 'handover',     'titulo': 'Entrega / onboarding',  'icono': 'bi-people-fill', 'orden': 20},
    {'area': 'legal',        'titulo': 'Propiedad y confidencialidad', 'icono': 'bi-c-circle-fill', 'orden': 21},
]
_AREA_ORDEN = {s['area']: s['orden'] for s in SECCIONES_DOC}


# ── Lógica de acceso (pura y testeable) ─────────────────────────────────────
def niveles_visibles(superadmin_unlocked):
    """PURA: niveles de acceso que puede ver un admin con permiso 'documentacion'.
    Con step-up de SuperAdmin vigente, suma 'superadmin'."""
    niveles = ['publico', 'admin']
    if superadmin_unlocked:
        niveles.append('superadmin')
    return niveles


def _unlock_vigente():
    ts = session.get(_UNLOCK_KEY)
    if not ts:
        return False
    try:
        return (time.time() - float(ts)) < UNLOCK_TTL
    except Exception:
        return False


def _niveles():
    return niveles_visibles(_unlock_vigente())


def validar_doc(data, parcial=False):
    """PURA: valida payload de una entrada de documentación técnica."""
    errores = []
    if (not parcial) or ('clave' in data):
        if not str(data.get('clave') or '').strip():
            errores.append('clave requerida')
    if (not parcial) or ('titulo' in data):
        if not str(data.get('titulo') or '').strip():
            errores.append('titulo requerido')
    if (not parcial) or ('area' in data):
        if not str(data.get('area') or '').strip():
            errores.append('area (sección) requerida')
    if 'nivel_acceso' in data and data.get('nivel_acceso') not in NIVELES_VALIDOS:
        errores.append(f"nivel_acceso inválido (válidos: {list(NIVELES_VALIDOS)})")
    return errores


# ── Step-up de SuperAdmin ───────────────────────────────────────────────────
@docs_tecnicas_bp.route('/unlock', methods=['POST'])
@requiere_permiso('documentacion')
def unlock():
    """Re-pide usuario+contraseña de un SuperAdmin para abrir lo crítico."""
    data = request.get_json() or {}
    email = str(data.get('email') or '').strip().lower()
    password = str(data.get('password') or '')
    if not email or not password:
        return jsonify({'success': False, 'error': 'Usuario y contraseña requeridos'}), 400

    # 1) el email debe ser de un SuperAdmin
    es_adm, adm = is_admin(email)
    if not es_adm or (adm or {}).get('rol') != 'superadmin':
        registrar_auditoria('soporte', 'docs_unlock', None, {'ok': False, 'motivo': 'no_superadmin', 'email': email})
        return jsonify({'success': False, 'error': 'Credenciales de SuperAdmin inválidas'}), 403

    # 2) verificar contraseña real (bcrypt) del usuario dueño de ese email
    try:
        from src.models.usuarios import Usuario
        u = Usuario.query.filter_by(correo=email).first()
        ok = bool(u and u.check_password(password))
    except Exception as e:
        logger.error(f"[docs] verificación step-up: {e}")
        ok = False

    if not ok:
        registrar_auditoria('soporte', 'docs_unlock', None, {'ok': False, 'motivo': 'password', 'email': email})
        return jsonify({'success': False, 'error': 'Credenciales de SuperAdmin inválidas'}), 403

    session[_UNLOCK_KEY] = time.time()
    session.modified = True
    registrar_auditoria('soporte', 'docs_unlock', None, {'ok': True, 'email': email})
    return jsonify({'success': True, 'desbloqueado': True, 'ttl': UNLOCK_TTL})


@docs_tecnicas_bp.route('/lock', methods=['POST'])
@requiere_permiso('documentacion')
def lock():
    session.pop(_UNLOCK_KEY, None)
    session.modified = True
    return jsonify({'success': True, 'desbloqueado': False})


@docs_tecnicas_bp.route('/estado', methods=['GET'])
@requiere_permiso('documentacion')
def estado():
    return jsonify({'success': True, 'desbloqueado': _unlock_vigente(), 'niveles': _niveles()})


@docs_tecnicas_bp.route('/secciones', methods=['GET'])
@requiere_permiso('documentacion')
def secciones():
    return jsonify({'success': True, 'secciones': SECCIONES_DOC})


# ── Lectura (filtrada por nivel) ────────────────────────────────────────────
def _row(r, con_contenido=False):
    d = {'id': r.id, 'clave': r.clave, 'titulo': r.titulo, 'area': r.area,
         'resumen': r.resumen, 'orden': r.orden, 'nivel_acceso': r.nivel_acceso or 'publico',
         'datos': r.datos or {}}
    if con_contenido:
        d['contenido'] = r.contenido
    return d


@docs_tecnicas_bp.route('/arbol', methods=['GET'])
@requiere_permiso('documentacion')
def arbol():
    niveles = _niveles()
    filas = (PlataformaKB.query
             .filter(PlataformaKB.tipo == 'tecnico', PlataformaKB.nivel_acceso.in_(niveles))
             .order_by(PlataformaKB.orden, PlataformaKB.titulo).all())
    por_area = {}
    for r in filas:
        por_area.setdefault(r.area or 'otros', []).append(_row(r))
    arbol = []
    secciones = sorted(SECCIONES_DOC, key=lambda s: s['orden'])
    vistos = set()
    for s in secciones:
        vistos.add(s['area'])
        arbol.append({**s, 'entradas': por_area.get(s['area'], [])})
    # áreas fuera de la taxonomía (por si acaso)
    for area, ents in por_area.items():
        if area not in vistos:
            arbol.append({'area': area, 'titulo': area, 'icono': 'bi-file-earmark-text', 'orden': 99, 'entradas': ents})
    return jsonify({'success': True, 'arbol': arbol, 'niveles': niveles, 'desbloqueado': _unlock_vigente()})


@docs_tecnicas_bp.route('/entrada/<clave>', methods=['GET'])
@requiere_permiso('documentacion')
def entrada(clave):
    r = PlataformaKB.query.filter_by(clave=clave, tipo='tecnico').first()
    if not r:
        return jsonify({'success': False, 'error': 'No encontrada'}), 404
    if (r.nivel_acceso or 'publico') not in _niveles():
        # Existe pero requiere step-up
        return jsonify({'success': False, 'error': 'Contenido restringido', 'requiere_unlock': True}), 403
    return jsonify({'success': True, 'entrada': _row(r, con_contenido=True)})


@docs_tecnicas_bp.route('/buscar', methods=['GET'])
@requiere_permiso('documentacion')
def buscar():
    q = (request.args.get('q') or '').strip()
    if len(q) < 2:
        return jsonify({'success': True, 'resultados': []})
    like = f"%{q.lower()}%"
    niveles = _niveles()
    filas = (PlataformaKB.query
             .filter(PlataformaKB.tipo == 'tecnico', PlataformaKB.nivel_acceso.in_(niveles))
             .filter(db.or_(db.func.lower(PlataformaKB.titulo).like(like),
                            db.func.lower(db.func.coalesce(PlataformaKB.resumen, '')).like(like),
                            db.func.lower(db.func.coalesce(PlataformaKB.contenido, '')).like(like)))
             .order_by(PlataformaKB.orden).limit(30).all())
    return jsonify({'success': True, 'resultados': [_row(r) for r in filas]})


# ── CRUD ────────────────────────────────────────────────────────────────────
@docs_tecnicas_bp.route('/entrada', methods=['POST'])
@requiere_permiso('documentacion')
def crear():
    data = request.get_json() or {}
    errores = validar_doc(data)
    if errores:
        return jsonify({'success': False, 'errores': errores}), 400
    if PlataformaKB.query.filter_by(clave=data['clave'].strip()).first():
        return jsonify({'success': False, 'error': 'La clave ya existe'}), 409
    nivel = data.get('nivel_acceso') if data.get('nivel_acceso') in NIVELES_VALIDOS else 'admin'
    try:
        e = PlataformaKB(
            tipo='tecnico', area=data['area'].strip(), clave=data['clave'].strip(),
            titulo=data['titulo'].strip(), resumen=data.get('resumen'), contenido=data.get('contenido'),
            datos=data.get('datos') or {}, orden=int(data.get('orden') or 0),
            publicado=True, nivel_acceso=nivel)
        db.session.add(e); db.session.commit()
        registrar_auditoria('crear', 'doc_tecnica', e.id, {'clave': e.clave, 'nivel': nivel})
        return jsonify({'success': True, 'entrada': _row(e, con_contenido=True)}), 201
    except Exception as ex:
        db.session.rollback()
        logger.error(f"[docs] crear: {ex}")
        return jsonify({'success': False, 'error': str(ex)}), 500


@docs_tecnicas_bp.route('/entrada/<int:eid>', methods=['PUT', 'PATCH'])
@requiere_permiso('documentacion')
def editar(eid):
    e = PlataformaKB.query.filter_by(id=eid, tipo='tecnico').first()
    if not e:
        return jsonify({'success': False, 'error': 'No encontrada'}), 404
    data = request.get_json() or {}
    errores = validar_doc(data, parcial=True)
    if errores:
        return jsonify({'success': False, 'errores': errores}), 400
    try:
        for campo in ('area', 'titulo', 'resumen', 'contenido', 'datos', 'nivel_acceso'):
            if campo in data:
                setattr(e, campo, data[campo])
        if 'orden' in data:
            e.orden = int(data.get('orden') or 0)
        db.session.commit()
        registrar_auditoria('editar', 'doc_tecnica', e.id, {'clave': e.clave})
        return jsonify({'success': True, 'entrada': _row(e, con_contenido=True)})
    except Exception as ex:
        db.session.rollback()
        logger.error(f"[docs] editar: {ex}")
        return jsonify({'success': False, 'error': str(ex)}), 500


@docs_tecnicas_bp.route('/entrada/<int:eid>', methods=['DELETE'])
@requiere_permiso('documentacion')
def eliminar(eid):
    e = PlataformaKB.query.filter_by(id=eid, tipo='tecnico').first()
    if not e:
        return jsonify({'success': False, 'error': 'No encontrada'}), 404
    clave = e.clave
    try:
        db.session.delete(e); db.session.commit()
        registrar_auditoria('eliminar', 'doc_tecnica', eid, {'clave': clave})
        return jsonify({'success': True})
    except Exception as ex:
        db.session.rollback()
        logger.error(f"[docs] eliminar: {ex}")
        return jsonify({'success': False, 'error': str(ex)}), 500
