"""
Test del editor visual de criterios (Admin Panel — Sprint A16).

Ejecutar:
    PYTHONUTF8=1 venv/Scripts/python.exe src/tests_apis/test_admin_criterios_a16.py
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
    from src.models.colombia_data.ratings.config_gamificacion import (
        METRICAS_CRITERIO, METRICAS_CRITERIO_KEYS
    )

    print("\n[1] Catálogo de métricas")
    check("hay métricas", len(METRICAS_CRITERIO) >= 20)
    check("todas tienen key+label", all(m.get('key') and m.get('label') for m in METRICAS_CRITERIO))
    keys = [m['key'] for m in METRICAS_CRITERIO]
    check("sin duplicados", len(keys) == len(set(keys)))
    check("incluye métricas clave", {'pedidos_completados','ventas_cop','es_fundador','onboarding_completado'} <= set(keys))
    check("KEYS coincide", METRICAS_CRITERIO_KEYS == set(keys))

    print("\n[2] Las métricas existen en el servicio (no inventadas)")
    nb = open(os.path.join(os.path.dirname(__file__), '..', 'api', 'utils', 'badge_verification_service.py'), encoding='utf-8').read()
    faltantes = [k for k in keys if f"metricas['{k}']" not in nb]
    check(f"todas las métricas se calculan en el servicio (faltan: {faltantes})", not faltantes)

    print("\n[3] _evaluar_criterio (operadores)")
    from src.api.utils.badge_verification_service import BadgeVerificationService as B
    check(">= cumple", B._evaluar_criterio(10, '>=', 10) is True)
    check("> no cumple en igualdad", B._evaluar_criterio(10, '>', 10) is False)
    check("< cumple", B._evaluar_criterio(3, '<', 5) is True)
    check("== cumple", B._evaluar_criterio(5, '==', 5) is True)

    print("\n[4] Endpoints registrados")
    import src.api.admin_api as api
    check("list_metricas_criterio existe", hasattr(api, 'list_metricas_criterio'))
    check("preview_criterio existe", hasattr(api, 'preview_criterio'))
    src = inspect.getsource(api.preview_criterio)
    check("preview valida métrica conocida", 'METRICAS_CRITERIO_KEYS' in src)
    check("preview valida operador", 'OPERADORES_CRITERIO' in src)
    check("preview cuenta cumplen/revisados (no escribe)", 'cumplen' in src and 'commit' not in src)
    check("preview acotado (CAP) sin cap silencioso", 'capado' in src)

    print(f"\n{'='*50}\n  RESULTADO: {PASS} pasaron, {FAIL} fallaron\n{'='*50}")
    return 0 if FAIL == 0 else 1


if __name__ == '__main__':
    sys.exit(main())
