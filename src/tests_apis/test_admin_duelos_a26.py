"""
Test de moderación de duelos (Admin Panel — Sprint A26).

Ejecutar:
    PYTHONUTF8=1 venv/Scripts/python.exe src/tests_apis/test_admin_duelos_a26.py
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
    from src.models.colombia_data.ratings.duelo import (
        puede_cancelar_duelo, ESTADOS_CANCELABLES, determinar_ganador
    )

    print("\n[1] puede_cancelar_duelo — función pura")
    check("pendiente → cancelable", puede_cancelar_duelo('pendiente') is True)
    check("activo → cancelable", puede_cancelar_duelo('activo') is True)
    check("finalizado → NO cancelable", puede_cancelar_duelo('finalizado') is False)
    check("rechazado → NO cancelable", puede_cancelar_duelo('rechazado') is False)
    check("expirado → NO cancelable", puede_cancelar_duelo('expirado') is False)
    check("cancelado → NO cancelable (idempotente)", puede_cancelar_duelo('cancelado') is False)
    check("mayúsculas/espacios tolerados", puede_cancelar_duelo('  ACTIVO ') is True)
    check("None → NO cancelable", puede_cancelar_duelo(None) is False)
    check("estado raro → NO cancelable", puede_cancelar_duelo('zzz') is False)

    print("\n[2] ESTADOS_CANCELABLES")
    check("solo pendiente y activo", ESTADOS_CANCELABLES == {'pendiente', 'activo'})

    print("\n[3] determinar_ganador (no se rompe con la moderación)")
    check("gana el retador", determinar_ganador(1, 10, 2, 5) == 1)
    check("gana el retado", determinar_ganador(1, 3, 2, 9) == 2)
    check("empate → None", determinar_ganador(1, 4, 2, 4) is None)

    print("\n[4] Endpoints + auditoría")
    import src.api.admin_api as api
    check("admin_duelos existe", hasattr(api, 'admin_duelos'))
    check("cancelar_duelo existe", hasattr(api, 'cancelar_duelo'))
    import inspect
    src_cancel = inspect.getsource(api.cancelar_duelo)
    check("cancelar valida puede_cancelar_duelo", 'puede_cancelar_duelo' in src_cancel)
    check("cancelar pone estado 'cancelado'", "'cancelado'" in src_cancel)
    check("cancelar audita", 'registrar_auditoria' in src_cancel)
    src_list = inspect.getsource(api.admin_duelos)
    check("listado hace join de nombres de negocio", 'nombre_negocio' in src_list)
    check("listado calcula resumen por estado", 'GROUP BY LOWER(estado)' in src_list)

    print(f"\n{'='*50}\n  RESULTADO: {PASS} pasaron, {FAIL} fallaron\n{'='*50}")
    return 0 if FAIL == 0 else 1


if __name__ == '__main__':
    sys.exit(main())
