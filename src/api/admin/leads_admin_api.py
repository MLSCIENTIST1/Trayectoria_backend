"""
╔══════════════════════════════════════════════════════════════╗
║  LEADS ADMIN API — Blueprint Flask                          ║
║  Prefix: /api/admin/leads                                   ║
║  Acceso: superadmin exclusivo                               ║
╚══════════════════════════════════════════════════════════════╝
"""

import logging
from datetime import datetime, timedelta, timezone

from flask import Blueprint, jsonify, request, g
from sqlalchemy import or_

from src.models.database import db
from src.models.leads.lead import LeadCampana, PlantillaMensaje
from src.api.auth.auth_system import superadmin_required

logger = logging.getLogger(__name__)

leads_admin_bp = Blueprint('leads_admin_bp', __name__)

# ══════════════════════════════════════════════════════════════
#  PLANTILLAS POR DEFECTO — se insertan en primer arranque
# ══════════════════════════════════════════════════════════════
PLANTILLAS_SEED = [
    {
        'nombre': 'Saludo inicial nuevo lead (TuKomercio)',
        'orden':  1,
        'cuerpo': (
            "¡Hola {nombre}! 👋 Soy Carlos, de *TuKomercio*.\n\n"
            "Vi que mostraste interés en digitalizar tu negocio. "
            "Me encantaría contarte cómo podemos ayudarte a tener tu tienda online "
            "lista en menos de 24h, con pagos, catálogo y todo incluido. 🚀\n\n"
            "¿Tienes 5 minuticos para que te cuente? 😊"
        ),
    },
    {
        'nombre': 'Saludo inicial nuevo lead (RODAR)',
        'orden':  2,
        'cuerpo': (
            "¡Hola {nombre}! 👋 Soy Carlos, de *Rodar*.\n\n"
            "Me llegó que tienes un negocio de *{nicho}* y quería contarte "
            "que tenemos una solución especial para vendedores como tú. 💼\n\n"
            "¿Podemos hablar hoy? Te explico todo en 5 minutos."
        ),
    },
    {
        'nombre': 'Follow-up suave 24h',
        'orden':  3,
        'cuerpo': (
            "¡Hola {nombre}! 😊 Solo quería saber si pudiste revisar "
            "lo que te compartí ayer sobre TuKomercio.\n\n"
            "Si tienes alguna duda o quieres que te explique algo puntual, "
            "con gusto te ayudo. No hay prisa. 🤝"
        ),
    },
    {
        'nombre': 'Validación de nicho — personalizado',
        'orden':  4,
        'cuerpo': (
            "¡Hola {nombre}! Cuéntame un poco más sobre tu negocio de *{nicho}*:\n\n"
            "1️⃣ ¿Vendes más por WhatsApp, Instagram o punto físico?\n"
            "2️⃣ ¿Tienes catálogo digital hoy en día?\n"
            "3️⃣ ¿Cuántos pedidos manejas más o menos al mes?\n\n"
            "Con eso te digo exactamente qué plan te conviene más. 🎯"
        ),
    },
    {
        'nombre': 'Cierre de videollamada',
        'orden':  5,
        'cuerpo': (
            "¡Hola {nombre}! 😊 ¿Te parece si nos vemos 15 minuticos por meet o zoom?\n\n"
            "Te muestro en vivo cómo quedaría tu tienda online, "
            "resolvemos tus dudas y definimos si esto es para ti. "
            "Sin compromiso. 📱\n\n"
            "¿Qué día y hora te queda bien esta semana?"
        ),
    },
    {
        'nombre': 'Cotización Plan Impermeable',
        'orden':  6,
        'cuerpo': (
            "¡Hola {nombre}! Aquí te va el resumen del plan que te recomiendo:\n\n"
            "✅ *Plan Distinguished* — $XX.000/mes\n"
            "• Tienda online con dominio propio\n"
            "• Catálogo ilimitado + pagos con Wompi\n"
            "• Soporte prioritario\n\n"
            "¿Arrancamos? Te tengo lista en 24h. 🚀"
        ),
    },
    {
        'nombre': 'Pitch técnico Distinguished/Pro',
        'orden':  7,
        'cuerpo': (
            "¡Hola {nombre}! Te cuento qué incluye TuKomercio Distinguished:\n\n"
            "🛒 Tienda online profesional\n"
            "💳 Pagos con tarjeta / PSE / efectivo (Wompi)\n"
            "📦 Gestión de pedidos en tiempo real\n"
            "📊 Dashboard de ventas\n"
            "📱 100% desde el celular\n\n"
            "Todo por un precio fijo mensual sin comisiones. "
            "¿Le doy? 💪"
        ),
    },
]


def _seed_plantillas():
    """Inserta plantillas por defecto si la tabla está vacía."""
    try:
        if PlantillaMensaje.query.count() == 0:
            for p in PLANTILLAS_SEED:
                db.session.add(PlantillaMensaje(**p))
            db.session.commit()
            logger.info('✅ Plantillas de mensajes inicializadas.')
    except Exception as exc:
        db.session.rollback()
        logger.warning(f'⚠️  No se pudieron seed plantillas: {exc}')


