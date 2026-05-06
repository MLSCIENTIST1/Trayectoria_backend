"""
TuKomercio — API Vertical Restaurante v1.0
Endpoints para gestión de restaurantes: mesas, comandas y carta.

Prefijo: /api/restaurante
Autenticación: @login_required (Flask-Login)

Endpoints:
  GET    /restaurante/mesas               — listar mesas (con estado)
  POST   /restaurante/mesas               — crear mesa
  PUT    /restaurante/mesas/<id>          — actualizar mesa (nombre, capacidad, estado)
  DELETE /restaurante/mesas/<id>          — eliminar mesa (solo si libre)

  GET    /restaurante/comandas            — listar comandas activas / con filtros
  POST   /restaurante/comandas            — abrir comanda
  GET    /restaurante/comandas/<id>       — detalle comanda
  PUT    /restaurante/comandas/<id>       — actualizar comanda (estado, notas, pago)
  POST   /restaurante/comandas/<id>/items — agregar ítem
  PUT    /restaurante/comandas/<id>/items/<iid>    — actualizar ítem (cantidad, notas, estado)
  DELETE /restaurante/comandas/<id>/items/<iid>    — quitar ítem
  POST   /restaurante/comandas/<id>/cerrar         — cerrar y cobrar comanda

  GET    /restaurante/stats               — resumen: mesas ocupadas, ventas hoy
  GET    /restaurante/carta               — productos del negocio (carta digital)
"""

import logging
from datetime import datetime, date, timedelta
from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user

from src.models.database import db
from src.models.restaurante.restaurante import Mesa, Comanda, ItemComanda
from src.models.colombia_data.contabilidad.operaciones_y_catalogo import ProductoCatalogo

logger = logging.getLogger(__name__)

restaurante_bp = Blueprint('restaurante_bp', __name__)


# ══════════════════════════════════════════════════════════════
# HELPERS
# ══════════════════════════════════════════════════════════════

def _get_negocio_id():
    nid = (
        request.args.get('negocio_id')
        or request.headers.get('X-Business-ID')
        or (request.get_json(silent=True) or {}).get('negocio_id')
    )
    return int(nid) if nid else None


def _validar_negocio(negocio_id: int):
    from src.models.colombia_data.negocio import Negocio
    n = Negocio.query.get(negocio_id)
    if not n:
        return False, jsonify({'error': 'Negocio no encontrado'}), 404
    if n.usuario_id != current_user.id_usuario:
        return False, jsonify({'error': 'Sin permiso'}), 403
    return True, n, 200


# ══════════════════════════════════════════════════════════════
# MESAS
# ══════════════════════════════════════════════════════════════

@restaurante_bp.route('/restaurante/mesas', methods=['GET', 'OPTIONS'])
@login_required
def listar_mesas():
    """GET /api/restaurante/mesas — Lista todas las mesas con su estado actual."""
    if request.method == 'OPTIONS':
        return jsonify({}), 200

    negocio_id = _get_negocio_id()
    if not negocio_id:
        return jsonify({'error': 'negocio_id requerido'}), 400

    ok, resultado, code = _validar_negocio(negocio_id)
    if not ok:
        return resultado, code

    mesas = Mesa.query.filter_by(negocio_id=negocio_id, activa=True)\
                      .order_by(Mesa.numero.asc()).all()

    return jsonify({
        'mesas': [m.to_dict(include_comanda=True) for m in mesas],
        'total': len(mesas),
        'resumen': {
            'libres':    sum(1 for m in mesas if m.estado == 'libre'),
            'ocupadas':  sum(1 for m in mesas if m.estado == 'ocupada'),
            'reservadas': sum(1 for m in mesas if m.estado == 'reservada'),
        }
    })


