import os

def listar_estructura(carpeta, nivel=0):
    """
    Lista la estructura de archivos y carpetas de la ruta especificada.
    """
    for elemento in os.listdir(carpeta):
        ruta = os.path.join(carpeta, elemento)
        print("  " * nivel + f"|-- {elemento}")
        if os.path.isdir(ruta):
            listar_estructura(ruta, nivel + 1)

if __name__ == "__main__":
    # Define la ruta base para la carpeta 'api'
    carpeta_api = os.path.join(os.path.dirname(__file__), 'api')

    if os.path.exists(carpeta_api):
        print("Estructura de la carpeta 'api':")
        listar_estructura(carpeta_api)
    else:
        print("La carpeta 'api' no existe.")
