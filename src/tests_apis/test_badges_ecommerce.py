"""
Test de badges de e-commerce (Sprints 9 y 10).
Verifica definiciones, seeder y evaluación de criterios.

Ejecutar:
    PYTHONUTF8=1 venv/Scripts/python.exe src/tests_apis/test_badges_ecommerce.py
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

    print("\n[1] Badges S9 (pedidos) presentes")
    cods = {b['codigo'] for b in BADGES_INICIALES}
    for c in ['primera_venta', 'despegando', 'en_vuelo', 'maquina_ventas', 'leyenda_ventas']:
        check(f"badge '{c}' definido", c in cods)

    print("\n[2] Badges S10 (ingresos/calidad) presentes")
    for c in ['primer_millon', 'top_vendedor', 'unicornio', 'bien_calificado', 'confiable', 'catalogo_rico']:
        check(f"badge '{c}' definido", c in cods)

    print("\n[3] Criterios correctos")
    by = {b['codigo']: b for b in BADGES_INICIALES}
    check("primer_millon = ventas_cop >= 1.000.000",
          by['primer_millon']['criterio_tipo'] == 'ventas_cop' and by['primer_millon']['criterio_valor'] == 1000000)
    check("leyenda_ventas = pedidos_completados >= 500",
          by['leyenda_ventas']['criterio_valor'] == 500)
    check("bien_calificado = calificacion_calificada >= 4.5",
          by['bien_calificado']['criterio_tipo'] == 'calificacion_calificada' and by['bien_calificado']['criterio_valor'] == 4.5)

    print("\n[4] Evaluación de criterios (_evaluar_criterio)")
    ev = BadgeVerificationService._evaluar_criterio
    check("ventas 1.5M cumple >= 1M", ev(1500000, '>=', 1000000) is True)
    check("ventas 900k NO cumple >= 1M", ev(900000, '>=', 1000000) is False)
    check("rating 4.6 cumple >= 4.5", ev(4.6, '>=', 4.5) is True)
    check("rating 4.4 NO cumple >= 4.5", ev(4.4, '>=', 4.5) is False)
    check("1 pedido cumple >= 1 (primera venta)", ev(1, '>=', 1) is True)
    check("0 pedidos NO cumple >= 1", ev(0, '>=', 1) is False)

    print("\n[4b] Badges de creador (S11)")
    for c in ['multi_negocio', 'emprendedor_serial', 'veterano_tuko', 'pilar_comunidad']:
        check(f"badge creador '{c}' definido", c in cods)
    check("multi_negocio = negocios_del_owner >= 3",
          by['multi_negocio']['criterio_tipo'] == 'negocios_del_owner' and by['multi_negocio']['criterio_valor'] == 3)
    check("pilar_comunidad = dias_registrado_owner >= 365",
          by['pilar_comunidad']['criterio_tipo'] == 'dias_registrado_owner' and by['pilar_comunidad']['criterio_valor'] == 365)
    check("3 negocios cumple multi_negocio", ev(3, '>=', 3) is True)
    check("2 negocios NO cumple multi_negocio", ev(2, '>=', 3) is False)

    print("\n[5] Seeder incluye los nuevos badges")
    app = _app()
    with app.app_context():
        db.metadata.create_all(bind=db.engine, tables=[NegocioBadge.__table__])
        r = seed_badges_catalogo(db.session)
        check(f"seeder crea {len(BADGES_INICIALES)} badges (incluye e-commerce)",
              r['creados'] == len(BADGES_INICIALES))
        pv = db.session.query(NegocioBadge).filter_by(codigo='primera_venta').first()
        check("primera_venta en BD con criterio pedidos_completados",
              pv and pv.criterio_tipo == 'pedidos_completados')
        # criterio del modelo evalúa bien
        check("NegocioBadge.verificar_criterio(1) para primera_venta", pv and pv.verificar_criterio(1) is True)

    print(f"\n{'='*50}\n  RESULTADO: {PASS} pasaron, {FAIL} fallaron\n{'='*50}")
    return 0 if FAIL == 0 else 1


if __name__ == '__main__':
    sys.exit(main())
