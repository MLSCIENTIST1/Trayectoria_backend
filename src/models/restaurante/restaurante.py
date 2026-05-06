"""
TuKomercio - Modelos Vertical Restaurante
Gestión de mesas, carta y comandas

Tablas:
  - mesas_restaurante : mesas del salón
  - comandas          : orden por mesa / domicilio / para llevar
  - items_comanda     : platos/bebidas de cada comanda
"""

import sqlalchemy as sa
from sqlalchemy.orm import relationship
from src.models.database import db
from datetime import datetime


# ─────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────

def _generar_numero_comanda(negocio_id: int) -> str:
    ts = datetime.utcnow().strftime('%y%m%d%H%M%S')
    return f"CMD-{negocio_id}-{ts}"


# ─────────────────────────────────────────────
# MESA
# ─────────────────────────────────────────────

class Mesa(db.Model):
    """
    Mesa del restaurante.
    Estado: libre | ocupada | reservada | bloqueada
    """
    __tablename__ = 'mesas_restaurante'

    id         = sa.Column(sa.Integer, primary_key=True)
    negocio_id = sa.Column(
        sa.Integer,
        sa.ForeignKey('negocios.id_negocio', ondelete='CASCADE'),
        nullable=False, index=True
    )
    numero     = sa.Column(sa.Integer,     nullable=False)          # 1, 2, 3…
    nombre     = sa.Column(sa.String(60),  nullable=True)           # "Terraza", "VIP"
    capacidad  = sa.Column(sa.Integer,     default=4)
    estado     = sa.Column(sa.String(20),  default='libre', nullable=False, index=True)
    activa     = sa.Column(sa.Boolean,     default=True)

    negocio  = relationship('Negocio', foreign_keys=[negocio_id])
    comandas = relationship(
        'Comanda',
        back_populates='mesa',
        lazy='dynamic'
    )

    __table_args__ = (
        sa.UniqueConstraint('negocio_id', 'numero', name='uq_mesa_negocio_numero'),
    )

    def __init__(self, negocio_id: int, numero: int, **kw):
        self.negocio_id = negocio_id
        self.numero     = numero
        self.nombre     = kw.get('nombre') or f"Mesa {numero}"
        self.capacidad  = kw.get('capacidad', 4)
        self.estado     = 'libre'
        self.activa     = True

    def comanda_activa(self):
        """Retorna la comanda abierta de esta mesa, si existe."""
        return self.comandas.filter(
            Comanda.estado.in_(['abierta', 'en_cocina', 'lista'])
        ).first()

    def to_dict(self, include_comanda=False):
        d = {
            'id':        self.id,
            'negocio_id': self.negocio_id,
            'numero':    self.numero,
            'nombre':    self.nombre or f"Mesa {self.numero}",
            'capacidad': self.capacidad,
            'estado':    self.estado,
            'activa':    self.activa,
        }
        if include_comanda:
            c = self.comanda_activa()
            d['comanda_activa'] = c.to_dict() if c else None
        return d

    def __repr__(self):
        return f'<Mesa {self.numero} | {self.estado}>'


# ─────────────────────────────────────────────
# COMANDA
# ─────────────────────────────────────────────

