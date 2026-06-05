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
# INSIGNIAS (A15) — validación para el CRUD del catálogo (tabla negocio_badges)
# ═══════════════════════════════════════════════════════════════════
OPERADORES_CRITERIO = {'>=', '<=', '==', '>', '<', '!='}
TIERS_BADGE = {1: 'Bronce', 2: 'Plata', 3: 'Oro', 4: 'Platino', 5: 'Diamante'}

# A16: catálogo de métricas disponibles para el criterio de una insignia (key → etiqueta legible).
# Las claves deben existir en BadgeVerificationService._calcular_metricas_para_badges.
METRICAS_CRITERIO = [
    {'key': 'pedidos_completados',   'label': 'Pedidos entregados'},
    {'key': 'ventas_cop',            'label': 'Ventas acumuladas (COP)'},
    {'key': 'productos_activos',     'label': 'Productos activos'},
    {'key': 'pedidos_sin_devolucion','label': 'Pedidos sin devolución'},
    {'key': 'calificaciones_5',      'label': 'Calificaciones de 5★'},
    {'key': 'trabajos_perfectos',    'label': 'Trabajos perfectos (5★)'},
    {'key': 'contratos_completados', 'label': 'Contratos completados'},
    {'key': 'clientes_recurrentes',  'label': 'Clientes recurrentes'},
    {'key': 'entregas_anticipadas',  'label': 'Entregas anticipadas'},
    {'key': 'resenas_recibidas',     'label': 'Reseñas recibidas'},
    {'key': 'visitas_tienda',        'label': 'Visitas a la tienda'},
    {'key': 'videos_subidos',        'label': 'Videos subidos'},
    {'key': 'referidos_exitosos',    'label': 'Referidos exitosos'},
    {'key': 'duelos_ganados',        'label': 'Duelos ganados'},
    {'key': 'votos_emitidos_owner',  'label': 'Votos emitidos'},
    {'key': 'dias_registrado_owner', 'label': 'Días registrado'},
    {'key': 'negocios_del_owner',    'label': 'Negocios del dueño'},
    {'key': 'max_pedidos_dia',       'label': 'Máx. pedidos en un día'},
    {'key': 'onboarding_completado', 'label': 'Onboarding completado (1/0)'},
    {'key': 'es_fundador',           'label': 'Es fundador (1/0)'},
    {'key': 'verificado',            'label': 'Negocio verificado (1/0)'},
    {'key': 'perfil_completo',       'label': 'Perfil completo (1/0)'},
    {'key': 'tiene_whatsapp',        'label': 'Tiene WhatsApp (1/0)'},
    {'key': 'tiene_direccion',       'label': 'Tiene dirección (1/0)'},
    {'key': 'orden_registro',        'label': 'Orden de registro (nº)'},
    {'key': 'ventas_fin_semana',     'label': 'Ventas en fin de semana'},
    {'key': 'ventas_madrugada',      'label': 'Ventas de madrugada'},
    {'key': 'ventas_aniversario',    'label': 'Ventas en aniversario'},
]
METRICAS_CRITERIO_KEYS = {m['key'] for m in METRICAS_CRITERIO}

# Dirección de dificultad según operador: True = "más valor es más difícil" (>=, >),
# False = "menos valor es más difícil" (<=, <). None = no evaluable (==, !=).
def _direccion_dificultad(operador):
    if operador in ('>=', '>'):
        return True
    if operador in ('<=', '<'):
        return False
    return None


def evaluar_coherencia_tier(nivel, criterio_tipo, operador, valor, otros):
    """
    A18: avisa (no bloquea) si la dificultad rompe la monotonicidad por tier
    entre insignias de la MISMA métrica. Función PURA.
    `otros`: lista de dicts {nivel, criterio_valor, nombre, criterio_operador}.
    Retorna lista de advertencias (strings). Vacía = coherente.
    """
    adv = []
    dir_self = _direccion_dificultad(operador)
    if dir_self is None:
        return adv
    try:
        nivel = int(nivel); valor = float(valor)
    except (TypeError, ValueError):
        return adv
    for o in (otros or []):
        if o.get('criterio_tipo', criterio_tipo) != criterio_tipo:
            continue
        if _direccion_dificultad(o.get('criterio_operador', operador)) != dir_self:
            continue
        try:
            o_nivel = int(o.get('nivel')); o_valor = float(o.get('criterio_valor'))
        except (TypeError, ValueError):
            continue
        if o_nivel == nivel:
            continue
        nombre = o.get('nombre', f'tier {o_nivel}')
        if dir_self:  # más es más difícil → tier mayor debe exigir más
            if o_nivel < nivel and o_valor > valor:
                adv.append(f'«{nombre}» (tier {o_nivel}) exige {o_valor:g}, MÁS que este tier {nivel} ({valor:g}).')
            elif o_nivel > nivel and o_valor < valor:
                adv.append(f'«{nombre}» (tier {o_nivel}) exige {o_valor:g}, MENOS que este tier {nivel} ({valor:g}).')
        else:  # menos es más difícil → tier mayor debe exigir menos
            if o_nivel < nivel and o_valor < valor:
                adv.append(f'«{nombre}» (tier {o_nivel}) exige {o_valor:g}, más difícil que este tier {nivel} ({valor:g}).')
            elif o_nivel > nivel and o_valor > valor:
                adv.append(f'«{nombre}» (tier {o_nivel}) exige {o_valor:g}, más fácil que este tier {nivel} ({valor:g}).')
    return adv


