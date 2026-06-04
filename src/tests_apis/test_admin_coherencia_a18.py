"""
Test del validador de coherencia por tier (Admin Panel — Sprint A18).

Ejecutar:
    PYTHONUTF8=1 venv/Scripts/python.exe src/tests_apis/test_admin_coherencia_a18.py
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
    from src.models.colombia_data.ratings.config_gamificacion import evaluar_coherencia_tier as ev

    # Catálogo de ejemplo (misma métrica pedidos_completados, operador >=)
    otros = [
        {'nivel': 1, 'criterio_valor': 1,  'criterio_operador': '>=', 'nombre': 'Primera venta'},
        {'nivel': 3, 'criterio_valor': 50, 'criterio_operador': '>=', 'nombre': 'Vendedor Oro'},
    ]

    print("\n[1] Coherente (>= creciente con tier)")
    check("tier 2 con 10 (entre 1 y 50) → sin avisos", ev(2, 'pedidos_completados', '>=', 10, otros) == [])
    check("tier 5 con 100 → sin avisos", ev(5, 'pedidos_completados', '>=', 100, otros) == [])

    print("\n[2] Incoherente (>= )")
    a = ev(2, 'pedidos_completados', '>=', 100, otros)  # tier 2 exige 100 > Oro(50)
    check("tier 2 con 100 (> Oro tier3=50) → avisa", len(a) >= 1)
    b = ev(4, 'pedidos_completados', '>=', 0, otros)  # tier 4 exige 0 < tier1=1 y tier3=50
    check("tier 4 con 0 (< menores) → avisa", len(b) >= 1)

    print("\n[3] Operador inverso (<=: menos es más difícil, ej. tiempo_respuesta)")
    otros_inv = [
        {'nivel': 1, 'criterio_valor': 24, 'criterio_operador': '<=', 'nombre': 'Responde en 24h'},
        {'nivel': 3, 'criterio_valor': 4,  'criterio_operador': '<=', 'nombre': 'Responde en 4h'},
    ]
    check("tier 5 con 1h (< 4h) → coherente", ev(5, 'tiempo_respuesta_hrs', '<=', 1, otros_inv) == [])
    check("tier 5 con 10h (> tier3=4) → avisa (más fácil)", len(ev(5, 'tiempo_respuesta_hrs', '<=', 10, otros_inv)) >= 1)

    print("\n[4] No evaluable / aislado")
    check("operador == → sin avisos (no monótono)", ev(2, 'x', '==', 5, otros) == [])
    check("métrica distinta → ignora otros",
          ev(2, 'otra_metrica', '>=', 999,
             [{'nivel': 3, 'criterio_valor': 1, 'criterio_tipo': 'pedidos_completados',
               'criterio_operador': '>=', 'nombre': 'x'}]) == [])
    check("sin otros → coherente", ev(3, 'pedidos_completados', '>=', 30, []) == [])
    check("ignora mismo nivel", ev(3, 'pedidos_completados', '>=', 999, [{'nivel':3,'criterio_valor':1,'criterio_operador':'>=','nombre':'x'}]) == [])

    print("\n[5] Robustez")
    check("valor inválido → sin crash", ev(2, 'x', '>=', 'abc', otros) == [])
    check("otro con valor None → se ignora", ev(2, 'pedidos_completados', '>=', 10, [{'nivel':1,'criterio_valor':None,'criterio_operador':'>=','nombre':'x'}]) == [])

    print("\n[6] Endpoint registrado")
    import src.api.admin_api as api
    check("coherencia_insignia existe", hasattr(api, 'coherencia_insignia'))
    src = inspect.getsource(api.coherencia_insignia)
    check("excluye el propio badge por id", 'propio_id' in src)
    check("no bloquea (devuelve advertencias)", 'advertencias' in src and 'coherente' in src)

    print(f"\n{'='*50}\n  RESULTADO: {PASS} pasaron, {FAIL} fallaron\n{'='*50}")
    return 0 if FAIL == 0 else 1


if __name__ == '__main__':
    sys.exit(main())
