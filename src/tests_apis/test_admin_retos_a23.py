"""
Test del editor de retos mensuales configurables (Admin Panel — Sprint A23).

Ejecutar:
    PYTHONUTF8=1 venv/Scripts/python.exe src/tests_apis/test_admin_retos_a23.py
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
    from src.models.colombia_data.ratings.config_gamificacion import (
        validar_retos, validar_programacion_retos, seleccionar_reto,
        _retos_default, METRICAS_RETO
    )
    from src.api.gamificacion.gamificacion_api import RETOS_MENSUALES, _reto_del_mes

    print("\n[1] DEFAULT y métricas")
    d = _retos_default()
    check("default == RETOS_MENSUALES", d is RETOS_MENSUALES)
    check("hay retos por defecto", isinstance(d, list) and len(d) >= 1)
    check("métricas del default soportadas", all(r['metrica'] in METRICAS_RETO for r in d))
    check("3 métricas válidas conocidas",
          set(METRICAS_RETO) == {'ventas_mes', 'productos_mes', 'productos_activos'})

    print("\n[2] validar_retos — válidos")
    ok, limpio, err = validar_retos([
        {'codigo': 'Rey Ventas', 'nombre': 'Rey', 'icono': '👑', 'metrica': 'ventas_mes', 'descripcion': 'x'}
    ])
    check("válido → ok", ok and err is None)
    check("código normalizado", limpio[0]['codigo'] == 'rey_ventas')
    check("unidad por defecto", limpio[0]['unidad'] == 'puntos')

    print("\n[3] validar_retos — inválidos")
    check("no-lista → inválido", validar_retos({})[0] is False)
    check("lista vacía → inválido", validar_retos([])[0] is False)
    check("sin nombre → inválido", validar_retos([{'codigo': 'a', 'metrica': 'ventas_mes'}])[0] is False)
    check("métrica desconocida → inválido",
          validar_retos([{'codigo': 'a', 'nombre': 'A', 'metrica': 'inventada'}])[0] is False)
    check("código duplicado → inválido", validar_retos([
        {'codigo': 'a', 'nombre': 'A', 'metrica': 'ventas_mes'},
        {'codigo': 'a', 'nombre': 'B', 'metrica': 'ventas_mes'},
    ])[0] is False)

    print("\n[4] validar_programacion_retos")
    cods = {'rey_ventas', 'productivo'}
    check("vacío/None → válido", validar_programacion_retos(None, cods) == (True, {}, None))
    okp, limp, _ = validar_programacion_retos({'2026-07': 'rey_ventas'}, cods)
    check("mes válido + código válido → ok", okp and limp == {'2026-07': 'rey_ventas'})
    check("mes mal formado → inválido", validar_programacion_retos({'2026-7': 'rey_ventas'}, cods)[0] is False)
    check("mes 13 → inválido", validar_programacion_retos({'2026-13': 'rey_ventas'}, cods)[0] is False)
    check("código fuera del pool → inválido", validar_programacion_retos({'2026-07': 'xxx'}, cods)[0] is False)
    check("no-dict → inválido", validar_programacion_retos([], cods)[0] is False)

    print("\n[5] seleccionar_reto — función pura")
    pool = [
        {'codigo': 'a', 'nombre': 'A', 'metrica': 'ventas_mes'},
        {'codigo': 'b', 'nombre': 'B', 'metrica': 'productos_mes'},
    ]
    # Rotación determinista por índice de mes.
    r_ene = seleccionar_reto(pool, {}, datetime(2026, 1, 15))
    r_feb = seleccionar_reto(pool, {}, datetime(2026, 2, 15))
    check("rotación cambia entre meses consecutivos", r_ene['codigo'] != r_feb['codigo'])
    check("rotación determinista (mismo mes → mismo reto)",
          seleccionar_reto(pool, {}, datetime(2026, 1, 2))['codigo'] == r_ene['codigo'])
    # Programación gana sobre rotación.
    forzado = seleccionar_reto(pool, {'2026-01': 'b'}, datetime(2026, 1, 15))
    check("programación gana sobre rotación", forzado['codigo'] == 'b')
    check("programación con código inexistente → cae a rotación",
          seleccionar_reto(pool, {'2026-01': 'zzz'}, datetime(2026, 1, 15))['codigo'] == r_ene['codigo'])
    check("pool vacío → None", seleccionar_reto([], {}, datetime(2026, 1, 1)) is None)

    print("\n[6] Fallback sin BD (_reto_del_mes)")
    reto = _reto_del_mes(datetime(2026, 5, 15))
    check("_reto_del_mes devuelve un reto del default (fallback)",
          reto is not None and reto in RETOS_MENSUALES)

    print("\n[7] Endpoints")
    import src.api.admin_api as api
    check("get_gamif_retos existe", hasattr(api, 'get_gamif_retos'))
    check("update_gamif_retos existe", hasattr(api, 'update_gamif_retos'))
    import inspect
    src_api = inspect.getsource(api.update_gamif_retos)
    check("update audita", 'registrar_auditoria' in src_api)
    check("update valida retos y programación",
          'validar_retos' in src_api and 'validar_programacion_retos' in src_api)

    print(f"\n{'='*50}\n  RESULTADO: {PASS} pasaron, {FAIL} fallaron\n{'='*50}")
    return 0 if FAIL == 0 else 1


if __name__ == '__main__':
    sys.exit(main())
