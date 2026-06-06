"""
Servicio de Integraciones y automatizaciones (Admin Panel — Sprint A48).

Estado de las integraciones externas (Resend, Groq/Dora, Cloudinary, Wompi) y
configuración de automatizaciones (WhatsApp post-venta). Lógica PURA aquí; el
estado real y la persistencia, en el endpoint.

© 2024-2026 Carlos Eduardo Huérfano Bermúdez. Todos los derechos reservados.
"""

TRIGGERS_POSTVENTA = {'confirmado', 'enviado', 'entregado'}

INTEGRACIONES_CONFIG_DEFAULT = {
    'whatsapp_postventa_activo': False,
    'whatsapp_postventa_trigger': 'entregado',
    'whatsapp_postventa_plantilla': '¡Hola {{cliente}}! Gracias por tu compra en {{negocio}}. '
                                    'Tu pedido {{codigo_pedido}} ya fue entregado. ¿Nos dejas una reseña? 🙌',
}


def estado_integraciones(env, wompi_activos=0):
    """
    Construye el estado de cada integración externa. Función PURA.
    'env' = dict con presencia de variables (RESEND_API_KEY, GROQ_API_KEY, ...).
    Cloudinary está embebido en el código → siempre disponible.
    """
    env = env or {}
    def _has(k):
        v = env.get(k)
        return bool(v.strip()) if isinstance(v, str) else bool(v)
    items = [
        {'clave': 'resend', 'label': 'Resend (emails)', 'configurado': _has('RESEND_API_KEY'),
         'nota': 'Correos transaccionales'},
        {'clave': 'groq', 'label': 'Groq (Dora IA)', 'configurado': _has('GROQ_API_KEY'),
         'nota': 'Asistente de IA'},
        {'clave': 'cloudinary', 'label': 'Cloudinary (imágenes/video)', 'configurado': True,
         'nota': 'Almacenamiento multimedia'},
        {'clave': 'wompi', 'label': 'Wompi (pagos)', 'configurado': int(wompi_activos or 0) > 0,
         'nota': f'{int(wompi_activos or 0)} negocio(s) con Wompi activo'},
    ]
    return items


def validar_integraciones_config(payload):
    """Valida la config de integraciones/automatizaciones. PURA. (ok, limpio, error)."""
    if not isinstance(payload, dict):
        return False, {}, 'Se espera un objeto'
    limpio = {}
    if 'whatsapp_postventa_activo' in payload:
        limpio['whatsapp_postventa_activo'] = bool(payload['whatsapp_postventa_activo'])
    if 'whatsapp_postventa_trigger' in payload and payload['whatsapp_postventa_trigger']:
        t = str(payload['whatsapp_postventa_trigger']).strip().lower()
        if t not in TRIGGERS_POSTVENTA:
            return False, {}, f"trigger inválido (usa: {', '.join(sorted(TRIGGERS_POSTVENTA))})"
        limpio['whatsapp_postventa_trigger'] = t
    if 'whatsapp_postventa_plantilla' in payload:
        p = payload['whatsapp_postventa_plantilla']
        if not isinstance(p, str):
            return False, {}, 'La plantilla debe ser texto'
        limpio['whatsapp_postventa_plantilla'] = p[:1000]
    return True, limpio, None
