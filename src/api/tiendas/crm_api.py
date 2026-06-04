# ═══════════════════════════════════════════════════════════════════════════════
# TUKOMERCIO — CRM Básico de Compradores v1.0
# ═══════════════════════════════════════════════════════════════════════════════
#
# Endpoints (todos requieren negocio_id):
#   GET /api/negocio/<id>/crm/resumen       → totales rápidos
#   GET /api/negocio/<id>/crm/compradores   → lista paginada (?q=, ?page=)
#   GET /api/negocio/<id>/crm/comprador/<cid>/pedidos → historial de pedidos
#
# Maneja dos tipos de clientes:
#   • Registrados  — tienen comprador_id en el pedido → join con tabla compradores
#   • Invitados    — comprador_id NULL → usa snapshot datos_comprador del pedido
#
# ═══════════════════════════════════════════════════════════════════════════════

import logging
from flask import Blueprint, request, jsonify
from sqlalchemy import func, text

logger = logging.getLogger(__name__)
crm_bp = Blueprint('crm_bp', __name__)

# ─── Imports defensivos ───────────────────────────────────────────────────────
try:
    from src.models.database import db
    from src.models.compradores.comprador import Comprador
    from src.models.compradores.pedido import Pedido
    _OK = True
except ImportError as e:
    Comprador = Pedido = db = None
    _OK = False
    logger.error(f'❌ CRM models no disponibles: {e}')


def _err(msg, code=400): return jsonify({'error': msg}), code
def _nav(): return _err('Módulo CRM no disponible', 503)


# ══════════════════════════════════════════════════════════════════════════════
# RESUMEN RÁPIDO
# ══════════════════════════════════════════════════════════════════════════════

@crm_bp.route('/negocio/<int:negocio_id>/crm/resumen', methods=['GET'])
def resumen_crm(negocio_id):
    """Totales generales del CRM para las cards del encabezado."""
    if not _OK: return _nav()
    try:
        stats = db.session.query(
            func.count(Pedido.id_pedido).label('total_pedidos'),
            func.sum(Pedido.total).label('total_facturado'),
            func.count(func.distinct(Pedido.comprador_id)).label('compradores_registrados'),
        ).filter(Pedido.negocio_id == negocio_id).one()

        # Pedidos sin cuenta (guests)
        guests = db.session.query(func.count(Pedido.id_pedido))\
            .filter(Pedido.negocio_id == negocio_id, Pedido.comprador_id.is_(None))\
            .scalar() or 0

        # Compradores únicos estimados (registrados + grupos de invitados por teléfono)
        total_estimado = (stats.compradores_registrados or 0) + guests

        return jsonify({
            'total_pedidos':       stats.total_pedidos or 0,
            'total_facturado':     float(stats.total_facturado or 0),
            'clientes_registrados': stats.compradores_registrados or 0,
            'pedidos_invitados':   guests,
            'total_clientes_est':  total_estimado,
        })
    except Exception as e:
        logger.error(f'Error resumen_crm negocio {negocio_id}: {e}')
        return _err(str(e), 500)


# ══════════════════════════════════════════════════════════════════════════════
# LISTA DE COMPRADORES
# ══════════════════════════════════════════════════════════════════════════════

