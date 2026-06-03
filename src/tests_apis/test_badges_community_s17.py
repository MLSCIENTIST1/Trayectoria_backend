"""
Test de badges de comunidad (Sprint 17).

Ejecutar:
    PYTHONUTF8=1 venv/Scripts/python.exe src/tests_apis/test_badges_community_s17.py
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
    from src.api.utils.badge_verification_service import BadgeVerificationService

    by = {b['codigo']: b for b in BADGES_INICIALES}

    print("\n[1] Badges de comunidad definidos")
    for c in ['embajador', 'vitrina_visitada', 'primera_resena', 'fan_club']:
        check(f"'{c}' existe", c in by)

    print("\n[2] Criterios correctos")
    check("embajador = votos_emitidos_owner >= 10",
          by['embajador']['criterio_tipo'] == 'votos_emitidos_owner' and by['embajador']['criterio_valor'] == 10)
    check("vitrina_visitada = visitas_tienda >= 100", by['vitrina_visitada']['criterio_valor'] == 100)
    check("primera_resena = resenas_recibidas >= 1", by['primera_resena']['criterio_valor'] == 1)
    check("fan_club = resenas_recibidas >= 25", by['fan_club']['criterio_valor'] == 25)

    print("\n[3] Evaluación de criterios")
    ev = BadgeVerificationService._evaluar_criterio
    check("100 visitas cumple vitrina (>=100)", ev(100, '>=', 100) is True)
    check("99 visitas NO cumple vitrina", ev(99, '>=', 100) is False)
    check("1 reseña cumple primera_resena", ev(1, '>=', 1) is True)

    print("\n[4] Seeder incluye comunidad")
    app = _app()
    with app.app_context():
        db.metadata.create_all(bind=db.engine, tables=[NegocioBadge.__table__])
        r = seed_badges_catalogo(db.session)
        check(f"seeder crea {len(BADGES_INICIALES)} badges", r['creados'] == len(BADGES_INICIALES))
        fc = db.session.query(NegocioBadge).filter_by(codigo='fan_club').first()
        check("fan_club sembrado con criterio resenas_recibidas",
              fc and fc.criterio_tipo == 'resenas_recibidas')

    print(f"\n{'='*50}\n  RESULTADO: {PASS} pasaron, {FAIL} fallaron\n{'='*50}")
    return 0 if FAIL == 0 else 1


if __name__ == '__main__':
    sys.exit(main())
