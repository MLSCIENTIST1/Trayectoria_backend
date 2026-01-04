import sqlalchemy as sa
from sqlalchemy.orm import relationship
from src.models.database import db
from datetime import datetime

class TransaccionOperativa(db.Model):
    __tablename__ = 'transacciones_operativas'

    id_transaccion = sa.Column(sa.Integer, primary_key=True)
    
    # Vinculación con Negocios y Usuarios (subiendo dos niveles en la jerarquía de modelos)
    negocio_id = sa.Column(sa.Integer, sa.ForeignKey('negocios.id_negocio'), nullable=False)
    usuario_id = sa.Column(sa.Integer, sa.ForeignKey('usuarios.id_usuario'), nullable=False)
    sucursal_id = sa.Column(sa.Integer, nullable=True, default=1)

    # Detalle Financiero
    tipo = sa.Column(sa.String(50), nullable=False) # 'VENTA', 'GASTO', 'COMPRA', 'INGRESO_DIV'
    concepto = sa.Column(sa.String(255), nullable=False)
    monto = sa.Column(sa.Numeric(15, 2), nullable=False)
    categoria = sa.Column(sa.String(100))
    metodo_pago = sa.Column(sa.String(50)) # 'Efectivo', 'Banco', etc.
    referencia_guia = sa.Column(sa.String(100)) 
    fecha = sa.Column(sa.DateTime, default=datetime.utcnow)

    # Relaciones explícitas
    negocio = relationship("Negocio", foreign_keys=[negocio_id])
    usuario = relationship("Usuario", foreign_keys=[usuario_id])

    def to_dict(self):
        return {
            "id": self.id_transaccion,
            "tipo": self.tipo,
            "concepto": self.concepto,
            "monto": float(self.monto),
            "categoria": self.categoria,
            "metodo": self.metodo_pago,
            "guia": self.referencia_guia,
            "fecha": self.fecha.strftime('%Y-%m-%d %H:%M:%S')
        }

class AlertaOperativa(db.Model):
    __tablename__ = 'alertas_operativas'

    id_alerta = sa.Column(sa.Integer, primary_key=True)
    negocio_id = sa.Column(sa.Integer, sa.ForeignKey('negocios.id_negocio'), nullable=False)
    usuario_id = sa.Column(sa.Integer, sa.ForeignKey('usuarios.id_usuario'), nullable=False)
    
    tarea = sa.Column(sa.Text, nullable=False)
    fecha_programada = sa.Column(sa.DateTime, nullable=False)
    prioridad = sa.Column(sa.String(20), default="MEDIA") # ALTA, MEDIA, BAJA
    completada = sa.Column(sa.Boolean, default=False)
    fecha_creacion = sa.Column(sa.DateTime, default=datetime.utcnow)