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


# ═══════════════════════════════════════════════════════════════════
# BONO DE TUKOINS POR FECHA (A9) — configurable desde el panel
# ═══════════════════════════════════════════════════════════════════
BONO_DEFAULT = {
    'activo': True,
    'dia_semana': 6,        # 0=lunes … 6=domingo
    'multiplicador': 2,
    'nombre': 'Domingo de TuKoins',
}
DIAS_SEMANA = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']


def calcular_bono(fecha, config):
    """Devuelve (multiplicador, nombre) del bono para una fecha. Función PURA."""
    cfg = config if isinstance(config, dict) else BONO_DEFAULT
    if not cfg.get('activo', True):
        return 1, None
    try:
        dia = int(cfg.get('dia_semana', 6))
        mult = int(cfg.get('multiplicador', 2))
    except (TypeError, ValueError):
        return 1, None
    if fecha.weekday() == dia and mult > 1:
        return mult, cfg.get('nombre') or 'Bono de TuKoins'
    return 1, None


def validar_bono_config(payload):
    """Valida la config del bono. Función PURA. Retorna (ok, limpio, error)."""
    if not isinstance(payload, dict):
        return False, {}, 'Payload inválido'
    try:
        dia = int(payload.get('dia_semana', BONO_DEFAULT['dia_semana']))
        mult = int(payload.get('multiplicador', BONO_DEFAULT['multiplicador']))
    except (TypeError, ValueError):
        return False, {}, 'dia_semana y multiplicador deben ser números'
    if dia < 0 or dia > 6:
        return False, {}, 'dia_semana debe estar entre 0 (lunes) y 6 (domingo)'
    if mult < 1 or mult > 10:
        return False, {}, 'multiplicador debe estar entre 1 y 10'
    limpio = {
        'activo': bool(payload.get('activo', True)),
        'dia_semana': dia,
        'multiplicador': mult,
        'nombre': str(payload.get('nombre', '') or 'Bono de TuKoins')[:60],
    }
    return True, limpio, None


def get_bono_config():
    """Lee la config del bono de la BD. Fallback a BONO_DEFAULT."""
    try:
        row = GamifConfig.query.get('bono_tukoins')
        if row and isinstance(row.valor, dict):
            merged = dict(BONO_DEFAULT)
            merged.update(row.valor)
            return merged
    except Exception:
        pass
    return dict(BONO_DEFAULT)


def set_bono_config(limpio, db_session=None):
    """Guarda la config del bono en gamif_config."""
    sess = db_session or db.session
    row = GamifConfig.query.get('bono_tukoins')
    if row:
        row.valor = limpio
        row.updated_at = datetime.utcnow()
    else:
        sess.add(GamifConfig(clave='bono_tukoins', valor=limpio))
    sess.commit()
    return limpio


# ═══════════════════════════════════════════════════════════════════
# SIMULADOR / MODO PRUEBA (A13) — dry-run, sin tocar la BD
# ═══════════════════════════════════════════════════════════════════

def nivel_por_xp(xp, niveles):
    """Calcula (nivel, nombre) para un XP dado, a partir de la tabla NIVELES. Función PURA."""
    nivel, nombre = 1, (niveles[0][2] if niveles else '')
    for xp_req, n, nom in niveles:
        if xp >= xp_req:
            nivel, nombre = n, nom
    return nivel, nombre


def simular_evento(evento, xp_inicial, xp_eventos, xp_mult, bono_mult, niveles, misiones=None):
    """
    Calcula qué otorgaría un evento con la config dada, SIN persistir nada. Función PURA.
    Replica la lógica de los hooks: el XP base del evento y el XP de misiones se multiplican por
    xp_mult (evento especial); los TuKoins de misiones se multiplican por bono_mult; los TuKoins
    base del evento NO se multiplican por el bono (igual que en el motor real).
    """
    try:
        xp_inicial = max(0, int(xp_inicial))
    except (TypeError, ValueError):
        xp_inicial = 0
    cfg = xp_eventos.get(evento, {'xp': 0, 'tukoins': 0})
    xp_evento = int(cfg.get('xp', 0)) * xp_mult
    tk_evento = int(cfg.get('tukoins', 0))

    det_mis, xp_mis, tk_mis = [], 0, 0
    for m in (misiones or []):
        mx = int(m.get('xp', 0)) * xp_mult
        mt = int(m.get('tukoins', 0)) * bono_mult
        xp_mis += mx; tk_mis += mt
        det_mis.append({'codigo': m.get('codigo'), 'nombre': m.get('nombre'),
                        'xp': mx, 'tukoins': mt})

    xp_total = xp_evento + xp_mis
    tk_total = tk_evento + tk_mis
    nivel_antes, nombre_antes = nivel_por_xp(xp_inicial, niveles)
    nivel_desp, nombre_desp = nivel_por_xp(xp_inicial + xp_total, niveles)
    return {
        'evento': evento,
        'xp_inicial': xp_inicial,
        'xp_evento': xp_evento,
        'tukoins_evento': tk_evento,
        'misiones': det_mis,
        'xp_total_otorgado': xp_total,
        'tukoins_total_otorgado': tk_total,
        'xp_mult': xp_mult,
        'bono_mult': bono_mult,
        'xp_final': xp_inicial + xp_total,
        'nivel_antes': nivel_antes,
        'nivel_despues': nivel_desp,
        'nombre_nivel_antes': nombre_antes,
        'nombre_nivel_despues': nombre_desp,
        'subio_nivel': nivel_desp > nivel_antes,
    }


