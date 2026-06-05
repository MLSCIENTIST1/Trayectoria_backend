"""
Test del gestor de eventos especiales configurables (Admin Panel — Sprint A22).

Ejecutar:
    PYTHONUTF8=1 venv/Scripts/python.exe src/tests_apis/test_admin_eventos_a22.py
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
        validar_eventos, evento_activo_en, _eventos_default
    )
    from src.models.colombia_data.ratings.negocio_gamificacion import (
        EVENTOS_ESPECIALES, evento_especial, multiplicador_xp
    )

    print("\n[1] DEFAULT")
    d = _eventos_default()
    check("hay eventos por defecto", isinstance(d, list) and len(d) >= 1)
    check("default == EVENTOS_ESPECIALES", d is EVENTOS_ESPECIALES)
    check("cada evento tiene claves requeridas",
          all(all(k in ev for k in ('codigo','nombre','icono','mes','dia_ini','dia_fin','xp_mult')) for ev in d))

    print("\n[2] evento_activo_en — función pura")
    lista = [{'codigo':'x','nombre':'X','icono':'🎉','mes':7,'dia_ini':1,'dia_fin':7,'xp_mult':3}]
    check("dentro de rango → encuentra", evento_activo_en(lista, datetime(2026,7,4)) is not None)
    check("fuera de rango (día) → None", evento_activo_en(lista, datetime(2026,7,8)) is None)
    check("fuera de rango (mes) → None", evento_activo_en(lista, datetime(2026,8,4)) is None)
    check("lista vacía → None", evento_activo_en([], datetime(2026,7,4)) is None)
    check("lista None → None", evento_activo_en(None, datetime(2026,7,4)) is None)
    check("evento corrupto no rompe", evento_activo_en([{'mes':'??'}], datetime(2026,7,4)) is None)

    print("\n[3] validar_eventos — válidos")
    ok, limpio, err = validar_eventos([
        {'codigo':'Semana Tendero','nombre':'Semana','icono':'🛍️','mes':7,'dia_ini':1,'dia_fin':7,'xp_mult':3}
    ])
    check("válido → ok", ok and err is None)
    check("código normalizado (slug)", limpio[0]['codigo'] == 'semana_tendero')
    check("tipos coercionados a int", isinstance(limpio[0]['mes'], int) and isinstance(limpio[0]['xp_mult'], int))
    ok0, limpio0, _ = validar_eventos([])
    check("lista vacía → válida (sin eventos)", ok0 and limpio0 == [])

    print("\n[4] validar_eventos — inválidos")
    check("no-lista → inválido", validar_eventos({'a':1})[0] is False)
    check("sin nombre → inválido", validar_eventos([{'codigo':'a','mes':7,'dia_ini':1,'dia_fin':7,'xp_mult':2}])[0] is False)
    check("mes fuera de rango → inválido", validar_eventos([{'codigo':'a','nombre':'A','mes':13,'dia_ini':1,'dia_fin':7,'xp_mult':2}])[0] is False)
    check("dia_ini>dia_fin → inválido", validar_eventos([{'codigo':'a','nombre':'A','mes':7,'dia_ini':9,'dia_fin':2,'xp_mult':2}])[0] is False)
    check("día 0 → inválido", validar_eventos([{'codigo':'a','nombre':'A','mes':7,'dia_ini':0,'dia_fin':7,'xp_mult':2}])[0] is False)
    check("mult fuera de rango → inválido", validar_eventos([{'codigo':'a','nombre':'A','mes':7,'dia_ini':1,'dia_fin':7,'xp_mult':99}])[0] is False)
    check("mult no numérico → inválido", validar_eventos([{'codigo':'a','nombre':'A','mes':7,'dia_ini':1,'dia_fin':7,'xp_mult':'x'}])[0] is False)
    check("código duplicado → inválido", validar_eventos([
        {'codigo':'a','nombre':'A','mes':7,'dia_ini':1,'dia_fin':7,'xp_mult':2},
        {'codigo':'a','nombre':'B','mes':8,'dia_ini':1,'dia_fin':7,'xp_mult':2},
    ])[0] is False)

    print("\n[5] Fallback sin BD (evento_especial / multiplicador_xp)")
    # Sin app context, get_eventos_especiales lanza y cae al DEFAULT del módulo.
    ev_jul = evento_especial(datetime(2026,7,4))
    check("evento_especial usa fallback al DEFAULT (Semana del Tendero)", ev_jul is not None and ev_jul['xp_mult'] == 3)
    check("multiplicador_xp coherente con evento", multiplicador_xp(datetime(2026,7,4)) == 3)
    check("fecha sin evento → mult 1", multiplicador_xp(datetime(2026,2,2)) == 1)

    print("\n[6] Endpoints")
    import src.api.admin_api as api
    check("get_gamif_eventos existe", hasattr(api, 'get_gamif_eventos'))
    check("update_gamif_eventos existe", hasattr(api, 'update_gamif_eventos'))
    import inspect
    src_api = inspect.getsource(api.update_gamif_eventos)
    check("update audita (registrar_auditoria)", 'registrar_auditoria' in src_api)
    check("update valida (validar_eventos)", 'validar_eventos' in src_api)

    print(f"\n{'='*50}\n  RESULTADO: {PASS} pasaron, {FAIL} fallaron\n{'='*50}")
    return 0 if FAIL == 0 else 1


if __name__ == '__main__':
    sys.exit(main())
