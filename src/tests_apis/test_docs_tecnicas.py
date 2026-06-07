"""
Documentación Maestra — Fase 1: lógica de acceso + step-up + CRUD presente.

Ejecutar:
    PYTHONUTF8=1 venv/Scripts/python.exe src/tests_apis/test_docs_tecnicas.py
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
    from src.api.ayuda import docs_tecnicas_api as d

    print("\n[1] niveles_visibles — PURO (step-up)")
    check("sin desbloqueo → publico+admin (NO superadmin)", d.niveles_visibles(False) == ['publico', 'admin'])
    check("con desbloqueo → incluye superadmin", 'superadmin' in d.niveles_visibles(True))
    check("sin desbloqueo NO expone superadmin", 'superadmin' not in d.niveles_visibles(False))

    print("\n[2] validar_doc — PURO")
    v = d.validar_doc
    check("válida", v({'clave': 'x', 'titulo': 'T', 'area': 'backend'}) == [])
    check("clave requerida", any('clave' in e for e in v({'titulo': 'T', 'area': 'backend'})))
    check("area requerida", any('area' in e for e in v({'clave': 'x', 'titulo': 'T'})))
    check("nivel inválido detectado", v({'clave': 'x', 'titulo': 'T', 'area': 'a', 'nivel_acceso': 'zzz'}) != [])
    check("nivel válido superadmin ok", v({'clave': 'x', 'titulo': 'T', 'area': 'a', 'nivel_acceso': 'superadmin'}) == [])
    check("parcial valida solo lo presente", v({'titulo': 'Nuevo'}, parcial=True) == [])

    print("\n[3] Taxonomía de secciones")
    areas = [s['area'] for s in d.SECCIONES_DOC]
    for must in ['arquitectura', 'backend', 'base-datos', 'frontend', 'seguridad', 'despliegue']:
        check(f"sección '{must}' presente", must in areas)
    check("taxonomía ampliada (>=14 secciones)", len(d.SECCIONES_DOC) >= 14)
    check("incluye glosario y secciones extra", {'glosario', 'errores', 'terceros', 'handover'} <= set(areas))

    print("\n[4] Endpoints y seguridad")
    for fn in ['unlock', 'lock', 'estado', 'arbol', 'entrada', 'buscar', 'crear', 'editar', 'eliminar']:
        check(f"{fn} existe", hasattr(d, fn))
    src = inspect.getsource(d)
    check("unlock verifica SuperAdmin (rol superadmin)", "rol') != 'superadmin'" in src or "'superadmin'" in inspect.getsource(d.unlock))
    check("unlock usa check_password (bcrypt)", 'check_password' in inspect.getsource(d.unlock))
    check("CRUD audita", all('registrar_auditoria' in inspect.getsource(getattr(d, f)) for f in ['crear', 'editar', 'eliminar']))
    check("entrada respeta nivel (requiere_unlock 403)", 'requiere_unlock' in inspect.getsource(d.entrada))

    print("\n[5] Permiso 'documentacion' registrado")
    import src.api.admin_api as a
    check("documentacion en MODULOS_PERMISOS", any(m['key'] == 'documentacion' for m in a.MODULOS_PERMISOS))

    print(f"\n{'='*52}\n  RESULTADO: {PASS} pasaron, {FAIL} fallaron\n{'='*52}")
    return 0 if FAIL == 0 else 1


if __name__ == '__main__':
    sys.exit(main())