# ══════════════════════════════════════════════════════════════
#  HELPERS
# ══════════════════════════════════════════════════════════════
def _parse_dt(value):
    """Convierte string ISO a datetime. Retorna None si falla."""
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace('Z', '+00:00')).replace(tzinfo=None)
    except Exception:
        return None


# ══════════════════════════════════════════════════════════════
#  LEADS — CRUD
# ══════════════════════════════════════════════════════════════

@leads_admin_bp.route('', methods=['GET'])
@superadmin_required
def listar_leads():
    """GET /api/admin/leads — Lista leads con filtros y paginación."""
    estado    = request.args.get('estado')
    prioridad = request.args.get('prioridad')
    origen    = request.args.get('origen')
    buscar    = request.args.get('q', '').strip()
    page      = max(1, int(request.args.get('page', 1)))
    per_page  = min(100, int(request.args.get('per_page', 50)))

    query = LeadCampana.query

    if estado:
        query = query.filter(LeadCampana.estado == estado)
    if prioridad:
        query = query.filter(LeadCampana.prioridad == prioridad)
    if origen:
        query = query.filter(LeadCampana.origen == origen)
    if buscar:
        like = f'%{buscar}%'
        query = query.filter(
            or_(LeadCampana.nombre.ilike(like), LeadCampana.telefono.ilike(like))
        )

    query = query.order_by(LeadCampana.fecha_ultimo_mensaje.desc().nullslast(),
                           LeadCampana.created_at.desc())

    pagination = query.paginate(page=page, per_page=per_page, error_out=False)

    return jsonify({
        'ok':      True,
        'leads':   [l.to_dict() for l in pagination.items],
        'total':   pagination.total,
        'page':    page,
        'pages':   pagination.pages,
        'per_page': per_page,
    })


@leads_admin_bp.route('', methods=['POST'])
@superadmin_required
def crear_lead():
    """POST /api/admin/leads — Crea un nuevo lead."""
    data = request.get_json(silent=True) or {}

    telefono = data.get('telefono', '').strip()
    if not telefono:
        return jsonify({'ok': False, 'error': 'telefono es obligatorio'}), 400

    lead = LeadCampana(
        nombre=data.get('nombre'),
        telefono=telefono,
        nicho=data.get('nicho'),
        info_adicional=data.get('info_adicional'),
        estado=data.get('estado', 'nuevo'),
        prioridad=data.get('prioridad', 'media'),
        origen=data.get('origen', 'meta_ads_tukomercio'),
        fecha_primer_contacto=_parse_dt(data.get('fecha_primer_contacto')) or datetime.utcnow(),
        proximo_recordatorio=_parse_dt(data.get('proximo_recordatorio')),
    )
    db.session.add(lead)
    db.session.commit()
    logger.info(f'✅ Lead creado: {lead.id} — {lead.nombre or lead.telefono}')
    return jsonify({'ok': True, 'lead': lead.to_dict()}), 201


@leads_admin_bp.route('/<int:lead_id>', methods=['PUT'])
@superadmin_required
def actualizar_lead(lead_id):
    """PUT /api/admin/leads/<id> — Actualiza campos del lead."""
    lead = LeadCampana.query.get_or_404(lead_id)
    data = request.get_json(silent=True) or {}

    campos = [
        'nombre', 'telefono', 'nicho', 'info_adicional',
        'estado', 'prioridad', 'origen',
    ]
    for campo in campos:
        if campo in data:
            setattr(lead, campo, data[campo])

    if 'proximo_recordatorio' in data:
        lead.proximo_recordatorio = _parse_dt(data['proximo_recordatorio'])
    if 'fecha_primer_contacto' in data:
        lead.fecha_primer_contacto = _parse_dt(data['fecha_primer_contacto'])

    lead.updated_at = datetime.utcnow()
    db.session.commit()
    return jsonify({'ok': True, 'lead': lead.to_dict()})


@leads_admin_bp.route('/<int:lead_id>', methods=['DELETE'])
@superadmin_required
def eliminar_lead(lead_id):
    """DELETE /api/admin/leads/<id> — Elimina un lead."""
    lead = LeadCampana.query.get_or_404(lead_id)
    db.session.delete(lead)
    db.session.commit()
    return jsonify({'ok': True, 'mensaje': f'Lead {lead_id} eliminado'})


# ══════════════════════════════════════════════════════════════
#  MARCAR ENVIADO
# ══════════════════════════════════════════════════════════════