def badge_vigente(inicio, fin, hoy):
    """
    A19: ¿el badge está dentro de su ventana de vigencia? Función PURA.
    inicio/fin son date|None; None = sin límite por ese lado. hoy es date.
    Sin ventana (ambos None) → siempre vigente.
    """
    if inicio is not None and hoy < inicio:
        return False
    if fin is not None and hoy > fin:
        return False
    return True


def _parse_fecha(v):
    """Parsea 'YYYY-MM-DD' (o date) → date | None. Función auxiliar."""
    from datetime import date as _date, datetime as _dt
    if v in (None, ''):
        return None
    if isinstance(v, _date):
        return v
    try:
        return _dt.strptime(str(v)[:10], '%Y-%m-%d').date()
    except (TypeError, ValueError):
        return 'ERROR'


def validar_badge(payload, requerir_codigo=False):
    """
    Valida/sanea un badge del catálogo. Función PURA. (ok, limpio, error).
    En creación (requerir_codigo=True) exige codigo, nombre y criterio.
    """
    if not isinstance(payload, dict):
        return False, {}, 'Payload inválido'
    limpio = {}

    if requerir_codigo:
        import re as _re
        codigo = _re.sub(r'[^a-z0-9_]', '', str(payload.get('codigo', '')).strip().lower().replace(' ', '_'))
        if not codigo:
            return False, {}, 'El código es obligatorio (solo letras, números y _)'
        if len(codigo) > 50:
            return False, {}, 'Código demasiado largo (máx 50)'
        limpio['codigo'] = codigo

    if 'nombre' in payload or requerir_codigo:
        nombre = str(payload.get('nombre', '')).strip()
        if requerir_codigo and not nombre:
            return False, {}, 'El nombre es obligatorio'
        if nombre:
            limpio['nombre'] = nombre[:100]

    # Criterio (obligatorio al crear; opcional al editar)
    if 'criterio_tipo' in payload or requerir_codigo:
        ctipo = str(payload.get('criterio_tipo', '')).strip()
        if requerir_codigo and not ctipo:
            return False, {}, 'El criterio (criterio_tipo) es obligatorio'
        if ctipo:
            limpio['criterio_tipo'] = ctipo[:50]
    if 'criterio_valor' in payload or requerir_codigo:
        try:
            limpio['criterio_valor'] = float(payload.get('criterio_valor', 0))
        except (TypeError, ValueError):
            return False, {}, 'criterio_valor debe ser numérico'
    if 'criterio_operador' in payload and payload['criterio_operador']:
        op = str(payload['criterio_operador']).strip()
        if op not in OPERADORES_CRITERIO:
            return False, {}, f'Operador inválido (usa: {", ".join(sorted(OPERADORES_CRITERIO))})'
        limpio['criterio_operador'] = op
    elif requerir_codigo:
        limpio['criterio_operador'] = '>='

    if 'nivel' in payload:
        try:
            niv = int(payload['nivel'])
        except (TypeError, ValueError):
            return False, {}, 'nivel debe ser un número'
        if niv not in TIERS_BADGE:
            return False, {}, 'nivel (tier) debe estar entre 1 y 5'
        limpio['nivel'] = niv
    if 'puntos' in payload:
        try:
            pts = int(payload['puntos'])
        except (TypeError, ValueError):
            return False, {}, 'puntos debe ser un número'
        if pts < 0 or pts > 100000:
            return False, {}, 'puntos fuera de rango'
        limpio['puntos'] = pts
    if 'orden' in payload and payload['orden'] != '':
        try:
            limpio['orden'] = int(payload['orden'])
        except (TypeError, ValueError):
            return False, {}, 'orden debe ser un número'
    if 'max_otorgamientos' in payload:
        mo = payload['max_otorgamientos']
        if mo in (None, ''):
            limpio['max_otorgamientos'] = None
        else:
            try:
                limpio['max_otorgamientos'] = max(1, int(mo))
            except (TypeError, ValueError):
                return False, {}, 'max_otorgamientos debe ser un número o vacío'

    # A-SEC-1 (XSS): validar color/ícono estrictos (no confiar en lo que llega del panel)
    from src.api.utils.seguridad import color_hex_valido, color_css_valido, icono_valido
    if 'color_primario' in payload and payload['color_primario'] not in (None, ''):
        if not color_hex_valido(payload['color_primario']):
            return False, {}, 'color_primario debe ser un hex válido (#rrggbb)'
        limpio['color_primario'] = str(payload['color_primario']).strip()
    if 'color_fondo' in payload and payload['color_fondo'] not in (None, ''):
        if not color_css_valido(payload['color_fondo']):
            return False, {}, 'color_fondo debe ser hex o rgba() válido'
        limpio['color_fondo'] = str(payload['color_fondo']).strip()
    if 'icono' in payload and payload['icono'] not in (None, ''):
        if not icono_valido(payload['icono']):
            return False, {}, 'ícono inválido (usa una clase bi-... o un emoji)'
        limpio['icono'] = str(payload['icono']).strip()

    for campo, maxlen in (('descripcion', 255), ('gradiente', 200), ('categoria', 50),
                          ('imagen_url', 500)):
        if campo in payload and payload[campo] is not None:
            limpio[campo] = str(payload[campo])[:maxlen]
    for campo in ('activo', 'es_secreto', 'es_exclusivo', 'visible_en_catalogo'):
        if campo in payload:
            limpio[campo] = bool(payload[campo])

    # A19: ventana de vigencia (temporada/evento)
    for campo in ('vigencia_inicio', 'vigencia_fin'):
        if campo in payload:
            f = _parse_fecha(payload[campo])
            if f == 'ERROR':
                return False, {}, f'{campo} debe ser una fecha válida (YYYY-MM-DD) o vacío'
            limpio[campo] = f   # date | None
    if (limpio.get('vigencia_inicio') and limpio.get('vigencia_fin')
            and limpio['vigencia_inicio'] > limpio['vigencia_fin']):
        return False, {}, 'La vigencia de inicio no puede ser posterior a la de fin'

    if not limpio:
        return False, {}, 'Nada que guardar'
    return True, limpio, None


