"""
Test del armado de ranking de ligas (Sprints 26/27) — helper puro _armar_ranking.

Ejecutar:
    PYTHONUTF8=1 venv/Scripts/python.exe src/tests_apis/test_ligas_s26.py
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
    from src.api.gamificacion.gamificacion_api import _armar_ranking

    # (id, nombre, ciudad, categoria, logo, slug, score) — ya ordenadas desc
    filas = [
        (10, 'RODAR', 'Bogotá', 'Automotriz', None, 'rodar', 80),
        (20, 'AZ Natural', 'Bogotá', 'Naturales', None, 'aznatural', 55),
        (30, 'Caballeros', 'Bogotá', 'Ropa', None, 'caballeros', 30),
        (40, 'Cuarto', 'Bogotá', 'Tech', None, 'cuarto', 10),
    ]

    print("\n[1] Posiciones y medallas")
    r = _armar_ranking(filas, mi_negocio_id=30)
    rk = r['ranking']
    check("4 entradas", len(rk) == 4)
    check("1ro = oro 🥇", rk[0]['medalla'] == '🥇' and rk[0]['posicion'] == 1)
    check("2do = plata 🥈", rk[1]['medalla'] == '🥈')
    check("3ro = bronce 🥉", rk[2]['medalla'] == '🥉')
    check("4to sin medalla", rk[3]['medalla'] == '')
    check("puntaje del líder = 80", rk[0]['puntaje'] == 80)

    print("\n[2] Mi posición")
    check("negocio 30 está en posición 3", r['mi_posicion'] == 3)
    r2 = _armar_ranking(filas, mi_negocio_id=999)
    check("negocio ausente → mi_posicion None", r2['mi_posicion'] is None)
    r3 = _armar_ranking(filas, mi_negocio_id=None)
    check("sin negocio → mi_posicion None", r3['mi_posicion'] is None)

    print("\n[3] Lista vacía")
    rv = _armar_ranking([], 5)
    check("vacío → ranking [] y mi_posicion None", rv['ranking'] == [] and rv['mi_posicion'] is None)

    print(f"\n{'='*50}\n  RESULTADO: {PASS} pasaron, {FAIL} fallaron\n{'='*50}")
    return 0 if FAIL == 0 else 1


if __name__ == '__main__':
    sys.exit(main())
