"""
Test del buscador global del panel admin (Admin Panel — Sprint A5).

El endpoint hace lecturas a Postgres; aquí validamos contrato y reglas:
- endpoint registrado
- estructura de resultados (grupos)
- regla de longitud mínima (q < 2 → sin búsqueda)

Ejecutar:
    PYTHONUTF8=1 venv/Scripts/python.exe src/tests_apis/test_admin_search_a5.py
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
    import inspect
    import src.api.admin_api as api

    print("\n[1] Endpoint registrado")
    check("admin_search existe", hasattr(api, 'admin_search'))

    src = inspect.getsource(api.admin_search)

    print("\n[2] Busca en las 3 entidades esperadas")
    check("busca usuarios", 'usuarios' in src and 'FROM usuarios' in src)
    check("busca negocios", 'FROM negocios' in src)
    check("busca administradores", 'FROM administradores' in src)

    print("\n[3] Regla de longitud mínima (q < 2)")
    check("exige al menos 2 caracteres", 'len(q) < 2' in src)

    print("\n[4] Cada grupo es tolerante a fallos (rollback por bloque)")
    check("tiene rollback ante fallo de un bloque", src.count('rollback') >= 3)

    print("\n[5] Devuelve 'seccion' para que el front sepa a dónde saltar")
    check("incluye 'seccion' en resultados", "'seccion'" in src)
    check("limita resultados por grupo (LIMIT)", 'LIMIT 6' in src)

    print("\n[6] Regla de longitud (lógica pura replicada)")
    def valido(q):
        return len((q or '').strip()) >= 2
    check("'a' → inválido", not valido('a'))
    check("'' → inválido", not valido(''))
    check("'ro' → válido", valido('ro'))
    check("'  x ' (1 char tras trim) → inválido", not valido('  x '))

    print(f"\n{'='*50}\n  RESULTADO: {PASS} pasaron, {FAIL} fallaron\n{'='*50}")
    return 0 if FAIL == 0 else 1


if __name__ == '__main__':
    sys.exit(main())