@crm_bp.route('/negocio/<int:negocio_id>/crm/compradores', methods=['GET'])
def listar_compradores(negocio_id):
    """
    Lista compradores que han pedido en este negocio.
    ?q=<texto>   → filtra por nombre, teléfono o correo
    ?page=1      → paginación (20 por página)
    ?tipo=todos|registrados|invitados
    """
    if not _OK: return _nav()

    q    = request.args.get('q', '').strip().lower()
    page = max(1, int(request.args.get('page', 1)))
    tipo = request.args.get('tipo', 'todos')   # todos | registrados | invitados
    PER  = 20

    try:
        clientes = []

        # ── 1. COMPRADORES REGISTRADOS ─────────────────────────────────────────
        if tipo in ('todos', 'registrados'):
            base = db.session.query(
                Comprador.id_comprador,
                Comprador.nombre,
                Comprador.apellidos,
                Comprador.correo,
                Comprador.telefono,
                func.count(Pedido.id_pedido).label('num_pedidos'),
                func.sum(Pedido.total).label('total_gastado'),
                func.max(Pedido.fecha_pedido).label('ultimo_pedido'),
            ).join(Pedido, Pedido.comprador_id == Comprador.id_comprador)\
             .filter(Pedido.negocio_id == negocio_id)

            if q:
                base = base.filter(
                    db.or_(
                        func.lower(Comprador.nombre).contains(q),
                        func.lower(Comprador.apellidos).contains(q),
                        Comprador.telefono.contains(q),
                        func.lower(Comprador.correo).contains(q),
                    )
                )

            rows = base.group_by(
                Comprador.id_comprador,
                Comprador.nombre,
                Comprador.apellidos,
                Comprador.correo,
                Comprador.telefono,
            ).order_by(func.max(Pedido.fecha_pedido).desc()).all()

            for r in rows:
                nombre = f"{r.nombre or ''} {r.apellidos or ''}".strip()
                clientes.append({
                    'tipo':          'registrado',
                    'comprador_id':  r.id_comprador,
                    'nombre':        nombre,
                    'telefono':      r.telefono or '',
                    'correo':        r.correo or '',
                    'num_pedidos':   r.num_pedidos or 0,
                    'total_gastado': float(r.total_gastado or 0),
                    'ultimo_pedido': r.ultimo_pedido.isoformat() if r.ultimo_pedido else None,
                })

        # ── 2. INVITADOS (sin cuenta, comprador_id NULL) ───────────────────────
        if tipo in ('todos', 'invitados'):
            invitados_raw = Pedido.query.filter(
                Pedido.negocio_id == negocio_id,
                Pedido.comprador_id.is_(None),
            ).order_by(Pedido.fecha_pedido.desc()).all()

            # Agrupar por teléfono (snapshot datos_comprador)
            grupos: dict = {}
            for p in invitados_raw:
                dc      = p.datos_comprador or {}
                tel     = dc.get('telefono', '').strip()
                nombre  = dc.get('nombre', 'Invitado').strip()
                correo  = dc.get('correo') or dc.get('email') or ''
                key     = tel or nombre   # agrupar por tel; si no hay, por nombre

                if q:
                    haystack = f"{nombre} {tel} {correo}".lower()
                    if q not in haystack:
                        continue

                if key not in grupos:
                    grupos[key] = {
                        'tipo':          'invitado',
                        'comprador_id':  None,
                        'telefono_key':  key,
                        'nombre':        nombre,
                        'telefono':      tel,
                        'correo':        correo,
                        'num_pedidos':   0,
                        'total_gastado': 0.0,
                        'ultimo_pedido': None,
                    }
                g = grupos[key]
                g['num_pedidos']   += 1
                g['total_gastado'] += float(p.total or 0)
                fp = p.fecha_pedido.isoformat() if p.fecha_pedido else None
                if not g['ultimo_pedido'] or (fp and fp > g['ultimo_pedido']):
                    g['ultimo_pedido'] = fp

            clientes.extend(grupos.values())

        # ── Ordenar todo por último pedido desc ────────────────────────────────
        clientes.sort(key=lambda c: c.get('ultimo_pedido') or '', reverse=True)

        # ── Paginación ─────────────────────────────────────────────────────────
        total   = len(clientes)
        inicio  = (page - 1) * PER
        pagina  = clientes[inicio: inicio + PER]

        return jsonify({
            'clientes':    pagina,
            'total':       total,
            'page':        page,
            'per_page':    PER,
            'total_pages': max(1, (total + PER - 1) // PER),
        })

    except Exception as e:
        logger.error(f'Error listar_compradores negocio {negocio_id}: {e}')
        return _err(str(e), 500)


# ══════════════════════════════════════════════════════════════════════════════
# HISTORIAL DE PEDIDOS DE UN COMPRADOR REGISTRADO
# ══════════════════════════════════════════════════════════════════════════════

@crm_bp.route('/negocio/<int:negocio_id>/crm/comprador/<int:comprador_id>/pedidos', methods=['GET'])
def pedidos_del_comprador(negocio_id, comprador_id):
    """Todos los pedidos de un comprador registrado en este negocio."""
    if not _OK: return _nav()
    try:
        comprador = Comprador.query.get(comprador_id)
        if not comprador:
            return _err('Comprador no encontrado', 404)

        pedidos = Pedido.query.filter_by(
            negocio_id=negocio_id,
            comprador_id=comprador_id,
        ).order_by(Pedido.fecha_pedido.desc()).all()

        return jsonify({
            'comprador': comprador.to_dict(),
            'pedidos':   [p.to_dict_lista() for p in pedidos],
            'total':     len(pedidos),
            'gastado':   float(sum(p.total or 0 for p in pedidos)),
        })
    except Exception as e:
        logger.error(f'Error pedidos_del_comprador {comprador_id}: {e}')
        return _err(str(e), 500)


# ══════════════════════════════════════════════════════════════════════════════
# HISTORIAL DE UN INVITADO (por teléfono)
# ══════════════════════════════════════════════════════════════════════════════

@crm_bp.route('/negocio/<int:negocio_id>/crm/invitado/pedidos', methods=['GET'])
def pedidos_del_invitado(negocio_id):
    """
    Pedidos de un invitado filtrados por teléfono (snapshot).
    ?telefono=3001234567
    """
    if not _OK: return _nav()
    tel = (request.args.get('telefono') or '').strip()
    if not tel:
        return _err('Se requiere el parámetro ?telefono=')
    try:
        # Buscar en el JSONB datos_comprador→telefono
        pedidos = Pedido.query.filter(
            Pedido.negocio_id == negocio_id,
            Pedido.comprador_id.is_(None),
            Pedido.datos_comprador['telefono'].astext == tel,
        ).order_by(Pedido.fecha_pedido.desc()).all()

        if not pedidos:
            return _err('No se encontraron pedidos para ese teléfono', 404)

        dc = pedidos[0].datos_comprador or {}
        return jsonify({
            'comprador': {
                'tipo':     'invitado',
                'nombre':   dc.get('nombre', 'Invitado'),
                'telefono': tel,
                'correo':   dc.get('correo') or dc.get('email') or '',
            },
            'pedidos': [p.to_dict_lista() for p in pedidos],
            'total':   len(pedidos),
            'gastado': float(sum(p.total or 0 for p in pedidos)),
        })
    except Exception as e:
        logger.error(f'Error pedidos_del_invitado {negocio_id} tel={tel}: {e}')
        return _err(str(e), 500)


# ═══ A-SEC-2: tenant isolation (CRM = PII, todo privado) ═══
from src.api.utils.seguridad import crear_guard_tenant as _guard_tenant
crm_bp.before_request(_guard_tenant(publicos=set()))
