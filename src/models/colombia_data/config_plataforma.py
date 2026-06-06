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
