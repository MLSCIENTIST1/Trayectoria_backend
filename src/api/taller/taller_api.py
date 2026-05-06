"""
TuKomercio — API Vertical Taller v1.0
Endpoints para gestión de talleres automotrices y de motos.

Prefijo: /api/taller
Autenticación: @login_required (Flask-Login)

Endpoints:
  GET    /taller/ordenes              — listar OTs del negocio
  POST   /taller/ordenes              — crear OT
  GET    /taller/ordenes/<id>         — detalle OT
  PUT    /taller/ordenes/<id>         — actualizar OT (estado, datos, items)
  DELETE /taller/ordenes/<id>         — eliminar OT (solo recibido/cancelado)
  GET    /taller/ordenes/<id>/pdf     — datos para imprimir OT (HTML print)
  POST   /taller/ordenes/<id>/items   — agregar ítem a OT
  DELETE /taller/ordenes/<id>/items/<iid> — eliminar ítem de OT

  GET    /taller/citas                — listar citas del negocio
  POST   /taller/citas                — crear cita
  PUT    /taller/citas/<id>           — actualizar cita (estado, datos)
  POST   /taller/citas/<id>/convertir — convertir cita en OT

  GET    /taller/stats                — resumen rápido (OTs activas, citas hoy, ingresos mes)
  GET    /taller/historial/<placa>    — historial de OTs por placa
"""

import logging
from datetime import datetime, date, timedelta
from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user

from src.models.database import db
from src.models.taller.orden_trabajo import OrdenTrabajo, ItemOrdenTrabajo, CitaTaller
from src.models.colombia_data.contabilidad.operaciones_y_catalogo import ProductoCatalogo

logger = logging.getLogger(__name__)

taller_bp = Blueprint('taller_bp', __name__)


# ══════════════════════════════════════════════════════════════
# HELPERS
# ══════════════════════════════════════════════════════════════

def _get_negocio_id():
    """Obtiene negocio_id desde query param, header o body."""
    nid = (
        request.args.get('negocio_id')
        or request.headers.get('X-Business-ID')
        or (request.get_json(silent=True) or {}).get('negocio_id')
    )
    return int(nid) if nid else None


def _validar_negocio(negocio_id: int):
    """Verifica que el negocio pertenece al usuario actual."""
    from src.models.colombia_data.negocio import Negocio
    n = Negocio.query.get(negocio_id)
    if not n:
        return False, jsonify({'error': 'Negocio no encontrado'}), 404
    if n.usuario_id != current_user.id_usuario:
        return False, jsonify({'error': 'Sin permiso'}), 403
    return True, n, 200


def _parse_fecha(s: str):
    """Parsea string ISO o datetime."""
    if not s:
        return None
    try:
        return datetime.fromisoformat(s.replace('Z', '+00:00'))
    except Exception:
        return None


# ══════════════════════════════════════════════════════════════
# ÓRDENES DE TRABAJO
# ══════════════════════════════════════════════════════════════

@taller_bp.route('/taller/ordenes', methods=['GET', 'OPTIONS'])
@login_required
def listar_ordenes():
    """GET /api/taller/ordenes — Lista OTs del negocio con filtros opcionales."""
    if request.method == 'OPTIONS':
        return jsonify({}), 200

    negocio_id = _get_negocio_id()
    if not negocio_id:
        return jsonify({'error': 'negocio_id requerido'}), 400

    ok, resultado, code = _validar_negocio(negocio_id)
    if not ok:
        return resultado, code

    q = OrdenTrabajo.query.filter_by(negocio_id=negocio_id)

    # Filtros
    estado = request.args.get('estado')
    if estado:
        q = q.filter(OrdenTrabajo.estado == estado)

    placa = request.args.get('placa', '').strip().upper()
    if placa:
        q = q.filter(OrdenTrabajo.placa.ilike(f'%{placa}%'))

    cliente = request.args.get('cliente', '').strip()
    if cliente:
        q = q.filter(OrdenTrabajo.cliente_nombre.ilike(f'%{cliente}%'))

    desde = request.args.get('desde')
    hasta = request.args.get('hasta')
    if desde:
        q = q.filter(OrdenTrabajo.fecha_ingreso >= _parse_fecha(desde))
    if hasta:
        q = q.filter(OrdenTrabajo.fecha_ingreso <= _parse_fecha(hasta))

    q = q.order_by(OrdenTrabajo.fecha_ingreso.desc())

    # Paginación
    page  = int(request.args.get('page', 1))
    limit = int(request.args.get('limit', 20))
    total = q.count()
    ots   = q.offset((page - 1) * limit).limit(limit).all()

    return jsonify({
        'ordenes': [o.to_dict() for o in ots],
        'total':   total,
        'page':    page,
        'pages':   (total + limit - 1) // limit,
    })


