import os
import shutil

# Ruta al directorio raíz (carpeta api)
directory = "C:/Users/carlo/Desktop/proyecto_sena/TRAYECTORIA_Python_mvc/src/api/"
backup_extension = ".bak"  # Extensión de los archivos de respaldo

def restore_file(file_path):
    """
    Restaura un archivo desde su respaldo con la extensión .bak.
    """
    backup_file_path = f"{file_path}{backup_extension}"
    try:
        if os.path.exists(backup_file_path):
            # Restaurar el archivo original desde su respaldo
            shutil.copy(backup_file_path, file_path)
            print(f"✅ Archivo restaurado: {file_path}")
        else:
            print(f"⚠️ Respaldo no encontrado para: {file_path}")
    except Exception as e:
        print(f"❌ Error al restaurar {file_path}: {e}")

def process_all_files(directory):
    """
    Recorre todos los archivos en el directorio y restaura los respaldos.
    """
    print("=== INICIO DE LA RESTAURACIÓN ===")
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(".py"):  # Procesar solo archivos .py
                file_path = os.path.join(root, file)
                restore_file(file_path)
    print("=== FIN DE LA RESTAURACIÓN ===")

# Ejecutar el script
process_all_files(directory)
