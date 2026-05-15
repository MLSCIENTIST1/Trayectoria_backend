"""
fix_productos_huerfanos.py
──────────────────────────────────────────────────────────────────────────────
Asigna los productos sin negocio_id al negocio correcto en Neon.

Flujo:
  1. Diagnóstico — muestra cuántos huérfanos hay y qué negocios existen.
  2. Pide confirmación antes de tocar nada.
  3. UPDATE dentro de transacción con rollback automático si algo falla.
  4. Verificación final.

Uso:
  venv\\Scripts\\python fix_productos_huerfanos.py      (Windows)
  venv/bin/python    fix_productos_huerfanos.py      (Mac/Linux)
──────────────────────────────────────────────────────────────────────────────
"""

import psycopg2
from psycopg2.extras import RealDictCursor

DATABASE_URL = (
    "postgresql://neondb_owner:npg_XowUyaAE7IB4"
    "@ep-polished-rice-a4shbmdi-pooler.us-east-1.aws.neon.tech"
    "/neondb?sslmode=require"
)

def sep(titulo=""):
    linea = "-" * 62
    if titulo:
        print(f"\n{linea}\n  {titulo}\n{linea}")
    else:
        print(linea)

def main():
    print("\n============================================================")
    print("  FIX: Productos huerfanos (negocio_id IS NULL) -> Neon")
    print("============================================================")

    conn = psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)
    cur  = conn.cursor()

    # ── PASO 1: negocios existentes ───────────────────────────────
    sep("PASO 1 — Negocios en la cuenta")

    cur.execute("""
        SELECT  n.id_negocio,
                n.nombre_negocio,
                n.slug,
                n.fecha_registro,
                COUNT(pc.id_producto) AS total_productos
        FROM    negocios n
        LEFT JOIN productos_catalogo pc ON pc.negocio_id = n.id_negocio
        GROUP BY n.id_negocio, n.nombre_negocio, n.slug, n.fecha_registro
        ORDER BY n.fecha_registro ASC;
    """)
    negocios = cur.fetchall()

    if not negocios:
        print("  [!]  No se encontraron negocios. Verifica la conexión.")
        conn.close(); return

    for n in negocios:
        fecha = str(n['fecha_registro'])[:10] if n['fecha_registro'] else "—"
        print(f"  id={n['id_negocio']:<4} | {str(n['nombre_negocio']):<28} | "
              f"slug={str(n['slug']):<20} | {n['total_productos']} prods | {fecha}")

    # ── PASO 2: huérfanos por usuario ─────────────────────────────
    sep("PASO 2 — Productos sin negocio_id (huérfanos)")

    cur.execute("""
        SELECT  pc.usuario_id,
                COUNT(*)            AS huerfanos,
                MIN(pc.id_producto) AS primer_id,
                MAX(pc.id_producto) AS ultimo_id
        FROM    productos_catalogo pc
        WHERE   pc.negocio_id IS NULL
        GROUP BY pc.usuario_id
        ORDER BY huerfanos DESC;
    """)
    resumen = cur.fetchall()

    if not resumen:
        print("  [OK] No hay productos huérfanos. ¡Todo está limpio!")

        # Mostrar estado actual de todos modos
        sep("Estado actual por negocio")
        cur.execute("""
            SELECT  n.id_negocio,
                    n.nombre_negocio,
                    COUNT(pc.id_producto) AS productos
            FROM    negocios n
            LEFT JOIN productos_catalogo pc ON pc.negocio_id = n.id_negocio
            GROUP BY n.id_negocio, n.nombre_negocio
            ORDER BY n.id_negocio;
        """)
        for e in cur.fetchall():
            print(f"  negocio {e['id_negocio']} ({e['nombre_negocio']}): "
                  f"{e['productos']} productos")
        conn.close(); return

    total_huerfanos = sum(r['huerfanos'] for r in resumen)
    for r in resumen:
        print(f"  usuario_id={r['usuario_id']}  |  "
              f"{r['huerfanos']} huérfanos  |  "
              f"ids {r['primer_id']} → {r['ultimo_id']}")

    # ── PASO 3: confirmación ──────────────────────────────────────
    sep("PASO 3 — Confirmación")
    print(f"\n  Se encontraron {total_huerfanos} producto(s) sin negocio asignado.")
    print("  Elige a cuál negocio asignarlos (normalmente el PRIMERO / más antiguo):\n")

    for n in negocios:
        print(f"    [{n['id_negocio']}]  {n['nombre_negocio']}  (slug: {n['slug']})")

    try:
        negocio_destino = int(input("\n  → Escribe el id_negocio destino: ").strip())
    except ValueError:
        print("  [ERR] Valor inválido. Abortando sin cambios.")
        conn.close(); return

    if negocio_destino not in [n['id_negocio'] for n in negocios]:
        print(f"  [ERR] {negocio_destino} no es un id_negocio válido. Abortando.")
        conn.close(); return

    # Previsualización
    cur.execute("""
        SELECT id_producto, nombre, categoria, precio
        FROM   productos_catalogo
        WHERE  negocio_id IS NULL
        ORDER  BY id_producto
        LIMIT  8;
    """)
    muestra = cur.fetchall()
    print(f"\n  Primeros productos que se moverán a negocio {negocio_destino}:")
    for p in muestra:
        print(f"    id={p['id_producto']:<6}  {str(p['nombre'])[:38]:<38}  "
              f"${p['precio']}")
    if total_huerfanos > 8:
        print(f"    ... y {total_huerfanos - 8} más")

    confirmar = input(f"\n  ¿Mover {total_huerfanos} productos → negocio {negocio_destino}? "
                      f"(escribe 'si'): ").strip().lower()

    if confirmar not in ('si', 'sí', 'yes'):
        print("  [ERR] Cancelado. Sin cambios.")
        conn.close(); return

    # ── PASO 4: UPDATE ────────────────────────────────────────────
    sep("PASO 4 — Ejecutando UPDATE")

    try:
        cur.execute("""
            UPDATE productos_catalogo
            SET    negocio_id = %s
            WHERE  negocio_id IS NULL;
        """, (negocio_destino,))

        filas = cur.rowcount
        conn.commit()
        print(f"  [OK] {filas} productos actualizados → negocio_id = {negocio_destino}")

    except Exception as e:
        conn.rollback()
        print(f"  [ERR] Error en UPDATE: {e}")
        print("  ROLLBACK aplicado — base de datos sin cambios.")
        conn.close(); return

    # ── PASO 5: verificación final ────────────────────────────────
    sep("PASO 5 — Estado final")

    cur.execute("""
        SELECT  n.id_negocio,
                n.nombre_negocio,
                COUNT(pc.id_producto) AS total
        FROM    negocios n
        LEFT JOIN productos_catalogo pc ON pc.negocio_id = n.id_negocio
        GROUP BY n.id_negocio, n.nombre_negocio
        ORDER BY n.id_negocio;
    """)
    for e in cur.fetchall():
        print(f"  negocio {e['id_negocio']} ({e['nombre_negocio']}): "
              f"{e['total']} productos")

    cur.execute("SELECT COUNT(*) AS c FROM productos_catalogo WHERE negocio_id IS NULL;")
    restantes = cur.fetchone()['c']
    if restantes == 0:
        print("\n  [OK] ¡Sin huérfanos! Inventario limpio en Neon.")
    else:
        print(f"\n  [!]  Quedan {restantes} huérfanos (posiblemente de otro usuario).")

    conn.close()
    sep()
    print("  Recarga el inventario en la app para confirmar.\n")

if __name__ == "__main__":
    main()
