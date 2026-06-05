"""
Test de Ficha 360° del negocio (Admin Panel — Sprint A29).

Ejecutar:
    PYTHONUTF8=1 venv/Scripts/python.exe src/tests_apis/test_admin_ficha360_a29.py
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

    print("\n[1] Endpoint existe y está protegido")
    check("ficha_negocio_360 existe", hasattr(api, 'ficha_negocio_360'))
    src_f = inspect.getsource(api.ficha_negocio_360)
    check("requiere permiso 'negocios'", "requiere_permiso('negocios')" in src_f)
    check("ruta /negocios/<id>/ficha360", 'ficha360' in src_f or 'ficha360' in inspect.getsource(api))

    print("\n[2] Agrega los bloques esperados")
    for bloque in ['negocio', 'dueno', 'suscripcion', 'gamificacion', 'pedidos', 'videos', 'productos', 'insignias']:
        check(f"incluye bloque '{bloque}'", f"'{bloque}'" in src_f)

    print("\n[3] Usa columnas correctas de negocios")
    check("usa id_negocio", 'id_negocio' in src_f)
    check("usa nombre_negocio", 'nombre_negocio' in src_f)
    check("NO usa el join roto n.nombre/n.id suelto", 'n.nombre ' not in src_f)

    print("\n[4] Tolerancia a fallos (cada bloque en try/except)")
    check("suscripción tolerante", 'suscripción no disponible' in src_f or 'ficha360] suscrip' in src_f)
    check("gamificación tolerante", 'gamificación no disponible' in src_f or 'ficha360] gamif' in src_f)
    check("usa _scalar_admin para conteos", '_scalar_admin' in src_f)

    print("\n[5] Conteos correctos")
    check("pedidos entregados filtra estado", "estado = 'entregado'" in src_f)
    check("videos por estado_moderacion", 'estado_moderacion' in src_f)
    check("negocio no encontrado → 404", '404' in src_f)

    print(f"\n{'='*50}\n  RESULTADO: {PASS} pasaron, {FAIL} fallaron\n{'='*50}")
    return 0 if FAIL == 0 else 1


if __name__ == '__main__':
    sys.exit(main())
