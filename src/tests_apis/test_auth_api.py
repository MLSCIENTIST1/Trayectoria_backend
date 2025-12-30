from flask import Flask, request, jsonify
from unittest.mock import patch
import sys
import os

# Agregar el directorio raíz del proyecto al PATH
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

# Importamos la función que queremos probar
# Aquí mockearemos la parte de la base de datos en login_api()
from src.api.auth.auth_api import login_api

# Configuración básica para simular Flask
app = Flask(__name__)

# Mockeamos la sesión de la base de datos en login_api()
@patch("src.api.auth_api.db_session")  # Cambia "db_session" al nombre real de la dependencia en auth_api.py
def test_valid_login(mock_db_session):
    # Configuramos el mock de la base de datos
    mock_db_session.query.return_value.filter_by.return_value.first.return_value = {
        "correo": "test@example.com",
        "password": "contraseña123",
        "activo": True,
    }

    # Simulamos una solicitud válida
    with app.test_request_context('/api/login', method='POST', json={"correo": "test@example.com", "password": "contraseña123"}):
        print("Probando solicitud válida...")
        response = login_api()
        print(f"Respuesta: {response.get_json()}")


@patch("src.api.auth_api.db_session")  # Mockear DB para otras solicitudes
def test_invalid_login(mock_db_session):
    # Configuramos el mock para una consulta vacía (usuario no encontrado)
    mock_db_session.query.return_value.filter_by.return_value.first.return_value = None

    # Simulamos una solicitud inválida (credenciales incorrectas)
    with app.test_request_context('/api/login', method='POST', json={"correo": "wrong@example.com", "password": "wrongpassword"}):
        print("\nProbando credenciales incorrectas...")
        response = login_api()
        print(f"Respuesta: {response.get_json()}")

# Ejecutar las pruebas
if __name__ == "__main__":
    test_valid_login()
    test_invalid_login()