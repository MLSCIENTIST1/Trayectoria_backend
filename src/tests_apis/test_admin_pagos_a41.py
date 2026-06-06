"""
Test del Centro de pagos / Wompi (Admin Panel — Sprint A41).

Ejecutar:
    PYTHONUTF8=1 venv/Scripts/python.exe src/tests_apis/test_admin_pagos_a41.py
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
    from src.api.utils.pagos_service import evaluar_config_wompi, mascara_clave

    print("\n[1] evaluar_config_wompi — estados")
    ok = evaluar_config_wompi({'public_key': 'pk_prod_x', 'integrity_key': 'i', 'events_key': 'e',
                               'ambiente': 'prod', 'activo': True})
    check("todo presente → ok", ok['estado'] == 'ok')
    check("prod detectado", ok['prod'] is True)
    check("webhook_ok con events_key", ok['webhook_ok'] is True)
    check("sin faltantes", ok['faltantes'] == [])

    sin = evaluar_config_wompi({})
    check("vacío → sin_configurar", sin['estado'] == 'sin_configurar')
    check("vacío → webhook_ok False", sin['webhook_ok'] is False)
    check("vacío → ambiente test por defecto", sin['ambiente'] == 'test')

    inc = evaluar_config_wompi({'public_key': 'pk', 'integrity_key': 'i', 'events_key': '', 'activo': True})
    check("sin events_key → incompleto", inc['estado'] == 'incompleto')
    check("sin events_key → webhook roto", inc['webhook_ok'] is False)
    check("events_key en faltantes", 'events_key' in inc['faltantes'])

    print("\n[2] evaluar_config_wompi — bordes")
    check("None → sin_configurar", evaluar_config_wompi(None)['estado'] == 'sin_configurar')
    check("strings vacíos cuentan como ausentes",
          evaluar_config_wompi({'public_key': '   ', 'integrity_key': '', 'events_key': None})['estado'] == 'sin_configurar')

    print("\n[3] mascara_clave — no expone secretos")
    check("clave larga enmascarada", mascara_clave('pk_test_1234567890abcd') == 'pk_test…abcd')
    check("clave corta", mascara_clave('abc') == 'abc…')
    check("vacío → ''", mascara_clave('') == '')
    check("None → ''", mascara_clave(None) == '')

    print("\n[4] Endpoints")
    import src.api.admin_api as api
    check("admin_pagos_wompi existe", hasattr(api, 'admin_pagos_wompi'))
    check("admin_pagos_wompi_detalle existe", hasattr(api, 'admin_pagos_wompi_detalle'))
    src_o = inspect.getsource(api.admin_pagos_wompi)
    check("overview detecta webhook roto (activo sin events)", 'webhook_roto' in src_o)
    check("overview trae métricas de pago", "estado_pago='aprobado'" in src_o)
    check("overview requiere permiso pagos", "requiere_permiso('pagos')" in src_o)
    src_d = inspect.getsource(api.admin_pagos_wompi_detalle)
    check("detalle enmascara public_key", 'mascara_clave' in src_d and 'public_key_mask' in src_d)
    # La respuesta (config) se arma desde el evaluador puro (**ev) + presencia, nunca con los secretos crudos.
    check("config derivado del evaluador puro (**ev)", '**ev' in src_d)
    check("detalle solo expone presencia de secretos (no valores)",
          'tiene_integrity_key' in src_d and 'tiene_events_key' in src_d)
    check("evaluador puro no retorna claves crudas",
          all(k not in __import__('src.api.utils.pagos_service', fromlist=['evaluar_config_wompi']).evaluar_config_wompi(
              {'public_key': 'pk', 'integrity_key': 'SECRETO', 'events_key': 'SECRETO2', 'activo': True})
              for k in ('integrity_key', 'events_key', 'public_key')))
    check("detalle 404 si no hay config", '404' in src_d)

    print(f"\n{'='*50}\n  RESULTADO: {PASS} pasaron, {FAIL} fallaron\n{'='*50}")
    return 0 if FAIL == 0 else 1


if __name__ == '__main__':
    sys.exit(main())
