import sqlalchemy as sa
from sqlalchemy.orm import relationship
from src.models.database import db
from datetime import datetime

class TransaccionOperativa(db.Model):
    """
    Modelo para registrar el historial financiero (Kardex financiero).
    Almacena cada VENTA, COMPRA o GASTO vinculado a un negocio.
    """
    __tablename__ = 'transacciones_operativas'

    id_transaccion = sa.Column(sa.Integer, primary_key=True)
    
    # Relaciones de jerarquía (Multi-tenancy)
    negocio_id = sa.Column(sa.Integer, sa.ForeignKey('negocios.id_negocio'), nullable=False)
    usuario_id = sa.Column(sa.Integer, sa.ForeignKey('usuarios.id_usuario'), nullable=False)
    sucursal_id = sa.Column(sa.Integer, nullable=True, default=1)

    # Detalles de la operación
    tipo = sa.Column(sa.String(50), nullable=False) # 'VENTA', 'GASTO', 'COMPRA'
    concepto = sa.Column(sa.String(255), nullable=False)
    monto = sa.Column(sa.Numeric(15, 2), nullable=False)
    categoria = sa.Column(sa.String(100))
    metodo_pago = sa.Column(sa.String(50)) # Ejemplo: 'Efectivo', 'Nequi', 'Transferencia'
    referencia_guia = sa.Column(sa.String(100)) 
    fecha = sa.Column(sa.DateTime, default=datetime.utcnow)

    # Relaciones para consultas ORM
    negocio = relationship("Negocio", foreign_keys=[negocio_id])
    usuario = relationship("Usuario", foreign_keys=[usuario_id])

    def to_dict(self):
        """Convierte el objeto en un diccionario compatible con el Frontend (JSON)"""
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
    """
    Modelo para el control de inventario bajo (Stock crítico) y 
    recordatorios de tareas operativas pendientes.
    """
    __tablename__ = 'alertas_operativas'
    
    id_alerta = sa.Column(sa.Integer, primary_key=True)
    negocio_id = sa.Column(sa.Integer, sa.ForeignKey('negocios.id_negocio'), nullable=False)
    usuario_id = sa.Column(sa.Integer, sa.ForeignKey('usuarios.id_usuario'), nullable=False)
    
    tarea = sa.Column(sa.Text, nullable=False) # Ejemplo: 'Stock crítico: Aceite (3 uds.)'
    fecha_programada = sa.Column(sa.DateTime, nullable=False)
    prioridad = sa.Column(sa.String(20), default="MEDIA") # ALTA, MEDIA, BAJA
    completada = sa.Column(sa.Boolean, default=False)
    fecha_creacion = sa.Column(sa.DateTime, default=datetime.utcnow)