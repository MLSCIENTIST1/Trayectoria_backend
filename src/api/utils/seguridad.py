"""
TuKomercio — Helpers de seguridad transversal (A-SEC-1)
- CSRF: validación de Origin contra whitelist (la sesión usa cookie SameSite=None).
- XSS: validadores de color hex / íconos / longitud.
- Fuerza bruta: lógica pura de bloqueo + store en BD (tabla intentos_login).
- IDOR: validación de propiedad de negocio (en gamificacion_api / endpoints).

Las funciones puras son testeables sin Flask ni BD.
"""

import re
from datetime import datetime

from src.models.database import db


# ═══════════════════════════════════════════════════════════════════
# CSRF — validación de Origin
# ═══════════════════════════════════════════════════════════════════
METODOS_MUTANTES = {'POST', 'PUT', 'DELETE', 'PATCH'}

# Rutas exentas de la verificación CSRF de Origin (clientes no-navegador legítimos):
#  - webhook de Wompi (POST externo, sin Origin)
#  - health checks
RUTAS_EXENTAS_CSRF = ('/api/wompi/webhook', '/api/health')


def origen_permitido(origin, allowed):
    """¿El Origin está en la whitelist? Función PURA. None/'' → False (se rechaza)."""
    if not origin:
        return False
    return origin in (allowed or [])


def ruta_exenta_csrf(path):
    """¿La ruta está exenta de CSRF? Función PURA."""
    p = (path or '')
    return any(p == r or p.startswith(r) for r in RUTAS_EXENTAS_CSRF)


def requiere_chequeo_csrf(method, path):
    """¿Este request mutante debe pasar el chequeo de Origin? Función PURA."""
    if (method or '').upper() not in METODOS_MUTANTES:
        return False
    if ruta_exenta_csrf(path):
        return False
    return True


# ═══════════════════════════════════════════════════════════════════
# XSS — validadores de entrada
# ═══════════════════════════════════════════════════════════════════
_HEX_RE = re.compile(r'^#[0-9a-fA-F]{6}$')
_RGBA_RE = re.compile(r'^rgba?\(\s*\d{1,3}\s*,\s*\d{1,3}\s*,\s*\d{1,3}\s*(,\s*(0|1|0?\.\d+)\s*)?\)$')
_ICONO_BI_RE = re.compile(r'^bi-[a-z0-9\-]{1,40}$')


def color_hex_valido(c):
    """True si es un color hex #rrggbb válido. Función PURA."""
    return bool(c and _HEX_RE.match(str(c).strip()))


def color_css_valido(c):
    """True si es hex o rgba() válido (para color_fondo). Función PURA."""
    s = str(c or '').strip()
    return bool(_HEX_RE.match(s) or _RGBA_RE.match(s))


def icono_valido(i):
    """
    True si es un ícono seguro: clase Bootstrap 'bi-...' o 1-2 emojis/caracteres cortos.
    Evita inyección (sin '<', '>', comillas). Función PURA.
    """
    s = str(i or '').strip()
    if not s or len(s) > 50:
        return False
    if _ICONO_BI_RE.match(s):
        return True
    # emoji / símbolo corto sin caracteres peligrosos
    return len(s) <= 8 and not re.search(r'[<>"\'`/\\]', s)


def texto_limpio(s, maxlen):
    """Recorta y quita caracteres de control. Función PURA. (El escape de HTML va en el front.)"""
    s = '' if s is None else str(s)
    s = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f]', '', s)
    return s[:maxlen]


# ═══════════════════════════════════════════════════════════════════
# FUERZA BRUTA — lógica pura de bloqueo
# ═══════════════════════════════════════════════════════════════════
UMBRAL_INTENTOS = 5
VENTANA_SEG = 15 * 60   # 15 minutos


