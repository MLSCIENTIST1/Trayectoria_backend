"""
Test de economía expandida TuKoins (Sprint 36) — bono por fecha.

Ejecutar:
    PYTHONUTF8=1 venv/Scripts/python.exe src/tests_apis/test_economia_s36.py
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
    from src.models.colombia_data.ratings.negocio_gamificacion import bono_tukoins

    # 2026-06-07 es domingo; 2026-06-08 lunes; 2026-06-06 sábado
    print("\n[1] Domingo → x2")
    mult, nombre = bono_tukoins(datetime(2026, 6, 7))
    check("domingo multiplicador = 2", mult == 2)
    check("domingo tiene nombre de bono", nombre == 'Domingo de TuKoins')

    print("\n[2] Días normales → x1 sin bono")
    for d, dia in [(8, 'lunes'), (9, 'martes'), (6, 'sábado')]:
        m, n = bono_tukoins(datetime(2026, 6, d))
        check(f"{dia} → x1 sin bono", m == 1 and n is None)

    print("\n[3] Aplicación del multiplicador (cálculo)")
    mult_dom, _ = bono_tukoins(datetime(2026, 6, 7))
    base = 10
    check("misión de 10 TuKoins en domingo → 20", base * mult_dom == 20)
    mult_lun, _ = bono_tukoins(datetime(2026, 6, 8))
    check("misión de 10 TuKoins en lunes → 10", base * mult_lun == 10)

    print(f"\n{'='*50}\n  RESULTADO: {PASS} pasaron, {FAIL} fallaron\n{'='*50}")
    return 0 if FAIL == 0 else 1


if __name__ == '__main__':
    sys.exit(main())
