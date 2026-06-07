"""
Documentación Maestra — integridad del CONTENIDO (Fase 2, seed).

Ejecutar:
    PYTHONUTF8=1 venv/Scripts/python.exe src/tests_apis/test_docs_tecnicas_seed.py
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
    from src.models.colombia_data.docs_tecnicas_seed import SEED_DOCS, seed_docs_tecnicas
    from src.api.ayuda.docs_tecnicas_api import SECCIONES_DOC, NIVELES_VALIDOS

    areas_tax = {s['area'] for s in SECCIONES_DOC}
    claves = [d['clave'] for d in SEED_DOCS]

    print("\n[1] Integridad del contenido")
    check("claves únicas", len(claves) == len(set(claves)))
    check("todas con título y contenido", all(d.get('titulo') and d.get('contenido') for d in SEED_DOCS))
    check("niveles válidos", all(d['nivel'] in NIVELES_VALIDOS for d in SEED_DOCS))
    check("áreas dentro de la taxonomía", all(d['area'] in areas_tax for d in SEED_DOCS))
    check("claves con prefijo doc-", all(d['clave'].startswith('doc-') for d in SEED_DOCS))

    print("\n[2] Cobertura mínima del lote 1")
    claves_set = set(claves)
    for must in ['doc-back-init', 'doc-back-run', 'doc-back-password-reset', 'doc-back-blueprints',
                 'doc-errores-comunes', 'doc-front-worker', 'doc-glosario']:
        check(f"incluye {must}", must in claves_set)
    niveles = {d['nivel'] for d in SEED_DOCS}
    check("hay contenido 🔴 superadmin (seguridad)", 'superadmin' in niveles)
    check("hay contenido 🟢 público", 'publico' in niveles)

    print("\n[3] Seeder existe y es callable")
    check("seed_docs_tecnicas es función", callable(seed_docs_tecnicas))

    print(f"\n{'='*52}\n  RESULTADO: {PASS} pasaron, {FAIL} fallaron\n{'='*52}")
    return 0 if FAIL == 0 else 1


if __name__ == '__main__':
    sys.exit(main())
