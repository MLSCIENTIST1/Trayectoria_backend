"""
Test de permisos granulares del panel admin (Admin Panel — Sprint A3).

Ejecutar:
    PYTHONUTF8=1 venv/Scripts/python.exe src/tests_apis/test_admin_permisos_a3.py
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
    from src.api.admin_api import (
        admin_tiene_permiso, MODULOS_PERMISOS, PERMISOS_VALIDOS
    )

    print("\n[1] admin_tiene_permiso (función pura)")
    superadmin = {'rol': 'superadmin', 'permisos': []}
    check("superadmin pasa cualquier permiso", admin_tiene_permiso(superadmin, 'pagos') is True)
    check("superadmin pasa permiso inventado", admin_tiene_permiso(superadmin, 'lo_que_sea') is True)

    admin = {'rol': 'admin', 'permisos': ['usuarios', 'negocios']}
    check("admin con permiso → True", admin_tiene_permiso(admin, 'usuarios') is True)
    check("admin sin permiso → False", admin_tiene_permiso(admin, 'pagos') is False)

    check("admin permisos None → False", admin_tiene_permiso({'rol': 'admin', 'permisos': None}, 'usuarios') is False)
    check("admin_data None → False", admin_tiene_permiso(None, 'usuarios') is False)
    check("admin permisos vacíos → False", admin_tiene_permiso({'rol': 'admin', 'permisos': []}, 'usuarios') is False)

    print("\n[2] Catálogo de módulos")
    keys = [m['key'] for m in MODULOS_PERMISOS]
    check("todos los módulos tienen key/label/grupo",
          all(m.get('key') and m.get('label') and m.get('grupo') for m in MODULOS_PERMISOS))
    check("no hay claves duplicadas", len(keys) == len(set(keys)))
    check("incluye módulos de los 40 sprints",
          {'gamificacion', 'insignias', 'eventos', 'economia', 'pagos'} <= set(keys))
    check("incluye módulos existentes", {'usuarios', 'negocios', 'challenges'} <= set(keys))
    check("PERMISOS_VALIDOS coincide con las keys", PERMISOS_VALIDOS == set(keys))

    print("\n[3] Saneo de permisos (réplica de la lógica del endpoint)")
    def sanear(permisos_in):
        s = set(permisos_in)
        return [m['key'] for m in MODULOS_PERMISOS if m['key'] in s]
    limpio = sanear(['usuarios', 'hackear', 'pagos', 'usuarios'])
    check("filtra claves inválidas", 'hackear' not in limpio)
    check("elimina duplicados", limpio.count('usuarios') == 1)
    check("conserva válidas", set(limpio) == {'usuarios', 'pagos'})
    check("lista vacía → vacío", sanear([]) == [])

    print("\n[4] Endpoints registrados")
    import src.api.admin_api as api
    check("list_modulos_permisos existe", hasattr(api, 'list_modulos_permisos'))
    check("update_admin_permisos existe", hasattr(api, 'update_admin_permisos'))
    check("requiere_permiso existe", hasattr(api, 'requiere_permiso'))

    print(f"\n{'='*50}\n  RESULTADO: {PASS} pasaron, {FAIL} fallaron\n{'='*50}")
    return 0 if FAIL == 0 else 1


if __name__ == '__main__':
    sys.exit(main())
