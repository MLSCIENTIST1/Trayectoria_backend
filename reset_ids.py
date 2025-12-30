from src.models.database import db
#se ejecuta con python reset_ids.py

def resetear_ids_tablas():
    try:
        print("Iniciando el reseteo de IDs en todas las tablas...")
        
        # Ejecutar comandos TRUNCATE para cada tabla
        db.session.execute("TRUNCATE TABLE aditional_services RESTART IDENTITY CASCADE;")
        db.session.execute("TRUNCATE TABLE alembic_version RESTART IDENTITY CASCADE;")
        db.session.execute("TRUNCATE TABLE audios RESTART IDENTITY CASCADE;")
        db.session.execute("TRUNCATE TABLE calificacion RESTART IDENTITY CASCADE;")
        db.session.execute("TRUNCATE TABLE colombia RESTART IDENTITY CASCADE;")
        db.session.execute("TRUNCATE TABLE etapas RESTART IDENTITY CASCADE;")
        db.session.execute("TRUNCATE TABLE fotos RESTART IDENTITY CASCADE;")
        db.session.execute("TRUNCATE TABLE message RESTART IDENTITY CASCADE;")
        db.session.execute("TRUNCATE TABLE notification RESTART IDENTITY CASCADE;")
        db.session.execute("TRUNCATE TABLE servicio RESTART IDENTITY CASCADE;")
        db.session.execute("TRUNCATE TABLE usuario RESTART IDENTITY CASCADE;")
        db.session.execute("TRUNCATE TABLE usuario_servicio RESTART IDENTITY CASCADE;")
        db.session.execute("TRUNCATE TABLE videos RESTART IDENTITY CASCADE;")

        db.session.commit()
        print("IDs de todas las tablas reiniciados exitosamente.")
    except Exception as e:
        db.session.rollback()
        print(f"Error al resetear IDs: {e}")

if __name__ == "__main__":
    resetear_ids_tablas()