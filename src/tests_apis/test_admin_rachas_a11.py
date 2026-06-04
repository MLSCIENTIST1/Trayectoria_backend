"""
Test de reglas de rachas configurables (Admin Panel — Sprint A11).

Ejecutar:
    PYTHONUTF8=1 venv/Scripts/python.exe src/tests_apis/test_admin_rachas_a11.py
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
        validar_rachas_config, RACHAS_DEFAULT
    )

    print("\n[1] DEFAULT")
    check("umbral_record por defecto = 3", RACHAS_DEFAULT['umbral_record'] == 3)
    check("tukoins_por_record por defecto = 0 (sin cambio de comportamiento)", RACHAS_DEFAULT['tukoins_por_record'] == 0)

    print("\n[2] validar_rachas_config — válidos")
    ok, limpio, err = validar_rachas_config({'umbral_record': 7, 'tukoins_por_record': 20})
    check("válido → ok", ok and err is None)
    check("limpio correcto", limpio == {'umbral_record': 7, 'tukoins_por_record': 20})
    ok2, limpio2, _ = validar_rachas_config({})
    check("vacío → usa defaults", ok2 and limpio2['umbral_record'] == 3 and limpio2['tukoins_por_record'] == 0)

    print("\n[3] validar — rangos")
    check("umbral 0 → inválido", validar_rachas_config({'umbral_record': 0})[0] is False)
    check("umbral 400 → inválido", validar_rachas_config({'umbral_record': 400})[0] is False)
    check("bono negativo → inválido", validar_rachas_config({'tukoins_por_record': -5})[0] is False)
    check("bono gigante → inválido", validar_rachas_config({'tukoins_por_record': 999999})[0] is False)
    check("no numérico → inválido", validar_rachas_config({'umbral_record': 'x'})[0] is False)
    check("no-dict → inválido", validar_rachas_config('x')[0] is False)

    print("\n[4] Lógica de récord (réplica del hook)")
    def es_record(racha, record_antes, umbral):
        return racha > record_antes and racha >= umbral
    check("racha 3, umbral 3, sin record previo → récord", es_record(3, 0, 3))
    check("racha 2, umbral 3 → NO récord", not es_record(2, 0, 3))
    check("umbral configurable a 5: racha 4 → NO", not es_record(4, 3, 5))
    check("umbral configurable a 5: racha 5 → SÍ", es_record(5, 4, 5))
    check("no supera récord previo → NO", not es_record(4, 6, 3))

    print("\n[5] Bono solo al alcanzar el umbral exacto (no se repite)")
    def da_bono(racha, record_antes, umbral, bono):
        return bool(bono) and (racha > record_antes and racha >= umbral) and racha == umbral
    check("racha == umbral → da bono", da_bono(3, 0, 3, 10) is True)
    check("racha > umbral → NO repite bono", da_bono(4, 3, 3, 10) is False)
    check("bono 0 → nunca da", da_bono(3, 0, 3, 0) is False)

    print("\n[6] Endpoints + hooks")
    import src.api.admin_api as api
    check("get_gamif_rachas existe", hasattr(api, 'get_gamif_rachas'))
    check("update_gamif_rachas existe", hasattr(api, 'update_gamif_rachas'))
    import inspect, src.api.gamificacion.gamificacion_hooks as hooks
    src = inspect.getsource(hooks)
    check("hooks usa get_rachas_config", 'get_rachas_config' in src)
    check("hooks ya NO usa '>= 3' hardcodeado", '>= 3' not in src)

    print(f"\n{'='*50}\n  RESULTADO: {PASS} pasaron, {FAIL} fallaron\n{'='*50}")
    return 0 if FAIL == 0 else 1


if __name__ == '__main__':
    sys.exit(main())
