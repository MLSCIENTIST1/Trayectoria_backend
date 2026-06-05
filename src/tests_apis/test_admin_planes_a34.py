"""
Test de gestión avanzada de planes (Admin Panel — Sprint A34).

Ejecutar:
    PYTHONUTF8=1 venv/Scripts/python.exe src/tests_apis/test_admin_planes_a34.py
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
    from src.models.feature_models import validar_plan_datos

    print("\n[1] validar_plan_datos — válidos")
    ok, limpio, err = validar_plan_datos({
        'nombre': 'Deluxe', 'precio_mensual': 49900, 'precio_anual': 499000,
        'color': '#f59e0b', 'icono': '👑', 'orden': 4, 'activo': True, 'descripcion': 'Top'
    })
    check("válido → ok", ok and err is None)
    check("precios redondeados a float", limpio['precio_mensual'] == 49900.0)
    check("activo bool", limpio['activo'] is True)
    check("color conservado", limpio['color'] == '#f59e0b')

    print("\n[2] Parciales (solo los campos enviados)")
    ok2, limpio2, _ = validar_plan_datos({'precio_mensual': 0})
    check("solo precio → limpio solo trae precio", ok2 and limpio2 == {'precio_mensual': 0.0})
    ok3, limpio3, _ = validar_plan_datos({'activo': False})
    check("solo activo", ok3 and limpio3 == {'activo': False})
    check("vacío → ok, sin cambios", validar_plan_datos({}) == (True, {}, None))

    print("\n[3] Inválidos")
    check("no-dict → inválido", validar_plan_datos('x')[0] is False)
    check("nombre vacío (si se envía) → inválido", validar_plan_datos({'nombre': '  '})[0] is False)
    check("precio negativo → inválido", validar_plan_datos({'precio_mensual': -1})[0] is False)
    check("precio no numérico → inválido", validar_plan_datos({'precio_anual': 'x'})[0] is False)
    check("color mal formado → inválido", validar_plan_datos({'color': 'rojo'})[0] is False)
    check("color sin # → inválido", validar_plan_datos({'color': 'f59e0b'})[0] is False)
    check("orden no entero → inválido", validar_plan_datos({'orden': 'x'})[0] is False)

    print("\n[4] Endpoint")
    import src.api.admin_features_api as feat
    check("update_plan_datos existe", hasattr(feat, 'update_plan_datos'))
    src_u = inspect.getsource(feat.update_plan_datos)
    check("valida con validar_plan_datos", 'validar_plan_datos' in src_u)
    check("404 si no existe", '404' in src_u)
    check("audita el cambio", 'registrar_auditoria' in src_u)
    check("setea solo campos limpios", 'setattr(plan' in src_u)

    print(f"\n{'='*50}\n  RESULTADO: {PASS} pasaron, {FAIL} fallaron\n{'='*50}")
    return 0 if FAIL == 0 else 1


if __name__ == '__main__':
    sys.exit(main())
