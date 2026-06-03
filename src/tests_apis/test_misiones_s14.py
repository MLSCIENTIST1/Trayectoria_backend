"""
Test de ampliación de misiones + misiones mensuales (Sprint 14).

Ejecutar:
    PYTHONUTF8=1 venv/Scripts/python.exe src/tests_apis/test_misiones_s14.py
"""
import os
import sys
from datetime import date
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
    from src.models.colombia_data.ratings.negocio_gamificacion import (
        POOL_MISIONES_DIARIAS, POOL_MISIONES_SEMANALES, POOL_MISIONES_MENSUALES,
        NegocioMisionCompletada
    )

    print("\n[1] Composición de los pools")
    check("12 misiones diarias (ampliado de 6)", len(POOL_MISIONES_DIARIAS) == 12)
    check("3 misiones semanales", len(POOL_MISIONES_SEMANALES) == 3)
    check("3 misiones mensuales (nuevas)", len(POOL_MISIONES_MENSUALES) == 3)

    print("\n[2] Misiones nuevas con flags correctos")
    d = {m['codigo']: m for m in POOL_MISIONES_DIARIAS}
    check("vender_3 es auto", d['vender_3']['auto'] is True)
    check("compartir_producto es manual", d['compartir_producto']['auto'] is False)
    check("dos_productos es auto", d['dos_productos']['auto'] is True)
    mm = {m['codigo']: m for m in POOL_MISIONES_MENSUALES}
    check("ventas_mes_20 existe y es auto", mm.get('ventas_mes_20', {}).get('auto') is True)
    check("ventas_mes_20 da 300 XP", mm['ventas_mes_20']['xp'] == 300)
    check("todas las mensuales tipo='mensual'", all(m['tipo'] == 'mensual' for m in POOL_MISIONES_MENSUALES))

    print("\n[3] Selección diaria sigue dando 3 distintas (de 12)")
    from src.api.gamificacion.gamificacion_api import _elegir_misiones_diarias
    sel = _elegir_misiones_diarias(4)
    check("devuelve exactamente 3 misiones", len(sel) == 3)
    check("las 3 son distintas", len({m['codigo'] for m in sel}) == 3)
    # determinista: misma entrada → mismo resultado
    sel2 = _elegir_misiones_diarias(4)
    check("selección determinista (mismo negocio/día)",
          [m['codigo'] for m in sel] == [m['codigo'] for m in sel2])

    print("\n[4] Idempotencia mensual (BD)")
    app = _app()
    with app.app_context():
        db.metadata.create_all(bind=db.engine, tables=[NegocioMisionCompletada.__table__])
        from src.api.gamificacion.gamificacion_api import _mision_completada_mes

        check("mes sin registro → no completada", _mision_completada_mes(4, 'ventas_mes_20') is False)
        db.session.add(NegocioMisionCompletada(
            negocio_id=4, gamificacion_id=1, mision_codigo='ventas_mes_20',
            fecha=date.today(), xp_ganado=300, tukoins_ganados=150, tipo='mensual'))
        db.session.commit()
        check("tras registrar → completada este mes", _mision_completada_mes(4, 'ventas_mes_20') is True)

    print(f"\n{'='*50}\n  RESULTADO: {PASS} pasaron, {FAIL} fallaron\n{'='*50}")
    return 0 if FAIL == 0 else 1


if __name__ == '__main__':
    sys.exit(main())
