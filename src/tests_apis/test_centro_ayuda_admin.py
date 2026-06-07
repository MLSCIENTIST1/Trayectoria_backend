"""
Test del CRUD admin del Centro de Ayuda (M3.3).
Valida el validador puro + que los endpoints existan, estén protegidos y auditados.

Ejecutar:
    PYTHONUTF8=1 venv/Scripts/python.exe src/tests_apis/test_centro_ayuda_admin.py
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
    from src.api.ayuda import centro_ayuda_admin_api as adm

    print("\n[1] validar_entrada_kb — PURO")
    v = adm.validar_entrada_kb
    check("válida sin errores", v({'tipo': 'articulo', 'clave': 'x', 'titulo': 'T'}) == [])
    check("tipo inválido detectado", any('tipo' in e for e in v({'tipo': 'zzz', 'clave': 'x', 'titulo': 'T'})))
    check("clave faltante detectada", any('clave' in e for e in v({'tipo': 'articulo', 'clave': '  ', 'titulo': 'T'})))
    check("titulo faltante detectado", any('titulo' in e for e in v({'tipo': 'articulo', 'clave': 'x', 'titulo': ''})))
    check("parcial: solo valida lo presente", v({'titulo': 'Nuevo'}, parcial=True) == [])
    check("parcial: tipo malo sí falla", v({'tipo': 'zzz'}, parcial=True) != [])

    print("\n[2] Endpoints CRUD presentes")
    for fn in ['listar', 'obtener', 'crear', 'editar', 'eliminar', 'publicar']:
        check(f"{fn} existe", hasattr(adm, fn))

    print("\n[3] Protegidos por permiso + auditados")
    for fn in ['crear', 'editar', 'eliminar', 'publicar']:
        src = inspect.getsource(getattr(adm, fn))
        check(f"{fn} audita (registrar_auditoria)", 'registrar_auditoria' in src)
    src_mod = inspect.getsource(adm)
    check("usa @requiere_permiso('centro_ayuda')", "requiere_permiso('centro_ayuda')" in src_mod)
    check("crear evita clave duplicada (409)", '409' in inspect.getsource(adm.crear))

    print("\n[4] Permiso 'centro_ayuda' registrado en el panel")
    import src.api.admin_api as a
    check("centro_ayuda en MODULOS_PERMISOS", any(m['key'] == 'centro_ayuda' for m in a.MODULOS_PERMISOS))
    check("centro_ayuda en PERMISOS_VALIDOS", 'centro_ayuda' in a.PERMISOS_VALIDOS)

    print(f"\n{'='*50}\n  RESULTADO: {PASS} pasaron, {FAIL} fallaron\n{'='*50}")
    return 0 if FAIL == 0 else 1


if __name__ == '__main__':
    sys.exit(main())
