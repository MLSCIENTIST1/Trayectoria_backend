"""
Test de Habeas Data / privacidad (Admin Panel — Sprint A45).

Ejecutar:
    PYTHONUTF8=1 venv/Scripts/python.exe src/tests_apis/test_admin_privacidad_a45.py
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
    from src.api.utils.privacidad_service import (
        validar_tipo_solicitud, construir_export_usuario, CAMPOS_SENSIBLES, TIPOS_SOLICITUD
    )

    print("\n[1] validar_tipo_solicitud")
    check("export válido", validar_tipo_solicitud('export') is True)
    check("eliminacion válido", validar_tipo_solicitud('eliminacion') is True)
    check("mayúsculas/espacios", validar_tipo_solicitud('  EXPORT ') is True)
    check("inválido → False", validar_tipo_solicitud('otra') is False)
    check("None → False", validar_tipo_solicitud(None) is False)
    check("tipos = export/eliminacion", TIPOS_SOLICITUD == {'export', 'eliminacion'})

    print("\n[2] construir_export_usuario — NO expone secretos")
    usuario = {'id_usuario': 5, 'nombre': 'Ana', 'correo': 'ana@x.com',
               'contrasenia': 'HASH_SECRETO', 'confirmacion_contrasenia': 'HASH', 'token_acceso': 'tok',
               'acepto_terminos': True, 'fecha_aceptacion_terminos': '2026-01-01'}
    exp = construir_export_usuario(usuario, negocios=[{'nombre_negocio': 'Tienda', 'password_hash': 'x'}],
                                   resenas=[{'rating': 5, 'token': 't'}], generado_en='2026-06-05')
    check("incluye datos del usuario", exp['usuario']['nombre'] == 'Ana')
    check("NO incluye contrasenia", 'contrasenia' not in exp['usuario'])
    check("NO incluye confirmacion", 'confirmacion_contrasenia' not in exp['usuario'])
    check("NO incluye token", 'token_acceso' not in exp['usuario'])
    check("limpia secretos en negocios", 'password_hash' not in exp['negocios'][0])
    check("limpia secretos en reseñas", 'token' not in exp['resenas'][0])
    check("registra consentimiento", exp['consentimiento']['acepto_terminos'] is True)
    check("menciona Ley 1581", '1581' in exp['ley'])
    check("CAMPOS_SENSIBLES cubre contrasenia/token", 'contrasenia' in CAMPOS_SENSIBLES and 'token' in CAMPOS_SENSIBLES)

    print("\n[3] Endpoints")
    import src.api.admin_api as api
    for fn in ['privacidad_export', 'privacidad_solicitudes', 'privacidad_crear_solicitud', 'privacidad_procesar_solicitud']:
        check(f"{fn} existe", hasattr(api, fn))
    src_exp = inspect.getsource(api.privacidad_export)
    check("export usa construir_export_usuario", 'construir_export_usuario' in src_exp)
    check("export audita", "registrar_auditoria('export'" in src_exp)
    check("export NO selecciona contrasenia", 'contrasenia' not in src_exp)
    src_proc = inspect.getsource(api.privacidad_procesar_solicitud)
    check("procesar exige superadmin", 'superadmin_required' in src_proc)
    check("eliminación = baja lógica (papelera, no purga)", 'eliminado=TRUE' in src_proc and 'DELETE FROM usuarios' not in src_proc)
    check("bloquea eliminar admins activos", 'administrador' in src_proc.lower() or 'administradores' in src_proc)
    check("procesar audita", 'registrar_auditoria' in src_proc)

    print("\n[4] Migración")
    import src as _src
    check("solicitudes_privacidad en create_app", 'CREATE TABLE IF NOT EXISTS solicitudes_privacidad' in inspect.getsource(_src.create_app))

    print(f"\n{'='*50}\n  RESULTADO: {PASS} pasaron, {FAIL} fallaron\n{'='*50}")
    return 0 if FAIL == 0 else 1


if __name__ == '__main__':
    sys.exit(main())
