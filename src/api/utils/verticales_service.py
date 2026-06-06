"""
Servicio de overview de verticales + tienda avanzada (Admin Panel — Sprint A47).

Las verticales se distinguen por negocios.tipo_pagina. Aquí solo lógica PURA de
etiquetado; las métricas se agregan en el endpoint.

© 2024-2026 Carlos Eduardo Huérfano Bermúdez. Todos los derechos reservados.
"""

VERTICALES_META = {
    'ecommerce':   {'label': 'Tienda / E-commerce', 'icono': '🛒'},
    'landing':     {'label': 'Landing / Página',    'icono': '📄'},
    'taller':      {'label': 'Taller automotriz',   'icono': '🔧'},
    'restaurante': {'label': 'Restaurante',         'icono': '🍽️'},
    'mecalink':    {'label': 'MecaLink',            'icono': '🔗'},
    'servicios':   {'label': 'Servicios',           'icono': '🛠️'},
}


def etiqueta_vertical(tipo):
    """Devuelve {tipo, label, icono} para un tipo_pagina. Función PURA."""
    t = (tipo or 'landing').strip().lower()
    meta = VERTICALES_META.get(t, {'label': t.capitalize() or 'Otro', 'icono': '🏷️'})
    return {'tipo': t, 'label': meta['label'], 'icono': meta['icono']}