# ═══════════════════════════════════════════════════════════════════
# REGLAS DE RACHAS (A11) — configurables desde el panel
# ═══════════════════════════════════════════════════════════════════
RACHAS_DEFAULT = {
    'umbral_record': 3,        # días mínimos para considerar/notificar "récord" de racha
    'tukoins_por_record': 0,   # bono de TuKoins al ALCANZAR el umbral (0 = sin bono)
}


def validar_rachas_config(payload):
    """Valida la config de rachas. Función PURA. Retorna (ok, limpio, error)."""
    if not isinstance(payload, dict):
        return False, {}, 'Payload inválido'
    try:
        umbral = int(payload.get('umbral_record', RACHAS_DEFAULT['umbral_record']))
        bono = int(payload.get('tukoins_por_record', RACHAS_DEFAULT['tukoins_por_record']))
    except (TypeError, ValueError):
        return False, {}, 'umbral_record y tukoins_por_record deben ser números'
    if umbral < 1 or umbral > 365:
        return False, {}, 'umbral_record debe estar entre 1 y 365'
    if bono < 0 or bono > 100000:
        return False, {}, 'tukoins_por_record fuera de rango'
    return True, {'umbral_record': umbral, 'tukoins_por_record': bono}, None


def get_rachas_config():
    """Config de rachas efectiva (BD + fallback al DEFAULT)."""
    try:
        row = GamifConfig.query.get('rachas')
        if row and isinstance(row.valor, dict):
            merged = dict(RACHAS_DEFAULT)
            merged.update(row.valor)
            return merged
    except Exception:
        pass
    return dict(RACHAS_DEFAULT)


def set_rachas_config(limpio, db_session=None):
    """Guarda la config de rachas en gamif_config."""
    sess = db_session or db.session
    row = GamifConfig.query.get('rachas')
    if row:
        row.valor = limpio
        row.updated_at = datetime.utcnow()
    else:
        sess.add(GamifConfig(clave='rachas', valor=limpio))
    sess.commit()
    return limpio


# ═══════════════════════════════════════════════════════════════════
# TIENDA DE ÍTEMS (A8) — la tabla tienda_items ya existe; aquí solo validación
# ═══════════════════════════════════════════════════════════════════
TIPOS_ITEM_VALIDOS = {
    'marco_logo', 'tema_color', 'banner_tienda', 'sticker',
    'badge_temporal', 'efecto_badge', 'destacado', 'otro',
}


def validar_item_tienda(payload, requerir_codigo=False):
    """
    Valida/sanea un ítem de la tienda. Función PURA.
    requerir_codigo=True para creación (codigo + nombre + precio obligatorios).
    Retorna (ok, limpio, error).
    """
    if not isinstance(payload, dict):
        return False, {}, 'Payload inválido'
    limpio = {}

    if requerir_codigo:
        codigo = str(payload.get('codigo', '')).strip().lower().replace(' ', '_')
        if not codigo:
            return False, {}, 'El código es obligatorio'
        if len(codigo) > 60:
            return False, {}, 'Código demasiado largo'
        limpio['codigo'] = codigo

    if 'nombre' in payload or requerir_codigo:
        nombre = str(payload.get('nombre', '')).strip()
        if requerir_codigo and not nombre:
            return False, {}, 'El nombre es obligatorio'
        if nombre:
            limpio['nombre'] = nombre[:100]

    if 'precio_tukoins' in payload or requerir_codigo:
        try:
            precio = int(payload.get('precio_tukoins', 0))
        except (TypeError, ValueError):
            return False, {}, 'precio_tukoins debe ser un número'
        if precio < 0 or precio > 1000000:
            return False, {}, 'precio_tukoins fuera de rango'
        limpio['precio_tukoins'] = precio

    if 'nivel_requerido' in payload:
        try:
            niv = int(payload.get('nivel_requerido', 1))
        except (TypeError, ValueError):
            return False, {}, 'nivel_requerido debe ser un número'
        if niv < 1 or niv > 100:
            return False, {}, 'nivel_requerido fuera de rango'
        limpio['nivel_requerido'] = niv

    if 'tipo' in payload and payload['tipo']:
        tipo = str(payload['tipo']).strip()
        limpio['tipo'] = tipo if tipo in TIPOS_ITEM_VALIDOS else 'otro'
    elif requerir_codigo:
        limpio['tipo'] = 'otro'

    for campo, maxlen in (('descripcion', 255), ('css_value', 5000), ('imagen_preview', 500)):
        if campo in payload and payload[campo] is not None:
            limpio[campo] = str(payload[campo])[:maxlen]
    if 'icono' in payload and payload['icono']:
        limpio['icono'] = str(payload['icono'])[:10]
    if 'activo' in payload:
        limpio['activo'] = bool(payload['activo'])

    if not limpio:
        return False, {}, 'Nada que actualizar'
    return True, limpio, None
