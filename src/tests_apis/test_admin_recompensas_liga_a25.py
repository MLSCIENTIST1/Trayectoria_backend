"""
Test de recompensas automáticas de liga (Admin Panel — Sprint A25).

Ejecutar:
    PYTHONUTF8=1 venv/Scripts/python.exe src/tests_apis/test_admin_recompensas_liga_a25.py
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
        validar_recompensas_liga, recompensa_por_posicion, construir_plan_recompensas,
        get_recompensas_liga, RECOMPENSAS_LIGA_DEFAULT
    )

    print("\n[1] DEFAULT")
    check("default top-3", len(RECOMPENSAS_LIGA_DEFAULT) == 3)
    check("puesto 1 da más XP que el 3", RECOMPENSAS_LIGA_DEFAULT[0]['xp'] > RECOMPENSAS_LIGA_DEFAULT[2]['xp'])
    check("get_recompensas_liga sin BD → default", get_recompensas_liga()[0]['pos'] == 1)

    print("\n[2] validar_recompensas_liga — válidos")
    ok, limpio, err = validar_recompensas_liga([{'pos': 2, 'xp': 100, 'tukoins': 50}, {'pos': 1, 'xp': 200, 'tukoins': 80}])
    check("válido → ok", ok and err is None)
    check("se ordena por posición", [r['pos'] for r in limpio] == [1, 2])

    print("\n[3] validar_recompensas_liga — inválidos")
    check("no-lista → inválido", validar_recompensas_liga({})[0] is False)
    check("lista vacía → inválido", validar_recompensas_liga([])[0] is False)
    check("pos 0 → inválido", validar_recompensas_liga([{'pos': 0, 'xp': 1, 'tukoins': 1}])[0] is False)
    check("pos 11 → inválido", validar_recompensas_liga([{'pos': 11, 'xp': 1, 'tukoins': 1}])[0] is False)
    check("pos duplicada → inválido", validar_recompensas_liga([{'pos':1,'xp':1,'tukoins':1},{'pos':1,'xp':2,'tukoins':2}])[0] is False)
    check("xp gigante → inválido", validar_recompensas_liga([{'pos':1,'xp':999999,'tukoins':1}])[0] is False)
    check("no numérico → inválido", validar_recompensas_liga([{'pos':1,'xp':'x','tukoins':1}])[0] is False)

    print("\n[4] recompensa_por_posicion — función pura")
    cfg = [{'pos':1,'xp':500,'tukoins':200},{'pos':2,'xp':300,'tukoins':120}]
    check("pos 1 → 500/200", recompensa_por_posicion(cfg, 1) == {'xp':500,'tukoins':200})
    check("pos 3 (sin premio) → None", recompensa_por_posicion(cfg, 3) is None)

    print("\n[5] construir_plan_recompensas — función pura")
    filas = [
        (10, 'Top', 'Bogota', 'ropa', '', 'a', 50),
        (20, 'Seg', 'Bogota', 'ropa', '', 'b', 40),
        (30, 'Ter', 'Bogota', 'ropa', '', 'c', 30),
        (40, 'Cua', 'Bogota', 'ropa', '', 'd', 20),
    ]
    plan = construir_plan_recompensas(filas, RECOMPENSAS_LIGA_DEFAULT, [])
    check("plan premia 3 puestos", len(plan) == 3)
    check("puesto 1 es el de mayor puntaje (id 10)", plan[0]['negocio_id'] == 10 and plan[0]['posicion'] == 1)
    check("el 4º no recibe premio", all(p['negocio_id'] != 40 for p in plan))

    print("\n[6] construir_plan — los vetados NO ocupan podio")
    plan2 = construir_plan_recompensas(filas, RECOMPENSAS_LIGA_DEFAULT, [10])  # vetar al líder
    check("líder vetado no está en el plan", all(p['negocio_id'] != 10 for p in plan2))
    check("el 2º sube a puesto 1", plan2[0]['negocio_id'] == 20 and plan2[0]['posicion'] == 1)
    check("ahora entra el 4º al podio (puesto 3)", any(p['negocio_id'] == 40 for p in plan2))

    print("\n[7] construir_plan — bordes")
    check("sin filas → plan vacío", construir_plan_recompensas([], RECOMPENSAS_LIGA_DEFAULT, []) == [])
    check("premio 0 no genera entrada", construir_plan_recompensas(filas, [{'pos':1,'xp':0,'tukoins':0}], []) == [])

    print("\n[8] Servicio + endpoints")
    import src.api.utils.liga_recompensas_service as svc
    check("calcular_recompensas_liga existe", hasattr(svc, 'calcular_recompensas_liga'))
    check("otorgar_recompensas_liga existe", hasattr(svc, 'otorgar_recompensas_liga'))
    check("historial_recompensas_liga existe", hasattr(svc, 'historial_recompensas_liga'))
    import inspect
    src_otorgar = inspect.getsource(svc.otorgar_recompensas_liga)
    check("otorgar es idempotente (chequea liga_recompensas)", 'liga_recompensas' in src_otorgar and 'ya_premiado' in src_otorgar)
    check("otorgar usa ON CONFLICT DO NOTHING", 'ON CONFLICT' in src_otorgar)

    import src.api.admin_api as api
    check("get_liga_recompensas existe", hasattr(api, 'get_liga_recompensas'))
    check("update_liga_recompensas_config existe", hasattr(api, 'update_liga_recompensas_config'))
    check("simular_liga_recompensas existe", hasattr(api, 'simular_liga_recompensas'))
    check("ejecutar_liga_recompensas existe", hasattr(api, 'ejecutar_liga_recompensas'))
    src_ej = inspect.getsource(api.ejecutar_liga_recompensas)
    check("ejecutar exige superadmin", 'superadmin_required' in src_ej)
    check("ejecutar exige confirmar", "confirmar" in src_ej)
    check("ejecutar audita", 'registrar_auditoria' in src_ej)

    print(f"\n{'='*50}\n  RESULTADO: {PASS} pasaron, {FAIL} fallaron\n{'='*50}")
    return 0 if FAIL == 0 else 1


if __name__ == '__main__':
    sys.exit(main())
