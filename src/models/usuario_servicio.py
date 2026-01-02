from sqlalchemy import Table, Column, Integer, ForeignKey
from src.models.database import db

# Tabla intermedia para la relación Usuario <-> Servicio
# Esta tabla es crucial para que el mapeador de SQLAlchemy funcione correctamente

usuario_servicio = Table(
    'usuario_servicio',
    db.Model.metadata,
    # ✅ CORRECCIÓN: Apuntar a 'usuarios' (plural) y usar nombres de columna consistentes
    Column('id_usuario', Integer, ForeignKey('usuarios.id_usuario', ondelete='CASCADE'), primary_key=True),
    Column('id_servicio', Integer, ForeignKey('servicio.id_servicio', ondelete='CASCADE'), primary_key=True),
)