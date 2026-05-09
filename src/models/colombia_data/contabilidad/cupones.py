# ═══════════════════════════════════════════════════════════════════════════════
# TUKOMERCIO — Modelo Cupones de Descuento v1.0
# ═══════════════════════════════════════════════════════════════════════════════
#
# Tabla: cupones
#   - Un cupón pertenece a un negocio (multi-tenant)
#   - Tipos: porcentaje (%) o valor_fijo (COP)
#   - Controla: fecha_inicio, fecha_fin, usos_max, min_compra, max_descuento
#
# ═══════════════════════════════════════════════════════════════════════════════

from datetime import datetime, timezone, date as _date
from src.models.database import db


class Cupon(db.Model):
    """Cupón de descuento para una tienda TuKomercio."""

    __tablename__ = 'cupones'

    # ─── PK ───────────────────────────────────────────────────────────────────
    id = db.Column(db.Integer, primary_key=True)

    # ─── Pertenencia ──────────────────────────────────────────────────────────
    negocio_id = db.Column(
        db.Integer,
        db.ForeignKey('negocios.id_negocio', ondelete='CASCADE'),
        nullable=False,
        index=True
    )

    # ─── Identificación ───────────────────────────────────────────────────────
    codigo = db.Column(db.String(50), nullable=False)
    descripcion = db.Column(db.String(250))

    # ─── Tipo y valor ─────────────────────────────────────────────────────────
    tipo = db.Column(db.String(20), nullable=False)          # 'porcentaje' | 'valor_fijo'
    valor = db.Column(db.Numeric(10, 2), nullable=False)     # % o COP

    # ─── Condiciones ──────────────────────────────────────────────────────────
    min_compra = db.Column(db.Numeric(12, 2), default=0)     # subtotal mínimo
    max_descuento = db.Column(db.Numeric(12, 2))             # tope para porcentaje

    # ─── Límite de usos ───────────────────────────────────────────────────────
    usos_max = db.Column(db.Integer)                         # None = ilimitado
    usos_actuales = db.Column(db.Integer, default=0, nullable=False)

    # ─── Vigencia ─────────────────────────────────────────────────────────────
    fecha_inicio = db.Column(db.Date)
    fecha_fin = db.Column(db.Date)

    # ─── Estado ───────────────────────────────────────────────────────────────
    activo = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(
        db.DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc)
    )

    # ─── Unicidad por negocio ─────────────────────────────────────────────────
    __table_args__ = (
        db.UniqueConstraint('negocio_id', 'codigo', name='uq_cupon_negocio_codigo'),
    )

    # ─────────────────────────────────────────────────────────────────────────
    # MÉTODOS DE NEGOCIO
    # ─────────────────────────────────────────────────────────────────────────

    def calcular_descuento(self, subtotal: float) -> float:
        """Devuelve el monto de descuento aplicable al subtotal dado."""
        subtotal = float(subtotal)
        if self.tipo == 'porcentaje':
            desc = subtotal * float(self.valor) / 100.0
            if self.max_descuento:
                desc = min(desc, float(self.max_descuento))
        else:  # valor_fijo
            desc = float(self.valor)
        return round(min(desc, subtotal), 2)

    def es_valido(self, subtotal: float) -> tuple:
        """
        Verifica si el cupón puede aplicarse al subtotal dado.
        Retorna (bool_valido, str_mensaje_error).
        """
        hoy = _date.today()

        if not self.activo:
            return False, 'El cupón no está activo'
        if self.fecha_inicio and hoy < self.fecha_inicio:
            return False, f'El cupón estará disponible desde el {self.fecha_inicio.strftime("%d/%m/%Y")}'
        if self.fecha_fin and hoy > self.fecha_fin:
            return False, 'El cupón ha expirado'
        if self.usos_max is not None and self.usos_actuales >= self.usos_max:
            return False, 'El cupón ya agotó todos sus usos'
        if self.min_compra and float(subtotal) < float(self.min_compra):
            return False, f'Compra mínima de ${float(self.min_compra):,.0f} requerida para usar este cupón'

        return True, ''

    def to_dict(self):
        return {
            'id': self.id,
            'negocio_id': self.negocio_id,
            'codigo': self.codigo,
            'descripcion': self.descripcion,
            'tipo': self.tipo,
            'valor': float(self.valor),
            'min_compra': float(self.min_compra) if self.min_compra else 0,
            'max_descuento': float(self.max_descuento) if self.max_descuento else None,
            'usos_max': self.usos_max,
            'usos_actuales': self.usos_actuales,
            'fecha_inicio': self.fecha_inicio.isoformat() if self.fecha_inicio else None,
            'fecha_fin': self.fecha_fin.isoformat() if self.fecha_fin else None,
            'activo': self.activo,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }

    def __repr__(self):
        return f'<Cupon {self.codigo} negocio={self.negocio_id} tipo={self.tipo} valor={self.valor}>'
