"""
diagnostico_tiendas.py
------------------------------------------------------------------------------
Diagnostica el estado de negocios y productos en Neon.
Detecta:
  1. Negocios con activo=False o tiene_pagina=False (tiendas que dan 404)
  2. Distribucion de productos por negocio (detecta el "robo" de force=True)
  3. Ofrece corregir: mover productos del negocio equivocado al correcto

Uso:
  venv\Scripts\python diagnostico_tiendas.py
------------------------------------------------------------------------------
"""

import psycopg2
from psycopg2.extras import RealDictCursor

DATABASE_URL = (
    "postgresql://neondb_owner:npg_XowUyaAE7IB4"
    "@ep-polished-rice-a4shbmdi-pooler.us-east-1.aws.neon.tech"
    "/neondb?sslmode=require"
)

def sep(titulo=""):
    linea = "-" * 66
    if titulo:
        print(f"\n{linea}\n  {titulo}\n{linea}")
    else:
        print(linea)

def main():
    print("\n============================================================")
    print("  DIAGNOSTICO DE TIENDAS Y PRODUCTOS - Neon")
    print("============================================================")

    conn = psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)
    cur  = conn.cursor()

    # ── 1. Estado de todos los negocios ──────────────────────────────
    sep("PASO 1 - Estado de negocios (activo / tiene_pagina)")

    cur.execute("""
        SELECT  n.id_negocio,
                n.nombre_negocio,
                n.slug,
                n.activo,
                n.tiene_pagina,
                u.correo        AS usuario,
                COUNT(pc.id_producto) AS total_productos
        FROM    negocios n
        LEFT JOIN usuarios u  ON u.id_usuario = n.usuario_id
        LEFT JOIN productos_catalogo pc ON pc.negocio_id = n.id_negocio
        GROUP BY n.id_negocio, n.nombre_negocio, n.slug,
                 n.activo, n.tiene_pagina, u.correo
        ORDER BY n.id_negocio;
    """)
    negocios = cur.fetchall()

    if not negocios:
        print("  [!] No se encontraron negocios.")
        conn.close(); return

    problemas_flags = []
    for n in negocios:
        activo    = n['activo']
        pagina    = n['tiene_pagina']
        flag_warn = ""
        if not activo or not pagina:
            flag_warn = " <-- [PROBLEMA: tienda da 404]"
            problemas_flags.append(n)
        print(f"  id={n['id_negocio']:<4} | slug={str(n['slug']):<22} | "
              f"activo={str(activo):<5} | tiene_pagina={str(pagina):<5} | "
              f"{n['total_productos']:>4} prods | {n['usuario']}{flag_warn}")

    # ── 2. Productos huerfanos (negocio_id IS NULL) ──────────────────
    sep("PASO 2 - Productos sin negocio_id (huerfanos)")

    cur.execute("""
        SELECT COUNT(*) AS c FROM productos_catalogo WHERE negocio_id IS NULL;
    """)
    huerfanos = cur.fetchone()['c']
    if huerfanos == 0:
        print("  [OK] No hay productos huerfanos.")
    else:
        print(f"  [!]  {huerfanos} productos sin negocio_id encontrados.")

    # ── 3. Distribucion de productos por negocio / usuario ───────────
    sep("PASO 3 - Productos por negocio por usuario")

    cur.execute("""
        SELECT  u.correo,
                n.id_negocio,
                n.nombre_negocio,
                n.slug,
                COUNT(pc.id_producto) AS total
        FROM    usuarios u
        JOIN    negocios n  ON n.usuario_id = u.id_usuario
        LEFT JOIN productos_catalogo pc ON pc.negocio_id = n.id_negocio
        GROUP BY u.correo, n.id_negocio, n.nombre_negocio, n.slug
        ORDER BY u.correo, n.id_negocio;
    """)
    dist = cur.fetchall()

    usuario_actual = None
    for row in dist:
        if row['correo'] != usuario_actual:
            usuario_actual = row['correo']
            print(f"\n  Usuario: {usuario_actual}")
        print(f"    negocio {row['id_negocio']} ({row['slug']:<22}): {row['total']:>4} productos")

    # ── 4. Deteccion de posible robo por force=True ──────────────────
    sep("PASO 4 - Verificar slugs 'rodar' y 'caballeroshouse'")

    for slug_buscar in ['rodar', 'caballeroshouse']:
        cur.execute("""
            SELECT n.id_negocio, n.slug, n.activo, n.tiene_pagina,
                   COUNT(pc.id_producto) AS total
            FROM   negocios n
            LEFT JOIN productos_catalogo pc ON pc.negocio_id = n.id_negocio
            WHERE  n.slug = %s
            GROUP BY n.id_negocio, n.slug, n.activo, n.tiene_pagina;
        """, (slug_buscar,))
        row = cur.fetchone()
        if not row:
            print(f"  [!] slug '{slug_buscar}' NO encontrado en negocios")
        else:
            estado = []
            if not row['activo']:     estado.append("activo=False")
            if not row['tiene_pagina']: estado.append("tiene_pagina=False")
            if not estado:            estado.append("flags OK")
            print(f"  slug='{slug_buscar}' | id={row['id_negocio']} | "
                  f"prods={row['total']} | {', '.join(estado)}")

    # ── 5. Opcion de reparar flags ───────────────────────────────────
    if problemas_flags:
        sep("PASO 5 - Reparar flags de negocios con 404")
        print(f"\n  Hay {len(problemas_flags)} negocio(s) con activo o tiene_pagina en False:\n")
        for n in problemas_flags:
            print(f"    id={n['id_negocio']} | slug={n['slug']} | "
                  f"activo={n['activo']} | tiene_pagina={n['tiene_pagina']}")

        resp = input("\n  Activar todos y poner tiene_pagina=True? (escribe 'si'): ").strip().lower()
        if resp in ('si', 'yes'):
            ids = [n['id_negocio'] for n in problemas_flags]
            cur.execute("""
                UPDATE negocios
                SET    activo = TRUE, tiene_pagina = TRUE
                WHERE  id_negocio = ANY(%s);
            """, (ids,))
            conn.commit()
            print(f"  [OK] {cur.rowcount} negocio(s) activados.")
        else:
            print("  Cancelado, sin cambios en flags.")
    else:
        sep("PASO 5 - Reparar flags")
        print("  [OK] Todos los negocios tienen activo=True y tiene_pagina=True.")

    # ── 6. Opcion de reasignar productos al negocio correcto ─────────
    sep("PASO 6 - Reasignar productos mal migrados (fix force=True)")
    print("\n  Si los productos de Rodar aparecen en otro negocio, aqui los devuelves.")
    print("  Deja en blanco y presiona Enter para saltar.\n")

    origen_str  = input("  id_negocio ORIGEN (donde estan ahora, el incorrecto): ").strip()
    destino_str = input("  id_negocio DESTINO (donde deben ir, el correcto):     ").strip()

    if origen_str and destino_str:
        try:
            origen  = int(origen_str)
            destino = int(destino_str)
        except ValueError:
            print("  [ERR] IDs invalidos. Cancelado.")
            conn.close(); return

        cur.execute("""
            SELECT COUNT(*) AS c
            FROM   productos_catalogo
            WHERE  negocio_id = %s;
        """, (origen,))
        cantidad = cur.fetchone()['c']
        print(f"\n  Se moveran {cantidad} productos de negocio {origen} -> negocio {destino}.")

        # Preview
        cur.execute("""
            SELECT id_producto, nombre, precio
            FROM   productos_catalogo
            WHERE  negocio_id = %s
            ORDER BY id_producto
            LIMIT 6;
        """, (origen,))
        for p in cur.fetchall():
            print(f"    id={p['id_producto']:<6} {str(p['nombre'])[:40]:<40} ${p['precio']}")
        if cantidad > 6:
            print(f"    ... y {cantidad - 6} mas")

        conf = input(f"\n  Confirmar mover {cantidad} productos? (escribe 'si'): ").strip().lower()
        if conf in ('si', 'yes'):
            try:
                cur.execute("""
                    UPDATE productos_catalogo
                    SET    negocio_id = %s
                    WHERE  negocio_id = %s;
                """, (destino, origen))
                conn.commit()
                print(f"  [OK] {cur.rowcount} productos movidos a negocio {destino}.")
            except Exception as e:
                conn.rollback()
                print(f"  [ERR] {e} - ROLLBACK aplicado.")
        else:
            print("  Cancelado, sin cambios.")
    else:
        print("  Saltando reasignacion.")

    conn.close()
    sep()
    print("  Diagnostico completo. Recarga las tiendas para verificar.\n")

if __name__ == "__main__":
    main()
