import os

def agregar_imports(carpeta_api, imports):
    """
    Agrega los imports especificados a todos los archivos Python en la carpeta indicada.
    
    :param carpeta_api: Ruta de la carpeta que contiene las APIs.
    :param imports: Lista de imports que se deben agregar.
    """
    for root, dirs, files in os.walk(carpeta_api):
        for file in files:
            if file.endswith(".py"):
                archivo_path = os.path.join(root, file)
                try:
                    with open(archivo_path, 'r') as f:
                        contenido = f.readlines()

                    # Verificar si los imports ya existen
                    nuevos_imports = []
                    for import_line in imports:
                        if any(import_line in linea for linea in contenido):
                            print(f"Import '{import_line}' ya existe en {file}.")
                        else:
                            nuevos_imports.append(import_line)

                    # Agregar nuevos imports al inicio del archivo
                    if nuevos_imports:
                        with open(archivo_path, 'w') as f:
                            f.write("\n".join(nuevos_imports) + "\n")  # Agregar nuevos imports
                            f.write("".join(contenido))  # Mantener el contenido existente
                        print(f"Se agregaron nuevos imports a {file}: {nuevos_imports}")

                except Exception as e:
                    print(f"Error al procesar {archivo_path}: {e}")

# Especifica la ruta de la carpeta 'api' y los imports a agregar
carpeta_api = 'src/api'
imports_a_agregar = [
    'from src.models.database import db',
    'from src.models.usuarios import Usuario'
]

# Ejecutar la función
agregar_imports(carpeta_api, imports_a_agregar)
