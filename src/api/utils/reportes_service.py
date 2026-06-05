"""
Servicio de reportes exportables (Admin Panel — Sprint A36).

Helper PURO para serializar filas a CSV (con escape correcto) y constructores de
los reportes de plataforma (crecimiento, economía de TuKoins, adopción de planes).

© 2024-2026 Carlos Eduardo Huérfano Bermúdez. Todos los derechos reservados.
"""


def _celda_csv(valor):
    """Escapa un valor para CSV. Función PURA."""
    if valor is None:
        return ''
    s = str(valor)
    if any(c in s for c in (',', '"', '\n', '\r')):
        s = '"' + s.replace('"', '""') + '"'
    return s


def a_csv(headers, filas):
    """
    Serializa a CSV. Función PURA.
    headers: lista de (clave, etiqueta). filas: lista de dicts.
    Devuelve un string CSV (con BOM para que Excel respete acentos/UTF-8).
    """
    claves = [h[0] for h in headers]
    etiquetas = [h[1] for h in headers]
    lineas = [','.join(_celda_csv(e) for e in etiquetas)]
    for fila in (filas or []):
        lineas.append(','.join(_celda_csv((fila or {}).get(k, '')) for k in claves))
    return '﻿' + '\r\n'.join(lineas)
