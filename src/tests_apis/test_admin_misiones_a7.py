"""
Test del editor de misiones del panel admin (Admin Panel — Sprint A7).
Valida los helpers puros de merge/validación de overrides de misiones.

Ejecutar:
    PYTHONUTF8=1 venv/Scripts/python.exe src/tests_apis/test_admin_misiones_a7.py
"""
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

PASS = 0; FAIL = 0
def check(n, c):
    global PASS, FAIL
    if c: PASS += 1; print(f"  ✅ {n}")
    else: FAIL += 1; print(f"  ❌ {n}")


POOL = [
    {'codigo': 'm1', 'nombre': 'Misión 1', 'descripcion': 'd1', 'icono': '🛒', 'xp': 20, 'tukoins': 10, 'tipo': 'diaria'},
    {'codigo': 'm2', 'nombre': 'Misión 2', 'descripcion': 'd2', 'icono': '📦', 'xp': 15, 'tukoins': 5,  'tipo': 'diaria'},
    {'codigo': 'm3', 'nombre': 'Misión 3', 'descripcion': 'd3', 'icono': '⭐', 'xp': 30, 'tukoins': 8,  'tipo': 'diaria'},
]


def main():
    from src.models.colombia_data.ratings.config_gamificacion import (
        merge_misiones, validar_misiones_override
    )

    print("\n[1] merge_misiones — sin overrides")
    base = merge_misiones(POOL, None)
    check("None → pool completo", len(base) == 3)
    check("es copia (no mismos dicts)", base[0] is not POOL[0])

    print("\n[2] merge — editar campos")
    m = merge_misiones(POOL, {'m1': {'xp': 99, 'tukoins': 50, 'nombre': 'Nueva'}})
    m1 = next(x for x in m if x['codigo'] == 'm1')
    check("xp editado", m1['xp'] == 99)
    check("tukoins editado", m1['tukoins'] == 50)
    check("nombre editado", m1['nombre'] == 'Nueva')
    check("otras misiones intactas", next(x for x in m if x['codigo'] == 'm2')['xp'] == 15)

    print("\n[3] merge — desactivar excluye del pool")
    m = merge_misiones(POOL, {'m2': {'activa': False}})
    codigos = [x['codigo'] for x in m]
    check("m2 excluida", 'm2' not in codigos)
    check("quedan 2", len(m) == 2)
    check("activa True no excluye", len(merge_misiones(POOL, {'m2': {'activa': True}})) == 3)

    print("\n[4] merge — saneo de valores")
    m = merge_misiones(POOL, {'m1': {'xp': -10}})
    check("xp negativo → 0", next(x for x in m if x['codigo'] == 'm1')['xp'] == 0)
    m = merge_misiones(POOL, {'m1': {'xp': 'abc'}})
    check("xp no numérico → conserva default", next(x for x in m if x['codigo'] == 'm1')['xp'] == 20)
    check("override de código inexistente no rompe", len(merge_misiones(POOL, {'zzz': {'xp': 5}})) == 3)

    print("\n[5] validar_misiones_override")
    ok, limpio, err = validar_misiones_override({'m1': {'xp': 25, 'activa': False}})
    check("válido → ok", ok is True and err is None)
    check("limpio normaliza xp int", limpio['m1']['xp'] == 25)
    check("limpio conserva activa bool", limpio['m1']['activa'] is False)

    ok2, _, err2 = validar_misiones_override({'m1': {'xp': 'x'}})
    check("xp no numérico → inválido", ok2 is False)

    ok3, _, err3 = validar_misiones_override({'m1': {'xp': 999999}})
    check("xp fuera de rango → inválido", ok3 is False)

    ok4, limpio4, _ = validar_misiones_override({'m1': {'nombre': 'X' * 500}})
    check("nombre se recorta a 120", ok4 and len(limpio4['m1']['nombre']) <= 120)

    ok5, _, err5 = validar_misiones_override("no-dict")
    check("payload no-dict → inválido", ok5 is False)

    print("\n[6] Endpoints registrados")
    import src.api.admin_api as api
    check("get_gamif_misiones existe", hasattr(api, 'get_gamif_misiones'))
    check("update_gamif_misiones existe", hasattr(api, 'update_gamif_misiones'))

    print("\n[7] hooks y selección diaria usan el pool efectivo")
    import inspect
    import src.api.gamificacion.gamificacion_hooks as hooks
    import src.api.gamificacion.gamificacion_api as gapi
    check("hooks usa _get_pool('diaria')", "_get_pool('diaria')" in inspect.getsource(hooks))
    check("hooks usa _get_pool('semanal')", "_get_pool('semanal')" in inspect.getsource(hooks))
    check("seleccion diaria usa get_pool", "get_pool('diaria')" in inspect.getsource(gapi))

    print(f"\n{'='*50}\n  RESULTADO: {PASS} pasaron, {FAIL} fallaron\n{'='*50}")
    return 0 if FAIL == 0 else 1


if __name__ == '__main__':
    sys.exit(main())
