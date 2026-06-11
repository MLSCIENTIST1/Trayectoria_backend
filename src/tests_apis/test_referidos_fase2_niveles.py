"""
Test Fase 2 — gatillo de dos niveles + on_pago_confirmado (punto de enganche único).
Nivel 1 = publica tienda (reusa procesar_conversion_referido, ya probado).
Nivel 2 = primer pago → procesar_pago_referido (1000 TuKoins), idempotente.

Ejecutar:
    PYTHONUTF8=1 venv/Scripts/python.exe src/tests_apis/test_referidos_fase2_niveles.py
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
    from src.models.colombia_data.ratings.referido import Referido
    from src.models.colombia_data.ratings.negocio_gamificacion import (
        NegocioGamificacion, TuKoinTransaccion
    )
    import src.api.gamificacion.gamificacion_hooks as hooks
    from src.api.gamificacion.gamificacion_api import procesar_pago_referido

    app = _app()
    with app.app_context():
        db.metadata.create_all(bind=db.engine, tables=[
            Referido.__table__, NegocioGamificacion.__table__, TuKoinTransaccion.__table__,
        ])

        print("\n[1] NIVEL 2 — primer pago premia al referidor")
        db.session.add(Referido(referidor_usuario_id=100, referido_usuario_id=200))
        db.session.commit()
        r = procesar_pago_referido(200)
        check("retorna recompensa de nivel 2", r is not None and r.get('nivel') == 2)
        check("premio = 1000 TuKoins (default)", r and r.get('tukoins') == 1000)
        ref = Referido.query.filter_by(referido_usuario_id=200).first()
        check("pago_confirmado = True", ref.pago_confirmado is True)
        check("recompensado_pago = True", ref.recompensado_pago is True)
        check("fecha_pago seteada", ref.fecha_pago is not None)

        print("\n[2] Idempotencia — no premia dos veces")
        r2 = procesar_pago_referido(200)
        check("segundo pago → None (no re-premia)", r2 is None)

        print("\n[3] Usuario sin referidor → None")
        check("procesar_pago_referido(999) → None", procesar_pago_referido(999) is None)

        print("\n[4] Niveles independientes")
        db.session.add(Referido(referidor_usuario_id=101, referido_usuario_id=300))
        db.session.commit()
        ref3 = Referido.query.filter_by(referido_usuario_id=300).first()
        ref3.convertido = True; ref3.recompensado = True  # nivel 1 ya recompensado
        db.session.commit()
        r3 = procesar_pago_referido(300)
        check("nivel 2 funciona aunque nivel 1 ya esté recompensado",
              r3 is not None and r3.get('nivel') == 2)

        print("\n[5] on_pago_confirmado — ruteo por es_primer_pago")
        hooks._owner_user_id = lambda nid: 400  # stub: dueño del negocio = usuario 400
        db.session.add(Referido(referidor_usuario_id=102, referido_usuario_id=400))
        db.session.commit()
        hooks.on_pago_confirmado(negocio_id=55, es_primer_pago=False, origen='manual')
        ref4 = Referido.query.filter_by(referido_usuario_id=400).first()
        check("es_primer_pago=False → NO premia nivel 2", ref4.recompensado_pago is False)
        hooks.on_pago_confirmado(negocio_id=55, es_primer_pago=True, origen='manual')
        ref4 = Referido.query.filter_by(referido_usuario_id=400).first()
        check("es_primer_pago=True → premia nivel 2", ref4.recompensado_pago is True)

        print("\n[6] El crédito de TuKoins queda en el historial")
        gn = NegocioGamificacion.obtener_o_crear(777, db.session)
        saldo0 = gn.tukoins
        gn.agregar_tukoins(1000, "Referido pagó su 1ª mensualidad", db_session=db.session)
        db.session.commit()
        check("saldo sube +1000", gn.tukoins == saldo0 + 1000)
        check("queda registro en historial de transacciones",
              TuKoinTransaccion.query.filter_by(negocio_id=777).count() >= 1)

    print(f"\n{'='*50}\n  RESULTADO: {PASS} pasaron, {FAIL} fallaron\n{'='*50}")
    return 0 if FAIL == 0 else 1


if __name__ == '__main__':
    sys.exit(main())
