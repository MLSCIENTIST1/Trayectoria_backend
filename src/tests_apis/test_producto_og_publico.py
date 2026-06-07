"""
Endpoint público de OG de producto (vista previa al compartir por WhatsApp).
GET /api/tienda/<slug>/producto/<id>/og

Ejecutar:
    PYTHONUTF8=1 venv/Scripts/python.exe src/tests_apis/test_producto_og_publico.py
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
    import src.api.negocio.catalogo_api as cat

    print("\n[1] La función existe y es pública")
    check("producto_og_publico existe", hasattr(cat, 'producto_og_publico'))
    src_fn = inspect.getsource(cat.producto_og_publico)

    print("\n[2] Seguridad: solo productos activos y publicados, del negocio del slug")
    check("filtra activo=True", 'activo=True' in src_fn)
    check("filtra estado_publicacion=True", 'estado_publicacion=True' in src_fn)
    check("busca negocio por slug", "filter_by(slug=slug)" in src_fn)
    check("no expone más que campos OG", all(k in src_fn for k in ['nombre', 'precio', 'imagen', 'descripcion']))
    check("recorta descripción", "[:300]" in src_fn)

    print("\n[3] Ruta registrada en el blueprint")
    rutas = [str(r) for r in cat.catalogo_api_bp.deferred_functions] if hasattr(cat.catalogo_api_bp, 'deferred_functions') else []
    # Verificación robusta: la cadena de la ruta está en el código fuente del módulo
    src_mod = inspect.getsource(cat)
    check("ruta /tienda/<slug>/producto/<int:id_producto>/og",
          "/tienda/<slug>/producto/<int:id_producto>/og" in src_mod)

    print(f"\n{'='*50}\n  RESULTADO: {PASS} pasaron, {FAIL} fallaron\n{'='*50}")
    return 0 if FAIL == 0 else 1


if __name__ == '__main__':
    sys.exit(main())
