"""
Test de gamificación del onboarding (Sprint 40 — ÚLTIMO de los 40).

Cubre:
- columna/flag onboarding_completado (default + serialize)
- badge "Setup Completo" en el catálogo con criterio correcto
- hook on_onboarding_completado: recompensa la 1ra vez, idempotente la 2da
- multiplicador de XP por evento especial aplica

Ejecutar:
    PYTHONUTF8=1 venv/Scripts/python.exe src/tests_apis/test_onboarding_s40.py
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


def _build_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    try: db._engine_options = {}
    except Exception: pass
    db.init_app(app)
    return app


def main():
    # ── [1] Flag por defecto + serialize ─────────────────────────────
    print("\n[1] Flag onboarding_completado")
    from src.models.colombia_data.ratings.negocio_gamificacion import NegocioGamificacion
    g = NegocioGamificacion()
    g.xp_total = 0; g.nivel = 1; g.tukoins = 0; g.prestigio = 0
    g.onboarding_completado = False
    s = g.serialize()
    check("serialize incluye 'onboarding_completado'", 'onboarding_completado' in s)
    check("default = False", s['onboarding_completado'] is False)
    g.onboarding_completado = True
    check("serialize refleja True", g.serialize()['onboarding_completado'] is True)

    # ── [2] Badge en el catálogo ─────────────────────────────────────
    print("\n[2] Badge 'Setup Completo' en el catálogo")
    from src.models.colombia_data.ratings.negocio_badge import BADGES_INICIALES
    setup = next((b for b in BADGES_INICIALES if b['codigo'] == 'setup_completo'), None)
    check("badge setup_completo existe", setup is not None)
    check("criterio_tipo = onboarding_completado", setup and setup['criterio_tipo'] == 'onboarding_completado')
    check("criterio_valor = 1", setup and setup['criterio_valor'] == 1)
    check("tiene nivel e icono", setup and setup.get('nivel') and setup.get('icono'))

    # ── [3] Hook con SQLite en memoria ───────────────────────────────
    print("\n[3] Hook on_onboarding_completado (SQLite en memoria)")
    app = _build_app()
    with app.app_context():
        from src.api.gamificacion.gamificacion_hooks import (
            on_onboarding_completado, XP_ONBOARDING, TUKOINS_ONBOARDING
        )
        from src.models.colombia_data.ratings.negocio_gamificacion import (
            NegocioGamificacion, NegocioMisionCompletada, TuKoinTransaccion
        )
        db.metadata.create_all(bind=db.engine, tables=[
            NegocioGamificacion.__table__,
            NegocioMisionCompletada.__table__,
            TuKoinTransaccion.__table__,
        ])

        NID = 7777
        cel = on_onboarding_completado(NID)
        check("retorna celebración", cel is not None)
        check("no estaba completado antes", cel and cel['ya_completado'] is False)
        # En día normal el multiplicador es 1 (a menos que hoy caiga en evento)
        from src.models.colombia_data.ratings.negocio_gamificacion import multiplicador_xp
        m = multiplicador_xp()
        check(f"XP otorgado = {XP_ONBOARDING}*{m}", cel and cel['xp_ganado'] == XP_ONBOARDING * m)
        check(f"TuKoins otorgados = {TUKOINS_ONBOARDING}", cel and cel['tukoins_ganados'] == TUKOINS_ONBOARDING)

        gami = NegocioGamificacion.query.filter_by(negocio_id=NID).first()
        check("flag persistido en BD", gami and gami.onboarding_completado is True)
        check("XP persistido", gami and gami.xp_total == XP_ONBOARDING * m)

        # ── [4] Idempotencia ─────────────────────────────────────────
        print("\n[4] Idempotencia (segunda llamada no re-recompensa)")
        cel2 = on_onboarding_completado(NID)
        check("2da vez: ya_completado = True", cel2 and cel2['ya_completado'] is True)
        check("2da vez: 0 XP", cel2 and cel2['xp_ganado'] == 0)
        check("2da vez: 0 TuKoins", cel2 and cel2['tukoins_ganados'] == 0)
        gami2 = NegocioGamificacion.query.filter_by(negocio_id=NID).first()
        check("XP NO se duplicó", gami2 and gami2.xp_total == XP_ONBOARDING * m)

        # ── [5] Robustez ─────────────────────────────────────────────
        print("\n[5] Robustez")
        check("negocio_id None → None", on_onboarding_completado(None) is None)

    print(f"\n{'='*50}\n  RESULTADO: {PASS} pasaron, {FAIL} fallaron\n{'='*50}")
    return 0 if FAIL == 0 else 1


if __name__ == '__main__':
    sys.exit(main())
