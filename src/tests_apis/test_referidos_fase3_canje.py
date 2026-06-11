"""
Test Fase 3 — canje de TuKoins como abono al plan.
Cubre: cálculo dentro de tope, exceso de tope (rechaza), saldo insuficiente,
doble canje (respeta saldo restante), y registro en historial.

Ejecutar:
    PYTHONUTF8=1 venv/Scripts/python.exe src/tests_apis/test_referidos_fase3_canje.py
"""
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from flask import Flask
from src.models.database import db

PASS = 0; FAIL = 0
def check(n, c):
    global PASS, FAIL
    if c: PASS += 1; print(f"  ✅ {n}")
    else: FAIL += 1; print(f"  ❌ {n}")


def _app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    try: db._engine_options = {}
    except Exception: pass
    db.init_app(app)
    return app


def main():
    import src.models.colombia_data.ratings.config_gamificacion as cfgmod
    from src.models.colombia_data.ratings.config_gamificacion import (
        calcular_canje_tukoins, validar_tukoins_canje_config,
        TUKOINS_CANJE_CONFIG_DEFAULT
    )
    from src.models.colombia_data.ratings.negocio_gamificacion import (
        NegocioGamificacion, TuKoinTransaccion
    )
    from src.api.gamificacion.gamificacion_api import aplicar_canje_plan

    # gamif_config usa JSONB (no compila en SQLite); el getter es fail-safe pero
    # evitamos el query para no ensuciar la sesión: usamos el default directamente.
    cfgmod.get_tukoins_canje_config = lambda: dict(TUKOINS_CANJE_CONFIG_DEFAULT)

    print("\n[1] calcular_canje_tukoins — función pura (default 1 TK = $10, tope 50%)")
    ok, res, err = calcular_canje_tukoins(500, 50000)   # 500*10=5000 ; tope=25000 → OK
    check("dentro del tope → ok", ok and err is None)
    check("monto_cop = 5000", res and res['monto_cop'] == 5000)
    check("monto_efectivo = 45000", res and res['monto_efectivo'] == 45000)
    check("tope_cop = 25000 (50% de 50000)", res and res['tope_cop'] == 25000)

    ok, res, err = calcular_canje_tukoins(3000, 50000)  # 3000*10=30000 > tope 25000 → rechaza
    check("excede el tope → rechaza", (not ok) and res is None and 'tope' in (err or '').lower())

    ok, res, err = calcular_canje_tukoins(0, 50000)
    check("0 TuKoins → inválido", not ok)
    ok, res, err = calcular_canje_tukoins(100, 0)
    check("mensualidad 0 → inválido", not ok)

    print("\n[2] validar_tukoins_canje_config")
    ok, limpio, err = validar_tukoins_canje_config({'cop_por_tukoin': 20, 'tope_pct': 70})
    check("config válida", ok and limpio == {'cop_por_tukoin': 20, 'tope_pct': 70})
    check("tope_pct 150 → inválido", validar_tukoins_canje_config({'tope_pct': 150})[0] is False)
    check("cop_por_tukoin 0 → inválido", validar_tukoins_canje_config({'cop_por_tukoin': 0})[0] is False)

    print("\n[3] aplicar_canje_plan — saldo, tope, historial (SQLite)")
    app = _app()
    with app.app_context():
        db.metadata.create_all(bind=db.engine, tables=[
            NegocioGamificacion.__table__, TuKoinTransaccion.__table__,
        ])
        gn = NegocioGamificacion.obtener_o_crear(10, db.session)
        gn.tukoins = 2000
        db.session.commit()

        ok, res, err = aplicar_canje_plan(10, 500, 50000, db.session)
        db.session.commit()
        check("canje válido → ok", ok and err is None)
        check("descuenta 500 TuKoins (saldo 1500)", gn.tukoins == 1500 and res['saldo_restante'] == 1500)
        check("queda registro 'gastado' en historial",
              TuKoinTransaccion.query.filter_by(negocio_id=10, tipo='gastado').count() == 1)

        # saldo insuficiente (pide 5000, hay 1500)
        ok, res, err = aplicar_canje_plan(10, 5000, 500000, db.session)
        check("saldo insuficiente → rechaza", (not ok) and 'insuficiente' in (err or '').lower())
        check("saldo intacto tras rechazo", gn.tukoins == 1500)

        # excede tope (1000 TK = 10000 COP > tope 50% de 10000 = 5000)
        ok, res, err = aplicar_canje_plan(10, 1000, 10000, db.session)
        check("excede tope → rechaza", (not ok) and 'tope' in (err or '').lower())

        # doble canje respeta saldo restante
        ok, res, err = aplicar_canje_plan(10, 1000, 30000, db.session)  # 10000<=15000, saldo 1500>=1000
        db.session.commit()
        check("primer canje de 1000 → ok (saldo 500)", ok and gn.tukoins == 500)
        ok, res, err = aplicar_canje_plan(10, 1000, 30000, db.session)  # saldo 500 < 1000
        check("segundo canje sin saldo → rechaza", (not ok) and 'insuficiente' in (err or '').lower())

    print(f"\n{'='*50}\n  RESULTADO: {PASS} pasaron, {FAIL} fallaron\n{'='*50}")
    return 0 if FAIL == 0 else 1


if __name__ == '__main__':
    sys.exit(main())
