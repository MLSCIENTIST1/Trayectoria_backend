import os
import re
import importlib

# Ruta del directorio raíz (carpeta api)
directory = "C:/Users/carlo/Desktop/proyecto_sena/TRAYECTORIA_Python_mvc/src/api/"

# Lista de módulos estándar de Python para validar imports
STANDARD_MODULES = set([
    "os", "sys", "re", "json", "logging", "datetime", "math", "random",
    "collections", "itertools", "functools", "hashlib", "uuid", "time",
    "typing", "pathlib", "shutil"
])

def find_missing_imports(file_path):
    """
    Analiza el archivo para encontrar referencias y verifica los imports necesarios.
    """
    existing_imports = set()
    used_symbols = set()
    missing_imports = set()

    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            lines = file.readlines()

        for line in lines:
            # Capturar las líneas de importación existentes
            import_match = re.match(r"^import (\w+)|^from (\w+)", line)
            if import_match:
                module_name = import_match.group(1) or import_match.group(2)
                existing_imports.add(module_name)

            # Capturar símbolos usados en el archivo (clases, funciones, etc.)
            symbol_match = re.findall(r"(\w+)\.", line)
            if symbol_match:
                used_symbols.update(symbol_match)

        # Validar qué símbolos no tienen un import asociado
        for symbol in used_symbols:
            if symbol not in existing_imports and symbol not in STANDARD_MODULES:
                try:
                    importlib.import_module(symbol)  # Verificar si el módulo existe
                    missing_imports.add(symbol)
                except ImportError:
                    continue

    except Exception as e:
        print(f"❌ Error analizando {file_path}: {e}")

    return missing_imports

def add_missing_imports(file_path, missing_imports):
    """
    Agrega los imports faltantes al inicio del archivo.
    """
    if not missing_imports:
        return False  # Nada que agregar

    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.readlines()

        # Insertar los imports al inicio del archivo
        with open(file_path, 'w', encoding='utf-8') as file:
            for module in missing_imports:
                file.write(f"import {module}\n")
            file.writelines(content)

        print(f"✅ Imports agregados a: {file_path}")
        return True

    except Exception as e:
        print(f"❌ Error al agregar imports en {file_path}: {e}")
        return False

def process_all_files(directory):
    """
    Recorre todos los archivos en el directorio y valida/agrega imports.
    """
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(".py") and file != "__init__.py":
                file_path = os.path.join(root, file)
                missing_imports = find_missing_imports(file_path)
                if missing_imports:
                    print(f"🔍 Imports faltantes detectados en {file_path}: {', '.join(missing_imports)}")
                    add_missing_imports(file_path, missing_imports)
                else:
                    print(f"✅ Todos los imports ya están presentes en: {file_path}")

# Ejecutar el script
process_all_files(directory)
