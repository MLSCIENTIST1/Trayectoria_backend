"""
Test del CRUD de insignias (Admin Panel — Sprint A15).

Ejecutar:
    PYTHONUTF8=1 venv/Scripts/python.exe src/tests_apis/test_admin_insignias_a15.py
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
        validar_badge, OPERADORES_CRITERIO, TIERS_BADGE
    )

    print("\n[1] Edición (sin requerir código)")
    ok, limpio, err = validar_badge({'nombre': 'Nuevo', 'nivel': 3, 'puntos': 50})
    check("válido → ok", ok and err is None)
    check("nivel 3", limpio['nivel'] == 3)
    check("activo bool si viene", validar_badge({'activo': False})[1]['activo'] is False)

    print("\n[2] Validaciones")
    check("nivel 6 → inválido", validar_badge({'nivel': 6})[0] is False)
    check("nivel 0 → inválido", validar_badge({'nivel': 0})[0] is False)
    check("operador inválido → falla", validar_badge({'criterio_operador': '=>'})[0] is False)
    check("operador válido", validar_badge({'criterio_operador': '>='})[0] is True)
    check("criterio_valor no numérico → falla", validar_badge({'criterio_valor': 'x'})[0] is False)
    check("puntos fuera de rango → falla", validar_badge({'puntos': 999999})[0] is False)
    check("payload vacío (edición) → inválido", validar_badge({})[0] is False)
    check("no-dict → inválido", validar_badge('x')[0] is False)

    print("\n[3] Creación (requiere codigo + nombre + criterio)")
    ok2, l2, _ = validar_badge({'codigo': 'Mi Badge!', 'nombre': 'Mi Badge',
                                'criterio_tipo': 'ventas_cop', 'criterio_valor': 1000000}, requerir_codigo=True)
    check("creación válida", ok2 is True)
    check("codigo normalizado", l2['codigo'] == 'mi_badge')
    check("operador por defecto >=", l2['criterio_operador'] == '>=')
    check("sin criterio_tipo → inválido", validar_badge({'codigo': 'x', 'nombre': 'X'}, requerir_codigo=True)[0] is False)
    check("sin nombre → inválido", validar_badge({'codigo': 'x', 'criterio_tipo': 't', 'criterio_valor': 1}, requerir_codigo=True)[0] is False)

    print("\n[4] Saneo de longitudes")
    check("descripcion recortada a 255", len(validar_badge({'descripcion': 'd'*400})[1]['descripcion']) == 255)
    check("TIERS 1-5", set(TIERS_BADGE.keys()) == {1,2,3,4,5})
    check("operadores incluyen los básicos", {'>=','<=','=='} <= OPERADORES_CRITERIO)

    print("\n[5] Endpoints + seguridad")
    import src.api.admin_api as api
    check("list_insignias existe", hasattr(api, 'list_insignias'))
    check("create_insignia existe", hasattr(api, 'create_insignia'))
    check("update_insignia existe", hasattr(api, 'update_insignia'))
    check("delete_insignia existe", hasattr(api, 'delete_insignia'))
    check("delete exige superadmin", "@superadmin_required" in inspect.getsource(api.delete_insignia))
    check("update marca editado_admin", "editado_admin = True" in inspect.getsource(api.update_insignia))
    check("delete bloquea si fue otorgada", "total_otorgados" in inspect.getsource(api.delete_insignia))

    print("\n[6] El seeder respeta editado_admin")
    import src.models.colombia_data.ratings.negocio_badge as nb
    src = inspect.getsource(nb.seed_badges_catalogo)
    check("seeder salta badges editados por admin", "editado_admin" in src)

    print(f"\n{'='*50}\n  RESULTADO: {PASS} pasaron, {FAIL} fallaron\n{'='*50}")
    return 0 if FAIL == 0 else 1


if __name__ == '__main__':
    sys.exit(main())
