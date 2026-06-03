"""
Test de items de la tienda TuKoins + seeder idempotente (Sprint 15).

Ejecutar:
    PYTHONUTF8=1 venv/Scripts/python.exe src/tests_apis/test_tienda_items_s15.py
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
    from src.models.colombia_data.ratings.negocio_gamificacion import (
        TiendaItem, TIENDA_ITEMS_SEED, seed_tienda_items
    )

    print("\n[1] Catálogo de items ampliado")
    check("20 items en el seed (ampliado de 9)", len(TIENDA_ITEMS_SEED) == 20)
    cods = {i['codigo'] for i in TIENDA_ITEMS_SEED}
    check("códigos únicos (sin duplicados)", len(cods) == len(TIENDA_ITEMS_SEED))
    tipos = {i['tipo'] for i in TIENDA_ITEMS_SEED}
    check("incluye tipo 'tema_color' (nuevo)", 'tema_color' in tipos)
    for c in ['marco_neon', 'tema_oceano', 'tema_medianoche', 'sticker_eco', 'fondo_geometrico']:
        check(f"item '{c}' presente", c in cods)

    print("\n[2] Seeder idempotente (SQLite en memoria)")
    app = _app()
    with app.app_context():
        db.metadata.create_all(bind=db.engine, tables=[TiendaItem.__table__])
        r1 = seed_tienda_items(db.session)
        check(f"1ra siembra crea {len(TIENDA_ITEMS_SEED)} items", r1['creados'] == len(TIENDA_ITEMS_SEED))
        check("items en BD = catálogo", db.session.query(TiendaItem).count() == len(TIENDA_ITEMS_SEED))

        r2 = seed_tienda_items(db.session)
        check("2da siembra crea 0 (idempotente)", r2['creados'] == 0)
        check("sin duplicados tras re-seed", db.session.query(TiendaItem).count() == len(TIENDA_ITEMS_SEED))

        # actualización de precio se refleja en re-seed
        it = db.session.query(TiendaItem).filter_by(codigo='marco_neon').first()
        it.precio_tukoins = 999
        db.session.commit()
        r3 = seed_tienda_items(db.session)
        it2 = db.session.query(TiendaItem).filter_by(codigo='marco_neon').first()
        check("re-seed restaura precio del catálogo", it2.precio_tukoins == 130)
        check("re-seed reporta >=1 actualizado", r3['actualizados'] >= 1)

    print(f"\n{'='*50}\n  RESULTADO: {PASS} pasaron, {FAIL} fallaron\n{'='*50}")
    return 0 if FAIL == 0 else 1


if __name__ == '__main__':
    sys.exit(main())
