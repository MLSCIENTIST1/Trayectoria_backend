from src.models.database import db
from datetime import datetime
from sqlalchemy.dialects.postgresql import JSON  # O usa db.JSON si usas SQLite/MySQL moderno

class Sucursal(db.Model):
    __tablename__ = 'sucursales'
    
    id_sucursal = db.Column(db.Integer, primary_key=True)
    nombre_sucursal = db.Column(db.String(100), nullable=False)
    direccion = db.Column(db.String(200))
    telefono = db.Column(db.String(20))
    ciudad = db.Column(db.String(100))
    departamento = db.Column(db.String(100))
    codigo_postal = db.Column(db.String(20))
    
    activo = db.Column(db.Boolean, default=True)
    es_principal = db.Column(db.Boolean, default=False)
    fecha_registro = db.Column(db.DateTime, default=datetime.utcnow)
    
    # --- ALMACENAMIENTO DE PERSONAL (Estructura flexible) ---
    # Almacena listas de objetos: [{"nombre": "...", "identificacion": "..."}]
    cajeros = db.Column(db.JSON, default=[])
    administradores = db.Column(db.JSON, default=[])
    
    # LLAVE FORÁNEA: Conecta con la tabla de negocios
    negocio_id = db.Column(db.Integer, db.ForeignKey('negocios.id_negocio'), nullable=False)

    def to_dict(self):
        """Convierte el objeto en un diccionario para respuestas API JSON"""
        return {
            "id": self.id_sucursal,
            "nombre_sucursal": self.nombre_sucursal,
            "direccion": self.direccion,
            "telefono": self.telefono,
            "ciudad": self.ciudad,
            "departamento": self.departamento,
            "codigo_postal": self.codigo_postal,
            "activo": self.activo,
            "es_principal": self.es_principal,
            "cajeros": self.cajeros,
            "administradores": self.administradores,
            "negocio_id": self.negocio_id,
            "fecha_registro": self.fecha_registro.isoformat() if self.fecha_registro else None
        }