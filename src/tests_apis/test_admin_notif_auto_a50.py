"""
Test de notificaciones automáticas del sistema (Admin Panel — Sprint A50).

Ejecutar:
    PYTHONUTF8=1 venv/Scripts/python.exe src/tests_apis/test_admin_notif_auto_a50.py
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
    from src.api.utils.notificaciones_service import construir_notificacion, notificar_negocio

    print("\n[1] construir_notificacion — función pura")
    pc = construir_notificacion('plan_cambiado', {'plan': 'Deluxe'})
    check("plan_cambiado tiene titulo/mensaje/prioridad", pc and all(k in pc for k in ('titulo', 'mensaje', 'prioridad')))
    check("plan_cambiado interpola el plan", 'Deluxe' in pc['mensaje'])
    check("plan_cambiado prioridad alta", pc['prioridad'] == 'alta')
    bg = construir_notificacion('badge_ganado', {'badge': 'Veterano'})
    check("badge_ganado interpola el badge", 'Veterano' in bg['mensaje'])
    sv = construir_notificacion('suscripcion_por_vencer', {'dias': 3})
    check("suscripcion_por_vencer interpola días", '3' in sv['mensaje'])
    check("recompensa_liga existe", construir_notificacion('recompensa_liga') is not None)
    check("evento desconocido → None", construir_notificacion('xyz') is None)
    check("None → None", construir_notificacion(None) is None)
    check("mayúsculas/espacios tolerados", construir_notificacion('  PLAN_CAMBIADO ') is not None)

    print("\n[2] notificar_negocio — a prueba de fallos")
    src_n = inspect.getsource(notificar_negocio)
    check("inserta en tabla notification", 'INSERT INTO notification' in src_n)
    check("resuelve dueño del negocio", 'usuario_id FROM negocios' in src_n)
    check("rollback ante error (no rompe)", 'rollback' in src_n)
    check("acepta evento (plantilla) o titulo/mensaje", "evento" in src_n and 'construir_notificacion' in src_n)
    # No lanza aunque la BD no esté (fuera de app context): devuelve False
    check("no lanza sin contexto BD", notificar_negocio(999999, evento='plan_cambiado', ctx={'plan': 'X'}) in (True, False))

    print("\n[3] Wires en eventos del sistema")
    import src.api.utils.badge_verification_service as bvs
    check("badge ganado → notifica", "evento='badge_ganado'" in inspect.getsource(bvs.BadgeVerificationService._asignar_badge))
    import src.api.admin_features_api as feat
    check("cambio de plan → notifica", "evento='plan_cambiado'" in inspect.getsource(feat.assign_plan_to_negocio))
    import src.api.utils.liga_recompensas_service as liga
    check("recompensa de liga → notifica", "evento='recompensa_liga'" in inspect.getsource(liga.otorgar_recompensas_liga))

    print(f"\n{'='*50}\n  RESULTADO: {PASS} pasaron, {FAIL} fallaron\n{'='*50}")
    return 0 if FAIL == 0 else 1


if __name__ == '__main__':
    sys.exit(main())
