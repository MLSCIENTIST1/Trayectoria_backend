import os
import re

# Ruta del directorio raíz (carpeta api)
directory = "C:/Users/carlo/Desktop/proyecto_sena/TRAYECTORIA_Python_mvc/src/api/"
output_file = os.path.join(directory, "__init__.py")  # Archivo __init__.py existente


def extract_blueprints_and_routes(file_path):
    """Extrae los nombres de Blueprints y rutas de los archivos Python."""
    blueprints = []
    routes = []
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            for line in file:
                # Detectar Blueprints
                bp_match = re.search(r"Blueprint\(\s*[\'\"](\w+)[\'\"]", line)
                if bp_match:
                    blueprint_name = bp_match.group(1)
                    blueprints.append(blueprint_name)

                # Detectar rutas decoradas
                route_match = re.search(r"@.*\.route\([\'\"]([^\'\"]+)", line)
                if route_match:
                    route = route_match.group(1)
                    routes.append(route)
    except Exception as e:
        print(f"⚠️ Error leyendo el archivo {file_path}: {e}")
    return blueprints, routes


def validate_and_correct_file(file_path, bp_name):
    """Valida y corrige nombres y decoradores dentro de un archivo."""
    updated_lines = []
    modified = False

    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            for line in file:
                # Validar y corregir el nombre del Blueprint
                if f"Blueprint('{bp_name}'" not in line and "Blueprint(" in line:
                    print(f"⚠️ Corrigiendo nombre del Blueprint en {file_path}")
                    line = re.sub(r"Blueprint\(\s*[\'\"].+?[\'\"]", f"Blueprint('{bp_name}'", line)
                    modified = True
                updated_lines.append(line)

        if modified:
            with open(file_path, 'w', encoding='utf-8') as file:
                file.writelines(updated_lines)
            print(f"✅ Archivo corregido: {file_path}")

    except Exception as e:
        print(f"⚠️ Error validando y corrigiendo {file_path}: {e}")


def update_init(directory):
    """Recorre archivos, valida Blueprints y genera el archivo __init__.py."""
    imports = []
    registrations = []

    # Limpiar el archivo __init__.py antes de comenzar
    with open(output_file, 'w', encoding='utf-8') as init_file:
        init_file.write("# Archivo generado automáticamente para la gestión de Blueprints\n")
        init_file.write("from flask import Flask\n")
        init_file.write("app = Flask(__name__)\n\n")

    # Recorrer todas las subcarpetas y archivos en `api`
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(".py") and file != "__init__.py":
                file_path = os.path.join(root, file)
                relative_import = os.path.relpath(file_path, directory).replace("\\", ".").replace(".py", "")

                # Extraer Blueprints y rutas del archivo actual
                blueprints, routes = extract_blueprints_and_routes(file_path)

                for bp in blueprints:
                    # Validar y corregir nombres y rutas dentro del archivo
                    validate_and_correct_file(file_path, bp)

                    # Crear importaciones y registros
                    imports.append(f"from .{relative_import} import {bp}")
                    registrations.append(f"    app.register_blueprint({bp}, url_prefix='/{bp}')")

                if not blueprints:
                    print(f"⚠️ No se detectaron Blueprints en el archivo '{file_path}'. Verifica si es correcto.")
                if routes:
                    print(f"   🚏 Rutas detectadas: {', '.join(routes)}")

    # Verificar si se encontraron Blueprints
    if not imports:
        print("⚠️ No se encontraron Blueprints en los archivos. Revisa tu código.")
        return

    # Escribir importaciones y registros en el archivo __init__.py
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
