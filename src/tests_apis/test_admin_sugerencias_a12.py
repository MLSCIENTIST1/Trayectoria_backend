"""
Test de parámetros de sugerencias/comparativas (Admin Panel — Sprint A12).

Ejecutar:
    PYTHONUTF8=1 venv/Scripts/python.exe src/tests_apis/test_admin_sugerencias_a12.py
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
        validar_sugerencias_config, SUGERENCIAS_DEFAULT
    )
    from src.api.gamificacion.gamificacion_api import generar_sugerencias

    print("\n[1] DEFAULT")
    check("umbral_casi 70", SUGERENCIAS_DEFAULT['umbral_casi'] == 70)
    check("destacado_top_pct 10", SUGERENCIAS_DEFAULT['destacado_top_pct'] == 10)

    print("\n[2] validar_sugerencias_config")
    ok, limpio, err = validar_sugerencias_config({'umbral_casi': 80, 'umbral_avance': 50, 'max_sugerencias': 5})
    check("válido → ok", ok and err is None)
    check("limpio toma valores", limpio['umbral_casi'] == 80 and limpio['max_sugerencias'] == 5)
    check("rellena faltantes con default", limpio['racha_minima'] == SUGERENCIAS_DEFAULT['racha_minima'])
    check("avance > casi → inválido", validar_sugerencias_config({'umbral_casi': 40, 'umbral_avance': 70})[0] is False)
    check("max_sugerencias 0 → inválido", validar_sugerencias_config({'max_sugerencias': 0})[0] is False)
    check("no numérico → inválido", validar_sugerencias_config({'umbral_casi': 'x'})[0] is False)
    check("no-dict → inválido", validar_sugerencias_config('x')[0] is False)

    print("\n[3] generar_sugerencias respeta cfg (umbrales)")
    prox = [{'criterio_tipo': 'pedidos_completados', 'nombre': 'Vendedor', 'falta': 1,
             'progreso_pct': 50, 'icono': 'bi-trophy'}]
    # con default (casi=70): 50% → prioridad media
    s_def = generar_sugerencias(prox, 0)
    check("50% con casi=70 → media", s_def[0]['prioridad'] == 'media')
    # con cfg casi=40: 50% → alta
    cfg = dict(SUGERENCIAS_DEFAULT); cfg['umbral_casi'] = 40
    s_cfg = generar_sugerencias(prox, 0, cfg=cfg)
    check("50% con casi=40 → alta", s_cfg[0]['prioridad'] == 'alta')

    print("\n[4] cfg controla max_sugerencias y badges_considerar")
    prox3 = [dict(prox[0], nombre=f'B{i}') for i in range(3)]
    cfg2 = dict(SUGERENCIAS_DEFAULT); cfg2['max_sugerencias'] = 1; cfg2['badges_considerar'] = 3
    check("max_sugerencias=1 → 1", len(generar_sugerencias(prox3, 0, cfg=cfg2)) == 1)
    cfg3 = dict(SUGERENCIAS_DEFAULT); cfg3['badges_considerar'] = 1; cfg3['max_sugerencias'] = 9
    check("badges_considerar=1 → 1 sugerencia de badge", len(generar_sugerencias(prox3, 0, cfg=cfg3)) == 1)

    print("\n[5] racha_minima configurable")
    cfg4 = dict(SUGERENCIAS_DEFAULT); cfg4['racha_minima'] = 5
    s5 = generar_sugerencias([], 3, cfg=cfg4)  # racha 3 < 5 → no nudge
    check("racha 3 con min 5 → sin aviso de racha", not any('racha' in x['texto'].lower() for x in s5))
    s6 = generar_sugerencias([], 6, cfg=cfg4)  # racha 6 >= 5 → nudge
    check("racha 6 con min 5 → aviso de racha", any('racha' in x['texto'].lower() for x in s6))

    print("\n[6] Compatibilidad S35 (limite sigue funcionando)")
    check("limite=2 cap", len(generar_sugerencias(prox3, 9, limite=2)) <= 2)
    check("None → lista", isinstance(generar_sugerencias(None, 0), list))

    print("\n[7] Endpoints registrados")
    import src.api.admin_api as api
    check("get_gamif_sugerencias existe", hasattr(api, 'get_gamif_sugerencias'))
    check("update_gamif_sugerencias existe", hasattr(api, 'update_gamif_sugerencias'))

    print(f"\n{'='*50}\n  RESULTADO: {PASS} pasaron, {FAIL} fallaron\n{'='*50}")
    return 0 if FAIL == 0 else 1


if __name__ == '__main__':
    sys.exit(main())
