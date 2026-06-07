"""
Test del Centro de Ayuda API (lectura pública sobre plataforma_kb).
SQLite en memoria + test_client. Verifica que SOLO se devuelva contenido publicado.

Ejecutar:
    PYTHONUTF8=1 venv/Scripts/python.exe src/tests_apis/test_centro_ayuda_api.py
"""
import os
import sys
import json
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from flask import Flask
from src.models.database import db

PASS = 0; FAIL = 0
def check(n, c):
    global PASS, FAIL
    if c: PASS += 1; print(f"  ✅ {n}")
    else: FAIL += 1; print(f"  ❌ {n}")


def main():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    try: db._engine_options = {}
    except Exception: pass
    db.init_app(app)

    from src.api.ayuda.centro_ayuda_api import centro_ayuda_bp
    app.register_blueprint(centro_ayuda_bp)

    with app.app_context():
        from sqlalchemy import text
        db.session.execute(text("""
            CREATE TABLE plataforma_kb (
                id INTEGER PRIMARY KEY AUTOINCREMENT, tipo TEXT, area TEXT, clave TEXT UNIQUE,
                titulo TEXT, resumen TEXT, contenido TEXT, datos TEXT, orden INTEGER, publicado BOOLEAN)"""))

        def ins(tipo, clave, titulo, pub, area=None, resumen='', contenido='', datos=None, orden=0):
            db.session.execute(text("""INSERT INTO plataforma_kb
                (tipo,area,clave,titulo,resumen,contenido,datos,orden,publicado)
                VALUES (:t,:a,:c,:ti,:r,:co,:d,:o,:p)"""),
                {'t': tipo, 'a': area, 'c': clave, 'ti': titulo, 'r': resumen, 'co': contenido,
                 'd': json.dumps(datos or {}), 'o': orden, 'p': 1 if pub else 0})

        # Publicados
        ins('categoria', 'cat-pub', 'Categoría publicada', True, area='ayuda', datos={'icono': '🚀'}, orden=1)
        ins('feature', 'art-pub', 'Cómo crear mi tienda', True, area='tienda',
            resumen='Guía para crear tu tienda', contenido='Pasos...', datos={'categoria': 'cat-pub'}, orden=1)
        ins('changelog', 'cl-pub', 'Nueva función', True, area='novedades', datos={'tipo': 'nuevo'}, orden=1)
        # Ocultos (publicado=0) — NO deben aparecer
        ins('categoria', 'cat-oculta', 'Categoría oculta', False)
        ins('feature', 'art-oculto', 'Artículo oculto secreto', False, area='tienda')
        db.session.commit()

        c = app.test_client()

        print("\n[1] /home — solo publicados")
        h = c.get('/api/ayuda/home').get_json()
        check("success", h.get('success') is True)
        check("1 categoría publicada", len(h['categorias']) == 1 and h['categorias'][0]['clave'] == 'cat-pub')
        check("datos parseado a dict", isinstance(h['categorias'][0]['datos'], dict) and h['categorias'][0]['datos'].get('icono') == '🚀')
        check("populares incluye art-pub", any(p['clave'] == 'art-pub' for p in h['populares']))
        check("novedades incluye cl-pub", any(n['clave'] == 'cl-pub' for n in h['novedades']))
        check("NO aparece nada oculto", not any('ocult' in json.dumps(h)[i:i+20].lower() for i in []) and 'cat-oculta' not in json.dumps(h))

        print("\n[2] /categorias")
        cats = c.get('/api/ayuda/categorias').get_json()
        check("solo 1 categoría (publicada)", len(cats['categorias']) == 1)

        print("\n[3] /articulo/<clave>")
        a = c.get('/api/ayuda/articulo/art-pub').get_json()
        check("devuelve el artículo", a.get('success') and a['articulo']['clave'] == 'art-pub')
        check("incluye contenido", 'contenido' in a['articulo'])
        check("artículo oculto → 404", c.get('/api/ayuda/articulo/art-oculto').status_code == 404)

        print("\n[4] /buscar")
        b = c.get('/api/ayuda/buscar?q=crear').get_json()
        check("encuentra 'crear' en publicado", any(r['clave'] == 'art-pub' for r in b['resultados']))
        b2 = c.get('/api/ayuda/buscar?q=secreto').get_json()
        check("NO encuentra contenido oculto", not any(r['clave'] == 'art-oculto' for r in b2['resultados']))
        check("query corta → vacío", c.get('/api/ayuda/buscar?q=a').get_json()['resultados'] == [])

        print("\n[5] /novedades")
        nv = c.get('/api/ayuda/novedades').get_json()
        check("1 novedad publicada", len(nv['novedades']) == 1 and nv['novedades'][0]['clave'] == 'cl-pub')

    print(f"\n{'='*50}\n  RESULTADO: {PASS} pasaron, {FAIL} fallaron\n{'='*50}")
    return 0 if FAIL == 0 else 1


if __name__ == '__main__':
    sys.exit(main())
