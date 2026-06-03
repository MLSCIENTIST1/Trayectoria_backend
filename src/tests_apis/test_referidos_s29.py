"""
Test de referidos gamificados (Sprint 29).

Ejecutar:
    PYTHONUTF8=1 venv/Scripts/python.exe src/tests_apis/test_referidos_s29.py
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

    print("\n[1] Código de referido (pura)")
    check("usuario 12 → TK12", Referido.codigo_de_usuario(12) == 'TK12')
    check("'TK12' → 12", Referido.usuario_de_codigo('TK12') == 12)
    check("'tk8' (minúscula) → 8", Referido.usuario_de_codigo('tk8') == 8)
    check("'42' → 42", Referido.usuario_de_codigo('42') == 42)
    check("'abc' → None", Referido.usuario_de_codigo('abc') is None)
    check("'' → None", Referido.usuario_de_codigo('') is None)

    print("\n[2] Constraint y conversión (SQLite en memoria)")
    app = _app()
    with app.app_context():
        db.metadata.create_all(bind=db.engine, tables=[Referido.__table__])

        # usuario 100 refiere a 200
        db.session.add(Referido(referidor_usuario_id=100, referido_usuario_id=200))
        db.session.commit()
        check("referido creado", Referido.query.count() == 1)

        # un referido solo puede tener UN referidor (constraint único)
        dup_falla = False
        try:
            db.session.add(Referido(referidor_usuario_id=101, referido_usuario_id=200))
            db.session.commit()
        except Exception:
            dup_falla = True
            db.session.rollback()
        check("no se puede referir 2 veces al mismo usuario", dup_falla)

        # conversión: marcar convertido
        ref = Referido.query.filter_by(referido_usuario_id=200).first()
        check("inicia no convertido", ref.convertido is False)
        ref.convertido = True
        db.session.commit()
        convertidos = Referido.query.filter_by(referidor_usuario_id=100, convertido=True).count()
        check("referidor 100 tiene 1 convertido", convertidos == 1)

        # serialize
        s = ref.serialize()
        check("serialize incluye convertido y fechas", 'convertido' in s and 'fecha_registro' in s)

    print(f"\n{'='*50}\n  RESULTADO: {PASS} pasaron, {FAIL} fallaron\n{'='*50}")
    return 0 if FAIL == 0 else 1


if __name__ == '__main__':
    sys.exit(main())