@taller_bp.route('/taller/ordenes', methods=['POST'])
@login_required
def crear_orden():
    """POST /api/taller/ordenes — Crea una nueva OT."""
    data = request.get_json(silent=True) or {}
    negocio_id = data.get('negocio_id') or _get_negocio_id()
    if not negocio_id:
        return jsonify({'error': 'negocio_id requerido'}), 400

    ok, resultado, code = _validar_negocio(negocio_id)
    if not ok:
        return resultado, code

    cliente_nombre = (data.get('cliente_nombre') or '').strip()
    if not cliente_nombre:
        return jsonify({'error': 'cliente_nombre requerido'}), 400

    try:
        ot = OrdenTrabajo(
            negocio_id=negocio_id,
            cliente_nombre=cliente_nombre,
            placa               = data.get('placa'),
            marca               = data.get('marca'),
            modelo              = data.get('modelo'),
            anio                = data.get('anio'),
            kilometraje         = data.get('kilometraje'),
            color               = data.get('color'),
            tipo_vehiculo       = data.get('tipo_vehiculo', 'carro'),
            cliente_telefono    = data.get('cliente_telefono'),
            cliente_email       = data.get('cliente_email'),
            problema_reportado  = data.get('problema_reportado'),
            diagnostico         = data.get('diagnostico'),
            observaciones       = data.get('observaciones'),
            estado              = data.get('estado', 'recibido'),
            metodo_pago         = data.get('metodo_pago'),
            descuento           = data.get('descuento', 0),
            fecha_entrega_estimada = _parse_fecha(data.get('fecha_entrega_estimada')),
        )
        db.session.add(ot)
        db.session.flush()  # obtener ot.id antes de agregar items

        # Items iniciales opcionales
        for item_data in data.get('items', []):
            _agregar_item_a_ot(ot, item_data)

        ot.recalcular_totales()
        db.session.commit()
        logger.info(f"✅ OT creada: {ot.numero_ot} (negocio {negocio_id})")
        return jsonify({'ok': True, 'orden': ot.to_dict()}), 201

    except Exception as e:
        db.session.rollback()
        logger.error(f"❌ Error creando OT: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500


@taller_bp.route('/taller/ordenes/<int:ot_id>', methods=['GET', 'OPTIONS'])
@login_required
def detalle_orden(ot_id):
    """GET /api/taller/ordenes/<id> — Detalle completo de una OT."""
    if request.method == 'OPTIONS':
        return jsonify({}), 200

    ot = OrdenTrabajo.query.get_or_404(ot_id)
    ok, resultado, code = _validar_negocio(ot.negocio_id)
    if not ok:
        return resultado, code

    return jsonify(ot.to_dict())


@taller_bp.route('/taller/ordenes/<int:ot_id>', methods=['PUT', 'OPTIONS'])
@login_required
def actualizar_orden(ot_id):
    """PUT /api/taller/ordenes/<id> — Actualiza datos y/o estado de una OT."""
    if request.method == 'OPTIONS':
        return jsonify({}), 200

    ot = OrdenTrabajo.query.get_or_404(ot_id)
    ok, resultado, code = _validar_negocio(ot.negocio_id)
    if not ok:
        return resultado, code

    data = request.get_json(silent=True) or {}

    try:
        # Campos editables
        campos = [
            'placa', 'marca', 'modelo', 'anio', 'kilometraje', 'color',
            'tipo_vehiculo', 'cliente_nombre', 'cliente_telefono', 'cliente_email',
            'problema_reportado', 'diagnostico', 'observaciones',
            'metodo_pago', 'descuento',
        ]
        for campo in campos:
            if campo in data:
                val = data[campo]
                if campo == 'placa' and val:
                    val = val.strip().upper()
                setattr(ot, campo, val)

        # Estado con reglas
        if 'estado' in data:
            nuevo_estado = data['estado']
            if nuevo_estado in OrdenTrabajo.ESTADOS:
                ot.estado = nuevo_estado
                if nuevo_estado == 'entregado' and not ot.fecha_entrega_real:
                    ot.fecha_entrega_real = datetime.utcnow()

        if 'estado_pago' in data and data['estado_pago'] in OrdenTrabajo.ESTADOS_PAGO:
            ot.estado_pago = data['estado_pago']

        if 'fecha_entrega_estimada' in data:
            ot.fecha_entrega_estimada = _parse_fecha(data['fecha_entrega_estimada'])

        ot.recalcular_totales()
        db.session.commit()
        return jsonify({'ok': True, 'orden': ot.to_dict()})

    except Exception as e:
        db.session.rollback()
        logger.error(f"❌ Error actualizando OT {ot_id}: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500


@taller_bp.route('/taller/ordenes/<int:ot_id>', methods=['DELETE'])
@login_required
def eliminar_orden(ot_id):
    """DELETE /api/taller/ordenes/<id> — Elimina OT (solo si está en recibido o cancelado)."""
    ot = OrdenTrabajo.query.get_or_404(ot_id)
    ok, resultado, code = _validar_negocio(ot.negocio_id)
    if not ok:
        return resultado, code

    if ot.estado not in ('recibido', 'cancelado'):
        return jsonify({'error': 'Solo se pueden eliminar OTs en estado recibido o cancelado'}), 400

    try:
        db.session.delete(ot)
        db.session.commit()
        return jsonify({'ok': True, 'mensaje': f'OT {ot.numero_ot} eliminada'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


# ── Items de OT ───────────────────────────────────────────────

def _agregar_item_a_ot(ot: OrdenTrabajo, data: dict):
    """Helper interno: crea un ItemOrdenTrabajo y lo agrega a la OT."""
    tipo        = data.get('tipo', 'servicio')
    descripcion = (data.get('descripcion') or '').strip()
    if not descripcion:
        return None
    cantidad        = float(data.get('cantidad', 1))
    precio_unitario = float(data.get('precio_unitario', 0))
    producto_id     = data.get('producto_id')

    item = ItemOrdenTrabajo(
        orden_id        = ot.id,
        tipo            = tipo,
        descripcion     = descripcion,
        cantidad        = cantidad,
        precio_unitario = precio_unitario,
        producto_id     = producto_id,
    )
    db.session.add(item)
    return item


@taller_bp.route('/taller/ordenes/<int:ot_id>/items', methods=['POST', 'OPTIONS'])
@login_required
def agregar_item(ot_id):
    """POST /api/taller/ordenes/<id>/items — Agrega un ítem a la OT."""
    if request.method == 'OPTIONS':
        return jsonify({}), 200

    ot = OrdenTrabajo.query.get_or_404(ot_id)
    ok, resultado, code = _validar_negocio(ot.negocio_id)
    if not ok:
        return resultado, code

    data = request.get_json(silent=True) or {}
    try:
        item = _agregar_item_a_ot(ot, data)
        if not item:
            return jsonify({'error': 'descripcion requerida'}), 400
        db.session.flush()
        ot.recalcular_totales()
        db.session.commit()
        return jsonify({'ok': True, 'item': item.to_dict(), 'orden': ot.to_dict()}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@taller_bp.route('/taller/ordenes/<int:ot_id>/items/<int:item_id>', methods=['DELETE'])
@login_required
def eliminar_item(ot_id, item_id):
    """DELETE /api/taller/ordenes/<ot_id>/items/<item_id>"""
    ot   = OrdenTrabajo.query.get_or_404(ot_id)
    ok, resultado, code = _validar_negocio(ot.negocio_id)
    if not ok:
        return resultado, code

    item = ItemOrdenTrabajo.query.filter_by(id=item_id, orden_id=ot_id).first_or_404()
    try:
        db.session.delete(item)
        db.session.flush()
        ot.recalcular_totales()
        db.session.commit()
        return jsonify({'ok': True, 'orden': ot.to_dict()})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@taller_bp.route('/taller/ordenes/<int:ot_id>/pdf', methods=['GET', 'OPTIONS'])
@login_required
def pdf_orden(ot_id):
    """
    GET /api/taller/ordenes/<id>/pdf
    Devuelve los datos completos de la OT para que el frontend
    genere el HTML de impresión (window.print()).
    """
    if request.method == 'OPTIONS':
        return jsonify({}), 200

    ot = OrdenTrabajo.query.get_or_404(ot_id)
    ok, resultado, code = _validar_negocio(ot.negocio_id)
    if not ok:
        return resultado, code

    from src.models.colombia_data.negocio import Negocio
    negocio = Negocio.query.get(ot.negocio_id)

    return jsonify({
        'orden':   ot.to_dict(),
        'negocio': {
            'nombre':    negocio.nombre_negocio if negocio else '',
            'telefono':  negocio.telefono        if negocio else '',
            'direccion': negocio.direccion        if negocio else '',
            'logo_url':  negocio.logo_url         if negocio else '',
            'whatsapp':  negocio.whatsapp         if negocio else '',
        },
        'generado': datetime.utcnow().isoformat(),
    })


# ══════════════════════════════════════════════════════════════
# CITAS
# ══════════════════════════════════════════════════════════════

@taller_bp.route('/taller/citas', methods=['GET', 'OPTIONS'])
@login_required
def listar_citas():
    """GET /api/taller/citas — Lista citas del negocio."""
    if request.method == 'OPTIONS':
        return jsonify({}), 200

    negocio_id = _get_negocio_id()
    if not negocio_id:
        return jsonify({'error': 'negocio_id requerido'}), 400

    ok, resultado, code = _validar_negocio(negocio_id)
    if not ok:
        return resultado, code

    q = CitaTaller.query.filter_by(negocio_id=negocio_id)

    estado = request.args.get('estado')
    if estado:
        q = q.filter(CitaTaller.estado == estado)

    # Por defecto: citas de los próximos 30 días
    desde = _parse_fecha(request.args.get('desde')) or datetime.utcnow() - timedelta(days=1)
    hasta = _parse_fecha(request.args.get('hasta')) or datetime.utcnow() + timedelta(days=30)
    q = q.filter(CitaTaller.fecha_cita >= desde, CitaTaller.fecha_cita <= hasta)

    q = q.order_by(CitaTaller.fecha_cita.asc())
    citas = q.all()

    return jsonify({'citas': [c.to_dict() for c in citas], 'total': len(citas)})


@taller_bp.route('/taller/citas', methods=['POST'])
@login_required
def crear_cita():
    """POST /api/taller/citas — Crea una nueva cita."""
    data = request.get_json(silent=True) or {}
    negocio_id = data.get('negocio_id') or _get_negocio_id()
    if not negocio_id:
        return jsonify({'error': 'negocio_id requerido'}), 400

    ok, resultado, code = _validar_negocio(negocio_id)
    if not ok:
        return resultado, code

    cliente_nombre = (data.get('cliente_nombre') or '').strip()
    fecha_cita_str = data.get('fecha_cita')
    if not cliente_nombre or not fecha_cita_str:
        return jsonify({'error': 'cliente_nombre y fecha_cita requeridos'}), 400

    fecha_cita = _parse_fecha(fecha_cita_str)
    if not fecha_cita:
        return jsonify({'error': 'fecha_cita inválida (ISO 8601)'}), 400

    try:
        cita = CitaTaller(
            negocio_id          = negocio_id,
            cliente_nombre      = cliente_nombre,
            fecha_cita          = fecha_cita,
            cliente_telefono    = data.get('cliente_telefono'),
            placa               = data.get('placa'),
            tipo_vehiculo       = data.get('tipo_vehiculo', 'carro'),
            servicio_solicitado = data.get('servicio_solicitado'),
            notas               = data.get('notas'),
            duracion_minutos    = data.get('duracion_minutos', 60),
        )
        db.session.add(cita)
        db.session.commit()
        return jsonify({'ok': True, 'cita': cita.to_dict()}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@taller_bp.route('/taller/citas/<int:cita_id>', methods=['PUT', 'OPTIONS'])
@login_required
def actualizar_cita(cita_id):
    """PUT /api/taller/citas/<id> — Actualiza estado o datos de una cita."""
    if request.method == 'OPTIONS':
        return jsonify({}), 200

    cita = CitaTaller.query.get_or_404(cita_id)
    ok, resultado, code = _validar_negocio(cita.negocio_id)
    if not ok:
        return resultado, code

    data = request.get_json(silent=True) or {}
    try:
        for campo in ['cliente_nombre', 'cliente_telefono', 'placa', 'tipo_vehiculo',
                      'servicio_solicitado', 'notas', 'duracion_minutos', 'estado']:
            if campo in data:
                setattr(cita, campo, data[campo])
        if 'fecha_cita' in data:
            cita.fecha_cita = _parse_fecha(data['fecha_cita'])
        db.session.commit()
        return jsonify({'ok': True, 'cita': cita.to_dict()})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@taller_bp.route('/taller/citas/<int:cita_id>/convertir', methods=['POST', 'OPTIONS'])
@login_required
def convertir_cita_a_ot(cita_id):
    """
    POST /api/taller/citas/<id>/convertir
    Convierte una cita en OT. Marca la cita como completada.
    """
    if request.method == 'OPTIONS':
        return jsonify({}), 200

    cita = CitaTaller.query.get_or_404(cita_id)
    ok, resultado, code = _validar_negocio(cita.negocio_id)
    if not ok:
        return resultado, code

    if cita.orden_trabajo_id:
        return jsonify({'error': 'Esta cita ya tiene una OT asociada',
                        'orden_trabajo_id': cita.orden_trabajo_id}), 400

    try:
        ot = OrdenTrabajo(
            negocio_id          = cita.negocio_id,
            cliente_nombre      = cita.cliente_nombre,
            placa               = cita.placa,
            tipo_vehiculo       = cita.tipo_vehiculo,
            cliente_telefono    = cita.cliente_telefono,
            problema_reportado  = cita.servicio_solicitado,
        )
        db.session.add(ot)
        db.session.flush()

        cita.orden_trabajo_id = ot.id
        cita.estado = 'completada'

        db.session.commit()
        return jsonify({'ok': True, 'orden': ot.to_dict(), 'cita': cita.to_dict()}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


# ══════════════════════════════════════════════════════════════
# STATS Y HISTORIAL
# ══════════════════════════════════════════════════════════════

@taller_bp.route('/taller/stats', methods=['GET', 'OPTIONS'])
@login_required
def stats_taller():
    """GET /api/taller/stats — Resumen rápido del taller."""
    if request.method == 'OPTIONS':
        return jsonify({}), 200

    negocio_id = _get_negocio_id()
    if not negocio_id:
        return jsonify({'error': 'negocio_id requerido'}), 400

    ok, resultado, code = _validar_negocio(negocio_id)
    if not ok:
        return resultado, code

    hoy      = date.today()
    inicio_mes = datetime(hoy.year, hoy.month, 1)

    ots_activas = OrdenTrabajo.query.filter(
        OrdenTrabajo.negocio_id == negocio_id,
        OrdenTrabajo.estado.in_(['recibido', 'diagnostico', 'en_proceso', 'listo'])
    ).count()

    ots_entregadas_mes = OrdenTrabajo.query.filter(
        OrdenTrabajo.negocio_id == negocio_id,
        OrdenTrabajo.estado == 'entregado',
        OrdenTrabajo.fecha_entrega_real >= inicio_mes
    ).all()

    ingresos_mes = sum(float(o.total or 0) for o in ots_entregadas_mes)

    citas_hoy = CitaTaller.query.filter(
        CitaTaller.negocio_id == negocio_id,
        CitaTaller.estado.in_(['pendiente', 'confirmada']),
        CitaTaller.fecha_cita >= datetime.combine(hoy, datetime.min.time()),
        CitaTaller.fecha_cita <  datetime.combine(hoy + timedelta(days=1), datetime.min.time()),
    ).count()

    por_estado = {}
    for estado in OrdenTrabajo.ESTADOS:
        por_estado[estado] = OrdenTrabajo.query.filter_by(
            negocio_id=negocio_id, estado=estado
        ).count()

    return jsonify({
        'ots_activas':          ots_activas,
        'citas_hoy':            citas_hoy,
        'ingresos_mes':         ingresos_mes,
        'ots_entregadas_mes':   len(ots_entregadas_mes),
        'distribucion_estados': por_estado,
    })


@taller_bp.route('/taller/historial/<placa>', methods=['GET', 'OPTIONS'])
@login_required
def historial_placa(placa):
    """GET /api/taller/historial/<placa> — Historial completo de un vehículo."""
    if request.method == 'OPTIONS':
        return jsonify({}), 200

    negocio_id = _get_negocio_id()
    if not negocio_id:
        return jsonify({'error': 'negocio_id requerido'}), 400

    ok, resultado, code = _validar_negocio(negocio_id)
    if not ok:
        return resultado, code

    placa_upper = placa.strip().upper()
    ots = OrdenTrabajo.query.filter(
        OrdenTrabajo.negocio_id == negocio_id,
        OrdenTrabajo.placa == placa_upper
    ).order_by(OrdenTrabajo.fecha_ingreso.desc()).all()

    return jsonify({
        'placa':   placa_upper,
        'total':   len(ots),
        'ordenes': [o.to_dict() for o in ots],
    })
