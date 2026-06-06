"""
TuKomercio — Configuración global de la plataforma (Admin Panel A38)

Tabla `config_global` (clave -> valor JSONB), patrón "constante → BD con fallback".
Toggles globales (mantenimiento, registro abierto/cerrado) y textos legales/landing,
editables desde el panel SIN tocar código.

⚠️ La tabla se crea por `db.create_all()` (tiene modelo) → funciona en producción.

© 2024-2026 Carlos Eduardo Huérfano Bermúdez. Todos los derechos reservados.
"""

from datetime import datetime
from src.models.database import db
from sqlalchemy.dialects.postgresql import JSONB


class ConfigGlobal(db.Model):
    __tablename__ = 'config_global'
    clave      = db.Column(db.String(60), primary_key=True)
    valor      = db.Column(JSONB, default={})
    updated_at = db.Column(db.DateTime, default=datetime.utcnow)


# Una sola clave que guarda todo el objeto de configuración.
_CLAVE = 'plataforma'

CONFIG_GLOBAL_DEFAULT = {
    'modo_mantenimiento':   False,
    'mensaje_mantenimiento': 'Estamos haciendo mejoras. Volvemos en unos minutos. 🙏',
    'registro_abierto':     True,
    'mensaje_registro_cerrado': 'El registro de nuevas cuentas está temporalmente cerrado.',
    'texto_terminos':       '',
    'texto_privacidad':     '',
    'texto_landing_hero':   '',
}


def validar_config_global(payload):
    """Valida y normaliza la config global. PURA. (ok, limpio, error). Parcial."""
    if not isinstance(payload, dict):
        return False, {}, 'Se espera un objeto'
    limpio = {}
    for b in ('modo_mantenimiento', 'registro_abierto'):
        if b in payload:
            limpio[b] = bool(payload[b])
    for t, maxlen in (('mensaje_mantenimiento', 300), ('mensaje_registro_cerrado', 300),
                      ('texto_terminos', 50000), ('texto_privacidad', 50000),
                      ('texto_landing_hero', 2000)):
        if t in payload:
            if payload[t] is None:
                limpio[t] = ''
            elif not isinstance(payload[t], str):
                return False, {}, f'{t} debe ser texto'
            else:
                limpio[t] = payload[t][:maxlen]
    return True, limpio, None


def get_config_global():
    """Config global efectiva (override BD sobre DEFAULT). A prueba de fallos."""
    cfg = dict(CONFIG_GLOBAL_DEFAULT)
    try:
        row = ConfigGlobal.query.get(_CLAVE)
        if row and isinstance(row.valor, dict):
            cfg.update(row.valor)
    except Exception:
        pass
    return cfg


def set_config_global(limpio, db_session=None):
    """Aplica un parche parcial sobre la config global."""
    sess = db_session or db.session
    actual = dict(CONFIG_GLOBAL_DEFAULT)
    row = ConfigGlobal.query.get(_CLAVE)
    if row and isinstance(row.valor, dict):
        actual.update(row.valor)
    actual.update(limpio or {})
    if row:
        row.valor = actual
        row.updated_at = datetime.utcnow()
    else:
        sess.add(ConfigGlobal(clave=_CLAVE, valor=actual))
    sess.commit()
    return actual


# ═══════════════════════════════════════════════════════════════════
# CONFIGURACIÓN DE IA / DORA (A44) — reusa la tabla config_global (clave 'ia')
# ═══════════════════════════════════════════════════════════════════
_CLAVE_IA = 'ia'

IA_CONFIG_DEFAULT = {
    'ia_activa':        True,                    # toggle global de Dora
    'modelo':           'llama-3.1-8b-instant',  # modelo de Groq
    'max_tokens':       512,
    'limite_dia_basic':   20,                    # usos/día por plan
    'limite_dia_pro':     100,
    'limite_dia_premium': 500,
    'limite_dia_delux':   2000,
}


