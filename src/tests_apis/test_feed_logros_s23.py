"""
Test del feed de logros (Sprint 23) — helper puro _merge_eventos.

Ejecutar:
    PYTHONUTF8=1 venv/Scripts/python.exe src/tests_apis/test_feed_logros_s23.py
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
    from src.api.gamificacion.gamificacion_api import _merge_eventos

    badges = [
        {'tipo': 'badge', 'titulo': 'Insignia A', 'ts': 100},
        {'tipo': 'badge', 'titulo': 'Insignia B', 'ts': 300},
    ]
    misiones = [
        {'tipo': 'mision', 'titulo': 'Misión X', 'ts': 200},
        {'tipo': 'mision', 'titulo': 'Misión Y', 'ts': 50},
    ]

    print("\n[1] Fusión y orden por fecha desc")
    feed = _merge_eventos([badges, misiones], limite=15)
    check("fusiona ambas listas (4 eventos)", len(feed) == 4)
    titulos = [e['titulo'] for e in feed]
    check("orden por ts desc: B(300), X(200), A(100), Y(50)",
          titulos == ['Insignia B', 'Misión X', 'Insignia A', 'Misión Y'])

    print("\n[2] Límite")
    feed2 = _merge_eventos([badges, misiones], limite=2)
    check("limite=2 devuelve 2", len(feed2) == 2)
    check("conserva los 2 más recientes", [e['titulo'] for e in feed2] == ['Insignia B', 'Misión X'])

    print("\n[3] Robustez con listas vacías / None")
    check("listas vacías → []", _merge_eventos([[], []]) == [])
    check("None dentro → no rompe", _merge_eventos([None, badges], 15) and len(_merge_eventos([None, badges], 15)) == 2)
    check("sin 'ts' → ts=0, no lanza", len(_merge_eventos([[{'titulo': 'sin ts'}]], 5)) == 1)

    print(f"\n{'='*50}\n  RESULTADO: {PASS} pasaron, {FAIL} fallaron\n{'='*50}")
    return 0 if FAIL == 0 else 1


if __name__ == '__main__':
    sys.exit(main())
