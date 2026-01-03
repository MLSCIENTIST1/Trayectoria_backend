from src.models.database import db
from datetime import datetime
import sqlalchemy as sa
from sqlalchemy.orm import relationship

class Producto(db.Model):
    """
    Representa un item individual dentro del catálogo de un negocio en BizFlow Studio.
    Vinculado jerárquicamente a Usuario -> Negocio -> Sucursal para garantizar
    que los datos pertenezcan únicamente al creador.
    """
    __tablename__ = 'productos_catalogo'

    # 1. Identificadores Únicos
    id_producto = sa.Column(sa.Integer, primary_key=True)
    
    # 2. Detalles Visuales y de Marketing (Para Rodar.html)
    nombre = sa.Column(sa.String(150), nullable=False)
    descripcion = sa.Column(sa.Text, nullable=True)
    referencia_sku = sa.Column(sa.String(50), nullable=True) # Código interno o código de barras
    
    # 3. Precios y Moneda
    # Se usa String para soportar formatos regionales como "$ 130.000" o "130.000 COP"
    precio = sa.Column(sa.String(50), nullable=False)
    precio_oferta = sa.Column(sa.String(50), nullable=True)
    
    # 4. Multimedia y Organización
    imagen_url = sa.Column(sa.String(255), nullable=True, default='../../assets/css/electromechanics/imgs/blog-1.jpg')
    categoria = sa.Column(sa.String(100), nullable=True) 
    etiquetas = sa.Column(sa.String(255), nullable=True) # Ej: 'nuevo, recomendado, descuento'
    
    # 5. Control de Inventario y Visibilidad
    stock_disponible = sa.Column(sa.Integer, default=0)
    estado_publicacion = sa.Column(sa.Boolean, default=True) # Define si aparece o no en la web pública
    fecha_registro = sa.Column(sa.DateTime, default=datetime.utcnow)

    # 6. LLAVES FORÁNEAS (Multi-Tenancy)
    # Estas llaves aseguran que cada producto esté "atado" a su dueño y sucursal
    usuario_id = sa.Column(sa.Integer, sa.ForeignKey('usuarios.id_usuario', ondelete='CASCADE'), nullable=False)
    negocio_id = sa.Column(sa.Integer, sa.ForeignKey('negocios.id_negocio', ondelete='CASCADE'), nullable=False)
    sucursal_id = sa.Column(sa.Integer, sa.ForeignKey('sucursales.id_sucursal', ondelete='CASCADE'), nullable=False)

    # 7. RELACIONES
    # back_populates es más robusto para sistemas con muchas relaciones como el tuyo
    dueno = relationship("Usuario", backref="productos_creados")
    negocio_rel = relationship("Negocio", backref="productos_del_negocio")
    sucursal_rel = relationship("Sucursal", backref="inventario_por_sucursal")

    def __init__(self, **kwargs):
        """Constructor flexible para creación rápida desde la API"""
        super(Producto, self).__init__(**kwargs)

    def serialize(self):
        """
        Retorna un diccionario limpio para la API de BizFlow y el catálogo.
        Mapea 'imagen_url' a 'img' para mantener compatibilidad con tu frontend actual.
        """
        return {
            "id": self.id_producto,
            "nombre": self.nombre,
            "descripcion": self.descripcion,
            "precio": self.precio,
            "precio_oferta": self.precio_oferta,
            "img": self.imagen_url,
            "categoria": self.categoria,
            "stock": self.stock_disponible,
            "activo": self.estado_publicacion,
            "negocio_id": self.negocio_id,
            "sucursal_id": self.sucursal_id,
            "sku": self.referencia_sku,
            "fecha": self.fecha_registro.strftime('%Y-%m-%d')
        }

    def __repr__(self):
        return f'<Producto {self.nombre} | Negocio ID: {self.negocio_id} | Sucursal: {self.sucursal_id}>'