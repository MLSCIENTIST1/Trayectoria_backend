"""
Test de eventos especiales (Sprint 38) — ventanas de fecha con XP multiplicado.

Ejecutar:
    PYTHONUTF8=1 venv/Scripts/python.exe src/tests_apis/test_eventos_especiales_s38.py
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
    from src.models.colombia_data.ratings.negocio_gamificacion import (
        evento_especial, multiplicador_xp, EVENTOS_ESPECIALES
    )

    print("\n[1] Semana del Tendero (julio 1-7) → XP x3")
    ev = evento_especial(datetime(2026, 7, 3))
    check("evento detectado", ev is not None)
    check("nombre = Semana del Tendero", ev and ev['nombre'] == 'Semana del Tendero')
    check("multiplicador = 3", multiplicador_xp(datetime(2026, 7, 3)) == 3)
    check("borde inicial (jul 1) activo", evento_especial(datetime(2026, 7, 1)) is not None)
    check("borde final (jul 7) activo", evento_especial(datetime(2026, 7, 7)) is not None)

    print("\n[2] Aniversario (julio 24-31) → XP x2")
    ev2 = evento_especial(datetime(2026, 7, 25))
    check("aniversario detectado", ev2 and ev2['codigo'] == 'aniversario')
    check("aniversario multiplicador = 2", multiplicador_xp(datetime(2026, 7, 25)) == 2)

    print("\n[3] Diciembre Mágico (dic 15-31) → XP x2")
    check("dic 20 activo x2", multiplicador_xp(datetime(2026, 12, 20)) == 2)
    check("dic 14 NO activo", evento_especial(datetime(2026, 12, 14)) is None)

    print("\n[4] Días sin evento → x1")
    for m, d, etq in [(6, 15, 'jun 15'), (7, 10, 'jul 10'), (1, 1, 'ene 1'), (7, 8, 'jul 8 (gap)')]:
        check(f"{etq} → sin evento, x1",
              evento_especial(datetime(2026, m, d)) is None and multiplicador_xp(datetime(2026, m, d)) == 1)

    print("\n[5] Aplicación del multiplicador (cálculo de XP)")
    base = 50
    check("misión 50 XP en Semana del Tendero → 150", base * multiplicador_xp(datetime(2026, 7, 3)) == 150)
    check("misión 50 XP en día normal → 50", base * multiplicador_xp(datetime(2026, 6, 1)) == 50)

    print("\n[6] Integridad del catálogo")
    check("hay eventos definidos", len(EVENTOS_ESPECIALES) >= 3)
    check("todos tienen xp_mult >= 2", all(e['xp_mult'] >= 2 for e in EVENTOS_ESPECIALES))
    check("todos tienen codigo/nombre/icono", all(e.get('codigo') and e.get('nombre') and e.get('icono') for e in EVENTOS_ESPECIALES))
    check("rangos de día válidos", all(1 <= e['dia_ini'] <= e['dia_fin'] <= 31 for e in EVENTOS_ESPECIALES))

    print(f"\n{'='*50}\n  RESULTADO: {PASS} pasaron, {FAIL} fallaron\n{'='*50}")
    return 0 if FAIL == 0 else 1


if __name__ == '__main__':
    sys.exit(main())
