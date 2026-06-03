"""
Test del helper de rango de mes para el resumen mensual (Sprint 21).

Ejecutar:
    PYTHONUTF8=1 venv/Scripts/python.exe src/tests_apis/test_resumen_mensual_s21.py
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
    from src.api.gamificacion.gamificacion_api import _rango_mes

    print("\n[1] Mes normal (junio 2026)")
    ini, fin, lbl = _rango_mes(datetime(2026, 6, 15, 10, 30))
    check("inicio = 1 junio 00:00", ini == datetime(2026, 6, 1))
    check("fin = 1 julio (exclusivo)", fin == datetime(2026, 7, 1))
    check("etiqueta = 'junio 2026'", lbl == 'junio 2026')

    print("\n[2] Diciembre cruza de año")
    ini, fin, lbl = _rango_mes(datetime(2026, 12, 31, 23, 59))
    check("inicio = 1 dic", ini == datetime(2026, 12, 1))
    check("fin = 1 enero del año siguiente", fin == datetime(2027, 1, 1))
    check("etiqueta = 'diciembre 2026'", lbl == 'diciembre 2026')

    print("\n[3] Enero (borde inferior)")
    ini, fin, lbl = _rango_mes(datetime(2026, 1, 1))
    check("inicio = 1 enero", ini == datetime(2026, 1, 1))
    check("fin = 1 febrero", fin == datetime(2026, 2, 1))
    check("etiqueta = 'enero 2026'", lbl == 'enero 2026')

    print("\n[4] El rango es semiabierto [ini, fin)")
    ini, fin, _ = _rango_mes(datetime(2026, 6, 15))
    check("fin > inicio", fin > ini)
    check("una venta del 30-jun-23:59 entra (< fin)", datetime(2026, 6, 30, 23, 59) < fin)
    check("una venta del 1-jul-00:00 NO entra (>= fin)", not (datetime(2026, 7, 1, 0, 0) < fin))

    print(f"\n{'='*50}\n  RESULTADO: {PASS} pasaron, {FAIL} fallaron\n{'='*50}")
    return 0 if FAIL == 0 else 1


if __name__ == '__main__':
    sys.exit(main())
