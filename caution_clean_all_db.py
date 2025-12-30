##se ejecuta con python reset_ids.py


from src.models.database import db
from src.models.servicio import Servicio
from src.models.usuarios import Usuario
from src.models.colombia_data.colombia_data import Colombia
from src.models.colombia_data.ratings import ServiceRatings, ServiceOverallScores, ServiceQualifiers
from src.models.notification import Notification
from src.models.message import Message
from src.models.etapa import Etapa
from src.models.foto import Foto
from src.models.audio import Audio
from src.models.video import Video

def limpiar_base_de_datos():
    try:
        # Elimina los datos de las tablas
        db.session.query(ServiceRatings).delete()
        db.session.query(ServiceOverallScores).delete()
        db.session.query(ServiceQualifiers).delete()
        db.session.query(Notification).delete()
        db.session.query(Message).delete()
        db.session.query(Foto).delete()
        db.session.query(Audio).delete()
        db.session.query(Video).delete()
        db.session.query(Etapa).delete()
        db.session.query(Colombia).delete()
        db.session.query(Servicio).delete()
        db.session.query(Usuario).delete()

        # Reinicia los IDs autoincrementales (opcional)
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
        print("Base de datos limpiada correctamente y tablas reiniciadas.")
    except Exception as e:
        db.session.rollback()
        print(f"Error al limpiar la base de datos: {e}")

# Llama a la función para limpiar la base de datos
limpiar_base_de_datos()