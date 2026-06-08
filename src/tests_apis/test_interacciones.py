"""
Interacciones sociales de tienda — Seguir / Like (toggle, conteo, auth).

Estrategia (§7): Flask mínimo + SQLite en memoria + modelo NegocioInteraccion,
y test_client para ejercer los endpoints reales con header X-User-ID.

Ejecutar:
    PYTHONUTF8=1 venv/Scripts/python.exe src/tests_apis/test_interacciones.py
"""
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

PASS = 0; FAIL = 0
def check(n, c):
    global PASS, FAIL
    if c: PASS += 1; print(f"  ✅ {n}")
    else: FAIL += 1; print(f"  ❌ {n}")


def make_app():
    from flask import Flask
    from src.models.database import db
    # Importa el modelo → queda en metadata para create_all
    from src.models.colombia_data.negocio_interaccion import NegocioInteraccion  # noqa
    from src.api.tiendas.interacciones_api import interacciones_bp

    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['TESTING'] = True
    db._engine_options = {}  # limpia opts de pool de Postgres
    db.init_app(app)
    app.register_blueprint(interacciones_bp, url_prefix='/api')
    with app.app_context():
        # Solo nuestra tabla (otros modelos usan JSONB, no soportado en SQLite)
        NegocioInteraccion.__table__.create(bind=db.engine, checkfirst=True)
    return app, db, NegocioInteraccion


def main():
    app, db, NegocioInteraccion = make_app()
    client = app.test_client()
    NID = 4
    H = {'X-User-ID': '7'}      # usuario logueado
    H2 = {'X-User-ID': '9'}     # otro usuario

    print("\n[1] Estado inicial /social (sin interacciones, sin usuario)")
    r = client.get(f'/api/negocio/{NID}/social')
    d = r.get_json()
    check("ok", d['ok'] is True)
    check("seguidores 0", d['seguidores'] == 0)
    check("likes 0", d['likes'] == 0)
    check("siguiendo False (invitado)", d['siguiendo'] is False)

    print("\n[2] Invitado NO puede seguir → 401 requiere_login")
    r = client.post(f'/api/negocio/{NID}/seguir')
    check("status 401", r.status_code == 401)
    check("requiere_login True", r.get_json().get('requiere_login') is True)
    with app.app_context():
        check("no se creó fila", NegocioInteraccion.query.count() == 0)

    print("\n[3] Usuario sigue → crea fila y cuenta 1")
    r = client.post(f'/api/negocio/{NID}/seguir', headers=H)
    d = r.get_json()
    check("siguiendo True", d['siguiendo'] is True)
    check("seguidores 1", d['seguidores'] == 1)
    with app.app_context():
        check("1 fila en BD", NegocioInteraccion.query.count() == 1)

    print("\n[4] Mismo usuario sigue de nuevo → toggle a 0 (des-seguir)")
    r = client.post(f'/api/negocio/{NID}/seguir', headers=H)
    d = r.get_json()
    check("siguiendo False", d['siguiendo'] is False)
    check("seguidores 0", d['seguidores'] == 0)

    print("\n[5] Like es independiente de seguir")
    client.post(f'/api/negocio/{NID}/seguir', headers=H)   # vuelve a seguir
    r = client.post(f'/api/negocio/{NID}/like', headers=H)
    d = r.get_json()
    check("liked True", d['liked'] is True)
    check("likes 1", d['likes'] == 1)
    r = client.get(f'/api/negocio/{NID}/social', headers=H)
    d = r.get_json()
    check("siguiendo True y liked True a la vez", d['siguiendo'] is True and d['liked'] is True)
    check("seguidores 1 / likes 1", d['seguidores'] == 1 and d['likes'] == 1)

    print("\n[6] Dos usuarios distintos suman seguidores")
    client.post(f'/api/negocio/{NID}/seguir', headers=H2)
    r = client.get(f'/api/negocio/{NID}/social')
    check("seguidores 2", r.get_json()['seguidores'] == 2)

    print("\n[7] UNIQUE evita duplicados (no se puede seguir 2 veces sumando)")
    with app.app_context():
        # el conteo real de filas 'seguir' debe ser exactamente 2 (user 7 y 9)
        n = NegocioInteraccion.query.filter_by(negocio_id=NID, tipo='seguir').count()
        check("exactamente 2 filas 'seguir'", n == 2)

    print("\n[8] /social del otro usuario refleja su propio estado")
    r = client.get(f'/api/negocio/{NID}/social', headers=H2)
    d = r.get_json()
    check("user9 siguiendo True", d['siguiendo'] is True)
    check("user9 liked False (no dio like)", d['liked'] is False)

    print(f"\n{'='*50}\n  RESULTADO: {PASS} pasaron, {FAIL} fallaron\n{'='*50}")
    return 0 if FAIL == 0 else 1


if __name__ == '__main__':
    sys.exit(main())
