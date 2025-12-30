import os
import re

# Ruta al directorio raíz
directory = "C:/Users/carlo/Desktop/proyecto_sena/TRAYECTORIA_Python_mvc/src/api/"
init_file_path = os.path.join(directory, "__init__.py")  # Ruta al archivo __init__.py

def load_blueprints_from_init(init_file_path):
    """
    Carga los Blueprints y sus prefijos desde el archivo __init__.py.
    """
    blueprints = {}
    try:
        with open(init_file_path, 'r', encoding='utf-8') as init_file:
            for line in init_file:
                # Detectar registros de Blueprints
                match = re.search(r"app\.register_blueprint\((\w+), url_prefix=[\'\"](.+?)[\'\"]", line)
                if match:
                    blueprint_name = match.group(1)
                    url_prefix = match.group(2)
                    blueprints[blueprint_name] = url_prefix
    except FileNotFoundError:
        print(f"⚠️ El archivo {init_file_path} no existe. Verifica tu configuración.")
    return blueprints

def check_logger(lines):
    """
    Verifica si el logger está configurado correctamente.
    """
    logger_found = any("logging.getLogger(__name__)" in line for line in lines)
    return logger_found

def check_blueprint(lines, file_name):
    """
    Verifica si el Blueprint está definido correctamente.
    """
    blueprint_name = f"{file_name}_bp"
    blueprint_found = any(re.search(rf"Blueprint\([\'\"]{file_name}[\'\"]", line) for line in lines)
    return blueprint_name, blueprint_found

def check_decorators(lines, blueprints):
    """
    Verifica si los decoradores de rutas están asociados al Blueprint correcto y tienen rutas válidas.
    """
    issues = []
    for line in lines:
        if ".route(" in line:
            match = re.match(r"@(\w+)\.route\([\'\"](.+?)[\'\"]", line)
            if match:
                blueprint_name = match.group(1)
                route = match.group(2)
                if blueprint_name not in blueprints:
                    issues.append(f"❌ Blueprint '{blueprint_name}' no registrado en __init__.py.")
                elif not route.startswith(blueprints[blueprint_name]):
                    issues.append(f"⚠️ Inconsistencia en el prefijo de la ruta '{route}' para el Blueprint '{blueprint_name}'.")
    return issues

def check_imports(lines):
    """
    Verifica si faltan importaciones necesarias.
    """
    missing_imports = []
    required_imports = ["from flask import Blueprint", "import logging"]
    for required in required_imports:
        if not any(required in line for line in lines):
            missing_imports.append(f"❌ Falta la importación: {required}")
    return missing_imports

def process_file(file_path, blueprints):
    """
    Procesa un archivo en busca de inconsistencias.
    """
    issues = []
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            lines = file.readlines()

        file_name = os.path.splitext(os.path.basename(file_path))[0]

        # Verificar logger
        if not check_logger(lines):
            issues.append(f"❌ Logger no configurado en {file_path}.")

        # Verificar Blueprint
        blueprint_name, blueprint_found = check_blueprint(lines, file_name)
        if not blueprint_found:
            issues.append(f"❌ Blueprint '{blueprint_name}' no definido en {file_path}.")

        # Verificar decoradores de rutas
        decorator_issues = check_decorators(lines, blueprints)
        issues.extend(decorator_issues)

        # Verificar importaciones
        import_issues = check_imports(lines)
        issues.extend(import_issues)

    except Exception as e:
        issues.append(f"❌ Error procesando el archivo {file_path}: {e}")

    return issues

def process_all_files(directory, init_file_path):
    """
    Recorre todos los archivos en busca de inconsistencias.
    """
    blueprints = load_blueprints_from_init(init_file_path)
    all_issues = {}

    print("=== BUSCANDO INCONSISTENCIAS ===")
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(".py") and file != "__init__.py":
                file_path = os.path.join(root, file)
                issues = process_file(file_path, blueprints)
                if issues:
                    all_issues[file_path] = issues

    # Imprimir informe de inconsistencias
    print("\n=== INFORME DE INCONSISTENCIAS ===")
    if all_issues:
        for file_path, issues in all_issues.items():
            print(f"\nArchivo: {file_path}")
            for issue in issues:
                print(f"  - {issue}")
    else:
        print("✅ No se encontraron inconsistencias.")
    print("=== FIN DEL INFORME ===")

# Ejecutar el script
process_all_files(directory, init_file_path)