# ═══════════════════════════════════════════════════════════════════
# SUGERENCIAS / COMPARATIVAS (A12) — parámetros configurables
# ═══════════════════════════════════════════════════════════════════
SUGERENCIAS_DEFAULT = {
    'umbral_casi': 70,        # % de progreso para "¡vas casi!" + prioridad alta
    'umbral_avance': 40,      # % para "¡buen avance!"
    'racha_minima': 2,        # días de racha para mostrar el aviso "no rompas tu racha"
    'max_sugerencias': 3,     # cuántas sugerencias mostrar
    'badges_considerar': 2,   # cuántos badges próximos convertir en sugerencia
    'destacado_top_pct': 10,  # comparativas: top X% se considera "destacado"
}


def validar_sugerencias_config(payload):
    """Valida la config de sugerencias/comparativas. Función PURA. (ok, limpio, error)."""
    if not isinstance(payload, dict):
        return False, {}, 'Payload inválido'
    limpio = dict(SUGERENCIAS_DEFAULT)
    rangos = {
        'umbral_casi': (1, 100), 'umbral_avance': (0, 100), 'racha_minima': (1, 60),
        'max_sugerencias': (1, 10), 'badges_considerar': (1, 10), 'destacado_top_pct': (1, 100),
    }
    for k, (lo, hi) in rangos.items():
        if k in payload and payload[k] is not None and payload[k] != '':
            try:
                v = int(payload[k])
            except (TypeError, ValueError):
                return False, {}, f'{k} debe ser un número'
            if v < lo or v > hi:
                return False, {}, f'{k} fuera de rango ({lo}-{hi})'
            limpio[k] = v
    if limpio['umbral_avance'] > limpio['umbral_casi']:
        return False, {}, 'umbral_avance no puede ser mayor que umbral_casi'
    return True, limpio, None


def get_sugerencias_config():
    """Config efectiva de sugerencias (BD + fallback al DEFAULT)."""
    try:
        row = GamifConfig.query.get('sugerencias')
        if row and isinstance(row.valor, dict):
            merged = dict(SUGERENCIAS_DEFAULT)
            merged.update(row.valor)
            return merged
    except Exception:
        pass
    return dict(SUGERENCIAS_DEFAULT)


def set_sugerencias_config(limpio, db_session=None):
    """Guarda la config de sugerencias en gamif_config."""
    sess = db_session or db.session
    row = GamifConfig.query.get('sugerencias')
    if row:
        row.valor = limpio
        row.updated_at = datetime.utcnow()
    else:
        sess.add(GamifConfig(clave='sugerencias', valor=limpio))
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
# EVENTOS ESPECIALES (A22) — ventanas de fecha con multiplicador de XP, editables
# El DEFAULT vive en negocio_gamificacion.EVENTOS_ESPECIALES; aquí el override BD.
# ═══════════════════════════════════════════════════════════════════

