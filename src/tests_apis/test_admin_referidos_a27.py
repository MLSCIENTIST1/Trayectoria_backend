"""
Test de gestión de referidos (Admin Panel — Sprint A27).

Ejecutar:
    PYTHONUTF8=1 venv/Scripts/python.exe src/tests_apis/test_admin_referidos_a27.py
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
        validar_referidos_config, marcar_referidores_sospechosos,
        get_referidos_config, REFERIDOS_CONFIG_DEFAULT
    )

    print("\n[1] DEFAULT (compatibilidad con S29)")
    check("xp_referidor default 50", REFERIDOS_CONFIG_DEFAULT['xp_referidor'] == 50)
    check("tukoins_referidor default 30", REFERIDOS_CONFIG_DEFAULT['tukoins_referidor'] == 30)
    check("get_referidos_config sin BD → default", get_referidos_config() == REFERIDOS_CONFIG_DEFAULT)

    print("\n[2] validar_referidos_config — válidos")
    ok, limpio, err = validar_referidos_config({'xp_referidor': 80, 'tukoins_referidor': 40, 'umbral_fraude': 20, 'ratio_min': 0.3})
    check("válido → ok", ok and err is None)
    check("limpio correcto", limpio == {'xp_referidor': 80, 'tukoins_referidor': 40, 'tukoins_pago_referidor': 1000, 'umbral_fraude': 20, 'ratio_min': 0.3})
    ok2, limpio2, _ = validar_referidos_config({})
    check("vacío → defaults", ok2 and limpio2 == REFERIDOS_CONFIG_DEFAULT)

    print("\n[3] validar_referidos_config — inválidos")
    check("xp negativo → inválido", validar_referidos_config({'xp_referidor': -1})[0] is False)
    check("xp gigante → inválido", validar_referidos_config({'xp_referidor': 999999})[0] is False)
    check("umbral 1 → inválido", validar_referidos_config({'umbral_fraude': 1})[0] is False)
    check("ratio 1.5 → inválido", validar_referidos_config({'ratio_min': 1.5})[0] is False)
    check("no numérico → inválido", validar_referidos_config({'xp_referidor': 'x'})[0] is False)
    check("no-dict → inválido", validar_referidos_config('x')[0] is False)

    print("\n[4] marcar_referidores_sospechosos — función pura")
    filas = [
        {'usuario_id': 1, 'total': 50, 'convertidos': 1},   # spam: muchos, casi 0 conversión
        {'usuario_id': 2, 'total': 50, 'convertidos': 45},  # legítimo: alta conversión
        {'usuario_id': 3, 'total': 3,  'convertidos': 0},   # pocos: bajo umbral, no se marca
    ]
    susp = marcar_referidores_sospechosos(filas, umbral=10, ratio_min=0.2)
    check("marca al spammer (id 1)", 1 in susp)
    check("NO marca al legítimo (id 2)", 2 not in susp)
    check("NO marca a quien tiene pocos referidos (id 3)", 3 not in susp)
    check("ratio del spammer es bajo", susp[1] < 0.2)

    print("\n[5] marcar_referidores_sospechosos — bordes")
    check("lista vacía → {}", marcar_referidores_sospechosos([], 10, 0.2) == {})
    check("None → {}", marcar_referidores_sospechosos(None, 10, 0.2) == {})
    check("fila corrupta no rompe", marcar_referidores_sospechosos([{'usuario_id': 9}], 10, 0.2) == {})
    check("justo en el umbral con 0 conversiones → marcado",
          10 in marcar_referidores_sospechosos([{'usuario_id': 10, 'total': 10, 'convertidos': 0}], 10, 0.2))

    print("\n[6] La conversión usa la config (revisión de código)")
    import inspect, src.api.gamificacion.gamificacion_api as g
    src_conv = inspect.getsource(g.procesar_conversion_referido)
    check("procesar_conversion lee get_referidos_config", 'get_referidos_config' in src_conv)
    check("fallback a constantes S29", 'REFERIDO_XP_REFERIDOR' in src_conv and 'REFERIDO_TUKOINS' in src_conv)

    print("\n[7] Endpoints + auditoría")
    import src.api.admin_api as api
    check("admin_referidos existe", hasattr(api, 'admin_referidos'))
    check("update_referidos_config existe", hasattr(api, 'update_referidos_config'))
    src_list = inspect.getsource(api.admin_referidos)
    check("listado calcula tasa de conversión", 'tasa_conversion' in src_list)
    check("listado marca sospechosos", 'marcar_referidores_sospechosos' in src_list)
    src_cfg = inspect.getsource(api.update_referidos_config)
    check("config audita", 'registrar_auditoria' in src_cfg)
    check("config valida", 'validar_referidos_config' in src_cfg)

    print(f"\n{'='*50}\n  RESULTADO: {PASS} pasaron, {FAIL} fallaron\n{'='*50}")
    return 0 if FAIL == 0 else 1


if __name__ == '__main__':
    sys.exit(main())
