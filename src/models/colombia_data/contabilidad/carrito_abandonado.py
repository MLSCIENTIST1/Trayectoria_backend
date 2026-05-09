# ═══════════════════════════════════════════════════════════════════════════════
# TUKOMERCIO — Carrito Abandonado v1.0
# ═══════════════════════════════════════════════════════════════════════════════
#
# Registra sesiones de checkout que NO terminaron en pedido.
# El checkout.js envía el carrito cuando el comprador llena su teléfono y
# luego abandona sin completar la compra.
#
# Flujo:
#   1. Comprador llena #telefono en el checkout → JS dispara POST (fire-and-forget)
#   2. Si completa el pedido → checkout_api.py llama marcar_recuperado(telefono)
#   3. Si no completa → queda como 'abandonado' y aparece en el panel del tendero
#   4. Tendero puede contactar por WhatsApp o marcar como 'ignorado'
#
# Unicidad: (negocio_id, telefono) → upsert actualiza el snapshot del carrito
# ═══════════════════════════════════════════════════════════════════════════════

from datetime import datetime, timezone
from sqlalchemy.dialects.postgresql import JSONB
from src.models.database import db


class CarritoAbandonado(db.Model):
    __tablename__ = 'carritos_abandonados'

    id         = db.Column(db.Integer, primary_key=True)
    negocio_id = db.Column(
        db.Integer,
        db.ForeignKey('negocios.id_negocio', ondelete='CASCADE'),
        nullable=False, index=True
    )

    # Datos del posible comprador (del formulario de checkout)
    telefono = db.Column(db.String(25), nullable=False)
    nombre   = db.Column(db.String(120))
    correo   = db.Column(db.String(150))

    # Snapshot del carrito
    productos       = db.Column(JSONB, default=list)
    total_estimado  = db.Column(db.Numeric(12, 2), default=0)
    num_items       = db.Column(db.Integer, default=0)

    # Estado
    # abandonado → sin pedido después de X tiempo
    # recuperado  → el comprador terminó comprando (pedido_id queda asignado)
    # ignorado    → el tendero lo descartó manualmente
    estado    = db.Column(db.String(20), default='abandonado', nullable=False, index=True)
    pedido_id = db.Column(db.Integer, nullable=True)  # ID del pedido si se recuperó

    created_at = db.Column(
        db.DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )
    updated_at = db.Column(
        db.DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc)
    )

    # Nota: sin relationship a Negocio — la API filtra por negocio_id directamente.
    # Evita conflictos de mapper en startup cuando el modelo se importa fuera
    # del ciclo principal de models/__init__.py.

    __table_args__ = (
        db.UniqueConstraint('negocio_id', 'telefono', name='uq_carrito_negocio_tel'),
    )

    # ── Métodos ──────────────────────────────────────────────────────────────

    @classmethod
    def upsert(cls, negocio_id: int, telefono: str, productos: list,
               total: float, nombre: str = None, correo: str = None):
        """
        Crea o actualiza el carrito abandonado de un teléfono.
        Si ya existía como 'recuperado', lo deja intacto.
        """
        existente = cls.query.filter_by(
            negocio_id=negocio_id, telefono=telefono
        ).first()

        if existente:
            if existente.estado == 'recuperado':
                # Ya compró → crear nuevo registro limpio solo si el carrito cambió mucho
                return existente
            # Actualizar snapshot
            existente.productos      = productos
            existente.total_estimado = total
            existente.num_items      = sum(p.get('cantidad', 1) for p in productos)
            existente.nombre         = nombre or existente.nombre
            existente.correo         = correo or existente.correo
            existente.estado         = 'abandonado'
            existente.updated_at     = datetime.now(timezone.utc)
            return existente

        nuevo = cls(
            negocio_id     = negocio_id,
            telefono       = telefono,
            nombre         = nombre,
            correo         = correo,
            productos      = productos,
            total_estimado = total,
            num_items      = sum(p.get('cantidad', 1) for p in productos),
            estado         = 'abandonado',
        )
        db.session.add(nuevo)
        return nuevo

    @classmethod
    def marcar_recuperado(cls, negocio_id: int, telefono: str, pedido_id: int = None):
        """Llamado desde checkout_api cuando el pedido se completa exitosamente."""
        c = cls.query.filter_by(
            negocio_id=negocio_id, telefono=telefono, estado='abandonado'
        ).first()
        if c:
            c.estado    = 'recuperado'
            c.pedido_id = pedido_id
            c.updated_at = datetime.now(timezone.utc)
        return c

    def to_dict(self) -> dict:
        return {
            'id':              self.id,
            'negocio_id':      self.negocio_id,
            'telefono':        self.telefono,
            'nombre':          self.nombre or '',
            'correo':          self.correo or '',
            'productos':       self.productos or [],
            'total_estimado':  float(self.total_estimado or 0),
            'num_items':       self.num_items or 0,
            'estado':          self.estado,
            'pedido_id':       self.pedido_id,
            'created_at':      self.created_at.isoformat() if self.created_at else None,
            'updated_at':      self.updated_at.isoformat() if self.updated_at else None,
        }

    def __repr__(self):
        return f'<CarritoAbandonado negocio={self.negocio_id} tel={self.telefono} estado={self.estado}>'
