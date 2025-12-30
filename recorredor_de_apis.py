import os
import re

# Ruta del directorio raíz (carpeta api)
directory = "C:/Users/carlo/Desktop/proyecto_sena/TRAYECTORIA_Python_mvc/src/api/"
output_file = os.path.join(directory, "__init__.py")  # Archivo __init__.py existente

def extract_blueprints(file_path):
    """Extrae los nombres de Blueprints y rutas de los archivos Python."""
    blueprints = []
    with open(file_path, 'r', encoding='utf-8') as file:
        for line in file:
            # Buscar líneas que definan Blueprints (Blueprint('nombre', __name__))
            bp_match = re.search(r'Blueprint\(\s*[\'"](\w+)[\'"]', line)
            if bp_match:
                blueprint_name = bp_match.group(1)
                blueprints.append(blueprint_name)
    return blueprints

def update_init(directory):
    """Escribe los imports y registros de Blueprints en el archivo __init__.py existente."""
    imports = []
    registrations = []

    # Recorrer todas las subcarpetas y archivos en `api`
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(".py") and file != "__init__.py":
                file_path = os.path.join(root, file)
                relative_import = os.path.relpath(file_path, directory).replace("\\", ".").replace(".py", "")

                # Extraer Blueprints definidos en el archivo actual
                blueprints = extract_blueprints(file_path)
                for bp in blueprints:
                    # Crear los imports y registros necesarios
                    imports.append(f"from .{relative_import} import {bp}")
                    registrations.append(f"    app.register_blueprint({bp}, url_prefix='/{bp}')")

    # Verificar si se encontraron Blueprints
    if not imports:
        print("⚠️ No se encontraron Blueprints en los archivos. Revisa tu código.")
        return

    # Leer contenido existente del archivo __init__.py
    with open(output_file, 'r', encoding='utf-8') as init_file:
        existing_content = init_file.read()

    # Verificar si ya hay imports o registros existentes
    if "# Importación de Blueprints" in existing_content or "# Registro de Blueprints" in existing_content:
        print("⚠️ Ya existen imports y registros de Blueprints en el archivo __init__.py. Se recomienda revisarlo antes de continuar.")
        return

    # Escribir contenido actualizado en el archivo __init__.py
    with open(output_file, 'a', encoding='utf-8') as init_file:
        init_file.write("\n# Importación de Blueprints\n")
        init_file.write("\n".join(imports) + "\n\n")

        init_file.write("# Registro de Blueprints\n")
        init_file.write("def register_blueprints():\n")
        init_file.write("\n".join(registrations) + "\n")

    print(f"✅ Archivo __init__.py actualizado correctamente en: {output_file}")
    print(f"✏️ En tu archivo app.py, agrega lo siguiente:\n")
    print("from src.api import app, register_blueprints\n")
    print("register_blueprints()\n")
    print("if __name__ == '__main__':")
    print("    app.run(debug=True')")

# Ejecutar el script
update_init(directory)
