"""
fix_ahora.py — Dos correcciones:
  1. Mover 1163 productos de negocio 23 (carlos) -> negocio 4 (rodar)
  2. Corregir slug caballeros-house -> caballeroshouse
"""
import psycopg2
from psycopg2.extras import RealDictCursor

DATABASE_URL = (
    "postgresql://neondb_owner:npg_XowUyaAE7IB4"
    "@ep-polished-rice-a4shbmdi-pooler.us-east-1.aws.neon.tech"
    "/neondb?sslmode=require"
)

conn = psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)
cur  = conn.cursor()

# ── FIX 1: Productos de negocio 23 (carlos) -> negocio 4 (rodar) ────
print("\n--- FIX 1: Mover productos de 'carlos' (23) a 'rodar' (4) ---")

cur.execute("SELECT COUNT(*) AS c FROM productos_catalogo WHERE negocio_id = 23;")
cantidad = cur.fetchone()['c']
print(f"  Productos en negocio 23: {cantidad}")

cur.execute("""
    UPDATE productos_catalogo
    SET    negocio_id = 4
    WHERE  negocio_id = 23;
""")
print(f"  [OK] {cur.rowcount} productos movidos a negocio 4 (rodar)")

# ── FIX 2: Corregir slug caballeros-house -> caballeroshouse ─────────
print("\n--- FIX 2: Slug caballeros-house -> caballeroshouse ---")

cur.execute("""
    UPDATE negocios
    SET    slug = 'caballeroshouse'
    WHERE  slug = 'caballeros-house';
""")
print(f"  [OK] {cur.rowcount} negocio(s) con slug corregido")

conn.commit()

# ── Verificacion final ───────────────────────────────────────────────
print("\n--- VERIFICACION FINAL ---")
cur.execute("""
    SELECT n.id_negocio, n.slug, COUNT(pc.id_producto) AS total
    FROM   negocios n
    LEFT JOIN productos_catalogo pc ON pc.negocio_id = n.id_negocio
    WHERE  n.slug IN ('rodar', 'carlos', 'caballeroshouse')
    GROUP BY n.id_negocio, n.slug
    ORDER BY n.id_negocio;
""")
for r in cur.fetchall():
    print(f"  negocio {r['id_negocio']} ({r['slug']}): {r['total']} productos")

conn.close()
print("\nListo. Recarga las tiendas.")