def validar_ia_config(payload):
    """Valida la config de IA. PURA. (ok, limpio, error). Parcial."""
    if not isinstance(payload, dict):
        return False, {}, 'Se espera un objeto'
    limpio = {}
    if 'ia_activa' in payload:
        limpio['ia_activa'] = bool(payload['ia_activa'])
    if 'modelo' in payload and payload['modelo']:
        m = str(payload['modelo']).strip()
        if not (1 <= len(m) <= 80):
            return False, {}, 'modelo inválido'
        limpio['modelo'] = m
    if 'max_tokens' in payload and payload['max_tokens'] not in (None, ''):
        try:
            v = int(payload['max_tokens'])
        except (TypeError, ValueError):
            return False, {}, 'max_tokens debe ser entero'
        if not (64 <= v <= 4096):
            return False, {}, 'max_tokens fuera de rango (64-4096)'
        limpio['max_tokens'] = v
    for k in ('limite_dia_basic', 'limite_dia_pro', 'limite_dia_premium', 'limite_dia_delux'):
        if k in payload and payload[k] not in (None, ''):
            try:
                v = int(payload[k])
            except (TypeError, ValueError):
                return False, {}, f'{k} debe ser entero'
            if not (0 <= v <= 1000000):
                return False, {}, f'{k} fuera de rango'
            limpio[k] = v
    return True, limpio, None


def get_ia_config():
    """Config IA efectiva (override BD sobre DEFAULT). A prueba de fallos."""
    cfg = dict(IA_CONFIG_DEFAULT)
    try:
        row = ConfigGlobal.query.get(_CLAVE_IA)
        if row and isinstance(row.valor, dict):
            cfg.update(row.valor)
    except Exception:
        pass
    return cfg


def set_ia_config(limpio, db_session=None):
    sess = db_session or db.session
    actual = dict(IA_CONFIG_DEFAULT)
    row = ConfigGlobal.query.get(_CLAVE_IA)
    if row and isinstance(row.valor, dict):
        actual.update(row.valor)
    actual.update(limpio or {})
    if row:
        row.valor = actual; row.updated_at = datetime.utcnow()
    else:
        sess.add(ConfigGlobal(clave=_CLAVE_IA, valor=actual))
    sess.commit()
    return actual


def limite_ia_por_plan(cfg, plan):
    """Devuelve el límite diario de IA para un plan. Función PURA."""
    cfg = cfg or {}
    plan = (plan or 'basic').strip().lower()
    mapa = {
        'basic':   cfg.get('limite_dia_basic', IA_CONFIG_DEFAULT['limite_dia_basic']),
        'pro':     cfg.get('limite_dia_pro', IA_CONFIG_DEFAULT['limite_dia_pro']),
        'premium': cfg.get('limite_dia_premium', IA_CONFIG_DEFAULT['limite_dia_premium']),
        'delux':   cfg.get('limite_dia_delux', IA_CONFIG_DEFAULT['limite_dia_delux']),
        'deluxe':  cfg.get('limite_dia_delux', IA_CONFIG_DEFAULT['limite_dia_delux']),
    }
    try:
        return int(mapa.get(plan, IA_CONFIG_DEFAULT['limite_dia_basic']))
    except (TypeError, ValueError):
        return IA_CONFIG_DEFAULT['limite_dia_basic']


def puede_usar_ia(usos_hoy, plan, cfg):
    """¿El negocio puede hacer otra petición de IA hoy? Función PURA. (permitido, limite, restantes)."""
    limite = limite_ia_por_plan(cfg, plan)
    try:
        usos = int(usos_hoy or 0)
    except (TypeError, ValueError):
        usos = 0
    restantes = max(0, limite - usos)
    return (usos < limite, limite, restantes)


# ═══════════════════════════════════════════════════════════════════
# PLANTILLAS DE EMAIL / RESEND (A46) — reusa config_global (clave 'email_plantillas')
# ═══════════════════════════════════════════════════════════════════
_CLAVE_EMAILS = 'email_plantillas'

