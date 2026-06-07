"""
Test de la base de conocimiento de la plataforma (tabla "oculta" plataforma_kb).

Ejecutar:
    PYTHONUTF8=1 venv/Scripts/python.exe src/tests_apis/test_plataforma_kb.py
"""
import os
import sys
import json
import inspect
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

PASS = 0; FAIL = 0
def check(n, c):
    global PASS, FAIL
    if c: PASS += 1; print(f"  ✅ {n}")
    else: FAIL += 1; print(f"  ❌ {n}")


def main():
    from src.models.colombia_data.plataforma_kb import PlataformaKB, SEED_KB, seed_plataforma_kb

    print("\n[1] Modelo y tabla")
    cols = set(c.name for c in PlataformaKB.__table__.columns)
    for c in ['tipo', 'area', 'clave', 'titulo', 'resumen', 'contenido', 'datos', 'orden', 'publicado']:
        check(f"columna {c}", c in cols)
    check("tabla = plataforma_kb", PlataformaKB.__tablename__ == 'plataforma_kb')

    print("\n[2] Integridad del seed")
    claves = [e['clave'] for e in SEED_KB]
    check("claves únicas", len(claves) == len(set(claves)))
    check("todas con titulo", all(e.get('titulo') for e in SEED_KB))
    check("datos serializable (JSON)", all(_ok_json(e.get('datos', {})) for e in SEED_KB))
    tipos = {}
    for e in SEED_KB:
        tipos[e['tipo']] = tipos.get(e['tipo'], 0) + 1
    check("hay categorías de ayuda", tipos.get('categoria', 0) >= 8)
    check("hay catálogo de funciones", tipos.get('feature', 0) >= 15)
    check("hay novedades/changelog", tipos.get('changelog', 0) >= 1)

    print("\n[3] Datos VISUALES de marca presentes")
    marca = next((e for e in SEED_KB if e['clave'] == 'sistema-diseno'), None)
    check("entrada sistema-diseno existe", marca is not None)
    if marca:
        d = marca['datos']
        check("tipografía wordmark=Orbitron", d.get('tipografia', {}).get('wordmark') == 'Orbitron')
        check("tipografía títulos=Sora", d.get('tipografia', {}).get('titulos') == 'Sora')
        check("tipografía texto=Plus Jakarta Sans", d.get('tipografia', {}).get('texto') == 'Plus Jakarta Sans')
        check("color índigo #4F46E5", d.get('colores', {}).get('indigo') == '#4F46E5')
        check("logo tuko-logo.gif", 'tuko-logo.gif' in (d.get('logo') or ''))

    print("\n[4] Migración + seeder cableados en create_app")
    import src as _src
    src_create = inspect.getsource(_src.create_app)
    check("CREATE TABLE plataforma_kb en migraciones", 'CREATE TABLE IF NOT EXISTS plataforma_kb' in src_create)
    check("seed_plataforma_kb llamado", 'seed_plataforma_kb' in src_create)
    check("seeder idempotente (ON CONFLICT)", 'ON CONFLICT (clave) DO NOTHING' in inspect.getsource(seed_plataforma_kb))

    print(f"\n{'='*50}\n  RESULTADO: {PASS} pasaron, {FAIL} fallaron\n{'='*50}")
    return 0 if FAIL == 0 else 1


def _ok_json(x):
    try:
        json.dumps(x); return True
    except Exception:
        return False


if __name__ == '__main__':
    sys.exit(main())
