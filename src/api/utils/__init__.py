"""
Módulo de utilidades - TuKomercio
Contiene funciones auxiliares y de conexión a base de datos
"""

from .db import get_db_connection, close_connection, execute_query

__all__ = ['get_db_connection', 'close_connection', 'execute_query']

print("📦 Módulo utils/__init__.py cargado")