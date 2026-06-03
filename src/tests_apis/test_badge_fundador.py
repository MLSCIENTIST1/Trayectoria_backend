"""
Test del seeder de badges + insignia Fundador (Sprint 5).
SQLite en memoria con el modelo real NegocioBadge.

Ejecutar:
    PYTHONUTF8=1 venv/Scripts/python.exe src/tests_apis/test_badge_fundador.py
"""
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from flask import Flask
from src.models.database import db

PASS = 0
FAIL = 0

def check(nombre, cond):
    global PASS, FAIL
    if cond:
        PASS += 1; print(f"  ✅ {nombre}")
    else:
        FAIL += 1; print(f"  ❌ {nombre}")


def _build_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    try:
        db._engine_options = {}
    except Exception:
        pass
    db.init_app(app)
    return app


def main():
    print("\n[1] Definición de la insignia Fundador")
    from src.models.colombia_data.ratings.negocio_badge import (
        NegocioBadge, BADGES_INICIALES, seed_badges_catalogo
    )
    fundador = next((b for b in BADGES_INICIALES if b['codigo'] == 'fundador'), None)
    check("Fundador existe en BADGES_INICIALES", fundador is not None)
    check("Fundador es nivel 5 (Diamante)", fundador and fundador['nivel'] == 5)
    check("Fundador es exclusivo", fundador and fundador['es_exclusivo'] is True)
    check("Fundador usa criterio es_fundador", fundador and fundador['criterio_tipo'] == 'es_fundador')
    check("Fundador tiene gradiente premium", fundador and 'gradient' in (fundador.get('gradiente') or ''))
    check("Fundador aparece de primero (orden 0)", fundador and fundador.get('orden') == 0)

    print("\n[2] Seeder idempotente (SQLite en memoria)")
    app = _build_app()
    with app.app_context():
        db.metadata.create_all(bind=db.engine, tables=[NegocioBadge.__table__])

        # Primera siembra
        r1 = seed_badges_catalogo(db.session)
        total_catalogo = len(BADGES_INICIALES)
        check(f"1ra siembra crea {total_catalogo} badges", r1['creados'] == total_catalogo)
        en_bd = db.session.query(NegocioBadge).count()
        check("Badges en BD = catálogo completo", en_bd == total_catalogo)

        # Segunda siembra → idempotente, no duplica
        r2 = seed_badges_catalogo(db.session)
        check("2da siembra crea 0 (idempotente)", r2['creados'] == 0)
        check("No hay duplicados en BD", db.session.query(NegocioBadge).count() == total_catalogo)

        # Fundador presente y correcto en BD
        f = db.session.query(NegocioBadge).filter_by(codigo='fundador').first()
        check("Fundador insertado en BD", f is not None)
        check("Fundador nivel Diamante en BD", f and f.get_nivel_nombre() == 'Diamante')
        check("Fundador puntos = 250", f and f.puntos == 250)

        # Actualización visual: cambiar descripción del modelo en BD y re-seed restaura
        f.descripcion = "TEXTO VIEJO MODIFICADO"
        db.session.commit()
        r3 = seed_badges_catalogo(db.session, actualizar_visual=True)
        f2 = db.session.query(NegocioBadge).filter_by(codigo='fundador').first()
        check("Re-seed refresca campos visuales", 'fundador' in (f2.descripcion or '').lower()
              and f2.descripcion != "TEXTO VIEJO MODIFICADO")
        check("Re-seed reporta al menos 1 actualizado", r3['actualizados'] >= 1)

    print("\n[3] Lógica del cupo de fundadores")
    from src.api.utils.badge_verification_service import FUNDADOR_CUPO
    check("FUNDADOR_CUPO definido = 50", FUNDADOR_CUPO == 50)
    # Simulación de la regla: owner es fundador si su posición <= cupo
    def es_fundador(posicion_usuario):
        return 1 if posicion_usuario <= FUNDADOR_CUPO else 0
    check("Usuario #1 es fundador", es_fundador(1) == 1)
    check("Usuario #50 es fundador (límite)", es_fundador(50) == 1)
    check("Usuario #51 NO es fundador", es_fundador(51) == 0)

    print(f"\n{'='*50}")
    print(f"  RESULTADO: {PASS} pasaron, {FAIL} fallaron")
    print(f"{'='*50}")
    return 0 if FAIL == 0 else 1


if __name__ == '__main__':
    sys.exit(main())
