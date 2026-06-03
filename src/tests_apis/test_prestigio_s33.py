"""
Test del sistema de prestigio (Sprint 33).

Ejecutar:
    PYTHONUTF8=1 venv/Scripts/python.exe src/tests_apis/test_prestigio_s33.py
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
    from src.models.colombia_data.ratings.negocio_gamificacion import NegocioGamificacion

    g = NegocioGamificacion()
    g.xp_total = 0; g.nivel = 1; g.prestigio = 0

    print("\n[1] Elegibilidad")
    check("0 XP → no puede prestigiar", g.puede_prestigiar() is False)
    g.xp_total = 25000  # Leyenda
    check("25000 XP (Leyenda) → puede prestigiar", g.puede_prestigiar() is True)
    check("xp_maximo = 25000", g.xp_maximo == 25000)

    print("\n[2] Prestigiar resetea y suma estrella")
    ok = g.prestigiar()
    check("prestigiar() retorna True", ok is True)
    check("prestigio = 1", g.prestigio == 1)
    check("XP reseteado a 0", g.xp_total == 0)
    check("nivel vuelve a 1", g.nivel == 1)

    print("\n[3] No se puede prestigiar sin estar en Leyenda")
    ok2 = g.prestigiar()
    check("prestigiar() de nuevo (0 XP) → False", ok2 is False)
    check("prestigio sigue en 1", g.prestigio == 1)

    print("\n[4] Múltiples prestigios acumulan estrellas")
    g.xp_total = 30000
    g.prestigiar()
    check("segundo prestigio → 2 estrellas", g.prestigio == 2)

    print("\n[5] serialize incluye prestigio")
    g.xp_total = 100
    s = g.serialize()
    check("serialize tiene 'prestigio'", s.get('prestigio') == 2)
    check("serialize tiene 'puede_prestigiar'", 'puede_prestigiar' in s)

    print(f"\n{'='*50}\n  RESULTADO: {PASS} pasaron, {FAIL} fallaron\n{'='*50}")
    return 0 if FAIL == 0 else 1


if __name__ == '__main__':
    sys.exit(main())
