"""
Test del gestor central de textos/copys (Admin Panel — Sprint A49).

Ejecutar:
    PYTHONUTF8=1 venv/Scripts/python.exe src/tests_apis/test_admin_textos_a49.py
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
    from src.models.colombia_data.config_plataforma import (
        validar_textos, get_textos, get_texto, TEXTOS_DEFAULT
    )

    print("\n[1] Catálogo por defecto")
    check("hay textos por defecto", len(TEXTOS_DEFAULT) >= 5)
    check("cada uno trae categoria/descripcion/valor",
          all(all(k in t for k in ('categoria', 'descripcion', 'valor')) for t in TEXTOS_DEFAULT.values()))
    check("get_textos sin BD = catálogo default", set(get_textos().keys()) >= set(TEXTOS_DEFAULT.keys()))

    print("\n[2] get_texto — fallback")
    una_clave = next(iter(TEXTOS_DEFAULT))
    check("clave conocida → valor default", get_texto(una_clave) == TEXTOS_DEFAULT[una_clave]['valor'])
    check("clave desconocida → fallback", get_texto('no.existe.xyz', 'POR_DEFECTO') == 'POR_DEFECTO')
    check("clave desconocida sin fallback → ''", get_texto('no.existe.xyz') == '')

    print("\n[3] validar_textos")
    ok, limpio, err = validar_textos({'onboarding.bienvenida': 'Hola nuevo'})
    check("válido → ok", ok and limpio == {'onboarding.bienvenida': 'Hola nuevo'})
    check("None → cadena vacía", validar_textos({'x': None})[1]['x'] == '')
    check("no-dict → inválido", validar_textos('x')[0] is False)
    check("valor no-string → inválido", validar_textos({'x': 123})[0] is False)
    check("clave vacía → inválido", validar_textos({'  ': 'v'})[0] is False)
    check("texto enorme → inválido", validar_textos({'x': 'a' * 6000})[0] is False)

    print("\n[4] Endpoints admin + público")
    import src.api.admin_api as api
    check("admin_textos existe", hasattr(api, 'admin_textos'))
    check("update_textos existe", hasattr(api, 'update_textos'))
    src_u = inspect.getsource(api.update_textos)
    check("update valida + audita", 'validar_textos' in src_u and 'registrar_auditoria' in src_u)
    check("ambos requieren permiso configuracion",
          "requiere_permiso('configuracion')" in inspect.getsource(api.admin_textos))
    import src.api.utils.register_user_api as reg
    check("textos_publicos (i18n) existe", hasattr(reg, 'textos_publicos'))
    src_pub = inspect.getsource(reg.textos_publicos)
    check("público devuelve mapa clave→valor", 'get_textos' in src_pub and 'textos' in src_pub)

    print(f"\n{'='*50}\n  RESULTADO: {PASS} pasaron, {FAIL} fallaron\n{'='*50}")
    return 0 if FAIL == 0 else 1


if __name__ == '__main__':
    sys.exit(main())
