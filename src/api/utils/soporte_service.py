"""
Servicio de soporte / "ver como el usuario" (Admin Panel — Sprint A35).

Modo soporte SEGURO: en vez de suplantar la sesión del usuario (riesgoso), se
arma un snapshot de SOLO LECTURA de su negocio y se corre un diagnóstico
automático para detectar problemas comunes. Todo acceso queda auditado.

© 2024-2026 Carlos Eduardo Huérfano Bermúdez. Todos los derechos reservados.
"""


def diagnosticar_negocio(d):
    """
    Analiza el snapshot de un negocio y devuelve una lista de hallazgos.
    Función PURA. Cada hallazgo: {nivel: 'ok'|'info'|'alerta', mensaje: str}.
    'd' contiene: negocio (dict), suscripcion (dict|None), productos (int),
    pedidos (int), videos (int).
    """
    d = d or {}
    n = d.get('negocio') or {}
    s = d.get('suscripcion')
    checks = []

    def add(nivel, msg):
        checks.append({'nivel': nivel, 'mensaje': msg})

    if n.get('eliminado'):
        add('alerta', 'El negocio está en la papelera (eliminado).')
    if not n.get('activo'):
        add('alerta', 'El negocio está inactivo / en lista negra.')
    if not n.get('logo_url'):
        add('info', 'No tiene logo cargado.')
    if not n.get('tiene_pagina'):
        add('info', 'Aún no ha publicado su página/tienda.')
    if not n.get('perfil_publico'):
        add('info', 'Perfil público desactivado (no aparece en comunidad/feed).')

    if int(d.get('productos', 0) or 0) == 0:
        add('alerta', 'No tiene productos cargados.')
    if int(d.get('pedidos', 0) or 0) == 0:
        add('info', 'Aún no tiene pedidos.')

    if s is None:
        add('info', f"Sin suscripción registrada (plan {n.get('plan_key') or 'basic'}).")
    else:
        estado = str(s.get('estado') or '').lower()
        if estado in ('vencida', 'cancelada', 'expirado', 'expirada', 'pausada'):
            add('alerta', f'Suscripción {estado}.')
        if s.get('es_trial'):
            add('info', 'En periodo de prueba (trial).')

    if not checks:
        add('ok', 'Sin problemas detectados.')
    return checks
