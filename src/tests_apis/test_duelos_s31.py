"""
Test de duelos entre negocios (Sprint 31).

Ejecutar:
    PYTHONUTF8=1 venv/Scripts/python.exe src/tests_apis/test_duelos_s31.py
"""
import os
import sys
from datetime import datetime, timedelta
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
    from src.models.colombia_data.ratings.duelo import Duelo, determinar_ganador, DURACION_DUELO_DIAS

    print("\n[1] Determinar ganador (pura)")
    check("retador gana (10>7)", determinar_ganador(1, 10, 2, 7) == 1)
    check("retado gana (5<9)", determinar_ganador(1, 5, 2, 9) == 2)
    check("empate → None", determinar_ganador(1, 4, 2, 4) is None)
    check("empate en 0 → None", determinar_ganador(1, 0, 2, 0) is None)

    print("\n[2] Duración del duelo")
    check("duración = 7 días", DURACION_DUELO_DIAS == 7)

    print("\n[3] Aceptar duelo (estado + fechas)")
    app = _app()
    with app.app_context():
        db.metadata.create_all(bind=db.engine, tables=[Duelo.__table__])
        d = Duelo(retador_negocio_id=1, retado_negocio_id=2, estado='pendiente')
        db.session.add(d); db.session.commit()
        check("inicia pendiente", d.estado == 'pendiente')
        d.aceptar()
        db.session.commit()
        check("tras aceptar → activo", d.estado == 'activo')
        check("fecha_fin = inicio + 7d",
              d.fecha_fin and abs((d.fecha_fin - d.fecha_inicio) - timedelta(days=7)).total_seconds() < 2)

        # serialize
        s = d.serialize()
        check("serialize incluye estado y ventas", 'estado' in s and 'ventas_retador' in s)

    print("\n[4] Rechazo")
    with app.app_context():
        db.metadata.create_all(bind=db.engine, tables=[Duelo.__table__])
        d2 = Duelo(retador_negocio_id=3, retado_negocio_id=4, estado='pendiente')
        db.session.add(d2); db.session.commit()
        d2.estado = 'rechazado'; db.session.commit()
        check("se puede rechazar", d2.estado == 'rechazado')

    print(f"\n{'='*50}\n  RESULTADO: {PASS} pasaron, {FAIL} fallaron\n{'='*50}")
    return 0 if FAIL == 0 else 1


if __name__ == '__main__':
    sys.exit(main())
