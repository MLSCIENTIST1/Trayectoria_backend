"""
Documentación Maestra — Fase 4: SEGURIDAD DE ACCESO.
Garantiza que el contenido 🔴 'superadmin' NUNCA se filtra sin desbloqueo.

Usa SQLite en memoria + el MISMO filtro que usan los endpoints
(tipo='tecnico' AND nivel_acceso IN niveles_visibles(...)).

Ejecutar:
    PYTHONUTF8=1 venv/Scripts/python.exe src/tests_apis/test_docs_acceso.py
"""
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from flask import Flask
from sqlalchemy import text
from src.models.database import db

PASS = 0; FAIL = 0
def check(n, c):
    global PASS, FAIL
    if c: PASS += 1; print(f"  ✅ {n}")
    else: FAIL += 1; print(f"  ❌ {n}")


def _ids(rows):
    return {r[0] for r in rows}


def main():
    from src.api.ayuda.docs_tecnicas_api import niveles_visibles, UNLOCK_TTL

    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    try: db._engine_options = {}
    except Exception: pass
    db.init_app(app)

    with app.app_context():
        db.session.execute(text("""
            CREATE TABLE plataforma_kb (
                id INTEGER PRIMARY KEY AUTOINCREMENT, tipo TEXT, area TEXT, clave TEXT UNIQUE,
                titulo TEXT, resumen TEXT, contenido TEXT, datos TEXT, orden INTEGER,
                publicado BOOLEAN, nivel_acceso TEXT)"""))
        def ins(clave, nivel, tipo='tecnico'):
            db.session.execute(text("INSERT INTO plataforma_kb (tipo,area,clave,titulo,orden,publicado,nivel_acceso) "
                                    "VALUES (:t,'seguridad',:c,:c,1,1,:n)"), {'t': tipo, 'c': clave, 'n': nivel})
        ins('d-pub', 'publico'); ins('d-adm', 'admin'); ins('d-sup', 'superadmin')
        ins('otro-no-tecnico', 'superadmin', tipo='feature')  # NO debe salir nunca (no es 'tecnico')
        db.session.commit()

        def consultar(niveles):
            ph = ','.join(f"'{n}'" for n in niveles)
            sql = f"SELECT clave FROM plataforma_kb WHERE tipo='tecnico' AND nivel_acceso IN ({ph})"
            return _ids(db.session.execute(text(sql)).fetchall())

        print("\n[1] BLOQUEADO (sin step-up) → NO se ve lo 🔴 superadmin")
        bloq = consultar(niveles_visibles(False))
        check("ve público", 'd-pub' in bloq)
        check("ve admin", 'd-adm' in bloq)
        check("NO ve superadmin 🔴", 'd-sup' not in bloq)

        print("\n[2] DESBLOQUEADO (step-up vigente) → sí ve lo 🔴")
        des = consultar(niveles_visibles(True))
        check("ahora SÍ ve superadmin", 'd-sup' in des)
        check("sigue viendo público y admin", {'d-pub', 'd-adm'} <= des)

        print("\n[3] Gate por entrada (lo que hace /entrada)")
        # Simula: entrada superadmin con bloqueo → debe negarse
        check("entrada 🔴 negada sin unlock", 'superadmin' not in niveles_visibles(False))
        check("entrada 🔴 permitida con unlock", 'superadmin' in niveles_visibles(True))

        print("\n[4] Aislamiento de tipo (solo 'tecnico')")
        # Aunque 'otro-no-tecnico' es superadmin, no es tipo tecnico → jamás aparece aquí
        check("contenido no-técnico nunca se mezcla", 'otro-no-tecnico' not in des)

        print("\n[5] Step-up tiene caducidad")
        check("TTL de desbloqueo definido (30 min)", UNLOCK_TTL == 1800)

    print(f"\n{'='*54}\n  RESULTADO: {PASS} pasaron, {FAIL} fallaron\n{'='*54}")
    return 0 if FAIL == 0 else 1


if __name__ == '__main__':
    sys.exit(main())