def evento_activo_en(lista, fecha):
    """Devuelve el evento activo en 'fecha' dentro de 'lista', o None. Función PURA."""
    for ev in (lista or []):
        try:
            if fecha.month == int(ev['mes']) and int(ev['dia_ini']) <= fecha.day <= int(ev['dia_fin']):
                return ev
        except (KeyError, TypeError, ValueError):
            continue
    return None


def validar_eventos(payload):
    """
    Valida una lista de eventos especiales. Función PURA. (ok, limpio, error).
    Cada evento: codigo, nombre, icono, mes (1-12), dia_ini/dia_fin (1-31), xp_mult (1-10).
    """
    import re as _re
    if not isinstance(payload, list):
        return False, [], 'Se espera una lista de eventos'
    limpio = []
    vistos = set()
    for i, ev in enumerate(payload):
        if not isinstance(ev, dict):
            return False, [], f'Evento #{i+1} inválido'
        codigo = _re.sub(r'[^a-z0-9_]', '', str(ev.get('codigo', '')).strip().lower().replace(' ', '_'))
        nombre = str(ev.get('nombre', '')).strip()
        if not codigo or not nombre:
            return False, [], f'Evento #{i+1}: código y nombre obligatorios'
        if codigo in vistos:
            return False, [], f'Código duplicado: {codigo}'
        vistos.add(codigo)
        try:
            mes = int(ev['mes']); di = int(ev['dia_ini']); df = int(ev['dia_fin']); mult = int(ev['xp_mult'])
        except (KeyError, TypeError, ValueError):
            return False, [], f'Evento «{nombre}»: mes/días/multiplicador deben ser números'
        if not (1 <= mes <= 12):
            return False, [], f'Evento «{nombre}»: mes fuera de rango (1-12)'
        if not (1 <= di <= 31) or not (1 <= df <= 31) or di > df:
            return False, [], f'Evento «{nombre}»: rango de días inválido'
        if not (1 <= mult <= 10):
            return False, [], f'Evento «{nombre}»: multiplicador fuera de rango (1-10)'
        limpio.append({'codigo': codigo, 'nombre': nombre[:60],
                       'icono': str(ev.get('icono', '🎉'))[:8] or '🎉',
                       'mes': mes, 'dia_ini': di, 'dia_fin': df, 'xp_mult': mult})
    return True, limpio, None


def _eventos_default():
    from src.models.colombia_data.ratings.negocio_gamificacion import EVENTOS_ESPECIALES
    return EVENTOS_ESPECIALES


def get_eventos_especiales():
    """Lista efectiva de eventos (override de BD o DEFAULT). A prueba de fallos."""
    try:
        row = GamifConfig.query.get('eventos_especiales')
        if row and isinstance(row.valor, list):
            return row.valor
    except Exception:
        pass
    return _eventos_default()


def set_eventos_especiales(limpio, db_session=None):
    """Guarda la lista de eventos en gamif_config."""
    sess = db_session or db.session
    row = GamifConfig.query.get('eventos_especiales')
    if row:
        row.valor = limpio
        row.updated_at = datetime.utcnow()
    else:
        sess.add(GamifConfig(clave='eventos_especiales', valor=limpio))
    sess.commit()
    return limpio


# ═══════════════════════════════════════════════════════════════════
# RETOS MENSUALES (A23) — pool editable + programación por mes
# El DEFAULT vive en gamificacion_api.RETOS_MENSUALES; aquí el override BD.
# La métrica DEBE estar soportada por _ranking_por_metrica (si no, el ranking sale vacío/erróneo).
# ═══════════════════════════════════════════════════════════════════

# Métricas válidas (las que sabe calcular _ranking_por_metrica) → etiqueta para el panel
METRICAS_RETO = {
    'ventas_mes':        'Más ventas entregadas en el mes',
    'productos_mes':     'Más productos nuevos en el mes',
    'productos_activos': 'Catálogo activo más grande (acumulado)',
}


def seleccionar_reto(pool, programacion, hoy):
    """
    Devuelve el reto activo para 'hoy'. Función PURA.
    Si hay un reto programado para ese mes (YYYY-MM) y existe en el pool, gana;
    si no, rotación determinista sobre el pool.
    """
    if not pool:
        return None
    try:
        clave = f"{hoy.year:04d}-{hoy.month:02d}"
        cod = (programacion or {}).get(clave)
        if cod:
            for r in pool:
                if r.get('codigo') == cod:
                    return r
        idx = (hoy.year * 12 + (hoy.month - 1)) % len(pool)
        return pool[idx]
    except (AttributeError, TypeError):
        return pool[0] if pool else None


