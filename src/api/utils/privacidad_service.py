"""
Servicio de Habeas Data / privacidad (Admin Panel — Sprint A45).

Cumplimiento Ley 1581 (Colombia): portabilidad (exportar datos), derecho al
olvido (eliminación trazable) y registro de consentimientos.

Helpers PUROS: validación del tipo de solicitud y armado del export SIN exponer
secretos (contraseñas, hashes).

© 2024-2026 Carlos Eduardo Huérfano Bermúdez. Todos los derechos reservados.
"""

TIPOS_SOLICITUD = {'export', 'eliminacion'}
ESTADOS_SOLICITUD = {'pendiente', 'completada', 'rechazada'}

# Campos que NUNCA deben salir en un export de datos personales.
CAMPOS_SENSIBLES = {
    'contrasenia', 'confirmacion_contrasenia', 'password', 'password_hash',
    'contrasena', 'hash', 'token', 'token_acceso',
}


def validar_tipo_solicitud(tipo):
    """True si el tipo de solicitud es válido. Función PURA."""
    return str(tipo or '').strip().lower() in TIPOS_SOLICITUD


def _limpiar_dict(d):
    """Quita campos sensibles de un dict. Función PURA."""
    if not isinstance(d, dict):
        return {}
    return {k: v for k, v in d.items() if k.lower() not in CAMPOS_SENSIBLES}


def construir_export_usuario(usuario, negocios=None, resenas=None, gamificacion=None, generado_en=None):
    """
    Arma el paquete de portabilidad de un usuario. Función PURA.
    NUNCA incluye contraseñas/hashes/tokens (se filtran con CAMPOS_SENSIBLES).
    """
    u = _limpiar_dict(usuario or {})
    consentimiento = {
        'acepto_terminos': (usuario or {}).get('acepto_terminos'),
        'fecha_aceptacion_terminos': (usuario or {}).get('fecha_aceptacion_terminos'),
    }
    return {
        'generado_en': generado_en,
        'ley': 'Ley 1581 de 2012 (Habeas Data, Colombia)',
        'usuario': u,
        'consentimiento': consentimiento,
        'negocios': [_limpiar_dict(n) for n in (negocios or [])],
        'resenas': [_limpiar_dict(r) for r in (resenas or [])],
        'gamificacion': _limpiar_dict(gamificacion or {}),
    }
