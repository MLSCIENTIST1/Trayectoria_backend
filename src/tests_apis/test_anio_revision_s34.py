"""
Test del año en revisión (Sprint 34) — helper de rango anual.

Ejecutar:
    PYTHONUTF8=1 venv/Scripts/python.exe src/tests_apis/test_anio_revision_s34.py
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
    from src.api.gamificacion.gamificacion_api import _rango_anio

    print("\n[1] Rango del año")
    ini, fin, anio = _rango_anio(datetime(2026, 6, 15))
    check("inicio = 1-ene-2026", ini == datetime(2026, 1, 1))
    check("fin = 1-ene-2027 (exclusivo)", fin == datetime(2027, 1, 1))
    check("año = 2026", anio == 2026)

    print("\n[2] Rango semiabierto cubre todo el año")
    check("31-dic-23:59 entra (< fin)", datetime(2026, 12, 31, 23, 59) < fin)
    check("1-ene-2027 NO entra (>= fin)", not (datetime(2027, 1, 1) < fin))
    check("1-ene-2026 entra (>= ini)", datetime(2026, 1, 1) >= ini)

    print("\n[3] Distinto año")
    ini2, fin2, a2 = _rango_anio(datetime(2025, 12, 31))
    check("año 2025 → [1-ene-2025, 1-ene-2026)",
          ini2 == datetime(2025, 1, 1) and fin2 == datetime(2026, 1, 1) and a2 == 2025)

    print(f"\n{'='*50}\n  RESULTADO: {PASS} pasaron, {FAIL} fallaron\n{'='*50}")
    return 0 if FAIL == 0 else 1


if __name__ == '__main__':
    sys.exit(main())