def validar_retos(payload):
    """Valida el pool de retos mensuales. PURA. (ok, limpio, error)."""
    import re as _re
    if not isinstance(payload, list):
        return False, [], 'Se espera una lista de retos'
    if not payload:
        return False, [], 'Debe haber al menos un reto'
    limpio = []
    vistos = set()
    for i, r in enumerate(payload):
        if not isinstance(r, dict):
            return False, [], f'Reto #{i+1} inválido'
        codigo = _re.sub(r'[^a-z0-9_]', '', str(r.get('codigo', '')).strip().lower().replace(' ', '_'))
        nombre = str(r.get('nombre', '')).strip()
        metrica = str(r.get('metrica', '')).strip()
        if not codigo or not nombre:
            return False, [], f'Reto #{i+1}: código y nombre obligatorios'
        if codigo in vistos:
            return False, [], f'Código duplicado: {codigo}'
        vistos.add(codigo)
        if metrica not in METRICAS_RETO:
            return False, [], f'Reto «{nombre}»: métrica inválida ({metrica or "vacía"})'
        limpio.append({
            'codigo': codigo, 'nombre': nombre[:60],
            'icono': str(r.get('icono', '🏆'))[:8] or '🏆',
            'descripcion': str(r.get('descripcion', '')).strip()[:160],
            'metrica': metrica,
            'unidad': str(r.get('unidad', '')).strip()[:20] or 'puntos',
        })
    return True, limpio, None


def validar_programacion_retos(payload, codigos_validos):
    """
    Valida el mapa de programación {YYYY-MM: codigo_reto}. PURA. (ok, limpio, error).
    Solo admite meses con formato válido y códigos presentes en el pool.
    """
    import re as _re
    if payload in (None, ''):
        return True, {}, None
    if not isinstance(payload, dict):
        return False, {}, 'La programación debe ser un objeto {mes: reto}'
    limpio = {}
    for mes, cod in payload.items():
        mes = str(mes).strip()
        if not _re.fullmatch(r'\d{4}-(0[1-9]|1[0-2])', mes):
            return False, {}, f'Mes inválido: {mes} (usa AAAA-MM)'
        cod = str(cod).strip()
        if cod not in codigos_validos:
            return False, {}, f'{mes}: el reto «{cod}» no existe en el pool'
        limpio[mes] = cod
    return True, limpio, None


def _retos_default():
    from src.api.gamificacion.gamificacion_api import RETOS_MENSUALES
    return RETOS_MENSUALES


def get_retos_mensuales():
    """Pool efectivo de retos (override BD o DEFAULT). A prueba de fallos."""
    try:
        row = GamifConfig.query.get('retos_mensuales')
        if row and isinstance(row.valor, list) and row.valor:
            return row.valor
    except Exception:
        pass
    return _retos_default()


def set_retos_mensuales(limpio, db_session=None):
    sess = db_session or db.session
    row = GamifConfig.query.get('retos_mensuales')
    if row:
        row.valor = limpio; row.updated_at = datetime.utcnow()
    else:
        sess.add(GamifConfig(clave='retos_mensuales', valor=limpio))
    sess.commit()
    return limpio


def get_programacion_retos():
    """Mapa efectivo de programación {YYYY-MM: codigo}. A prueba de fallos."""
    try:
        row = GamifConfig.query.get('retos_programacion')
        if row and isinstance(row.valor, dict):
            return row.valor
    except Exception:
        pass
    return {}


def set_programacion_retos(limpio, db_session=None):
    sess = db_session or db.session
    row = GamifConfig.query.get('retos_programacion')
    if row:
        row.valor = limpio; row.updated_at = datetime.utcnow()
    else:
        sess.add(GamifConfig(clave='retos_programacion', valor=limpio))
    sess.commit()
    return limpio


# ═══════════════════════════════════════════════════════════════════
# MODERACIÓN DE LIGAS (A24) — segmentación, anomalías y exclusiones
# Las ligas se calculan al vuelo (ranking por pedidos/mes). Aquí guardamos:
#   - configuración de segmentación/detección (gamif_config 'ligas_config')
#   - negocios vetados de las ligas por moderación (gamif_config 'ligas_excluidos')
# ═══════════════════════════════════════════════════════════════════

LIGAS_CONFIG_DEFAULT = {
    'min_participantes': 3,    # ligas con menos participantes se consideran "Nacional"
    'umbral_anomalia': 3.0,    # nº de desviaciones estándar sobre la media para marcar anomalía
}


def validar_ligas_config(payload):
    """Valida la config de ligas. PURA. (ok, limpio, error)."""
    if not isinstance(payload, dict):
        return False, {}, 'Se espera un objeto de configuración'
    limpio = dict(LIGAS_CONFIG_DEFAULT)
    try:
        if 'min_participantes' in payload and payload['min_participantes'] not in (None, ''):
            mp = int(payload['min_participantes'])
            if not (1 <= mp <= 100):
                return False, {}, 'min_participantes fuera de rango (1-100)'
            limpio['min_participantes'] = mp
        if 'umbral_anomalia' in payload and payload['umbral_anomalia'] not in (None, ''):
            ua = float(payload['umbral_anomalia'])
            if not (1.0 <= ua <= 6.0):
                return False, {}, 'umbral_anomalia fuera de rango (1.0-6.0)'
            limpio['umbral_anomalia'] = round(ua, 2)
    except (TypeError, ValueError):
        return False, {}, 'Valores numéricos inválidos'
    return True, limpio, None


