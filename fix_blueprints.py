import os
import re

# Ruta al directorio raíz (carpeta api)
directory = "C:/Users/carlo/Desktop/proyecto_sena/TRAYECTORIA_Python_mvc/src/api/"
init_file_path = os.path.join(directory, "__init__.py")  # Archivo __init__.py

def load_init_blueprints(init_file_path):
    """
    Carga los nombres de Blueprints y sus prefijos del archivo __init__.py.
    """
    blueprints = {}
    try:
        with open(init_file_path, 'r', encoding='utf-8') as init_file:
            for line in init_file:
                # Detectar importaciones de Blueprints
                import_match = re.search(r"from \.(.+?) import (\w+_bp)", line)
                if import_match:
                    file_name = import_match.group(1)
                    blueprint_name = import_match.group(2)
                    blueprints[blueprint_name] = None  # Inicialmente sin prefijo
                
                # Detectar registros de Blueprints
                register_match = re.search(r"app\.register_blueprint\((\w+_bp), url_prefix=[\'\"](.+?)[\'\"]", line)
                if register_match:
                    blueprint_name = register_match.group(1)
                    url_prefix = register_match.group(2)
                    if blueprint_name in blueprints:
                        blueprints[blueprint_name] = url_prefix

    except FileNotFoundError:
        print(f"⚠️ El archivo {init_file_path} no existe. Verifica tu configuración.")
    
    return blueprints

def fix_blueprint_and_routes(file_path, blueprints):
    """
    Corrige nombres de Blueprints mal configurados y valida decoradores de rutas en un archivo.
    """
    updated_lines = []
    modified = False
    errors = []

    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            for line in file:
                # Detectar el Blueprint mal configurado
                bp_match = re.search(r"Blueprint\(\s*[\'\"](.+?)[\'\"]", line)
                if bp_match:
                    original_name = bp_match.group(1)
                    file_base_name = os.path.splitext(os.path.basename(file_path))[0]
                    expected_name = f"{file_base_name}_bp"

                    # Comparar con el Blueprint cargado desde __init__.py
                    if expected_name not in blueprints:
                        errors.append(f"❌ Blueprint '{expected_name}' no encontrado en __init__.py")
                    elif original_name != expected_name:
                        print(f"⚠️ Corrigiendo Blueprint '{original_name}' a '{expected_name}' en {file_path}")
                        line = re.sub(r"Blueprint\(\s*[\'\"].+?[\'\"]", f"Blueprint('{expected_name}'", line)
                        modified = True
                
                # Validar decoradores de rutas
                for blueprint_name, url_prefix in blueprints.items():
                    if blueprint_name in line and url_prefix:
                        # Validar si la ruta cumple con el prefijo registrado
                        route_match = re.search(rf"{blueprint_name}\.route\([\'\"](.+?)[\'\"]", line)
                        if route_match:
                            route = route_match.group(1)
                            if not route.startswith(url_prefix):
                                print(f"⚠️ Corrigiendo ruta '{route}' para que use el prefijo '{url_prefix}' en {file_path}")
                                corrected_route = f"{url_prefix}{route}"
                                line = line.replace(route, corrected_route)
                                modified = True
                
                updated_lines.append(line)

        # Guardar cambios si se realizaron modificaciones
        if modified:
            with open(file_path, 'w', encoding='utf-8') as file:
                file.writelines(updated_lines)
            print(f"✅ Archivo corregido: {file_path}")
        else:
            print(f"🔍 No se encontraron errores en: {file_path}")

    except Exception as e:
        errors.append(f"❌ Error procesando {file_path}: {e}")

    return errors

def process_all_files(directory, blueprints):
    """
    Recorre todos los archivos en el directorio y corrige errores en Blueprints y decoradores de rutas.
    """
    errors = []
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(".py") and file != "__init__.py":
                file_path = os.path.join(root, file)
                file_errors = fix_blueprint_and_routes(file_path, blueprints)
                errors.extend(file_errors)

    # Mostrar errores encontrados
    if errors:
        print("❌ Errores encontrados durante el procesamiento:")
        for error in errors:
            print(error)
    else:
        print("✅ Todos los archivos fueron procesados correctamente.")

# Cargar los Blueprints desde __init__.py
blueprints = load_init_blueprints(init_file_path)

# Procesar todos los archivos
process_all_files(directory, blueprints)