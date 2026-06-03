"""
Test de badges de temporada (Sprint 13).
Valida el helper puro temporadas_activas() con fechas inyectadas + seeder.

Ejecutar:
    PYTHONUTF8=1 venv/Scripts/python.exe src/tests_apis/test_badges_temporada.py
"""
import os
import sys
from datetime import datetime
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
    from src.api.utils.badge_verification_service import temporadas_activas, SEASONAL_METRICS
    from src.models.colombia_data.ratings.negocio_badge import (
        NegocioBadge, BADGES_INICIALES, seed_badges_catalogo
    )

    print("\n[1] Ventanas de temporada (helper puro)")
    nav = temporadas_activas(datetime(2026, 12, 15))
    check("15-dic activa Navidad", 'ventas_navidad' in nav)
    check("15-dic NO activa otras", len(nav) == 1)

    amor = temporadas_activas(datetime(2026, 9, 18))
    check("18-sep activa Amor y Amistad", 'ventas_amor_amistad' in amor)

    madre = temporadas_activas(datetime(2026, 5, 10))
    check("10-may activa Día de la Madre", 'ventas_dia_madre' in madre)

    bf = temporadas_activas(datetime(2026, 11, 25))
    check("25-nov activa Black Friday", 'ventas_black_friday' in bf)
    bf_no = temporadas_activas(datetime(2026, 11, 10))
    check("10-nov NO activa Black Friday (antes del 20)", 'ventas_black_friday' not in bf_no)

    fuera = temporadas_activas(datetime(2026, 3, 3))
    check("3-mar sin temporadas activas", len(fuera) == 0)

    print("\n[2] Ventana de Navidad correcta")
    desde, hasta = nav['ventas_navidad']
    check("Navidad inicia 1-dic", desde == datetime(2026, 12, 1))
    check("Navidad termina 31-dic", hasta.month == 12 and hasta.day == 31)

    print("\n[3] Badges de temporada en el catálogo + seeder")
    cods = {b['codigo'] for b in BADGES_INICIALES}
    for c in ['navidad_2026', 'amor_amistad', 'dia_madre', 'black_friday']:
        check(f"badge '{c}' definido", c in cods)

    app = _app()
    with app.app_context():
        db.metadata.create_all(bind=db.engine, tables=[NegocioBadge.__table__])
        r = seed_badges_catalogo(db.session)
        check(f"seeder crea {len(BADGES_INICIALES)} badges (incluye temporada)",
              r['creados'] == len(BADGES_INICIALES))
        nb = db.session.query(NegocioBadge).filter_by(codigo='black_friday').first()
        check("black_friday sembrado con criterio ventas_black_friday",
              nb and nb.criterio_tipo == 'ventas_black_friday')

    print(f"\n{'='*50}\n  RESULTADO: {PASS} pasaron, {FAIL} fallaron\n{'='*50}")
    return 0 if FAIL == 0 else 1


if __name__ == '__main__':
    sys.exit(main())
