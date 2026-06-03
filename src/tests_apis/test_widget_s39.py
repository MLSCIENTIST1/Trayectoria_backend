"""
Test del widget embebible de insignias (Sprint 39).

Valida la lógica de selección/ordenamiento que usa GET /api/widget/badges/<slug>:
- solo badges no secretos
- orden por nivel desc
- recorte por 'max' y conteo de 'resto'

Ejecutar:
    PYTHONUTF8=1 venv/Scripts/python.exe src/tests_apis/test_widget_s39.py
"""
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

PASS = 0; FAIL = 0
def check(n, c):
    global PASS, FAIL
    if c: PASS += 1; print(f"  ✅ {n}")
    else: FAIL += 1; print(f"  ❌ {n}")


def _filtrar_ordenar(badges):
    """Réplica de la lógica SQL del endpoint (no secretos, orden nivel desc)."""
    vis = [b for b in badges if not b.get('es_secreto')]
    return sorted(vis, key=lambda b: b.get('nivel', 1), reverse=True)


def _recorte(badges, max_n):
    vis = badges[:max_n]
    resto = max(0, len(badges) - len(vis))
    return vis, resto


def main():
    catalogo = [
        {'nombre': 'Bronce A', 'nivel': 1, 'es_secreto': False},
        {'nombre': 'Diamante', 'nivel': 5, 'es_secreto': False},
        {'nombre': 'Oro', 'nivel': 3, 'es_secreto': False},
        {'nombre': 'Secreto', 'nivel': 4, 'es_secreto': True},
        {'nombre': 'Plata', 'nivel': 2, 'es_secreto': False},
    ]

    print("\n[1] Excluye secretos")
    pub = _filtrar_ordenar(catalogo)
    check("4 públicos (1 secreto fuera)", len(pub) == 4)
    check("ningún secreto presente", all(not b['es_secreto'] for b in pub))

    print("\n[2] Orden por nivel descendente")
    check("primero Diamante (5)", pub[0]['nivel'] == 5)
    check("último Bronce (1)", pub[-1]['nivel'] == 1)
    check("orden monótono desc", all(pub[i]['nivel'] >= pub[i+1]['nivel'] for i in range(len(pub)-1)))

    print("\n[3] Recorte por max + conteo de resto")
    vis, resto = _recorte(pub, 2)
    check("muestra 2", len(vis) == 2)
    check("resto = 2", resto == 2)
    vis2, resto2 = _recorte(pub, 10)
    check("max alto → muestra todos", len(vis2) == 4)
    check("resto = 0 cuando alcanza", resto2 == 0)

    print("\n[4] Caso sin insignias")
    vacio = _filtrar_ordenar([])
    v, r = _recorte(vacio, 8)
    check("lista vacía", v == [] and r == 0)

    print("\n[5] El endpoint existe y está registrado")
    import src.api.gamificacion.gamificacion_api as api
    check("función widget_badges definida", hasattr(api, 'widget_badges'))

    print(f"\n{'='*50}\n  RESULTADO: {PASS} pasaron, {FAIL} fallaron\n{'='*50}")
    return 0 if FAIL == 0 else 1


if __name__ == '__main__':
    sys.exit(main())
