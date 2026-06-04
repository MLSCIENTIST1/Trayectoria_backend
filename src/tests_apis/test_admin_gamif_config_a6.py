"""
Test del editor de XP por evento del panel admin (Admin Panel — Sprint A6).
Valida los helpers puros de merge/validación (constante → BD con fallback).

Ejecutar:
    PYTHONUTF8=1 venv/Scripts/python.exe src/tests_apis/test_admin_gamif_config_a6.py
"""
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

PASS = 0; FAIL = 0
def check(n, c):
    global PASS, FAIL
    if c: PASS += 1; print(f"  ✅ {n}")
    else: FAIL += 1; print(f"  ❌ {n}")


def main():
    from src.models.colombia_data.ratings.config_gamificacion import (
        merge_xp_eventos, validar_xp_eventos, XP_EVENTOS_DEFAULT
    )

    print("\n[1] merge_xp_eventos — fallback al DEFAULT")
    base = merge_xp_eventos(None)
    check("None → DEFAULT completo", base == XP_EVENTOS_DEFAULT)
    check("es una copia (no el mismo objeto)", base is not XP_EVENTOS_DEFAULT)
    check("{} → DEFAULT", merge_xp_eventos({}) == XP_EVENTOS_DEFAULT)

    print("\n[2] merge_xp_eventos — override parcial")
    m = merge_xp_eventos({'venta_completada': {'xp': 25, 'tukoins': 9}})
    check("override aplica xp", m['venta_completada']['xp'] == 25)
    check("override aplica tukoins", m['venta_completada']['tukoins'] == 9)
    check("otros eventos quedan en default", m['login_diario'] == XP_EVENTOS_DEFAULT['login_diario'])

    print("\n[3] merge — saneo y robustez")
    check("clave desconocida se ignora",
          'hackeo' not in merge_xp_eventos({'hackeo': {'xp': 999}}))
    check("xp negativo → 0", merge_xp_eventos({'venta_completada': {'xp': -5}})['venta_completada']['xp'] == 0)
    check("xp no numérico → conserva default",
          merge_xp_eventos({'venta_completada': {'xp': 'abc'}})['venta_completada']['xp'] == XP_EVENTOS_DEFAULT['venta_completada']['xp'])
    check("override solo xp conserva tukoins default",
          merge_xp_eventos({'video_subido': {'xp': 50}})['video_subido']['tukoins'] == XP_EVENTOS_DEFAULT['video_subido']['tukoins'])

    print("\n[4] validar_xp_eventos")
    ok, limpio, err = validar_xp_eventos({'venta_completada': {'xp': 15, 'tukoins': 4}})
    check("payload válido → ok", ok is True and err is None)
    check("limpio normaliza a int", limpio['venta_completada'] == {'xp': 15, 'tukoins': 4})

    ok2, _, err2 = validar_xp_eventos({})
    check("payload vacío → inválido", ok2 is False and err2)

    ok3, _, err3 = validar_xp_eventos({'venta_completada': {'xp': -1}})
    check("xp negativo → inválido", ok3 is False)

    ok4, _, err4 = validar_xp_eventos({'venta_completada': {'xp': 999999}})
    check("xp gigante → inválido", ok4 is False)

    ok5, limpio5, _ = validar_xp_eventos({'desconocido': {'xp': 5}, 'login_diario': {'xp': 7, 'tukoins': 2}})
    check("ignora desconocidas, acepta válidas", ok5 is True and 'desconocido' not in limpio5 and 'login_diario' in limpio5)

    ok6, _, err6 = validar_xp_eventos({'venta_completada': {'xp': 'x'}})
    check("xp no numérico → inválido", ok6 is False)

    print("\n[5] Endpoints + helpers de BD registrados")
    import src.api.admin_api as api
    check("get_gamif_config existe", hasattr(api, 'get_gamif_config'))
    check("update_gamif_xp_eventos existe", hasattr(api, 'update_gamif_xp_eventos'))
    from src.models.colombia_data.ratings.config_gamificacion import get_xp_eventos, set_xp_eventos
    check("get_xp_eventos existe", callable(get_xp_eventos))
    check("set_xp_eventos existe", callable(set_xp_eventos))

    print("\n[6] hooks usa la config efectiva")
    import inspect, src.api.gamificacion.gamificacion_hooks as hooks
    src = inspect.getsource(hooks)
    check("hooks llama _xp_eventos()", '_xp_eventos()' in src)

    print(f"\n{'='*50}\n  RESULTADO: {PASS} pasaron, {FAIL} fallaron\n{'='*50}")
    return 0 if FAIL == 0 else 1


if __name__ == '__main__':
    sys.exit(main())