def evaluar_bloqueo(intentos, primer_intento_ts, ahora_ts, umbral=UMBRAL_INTENTOS, ventana=VENTANA_SEG):
    """
    Decide si una clave (IP+email) está bloqueada. Función PURA.
    - Si pasó la ventana desde el primer intento → la cuenta se reinicia (no bloqueado).
    - Si intentos >= umbral dentro de la ventana → bloqueado, con segundos restantes.
    Retorna (bloqueado: bool, restante_seg: int, reiniciar: bool).
    """
    if not intentos or primer_intento_ts is None:
        return False, 0, False
    transcurrido = ahora_ts - primer_intento_ts
    if transcurrido >= ventana:
        return False, 0, True   # ventana expirada → reiniciar contador
    if intentos >= umbral:
        return True, int(ventana - transcurrido), False
    return False, 0, False


# ═══════════════════════════════════════════════════════════════════
# FUERZA BRUTA — store en BD (cross-worker, persistente)
# ═══════════════════════════════════════════════════════════════════
class IntentoLogin(db.Model):
    __tablename__ = 'intentos_login'
    clave        = db.Column(db.String(160), primary_key=True)   # "ip|email"
    intentos     = db.Column(db.Integer, default=0, nullable=False)
    primer_ts    = db.Column(db.Float, nullable=True)            # epoch del primer intento de la ventana
    updated_at   = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


def _clave(ip, email):
    return f"{(ip or '?')[:60]}|{(email or '?')[:90]}".lower()


def esta_bloqueado(ip, email, ahora_ts):
    """Consulta la BD y evalúa bloqueo. (bloqueado, restante_seg). A prueba de fallos → no bloquea si falla."""
    try:
        row = IntentoLogin.query.get(_clave(ip, email))
        if not row:
            return False, 0
        bloq, restante, reiniciar = evaluar_bloqueo(row.intentos, row.primer_ts, ahora_ts)
        if reiniciar:
            row.intentos = 0
            row.primer_ts = None
            db.session.commit()
        return bloq, restante
    except Exception:
        try:
            db.session.rollback()
        except Exception:
            pass
        return False, 0


def registrar_fallo(ip, email, ahora_ts):
    """Suma un intento fallido. Devuelve el número de intentos en la ventana actual."""
    try:
        clave = _clave(ip, email)
        row = IntentoLogin.query.get(clave)
        if not row:
            row = IntentoLogin(clave=clave, intentos=0, primer_ts=ahora_ts)
            db.session.add(row)
        # Reinicia la ventana si expiró
        if row.primer_ts is None or (ahora_ts - row.primer_ts) >= VENTANA_SEG:
            row.primer_ts = ahora_ts
            row.intentos = 0
        row.intentos += 1
        db.session.commit()
        return row.intentos
    except Exception:
        try:
            db.session.rollback()
        except Exception:
            pass
        return 0


def limpiar_intentos(ip, email):
    """Reinicia el contador tras un login exitoso."""
    try:
        row = IntentoLogin.query.get(_clave(ip, email))
        if row:
            row.intentos = 0
            row.primer_ts = None
            db.session.commit()
    except Exception:
        try:
            db.session.rollback()
        except Exception:
            pass


def registrar_evento_seguridad(accion, entidad, detalle=None, ip=None, email=None):
    """
    Inserta un evento en admin_audit_log SIN requerir g.admin (actor 'sistema').
    Para lockouts de login/reset. A prueba de fallos (conexión propia).
    """
    try:
        import os, json as _json, psycopg2
        url = os.environ.get('DATABASE_URL')
        if not url:
            return
        conn = psycopg2.connect(url)
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO admin_audit_log
                (admin_id, admin_email, accion, entidad, entidad_id, detalle, ip, created_at)
            VALUES (NULL, %s, %s, %s, %s, %s, %s, NOW())
        """, (email or 'sistema', accion, entidad, None,
              _json.dumps(detalle or {}), (ip or '')[:64]))
        conn.commit()
        cur.close()
        conn.close()
    except Exception:
        pass
