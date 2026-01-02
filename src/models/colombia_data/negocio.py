import sqlalchemy as sa
from sqlalchemy.orm import relationship
from src.models.database import db
from datetime import datetime

class Negocio(db.Model):
    __tablename__ = 'negocios'

    # 1. Columnas Principales
    id = sa.Column(sa.Integer, primary_key=True)
    nombre_negocio = sa.Column(sa.String(150), nullable=False)
    descripcion = sa.Column(sa.Text, nullable=True)
    direccion = sa.Column(sa.String(255), nullable=True)
    telefono = sa.Column(sa.String(20), nullable=True)
    categoria = sa.Column(sa.String(100), nullable=True) # Aquí cae 'tipoNegocio' del HTML
    
    # 2. Claves Foráneas (Foreign Keys)
    # Vinculamos con 'colombia.ciudad_id' (asegúrate que el modelo Colombia tenga ese nombre)
    ciudad_id = sa.Column(sa.Integer, sa.ForeignKey('colombia.ciudad_id'), nullable=False)
    
    # Vinculamos con 'usuarios.id_usuario' según tu modelo de Usuario
    usuario_id = sa.Column(sa.Integer, sa.ForeignKey('usuarios.id_usuario'), nullable=False)
    
    fecha_registro = sa.Column(sa.DateTime, default=datetime.utcnow)

    # 3. Relaciones (Relationships)
    # Usamos backref para acceder a los negocios desde una ciudad: ciudad.negocios
    ciudad = relationship("Colombia", backref="negocios_asociados")
    # Acceder desde usuario: usuario.mis_negocios
    dueno = relationship("Usuario", backref="mis_negocios")

    def __repr__(self):
        return f'<Negocio {self.nombre_negocio} (ID: {self.id})>'

    def serialize(self):
        """Retorna el objeto en formato diccionario para la API"""
        return {
            "id": self.id,
            "nombre_negocio": self.nombre_negocio,
            "descripcion": self.descripcion,
            "direccion": self.direccion,
            "telefono": self.telefono,
            "categoria": self.categoria,
            "ciudad_id": self.ciudad_id,
            "nombre_ciudad": self.ciudad.ciudad_nombre if self.ciudad else "No asignada",
            "fecha_registro": self.fecha_registro.strftime('%Y-%m-%d')
        }