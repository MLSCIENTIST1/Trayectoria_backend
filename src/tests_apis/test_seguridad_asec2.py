"""
Test de tenant isolation / IDOR — A-SEC-2 (dominios de pagos y datos).

Ejecutar:
    PYTHONUTF8=1 venv/Scripts/python.exe src/tests_apis/test_seguridad_asec2.py
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
    from src.api.utils import seguridad as S

    print("\n[1] Helpers de tenant — sin sesión deniegan")
    check("usuario_sesion_id sin contexto → None", S.usuario_sesion_id() is None)
    check("negocio_es_de_usuario sin datos → False", S.negocio_es_de_usuario(1, 1) is False)
    check("pedido_es_de_usuario sin datos → False/None", S.pedido_es_de_usuario(1, 1) in (False, None))

    print("\n[2] El guard de tenant existe y deniega sin sesión")
    g = S.crear_guard_tenant(publicos={'publico_x'})
    check("crear_guard_tenant devuelve callable", callable(g))
    src = inspect.getsource(S.crear_guard_tenant)
    check("guard exige sesión (401 si no)", 'no_autenticado' in src and '401' in src)
    check("guard valida pedido_id (403/404)", 'pedido_es_de_usuario' in src and 'forbidden' in src)
    check("guard valida negocio_id en ruta", 'negocio_es_de_usuario' in src)
    check("guard respeta allowlist de públicos", "in publicos" in src or "endpoint in publicos" in src)
    check("guard deja pasar OPTIONS", "OPTIONS" in src)

    print("\n[3] Guards cableados en cada blueprint")
    import src.api.tiendas.pedidos_api as ped
    import src.api.tiendas.wompi_api as wmp
    import src.api.tiendas.cupones_api as cup
    import src.api.tiendas.crm_api as crm
    import src.api.tiendas.carritos_api as car
    import src.api.tiendas.resenas_api as res
    import src.api.tiendas.analytics_api as ana
    def tiene_before(bp):
        # Flask guarda funciones before_request del blueprint en deferred_functions/_got_registered… usamos el source del módulo
        return True
    for mod, nombre in [(ped,'pedidos'),(wmp,'wompi'),(cup,'cupones'),(crm,'crm'),(car,'carritos'),(res,'resenas'),(ana,'analytics')]:
        s = inspect.getsource(mod)
        check(f"{nombre}: registra guard before_request", 'before_request(_guard_tenant' in s)

    print("\n[4] Allowlists públicas correctas (no dejan endpoints privados abiertos)")
    sped = inspect.getsource(ped)
    check("pedidos público = buscar + health (no estado/pago/manual)",
          'buscar_pedido' in sped and 'pedidos_health' in sped
          and 'cambiar_estado_pedido' not in sped.split('publicos=')[1].split('}')[0]
          and 'marcar_pagado' not in sped.split('publicos=')[1].split('}')[0])
    scrm = inspect.getsource(crm)
    check("crm: publicos=set() (todo privado, PII)", 'publicos=set()' in scrm)
    swmp = inspect.getsource(wmp)
    _wmp_publicos = swmp.split('publicos=')[1].split('}')[0]
    check("wompi: PUT config NO es público",
          'put_wompi_config' not in _wmp_publicos and '"get_wompi_config"' not in _wmp_publicos
          and "'get_wompi_config'" not in _wmp_publicos)
    check("wompi: webhook/session/verify/config-pub sí públicos",
          all(x in swmp for x in ['wompi_webhook','crear_sesion_wompi','verify_wompi_transaction','get_wompi_config_pub']))

    print("\n[5] Wompi webhook — firma obligatoria + monto")
    swh = inspect.getsource(wmp.wompi_webhook)
    check("firma OBLIGATORIA (rechaza si no hay events_key/checksum)", 'firma_requerida' in swh)
    check("valida monto vs total del pedido", 'monto_no_coincide' in swh)
    check("idempotente (no re-marca pagado)", "estado_pago == 'pagado'" in swh)
    check("usa compare_digest", 'compare_digest' in swh)

    print("\n[6] Auth por sesión (no header forjable)")
    import src.api.negocio.catalogo_api as cat
    sca = inspect.getsource(cat.get_authorized_user_id)
    check("catalogo: ya NO prioriza el header X-User-ID", 'Usando Header' not in sca and "request.headers.get('X-User-ID')" not in sca)
    check("catalogo: usa la sesión (current_user)", 'current_user' in sca)
    sgu = inspect.getsource(ped.get_user_id)
    check("pedidos.get_user_id sin fallback a header", "headers.get('X-User-ID'" not in sgu)

    print("\n[7] pedidos: telefono y devolución validan propiedad")
    check("buscar por telefono exige dueño", 'negocio_es_de_usuario' in inspect.getsource(ped.buscar_pedido))
    check("recibir_devolucion valida propiedad", 'negocio_es_de_usuario' in inspect.getsource(ped.recibir_devolucion))

    print(f"\n{'='*50}\n  RESULTADO: {PASS} pasaron, {FAIL} fallaron\n{'='*50}")
    return 0 if FAIL == 0 else 1


if __name__ == '__main__':
    sys.exit(main())
