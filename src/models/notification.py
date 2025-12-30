import logging
from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from src.models.database import db

# Configurar logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

file_handler = logging.FileHandler('notifications.log')
file_handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

# Modelo Notification
class Notification(db.Model):
    __tablename__ = "notification"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('usuario.id_usuario'), nullable=False)  # Receptor
    sender_id = Column(Integer, ForeignKey('usuario.id_usuario'), nullable=False)  # Remitente
    request_id = Column(Integer, nullable=True)  # ID de solicitud relacionado
    is_accepted = Column(Boolean, default=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    is_read = Column(Boolean, default=False)
    type = Column(String, default='default_type')
    extra_data = Column(JSON, nullable=True)
    response = Column(String(255), nullable=True)
    request_message_details = Column(String(255), nullable=True)
    questions = Column(String(255), nullable=True)
    message = Column(String(255), nullable=True)

    # Relaciones con Usuario
    sender = relationship('Usuario', foreign_keys=[sender_id], back_populates='sent_notifications')  # Remitente
    receiver = relationship('Usuario', foreign_keys=[user_id], back_populates='received_notifications')  # Receptor

    # Relación con Message
    messages = relationship('Message', back_populates='notification', lazy='select')

    @classmethod
    def create_notification(cls, user_id, sender_id, request_id, message, params=None, extra_data=None):
        try:
            notification_type = params.get('type', 'default_type') if params else 'default_type'
            notification = cls(
                user_id=user_id,
                sender_id=sender_id,
                request_id=request_id,
                message=message,
                type=notification_type,
                extra_data=extra_data
            )
            db.session.add(notification)
            db.session.commit()
            logger.info(f"Notificación creada: {notification}")
            return notification
        except Exception as e:
            logger.error(f"Error al crear la notificación: {e}", exc_info=True)
            db.session.rollback()
            raise

    @classmethod
    def accept_notification(cls, notification_id):
        try:
            notification = cls.query.get(notification_id)
            if not notification:
                logger.error(f"No se encontró la notificación con ID {notification_id}.")
                return False
            if notification.is_accepted:
                logger.info(f"La notificación con ID {notification_id} ya estaba aceptada.")
                return True
            notification.is_accepted = True
            db.session.commit()
            db.session.refresh(notification)
            logger.debug(f"Estado de la notificación después de commit: {notification}")
            logger.info(f"Notificación con ID {notification_id} aceptada.")
            return True
        except Exception as e:
            logger.error(f"Error al aceptar la notificación: {e}", exc_info=True)
            db.session.rollback()
            return False

# Importar Message y Usuario después de definir Notification
from src.models.message import Message
from src.models.usuarios import Usuario