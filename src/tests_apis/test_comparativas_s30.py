"""
Test de comparativas contextuales (Sprint 30) — helpers puros.

Ejecutar:
    PYTHONUTF8=1 venv/Scripts/python.exe src/tests_apis/test_comparativas_s30.py
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
    from src.api.gamificacion.gamificacion_api import (
        _pct_top, _crecimiento_pct, _rango_mes_anterior
    )

    print("\n[1] Percentil top X%")
    check("posición 1 de 100 → top 1%", _pct_top(1, 100) == 1)
    check("posición 15 de 100 → top 15%", _pct_top(15, 100) == 15)
    check("posición 50 de 100 → top 50%", _pct_top(50, 100) == 50)
    check("posición 1 de 1 → top 100%", _pct_top(1, 1) == 100)
    check("total 0 → None", _pct_top(1, 0) is None)
    check("nunca menos de 1%", _pct_top(1, 1000) == 1)

    print("\n[2] Crecimiento vs mes anterior")
    check("10 vs 8 → +25%", _crecimiento_pct(10, 8) == 25)
    check("8 vs 10 → -20%", _crecimiento_pct(8, 10) == -20)
    check("igual → 0%", _crecimiento_pct(10, 10) == 0)
    check("de 0 a 5 → +100% (debut)", _crecimiento_pct(5, 0) == 100)
    check("0 y 0 → None", _crecimiento_pct(0, 0) is None)

    print("\n[3] Rango del mes anterior")
    ini, fin, et = _rango_mes_anterior(datetime(2026, 6, 15))
    check("desde junio → mayo", ini == datetime(2026, 5, 1) and fin == datetime(2026, 6, 1))
    check("etiqueta 'mayo 2026'", et == 'mayo 2026')
    ini2, fin2, et2 = _rango_mes_anterior(datetime(2026, 1, 10))
    check("enero → diciembre año anterior", ini2 == datetime(2025, 12, 1) and fin2 == datetime(2026, 1, 1))
    check("etiqueta 'diciembre 2025'", et2 == 'diciembre 2025')

    print(f"\n{'='*50}\n  RESULTADO: {PASS} pasaron, {FAIL} fallaron\n{'='*50}")
    return 0 if FAIL == 0 else 1


if __name__ == '__main__':
    sys.exit(main())
