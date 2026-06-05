"""
Test de Challenges 2.0 — integración con gamificación (Admin Panel — Sprint A28).

Ejecutar:
    PYTHONUTF8=1 venv/Scripts/python.exe src/tests_apis/test_admin_challenges_a28.py
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
        validar_challenge_rewards, get_challenge_rewards, CHALLENGE_REWARDS_DEFAULT
    )

    print("\n[1] DEFAULT")
    check("xp_participar default 30", CHALLENGE_REWARDS_DEFAULT['xp_participar'] == 30)
    check("xp_ganador default 300", CHALLENGE_REWARDS_DEFAULT['xp_ganador'] == 300)
    check("ganador premia más que participar",
          CHALLENGE_REWARDS_DEFAULT['xp_ganador'] > CHALLENGE_REWARDS_DEFAULT['xp_participar'])
    check("get_challenge_rewards sin BD → default", get_challenge_rewards() == CHALLENGE_REWARDS_DEFAULT)

    print("\n[2] validar_challenge_rewards — válidos")
    ok, limpio, err = validar_challenge_rewards({'xp_participar': 40, 'tukoins_ganador': 200})
    check("válido → ok", ok and err is None)
    check("mezcla con defaults", limpio['xp_participar'] == 40 and limpio['tukoins_ganador'] == 200
          and limpio['xp_ganador'] == 300)
    ok2, limpio2, _ = validar_challenge_rewards({})
    check("vacío → defaults", ok2 and limpio2 == CHALLENGE_REWARDS_DEFAULT)

    print("\n[3] validar_challenge_rewards — inválidos")
    check("negativo → inválido", validar_challenge_rewards({'xp_participar': -1})[0] is False)
    check("gigante → inválido", validar_challenge_rewards({'xp_ganador': 999999})[0] is False)
    check("no numérico → inválido", validar_challenge_rewards({'tukoins_participar': 'x'})[0] is False)
    check("no-dict → inválido", validar_challenge_rewards('x')[0] is False)

    print("\n[4] Servicio de integración (idempotencia)")
    import src.api.utils.challenge_gamif_service as svc
    check("premiar_participacion_aprobada existe", hasattr(svc, 'premiar_participacion_aprobada'))
    check("finalizar_y_premiar existe", hasattr(svc, 'finalizar_y_premiar'))
    import inspect
    src_part = inspect.getsource(svc.premiar_participacion_aprobada)
    check("participación: chequea gamif_otorgado (idempotente)", 'gamif_otorgado' in src_part)
    check("participación: solo premia si estado aprobado", "'aprobado'" in src_part)
    src_fin = inspect.getsource(svc.finalizar_y_premiar)
    check("finalizar: chequea gamif_premiado (idempotente)", 'gamif_premiado' in src_fin)
    check("finalizar: ganador = más votos entre aprobadas", 'COUNT(cv.id)' in src_fin and "estado = 'aprobado'" in src_fin)
    check("finalizar: marca estado finalizado", "estado = 'finalizado'" in src_fin)
    check("finalizar: usa columnas correctas de negocios (id_negocio/nombre_negocio)",
          'id_negocio' in src_fin and 'nombre_negocio' in src_fin)

    print("\n[5] Endpoints + auditoría")
    import src.api.admin_api as api
    check("finalizar_challenge existe", hasattr(api, 'finalizar_challenge'))
    check("get_challenge_rewards_cfg existe", hasattr(api, 'get_challenge_rewards_cfg'))
    check("update_challenge_rewards_cfg existe", hasattr(api, 'update_challenge_rewards_cfg'))
    src_fc = inspect.getsource(api.finalizar_challenge)
    check("finalizar requiere permiso challenges", "requiere_permiso('challenges')" in src_fc)
    check("finalizar audita", 'registrar_auditoria' in src_fc)
    src_upd = inspect.getsource(api.update_participacion_estado)
    check("aprobar participación dispara premio gamif", 'premiar_participacion_aprobada' in src_upd)

    print(f"\n{'='*50}\n  RESULTADO: {PASS} pasaron, {FAIL} fallaron\n{'='*50}")
    return 0 if FAIL == 0 else 1


if __name__ == '__main__':
    sys.exit(main())
