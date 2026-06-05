"""
Test de soft-delete + papelera (Admin Panel — Sprint A30).

Ejecutar:
    PYTHONUTF8=1 venv/Scripts/python.exe src/tests_apis/test_admin_papelera_a30.py
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

    print("\n[1] Endpoints existen")
    for fn in ['negocio_a_papelera', 'restaurar_negocio', 'usuario_a_papelera',
               'restaurar_usuario', 'listar_papelera']:
        check(f"{fn} existe", hasattr(api, fn))

    print("\n[2] Soft-delete de negocio")
    src_np = inspect.getsource(api.negocio_a_papelera)
    check("marca eliminado=TRUE", 'eliminado = TRUE' in src_np)
    check("desactiva (activo=FALSE) para ocultarlo de las vistas", 'activo = FALSE' in src_np)
    check("registra eliminado_por/en", 'eliminado_por' in src_np and 'eliminado_en = NOW()' in src_np)
    check("audita", 'registrar_auditoria' in src_np)
    check("404 si no existe", '404' in src_np)

    print("\n[3] Restaurar negocio")
    src_rn = inspect.getsource(api.restaurar_negocio)
    check("eliminado=FALSE", 'eliminado = FALSE' in src_rn)
    check("reactiva (activo=TRUE)", 'activo = TRUE' in src_rn)
    check("audita como restaurar", "registrar_auditoria('restaurar'" in src_rn)

    print("\n[4] Soft-delete de usuario")
    src_up = inspect.getsource(api.usuario_a_papelera)
    check("solo superadmin", 'superadmin_required' in src_up)
    check("bloquea a administradores", 'es_admin' in src_up)
    check("desactiva (active=FALSE) → login lo rechaza", 'active = FALSE' in src_up)
    check("marca eliminado=TRUE", 'eliminado = TRUE' in src_up)

    print("\n[5] Restaurar usuario")
    src_ru = inspect.getsource(api.restaurar_usuario)
    check("reactiva (active=TRUE)", 'active = TRUE' in src_ru)
    check("eliminado=FALSE", 'eliminado = FALSE' in src_ru)

    print("\n[6] Listado de papelera")
    src_lp = inspect.getsource(api.listar_papelera)
    check("lista negocios eliminados", 'negocios WHERE eliminado IS TRUE' in src_lp)
    check("lista usuarios eliminados", 'usuarios WHERE eliminado IS TRUE' in src_lp)

    print("\n[7] Los listados normales excluyen la papelera")
    src_lu = inspect.getsource(api.list_usuarios)
    check("list_usuarios excluye eliminado", 'eliminado' in src_lu and 'FALSE' in src_lu)
    import src.api.admin_features_api as feat
    src_ln = inspect.getsource(feat.list_negocios_with_plans)
    check("list_negocios_with_plans excluye eliminado", 'eliminado' in src_ln)

    print("\n[8] Login rechaza usuarios desactivados (cubre soft-delete)")
    import src.api.auth.auth_system as auth
    src_login = inspect.getsource(auth.login)
    check("login valida usuario.active", 'usuario.active' in src_login)

    print(f"\n{'='*50}\n  RESULTADO: {PASS} pasaron, {FAIL} fallaron\n{'='*50}")
    return 0 if FAIL == 0 else 1


if __name__ == '__main__':
    sys.exit(main())
