import sqlalchemy as sa
from sqlalchemy.orm import relationship
from src.models.database import db
from datetime import datetime

class Negocio(db.Model):
    __tablename__ = 'negocios'

    # 1. Columnas Principales
    # Se cambia 'id' por 'id_negocio' para que coincida con la ForeignKey de Sucursales
    id_negocio = sa.Column(sa.Integer, primary_key=True)
    nombre_negocio = sa.Column(sa.String(150), nullable=False)
    descripcion = sa.Column(sa.Text, nullable=True)
    direccion = sa.Column(sa.String(255), nullable=True)
    telefono = sa.Column(sa.String(20), nullable=True)
    categoria = sa.Column(sa.String(100), nullable=True) 
    
    # 2. Claves Foráneas (Foreign Keys)
    ciudad_id = sa.Column(sa.Integer, sa.ForeignKey('colombia.ciudad_id'), nullable=False)
    usuario_id = sa.Column(sa.Integer, sa.ForeignKey('usuarios.id_usuario'), nullable=False)
    
    # Usamos func.now() o datetime.utcnow para mayor precisión
    fecha_registro = sa.Column(sa.DateTime, default=datetime.utcnow)

    # 3. Relaciones (Relationships)
    # Importante: El back_populates es preferible a backref en SQLAlchemy moderno
    ciudad = relationship(
        "Colombia", 
        foreign_keys=[ciudad_id]
    )
    
    dueno = relationship(
        "Usuario", 
        foreign_keys=[usuario_id]
    )

    # Relación inversa con sucursales (opcional pero recomendada)
    sucursales = relationship("Sucursal", backref="negocio", cascade="all, delete-orphan")

    def __repr__(self):
        return f'<Negocio {self.nombre_negocio} (ID: {self.id_negocio})>'

    def serialize(self):
        """Retorna el objeto en formato diccionario para la API"""
        try:
            nombre_ciudad = self.ciudad.ciudad_nombre if self.ciudad else "No asignada"
        except Exception:
            nombre_ciudad = "Error al cargar ciudad"

        return {
            "id": self.id_negocio, # Mantenemos la llave "id" para el JSON del frontend
            "id_negocio": self.id_negocio,
            "nombre_negocio": self.nombre_negocio,
            "descripcion": self.descripcion,
            "direccion": self.direccion,
            "telefono": self.telefono,
            "categoria": self.categoria,
            "ciudad_id": self.ciudad_id,
            "nombre_ciudad": nombre_ciudad,
            "fecha_registro": self.fecha_registro.strftime('%Y-%m-%d') if self.fecha_registro else None
        }