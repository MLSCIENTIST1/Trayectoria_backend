import sqlalchemy as sa
from sqlalchemy.orm import relationship
from src.models.database import db
from datetime import datetime

class Negocio(db.Model):
    __tablename__ = 'negocios'

    id = sa.Column(sa.Integer, primary_key=True)
    nombre_negocio = sa.Column(sa.String(150), nullable=False)
    descripcion = sa.Column(sa.Text, nullable=True)
    direccion = sa.Column(sa.String(255), nullable=True)
    telefono = sa.Column(sa.String(20), nullable=True)
    categoria = sa.Column(sa.String(100), nullable=True) # Ej: Restaurante, Ferretería
    
    # Relación con la tabla Colombia (ciudades)
    # Importante: usamos 'colombia.ciudad_id' porque ese es el nombre en tu DB
    ciudad_id = sa.Column(sa.Integer, sa.ForeignKey('colombia.ciudad_id'), nullable=False)
    
    # Relación con el Usuario (dueño del negocio)
    usuario_id = sa.Column(sa.Integer, sa.ForeignKey('usuarios.id_usuario'), nullable=False)
    
    fecha_registro = sa.Column(sa.DateTime, default=datetime.utcnow)

    # Relationships para facilitar consultas
    ciudad = relationship("Colombia", backref="negocios")
    dueno = relationship("Usuario", backref="mis_negocios")

    def __repr__(self):
        return f'<Negocio {self.nombre_negocio} en Ciudad ID {self.ciudad_id}>'

    def serialize(self):
        """Retorna el objeto en formato diccionario para la API"""
        return {
            "id": self.id,
            "nombre_negocio": self.nombre_negocio,
            "descripcion": self.descripcion,
            "categoria": self.categoria,
            "ciudad": self.ciudad.ciudad_nombre if self.ciudad else "No asignada",
            "fecha_registro": self.fecha_registro.strftime('%Y-%m-%d')
        }