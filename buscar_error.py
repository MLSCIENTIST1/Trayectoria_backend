import os
import re

def buscar_con_ruta_absoluta():
    # Patrones que indican headers manuales o IDs fijos
    patrones = {
        "HEADER_DETECTADO": r"['\"]usuario_id['\"]",
        "ASIGNACION_FIJA": r"usuario_id\s*[:=]\s*['\"]?1['\"]?\b",
        "HEADERS_OBJ": r"headers\s*:\s*\{"
    }
    
    # Exclusiones para no buscar en basura
    ignore_dirs = {'venv', '.venv', 'node_modules', '.git', '__pycache__', 'migrate'}
    extensiones_validas = ('.js', '.html', '.ts')

    print("="*80)
    print("🔍 ESCANEANDO ARCHIVOS DE BIZFLOW STUDIO (RUTAS COMPLETAS)")
    print("="*80)

    hallazgos = 0

    for raiz, carpetas, archivos in os.walk('.'):
        # Filtrar carpetas
        carpetas[:] = [c for c in carpetas if c not in ignore_dirs]

        for nombre_archivo in archivos:
            if nombre_archivo.endswith(extensiones_validas):
                # Construir la RUTA ABSOLUTA
                ruta_completa = os.path.abspath(os.path.join(raiz, nombre_archivo))
                
                try:
                    with open(ruta_completa, 'r', encoding='utf-8') as f:
                        for num_linea, contenido in enumerate(f, 1):
                            linea = contenido.strip()
                            
                            for tipo, regex in patrones.items():
                                if re.search(regex, linea):
                                    hallazgos += 1
                                    print(f"\n🚩 [{tipo}]")
                                    print(f"📂 RUTA: {ruta_completa}")
                                    print(f"🔢 LINEA: {num_linea}")
                                    print(f"💻 CODIGO: {linea}")
                                    print("-" * 40)
                except Exception:
                    continue

    if hallazgos == 0:
        print("\n✅ No se encontraron coincidencias sospechosas.")
    else:
        print(f"\n🚀 Escaneo finalizado. Se encontraron {hallazgos} puntos de interés.")

if __name__ == "__main__":
    buscar_con_ruta_absoluta()