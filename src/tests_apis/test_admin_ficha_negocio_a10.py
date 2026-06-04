"""
Test de la ficha de gamificación por negocio (Admin Panel — Sprint A10).

Ejecutar:
    PYTHONUTF8=1 venv/Scripts/python.exe src/tests_apis/test_admin_ficha_negocio_a10.py
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

    print("\n[1] Corrección de XP recalcula el nivel (lógica del endpoint)")
    g = NegocioGamificacion()
    g.xp_total = 0; g.nivel = 1; g.tukoins = 0; g.prestigio = 0
    g.xp_total = 25000; g.calcular_nivel()
    check("25000 XP → nivel Leyenda (30)", g.nivel == 30)
    g.xp_total = 100; g.calcular_nivel()
    check("100 XP → nivel 2", g.nivel == 2)
    g.xp_total = 0; g.calcular_nivel()
    check("0 XP → nivel 1", g.nivel == 1)

    print("\n[2] Clamp de valores (réplica del endpoint)")
    def clamp(v):
        return max(0, int(v))
    check("xp negativo → 0", clamp(-50) == 0)
    check("prestigio negativo → 0", clamp(-1) == 0)
    check("valor positivo se conserva", clamp(500) == 500)

    print("\n[3] Delta de TuKoins (set → delta sobre saldo actual)")
    g.tukoins = 30
    nuevo = 80
    delta = nuevo - g.tukoins
    check("delta correcto", delta == 50)
    g.tukoins = max(0, g.tukoins + delta)
    check("saldo tras delta", g.tukoins == 80)

    print("\n[4] serialize incluye los campos de la ficha")
    s = g.serialize()
    for campo in ('xp_total', 'nivel', 'tukoins', 'prestigio', 'onboarding_completado', 'racha_actividad'):
        check(f"serialize tiene '{campo}'", campo in s)

    print("\n[5] Endpoints registrados")
    import src.api.admin_api as api
    check("get_gamif_negocio existe", hasattr(api, 'get_gamif_negocio'))
    check("ajustar_gamif_negocio existe", hasattr(api, 'ajustar_gamif_negocio'))
    import inspect
    src = inspect.getsource(api.ajustar_gamif_negocio)
    check("exige motivo", "motivo" in src and "obligatorio" in src)
    check("recalcula nivel tras cambiar xp", "calcular_nivel()" in src)
    check("audita el ajuste", "registrar_auditoria" in src and "gamif_negocio" in src)

    print(f"\n{'='*50}\n  RESULTADO: {PASS} pasaron, {FAIL} fallaron\n{'='*50}")
    return 0 if FAIL == 0 else 1


if __name__ == '__main__':
    sys.exit(main())