@leads_admin_bp.route('/<int:lead_id>/marcar-enviado', methods=['POST'])
@superadmin_required
def marcar_enviado(lead_id):
    """POST /api/admin/leads/<id>/marcar-enviado — Registra envío de mensaje."""
    lead = LeadCampana.query.get_or_404(lead_id)
    data = request.get_json(silent=True) or {}

    lead.mensajes_enviados    += 1
    lead.fecha_ultimo_mensaje  = datetime.utcnow()
    lead.updated_at            = datetime.utcnow()

    if data.get('proximo_recordatorio'):
        lead.proximo_recordatorio = _parse_dt(data['proximo_recordatorio'])

    # Si el lead era 'nuevo', pasarlo a 'en_seguimiento' automáticamente
    if lead.estado == 'nuevo':
        lead.estado = 'en_seguimiento'

    db.session.commit()
    return jsonify({'ok': True, 'lead': lead.to_dict()})


# ══════════════════════════════════════════════════════════════
#  RECORDATORIOS
# ══════════════════════════════════════════════════════════════

@leads_admin_bp.route('/proximos-recordatorios', methods=['GET'])
@superadmin_required
def proximos_recordatorios():
    """GET /api/admin/leads/proximos-recordatorios — Leads con recordatorio <= ahora + 24h."""
    hasta = datetime.utcnow() + timedelta(hours=24)
    leads = (
        LeadCampana.query
        .filter(
            LeadCampana.proximo_recordatorio != None,
            LeadCampana.proximo_recordatorio <= hasta,
            ~LeadCampana.estado.in_(['cerrado_ganado', 'cerrado_perdido'])
        )
        .order_by(LeadCampana.proximo_recordatorio.asc())
        .all()
    )
    return jsonify({'ok': True, 'recordatorios': [l.to_dict() for l in leads], 'total': len(leads)})


# ══════════════════════════════════════════════════════════════
#  ESTADÍSTICAS
# ══════════════════════════════════════════════════════════════

@leads_admin_bp.route('/estadisticas', methods=['GET'])
@superadmin_required
def estadisticas():
    """GET /api/admin/leads/estadisticas — Resumen numérico."""
    total      = LeadCampana.query.count()
    por_estado = {}
    for estado in LeadCampana.ESTADOS:
        por_estado[estado] = LeadCampana.query.filter_by(estado=estado).count()

    por_prioridad = {}
    for p in LeadCampana.PRIORIDADES:
        por_prioridad[p] = LeadCampana.query.filter_by(prioridad=p).count()

    hoy    = datetime.utcnow().date()
    vencidos = (
        LeadCampana.query
        .filter(
            LeadCampana.proximo_recordatorio != None,
            LeadCampana.proximo_recordatorio < datetime.utcnow(),
            ~LeadCampana.estado.in_(['cerrado_ganado', 'cerrado_perdido'])
        )
        .count()
    )

    return jsonify({
        'ok': True,
        'total': total,
        'por_estado': por_estado,
        'por_prioridad': por_prioridad,
        'recordatorios_vencidos': vencidos,
    })


# ══════════════════════════════════════════════════════════════
#  PLANTILLAS
# ══════════════════════════════════════════════════════════════

@leads_admin_bp.route('/plantillas', methods=['GET'])
@superadmin_required
def listar_plantillas():
    """GET /api/admin/leads/plantillas — Lista todas las plantillas activas."""
    _seed_plantillas()
    plantillas = PlantillaMensaje.query.filter_by(activa=True).order_by(PlantillaMensaje.orden).all()
    return jsonify({'ok': True, 'plantillas': [p.to_dict() for p in plantillas]})


@leads_admin_bp.route('/plantillas', methods=['POST'])
@superadmin_required
def crear_plantilla():
    """POST /api/admin/leads/plantillas — Crea plantilla."""
    data = request.get_json(silent=True) or {}
    if not data.get('nombre') or not data.get('cuerpo'):
        return jsonify({'ok': False, 'error': 'nombre y cuerpo son obligatorios'}), 400
    p = PlantillaMensaje(nombre=data['nombre'], cuerpo=data['cuerpo'], orden=data.get('orden', 99))
    db.session.add(p)
    db.session.commit()
    return jsonify({'ok': True, 'plantilla': p.to_dict()}), 201


@leads_admin_bp.route('/plantillas/<int:pid>', methods=['PUT'])
@superadmin_required
def actualizar_plantilla(pid):
    """PUT /api/admin/leads/plantillas/<id> — Actualiza plantilla."""
    p    = PlantillaMensaje.query.get_or_404(pid)
    data = request.get_json(silent=True) or {}
    for campo in ['nombre', 'cuerpo', 'orden', 'activa']:
        if campo in data:
            setattr(p, campo, data[campo])
    p.updated_at = datetime.utcnow()
    db.session.commit()
    return jsonify({'ok': True, 'plantilla': p.to_dict()})


@leads_admin_bp.route('/plantillas/<int:pid>', methods=['DELETE'])
@superadmin_required
def eliminar_plantilla(pid):
    p = PlantillaMensaje.query.get_or_404(pid)
    p.activa = False
    db.session.commit()
    return jsonify({'ok': True})
