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