def detectar_anomalias(filas, umbral=3.0):
    """
    Detecta puntajes atípicamente ALTOS (posible fraude/abuso). Función PURA.
    'filas' = [(id, ..., score)] (score en la última posición).
    Marca un negocio si su z-score = (score-media)/desv >= umbral, con n>=3 y desv>0.
    Devuelve {negocio_id: z_score_redondeado}.
    """
    scores = []
    ids = []
    for f in (filas or []):
        try:
            ids.append(f[0]); scores.append(float(f[-1] or 0))
        except (IndexError, TypeError, ValueError):
            continue
    n = len(scores)
    if n < 3:
        return {}
    media = sum(scores) / n
    var = sum((s - media) ** 2 for s in scores) / n
    desv = var ** 0.5
    if desv <= 0:
        return {}
    anomalias = {}
    for nid, s in zip(ids, scores):
        z = (s - media) / desv
        if z >= umbral:
            anomalias[nid] = round(z, 2)
    return anomalias


def get_ligas_config():
    """Config efectiva de ligas (override BD o DEFAULT). A prueba de fallos."""
    try:
        row = GamifConfig.query.get('ligas_config')
        if row and isinstance(row.valor, dict):
            cfg = dict(LIGAS_CONFIG_DEFAULT); cfg.update(row.valor)
            return cfg
    except Exception:
        pass
    return dict(LIGAS_CONFIG_DEFAULT)


def set_ligas_config(limpio, db_session=None):
    sess = db_session or db.session
    row = GamifConfig.query.get('ligas_config')
    if row:
        row.valor = limpio; row.updated_at = datetime.utcnow()
    else:
        sess.add(GamifConfig(clave='ligas_config', valor=limpio))
    sess.commit()
    return limpio


def get_negocios_excluidos_ligas():
    """Lista de IDs de negocios vetados de las ligas. A prueba de fallos → []."""
    try:
        row = GamifConfig.query.get('ligas_excluidos')
        if row and isinstance(row.valor, list):
            return [int(x) for x in row.valor if str(x).strip().lstrip('-').isdigit()]
    except Exception:
        pass
    return []


def set_negocios_excluidos_ligas(lista, db_session=None):
    sess = db_session or db.session
    limpio = sorted({int(x) for x in lista if str(x).strip().lstrip('-').isdigit()})
    row = GamifConfig.query.get('ligas_excluidos')
    if row:
        row.valor = limpio; row.updated_at = datetime.utcnow()
    else:
        sess.add(GamifConfig(clave='ligas_excluidos', valor=limpio))
    sess.commit()
    return limpio


# ═══════════════════════════════════════════════════════════════════
# RECOMPENSAS DE LIGA (A25) — premio automático al top-N de cada liga
# ═══════════════════════════════════════════════════════════════════

RECOMPENSAS_LIGA_DEFAULT = [
    {'pos': 1, 'xp': 500, 'tukoins': 200},
    {'pos': 2, 'xp': 300, 'tukoins': 120},
    {'pos': 3, 'xp': 150, 'tukoins': 60},
]


def validar_recompensas_liga(payload):
    """Valida la tabla de recompensas por posición. PURA. (ok, limpio, error)."""
    if not isinstance(payload, list):
        return False, [], 'Se espera una lista de recompensas'
    if not payload:
        return False, [], 'Debe haber al menos una posición premiada'
    limpio = []
    vistas = set()
    for i, r in enumerate(payload):
        if not isinstance(r, dict):
            return False, [], f'Recompensa #{i+1} inválida'
        try:
            pos = int(r['pos']); xp = int(r.get('xp', 0)); tk = int(r.get('tukoins', 0))
        except (KeyError, TypeError, ValueError):
            return False, [], f'Recompensa #{i+1}: pos/xp/tukoins deben ser números'
        if not (1 <= pos <= 10):
            return False, [], f'Posición fuera de rango (1-10): {pos}'
        if pos in vistas:
            return False, [], f'Posición duplicada: {pos}'
        vistas.add(pos)
        if not (0 <= xp <= 100000) or not (0 <= tk <= 100000):
            return False, [], f'Posición {pos}: XP/TuKoins fuera de rango (0-100000)'
        limpio.append({'pos': pos, 'xp': xp, 'tukoins': tk})
    limpio.sort(key=lambda x: x['pos'])
    return True, limpio, None


def recompensa_por_posicion(config, pos):
    """Devuelve {'xp','tukoins'} para la posición 'pos', o None. PURA."""
    for r in (config or []):
        try:
            if int(r['pos']) == pos:
                return {'xp': int(r.get('xp', 0)), 'tukoins': int(r.get('tukoins', 0))}
        except (KeyError, TypeError, ValueError):
            continue
    return None


