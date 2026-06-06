"""
Test de Web Push real (Admin Panel — Sprint A51).

Ejecutar:
    PYTHONUTF8=1 venv/Scripts/python.exe src/tests_apis/test_admin_webpush_a51.py
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
    from src.api.utils.push_service import (
        construir_payload_push, _es_suscripcion_muerta, vapid_disponible, enviar_push_a_usuario
    )

    print("\n[1] construir_payload_push — PURO")
    p = construir_payload_push('Hola', 'Mensaje', '/x')
    check("incluye title/body/url", p['title'] == 'Hola' and p['body'] == 'Mensaje' and p['url'] == '/x')
    check("url por defecto '/'", construir_payload_push('a', 'b')['url'] == '/')
    check("título recortado a 120", len(construir_payload_push('t'*200, 'b')['title']) == 120)
    check("body recortado a 300", len(construir_payload_push('t', 'b'*500)['body']) == 300)
    check("tag presente", p.get('tag') == 'tukomercio')

    print("\n[2] _es_suscripcion_muerta — PURO")
    check("404 → muerta", _es_suscripcion_muerta(404) is True)
    check("410 → muerta", _es_suscripcion_muerta(410) is True)
    check("200 → viva", _es_suscripcion_muerta(200) is False)
    check("None → no muerta", _es_suscripcion_muerta(None) is False)

    print("\n[3] vapid_disponible — PURO")
    check("sin claves → no disponible", vapid_disponible({'public': '', 'private': ''}, lib_ok=True) is False)
    check("con claves pero sin librería → no disponible", vapid_disponible({'public': 'a', 'private': 'b'}, lib_ok=False) is False)
    check("con claves y librería → disponible", vapid_disponible({'public': 'a', 'private': 'b'}, lib_ok=True) is True)
    check("cfg vacío → no disponible", vapid_disponible({}, lib_ok=True) is False)

    print("\n[4] enviar_push_a_usuario — a prueba de fallos")
    src_e = inspect.getsource(enviar_push_a_usuario)
    check("gateado por vapid_disponible", 'vapid_disponible' in src_e)
    check("elimina suscripciones muertas", '_es_suscripcion_muerta' in src_e and 'DELETE FROM push_subscriptions' in src_e)
    check("no lanza sin VAPID (retorna 0)", enviar_push_a_usuario(999999, 'x', 'y') == 0)

    print("\n[5] Endpoints + wire + migración + deps")
    import src.api.notifications.notifications_negocio_api as nn
    for fn in ['push_vapid_key', 'push_subscribe', 'push_unsubscribe']:
        check(f"{fn} existe", hasattr(nn, fn))
    src_sub = inspect.getsource(nn.push_subscribe)
    check("subscribe usa sesión (no header forjable)", '_user_id_sesion' in src_sub)
    check("subscribe upsert por endpoint", 'ON CONFLICT (endpoint)' in src_sub)
    import src.api.utils.notificaciones_service as ns
    check("notificar_negocio dispara push", 'enviar_push_a_usuario' in inspect.getsource(ns.notificar_negocio))
    import src as _src
    check("migración push_subscriptions en create_app", 'CREATE TABLE IF NOT EXISTS push_subscriptions' in inspect.getsource(_src.create_app))
    reqs = open(os.path.join(os.path.dirname(__file__), '..', '..', 'requirements.txt'), encoding='utf-16').read()
    check("pywebpush en requirements", 'pywebpush' in reqs)

    print(f"\n{'='*50}\n  RESULTADO: {PASS} pasaron, {FAIL} fallaron\n{'='*50}")
    return 0 if FAIL == 0 else 1


if __name__ == '__main__':
    sys.exit(main())
