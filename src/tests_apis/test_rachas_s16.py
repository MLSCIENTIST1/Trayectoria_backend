"""
Test del cálculo de rachas (Sprint 16) — helper puro _racha_desde_dias.

Ejecutar:
    PYTHONUTF8=1 venv/Scripts/python.exe src/tests_apis/test_rachas_s16.py
"""
import os
import sys
from datetime import date, timedelta
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

PASS = 0; FAIL = 0
def check(n, c):
    global PASS, FAIL
    if c: PASS += 1; print(f"  ✅ {n}")
    else: FAIL += 1; print(f"  ❌ {n}")


def main():
    from src.api.gamificacion.gamificacion_api import _racha_desde_dias
    HOY = date(2026, 6, 3)
    d = lambda n: HOY - timedelta(days=n)  # noqa: hace fechas relativas a HOY

    print("\n[1] Lista vacía")
    a, m = _racha_desde_dias([], hoy=HOY)
    check("sin días → (0, 0)", a == 0 and m == 0)

    print("\n[2] Racha actual desde hoy")
    a, m = _racha_desde_dias([d(0), d(1), d(2)], hoy=HOY)
    check("hoy, ayer, antier → actual=3", a == 3)
    check("máxima=3", m == 3)

    print("\n[3] Tolerancia: empieza ayer (aún no vendí hoy)")
    a, m = _racha_desde_dias([d(1), d(2)], hoy=HOY)
    check("ayer y antier → actual=2 (no se rompe por no tener hoy)", a == 2)

    print("\n[4] Racha rota")
    a, m = _racha_desde_dias([d(0), d(3), d(4), d(5)], hoy=HOY)
    check("hoy aislado, luego hueco → actual=1", a == 1)
    check("máxima histórica=3 (días 3,4,5)", m == 3)

    print("\n[5] Sin actividad reciente (hace 10 días)")
    a, m = _racha_desde_dias([d(10), d(11), d(12)], hoy=HOY)
    check("actual=0 (racha vieja rota)", a == 0)
    check("máxima=3 conservada", m == 3)

    print("\n[6] Un solo día (hoy)")
    a, m = _racha_desde_dias([d(0)], hoy=HOY)
    check("solo hoy → actual=1, max=1", a == 1 and m == 1)

    print(f"\n{'='*50}\n  RESULTADO: {PASS} pasaron, {FAIL} fallaron\n{'='*50}")
    return 0 if FAIL == 0 else 1


if __name__ == '__main__':
    sys.exit(main())
