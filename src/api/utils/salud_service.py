"""
Servicio de salud del sistema (Admin Panel — Sprint A37).

Helper PURO para evaluar el estado general de la plataforma a partir de
indicadores (BD arriba, errores/bugs sin atender, etc.).

© 2024-2026 Carlos Eduardo Huérfano Bermúdez. Todos los derechos reservados.
"""

UMBRAL_BUGS_ATENCION = 5   # bugs 'nuevos' a partir de los cuales se marca "atención"


def evaluar_salud(d):
    """
    Evalúa el estado general. Función PURA.
    'd': {db_ok: bool, bugs_nuevos: int}.
    Devuelve {nivel: 'ok'|'atencion'|'critico', etiqueta, color}.
    """
    d = d or {}
    db_ok = d.get('db_ok', True)
    try:
        bugs_nuevos = int(d.get('bugs_nuevos', 0) or 0)
    except (TypeError, ValueError):
        bugs_nuevos = 0

    if not db_ok:
        nivel = 'critico'
    elif bugs_nuevos >= UMBRAL_BUGS_ATENCION:
        nivel = 'atencion'
    else:
        nivel = 'ok'

    meta = {
        'ok':       {'etiqueta': 'Operativo',        'color': '#16a34a'},
        'atencion': {'etiqueta': 'Requiere atención', 'color': '#f59e0b'},
        'critico':  {'etiqueta': 'Crítico',          'color': '#dc2626'},
    }[nivel]
    return {'nivel': nivel, 'etiqueta': meta['etiqueta'], 'color': meta['color'],
            'db_ok': bool(db_ok), 'bugs_nuevos': bugs_nuevos}
