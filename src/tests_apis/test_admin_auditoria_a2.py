"""
Test del log de auditoría del panel admin (Admin Panel — Sprint A2).

Ejecutar:
    PYTHONUTF8=1 venv/Scripts/python.exe src/tests_apis/test_admin_auditoria_a2.py
"""
import os
import sys
from datetime import datetime
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

PASS = 0; FAIL = 0
def check(n, c):
    global PASS, FAIL
    if c: PASS += 1; print(f"  ✅ {n}")
    else: FAIL += 1; print(f"  ❌ {n}")


def main():
    from src.models.admin_audit import (
        AdminAuditLog, normalizar_accion, ACCIONES_VALIDAS
    )

    print("\n[1] normalizar_accion (función pura, whitelist)")
    check("'crear' → crear", normalizar_accion('crear') == 'crear')
    check("'CREAR' → crear (minúsculas)", normalizar_accion('CREAR') == 'crear')
    check("'  Editar ' → editar (trim)", normalizar_accion('  Editar ') == 'editar')
    check("acción desconocida → otro", normalizar_accion('hackear') == 'otro')
    check("None → otro", normalizar_accion(None) == 'otro')
    check("'' → otro", normalizar_accion('') == 'otro')
    check("whitelist incluye acciones clave",
          {'crear', 'editar', 'eliminar', 'otorgar', 'revocar'} <= ACCIONES_VALIDAS)

    print("\n[2] to_dict del modelo (sin DB)")
    e = AdminAuditLog()
    e.id = 1; e.admin_id = 5; e.admin_email = 'a@b.com'
    e.accion = 'eliminar'; e.entidad = 'usuario'; e.entidad_id = '42'
    e.detalle = {'correo': 'x@y.com'}; e.ip = '1.2.3.4'; e.user_agent = 'UA'
    e.created_at = datetime(2026, 6, 3, 10, 0, 0)
    d = e.to_dict()
    check("to_dict tiene todos los campos",
          all(k in d for k in ('id', 'admin_id', 'admin_email', 'accion', 'entidad',
                               'entidad_id', 'detalle', 'ip', 'user_agent', 'created_at')))
    check("accion correcta", d['accion'] == 'eliminar')
    check("entidad_id correcto", d['entidad_id'] == '42')
    check("detalle es dict", d['detalle'] == {'correo': 'x@y.com'})
    check("created_at en ISO", d['created_at'] == '2026-06-03T10:00:00')

    print("\n[3] detalle None → dict vacío en to_dict")
    e2 = AdminAuditLog(); e2.detalle = None
    check("detalle None → {}", e2.to_dict()['detalle'] == {})

    print("\n[4] Endpoints/helpers registrados en admin_api")
    import src.api.admin_api as api
    check("registrar_auditoria existe", hasattr(api, 'registrar_auditoria'))
    check("list_auditoria existe", hasattr(api, 'list_auditoria'))

    print(f"\n{'='*50}\n  RESULTADO: {PASS} pasaron, {FAIL} fallaron\n{'='*50}")
    return 0 if FAIL == 0 else 1


if __name__ == '__main__':
    sys.exit(main())
