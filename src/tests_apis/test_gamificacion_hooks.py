"""
Test de integración del motor de gamificación (Sprint 1).
Usa SQLite en memoria con los modelos reales.

Ejecutar:
    PYTHONUTF8=1 venv/Scripts/python.exe src/tests_apis/test_gamificacion_hooks.py
"""
import os
import sys

# UTF-8 + raíz del proyecto
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from flask import Flask
from src.models.database import db


def _build_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    # Las opciones de pool de Postgres (pool_size, max_overflow) no aplican a
    # SQLite — se limpian solo para el entorno de test en memoria.
    try:
        db._engine_options = {}
    except Exception:
        pass
    db.init_app(app)
    return app


PASS = 0
FAIL = 0

def check(nombre, condicion):
    global PASS, FAIL
    if condicion:
        PASS += 1
        print(f"  ✅ {nombre}")
    else:
        FAIL += 1
        print(f"  ❌ {nombre}")


def main():
    # ── Test 1: lógica pura de niveles (sin DB) ──────────────────────
    print("\n[1] Lógica de niveles (NegocioGamificacion.calcular_nivel)")
    from src.models.colombia_data.ratings.negocio_gamificacion import NegocioGamificacion

    g = NegocioGamificacion()
    g.xp_total = 0; g.nivel = 1
    g.calcular_nivel()
    check("0 XP → nivel 1", g.nivel == 1)

    g.xp_total = 100; g.calcular_nivel()
    check("100 XP → nivel 2", g.nivel == 2)

    g.xp_total = 25000; g.calcular_nivel()
    check("25000 XP → nivel 30 (Leyenda)", g.nivel == 30)

    g.xp_total = 50; g.nivel = 1
    subio = g.agregar_xp(60, 'test')  # 50→110, cruza el umbral de 100
    check("agregar_xp detecta subida de nivel", subio is True and g.nivel == 2)

    # ── Test 2: motor completo con SQLite en memoria ─────────────────
    print("\n[2] Motor de eventos (SQLite en memoria)")
    app = _build_app()
    with app.app_context():
        # Crear SOLO las tablas de gamificación (otros modelos usan JSONB
        # que SQLite no compila; no los necesitamos para este test).
        from src.api.gamificacion.gamificacion_hooks import (
            on_venta_completada, _procesar_evento, XP_EVENTOS
        )
        from src.models.colombia_data.ratings.negocio_gamificacion import (
            NegocioGamificacion, NegocioMisionCompletada, TuKoinTransaccion
        )
        db.metadata.create_all(
            bind=db.engine,
            tables=[
                NegocioGamificacion.__table__,
                NegocioMisionCompletada.__table__,
                TuKoinTransaccion.__table__,
            ],
        )

        NID = 999  # negocio de prueba

        # Primera venta del día → XP base + misión completar_venta
        cel = _procesar_evento(
            NID, evento='venta_completada',
            misiones_diarias=['completar_venta'],
            misiones_semanales=[('ventas_semana_5', False)],
            verificar_badges=False,
        )
        check("Evento retorna celebración", cel is not None)
        xp_esperado = XP_EVENTOS['venta_completada']['xp'] + 20  # base + misión
        check(f"XP ganado = {xp_esperado} (base 10 + misión 20)",
              cel and cel['xp_ganado'] == xp_esperado)
        check("Misión completar_venta registrada", cel and len(cel['misiones']) == 1)

        gami = NegocioGamificacion.query.filter_by(negocio_id=NID).first()
        check("Gamificación persistida en BD", gami is not None)
        check(f"XP total en BD = {xp_esperado}", gami and gami.xp_total == xp_esperado)

        # Segunda venta MISMO día → misión NO se repite (idempotencia)
        cel2 = _procesar_evento(
            NID, evento='venta_completada',
            misiones_diarias=['completar_venta'],
            misiones_semanales=[('ventas_semana_5', False)],
            verificar_badges=False,
        )
        check("2da venta: solo XP base, misión no se repite",
              cel2 and cel2['xp_ganado'] == XP_EVENTOS['venta_completada']['xp']
              and len(cel2['misiones']) == 0)

        total_misiones = NegocioMisionCompletada.query.filter_by(negocio_id=NID).count()
        check("Solo 1 registro de misión (idempotencia BD)", total_misiones == 1)

        # Misión semanal cuando se cumple condición
        cel3 = _procesar_evento(
            NID, evento='venta_completada',
            misiones_diarias=['completar_venta'],  # ya completada hoy
            misiones_semanales=[('ventas_semana_5', True)],  # ahora sí cumple
            verificar_badges=False,
        )
        tiene_semanal = cel3 and any(m['codigo'] == 'ventas_semana_5' for m in cel3['misiones'])
        check("Misión semanal se completa al cumplir condición", tiene_semanal)

        # ── Test 3: fault-tolerance — badge verification rota no rompe ──
        print("\n[3] Tolerancia a fallos")
        # verificar_badges=True correrá BadgeVerificationService que usa SQL
        # Postgres (INTERVAL) → falla en SQLite, pero el hook debe sobrevivir
        cel4 = on_venta_completada(NID)
        check("on_venta_completada sobrevive aunque badges fallen en SQLite",
              cel4 is not None)
        check("badges_nuevos vacío tras fallo controlado",
              cel4 and cel4['badges_nuevos'] == [])

        # ── Test 4: hooks S3/S4 (producto, tienda) ───────────────────
        print("\n[4] Hooks de producto y tienda (S3/S4)")
        from src.api.gamificacion.gamificacion_hooks import (
            on_producto_creado, on_tienda_publicada, on_login
        )
        NID2 = 1001
        cp = on_producto_creado(NID2)
        xp_prod = XP_EVENTOS['producto_creado']['xp'] + 15  # base + misión agregar_producto
        check(f"producto_creado otorga {xp_prod} XP (base+misión)",
              cp and cp['xp_ganado'] == xp_prod)

        NID3 = 1002
        ct = on_tienda_publicada(NID3)
        check("tienda_publicada otorga 100 XP",
              ct and ct['xp_ganado'] == XP_EVENTOS['tienda_publicada']['xp'])

        # ── Test 5: hook de login (S2) — racha + XP diario ───────────
        print("\n[5] Hook de login (S2)")
        NID4 = 1003
        l1 = on_login(NID4)
        check("1er login: +5 XP y racha=1",
              l1 and l1['xp_ganado'] == XP_EVENTOS['login_diario']['xp'] and l1['racha_dias'] == 1)
        l2 = on_login(NID4)  # mismo día
        check("2do login mismo día: 0 XP (no duplica)",
              l2 and l2['xp_ganado'] == 0)
        gami4 = NegocioGamificacion.query.filter_by(negocio_id=NID4).first()
        check("Racha sigue en 1 tras 2do login mismo día",
              gami4 and gami4.racha_actividad_dias == 1)

    # ── Resumen ──────────────────────────────────────────────────────
    print(f"\n{'='*50}")
    print(f"  RESULTADO: {PASS} pasaron, {FAIL} fallaron")
    print(f"{'='*50}")
    return 0 if FAIL == 0 else 1


if __name__ == '__main__':
    sys.exit(main())
