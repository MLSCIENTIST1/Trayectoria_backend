"""
Test del cálculo de progreso hacia próximas insignias (Sprint 22).
Helper puro BadgeVerificationService.calcular_progreso.

Ejecutar:
    PYTHONUTF8=1 venv/Scripts/python.exe src/tests_apis/test_progreso_s22.py
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
    from src.api.utils.badge_verification_service import BadgeVerificationService as B

    catalogo = [
        {'id': 1, 'codigo': 'despegando', 'nombre': 'Despegando', 'criterio_tipo': 'pedidos_completados',
         'criterio_valor': 10, 'criterio_operador': '>=', 'nivel': 1},
        {'id': 2, 'codigo': 'en_vuelo', 'nombre': 'En Vuelo', 'criterio_tipo': 'pedidos_completados',
         'criterio_valor': 50, 'criterio_operador': '>=', 'nivel': 2},
        {'id': 3, 'codigo': 'primer_millon', 'nombre': 'Primer Millón', 'criterio_tipo': 'ventas_cop',
         'criterio_valor': 1000000, 'criterio_operador': '>=', 'nivel': 2},
        {'id': 4, 'codigo': 'secreto', 'nombre': 'Secreto', 'criterio_tipo': 'ventas_madrugada',
         'criterio_valor': 1, 'criterio_operador': '>=', 'nivel': 2, 'es_secreto': True},
        {'id': 5, 'codigo': 'ya_tengo', 'nombre': 'Ya tengo', 'criterio_tipo': 'pedidos_completados',
         'criterio_valor': 1, 'criterio_operador': '>=', 'nivel': 1},
    ]
    metricas = {'pedidos_completados': 8, 'ventas_cop': 250000, 'ventas_madrugada': 0}
    obtenidos = {5}  # 'ya_tengo' ya obtenido

    print("\n[1] Progreso básico")
    prox = B.calcular_progreso(catalogo, metricas, obtenidos, limite=10)
    cods = [p['codigo'] for p in prox]
    check("excluye badge ya obtenido", 'ya_tengo' not in cods)
    check("excluye badge secreto", 'secreto' not in cods)
    check("incluye despegando, en_vuelo, primer_millon", set(cods) == {'despegando', 'en_vuelo', 'primer_millon'})

    print("\n[2] Cálculo de porcentaje y faltante")
    desp = next(p for p in prox if p['codigo'] == 'despegando')
    check("despegando 8/10 → 80%", desp['progreso_pct'] == 80.0)
    check("despegando faltan 2", desp['falta'] == 2)
    millon = next(p for p in prox if p['codigo'] == 'primer_millon')
    check("primer_millon 250k/1M → 25%", millon['progreso_pct'] == 25.0)

    print("\n[3] Orden por cercanía (mayor progreso primero)")
    check("despegando (80%) va antes que en_vuelo (16%)",
          cods.index('despegando') < cods.index('en_vuelo'))

    print("\n[4] Límite respetado")
    prox2 = B.calcular_progreso(catalogo, metricas, obtenidos, limite=1)
    check("limite=1 devuelve 1", len(prox2) == 1)
    check("el más cercano es despegando", prox2[0]['codigo'] == 'despegando')

    print("\n[5] Badge ya cumplido no aparece como 'próximo'")
    metricas_full = {'pedidos_completados': 100}
    prox3 = B.calcular_progreso(
        [{'id': 9, 'codigo': 'x', 'nombre': 'X', 'criterio_tipo': 'pedidos_completados',
          'criterio_valor': 10, 'criterio_operador': '>=', 'nivel': 1}],
        metricas_full, set(), 10)
    check("100>=10 cumplido → no es próximo", len(prox3) == 0)

    print(f"\n{'='*50}\n  RESULTADO: {PASS} pasaron, {FAIL} fallaron\n{'='*50}")
    return 0 if FAIL == 0 else 1


if __name__ == '__main__':
    sys.exit(main())