class Comanda(db.Model):
    """
    Comanda = orden de un cliente.
    Puede ser de mesa, domicilio o para llevar.

    Estados: abierta → en_cocina → lista → entregada | cancelada
    Estado pago: pendiente | pagado
    """
    __tablename__ = 'comandas'

    id             = sa.Column(sa.Integer, primary_key=True)
    numero_comanda = sa.Column(sa.String(30), nullable=False, unique=True, index=True)
    negocio_id     = sa.Column(
        sa.Integer,
        sa.ForeignKey('negocios.id_negocio', ondelete='CASCADE'),
        nullable=False, index=True
    )
    mesa_id        = sa.Column(
        sa.Integer,
        sa.ForeignKey('mesas_restaurante.id', ondelete='SET NULL'),
        nullable=True
    )

    # ── Tipo de orden ─────────────────────────
    tipo           = sa.Column(sa.String(20), default='mesa', nullable=False)
    # mesa | domicilio | llevar

    # ── Cliente (para domicilio o datos extra) ─
    cliente_nombre    = sa.Column(sa.String(100), nullable=True)
    cliente_telefono  = sa.Column(sa.String(20),  nullable=True)
    direccion_entrega = sa.Column(sa.Text,         nullable=True)

    # ── Estado ────────────────────────────────
    estado       = sa.Column(sa.String(20), default='abierta', nullable=False, index=True)
    estado_pago  = sa.Column(sa.String(20), default='pendiente', nullable=False)
    metodo_pago  = sa.Column(sa.String(50), nullable=True)

    # ── Totales ───────────────────────────────
    subtotal     = sa.Column(sa.Numeric(14, 2), default=0)
    descuento    = sa.Column(sa.Numeric(14, 2), default=0)
    propina      = sa.Column(sa.Numeric(14, 2), default=0)
    total        = sa.Column(sa.Numeric(14, 2), default=0)

    # ── Notas ─────────────────────────────────
    notas        = sa.Column(sa.Text, nullable=True)

    # ── Fechas ────────────────────────────────
    fecha_apertura = sa.Column(sa.DateTime, default=datetime.utcnow, nullable=False)
    fecha_cierre   = sa.Column(sa.DateTime, nullable=True)

    # ── Relaciones ────────────────────────────
    mesa   = relationship('Mesa',        back_populates='comandas', foreign_keys=[mesa_id])
    negocio = relationship('Negocio',    foreign_keys=[negocio_id])
    items  = relationship(
        'ItemComanda',
        back_populates='comanda',
        cascade='all, delete-orphan',
        lazy='select'
    )

    ESTADO_LABELS = {
        'abierta':   ('🟢', 'Abierta'),
        'en_cocina': ('🔥', 'En cocina'),
        'lista':     ('✅', 'Lista'),
        'entregada': ('📦', 'Entregada'),
        'cancelada': ('❌', 'Cancelada'),
    }

    def __init__(self, negocio_id: int, **kw):
        self.negocio_id       = negocio_id
        self.numero_comanda   = _generar_numero_comanda(negocio_id)
        self.mesa_id          = kw.get('mesa_id')
        self.tipo             = kw.get('tipo', 'mesa')
        self.cliente_nombre   = kw.get('cliente_nombre')
        self.cliente_telefono = kw.get('cliente_telefono')
        self.direccion_entrega = kw.get('direccion_entrega')
        self.notas            = kw.get('notas')
        self.estado           = 'abierta'
        self.estado_pago      = 'pendiente'
        self.subtotal         = 0
        self.descuento        = float(kw.get('descuento', 0))
        self.propina          = float(kw.get('propina', 0))
        self.total            = 0

    def recalcular_totales(self):
        sub = sum(float(i.subtotal or 0) for i in self.items)
        self.subtotal = sub
        self.total    = sub - float(self.descuento or 0) + float(self.propina or 0)

    def to_dict(self):
        emoji, label = self.ESTADO_LABELS.get(self.estado, ('', self.estado))
        return {
            'id':               self.id,
            'numero_comanda':   self.numero_comanda,
            'negocio_id':       self.negocio_id,
            'mesa_id':          self.mesa_id,
            'mesa_nombre':      self.mesa.nombre if self.mesa else None,
            'tipo':             self.tipo,
            'cliente_nombre':   self.cliente_nombre,
            'cliente_telefono': self.cliente_telefono,
            'direccion_entrega': self.direccion_entrega,
            'estado':           self.estado,
            'estado_label':     label,
            'estado_emoji':     emoji,
            'estado_pago':      self.estado_pago,
            'metodo_pago':      self.metodo_pago,
            'subtotal':         float(self.subtotal or 0),
            'descuento':        float(self.descuento or 0),
            'propina':          float(self.propina or 0),
            'total':            float(self.total or 0),
            'notas':            self.notas,
            'fecha_apertura':   self.fecha_apertura.isoformat() if self.fecha_apertura else None,
            'fecha_cierre':     self.fecha_cierre.isoformat() if self.fecha_cierre else None,
            'items':            [i.to_dict() for i in self.items],
            'num_items':        len(self.items),
        }

    def __repr__(self):
        return f'<Comanda {self.numero_comanda} | {self.tipo} | {self.estado}>'


# ─────────────────────────────────────────────
# ITEM DE COMANDA
# ─────────────────────────────────────────────

class ItemComanda(db.Model):
    """
    Ítem de una comanda — plato, bebida o ítem del menú.
    Guarda snapshot del nombre y precio para no perder datos si el menú cambia.

    Estado individual: pendiente | preparando | listo | cancelado
    """
    __tablename__ = 'items_comanda'

    id              = sa.Column(sa.Integer, primary_key=True)
    comanda_id      = sa.Column(
        sa.Integer,
        sa.ForeignKey('comandas.id', ondelete='CASCADE'),
        nullable=False, index=True
    )
    # Vínculo al catálogo de productos (usado como carta del restaurante)
    producto_id     = sa.Column(
        sa.Integer,
        sa.ForeignKey('productos_catalogo.id_producto', ondelete='SET NULL'),
        nullable=True
    )

    # Snapshot (nombre y precio al momento de ordenar)
    nombre_item     = sa.Column(sa.String(200), nullable=False)
    precio_unitario = sa.Column(sa.Numeric(14, 2), nullable=False)
    cantidad        = sa.Column(sa.Integer,        default=1, nullable=False)
    subtotal        = sa.Column(sa.Numeric(14, 2), nullable=False)

    notas           = sa.Column(sa.String(200), nullable=True)   # "sin cebolla", "extra salsa"
    estado          = sa.Column(sa.String(20),  default='pendiente', nullable=False)

    comanda  = relationship('Comanda',          back_populates='items')
    producto = relationship('ProductoCatalogo', foreign_keys=[producto_id])

    def __init__(self, comanda_id: int, nombre_item: str,
                 precio_unitario, cantidad: int = 1, **kw):
        self.comanda_id      = comanda_id
        self.nombre_item     = nombre_item
        self.precio_unitario = precio_unitario
        self.cantidad        = cantidad
        self.subtotal        = float(precio_unitario) * int(cantidad)
        self.producto_id     = kw.get('producto_id')
        self.notas           = kw.get('notas')
        self.estado          = 'pendiente'

    def to_dict(self):
        return {
            'id':              self.id,
            'comanda_id':      self.comanda_id,
            'producto_id':     self.producto_id,
            'nombre_item':     self.nombre_item,
            'precio_unitario': float(self.precio_unitario),
            'cantidad':        self.cantidad,
            'subtotal':        float(self.subtotal),
            'notas':           self.notas,
            'estado':          self.estado,
        }

    def __repr__(self):
        return f'<ItemComanda {self.nombre_item} x{self.cantidad} | ${self.subtotal}>'
