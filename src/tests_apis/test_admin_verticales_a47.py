"""
Test de Verticales + overview de tienda avanzada (Admin Panel — Sprint A47).

Ejecutar:
    PYTHONUTF8=1 venv/Scripts/python.exe src/tests_apis/test_admin_verticales_a47.py
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
    from src.api.utils.verticales_service import etiqueta_vertical, VERTICALES_META

    print("\n[1] etiqueta_vertical — función pura")
    check("ecommerce", etiqueta_vertical('ecommerce')['label'] == 'Tienda / E-commerce')
    check("taller con ícono", etiqueta_vertical('taller')['icono'] == '🔧')
    check("restaurante", etiqueta_vertical('restaurante')['label'] == 'Restaurante')
    check("mecalink", etiqueta_vertical('mecalink')['tipo'] == 'mecalink')
    check("None → landing", etiqueta_vertical(None)['tipo'] == 'landing')
    check("mayúsculas/espacios", etiqueta_vertical('  TALLER ')['tipo'] == 'taller')
    desc = etiqueta_vertical('zzz_raro')
    check("desconocido → no rompe + ícono genérico", desc['icono'] == '🏷️' and desc['tipo'] == 'zzz_raro')
    check("VERTICALES_META incluye las claves clave",
          all(k in VERTICALES_META for k in ('ecommerce', 'taller', 'restaurante', 'mecalink')))

    print("\n[2] Endpoint")
    import src.api.admin_api as api
    check("verticales_overview existe", hasattr(api, 'verticales_overview'))
    src_v = inspect.getsource(api.verticales_overview)
    check("agrupa por tipo_pagina", 'tipo_pagina' in src_v)
    check("usa etiqueta_vertical", 'etiqueta_vertical' in src_v)
    check("excluye papelera", 'eliminado' in src_v)
    check("agrega cupones", 'FROM cupones' in src_v)
    check("agrega carritos abandonados", 'carritos_abandonados' in src_v and 'valor_recuperable' in src_v)
    check("agrega reseñas", 'producto_reviews' in src_v)
    check("requiere permiso negocios", "requiere_permiso('negocios')" in src_v)

    print(f"\n{'='*50}\n  RESULTADO: {PASS} pasaron, {FAIL} fallaron\n{'='*50}")
    return 0 if FAIL == 0 else 1


if __name__ == '__main__':
    sys.exit(main())
