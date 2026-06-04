"""
Test de vista de progreso/otorgamientos por insignia (Admin Panel — Sprint A20).

Ejecutar:
    PYTHONUTF8=1 venv/Scripts/python.exe src/tests_apis/test_admin_progreso_a20.py
"""
import os
import sys
import inspect
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

PASS = 0; FAIL = 0
def check(n, c):
    global PASS, FAIL
    if c: PASS += 1; print(f"  ✅ {n}")
    else: FAIL += 1; print(f"  ❌ {n}")


def main():
    import src.api.admin_api as api

    print("\n[1] Endpoints registrados")
    check("insignias_distribucion existe", hasattr(api, 'insignias_distribucion'))
    check("insignia_estadisticas existe", hasattr(api, 'insignia_estadisticas'))
    check("_scalar_admin_list existe", hasattr(api, '_scalar_admin_list'))

    sdist = inspect.getsource(api.insignias_distribucion)
    sest = inspect.getsource(api.insignia_estadisticas)

    print("\n[2] Distribución agrupa por tier")
    check("agrupa por nivel", 'GROUP BY nivel' in sdist)
    check("cuenta badges y otorgados", 'badges' in sdist and 'otorgados' in sdist)

    print("\n[3] Estadísticas por insignia")
    check("cuenta otorgados activos", 'total_otorgados' in sest and 'activo IS TRUE OR' in sest)
    check("trae recientes", 'recientes' in sest and 'fecha_obtencion DESC' in sest)
    check("ranking de cercanía", 'cercanos' in sest and 'pct' in sest)
    check("cercanía solo para >= numérico no secreto", "criterio_operador == '>='" in sest and 'es_secreto' in sest)
    check("excluye a quienes ya la tienen", "ya" in sest and 'nid in ya' in sest)
    check("excluye a quienes ya cumplen (se otorgaría solo)", 'val >= objetivo' in sest)
    check("acotado (CAP)", 'CAP' in sest)
    check("no escribe (sin commit)", 'commit' not in sest)

    print("\n[4] Cálculo de % de cercanía (réplica de la lógica)")
    def pct(actual, objetivo):
        return max(0.0, min(99.0, round(actual / objetivo * 100, 1)))
    check("50/100 → 50%", pct(50, 100) == 50.0)
    check("tope 99% (no 100)", pct(100, 100) == 99.0)
    check("0 → 0%", pct(0, 100) == 0.0)

    print("\n[5] Permiso")
    check("distribucion requiere permiso insignias", "requiere_permiso('insignias')" in sdist)
    check("estadisticas requiere permiso insignias", "requiere_permiso('insignias')" in sest)

    print(f"\n{'='*50}\n  RESULTADO: {PASS} pasaron, {FAIL} fallaron\n{'='*50}")
    return 0 if FAIL == 0 else 1


if __name__ == '__main__':
    sys.exit(main())
