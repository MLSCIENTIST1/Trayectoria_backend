"""
TuKomercio — Configuración editable de gamificación (Admin Panel A6)
Tabla: gamif_config  (clave -> valor JSONB)

Patrón "constante → BD con fallback": las constantes de gamificación
(XP por evento, etc.) viven aquí como DEFAULT y pueden sobreescribirse desde
el panel de admin SIN tocar código ni redesplegar. Si la BD no tiene override
o falla, se usa el DEFAULT (a prueba de fallos).
"""

from datetime import datetime
from src.models.database import db
from sqlalchemy.dialects.postgresql import JSONB


# DEFAULT canónico del XP/TuKoins por evento (antes vivía en gamificacion_hooks.XP_EVENTOS)
XP_EVENTOS_DEFAULT = {
    'venta_completada':   {'xp': 10,  'tukoins': 3},
    'producto_creado':    {'xp': 5,   'tukoins': 2},
    'tienda_publicada':   {'xp': 100, 'tukoins': 50},
    'login_diario':       {'xp': 5,   'tukoins': 1},
    'video_subido':       {'xp': 10,  'tukoins': 3},
}

# Etiquetas legibles para el panel
XP_EVENTOS_LABELS = {
    'venta_completada': 'Venta completada',
    'producto_creado':  'Producto creado',
    'tienda_publicada': 'Tienda publicada',
    'login_diario':     'Login diario',
    'video_subido':     'Video subido',
}


class GamifConfig(db.Model):
    __tablename__ = 'gamif_config'
    clave      = db.Column(db.String(50), primary_key=True)
    valor      = db.Column(JSONB, default=dict)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<GamifConfig {self.clave}>'


# ── Helpers PUROS (testeables sin DB) ────────────────────────────────

def merge_xp_eventos(override):
    """
    Combina el DEFAULT con un override (dict de BD). Función PURA.
    Solo respeta claves de eventos conocidas y sanea xp/tukoins a enteros >= 0.
    """
    out = {k: dict(v) for k, v in XP_EVENTOS_DEFAULT.items()}
    if isinstance(override, dict):
        for k, v in override.items():
            if k in out and isinstance(v, dict):
                if 'xp' in v:
                    try:
                        out[k]['xp'] = max(0, int(v['xp']))
                    except (TypeError, ValueError):
                        pass
                if 'tukoins' in v:
                    try:
                        out[k]['tukoins'] = max(0, int(v['tukoins']))
                    except (TypeError, ValueError):
                        pass
    return out


def validar_xp_eventos(payload):
    """
    Valida un payload de edición. Función PURA.
    Retorna (ok: bool, limpio: dict, error: str|None).
    """
    if not isinstance(payload, dict) or not payload:
        return False, {}, 'Payload vacío o inválido'
    limpio = {}
    for k, v in payload.items():
        if k not in XP_EVENTOS_DEFAULT:
            continue  # ignora claves desconocidas
        if not isinstance(v, dict):
            return False, {}, f'Valor inválido para {k}'
        try:
            xp = int(v.get('xp', XP_EVENTOS_DEFAULT[k]['xp']))
            tk = int(v.get('tukoins', XP_EVENTOS_DEFAULT[k]['tukoins']))
        except (TypeError, ValueError):
            return False, {}, f'xp/tukoins deben ser números en {k}'
        if xp < 0 or tk < 0:
            return False, {}, f'xp/tukoins no pueden ser negativos en {k}'
        if xp > 100000 or tk > 100000:
            return False, {}, f'valor demasiado alto en {k}'
        limpio[k] = {'xp': xp, 'tukoins': tk}
    if not limpio:
        return False, {}, 'Ningún evento válido en el payload'
    return True, limpio, None


# ── Acceso a BD (con fallback al DEFAULT) ────────────────────────────

def get_xp_eventos():
    """
    Devuelve el XP por evento efectivo (DEFAULT + override de BD).
    A prueba de fallos: ante cualquier error usa el DEFAULT.
    """
    try:
        row = GamifConfig.query.get('xp_eventos')
        return merge_xp_eventos(row.valor if row else None)
    except Exception:
        return merge_xp_eventos(None)