def construir_plan_recompensas(filas, config, excluidos=None):
    """
    Construye el plan de premios. Función PURA.
    'filas' = [(id, nombre, ...score)] YA ordenadas desc por score.
    Los negocios vetados NO ocupan podio (se excluyen antes de asignar posición).
    Devuelve [{negocio_id, nombre, posicion, xp, tukoins}] solo para posiciones con premio>0.
    """
    veto = set(excluidos or [])
    plan = []
    pos = 0
    for f in (filas or []):
        try:
            nid = f[0]
        except (IndexError, TypeError):
            continue
        if nid in veto:
            continue
        pos += 1
        r = recompensa_por_posicion(config, pos)
        if r and (r['xp'] > 0 or r['tukoins'] > 0):
            nombre = f[1] if len(f) > 1 else ''
            plan.append({'negocio_id': nid, 'nombre': nombre, 'posicion': pos,
                         'xp': r['xp'], 'tukoins': r['tukoins']})
    return plan


def get_recompensas_liga():
    """Tabla efectiva de recompensas (override BD o DEFAULT). A prueba de fallos."""
    try:
        row = GamifConfig.query.get('recompensas_liga')
        if row and isinstance(row.valor, list) and row.valor:
            return row.valor
    except Exception:
        pass
    return [dict(r) for r in RECOMPENSAS_LIGA_DEFAULT]


def set_recompensas_liga(limpio, db_session=None):
    sess = db_session or db.session
    row = GamifConfig.query.get('recompensas_liga')
    if row:
        row.valor = limpio; row.updated_at = datetime.utcnow()
    else:
        sess.add(GamifConfig(clave='recompensas_liga', valor=limpio))
    sess.commit()
    return limpio


# ═══════════════════════════════════════════════════════════════════
# REFERIDOS (A27) — recompensas configurables + detección de fraude
# DEFAULT histórico (S29): xp_referidor=50, tukoins_referidor=30.
# ═══════════════════════════════════════════════════════════════════

REFERIDOS_CONFIG_DEFAULT = {
    'xp_referidor': 50,       # XP personal para quien refirió, al convertir
    'tukoins_referidor': 30,  # TuKoins al negocio del referidor
    'umbral_fraude': 10,      # nº de referidos que dispara revisión
    'ratio_min': 0.2,         # tasa de conversión mínima esperada (<0.2 con muchos referidos = sospechoso)
}


def validar_referidos_config(payload):
    """Valida la config de referidos. PURA. (ok, limpio, error)."""
    if not isinstance(payload, dict):
        return False, {}, 'Se espera un objeto de configuración'
    limpio = dict(REFERIDOS_CONFIG_DEFAULT)
    try:
        if payload.get('xp_referidor') not in (None, ''):
            v = int(payload['xp_referidor'])
            if not (0 <= v <= 100000):
                return False, {}, 'xp_referidor fuera de rango (0-100000)'
            limpio['xp_referidor'] = v
        if payload.get('tukoins_referidor') not in (None, ''):
            v = int(payload['tukoins_referidor'])
            if not (0 <= v <= 100000):
                return False, {}, 'tukoins_referidor fuera de rango (0-100000)'
            limpio['tukoins_referidor'] = v
        if payload.get('umbral_fraude') not in (None, ''):
            v = int(payload['umbral_fraude'])
            if not (2 <= v <= 1000):
                return False, {}, 'umbral_fraude fuera de rango (2-1000)'
            limpio['umbral_fraude'] = v
        if payload.get('ratio_min') not in (None, ''):
            v = float(payload['ratio_min'])
            if not (0.0 <= v <= 1.0):
                return False, {}, 'ratio_min fuera de rango (0.0-1.0)'
            limpio['ratio_min'] = round(v, 2)
    except (TypeError, ValueError):
        return False, {}, 'Valores numéricos inválidos'
    return True, limpio, None


def marcar_referidores_sospechosos(filas, umbral, ratio_min):
    """
    Detecta referidores con patrón de fraude. Función PURA.
    'filas' = [{'usuario_id', 'total', 'convertidos'}].
    Sospechoso si total >= umbral Y (convertidos/total) < ratio_min
    (muchos referidos pero casi ninguno convierte → posibles cuentas falsas).
    Devuelve {usuario_id: ratio_redondeado}.
    """
    sospechosos = {}
    for f in (filas or []):
        try:
            uid = f['usuario_id']; total = int(f['total']); conv = int(f['convertidos'])
        except (KeyError, TypeError, ValueError):
            continue
        if total >= umbral:
            ratio = (conv / total) if total else 0
            if ratio < ratio_min:
                sospechosos[uid] = round(ratio, 2)
    return sospechosos


