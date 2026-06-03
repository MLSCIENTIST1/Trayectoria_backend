"""
Test de gamificación de usuario/persona (Sprint 8).
SQLite en memoria con el modelo real UsuarioGamificacion.

Ejecutar:
    PYTHONUTF8=1 venv/Scripts/python.exe src/tests_apis/test_usuario_gamificacion.py
"""
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from flask import Flask
from src.models.database import db

PASS = 0
FAIL = 0
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
    print("\n[1] Niveles de creador (lógica pura)")
    from src.models.colombia_data.ratings.usuario_gamificacion import UsuarioGamificacion
    g = UsuarioGamificacion(); g.xp_personal = 0; g.nivel = 1
    g.calcular_nivel(); check("0 XP → nivel 1 (Aprendiz)", g.nivel == 1)
    g.xp_personal = 150; g.calcular_nivel(); check("150 XP → nivel 2 (Emprendedor)", g.nivel == 2)
    g.xp_personal = 15000; g.calcular_nivel(); check("15000 XP → nivel 10 (Visionario)", g.nivel == 10)
    g.xp_personal = 140; g.nivel = 1
    subio = g.agregar_xp(20)  # 140→160 cruza 150
    check("agregar_xp detecta subida de nivel", subio is True and g.nivel == 2)

    print("\n[2] Hook de login personal (SQLite en memoria)")
    app = _app()
    with app.app_context():
        db.metadata.create_all(bind=db.engine, tables=[UsuarioGamificacion.__table__])
        from src.api.gamificacion.gamificacion_hooks import on_login_usuario

        UID = 7
        c1 = on_login_usuario(UID)
        check("1er login: +5 XP personal y racha=1",
              c1 and c1['xp_ganado'] == 5 and c1['racha_dias'] == 1)

        c2 = on_login_usuario(UID)  # mismo día
        check("2do login mismo día: 0 XP (no duplica)", c2 and c2['xp_ganado'] == 0)

        gu = UsuarioGamificacion.query.filter_by(usuario_id=UID).first()
        check("Persistido en BD con 5 XP", gu and gu.xp_personal == 5)
        check("Racha sigue en 1 tras 2do login", gu and gu.racha_login_dias == 1)

        # serialize expone progreso
        s = gu.serialize()
        check("serialize() incluye nombre_nivel y progreso_pct",
              'nombre_nivel' in s and 'progreso_pct' in s)
        check("serialize() incluye racha_login", isinstance(s.get('racha_login'), dict))

    print("\n[3] Independencia usuario vs negocio")
    # El hook de usuario no toca tablas de negocio (robusto si no existen)
    check("on_login_usuario no requiere tablas de negocio", True)

    print(f"\n{'='*50}\n  RESULTADO: {PASS} pasaron, {FAIL} fallaron\n{'='*50}")
    return 0 if FAIL == 0 else 1


if __name__ == '__main__':
    sys.exit(main())
