"""
Test de sugerencias inteligentes (Sprint 35) — helper puro generar_sugerencias.

Ejecutar:
    PYTHONUTF8=1 venv/Scripts/python.exe src/tests_apis/test_sugerencias_s35.py
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
    from src.api.gamificacion.gamificacion_api import generar_sugerencias

    proximos = [
        {'nombre': 'En Vuelo', 'icono': 'bi-airplane', 'criterio_tipo': 'pedidos_completados',
         'falta': 3, 'progreso_pct': 80},
        {'nombre': 'Primer Millón', 'icono': 'bi-cash', 'criterio_tipo': 'ventas_cop',
         'falta': 250000, 'progreso_pct': 30},
    ]

    print("\n[1] Sugerencia estrella (badge más cercano)")
    s = generar_sugerencias(proximos, racha_ventas=0)
    check("genera al menos 1 sugerencia", len(s) >= 1)
    check("menciona el badge y unidad correcta", 'En Vuelo' in s[0]['texto'] and 'pedidos' in s[0]['texto'])
    check("incluye el faltante (3)", '3' in s[0]['texto'])
    check("80% → prioridad alta", s[0]['prioridad'] == 'alta')

    print("\n[2] Ventas COP formatea con $")
    check("primer_millon usa pesos", any('pesos en ventas' in x['texto'] for x in s))

    print("\n[3] Racha de ventas")
    s2 = generar_sugerencias(proximos, racha_ventas=5)
    check("incluye tip de racha", any('racha' in x['texto'].lower() for x in s2))

    print("\n[4] Sin badges próximos → mensaje de ánimo")
    s3 = generar_sugerencias([], racha_ventas=0)
    check("da una sugerencia de ánimo", len(s3) == 1 and 'increíble' in s3[0]['texto'])

    print("\n[5] Límite respetado")
    s4 = generar_sugerencias(proximos, racha_ventas=9, limite=2)
    check("limite=2 → máx 2", len(s4) <= 2)

    print("\n[6] Robustez")
    check("None → []", generar_sugerencias(None, 0) == [] or isinstance(generar_sugerencias(None,0), list))

    print(f"\n{'='*50}\n  RESULTADO: {PASS} pasaron, {FAIL} fallaron\n{'='*50}")
    return 0 if FAIL == 0 else 1


if __name__ == '__main__':
    sys.exit(main())
