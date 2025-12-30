import os
import re

def buscar_blueprint(blueprint_name, base_dir="src"):
    """
    Genera un informe sobre el Blueprint especificado.
    
    :param blueprint_name: Nombre del Blueprint a buscar.
    :param base_dir: Carpeta base del proyecto donde buscar archivos.
    :return: Informe detallado sobre el Blueprint.
    """
    informe = {}
    blueprint_found = False

    for root, dirs, files in os.walk(base_dir):
        for file in files:
            if file.endswith(".py"):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'r') as f:
                        contenido = f.read()
                        # Buscar el Blueprint dentro del archivo
                        if blueprint_name in contenido:
                            blueprint_found = True
                            # Guardar el nombre del archivo
                            informe['Archivo'] = file
                            
                            # Buscar la importación del Blueprint
                            import_match = re.search(rf"(from .+ import {blueprint_name})", contenido)
                            if import_match:
                                informe['Importación'] = import_match.group(1)
                            
                            # Buscar el registro del Blueprint
                            registro_match = re.search(rf"(app\.register_blueprint\({blueprint_name},.+\))", contenido)
                            if registro_match:
                                informe['Registro'] = registro_match.group(1)
                            
                            # Buscar decoradores de rutas
                            decorador_match = re.findall(rf"@{blueprint_name}\.route\(.+\)", contenido)
                            if decorador_match:
                                informe['Decoradores'] = decorador_match
                            
                            # Buscar asignación del Blueprint
                            asignacion_match = re.search(rf"{blueprint_name} = Blueprint\(.+\)", contenido)
                            if asignacion_match:
                                informe['Asignación'] = asignacion_match.group(0)
                            
                            # Buscar funciones asociadas al Blueprint
                            funciones_match = re.findall(r"def .+\(", contenido)
                            if funciones_match:
                                informe['Funciones'] = funciones_match
                except Exception as e:
                    print(f"Error leyendo el archivo {file_path}: {e}")
    
    if blueprint_found:
        return informe
    else:
        return f"No se encontró el Blueprint '{blueprint_name}' en la carpeta '{base_dir}'."

# Ejemplo de uso
blueprint_name = input("Ingresa el nombre del Blueprint: ")
informe = buscar_blueprint(blueprint_name)
print("\nInforme sobre el Blueprint:")
print(informe)
