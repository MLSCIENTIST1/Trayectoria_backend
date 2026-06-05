"""
Test de configuración global de la plataforma (Admin Panel — Sprint A38).

Ejecutar:
    PYTHONUTF8=1 venv/Scripts/python.exe src/tests_apis/test_admin_config_global_a38.py
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
        validar_config_global, get_config_global, CONFIG_GLOBAL_DEFAULT, ConfigGlobal
    )

    print("\n[1] DEFAULT")
    check("registro abierto por defecto", CONFIG_GLOBAL_DEFAULT['registro_abierto'] is True)
    check("mantenimiento apagado por defecto", CONFIG_GLOBAL_DEFAULT['modo_mantenimiento'] is False)
    check("get sin BD → default", get_config_global()['registro_abierto'] is True)
    check("modelo ConfigGlobal tabla config_global", ConfigGlobal.__tablename__ == 'config_global')

    print("\n[2] validar_config_global — válidos / parcial")
    ok, limpio, err = validar_config_global({'modo_mantenimiento': True, 'mensaje_mantenimiento': 'Volvemos pronto'})
    check("válido → ok", ok and err is None)
    check("parcial: solo trae lo enviado", set(limpio.keys()) == {'modo_mantenimiento', 'mensaje_mantenimiento'})
    check("bool casteado", limpio['modo_mantenimiento'] is True)
    check("registro_abierto bool", validar_config_global({'registro_abierto': 0})[1]['registro_abierto'] is False)
    check("vacío → ok sin cambios", validar_config_global({}) == (True, {}, None))

    print("\n[3] validar_config_global — inválidos / límites")
    check("no-dict → inválido", validar_config_global('x')[0] is False)
    check("texto no-string → inválido", validar_config_global({'texto_terminos': 123})[0] is False)
    largo = validar_config_global({'mensaje_mantenimiento': 'a' * 500})[1]['mensaje_mantenimiento']
    check("mensaje recortado a 300", len(largo) == 300)
    check("None en texto → cadena vacía", validar_config_global({'texto_privacidad': None})[1]['texto_privacidad'] == '')

    print("\n[4] Endpoints admin")
    import src.api.admin_api as api
    check("get_config_global_admin existe", hasattr(api, 'get_config_global_admin'))
    check("update_config_global_admin existe", hasattr(api, 'update_config_global_admin'))
    src_g = inspect.getsource(api.get_config_global_admin)
    check("GET requiere permiso configuracion", "requiere_permiso('configuracion')" in src_g)
    src_u = inspect.getsource(api.update_config_global_admin)
    check("PUT exige superadmin (mantenimiento es crítico)", 'superadmin_required' in src_u)
    check("PUT valida y audita", 'validar_config_global' in src_u and 'registrar_auditoria' in src_u)

    print("\n[5] Público + cableo de registro")
    import src.api.utils.register_user_api as reg
    check("config_publica existe", hasattr(reg, 'config_publica'))
    src_pub = inspect.getsource(reg.config_publica)
    check("público expone modo_mantenimiento y registro_abierto",
          'modo_mantenimiento' in src_pub and 'registro_abierto' in src_pub)
    src_reg = inspect.getsource(reg.register_user)
    check("register respeta registro_abierto", 'registro_abierto' in src_reg)
    check("register devuelve 403 si cerrado", '403' in src_reg)

    print(f"\n{'='*50}\n  RESULTADO: {PASS} pasaron, {FAIL} fallaron\n{'='*50}")
    return 0 if FAIL == 0 else 1


if __name__ == '__main__':
    sys.exit(main())
