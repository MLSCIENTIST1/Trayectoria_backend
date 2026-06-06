"""
Test de moderación global de reseñas (Admin Panel — Sprint A43).

Ejecutar:
    PYTHONUTF8=1 venv/Scripts/python.exe src/tests_apis/test_admin_resenas_a43.py
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
    from src.api.utils.resenas_service import normalizar_email, evaluar_resena_sospechosa

    print("\n[1] normalizar_email")
    check("minúsculas + trim", normalizar_email('  Foo@BAR.com ') == 'foo@bar.com')
    check("None → ''", normalizar_email(None) == '')

    print("\n[2] evaluar_resena_sospechosa")
    ok = evaluar_resena_sospechosa({'rating': 4, 'comentario': 'Buen producto, llegó a tiempo y bien empacado', 'verificado': True})
    check("reseña normal verificada → no sospechosa", ok['sospechosa'] is False)
    s1 = evaluar_resena_sospechosa({'rating': 5, 'comentario': '', 'verificado': False})
    check("5★ sin texto y no verificada → sospechosa", s1['sospechosa'] is True)
    check("motivo no_verificada", 'no_verificada' in s1['motivos'])
    check("motivo comentario_minimo", 'comentario_minimo' in s1['motivos'])
    check("motivo extremo_sin_texto", 'extremo_sin_texto' in s1['motivos'])
    s2 = evaluar_resena_sospechosa({'rating': 1, 'comentario': 'x', 'verificado': True})
    check("1★ con texto mínimo → sospechosa", s2['sospechosa'] is True)
    check("rating inválido marcado", 'rating_invalido' in evaluar_resena_sospechosa({'rating': 9, 'comentario': 'algo largo aquí', 'verificado': True})['motivos'])
    check("dict vacío no rompe", isinstance(evaluar_resena_sospechosa({}), dict))
    check("None no rompe", isinstance(evaluar_resena_sospechosa(None), dict))

    print("\n[3] Endpoints")
    import src.api.admin_api as api
    for fn in ['admin_resenas', 'moderar_resena_admin', 'listar_baneos_resenas', 'banear_resenador', 'desbanear_resenador']:
        check(f"{fn} existe", hasattr(api, fn))
    src_list = inspect.getsource(api.admin_resenas)
    check("listado marca sospechosa", 'evaluar_resena_sospechosa' in src_list)
    check("listado marca baneados", 'resena_baneos' in src_list)
    src_mod = inspect.getsource(api.moderar_resena_admin)
    check("moderar valida aprobar/ocultar", "'aprobar'" in src_mod and "'ocultar'" in src_mod)
    check("moderar audita", 'registrar_auditoria' in src_mod)
    src_ban = inspect.getsource(api.banear_resenador)
    check("banear oculta reseñas existentes", 'UPDATE producto_reviews SET aprobado = FALSE' in src_ban)
    check("banear audita (excluir)", "registrar_auditoria('excluir'" in src_ban)

    print("\n[4] Wire en crear_resena + migración")
    import src.api.tiendas.resenas_api as r
    src_crear = inspect.getsource(r.crear_resena)
    check("crear_resena chequea baneo", 'resena_baneos' in src_crear)
    check("crear_resena no aprueba si baneado", 'not _baneado' in src_crear)
    import src as _src
    check("migración resena_baneos en create_app", 'CREATE TABLE IF NOT EXISTS resena_baneos' in inspect.getsource(_src.create_app))

    print(f"\n{'='*50}\n  RESULTADO: {PASS} pasaron, {FAIL} fallaron\n{'='*50}")
    return 0 if FAIL == 0 else 1


if __name__ == '__main__':
    sys.exit(main())
