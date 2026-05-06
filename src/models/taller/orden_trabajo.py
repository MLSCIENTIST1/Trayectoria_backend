"""
TuKomercio - Modelos Vertical Taller
Gestión de talleres automotrices y de motos

Tablas:
  - ordenes_trabajo     : OT principal (vehículo + cliente + estado)
  - items_orden_trabajo : líneas de servicios y repuestos de la OT
  - citas_taller        : agenda de citas
"""

import sqlalchemy as sa
from sqlalchemy.orm import relationship
from src.models.database import db
from datetime import datetime
import re


# ─────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────

def _generar_numero_ot(negocio_id: int) -> str:
    """Genera número OT único: OT-{negocio_id}-{timestamp}"""
    ts = datetime.utcnow().strftime('%y%m%d%H%M%S')
    return f"OT-{negocio_id}-{ts}"


def _generar_numero_cita(negocio_id: int) -> str:
    ts = datetime.utcnow().strftime('%y%m%d%H%M%S')
    return f"CITA-{negocio_id}-{ts}"


# ─────────────────────────────────────────────
# ORDEN DE TRABAJO
# ─────────────────────────────────────────────

class OrdenTrabajo(db.Model):
    """
    Orden de Trabajo (OT) — documento central del taller.
    Registra el vehículo, el cliente, los trabajos y el estado.

    Estados: recibido | diagnostico | en_proceso | listo | entregado | cancelado
    Estado pago: pendiente | parcial | pagado
    """
    __tablename__ = 'ordenes_trabajo'

    id            = sa.Column(sa.Integer, primary_key=True)
    numero_ot     = sa.Column(sa.String(30), nullable=False, unique=True, index=True)
    negocio_id    = sa.Column(
        sa.Integer,
        sa.ForeignKey('negocios.id_negocio', ondelete='CASCADE'),
        nullable=False, index=True
    )

    # ── Vehículo ──────────────────────────────
    placa         = sa.Column(sa.String(10),  nullable=True,  index=True)
    marca         = sa.Column(sa.String(60),  nullable=True)
    modelo        = sa.Column(sa.String(60),  nullable=True)
    anio          = sa.Column(sa.Integer,     nullable=True)
    kilometraje   = sa.Column(sa.Integer,     nullable=True)
    color         = sa.Column(sa.String(30),  nullable=True)
    tipo_vehiculo = sa.Column(sa.String(20),  default='carro')   # carro | moto | camioneta | otro

    # ── Cliente ───────────────────────────────
    cliente_nombre   = sa.Column(sa.String(100), nullable=False)
    cliente_telefono = sa.Column(sa.String(20),  nullable=True)
    cliente_email    = sa.Column(sa.String(120), nullable=True)

    # ── Diagnóstico ───────────────────────────
    problema_reportado = sa.Column(sa.Text, nullable=True)   # qué dice el cliente
    diagnostico        = sa.Column(sa.Text, nullable=True)   # qué encontró el mecánico
    observaciones      = sa.Column(sa.Text, nullable=True)   # notas internas

    # ── Estado ────────────────────────────────
    # recibido → diagnostico → en_proceso → listo → entregado | cancelado
    estado        = sa.Column(sa.String(20), default='recibido', nullable=False, index=True)
    estado_pago   = sa.Column(sa.String(20), default='pendiente', nullable=False)
    metodo_pago   = sa.Column(sa.String(50), nullable=True)

    # ── Fechas ────────────────────────────────
    fecha_ingreso          = sa.Column(sa.DateTime, default=datetime.utcnow, nullable=False)
    fecha_entrega_estimada = sa.Column(sa.DateTime, nullable=True)
    fecha_entrega_real     = sa.Column(sa.DateTime, nullable=True)
    fecha_actualizacion    = sa.Column(sa.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # ── Totales (calculados al guardar) ───────
    subtotal_servicios = sa.Column(sa.Numeric(14, 2), default=0)
    subtotal_repuestos = sa.Column(sa.Numeric(14, 2), default=0)
    descuento          = sa.Column(sa.Numeric(14, 2), default=0)
    total              = sa.Column(sa.Numeric(14, 2), default=0)

    # ── Relaciones ────────────────────────────
    items   = relationship(
        'ItemOrdenTrabajo',
        back_populates='orden',
        cascade='all, delete-orphan',
        lazy='select'
    )
    negocio = relationship('Negocio', foreign_keys=[negocio_id])

    # ──────────────────────────────────────────
    def __init__(self, negocio_id: int, cliente_nombre: str, **kw):
        self.negocio_id         = negocio_id
        self.cliente_nombre     = cliente_nombre
        self.numero_ot          = _generar_numero_ot(negocio_id)
        self.placa              = kw.get('placa', '').upper() if kw.get('placa') else None
        self.marca              = kw.get('marca')
        self.modelo             = kw.get('modelo')
        self.anio               = kw.get('anio')
        self.kilometraje        = kw.get('kilometraje')
        self.color              = kw.get('color')
        self.tipo_vehiculo      = kw.get('tipo_vehiculo', 'carro')
        self.cliente_telefono   = kw.get('cliente_telefono')
        self.cliente_email      = kw.get('cliente_email')
        self.problema_reportado = kw.get('problema_reportado')
        self.diagnostico        = kw.get('diagnostico')
        self.observaciones      = kw.get('observaciones')
        self.estado             = kw.get('estado', 'recibido')
        self.estado_pago        = kw.get('estado_pago', 'pendiente')
        self.metodo_pago        = kw.get('metodo_pago')
        self.fecha_entrega_estimada = kw.get('fecha_entrega_estimada')
        self.subtotal_servicios = 0
        self.subtotal_repuestos = 0
        self.descuento          = kw.get('descuento', 0)
        self.total              = 0

    def recalcular_totales(self):
        """Recalcula subtotales y total desde los items."""
        svc = sum(
            float(i.subtotal or 0) for i in self.items if i.tipo == 'servicio'
        )
        rep = sum(
            float(i.subtotal or 0) for i in self.items if i.tipo == 'repuesto'
        )
        self.subtotal_servicios = svc
        self.subtotal_repuestos = rep
        self.total = svc + rep - float(self.descuento or 0)

    # ── Estados helper ────────────────────────
    ESTADOS = ['recibido', 'diagnostico', 'en_proceso', 'listo', 'entregado', 'cancelado']
    ESTADOS_PAGO = ['pendiente', 'parcial', 'pagado']

    ESTADO_LABELS = {
        'recibido':    ('🔵', 'Recibido'),
        'diagnostico': ('🔍', 'En diagnóstico'),
        'en_proceso':  ('🔧', 'En proceso'),
        'listo':       ('✅', 'Listo'),
        'entregado':   ('📦', 'Entregado'),
        'cancelado':   ('❌', 'Cancelado'),
    }

    def to_dict(self):
        emoji, label = self.ESTADO_LABELS.get(self.estado, ('', self.estado))
        return {
            'id':                    self.id,
            'numero_ot':             self.numero_ot,
            'negocio_id':            self.negocio_id,
            # Vehículo
            'placa':                 self.placa,
            'marca':                 self.marca,
            'modelo':                self.modelo,
            'anio':                  self.anio,
            'kilometraje':           self.kilometraje,
            'color':                 self.color,
            'tipo_vehiculo':         self.tipo_vehiculo,
            'vehiculo_descripcion':  f"{self.marca or ''} {self.modelo or ''} {self.anio or ''}".strip(),
            # Cliente
            'cliente_nombre':        self.cliente_nombre,
            'cliente_telefono':      self.cliente_telefono,
            'cliente_email':         self.cliente_email,
            # Diagnóstico
            'problema_reportado':    self.problema_reportado,
            'diagnostico':           self.diagnostico,
            'observaciones':         self.observaciones,
            # Estado
            'estado':                self.estado,
            'estado_label':          label,
            'estado_emoji':          emoji,
            'estado_pago':           self.estado_pago,
            'metodo_pago':           self.metodo_pago,
            # Fechas
            'fecha_ingreso':         self.fecha_ingreso.isoformat() if self.fecha_ingreso else None,
            'fecha_entrega_estimada': self.fecha_entrega_estimada.isoformat() if self.fecha_entrega_estimada else None,
            'fecha_entrega_real':    self.fecha_entrega_real.isoformat() if self.fecha_entrega_real else None,
            # Totales
            'subtotal_servicios':    float(self.subtotal_servicios or 0),
            'subtotal_repuestos':    float(self.subtotal_repuestos or 0),
            'descuento':             float(self.descuento or 0),
            'total':                 float(self.total or 0),
            # Items
            'items':                 [i.to_dict() for i in self.items],
        }

    def __repr__(self):
        return f'<OT {self.numero_ot} | {self.placa} | {self.estado}>'


# ─────────────────────────────────────────────
# ITEM DE ORDEN DE TRABAJO
# ─────────────────────────────────────────────

class ItemOrdenTrabajo(db.Model):
    """
    Línea de una OT — puede ser un servicio (mano de obra) o un repuesto.
    Si es repuesto y está vinculado al inventario, descuenta stock al marcar entregado.
    """
    __tablename__ = 'items_orden_trabajo'

    id               = sa.Column(sa.Integer, primary_key=True)
    orden_id         = sa.Column(
        sa.Integer,
        sa.ForeignKey('ordenes_trabajo.id', ondelete='CASCADE'),
        nullable=False, index=True
    )
    tipo             = sa.Column(sa.String(20), nullable=False, default='servicio')  # servicio | repuesto
    descripcion      = sa.Column(sa.String(250), nullable=False)
    cantidad         = sa.Column(sa.Numeric(10, 2), default=1, nullable=False)
    precio_unitario  = sa.Column(sa.Numeric(14, 2), nullable=False)
    subtotal         = sa.Column(sa.Numeric(14, 2), nullable=False)

    # Vínculo opcional con inventario (solo repuestos)
    producto_id      = sa.Column(
        sa.Integer,
        sa.ForeignKey('productos_catalogo.id_producto', ondelete='SET NULL'),
        nullable=True
    )

    orden   = relationship('OrdenTrabajo', back_populates='items')
    producto = relationship('ProductoCatalogo', foreign_keys=[producto_id])

    def __init__(self, orden_id: int, tipo: str, descripcion: str,
                 cantidad, precio_unitario, producto_id=None):
        self.orden_id        = orden_id
        self.tipo            = tipo
        self.descripcion     = descripcion
        self.cantidad        = cantidad
        self.precio_unitario = precio_unitario
        self.subtotal        = float(cantidad) * float(precio_unitario)
        self.producto_id     = producto_id

    def to_dict(self):
        return {
            'id':              self.id,
            'orden_id':        self.orden_id,
            'tipo':            self.tipo,
            'descripcion':     self.descripcion,
            'cantidad':        float(self.cantidad),
            'precio_unitario': float(self.precio_unitario),
            'subtotal':        float(self.subtotal),
            'producto_id':     self.producto_id,
        }

    def __repr__(self):
        return f'<ItemOT {self.tipo} | {self.descripcion[:30]} | ${self.subtotal}>'


# ─────────────────────────────────────────────
# CITA DE TALLER
# ─────────────────────────────────────────────

class CitaTaller(db.Model):
    """
    Cita agendada en el taller.
    Puede convertirse en OT cuando el vehículo llega.

    Estados: pendiente | confirmada | cancelada | completada
    """
    __tablename__ = 'citas_taller'

    id                  = sa.Column(sa.Integer, primary_key=True)
    numero_cita         = sa.Column(sa.String(30), nullable=False, unique=True)
    negocio_id          = sa.Column(
        sa.Integer,
        sa.ForeignKey('negocios.id_negocio', ondelete='CASCADE'),
        nullable=False, index=True
    )

    # ── Cliente / vehículo ────────────────────
    cliente_nombre      = sa.Column(sa.String(100), nullable=False)
    cliente_telefono    = sa.Column(sa.String(20),  nullable=True)
    placa               = sa.Column(sa.String(10),  nullable=True)
    tipo_vehiculo       = sa.Column(sa.String(20),  default='carro')
    servicio_solicitado = sa.Column(sa.String(250), nullable=True)
    notas               = sa.Column(sa.Text,        nullable=True)

    # ── Fecha/hora ────────────────────────────
    fecha_cita          = sa.Column(sa.DateTime, nullable=False, index=True)
    duracion_minutos    = sa.Column(sa.Integer,  default=60)

    # ── Estado ────────────────────────────────
    estado              = sa.Column(sa.String(20), default='pendiente', nullable=False, index=True)

    # ── Vínculo con OT ────────────────────────
    orden_trabajo_id    = sa.Column(
        sa.Integer,
        sa.ForeignKey('ordenes_trabajo.id', ondelete='SET NULL'),
        nullable=True
    )

    # ── Fechas meta ───────────────────────────
    fecha_creacion      = sa.Column(sa.DateTime, default=datetime.utcnow)

    negocio     = relationship('Negocio',       foreign_keys=[negocio_id])
    orden       = relationship('OrdenTrabajo',  foreign_keys=[orden_trabajo_id])

    def __init__(self, negocio_id: int, cliente_nombre: str, fecha_cita, **kw):
        self.negocio_id          = negocio_id
        self.cliente_nombre      = cliente_nombre
        self.numero_cita         = _generar_numero_cita(negocio_id)
        self.fecha_cita          = fecha_cita
        self.cliente_telefono    = kw.get('cliente_telefono')
        self.placa               = kw.get('placa', '').upper() if kw.get('placa') else None
        self.tipo_vehiculo       = kw.get('tipo_vehiculo', 'carro')
        self.servicio_solicitado = kw.get('servicio_solicitado')
        self.notas               = kw.get('notas')
        self.duracion_minutos    = kw.get('duracion_minutos', 60)
        self.estado              = 'pendiente'

    def to_dict(self):
        return {
            'id':                  self.id,
            'numero_cita':         self.numero_cita,
            'negocio_id':          self.negocio_id,
            'cliente_nombre':      self.cliente_nombre,
            'cliente_telefono':    self.cliente_telefono,
            'placa':               self.placa,
            'tipo_vehiculo':       self.tipo_vehiculo,
            'servicio_solicitado': self.servicio_solicitado,
            'notas':               self.notas,
            'fecha_cita':          self.fecha_cita.isoformat() if self.fecha_cita else None,
            'duracion_minutos':    self.duracion_minutos,
            'estado':              self.estado,
            'orden_trabajo_id':    self.orden_trabajo_id,
            'fecha_creacion':      self.fecha_creacion.isoformat() if self.fecha_creacion else None,
        }

    def __repr__(self):
        return f'<Cita {self.numero_cita} | {self.cliente_nombre} | {self.fecha_cita}>'
