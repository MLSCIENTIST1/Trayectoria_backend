"""
Test de badges secretos (Sprint 12).
Verifica definiciones, ocultamiento en vista pública y seeder.

Ejecutar:
    PYTHONUTF8=1 venv/Scripts/python.exe src/tests_apis/test_badges_secretos.py
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
    from src.models.colombia_data.ratings.negocio_badge import (
        NegocioBadge, BADGES_INICIALES, seed_badges_catalogo
    )

    SECRETOS = ['noctambulo', 'velocista', 'cumpleanero', 'guerrero_finde']
    by = {b['codigo']: b for b in BADGES_INICIALES}

    print("\n[1] Badges secretos definidos y marcados es_secreto")
    for c in SECRETOS:
        check(f"'{c}' existe", c in by)
        check(f"'{c}' es_secreto=True", by.get(c, {}).get('es_secreto') is True)

    print("\n[2] Criterios temporales correctos")
    check("noctambulo = ventas_madrugada >= 1", by['noctambulo']['criterio_tipo'] == 'ventas_madrugada')
    check("velocista = max_pedidos_dia >= 10",
          by['velocista']['criterio_tipo'] == 'max_pedidos_dia' and by['velocista']['criterio_valor'] == 10)
    check("guerrero_finde = ventas_fin_semana >= 20", by['guerrero_finde']['criterio_valor'] == 20)

    print("\n[3] Ocultamiento en vista pública (serialize_publico)")
    app = _app()
    with app.app_context():
        db.metadata.create_all(bind=db.engine, tables=[NegocioBadge.__table__])
        seed_badges_catalogo(db.session)

        noct = db.session.query(NegocioBadge).filter_by(codigo='noctambulo').first()
        check("noctambulo sembrado en BD", noct is not None)
        pub = noct.serialize_publico()
        check("vista pública oculta el nombre (???)", pub['nombre'] == '???')
        check("vista pública marca es_secreto", pub.get('es_secreto') is True)
        # admin sí ve el nombre real
        adm = noct.serialize()
        check("serialize() admin muestra nombre real", adm['nombre'] == 'Noctámbulo')

        # criterio del modelo evalúa bien (10 pedidos en un día → velocista)
        velo = db.session.query(NegocioBadge).filter_by(codigo='velocista').first()
        check("velocista.verificar_criterio(10) == True", velo.verificar_criterio(10) is True)
        check("velocista.verificar_criterio(9) == False", velo.verificar_criterio(9) is False)

    print(f"\n{'='*50}\n  RESULTADO: {PASS} pasaron, {FAIL} fallaron\n{'='*50}")
    return 0 if FAIL == 0 else 1


if __name__ == '__main__':
    sys.exit(main())
