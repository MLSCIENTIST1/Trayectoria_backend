from src.models.database import db
from datetime import datetime

class Sucursal(db.Model):
    __tablename__ = 'sucursales'
    
    id_sucursal = db.Column(db.Integer, primary_key=True)
    nombre_sucursal = db.Column(db.String(100), nullable=False)
    direccion = db.Column(db.String(200))
    telefono = db.Column(db.String(20))
    es_principal = db.Column(db.Boolean, default=False)
    fecha_registro = db.Column(db.DateTime, default=datetime.utcnow)
    
    # LLAVE FORÁNEA: Conecta con la tabla de negocios
    # Asegúrate de que en tu tabla Negocio la PK se llame 'id_negocio'
    negocio_id = db.Column(db.Integer, db.ForeignKey('negocios.id_negocio'), nullable=False)

    def to_dict(self):
        return {
            "id": self.id_sucursal,
            "nombre_sucursal": self.nombre_sucursal,
            "direccion": self.direccion,
            "telefono": self.telefono,
            "es_principal": self.es_principal,
            "negocio_id": self.negocio_id
        }