EMAIL_PLANTILLAS_DEFAULT = {
    'recuperar_password': {
        'nombre': 'Recuperación de contraseña',
        'subject': '🔐 Restablecer contraseña - TuKomercio',
        'variables': ['nombre', 'reset_url'],
        'html': '<p>Hola {{nombre}},</p><p>Solicitaste restablecer tu contraseña. Haz clic en el botón:</p>'
                '<p><a href="{{reset_url}}">Restablecer contraseña</a></p>'
                '<p>Si no fuiste tú, ignora este correo.</p><p>— Equipo TuKomercio</p>',
    },
    'bienvenida': {
        'nombre': 'Bienvenida (nuevo registro)',
        'subject': '🎉 ¡Bienvenido a TuKomercio!',
        'variables': ['nombre'],
        'html': '<p>¡Hola {{nombre}}!</p><p>Tu cuenta en TuKomercio fue creada con éxito. '
                'Crea tu tienda y empieza a vender hoy mismo.</p><p>— Equipo TuKomercio</p>',
    },
    'confirmacion_pedido': {
        'nombre': 'Confirmación de pedido (comprador)',
        'subject': '✅ Tu pedido en {{negocio}} fue confirmado',
        'variables': ['nombre', 'negocio', 'codigo_pedido', 'total'],
        'html': '<p>Hola {{nombre}},</p><p>Tu pedido <strong>{{codigo_pedido}}</strong> en '
                '{{negocio}} por {{total}} fue confirmado. ¡Gracias por tu compra!</p>',
    },
}


def render_email(texto, variables):
    """Sustituye {{var}} / {{ var }} en una plantilla. Función PURA (sin ejecutar código)."""
    out = str(texto or '')
    for k, v in (variables or {}).items():
        val = '' if v is None else str(v)
        out = out.replace('{{' + str(k) + '}}', val).replace('{{ ' + str(k) + ' }}', val)
    return out


def validar_plantilla_email(payload):
    """Valida una plantilla (subject + html). PURA. (ok, limpio, error)."""
    if not isinstance(payload, dict):
        return False, {}, 'Se espera un objeto'
    subject = str(payload.get('subject', '')).strip()
    html = payload.get('html')
    if not subject:
        return False, {}, 'El asunto es obligatorio'
    if not isinstance(html, str) or not html.strip():
        return False, {}, 'El cuerpo (html) es obligatorio'
    if len(subject) > 200:
        return False, {}, 'Asunto demasiado largo (máx 200)'
    if len(html) > 100000:
        return False, {}, 'Cuerpo demasiado grande'
    return True, {'subject': subject[:200], 'html': html}, None


def get_email_plantillas():
    """Plantillas efectivas (override BD fusionado con DEFAULT). A prueba de fallos."""
    plantillas = {k: dict(v) for k, v in EMAIL_PLANTILLAS_DEFAULT.items()}
    try:
        row = ConfigGlobal.query.get(_CLAVE_EMAILS)
        if row and isinstance(row.valor, dict):
            for clave, ov in row.valor.items():
                base = plantillas.get(clave, {'nombre': clave, 'variables': []})
                base = dict(base)
                if isinstance(ov, dict):
                    if ov.get('subject'):
                        base['subject'] = ov['subject']
                    if ov.get('html'):
                        base['html'] = ov['html']
                    base['editada'] = True
                plantillas[clave] = base
    except Exception:
        pass
    return plantillas


def get_email_plantilla(clave):
    """Devuelve la plantilla efectiva de una clave (o None). A prueba de fallos."""
    return get_email_plantillas().get(clave)


def set_email_plantilla(clave, subject, html, db_session=None):
    sess = db_session or db.session
    row = ConfigGlobal.query.get(_CLAVE_EMAILS)
    actual = dict(row.valor) if (row and isinstance(row.valor, dict)) else {}
    actual[clave] = {'subject': subject, 'html': html}
    if row:
        row.valor = actual; row.updated_at = datetime.utcnow()
    else:
        sess.add(ConfigGlobal(clave=_CLAVE_EMAILS, valor=actual))
    sess.commit()
    return actual[clave]
