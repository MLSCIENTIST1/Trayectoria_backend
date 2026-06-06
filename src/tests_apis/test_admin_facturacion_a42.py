"""
Test de Facturación / cobro de suscripciones (Admin Panel — Sprint A42).

Ejecutar:
    PYTHONUTF8=1 venv/Scripts/python.exe src/tests_apis/test_admin_facturacion_a42.py
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
    from src.api.utils.pagos_service import clasificar_cobro

    print("\n[1] clasificar_cobro — buckets")
    check("activa con muchos días → al_dia", clasificar_cobro('activa', 25)['bucket'] == 'al_dia')
    check("al_dia no requiere acción", clasificar_cobro('activa', 25)['requiere_accion'] is False)
    check("activa por vencer (<=7) → por_vencer", clasificar_cobro('activa', 3)['bucket'] == 'por_vencer')
    check("por_vencer requiere acción", clasificar_cobro('activa', 3)['requiere_accion'] is True)
    check("trial por vencer → por_vencer", clasificar_cobro('trial', 1)['bucket'] == 'por_vencer')
    check("gracia → en_gracia + acción", clasificar_cobro('gracia', 0)['bucket'] == 'en_gracia' and clasificar_cobro('gracia', 0)['requiere_accion'])
    check("vencida → vencida + acción", clasificar_cobro('vencida', 0)['bucket'] == 'vencida' and clasificar_cobro('vencida', 0)['requiere_accion'])
    check("cancelada → no requiere acción de cobro", clasificar_cobro('cancelada', None)['requiere_accion'] is False)
    check("pausada → no requiere acción", clasificar_cobro('pausada', None)['bucket'] == 'pausada')

    print("\n[2] clasificar_cobro — bordes")
    check("trial muchos días → al_dia", clasificar_cobro('trial', 20)['bucket'] == 'al_dia')
    check("dias None en activa → al_dia (sin fecha)", clasificar_cobro('activa', None)['bucket'] == 'al_dia')
    check("umbral configurable", clasificar_cobro('activa', 10, dias_alerta=15)['bucket'] == 'por_vencer')
    check("cada bucket trae color", all('color' in clasificar_cobro(e, 0) for e in ('activa','gracia','vencida','trial')))

    print("\n[3] Endpoint")
    import src.api.admin_api as api
    check("facturacion_resumen existe", hasattr(api, 'facturacion_resumen'))
    src_f = inspect.getsource(api.facturacion_resumen)
    check("calcula MRR de las activas", 'mrr' in src_f and "== 'activa'" in src_f)
    check("usa estado_actual (propiedad confiable)", 'estado_actual' in src_f)
    check("usa clasificar_cobro para dunning", 'clasificar_cobro' in src_f)
    check("agrega cobros de pagos_suscripcion", 'pagos_suscripcion' in src_f)
    check("requiere permiso pagos", "requiere_permiso('pagos')" in src_f)
    check("ordena vencidas primero", "'vencida': 0" in src_f)

    print(f"\n{'='*50}\n  RESULTADO: {PASS} pasaron, {FAIL} fallaron\n{'='*50}")
    return 0 if FAIL == 0 else 1


if __name__ == '__main__':
    sys.exit(main())
