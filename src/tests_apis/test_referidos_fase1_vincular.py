"""
Test Fase 1 — vínculo de referido al registrarse (?ref=TKxxx).
Cubre: ref válido, ref inválido, auto-referido, sin ref, referidor inexistente,
y usuario ya referido (constraint único).

Ejecutar:
    PYTHONUTF8=1 venv/Scripts/python.exe src/tests_apis/test_referidos_fase1_vincular.py
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

    # Predicado inyectable: existen los usuarios 100 y 101 (referidores válidos)
    existe = lambda uid: uid in {100, 101}

    app = _app()
    with app.app_context():
        db.metadata.create_all(bind=db.engine, tables=[Referido.__table__])

        print("\n[1] Sin código → no vincula, sin error")
        ref, motivo = Referido.vincular(None, 200, db.session, referidor_existe=existe)
        check("None → (None, 'sin_codigo')", ref is None and motivo == 'sin_codigo')
        ref, motivo = Referido.vincular('', 200, db.session, referidor_existe=existe)
        check("'' → 'sin_codigo'", ref is None and motivo == 'sin_codigo')

        print("\n[2] Código inválido → no vincula, sin error")
        ref, motivo = Referido.vincular('abc', 200, db.session, referidor_existe=existe)
        check("'abc' → 'codigo_invalido'", ref is None and motivo == 'codigo_invalido')

        print("\n[3] Auto-referido → rechazado")
        ref, motivo = Referido.vincular('TK200', 200, db.session, referidor_existe=existe)
        check("TK200 con nuevo=200 → 'auto_referido'", ref is None and motivo == 'auto_referido')

        print("\n[4] Referidor inexistente → rechazado")
        ref, motivo = Referido.vincular('TK999', 200, db.session, referidor_existe=existe)
        check("TK999 (no existe) → 'referidor_inexistente'", ref is None and motivo == 'referidor_inexistente')
        check("nada se guardó aún", Referido.query.count() == 0)

        print("\n[5] Código válido → vincula")
        ref, motivo = Referido.vincular('TK100', 200, db.session, referidor_existe=existe)
        check("TK100 → ('ok')", ref is not None and motivo == 'ok')
        db.session.commit()
        check("queda 1 referido en BD", Referido.query.count() == 1)
        creado = Referido.query.filter_by(referido_usuario_id=200).first()
        check("referidor correcto (100)", creado.referidor_usuario_id == 100)
        check("inicia sin recompensar", creado.recompensado is False)

        print("\n[6] Usuario ya referido → rechazado (no duplica)")
        ref, motivo = Referido.vincular('TK101', 200, db.session, referidor_existe=existe)
        check("segundo referidor para 200 → 'ya_referido'", ref is None and motivo == 'ya_referido')
        check("sigue habiendo 1 referido", Referido.query.count() == 1)

        print("\n[7] Acepta código en minúscula y solo dígitos")
        ref, motivo = Referido.vincular('tk100', 300, db.session, referidor_existe=existe)
        check("'tk100' válido → 'ok'", ref is not None and motivo == 'ok')
        db.session.commit()
        ref, motivo = Referido.vincular('101', 400, db.session, referidor_existe=existe)
        check("'101' (solo dígitos) válido → 'ok'", ref is not None and motivo == 'ok')

    print(f"\n{'='*50}\n  RESULTADO: {PASS} pasaron, {FAIL} fallaron\n{'='*50}")
    return 0 if FAIL == 0 else 1


if __name__ == '__main__':
    sys.exit(main())
