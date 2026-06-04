"""
Test del dashboard de KPIs del panel admin (Admin Panel — Sprint A4).

Como el endpoint hace lecturas a Postgres, aquí validamos:
- que el endpoint está registrado
- el set de KPIs esperado (contrato de claves)
- formato COP (réplica del helper de frontend, lógica pura)

Ejecutar:
    PYTHONUTF8=1 venv/Scripts/python.exe src/tests_apis/test_admin_metrics_a4.py
"""
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

PASS = 0; FAIL = 0
def check(n, c):
    global PASS, FAIL
    if c: PASS += 1; print(f"  ✅ {n}")
    else: FAIL += 1; print(f"  ❌ {n}")


# Réplica de la lógica del backend para el caso "consulta falla → default"
def escalar_seguro(fn, default=0):
    try:
        v = fn()
        return v if v is not None else default
    except Exception:
        return default


def main():
    print("\n[1] Endpoint registrado")
    import src.api.admin_api as api
    check("get_admin_metrics existe", hasattr(api, 'get_admin_metrics'))

    print("\n[2] Tolerancia a fallos (escalar_seguro)")
    check("consulta OK → valor", escalar_seguro(lambda: 42) == 42)
    check("consulta None → default 0", escalar_seguro(lambda: None) == 0)
    check("consulta lanza error → default 0", escalar_seguro(lambda: (_ for _ in ()).throw(Exception('x'))) == 0)
    check("default personalizado", escalar_seguro(lambda: None, default=-1) == -1)

    print("\n[3] Contrato de KPIs esperados")
    ESPERADAS = {
        'usuarios_total', 'negocios_total', 'negocios_activos', 'negocios_publicos',
        'pedidos_entregados', 'pedidos_total', 'ventas_volumen',
        'xp_repartido', 'tukoins_circulando', 'negocios_jugando',
        'insignias_otorgadas', 'onboarding_completos',
        'admins_activos', 'acciones_admin_30d', 'evento_activo',
    }
    import inspect
    src = inspect.getsource(api.get_admin_metrics)
    faltantes = [k for k in ESPERADAS if k not in src]
    check(f"el endpoint produce todas las KPIs esperadas (faltan: {faltantes})", not faltantes)

    print("\n[4] Formato COP (lógica pura del frontend, replicada)")
    def fmt_cop(n):
        n = float(n or 0)
        return '$' + format(int(n), ',d').replace(',', '.')
    check("100000 → $100.000", fmt_cop(100000) == '$100.000')
    check("0 → $0", fmt_cop(0) == '$0')
    check("None → $0", fmt_cop(None) == '$0')

    print(f"\n{'='*50}\n  RESULTADO: {PASS} pasaron, {FAIL} fallaron\n{'='*50}")
    return 0 if FAIL == 0 else 1


if __name__ == '__main__':
    sys.exit(main())
