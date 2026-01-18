"""
Módulo de Tiendas Online - TuKomercio
Contiene APIs para checkout y gestión de pedidos de tiendas online
"""

from .checkout_api import checkout_api_bp

__all__ = ['checkout_api_bp']

print("📦 Módulo tiendas/__init__.py cargado correctamente")