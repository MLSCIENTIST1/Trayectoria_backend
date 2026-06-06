"""
Servicio del Centro de Pagos / Wompi (Admin Panel — Sprint A41).

Helper PURO para evaluar la salud de la configuración Wompi de un negocio
(claves presentes, webhook verificable, ambiente). NUNCA expone los secretos:
solo indica si están presentes.

© 2024-2026 Carlos Eduardo Huérfano Bermúdez. Todos los derechos reservados.
"""


def evaluar_config_wompi(cfg):
    """
    Evalúa la config Wompi. Función PURA. 'cfg' = dict con public_key, integrity_key,
    events_key, ambiente, activo (los valores pueden ser strings o None).
    Devuelve {estado, activo, ambiente, webhook_ok, faltantes, prod}.
      estado: 'sin_configurar' | 'incompleto' | 'ok'
    """
    cfg = cfg or {}
    has_pub = bool((cfg.get('public_key') or '').strip()) if isinstance(cfg.get('public_key'), str) else bool(cfg.get('public_key'))
    has_integ = bool((cfg.get('integrity_key') or '').strip()) if isinstance(cfg.get('integrity_key'), str) else bool(cfg.get('integrity_key'))
    has_events = bool((cfg.get('events_key') or '').strip()) if isinstance(cfg.get('events_key'), str) else bool(cfg.get('events_key'))

    faltantes = []
    if not has_pub:
        faltantes.append('public_key')
    if not has_integ:
        faltantes.append('integrity_key')
    if not has_events:
        faltantes.append('events_key')  # crítico: el webhook exige firma → sin esto rechaza todo

    if not (has_pub or has_integ or has_events):
        estado = 'sin_configurar'
    elif faltantes:
        estado = 'incompleto'
    else:
        estado = 'ok'

    ambiente = (cfg.get('ambiente') or 'test')
    return {
        'estado': estado,
        'activo': bool(cfg.get('activo')),
        'ambiente': ambiente,
        'prod': ambiente == 'prod',
        'webhook_ok': has_events,
        'faltantes': faltantes,
    }


def mascara_clave(valor):
    """Enmascara una clave para mostrarla sin exponerla. PURA. 'pk_test_abcd...wxyz' o ''."""
    if not valor or not isinstance(valor, str):
        return ''
    v = valor.strip()
    if len(v) <= 10:
        return v[:3] + '…'
    return v[:7] + '…' + v[-4:]