def get_referidos_config():
    """Config efectiva de referidos (override BD o DEFAULT). A prueba de fallos."""
    try:
        row = GamifConfig.query.get('referidos_config')
        if row and isinstance(row.valor, dict):
            cfg = dict(REFERIDOS_CONFIG_DEFAULT); cfg.update(row.valor)
            return cfg
    except Exception:
        pass
    return dict(REFERIDOS_CONFIG_DEFAULT)


def set_referidos_config(limpio, db_session=None):
    sess = db_session or db.session
    row = GamifConfig.query.get('referidos_config')
    if row:
        row.valor = limpio; row.updated_at = datetime.utcnow()
    else:
        sess.add(GamifConfig(clave='referidos_config', valor=limpio))
    sess.commit()
    return limpio


# ═══════════════════════════════════════════════════════════════════
# CHALLENGES 2.0 (A28) — recompensas de gamificación por challenge
# Integra el sistema de challenges (video) con XP/TuKoins: premio al participar
# (cuando la participación se aprueba) y al ganar (al finalizar el challenge).
# ═══════════════════════════════════════════════════════════════════

CHALLENGE_REWARDS_DEFAULT = {
    'xp_participar':      30,
    'tukoins_participar': 15,
    'xp_ganador':         300,
    'tukoins_ganador':    150,
}


def validar_challenge_rewards(payload):
    """Valida las recompensas de challenge. PURA. (ok, limpio, error)."""
    if not isinstance(payload, dict):
        return False, {}, 'Se espera un objeto de configuración'
    limpio = dict(CHALLENGE_REWARDS_DEFAULT)
    for clave in ('xp_participar', 'tukoins_participar', 'xp_ganador', 'tukoins_ganador'):
        if payload.get(clave) in (None, ''):
            continue
        try:
            v = int(payload[clave])
        except (TypeError, ValueError):
            return False, {}, f'{clave} debe ser un número'
        if not (0 <= v <= 100000):
            return False, {}, f'{clave} fuera de rango (0-100000)'
        limpio[clave] = v
    return True, limpio, None


def get_challenge_rewards():
    """Recompensas efectivas de challenge (override BD o DEFAULT). A prueba de fallos."""
    try:
        row = GamifConfig.query.get('challenge_rewards')
        if row and isinstance(row.valor, dict):
            cfg = dict(CHALLENGE_REWARDS_DEFAULT); cfg.update(row.valor)
            return cfg
    except Exception:
        pass
    return dict(CHALLENGE_REWARDS_DEFAULT)


def set_challenge_rewards(limpio, db_session=None):
    sess = db_session or db.session
    row = GamifConfig.query.get('challenge_rewards')
    if row:
        row.valor = limpio; row.updated_at = datetime.utcnow()
    else:
        sess.add(GamifConfig(clave='challenge_rewards', valor=limpio))
    sess.commit()
    return limpio


# ═══════════════════════════════════════════════════════════════════
# FEED DE COMUNIDAD (A32) — qué logros destacados aparecen (S32)
# ═══════════════════════════════════════════════════════════════════

FEED_COMUNIDAD_DEFAULT = {
    'nivel_minimo': 3,   # nivel de badge para aparecer en el feed (3 = Oro)
    'limite': 15,        # máximo de eventos a mostrar
}


def validar_feed_comunidad_config(payload):
    """Valida la config del feed de comunidad. PURA. (ok, limpio, error)."""
    if not isinstance(payload, dict):
        return False, {}, 'Se espera un objeto de configuración'
    limpio = dict(FEED_COMUNIDAD_DEFAULT)
    try:
        if payload.get('nivel_minimo') not in (None, ''):
            v = int(payload['nivel_minimo'])
            if not (1 <= v <= 5):
                return False, {}, 'nivel_minimo fuera de rango (1-5)'
            limpio['nivel_minimo'] = v
        if payload.get('limite') not in (None, ''):
            v = int(payload['limite'])
            if not (1 <= v <= 100):
                return False, {}, 'limite fuera de rango (1-100)'
            limpio['limite'] = v
    except (TypeError, ValueError):
        return False, {}, 'Valores numéricos inválidos'
    return True, limpio, None


def get_feed_comunidad_config():
    """Config efectiva del feed de comunidad (override BD o DEFAULT). A prueba de fallos."""
    try:
        row = GamifConfig.query.get('feed_comunidad_config')
        if row and isinstance(row.valor, dict):
            cfg = dict(FEED_COMUNIDAD_DEFAULT); cfg.update(row.valor)
            return cfg
    except Exception:
        pass
    return dict(FEED_COMUNIDAD_DEFAULT)


def set_feed_comunidad_config(limpio, db_session=None):
    sess = db_session or db.session
    row = GamifConfig.query.get('feed_comunidad_config')
    if row:
        row.valor = limpio; row.updated_at = datetime.utcnow()
    else:
        sess.add(GamifConfig(clave='feed_comunidad_config', valor=limpio))
    sess.commit()
    return limpio


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
