"""
Test de Administración de Dora IA (Admin Panel — Sprint A44).

Ejecutar:
    PYTHONUTF8=1 venv/Scripts/python.exe src/tests_apis/test_admin_ia_a44.py
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
    from src.models.colombia_data.config_plataforma import (
        validar_ia_config, get_ia_config, IA_CONFIG_DEFAULT, limite_ia_por_plan, puede_usar_ia
    )

    print("\n[1] DEFAULT")
    check("ia_activa por defecto", IA_CONFIG_DEFAULT['ia_activa'] is True)
    check("límites crecen por plan", IA_CONFIG_DEFAULT['limite_dia_basic'] < IA_CONFIG_DEFAULT['limite_dia_delux'])
    check("get_ia_config sin BD → default", get_ia_config()['modelo'] == IA_CONFIG_DEFAULT['modelo'])

    print("\n[2] validar_ia_config")
    ok, limpio, err = validar_ia_config({'ia_activa': False, 'max_tokens': 1024, 'limite_dia_pro': 200})
    check("válido → ok", ok and err is None)
    check("parcial: solo lo enviado", set(limpio.keys()) == {'ia_activa', 'max_tokens', 'limite_dia_pro'})
    check("max_tokens fuera de rango → inválido", validar_ia_config({'max_tokens': 99999})[0] is False)
    check("max_tokens muy bajo → inválido", validar_ia_config({'max_tokens': 10})[0] is False)
    check("límite negativo → inválido", validar_ia_config({'limite_dia_basic': -1})[0] is False)
    check("no-dict → inválido", validar_ia_config('x')[0] is False)

    print("\n[3] limite_ia_por_plan / puede_usar_ia")
    cfg = dict(IA_CONFIG_DEFAULT)
    check("plan basic", limite_ia_por_plan(cfg, 'basic') == cfg['limite_dia_basic'])
    check("plan delux", limite_ia_por_plan(cfg, 'delux') == cfg['limite_dia_delux'])
    check("alias deluxe", limite_ia_por_plan(cfg, 'deluxe') == cfg['limite_dia_delux'])
    check("plan desconocido → basic", limite_ia_por_plan(cfg, 'zzz') == cfg['limite_dia_basic'])
    perm, lim, rest = puede_usar_ia(0, 'basic', cfg)
    check("0 usos → permitido", perm is True and rest == cfg['limite_dia_basic'])
    perm2, _, rest2 = puede_usar_ia(cfg['limite_dia_basic'], 'basic', cfg)
    check("en el límite → NO permitido", perm2 is False and rest2 == 0)

    print("\n[4] Integración en call_groq (Dora)")
    import src.api.ia.dora_api as dora
    for fn in ['_ia_gate', '_ia_registrar_uso', '_ia_usos_hoy']:
        check(f"{fn} existe", hasattr(dora, fn))
    src_cg = inspect.getsource(dora.call_groq)
    check("call_groq aplica el gate", '_ia_gate()' in src_cg)
    check("call_groq usa modelo/max_tokens de config", "_cfg.get('modelo')" in src_cg and "_cfg.get('max_tokens')" in src_cg)
    check("call_groq registra uso solo tras éxito", '_ia_registrar_uso(_nid)' in src_cg)

    print("\n[5] Endpoints admin + migración")
    import src.api.admin_api as api
    check("admin_ia existe", hasattr(api, 'admin_ia'))
    check("update_ia_config existe", hasattr(api, 'update_ia_config'))
    src_g = inspect.getsource(api.admin_ia)
    check("consumo desde ia_uso", 'ia_uso' in src_g and 'usos_hoy' in src_g)
    src_u = inspect.getsource(api.update_ia_config)
    check("config solo superadmin (afecta costos)", 'superadmin_required' in src_u)
    check("config valida y audita", 'validar_ia_config' in src_u and 'registrar_auditoria' in src_u)
    import src as _src
    check("migración ia_uso en create_app", 'CREATE TABLE IF NOT EXISTS ia_uso' in inspect.getsource(_src.create_app))

    print(f"\n{'='*50}\n  RESULTADO: {PASS} pasaron, {FAIL} fallaron\n{'='*50}")
    return 0 if FAIL == 0 else 1


if __name__ == '__main__':
    sys.exit(main())
