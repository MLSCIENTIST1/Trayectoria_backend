"""
Centro de Ayuda — API pública (lectura).  Fase 3: M3.1 (lectura) + M3.2 (búsqueda).

Lee de la tabla `plataforma_kb` SOLO contenido publicado (`publicado`).
Endpoints (todos públicos, sin auth), url_prefix `/api/ayuda`:
  GET /home               → categorías + populares + novedades (para la home)
  GET /categorias         → categorías
  GET /categoria/<clave>  → artículos de esa categoría (datos.categoria == clave)
  GET /articulo/<clave>   → un artículo + relacionados
  GET /buscar?q=          → búsqueda en título/resumen/contenido
  GET /novedades          → changelog

SQL portable (PG en prod, SQLite en tests). A prueba de fallos.
© 2024-2026 Carlos Eduardo Huérfano Bermúdez.
"""
import json
import logging
from flask import Blueprint, jsonify, request
from sqlalchemy import text
from src.models.database import db

logger = logging.getLogger(__name__)
centro_ayuda_bp = Blueprint('centro_ayuda', __name__, url_prefix='/api/ayuda')


def _norm(row):
    """Normaliza una fila a dict y parsea `datos` (str JSON → dict)."""
    d = dict(row._mapping)
    dd = d.get('datos')
    if isinstance(dd, str):
        try:
            d['datos'] = json.loads(dd) if dd else {}
        except Exception:
            d['datos'] = {}
    elif dd is None:
        d['datos'] = {}
    return d


def _q(sql, params=None):
    try:
        return [_norm(r) for r in db.session.execute(text(sql), params or {}).fetchall()]
    except Exception as e:
        logger.warning(f"[centro_ayuda] query no crítica: {e}")
        db.session.rollback()
        return []


_FIELDS = "clave, tipo, area, titulo, resumen, datos, orden"


@centro_ayuda_bp.route('/home', methods=['GET'])
def home():
    cats = _q(f"SELECT {_FIELDS} FROM plataforma_kb WHERE tipo='categoria' AND publicado ORDER BY orden, titulo")
    populares = _q(f"SELECT {_FIELDS} FROM plataforma_kb WHERE tipo = 'articulo' AND publicado ORDER BY orden, titulo LIMIT 6")
    novedades = _q(f"SELECT {_FIELDS} FROM plataforma_kb WHERE tipo='changelog' AND publicado ORDER BY orden, titulo LIMIT 5")
    return jsonify({'success': True, 'categorias': cats, 'populares': populares, 'novedades': novedades})


@centro_ayuda_bp.route('/categorias', methods=['GET'])
def categorias():
    return jsonify({'success': True, 'categorias':
                    _q(f"SELECT {_FIELDS} FROM plataforma_kb WHERE tipo='categoria' AND publicado ORDER BY orden, titulo")})


@centro_ayuda_bp.route('/categoria/<clave>', methods=['GET'])
def categoria(clave):
    arts = _q(f"""SELECT {_FIELDS}, contenido FROM plataforma_kb
                  WHERE publicado AND tipo = 'articulo'
                    AND (datos->>'categoria' = :c)
                  ORDER BY orden, titulo""", {'c': clave})
    cat = _q(f"SELECT {_FIELDS} FROM plataforma_kb WHERE clave=:c AND tipo='categoria'", {'c': clave})
    return jsonify({'success': True, 'categoria': cat[0] if cat else None, 'articulos': arts})


@centro_ayuda_bp.route('/articulo/<clave>', methods=['GET'])
def articulo(clave):
    rows = _q(f"SELECT {_FIELDS}, contenido FROM plataforma_kb WHERE clave=:c AND publicado", {'c': clave})
    if not rows:
        return jsonify({'success': False, 'error': 'Artículo no encontrado'}), 404
    art = rows[0]
    rel = _q(f"""SELECT {_FIELDS} FROM plataforma_kb
                 WHERE publicado AND tipo = 'articulo' AND clave<>:c
                   AND (datos->>'categoria' = (:cat))
                 ORDER BY orden LIMIT 4""", {'cat': (art.get('datos') or {}).get('categoria'), 'c': clave})
    return jsonify({'success': True, 'articulo': art, 'relacionados': rel})


@centro_ayuda_bp.route('/buscar', methods=['GET'])
def buscar():
    q = (request.args.get('q') or '').strip()
    if len(q) < 2:
        return jsonify({'success': True, 'q': q, 'resultados': []})
    like = f"%{q.lower()}%"
    res = _q(f"""SELECT {_FIELDS} FROM plataforma_kb
                 WHERE publicado AND tipo IN ('articulo','categoria')
                   AND (LOWER(titulo) LIKE :l OR LOWER(COALESCE(resumen,'')) LIKE :l
                        OR LOWER(COALESCE(contenido,'')) LIKE :l)
                 ORDER BY orden, titulo LIMIT 20""", {'l': like})
    return jsonify({'success': True, 'q': q, 'resultados': res})


@centro_ayuda_bp.route('/novedades', methods=['GET'])
def novedades():
    return jsonify({'success': True, 'novedades':
                    _q(f"SELECT {_FIELDS}, contenido FROM plataforma_kb WHERE tipo='changelog' AND publicado ORDER BY orden, titulo")})