@restaurante_bp.route('/restaurante/mesas', methods=['POST'])
@login_required
def crear_mesa():
    """POST /api/restaurante/mesas — Crea una o varias mesas."""
    data = request.get_json(silent=True) or {}
    negocio_id = data.get('negocio_id') or _get_negocio_id()
    if not negocio_id:
        return jsonify({'error': 'negocio_id requerido'}), 400

    ok, resultado, code = _validar_negocio(negocio_id)
    if not ok:
        return resultado, code

    # Soporte para crear varias mesas a la vez: { cantidad: 5 }
    cantidad = int(data.get('cantidad', 1))
    if cantidad > 1:
        # Auto-numerar desde el siguiente disponible
        ultimo = Mesa.query.filter_by(negocio_id=negocio_id)\
                           .order_by(Mesa.numero.desc()).first()
        siguiente = (ultimo.numero + 1) if ultimo else 1
        mesas_creadas = []
        for i in range(cantidad):
            m = Mesa(
                negocio_id = negocio_id,
                numero     = siguiente + i,
                capacidad  = data.get('capacidad', 4),
            )
            db.session.add(m)
            mesas_creadas.append(m)
        try:
            db.session.commit()
            return jsonify({'ok': True, 'mesas': [m.to_dict() for m in mesas_creadas]}), 201
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': str(e)}), 500

    # Mesa individual
    numero = data.get('numero')
    if not numero:
        ultimo = Mesa.query.filter_by(negocio_id=negocio_id)\
                           .order_by(Mesa.numero.desc()).first()
        numero = (ultimo.numero + 1) if ultimo else 1

    # Verificar duplicado
    existente = Mesa.query.filter_by(negocio_id=negocio_id, numero=numero).first()
    if existente:
        return jsonify({'error': f'Ya existe la Mesa {numero}'}), 400

    try:
        mesa = Mesa(
            negocio_id = negocio_id,
            numero     = numero,
            nombre     = data.get('nombre'),
            capacidad  = data.get('capacidad', 4),
        )
        db.session.add(mesa)
        db.session.commit()
        return jsonify({'ok': True, 'mesa': mesa.to_dict()}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@restaurante_bp.route('/restaurante/mesas/<int:mesa_id>', methods=['PUT', 'OPTIONS'])
@login_required
def actualizar_mesa(mesa_id):
    """PUT /api/restaurante/mesas/<id> — Actualiza nombre, capacidad o estado."""
    if request.method == 'OPTIONS':
        return jsonify({}), 200

    mesa = Mesa.query.get_or_404(mesa_id)
    ok, resultado, code = _validar_negocio(mesa.negocio_id)
    if not ok:
        return resultado, code

    data = request.get_json(silent=True) or {}
    try:
        for campo in ['nombre', 'capacidad', 'estado']:
            if campo in data:
                setattr(mesa, campo, data[campo])
        db.session.commit()
        return jsonify({'ok': True, 'mesa': mesa.to_dict()})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@restaurante_bp.route('/restaurante/mesas/<int:mesa_id>', methods=['DELETE'])
@login_required
def eliminar_mesa(mesa_id):
    """DELETE /api/restaurante/mesas/<id> — Desactiva mesa (soft delete)."""
    mesa = Mesa.query.get_or_404(mesa_id)
    ok, resultado, code = _validar_negocio(mesa.negocio_id)
    if not ok:
        return resultado, code

    if mesa.estado != 'libre':
        return jsonify({'error': 'Solo se puede eliminar una mesa libre'}), 400

    try:
        mesa.activa = False
        db.session.commit()
        return jsonify({'ok': True, 'mensaje': f'Mesa {mesa.numero} desactivada'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


# ══════════════════════════════════════════════════════════════
# COMANDAS
# ══════════════════════════════════════════════════════════════

@restaurante_bp.route('/restaurante/comandas', methods=['GET', 'OPTIONS'])
@login_required
def listar_comandas():
    """GET /api/restaurante/comandas — Lista comandas con filtros."""
    if request.method == 'OPTIONS':
        return jsonify({}), 200

    negocio_id = _get_negocio_id()
    if not negocio_id:
        return jsonify({'error': 'negocio_id requerido'}), 400

    ok, resultado, code = _validar_negocio(negocio_id)
    if not ok:
        return resultado, code

    q = Comanda.query.filter_by(negocio_id=negocio_id)

    estado = request.args.get('estado')
    if estado:
        q = q.filter(Comanda.estado == estado)
    else:
        # Por defecto: solo activas
        q = q.filter(Comanda.estado.in_(['abierta', 'en_cocina', 'lista']))

    tipo = request.args.get('tipo')
    if tipo:
        q = q.filter(Comanda.tipo == tipo)

    fecha = request.args.get('fecha')  # YYYY-MM-DD
    if fecha:
        try:
            d = datetime.strptime(fecha, '%Y-%m-%d')
            q = q.filter(
                Comanda.fecha_apertura >= d,
                Comanda.fecha_apertura <  d + timedelta(days=1)
            )
        except Exception:
            pass

    q = q.order_by(Comanda.fecha_apertura.desc())
    page  = int(request.args.get('page', 1))
    limit = int(request.args.get('limit', 50))
    total = q.count()
    comandas = q.offset((page - 1) * limit).limit(limit).all()

    return jsonify({
        'comandas': [c.to_dict() for c in comandas],
        'total':    total,
        'page':     page,
    })


@restaurante_bp.route('/restaurante/comandas', methods=['POST'])
@login_required
def abrir_comanda():
    """POST /api/restaurante/comandas — Abre una nueva comanda."""
    data = request.get_json(silent=True) or {}
    negocio_id = data.get('negocio_id') or _get_negocio_id()
    if not negocio_id:
        return jsonify({'error': 'negocio_id requerido'}), 400

    ok, resultado, code = _validar_negocio(negocio_id)
    if not ok:
        return resultado, code

    mesa_id = data.get('mesa_id')

    # Si hay mesa, marcarla como ocupada
    if mesa_id:
        mesa = Mesa.query.get(mesa_id)
        if mesa and mesa.negocio_id == negocio_id:
            if mesa.estado == 'ocupada':
                return jsonify({'error': f'La mesa {mesa.numero} ya está ocupada'}), 400
            mesa.estado = 'ocupada'

    try:
        comanda = Comanda(
            negocio_id        = negocio_id,
            mesa_id           = mesa_id,
            tipo              = data.get('tipo', 'mesa'),
            cliente_nombre    = data.get('cliente_nombre'),
            cliente_telefono  = data.get('cliente_telefono'),
            direccion_entrega = data.get('direccion_entrega'),
            notas             = data.get('notas'),
        )
        db.session.add(comanda)
        db.session.flush()

        # Items iniciales opcionales
        for item_data in data.get('items', []):
            _agregar_item_a_comanda(comanda, item_data)

        comanda.recalcular_totales()
        db.session.commit()
        return jsonify({'ok': True, 'comanda': comanda.to_dict()}), 201

    except Exception as e:
        db.session.rollback()
        logger.error(f"❌ Error abriendo comanda: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500


@restaurante_bp.route('/restaurante/comandas/<int:comanda_id>', methods=['GET', 'OPTIONS'])
@login_required
def detalle_comanda(comanda_id):
    if request.method == 'OPTIONS':
        return jsonify({}), 200

    comanda = Comanda.query.get_or_404(comanda_id)
    ok, resultado, code = _validar_negocio(comanda.negocio_id)
    if not ok:
        return resultado, code

    return jsonify(comanda.to_dict())


@restaurante_bp.route('/restaurante/comandas/<int:comanda_id>', methods=['PUT', 'OPTIONS'])
@login_required
def actualizar_comanda(comanda_id):
    """PUT /api/restaurante/comandas/<id> — Actualiza estado, notas, pago."""
    if request.method == 'OPTIONS':
        return jsonify({}), 200

    comanda = Comanda.query.get_or_404(comanda_id)
    ok, resultado, code = _validar_negocio(comanda.negocio_id)
    if not ok:
        return resultado, code

    data = request.get_json(silent=True) or {}
    try:
        for campo in ['estado', 'notas', 'metodo_pago', 'estado_pago',
                      'cliente_nombre', 'cliente_telefono', 'direccion_entrega',
                      'descuento', 'propina']:
            if campo in data:
                setattr(comanda, campo, data[campo])

        comanda.recalcular_totales()
        db.session.commit()
        return jsonify({'ok': True, 'comanda': comanda.to_dict()})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@restaurante_bp.route('/restaurante/comandas/<int:comanda_id>/cerrar', methods=['POST', 'OPTIONS'])
@login_required
def cerrar_comanda(comanda_id):
    """
    POST /api/restaurante/comandas/<id>/cerrar
    Cierra la comanda, registra el pago y libera la mesa.
    """
    if request.method == 'OPTIONS':
        return jsonify({}), 200

    comanda = Comanda.query.get_or_404(comanda_id)
    ok, resultado, code = _validar_negocio(comanda.negocio_id)
    if not ok:
        return resultado, code

    if comanda.estado in ('entregada', 'cancelada'):
        return jsonify({'error': 'La comanda ya está cerrada'}), 400

    data = request.get_json(silent=True) or {}
    try:
        comanda.estado      = 'entregada'
        comanda.estado_pago = 'pagado'
        comanda.metodo_pago = data.get('metodo_pago', comanda.metodo_pago or 'efectivo')
        comanda.fecha_cierre = datetime.utcnow()

        if 'descuento' in data:
            comanda.descuento = float(data['descuento'])
        if 'propina' in data:
            comanda.propina = float(data['propina'])

        comanda.recalcular_totales()

        # Liberar mesa
        if comanda.mesa_id:
            mesa = Mesa.query.get(comanda.mesa_id)
            if mesa:
                mesa.estado = 'libre'

        db.session.commit()
        logger.info(f"✅ Comanda {comanda.numero_comanda} cerrada — total ${comanda.total}")
        return jsonify({'ok': True, 'comanda': comanda.to_dict()})

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


# ── Items de comanda ──────────────────────────────────────────

def _agregar_item_a_comanda(comanda: Comanda, data: dict):
    nombre_item     = (data.get('nombre_item') or data.get('nombre') or '').strip()
    precio_unitario = float(data.get('precio_unitario') or data.get('precio') or 0)
    cantidad        = int(data.get('cantidad', 1))
    if not nombre_item or precio_unitario <= 0:
        return None
    item = ItemComanda(
        comanda_id      = comanda.id,
        nombre_item     = nombre_item,
        precio_unitario = precio_unitario,
        cantidad        = cantidad,
        producto_id     = data.get('producto_id'),
        notas           = data.get('notas'),
    )
    db.session.add(item)
    return item


@restaurante_bp.route('/restaurante/comandas/<int:comanda_id>/items', methods=['POST', 'OPTIONS'])
@login_required
def agregar_item_comanda(comanda_id):
    """POST /api/restaurante/comandas/<id>/items — Agrega ítem a comanda."""
    if request.method == 'OPTIONS':
        return jsonify({}), 200

    comanda = Comanda.query.get_or_404(comanda_id)
    ok, resultado, code = _validar_negocio(comanda.negocio_id)
    if not ok:
        return resultado, code

    if comanda.estado in ('entregada', 'cancelada'):
        return jsonify({'error': 'No se puede agregar ítems a una comanda cerrada'}), 400

    data = request.get_json(silent=True) or {}
    try:
        item = _agregar_item_a_comanda(comanda, data)
        if not item:
            return jsonify({'error': 'nombre_item y precio_unitario requeridos'}), 400
        db.session.flush()
        comanda.recalcular_totales()
        db.session.commit()
        return jsonify({'ok': True, 'item': item.to_dict(), 'comanda': comanda.to_dict()}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@restaurante_bp.route('/restaurante/comandas/<int:comanda_id>/items/<int:item_id>',
                      methods=['PUT', 'OPTIONS'])
@login_required
def actualizar_item_comanda(comanda_id, item_id):
    """PUT /api/restaurante/comandas/<id>/items/<iid> — Cambia cantidad, notas o estado."""
    if request.method == 'OPTIONS':
        return jsonify({}), 200

    comanda = Comanda.query.get_or_404(comanda_id)
    ok, resultado, code = _validar_negocio(comanda.negocio_id)
    if not ok:
        return resultado, code

    item = ItemComanda.query.filter_by(id=item_id, comanda_id=comanda_id).first_or_404()
    data = request.get_json(silent=True) or {}
    try:
        if 'cantidad' in data:
            item.cantidad = int(data['cantidad'])
            item.subtotal = item.cantidad * float(item.precio_unitario)
        if 'notas' in data:
            item.notas = data['notas']
        if 'estado' in data:
            item.estado = data['estado']
        comanda.recalcular_totales()
        db.session.commit()
        return jsonify({'ok': True, 'item': item.to_dict(), 'comanda': comanda.to_dict()})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@restaurante_bp.route('/restaurante/comandas/<int:comanda_id>/items/<int:item_id>',
                      methods=['DELETE'])
@login_required
def quitar_item_comanda(comanda_id, item_id):
    """DELETE /api/restaurante/comandas/<id>/items/<iid>"""
    comanda = Comanda.query.get_or_404(comanda_id)
    ok, resultado, code = _validar_negocio(comanda.negocio_id)
    if not ok:
        return resultado, code

    item = ItemComanda.query.filter_by(id=item_id, comanda_id=comanda_id).first_or_404()
    try:
        db.session.delete(item)
        db.session.flush()
        comanda.recalcular_totales()
        db.session.commit()
        return jsonify({'ok': True, 'comanda': comanda.to_dict()})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


# ══════════════════════════════════════════════════════════════
# STATS Y CARTA
# ══════════════════════════════════════════════════════════════

@restaurante_bp.route('/restaurante/stats', methods=['GET', 'OPTIONS'])
@login_required
def stats_restaurante():
    """GET /api/restaurante/stats — Resumen del día."""
    if request.method == 'OPTIONS':
        return jsonify({}), 200

    negocio_id = _get_negocio_id()
    if not negocio_id:
        return jsonify({'error': 'negocio_id requerido'}), 400

    ok, resultado, code = _validar_negocio(negocio_id)
    if not ok:
        return resultado, code

    hoy = date.today()
    inicio_hoy = datetime.combine(hoy, datetime.min.time())
    fin_hoy    = inicio_hoy + timedelta(days=1)

    mesas_total   = Mesa.query.filter_by(negocio_id=negocio_id, activa=True).count()
    mesas_libres  = Mesa.query.filter_by(negocio_id=negocio_id, activa=True, estado='libre').count()
    mesas_ocupadas = mesas_total - mesas_libres

    comandas_hoy = Comanda.query.filter(
        Comanda.negocio_id == negocio_id,
        Comanda.fecha_apertura >= inicio_hoy,
        Comanda.fecha_apertura <  fin_hoy,
    ).all()

    ventas_hoy = sum(
        float(c.total or 0) for c in comandas_hoy if c.estado == 'entregada'
    )
    comandas_activas = Comanda.query.filter(
        Comanda.negocio_id == negocio_id,
        Comanda.estado.in_(['abierta', 'en_cocina', 'lista'])
    ).count()

    return jsonify({
        'mesas_total':       mesas_total,
        'mesas_libres':      mesas_libres,
        'mesas_ocupadas':    mesas_ocupadas,
        'comandas_activas':  comandas_activas,
        'comandas_hoy':      len(comandas_hoy),
        'ventas_hoy':        ventas_hoy,
    })


@restaurante_bp.route('/restaurante/publica/<slug>/carta', methods=['GET', 'OPTIONS'])
def carta_publica(slug: str):
    """
    GET /api/restaurante/publica/{slug}/carta — Carta digital PÚBLICA.
    No requiere autenticación. Usada por la página pública del restaurante.
    """
    if request.method == 'OPTIONS':
        return jsonify({}), 200

    from src.models.colombia_data.negocio import Negocio
    negocio = Negocio.query.filter_by(slug=slug).first()
    if not negocio:
        return jsonify({'error': 'Restaurante no encontrado'}), 404

    productos_q = ProductoCatalogo.query.filter_by(
        negocio_id=negocio.id_negocio, activo=True
    ).order_by(ProductoCatalogo.categoria, ProductoCatalogo.nombre).all()

    carta = {}
    for p in productos_q:
        cat = p.categoria or 'Sin categoría'
        if cat not in carta:
            carta[cat] = []
        carta[cat].append({
            'id':          p.id_producto,
            'nombre':      p.nombre,
            'descripcion': p.descripcion,
            'precio':      float(p.precio),
            'imagen_url':  p.imagen_url,
            'categoria':   cat,
            'disponible':  p.stock > 0 if p.stock is not None else True,
        })

    return jsonify({
        'negocio': {
            'id':         negocio.id_negocio,
            'nombre':     negocio.nombre,
            'slug':       negocio.slug,
            'logo_url':   negocio.logo_url if hasattr(negocio, 'logo_url') else None,
            'telefono':   negocio.telefono,
            'direccion':  negocio.direccion,
            'config':     negocio.config_tienda if hasattr(negocio, 'config_tienda') else {},
        },
        'carta':      carta,
        'categorias': list(carta.keys()),
        'total':      len(productos_q),
    })


@restaurante_bp.route('/restaurante/carta', methods=['GET', 'OPTIONS'])
@login_required
def carta_digital():
    """
    GET /api/restaurante/carta — Devuelve el catálogo de productos
    del negocio organizado como carta de restaurante.
    """
    if request.method == 'OPTIONS':
        return jsonify({}), 200

    negocio_id = _get_negocio_id()
    if not negocio_id:
        return jsonify({'error': 'negocio_id requerido'}), 400

    ok, resultado, code = _validar_negocio(negocio_id)
    if not ok:
        return resultado, code

    productos = ProductoCatalogo.query.filter_by(
        negocio_id=negocio_id, activo=True
    ).order_by(ProductoCatalogo.categoria, ProductoCatalogo.nombre).all()

    # Agrupar por categoría
    carta = {}
    for p in productos:
        cat = p.categoria or 'Sin categoría'
        if cat not in carta:
            carta[cat] = []
        carta[cat].append({
            'id':          p.id_producto,
            'nombre':      p.nombre,
            'descripcion': p.descripcion,
            'precio':      float(p.precio),
            'imagen_url':  p.imagen_url,
            'categoria':   cat,
            'disponible':  p.stock > 0 if p.stock is not None else True,
        })

    return jsonify({
        'carta':      carta,
        'categorias': list(carta.keys()),
        'total':      len(productos),
    })
