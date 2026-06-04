"""
Test de economía de TuKoins (Admin Panel — Sprint A9).
Valida el bono configurable (puro), la validación, y la compatibilidad con S36.

Ejecutar:
    PYTHONUTF8=1 venv/Scripts/python.exe src/tests_apis/test_admin_economia_a9.py
"""
import os
import sys
from datetime import datetime
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

PASS = 0; FAIL = 0
def check(n, c):
    global PASS, FAIL
    if c: PASS += 1; print(f"  ✅ {n}")
    else: FAIL += 1; print(f"  ❌ {n}")


def main():
    from src.models.colombia_data.ratings.config_gamificacion import (
        calcular_bono, validar_bono_config, BONO_DEFAULT
    )
    from src.models.colombia_data.ratings.negocio_gamificacion import bono_tukoins

    # 2026-06-07 domingo, 2026-06-08 lunes
    DOM = datetime(2026, 6, 7)
    LUN = datetime(2026, 6, 8)

    print("\n[1] calcular_bono con DEFAULT (domingo x2)")
    m, n = calcular_bono(DOM, BONO_DEFAULT)
    check("domingo → x2", m == 2 and n == 'Domingo de TuKoins')
    m2, n2 = calcular_bono(LUN, BONO_DEFAULT)
    check("lunes → x1 sin bono", m2 == 1 and n2 is None)

    print("\n[2] calcular_bono con config personalizada")
    cfg = {'activo': True, 'dia_semana': 0, 'multiplicador': 3, 'nombre': 'Lunes Loco'}
    check("lunes config → x3", calcular_bono(LUN, cfg) == (3, 'Lunes Loco'))
    check("domingo con config lunes → x1", calcular_bono(DOM, cfg) == (1, None))

    print("\n[3] bono desactivado")
    check("activo=False → x1", calcular_bono(DOM, {'activo': False, 'dia_semana': 6, 'multiplicador': 2}) == (1, None))
    check("multiplicador 1 → sin bono", calcular_bono(DOM, {'activo': True, 'dia_semana': 6, 'multiplicador': 1}) == (1, None))

    print("\n[4] validar_bono_config")
    ok, limpio, err = validar_bono_config({'dia_semana': 5, 'multiplicador': 2, 'nombre': 'Sábado'})
    check("válido → ok", ok and err is None)
    check("limpio correcto", limpio['dia_semana'] == 5 and limpio['multiplicador'] == 2)
    check("dia fuera de rango → inválido", validar_bono_config({'dia_semana': 9})[0] is False)
    check("multiplicador 0 → inválido", validar_bono_config({'multiplicador': 0})[0] is False)
    check("multiplicador 99 → inválido", validar_bono_config({'multiplicador': 99})[0] is False)
    check("no numérico → inválido", validar_bono_config({'dia_semana': 'x'})[0] is False)
    check("no-dict → inválido", validar_bono_config("x")[0] is False)
    check("nombre se recorta a 60", len(validar_bono_config({'nombre': 'N'*200})[1]['nombre']) <= 60)

    print("\n[5] Compatibilidad S36: bono_tukoins sigue funcionando (fallback sin DB)")
    mult, nombre = bono_tukoins(DOM)
    check("domingo sigue x2", mult == 2 and nombre == 'Domingo de TuKoins')
    check("lunes sigue x1", bono_tukoins(LUN) == (1, None))

    print("\n[6] Endpoints registrados")
    import src.api.admin_api as api
    check("get_gamif_economia existe", hasattr(api, 'get_gamif_economia'))
    check("ajustar_tukoins existe", hasattr(api, 'ajustar_tukoins'))
    check("update_gamif_bono existe", hasattr(api, 'update_gamif_bono'))

    print(f"\n{'='*50}\n  RESULTADO: {PASS} pasaron, {FAIL} fallaron\n{'='*50}")
    return 0 if FAIL == 0 else 1


if __name__ == '__main__':
    sys.exit(main())
