"""
Test de moderación del feed de comunidad (Admin Panel — Sprint A32).

Ejecutar:
    PYTHONUTF8=1 venv/Scripts/python.exe src/tests_apis/test_admin_feed_comunidad_a32.py
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
    from src.models.colombia_data.ratings.config_gamificacion import (
        validar_feed_comunidad_config, get_feed_comunidad_config, FEED_COMUNIDAD_DEFAULT
    )

    print("\n[1] DEFAULT")
    check("nivel_minimo default 3 (Oro)", FEED_COMUNIDAD_DEFAULT['nivel_minimo'] == 3)
    check("limite default 15", FEED_COMUNIDAD_DEFAULT['limite'] == 15)
    check("get sin BD → default", get_feed_comunidad_config() == FEED_COMUNIDAD_DEFAULT)

    print("\n[2] validar_feed_comunidad_config")
    ok, limpio, err = validar_feed_comunidad_config({'nivel_minimo': 4, 'limite': 30})
    check("válido → ok", ok and err is None and limpio == {'nivel_minimo': 4, 'limite': 30})
    check("vacío → defaults", validar_feed_comunidad_config({})[1] == FEED_COMUNIDAD_DEFAULT)
    check("nivel 0 → inválido", validar_feed_comunidad_config({'nivel_minimo': 0})[0] is False)
    check("nivel 6 → inválido", validar_feed_comunidad_config({'nivel_minimo': 6})[0] is False)
    check("limite 0 → inválido", validar_feed_comunidad_config({'limite': 0})[0] is False)
    check("limite 999 → inválido", validar_feed_comunidad_config({'limite': 999})[0] is False)
    check("no numérico → inválido", validar_feed_comunidad_config({'nivel_minimo': 'x'})[0] is False)
    check("no-dict → inválido", validar_feed_comunidad_config('x')[0] is False)

    print("\n[3] El feed público usa config + excluye ocultos")
    import src.api.gamificacion.gamificacion_api as g
    src_feed = inspect.getsource(g.eventos_comunidad)
    check("lee get_feed_comunidad_config", 'get_feed_comunidad_config' in src_feed)
    check("excluye oculto_feed", 'oculto_feed IS FALSE' in src_feed or 'oculto_feed IS NULL' in src_feed)
    check("usa nivel y limite configurables", ':niv' in src_feed and ':lim' in src_feed)

    print("\n[4] Endpoints admin")
    import src.api.admin_api as api
    check("admin_feed_comunidad existe", hasattr(api, 'admin_feed_comunidad'))
    check("ocultar_evento_comunidad existe", hasattr(api, 'ocultar_evento_comunidad'))
    check("update_feed_comunidad_config existe", hasattr(api, 'update_feed_comunidad_config'))
    src_oc = inspect.getsource(api.ocultar_evento_comunidad)
    check("ocultar actualiza oculto_feed (sin revocar badge)", 'oculto_feed' in src_oc and 'activo' not in src_oc.split('UPDATE')[1].split('WHERE')[0])
    check("ocultar 404 si no existe", '404' in src_oc)
    check("ocultar audita", 'registrar_auditoria' in src_oc)
    src_cfg = inspect.getsource(api.update_feed_comunidad_config)
    check("config valida y audita", 'validar_feed_comunidad_config' in src_cfg and 'registrar_auditoria' in src_cfg)

    print(f"\n{'='*50}\n  RESULTADO: {PASS} pasaron, {FAIL} fallaron\n{'='*50}")
    return 0 if FAIL == 0 else 1


if __name__ == '__main__':
    sys.exit(main())
