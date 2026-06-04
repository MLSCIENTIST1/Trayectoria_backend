"""
Test del simulador / modo prueba de gamificación (Admin Panel — Sprint A13).
Verifica el cálculo dry-run (sin BD) y que NO persiste nada.

Ejecutar:
    PYTHONUTF8=1 venv/Scripts/python.exe src/tests_apis/test_admin_simulador_a13.py
"""
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

PASS = 0; FAIL = 0
def check(n, c):
    global PASS, FAIL
    if c: PASS += 1; print(f"  ✅ {n}")
    else: FAIL += 1; print(f"  ❌ {n}")


# Tabla de niveles de prueba (subconjunto, mismo formato que NIVELES)
NIVELES = [(0,1,'🌱 Semilla'), (100,2,'🌱 Semilla II'), (250,3,'🌿 Brote'), (25000,30,'🏆 Leyenda')]
XP_EVENTOS = {
    'venta_completada': {'xp': 10, 'tukoins': 3},
    'tienda_publicada': {'xp': 100, 'tukoins': 50},
}


def main():
    from src.models.colombia_data.ratings.config_gamificacion import (
        nivel_por_xp, simular_evento
    )

    print("\n[1] nivel_por_xp (pura)")
    check("0 XP → nivel 1", nivel_por_xp(0, NIVELES)[0] == 1)
    check("150 XP → nivel 2", nivel_por_xp(150, NIVELES)[0] == 2)
    check("25000 XP → nivel 30 (Leyenda)", nivel_por_xp(25000, NIVELES)[0] == 30)

    print("\n[2] simular_evento — sin multiplicadores (x1)")
    r = simular_evento('venta_completada', 0, XP_EVENTOS, 1, 1, NIVELES)
    check("xp evento = 10", r['xp_evento'] == 10)
    check("tukoins evento = 3", r['tukoins_evento'] == 3)
    check("xp total = 10", r['xp_total_otorgado'] == 10)
    check("xp final = 10", r['xp_final'] == 10)
    check("nivel antes 1 → después 1", r['nivel_antes'] == 1 and r['nivel_despues'] == 1)
    check("no sube de nivel", r['subio_nivel'] is False)

    print("\n[3] Evento especial multiplica el XP (x3)")
    r3 = simular_evento('venta_completada', 0, XP_EVENTOS, 3, 1, NIVELES)
    check("xp evento 10 × 3 = 30", r3['xp_evento'] == 30)
    check("tukoins NO se afecta por xp_mult", r3['tukoins_evento'] == 3)

    print("\n[4] Subida de nivel")
    r4 = simular_evento('tienda_publicada', 95, XP_EVENTOS, 1, 1, NIVELES)  # 95 + 100 = 195 → nivel 2
    check("95 XP nivel 1 → 195 XP nivel 2", r4['nivel_antes'] == 1 and r4['nivel_despues'] == 2)
    check("subio_nivel True", r4['subio_nivel'] is True)

    print("\n[5] Misiones: XP×mult, TuKoins×bono")
    misiones = [{'codigo': 'm1', 'nombre': 'M1', 'xp': 20, 'tukoins': 10}]
    r5 = simular_evento('venta_completada', 0, XP_EVENTOS, 2, 2, NIVELES, misiones)
    # evento: 10×2=20 ; misión: xp 20×2=40, tk 10×2=20 ; evento tk base = 3 (sin bono)
    check("xp total = 20 + 40 = 60", r5['xp_total_otorgado'] == 60)
    check("tukoins total = 3 + 20 = 23", r5['tukoins_total_otorgado'] == 23)
    check("detalle de misión presente", len(r5['misiones']) == 1 and r5['misiones'][0]['xp'] == 40)

    print("\n[6] Robustez")
    rx = simular_evento('venta_completada', 'abc', XP_EVENTOS, 1, 1, NIVELES)
    check("xp_inicial inválido → 0", rx['xp_inicial'] == 0)
    rn = simular_evento('inexistente', 0, XP_EVENTOS, 1, 1, NIVELES)
    check("evento desconocido → 0 XP", rn['xp_total_otorgado'] == 0)

    print("\n[7] Endpoint registrado")
    import src.api.admin_api as api
    check("simular_gamificacion existe", hasattr(api, 'simular_gamificacion'))
    import inspect
    src = inspect.getsource(api.simular_gamificacion)
    check("NO hace commit (dry-run)", 'commit' not in src)
    from src.models.admin_audit import ACCIONES_VALIDAS
    check("'simular' en acciones válidas", 'simular' in ACCIONES_VALIDAS)

    print(f"\n{'='*50}\n  RESULTADO: {PASS} pasaron, {FAIL} fallaron\n{'='*50}")
    return 0 if FAIL == 0 else 1


if __name__ == '__main__':
    sys.exit(main())
