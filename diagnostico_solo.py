"""Solo diagnostico, sin input() — para correr automaticamente."""
import psycopg2
from psycopg2.extras import RealDictCursor

DATABASE_URL = (
    "postgresql://neondb_owner:npg_XowUyaAE7IB4"
    "@ep-polished-rice-a4shbmdi-pooler.us-east-1.aws.neon.tech"
    "/neondb?sslmode=require"
)

conn = psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)
cur  = conn.cursor()

print("\n=== 1. NEGOCIOS (activo / tiene_pagina) ===")
cur.execute("""
    SELECT n.id_negocio, n.nombre_negocio, n.slug,
           n.activo, n.tiene_pagina,
           u.correo,
           COUNT(pc.id_producto) AS total_productos
    FROM   negocios n
    LEFT JOIN usuarios u  ON u.id_usuario = n.usuario_id
    LEFT JOIN productos_catalogo pc ON pc.negocio_id = n.id_negocio
    GROUP BY n.id_negocio, n.nombre_negocio, n.slug, n.activo, n.tiene_pagina, u.correo
    ORDER BY n.id_negocio;
""")
for n in cur.fetchall():
    warn = " <-- PROBLEMA 404" if not n['activo'] or not n['tiene_pagina'] else ""
    print(f"  id={n['id_negocio']:<4} slug={str(n['slug']):<22} activo={str(n['activo']):<5} "
          f"tiene_pagina={str(n['tiene_pagina']):<5} prods={n['total_productos']:>4} "
          f"usuario={n['correo']}{warn}")

print("\n=== 2. HUERFANOS (negocio_id IS NULL) ===")
cur.execute("SELECT COUNT(*) AS c FROM productos_catalogo WHERE negocio_id IS NULL;")
print(f"  Huerfanos: {cur.fetchone()['c']}")

print("\n=== 3. PRODUCTOS POR NEGOCIO / USUARIO ===")
cur.execute("""
    SELECT u.correo, n.id_negocio, n.nombre_negocio, n.slug,
           COUNT(pc.id_producto) AS total
    FROM   usuarios u
    JOIN   negocios n ON n.usuario_id = u.id_usuario
    LEFT JOIN productos_catalogo pc ON pc.negocio_id = n.id_negocio
    GROUP BY u.correo, n.id_negocio, n.nombre_negocio, n.slug
    ORDER BY u.correo, n.id_negocio;
""")
usuario_prev = None
for r in cur.fetchall():
    if r['correo'] != usuario_prev:
        usuario_prev = r['correo']
        print(f"\n  Usuario: {r['correo']}")
    print(f"    negocio {r['id_negocio']} ({r['slug']:<22}): {r['total']:>4} productos")

print("\n=== 4. CHEQUEO ESPECIFICO: rodar / caballeroshouse ===")
for slug in ['rodar', 'caballeroshouse']:
    cur.execute("""
        SELECT n.id_negocio, n.slug, n.activo, n.tiene_pagina,
               COUNT(pc.id_producto) AS total
        FROM   negocios n
        LEFT JOIN productos_catalogo pc ON pc.negocio_id = n.id_negocio
        WHERE  n.slug = %s
        GROUP BY n.id_negocio, n.slug, n.activo, n.tiene_pagina;
    """, (slug,))
    row = cur.fetchone()
    if not row:
        print(f"  slug='{slug}' NO encontrado")
    else:
        issues = [k for k in ['activo','tiene_pagina'] if not row[k]]
        estado = ("PROBLEMA: " + ", ".join(f"{k}=False" for k in issues)) if issues else "OK"
        print(f"  slug='{slug}' id={row['id_negocio']} prods={row['total']} -> {estado}")

conn.close()
print("\nDiagnostico completo.")
