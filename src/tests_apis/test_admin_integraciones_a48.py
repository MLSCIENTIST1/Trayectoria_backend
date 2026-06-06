"""
Test de Integraciones y automatizaciones (Admin Panel — Sprint A48).

Ejecutar:
    PYTHONUTF8=1 venv/Scripts/python.exe src/tests_apis/test_admin_integraciones_a48.py
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
    from src.api.utils.integraciones_service import (
        estado_integraciones, validar_integraciones_config, TRIGGERS_POSTVENTA, INTEGRACIONES_CONFIG_DEFAULT
    )

    print("\n[1] estado_integraciones — función pura")
    est = estado_integraciones({'RESEND_API_KEY': 'x', 'GROQ_API_KEY': ''}, wompi_activos=2)
    by = {i['clave']: i for i in est}
    check("resend configurado", by['resend']['configurado'] is True)
    check("groq NO configurado (vacío)", by['groq']['configurado'] is False)
    check("cloudinary siempre configurado (embebido)", by['cloudinary']['configurado'] is True)
    check("wompi configurado si hay activos", by['wompi']['configurado'] is True)
    check("wompi 0 → no configurado", {i['clave']: i for i in estado_integraciones({}, 0)}['wompi']['configurado'] is False)
    check("cada item tiene label y nota", all(i.get('label') and 'nota' in i for i in est))

    print("\n[2] validar_integraciones_config")
    ok, limpio, err = validar_integraciones_config({'whatsapp_postventa_activo': True, 'whatsapp_postventa_trigger': 'entregado'})
    check("válido → ok", ok and err is None)
    check("activo casteado a bool", limpio['whatsapp_postventa_activo'] is True)
    check("trigger inválido → error", validar_integraciones_config({'whatsapp_postventa_trigger': 'xxx'})[0] is False)
    check("plantilla no-string → error", validar_integraciones_config({'whatsapp_postventa_plantilla': 123})[0] is False)
    check("plantilla recortada a 1000", len(validar_integraciones_config({'whatsapp_postventa_plantilla': 'a'*2000})[1]['whatsapp_postventa_plantilla']) == 1000)
    check("no-dict → inválido", validar_integraciones_config('x')[0] is False)
    check("triggers válidos", TRIGGERS_POSTVENTA == {'confirmado', 'enviado', 'entregado'})
    check("default trae plantilla", bool(INTEGRACIONES_CONFIG_DEFAULT['whatsapp_postventa_plantilla']))

    print("\n[3] Endpoints + config")
    import src.api.admin_api as api
    check("admin_integraciones existe", hasattr(api, 'admin_integraciones'))
    check("update_integraciones_config existe", hasattr(api, 'update_integraciones_config'))
    src_g = inspect.getsource(api.admin_integraciones)
    check("estado usa estado_integraciones", 'estado_integraciones' in src_g)
    check("cuenta wompi activos", 'wompi_configs' in src_g)
    src_u = inspect.getsource(api.update_integraciones_config)
    check("config valida + audita", 'validar_integraciones_config' in src_u and 'registrar_auditoria' in src_u)
    from src.models.colombia_data.config_plataforma import get_integraciones_config
    check("get_integraciones_config existe y trae defaults", 'whatsapp_postventa_trigger' in get_integraciones_config())

    print(f"\n{'='*50}\n  RESULTADO: {PASS} pasaron, {FAIL} fallaron\n{'='*50}")
    return 0 if FAIL == 0 else 1


if __name__ == '__main__':
    sys.exit(main())
