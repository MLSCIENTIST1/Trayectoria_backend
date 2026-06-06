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


def clasificar_cobro(estado_actual, dias_restantes, dias_alerta=7):
    """
    Clasifica una suscripción para gestión de cobro (dunning). Función PURA.
    Devuelve {bucket, accion, color, requiere_accion}.
      bucket: 'al_dia' | 'por_vencer' | 'en_gracia' | 'vencida' | 'cancelada' | 'pausada'
    """
    estado = (estado_actual or '').lower()
    dias = dias_restantes if isinstance(dias_restantes, int) else None

    if estado == 'cancelada':
        b, accion, color = 'cancelada', 'Cancelada — reactivar o archivar', '#94a3b8'
    elif estado == 'pausada':
        b, accion, color = 'pausada', 'Pausada — revisar', '#94a3b8'
    elif estado == 'vencida':
        b, accion, color = 'vencida', 'Vencida — cobrar o cortar acceso', '#dc2626'
    elif estado == 'gracia':
        b, accion, color = 'en_gracia', 'En gracia — cobrar urgente', '#f59e0b'
    elif estado in ('trial', 'activa') and dias is not None and dias <= dias_alerta:
        b, accion, color = 'por_vencer', f'Vence en {dias} día(s) — recordar pago', '#f59e0b'
    else:
        b, accion, color = 'al_dia', 'Al día', '#16a34a'

    return {'bucket': b, 'accion': accion, 'color': color,
            'requiere_accion': b not in ('al_dia', 'cancelada', 'pausada')}


def mascara_clave(valor):
    """Enmascara una clave para mostrarla sin exponerla. PURA. 'pk_test_abcd...wxyz' o ''."""
    if not valor or not isinstance(valor, str):
        return ''
    v = valor.strip()
    if len(v) <= 10:
        return v[:3] + '…'
    return v[:7] + '…' + v[-4:]
