# -*- coding: utf-8 -*-
from run import create_app
from src.models.database import db
from src.models.usuarios import Usuario

def crear_usuario_prueba():
    app = create_app()
    with app.app_context():
        print("🧪 [TEST]: Intentando insertar usuario de prueba con campos corregidos...")
        try:
            # Buscamos por 'correo' que es el nombre en tu modelo
            user_exists = Usuario.query.filter_by(correo="test@example.com").first()
            if user_exists:
                print("⚠️ [INFO]: El usuario de prueba ya existe en Neon.")
                return

            # Creamos el objeto usando los nombres de tu __init__
            nuevo_usuario = Usuario(
                nombre="Usuario",
                apellidos="De Prueba",
                correo="test@example.com",
                profesion="Tester",
                cedula=123456789,
                celular=3001234567,
                ciudad=1 # ciudad_id espera un entero según tu __init__
            )
            
            # Seteamos la contraseña usando tu método set_password
            nuevo_usuario.set_password("admin123")

            db.session.add(nuevo_usuario)
            db.session.commit()
            print("✅ [EXITO]: ¡Usuario insertado correctamente en Neon!")
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ [ERROR]: {e}")

if __name__ == "__main__":
    crear_usuario_prueba()