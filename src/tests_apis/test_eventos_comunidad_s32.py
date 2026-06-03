"""
Test de eventos de comunidad (Sprint 32) — helpers puros.

Ejecutar:
    PYTHONUTF8=1 venv/Scripts/python.exe src/tests_apis/test_eventos_comunidad_s32.py
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
    from src.api.gamificacion.gamificacion_api import (
        _es_evento_destacado, _titulo_evento_comunidad, NIVEL_EVENTO_DESTACADO
    )

    print("\n[1] Umbral de evento destacado (Oro+)")
    check("umbral = 3 (Oro)", NIVEL_EVENTO_DESTACADO == 3)
    check("Bronce (1) NO destacado", _es_evento_destacado(1) is False)
    check("Plata (2) NO destacado", _es_evento_destacado(2) is False)
    check("Oro (3) SÍ destacado", _es_evento_destacado(3) is True)
    check("Platino (4) SÍ", _es_evento_destacado(4) is True)
    check("Diamante (5) SÍ", _es_evento_destacado(5) is True)
    check("None → no destacado", _es_evento_destacado(None) is False)

    print("\n[2] Título del evento")
    t = _titulo_evento_comunidad('RODAR', 'Top Vendedor')
    check("incluye negocio y badge", 'RODAR' in t and 'Top Vendedor' in t)
    check("formato con trofeo", t.startswith('🏆'))

    print(f"\n{'='*50}\n  RESULTADO: {PASS} pasaron, {FAIL} fallaron\n{'='*50}")
    return 0 if FAIL == 0 else 1


if __name__ == '__main__':
    sys.exit(main())
