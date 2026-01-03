
from src.models.database import db
from datetime import datetime
import sqlalchemy as sa
from sqlalchemy.orm import relationship

class ProductoCatalogo(db.Model):
    __tablename__ = 'productos_catalogo'
    __table_args__ = {'extend_existing': True} 

    # Identificadores Únicos
    id_producto = sa.Column(sa.Integer, primary_key=True)

    # Información del Producto
    nombre = sa.Column(sa.String(150), nullable=False)
    descripcion = sa.Column(sa.Text, nullable=True)
    precio = sa.Column(sa.String(50), nullable=False)
    
    # Manejo de Imagen (Ruta local o URL remota)
    imagen_url = sa.Column(sa.String(500), nullable=True) 
    
    # Categorización y Estado
    categoria = sa.Column(sa.String(100), default='General')
    stock = sa.Column(sa.Integer, default=0)
    activo = sa.Column(sa.Boolean, default=True)
    estado_publicacion = sa.Column(sa.Boolean, default=True) # Usado en obtener_catalogo_publico
    fecha_creacion = sa.Column(sa.DateTime, default=datetime.utcnow)

    # Relaciones y Claves Foráneas (Multi-tenencia)
    negocio_id = sa.Column(sa.Integer, sa.ForeignKey('negocios.id_negocio', ondelete='CASCADE'), nullable=False)
    sucursal_id = sa.Column(sa.Integer, sa.ForeignKey('sucursales.id_sucursal', ondelete='CASCADE'), nullable=False)
    usuario_id = sa.Column(sa.Integer, sa.ForeignKey('usuarios.id_usuario', ondelete='CASCADE'), nullable=False)

    # Opcional: Definir relaciones para consultas inversas fáciles
    # negocio = relationship("Negocio", backref="productos")

    def to_dict(self):
        """Convierte el modelo a un diccionario para respuestas JSON (API)"""
        return {
            "id": self.id_producto,
            "nombre": self.nombre,
            "descripcion": self.descripcion,
            "precio": self.precio,
            "img": self.imagen_url,
            "categoria": self.categoria,
            "stock": self.stock,
            "activo": self.activo,
            "negocio_id": self.negocio_id,
            "sucursal_id": self.sucursal_id,
            "fecha": self.fecha_creacion.strftime('%Y-%m-%d')
        }

    def serialize(self):
        """Alias para mantener compatibilidad con nombres de métodos anteriores"""
        return self.to_dict()
