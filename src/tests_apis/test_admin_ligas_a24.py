"""
Test de moderación de ligas (Admin Panel — Sprint A24).

Ejecutar:
    PYTHONUTF8=1 venv/Scripts/python.exe src/tests_apis/test_admin_ligas_a24.py
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
    from src.models.colombia_data.ratings.config_gamificacion import (
        validar_ligas_config, detectar_anomalias, LIGAS_CONFIG_DEFAULT,
        get_ligas_config, get_negocios_excluidos_ligas
    )

    print("\n[1] DEFAULT")
    check("min_participantes por defecto = 3", LIGAS_CONFIG_DEFAULT['min_participantes'] == 3)
    check("umbral_anomalia por defecto = 3.0", LIGAS_CONFIG_DEFAULT['umbral_anomalia'] == 3.0)
    check("get_ligas_config sin BD cae al DEFAULT", get_ligas_config() == LIGAS_CONFIG_DEFAULT)
    check("get_negocios_excluidos_ligas sin BD → []", get_negocios_excluidos_ligas() == [])

    print("\n[2] validar_ligas_config — válidos")
    ok, limpio, err = validar_ligas_config({'min_participantes': 5, 'umbral_anomalia': 2.5})
    check("válido → ok", ok and err is None)
    check("limpio correcto", limpio == {'min_participantes': 5, 'umbral_anomalia': 2.5})
    ok2, limpio2, _ = validar_ligas_config({})
    check("vacío → usa defaults", ok2 and limpio2 == LIGAS_CONFIG_DEFAULT)

    print("\n[3] validar_ligas_config — inválidos")
    check("min 0 → inválido", validar_ligas_config({'min_participantes': 0})[0] is False)
    check("min 200 → inválido", validar_ligas_config({'min_participantes': 200})[0] is False)
    check("umbral 0.5 → inválido", validar_ligas_config({'umbral_anomalia': 0.5})[0] is False)
    check("umbral 9 → inválido", validar_ligas_config({'umbral_anomalia': 9})[0] is False)
    check("no numérico → inválido", validar_ligas_config({'min_participantes': 'x'})[0] is False)
    check("no-dict → inválido", validar_ligas_config('x')[0] is False)

    print("\n[4] detectar_anomalias — función pura")
    # 20 negocios normales (~10) + 1 outlier altísimo (id 99).
    # Nota: con un único outlier, el z-score máximo posible ≈ sqrt(n-1); por eso se
    # necesita una liga con suficientes participantes para detectarlo (correcto:
    # las anomalías importan en ligas grandes, no en grupos de 3-4).
    filas = [(i, f'N{i}', 'Bogota', 'ropa', '', f'n{i}', 10) for i in range(1, 21)]
    filas.append((99, 'X', 'Bogota', 'ropa', '', 'x', 100))  # outlier
    anom = detectar_anomalias(filas, 3.0)
    check("detecta el outlier (id 99)", 99 in anom)
    check("no marca a los normales", all(i not in anom for i in range(1, 21)))
    check("z-score del outlier es alto", anom[99] >= 3.0)
    check("umbral muy alto → no marca nada", detectar_anomalias(filas, 6.0) == {})

    print("\n[5] detectar_anomalias — bordes")
    check("menos de 3 participantes → {}", detectar_anomalias([(1,'A','','','','a',5),(2,'B','','','','b',9)], 2.0) == {})
    check("todos iguales (desv 0) → {}", detectar_anomalias([(1,'A','','','','a',5)]*4, 2.0) == {})
    check("lista vacía → {}", detectar_anomalias([], 3.0) == {})
    check("None → {}", detectar_anomalias(None, 3.0) == {})

    print("\n[6] La liga pública excluye a los vetados (revisión de código)")
    import inspect, src.api.gamificacion.gamificacion_api as g
    src_ligas = inspect.getsource(g.ligas)
    check("ligas() consulta get_negocios_excluidos_ligas", 'get_negocios_excluidos_ligas' in src_ligas)
    check("ligas() aplica NOT IN", 'NOT IN' in src_ligas)

    print("\n[7] Endpoints + auditoría")
    import src.api.admin_api as api
    check("admin_ligas existe", hasattr(api, 'admin_ligas'))
    check("update_admin_ligas_config existe", hasattr(api, 'update_admin_ligas_config'))
    check("moderar_liga_negocio existe", hasattr(api, 'moderar_liga_negocio'))
    src_mod = inspect.getsource(api.moderar_liga_negocio)
    check("moderar audita", 'registrar_auditoria' in src_mod)
    check("moderar valida accion excluir/readmitir", 'excluir' in src_mod and 'readmitir' in src_mod)
    from src.models.admin_audit import ACCIONES_VALIDAS
    check("acciones 'excluir'/'readmitir' en whitelist", 'excluir' in ACCIONES_VALIDAS and 'readmitir' in ACCIONES_VALIDAS)

    print(f"\n{'='*50}\n  RESULTADO: {PASS} pasaron, {FAIL} fallaron\n{'='*50}")
    return 0 if FAIL == 0 else 1


if __name__ == '__main__':
    sys.exit(main())
