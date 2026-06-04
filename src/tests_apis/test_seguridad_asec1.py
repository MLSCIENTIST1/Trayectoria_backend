"""
Test del sprint de seguridad transversal (A-SEC-1):
CSRF (Origin), XSS (validadores), fuerza bruta (lógica de bloqueo), IDOR (ownership).

Ejecutar:
    PYTHONUTF8=1 venv/Scripts/python.exe src/tests_apis/test_seguridad_asec1.py
"""
import os
import sys
import inspect
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

PASS = 0; FAIL = 0
def check(n, c):
    global PASS, FAIL
    if c: PASS += 1; print(f"  ✅ {n}")
    else: FAIL += 1; print(f"  ❌ {n}")


def main():
    from src.api.utils import seguridad as S

    ALLOWED = ['https://tukomercio.co', 'https://tuko.pages.dev', 'http://localhost:5173']

    print("\n[1] CSRF — origen_permitido")
    check("origen en whitelist → True", S.origen_permitido('https://tukomercio.co', ALLOWED))
    check("origen ajeno → False", S.origen_permitido('https://evil.com', ALLOWED) is False)
    check("sin origin → False (se rechaza)", S.origen_permitido('', ALLOWED) is False)
    check("None → False", S.origen_permitido(None, ALLOWED) is False)

    print("\n[2] CSRF — requiere_chequeo_csrf / exenciones")
    check("POST normal → requiere chequeo", S.requiere_chequeo_csrf('POST', '/api/gamificacion/dashboard'))
    check("GET → no requiere", S.requiere_chequeo_csrf('GET', '/api/x') is False)
    check("OPTIONS → no requiere", S.requiere_chequeo_csrf('OPTIONS', '/api/x') is False)
    check("webhook Wompi exento", S.requiere_chequeo_csrf('POST', '/api/wompi/webhook') is False)
    check("PUT/DELETE/PATCH requieren", all(S.requiere_chequeo_csrf(m, '/api/x') for m in ('PUT','DELETE','PATCH')))

    print("\n[3] XSS — validadores")
    check("hex válido", S.color_hex_valido('#a855f7'))
    check("hex inválido (texto)", S.color_hex_valido('red') is False)
    check("hex con inyección → False", S.color_hex_valido('#fff;</style><script>') is False)
    check("rgba válido", S.color_css_valido('rgba(245,158,11,0.15)'))
    check("ícono bi- válido", S.icono_valido('bi-award-fill'))
    check("ícono emoji válido", S.icono_valido('🏆'))
    check("ícono con < → False", S.icono_valido('<img src=x>') is False)
    check("texto_limpio recorta", len(S.texto_limpio('x'*100, 10)) == 10)
    check("texto_limpio quita control chars", '\x00' not in S.texto_limpio('a\x00b', 50))

    print("\n[4] Fuerza bruta — evaluar_bloqueo")
    bloq, rest, rei = S.evaluar_bloqueo(5, 1000.0, 1100.0)  # 5 intentos, 100s después
    check("5 intentos dentro de ventana → bloqueado", bloq is True and rest > 0)
    bloq2, _, _ = S.evaluar_bloqueo(4, 1000.0, 1100.0)
    check("4 intentos → no bloqueado", bloq2 is False)
    bloq3, _, rei3 = S.evaluar_bloqueo(5, 1000.0, 1000.0 + S.VENTANA_SEG + 1)
    check("ventana expirada → reinicia (no bloqueado)", bloq3 is False and rei3 is True)
    check("sin intentos → no bloqueado", S.evaluar_bloqueo(0, None, 1000.0)[0] is False)

    print("\n[5] XSS backend — validar_badge rechaza color/ícono peligrosos")
    from src.models.colombia_data.ratings.config_gamificacion import validar_badge
    check("color con inyección → inválido",
          validar_badge({'color_primario': '#fff"><script>'})[0] is False)
    check("color hex válido → ok", validar_badge({'color_primario': '#a855f7'})[0] is True)
    check("ícono con HTML → inválido", validar_badge({'icono': '<img onerror=x>'})[0] is False)

    print("\n[6] IDOR — _get_nid exige propiedad")
    from src.api.gamificacion import gamificacion_api as G
    src = inspect.getsource(G._get_nid)
    check("_get_nid valida propiedad (_negocio_es_mio)", '_negocio_es_mio' in src)
    check("_negocio_es_mio existe", hasattr(G, '_negocio_es_mio'))
    # Fuera de contexto de request → current_user no autenticado → deniega
    check("_negocio_es_mio sin auth → False", G._negocio_es_mio(999999) is False)
    check("_get_nid con id ajeno (sin auth) → None", G._get_nid(999999) is None)

    print("\n[7] Cableado en la app")
    import src.__init__ as appmod
    csrc = inspect.getsource(appmod.create_app)
    check("create_app tiene guardia CSRF before_request", '_csrf_origin_guard' in csrc and 'origen_permitido' in csrc)
    import src.api.auth.auth_system as auth
    lsrc = inspect.getsource(auth.login)
    check("login usa rate limit server-side (no session counter)",
          'esta_bloqueado' in lsrc and 'login_attempts_' not in lsrc)
    check("login audita bloqueo", 'registrar_evento_seguridad' in lsrc)
    import src.api.auth.password_reset_api as pr
    check("forgot_password tiene rate limit", 'esta_bloqueado' in inspect.getsource(pr.forgot_password))

    print("\n[8] Modelo de intentos + tabla")
    check("IntentoLogin definido", hasattr(S, 'IntentoLogin'))
    import re as _re
    runpy = open(os.path.join(os.path.dirname(__file__), '..', '..', 'run.py'), encoding='utf-8').read()
    check("run.py crea tabla intentos_login", 'intentos_login' in runpy)

    print(f"\n{'='*50}\n  RESULTADO: {PASS} pasaron, {FAIL} fallaron\n{'='*50}")
    return 0 if FAIL == 0 else 1


if __name__ == '__main__':
    sys.exit(main())
