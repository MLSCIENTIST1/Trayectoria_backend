"""
Test del editor de la tienda de ítems (Admin Panel — Sprint A8).
Valida el validador puro de ítems y el registro de endpoints.

Ejecutar:
    PYTHONUTF8=1 venv/Scripts/python.exe src/tests_apis/test_admin_tienda_a8.py
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
    from src.models.colombia_data.ratings.config_gamificacion import (
        validar_item_tienda, TIPOS_ITEM_VALIDOS
    )

    print("\n[1] Edición (sin requerir código)")
    ok, limpio, err = validar_item_tienda({'precio_tukoins': 50, 'activo': False})
    check("válido → ok", ok is True and err is None)
    check("precio normalizado a int", limpio['precio_tukoins'] == 50)
    check("activo bool", limpio['activo'] is False)

    print("\n[2] Validaciones de precio")
    ok2, _, e2 = validar_item_tienda({'precio_tukoins': -5})
    check("precio negativo → inválido", ok2 is False)
    ok3, _, e3 = validar_item_tienda({'precio_tukoins': 'abc'})
    check("precio no numérico → inválido", ok3 is False)
    ok4, _, e4 = validar_item_tienda({'precio_tukoins': 99999999})
    check("precio fuera de rango → inválido", ok4 is False)

    print("\n[3] nivel_requerido")
    ok5, l5, _ = validar_item_tienda({'nivel_requerido': 5})
    check("nivel válido", ok5 and l5['nivel_requerido'] == 5)
    ok6, _, _ = validar_item_tienda({'nivel_requerido': 0})
    check("nivel 0 → inválido", ok6 is False)

    print("\n[4] tipo se sanea contra whitelist")
    _, l7, _ = validar_item_tienda({'tipo': 'tema_color', 'nombre': 'X'})
    check("tipo válido se conserva", l7['tipo'] == 'tema_color')
    _, l8, _ = validar_item_tienda({'tipo': 'cualquier_cosa', 'nombre': 'X'})
    check("tipo desconocido → 'otro'", l8['tipo'] == 'otro')

    print("\n[5] Creación (requiere código + nombre + precio)")
    ok9, l9, _ = validar_item_tienda({'codigo': 'Mi Item', 'nombre': 'Mi Ítem', 'precio_tukoins': 30}, requerir_codigo=True)
    check("creación válida → ok", ok9 is True)
    check("código normalizado (lower + _)", l9['codigo'] == 'mi_item')
    check("tipo por defecto 'otro'", l9.get('tipo') == 'otro')

    ok10, _, e10 = validar_item_tienda({'nombre': 'Sin código', 'precio_tukoins': 10}, requerir_codigo=True)
    check("sin código → inválido", ok10 is False)
    ok11, _, e11 = validar_item_tienda({'codigo': 'x', 'precio_tukoins': 10}, requerir_codigo=True)
    check("sin nombre → inválido", ok11 is False)

    print("\n[6] Saneo de longitudes / payload inválido")
    _, l12, _ = validar_item_tienda({'nombre': 'N' * 300})
    check("nombre se recorta a 100", len(l12['nombre']) == 100)
    ok13, _, _ = validar_item_tienda("no-dict")
    check("payload no-dict → inválido", ok13 is False)
    ok14, _, _ = validar_item_tienda({})
    check("payload vacío (edición) → inválido", ok14 is False)

    print("\n[7] whitelist de tipos y endpoints")
    check("TIPOS_ITEM_VALIDOS tiene tipos clave",
          {'tema_color', 'marco_logo', 'banner_tienda'} <= TIPOS_ITEM_VALIDOS)
    import src.api.admin_api as api
    check("get_gamif_tienda existe", hasattr(api, 'get_gamif_tienda'))
    check("update_gamif_tienda_item existe", hasattr(api, 'update_gamif_tienda_item'))
    check("create_gamif_tienda_item existe", hasattr(api, 'create_gamif_tienda_item'))

    print(f"\n{'='*50}\n  RESULTADO: {PASS} pasaron, {FAIL} fallaron\n{'='*50}")
    return 0 if FAIL == 0 else 1


if __name__ == '__main__':
    sys.exit(main())
