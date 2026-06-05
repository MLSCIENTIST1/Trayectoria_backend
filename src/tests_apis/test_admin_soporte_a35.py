"""
Test de modo soporte / diagnóstico (Admin Panel — Sprint A35).

Ejecutar:
    PYTHONUTF8=1 venv/Scripts/python.exe src/tests_apis/test_admin_soporte_a35.py
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
    from src.api.utils.soporte_service import diagnosticar_negocio

    print("\n[1] diagnosticar_negocio — negocio sano")
    sano = {
        'negocio': {'activo': True, 'logo_url': 'http://x/logo.png', 'tiene_pagina': True,
                    'perfil_publico': True, 'plan_key': 'delux', 'eliminado': False},
        'suscripcion': {'estado': 'activa', 'es_trial': False},
        'productos': 5, 'pedidos': 3, 'videos': 1,
    }
    diag = diagnosticar_negocio(sano)
    check("sano → un único hallazgo 'ok'", len(diag) == 1 and diag[0]['nivel'] == 'ok')

    print("\n[2] diagnosticar_negocio — negocio con problemas")
    malo = {
        'negocio': {'activo': False, 'logo_url': None, 'tiene_pagina': False,
                    'perfil_publico': False, 'plan_key': 'basic', 'eliminado': True},
        'suscripcion': {'estado': 'vencida', 'es_trial': False},
        'productos': 0, 'pedidos': 0, 'videos': 0,
    }
    diag2 = diagnosticar_negocio(malo)
    msgs = ' '.join(c['mensaje'].lower() for c in diag2)
    niveles = {c['nivel'] for c in diag2}
    check("detecta inactivo", 'inactivo' in msgs or 'lista negra' in msgs)
    check("detecta papelera", 'papelera' in msgs)
    check("detecta sin logo", 'logo' in msgs)
    check("detecta sin productos", 'productos' in msgs)
    check("detecta suscripción vencida", 'vencida' in msgs)
    check("hay alertas", 'alerta' in niveles)
    check("NO incluye 'ok' cuando hay problemas", 'ok' not in niveles)

    print("\n[3] Bordes")
    check("dict vacío no rompe", isinstance(diagnosticar_negocio({}), list))
    check("None no rompe", isinstance(diagnosticar_negocio(None), list))
    sin_sus = diagnosticar_negocio({'negocio': {'activo': True, 'logo_url': 'x', 'tiene_pagina': True,
                                                 'perfil_publico': True, 'plan_key': 'basic'},
                                     'suscripcion': None, 'productos': 2, 'pedidos': 1})
    check("sin suscripción → lo informa", any('suscripción' in c['mensaje'].lower() for c in sin_sus))
    trial = diagnosticar_negocio({'negocio': {'activo': True, 'logo_url': 'x', 'tiene_pagina': True,
                                              'perfil_publico': True}, 'suscripcion': {'estado': 'activa', 'es_trial': True},
                                  'productos': 1, 'pedidos': 1})
    check("trial → lo informa", any('prueba' in c['mensaje'].lower() or 'trial' in c['mensaje'].lower() for c in trial))

    print("\n[4] Endpoint + seguridad + auditoría")
    import src.api.admin_api as api
    check("soporte_negocio existe", hasattr(api, 'soporte_negocio'))
    src_s = inspect.getsource(api.soporte_negocio)
    check("requiere permiso negocios", "requiere_permiso('negocios')" in src_s)
    check("NO suplanta sesión (no login_user)", 'login_user' not in src_s)
    check("es solo lectura (sin UPDATE/DELETE/INSERT)", not any(k in src_s for k in ('UPDATE ', 'DELETE FROM', 'INSERT INTO')))
    check("usa diagnosticar_negocio", 'diagnosticar_negocio' in src_s)
    check("audita el acceso", "registrar_auditoria('soporte'" in src_s)
    check("404 si no existe", '404' in src_s)
    from src.models.admin_audit import ACCIONES_VALIDAS
    check("'soporte' en ACCIONES_VALIDAS", 'soporte' in ACCIONES_VALIDAS)

    print(f"\n{'='*50}\n  RESULTADO: {PASS} pasaron, {FAIL} fallaron\n{'='*50}")
    return 0 if FAIL == 0 else 1


if __name__ == '__main__':
    sys.exit(main())
