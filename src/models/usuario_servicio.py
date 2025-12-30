from sqlalchemy import Table, Column, Integer, ForeignKey, String, Boolean
from src.models.database import db

# Tabla intermedia para la relación Usuario <-> Servicio


usuario_servicio = Table(
    'usuario_servicio',
    db.Model.metadata,
    Column('usuario_id', Integer, ForeignKey('usuario.id_usuario'), primary_key=True),
    Column('servicio_id', Integer, ForeignKey('servicio.id_servicio'), primary_key=True),
    
)