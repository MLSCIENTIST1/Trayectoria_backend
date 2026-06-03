"""
Test del reto temático del mes (Sprint 28) — rotación determinista.

Ejecutar:
    PYTHONUTF8=1 venv/Scripts/python.exe src/tests_apis/test_reto_mes_s28.py
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
    from src.api.gamificacion.gamificacion_api import _reto_del_mes, RETOS_MENSUALES

    print("\n[1] Definición de retos")
    check("hay 3 retos definidos", len(RETOS_MENSUALES) == 3)
    check("cada reto tiene metrica", all('metrica' in r for r in RETOS_MENSUALES))
    check("cada reto tiene nombre e icono", all(r.get('nombre') and r.get('icono') for r in RETOS_MENSUALES))

    print("\n[2] Rotación determinista")
    r1 = _reto_del_mes(datetime(2026, 1, 15))
    r1b = _reto_del_mes(datetime(2026, 1, 28))
    check("mismo mes → mismo reto", r1['codigo'] == r1b['codigo'])
    r2 = _reto_del_mes(datetime(2026, 2, 15))
    check("meses consecutivos → reto distinto", r1['codigo'] != r2['codigo'])

    print("\n[3] Cobertura: 3 meses seguidos cubren los 3 retos")
    cods = {_reto_del_mes(datetime(2026, m, 1))['codigo'] for m in (1, 2, 3)}
    check("ene-feb-mar usan los 3 retos distintos", len(cods) == 3)

    print("\n[4] Ciclo: vuelve a empezar tras N meses")
    ra = _reto_del_mes(datetime(2026, 1, 1))
    rb = _reto_del_mes(datetime(2026, 4, 1))  # 3 meses después → mismo
    check("mes+3 vuelve al mismo reto (ciclo de 3)", ra['codigo'] == rb['codigo'])

    print(f"\n{'='*50}\n  RESULTADO: {PASS} pasaron, {FAIL} fallaron\n{'='*50}")
    return 0 if FAIL == 0 else 1


if __name__ == '__main__':
    sys.exit(main())