def set_xp_eventos(limpio, db_session=None):
    """Guarda el override de XP por evento en gamif_config. Devuelve el merge resultante."""
    sess = db_session or db.session
    row = GamifConfig.query.get('xp_eventos')
    if row:
        row.valor = limpio
        row.updated_at = datetime.utcnow()
    else:
        sess.add(GamifConfig(clave='xp_eventos', valor=limpio))
    sess.commit()
    return merge_xp_eventos(limpio)


# ═══════════════════════════════════════════════════════════════════
# MISIONES — overrides editables (A7)
# El admin puede editar nombre/descripcion/icono/xp/tukoins y activar/desactivar
# cada misión. Los pools DEFAULT viven en negocio_gamificacion; aquí se aplican
# los overrides guardados en gamif_config['misiones_override'].
# ═══════════════════════════════════════════════════════════════════

def merge_misiones(pool_default, override):
    """
    Aplica overrides a un pool de misiones. Función PURA.
    override = { codigo: {nombre?, descripcion?, icono?, xp?, tukoins?, activa?} }
    Las misiones con activa=False se EXCLUYEN del pool resultante.
    """
    override = override or {}
    out = []
    for m in pool_default:
        ov = override.get(m['codigo'])
        nm = dict(m)
        if isinstance(ov, dict):
            if ov.get('activa') is False:
                continue
            for f in ('nombre', 'descripcion', 'icono'):
                if ov.get(f) not in (None, ''):
                    nm[f] = ov[f]
            for f in ('xp', 'tukoins'):
                if f in ov:
                    try:
                        nm[f] = max(0, int(ov[f]))
                    except (TypeError, ValueError):
                        pass
        out.append(nm)
    return out


def validar_misiones_override(payload):
    """
    Valida/sanea un payload de overrides de misiones. Función PURA.
    Retorna (ok, limpio, error).
    """
    if not isinstance(payload, dict):
        return False, {}, 'Payload inválido'
    limpio = {}
    for codigo, ov in payload.items():
        if not isinstance(ov, dict):
            return False, {}, f'Valor inválido para {codigo}'
        entry = {}
        for f in ('nombre', 'descripcion', 'icono'):
            if ov.get(f) not in (None, ''):
                entry[f] = str(ov[f])[:120]
        for f in ('xp', 'tukoins'):
            if f in ov and ov[f] is not None and ov[f] != '':
                try:
                    val = int(ov[f])
                except (TypeError, ValueError):
                    return False, {}, f'{f} debe ser número en {codigo}'
                if val < 0 or val > 100000:
                    return False, {}, f'{f} fuera de rango en {codigo}'
                entry[f] = val
        if 'activa' in ov:
            entry['activa'] = bool(ov['activa'])
        if entry:
            limpio[codigo] = entry
    return True, limpio, None


def _default_pool(tipo):
    from src.models.colombia_data.ratings.negocio_gamificacion import (
        POOL_MISIONES_DIARIAS, POOL_MISIONES_SEMANALES, POOL_MISIONES_MENSUALES
    )
    return {
        'diaria':  POOL_MISIONES_DIARIAS,
        'semanal': POOL_MISIONES_SEMANALES,
        'mensual': POOL_MISIONES_MENSUALES,
    }.get(tipo, [])


def get_misiones_override():
    """Lee el override de misiones de la BD. {} si no hay o falla."""
    try:
        row = GamifConfig.query.get('misiones_override')
        return row.valor if (row and isinstance(row.valor, dict)) else {}
    except Exception:
        return {}


def get_pool(tipo):
    """Pool efectivo de misiones de un tipo (DEFAULT + overrides). A prueba de fallos."""
    try:
        return merge_misiones(_default_pool(tipo), get_misiones_override())
    except Exception:
        return _default_pool(tipo)


def set_misiones_override(limpio, db_session=None):
    """Guarda el override de misiones en gamif_config."""
    sess = db_session or db.session
    row = GamifConfig.query.get('misiones_override')
    if row:
        row.valor = limpio
        row.updated_at = datetime.utcnow()
    else:
        sess.add(GamifConfig(clave='misiones_override', valor=limpio))
    sess.commit()
    return limpio
