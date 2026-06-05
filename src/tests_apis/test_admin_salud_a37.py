"""
Test de salud del sistema (Admin Panel — Sprint A37).

Ejecutar:
    PYTHONUTF8=1 venv/Scripts/python.exe src/tests_apis/test_admin_salud_a37.py
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
    from src.api.utils.salud_service import evaluar_salud, UMBRAL_BUGS_ATENCION

    print("\n[1] evaluar_salud — función pura")
    ok = evaluar_salud({'db_ok': True, 'bugs_nuevos': 0})
    check("BD ok + 0 bugs → ok", ok['nivel'] == 'ok')
    check("nivel ok trae etiqueta y color", ok['etiqueta'] and ok['color'])
    crit = evaluar_salud({'db_ok': False, 'bugs_nuevos': 0})
    check("BD caída → crítico", crit['nivel'] == 'critico')
    check("BD caída pesa más que bugs", evaluar_salud({'db_ok': False, 'bugs_nuevos': 0})['nivel'] == 'critico')
    aten = evaluar_salud({'db_ok': True, 'bugs_nuevos': UMBRAL_BUGS_ATENCION})
    check("bugs >= umbral → atención", aten['nivel'] == 'atencion')
    check("bugs bajo umbral → ok", evaluar_salud({'db_ok': True, 'bugs_nuevos': UMBRAL_BUGS_ATENCION - 1})['nivel'] == 'ok')

    print("\n[2] evaluar_salud — bordes")
    check("dict vacío → ok (db asumida arriba)", evaluar_salud({})['nivel'] == 'ok')
    check("None → ok", evaluar_salud(None)['nivel'] == 'ok')
    check("bugs no numérico → no rompe", evaluar_salud({'db_ok': True, 'bugs_nuevos': 'x'})['nivel'] == 'ok')
    check("nivel siempre válido", evaluar_salud({'db_ok': True, 'bugs_nuevos': 99})['nivel'] in ('ok', 'atencion', 'critico'))

    print("\n[3] Endpoint")
    import src.api.admin_api as api
    check("salud_sistema existe", hasattr(api, 'salud_sistema'))
    src_s = inspect.getsource(api.salud_sistema)
    check("hace health de BD (SELECT 1)", 'SELECT 1' in src_s)
    check("mide latencia", 'latencia_ms' in src_s)
    check("integra reportes de error (feedback bug)", "tipo_feedback='bug'" in src_s)
    check("trae errores recientes", 'errores_recientes' in src_s)
    check("métricas de uso (24h/7d)", "INTERVAL '24 hours'" in src_s and "INTERVAL '7 days'" in src_s)
    check("usa evaluar_salud", 'evaluar_salud' in src_s)
    check("requiere permiso reportes", "requiere_permiso('reportes')" in src_s)
    check("tolerante (db_ok False si falla)", 'db_ok = False' in src_s)

    print(f"\n{'='*50}\n  RESULTADO: {PASS} pasaron, {FAIL} fallaron\n{'='*50}")
    return 0 if FAIL == 0 else 1


if __name__ == '__main__':
    sys.exit(main())
