import logging
from src.models.notification import Notification
from src.models import db
from src.models.usuarios import Usuario  # Importar Usuario para validar que existe

# Configurar el logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

def send_contract_request_notification(user_id, message):
    try:
        # Verificar los valores antes de proceder
        logger.debug(f"Verificando valores - user_id: {user_id}, message: {message}")
        
        # Verificar si el usuario existe
        usuario = Usuario.query.get(user_id)
        
        # Verificar si el usuario con el id dado existe
        if not usuario:
            logger.error(f"Usuario con id {user_id} no encontrado.")
            raise ValueError(f"Usuario con id {user_id} no encontrado.")
        
        logger.info(f"Usuario encontrado: {usuario.nombre}")  # Confirmar que encontramos al usuario
        
        # Verificar si ya existe una notificación similar
        existing_notification = Notification.query.filter_by(user_id=user_id, message=message).first()
        
        if existing_notification:
            logger.warning(f"Ya existe una notificación para el usuario {user_id} con el mismo mensaje.")
            return  # Evita la duplicación
        
        # Crear la notificación
        notification = Notification(user_id=user_id, message=message)
        logger.debug(f"Creando notificación para el usuario {user_id} con mensaje: {message}")
        
        # Agregar la notificación a la sesión de la base de datos
        db.session.add(notification)
        db.session.flush()  # Enviar a la base de datos sin confirmar aún
        
        # Confirmar la transacción
        db.session.commit()
        
        # Recuperar la notificación de la base de datos para verificar que se guardó correctamente
        notification_in_db = Notification.query.filter_by(user_id=user_id).order_by(Notification.timestamp.desc()).first()
        
        logger.info(f"Notificación guardada: {notification_in_db}")
        logger.info(f"Notificación enviada a usuario {user_id}: {message}")
    
    except Exception as e:
        # Registrar el error completo con traceback
        logger.error(f"Error al enviar notificación: {e}", exc_info=True)
        db.session.rollback()  # Deshacer cualquier cambio si hubo un error