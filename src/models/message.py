from datetime import datetime
from src.models.database import db

class Message(db.Model):
    __tablename__ = 'message'

    id = db.Column(db.Integer, primary_key=True)
    notification_id = db.Column(db.Integer, db.ForeignKey('notification.id'), nullable=False)
    sender_id = db.Column(db.Integer, db.ForeignKey('usuario.id_usuario'), nullable=False)
    receiver_id = db.Column(db.Integer, db.ForeignKey('usuario.id_usuario'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    # Relaciones
    notification = db.relationship('Notification', back_populates='messages')
    
    sender = db.relationship('Usuario', foreign_keys=[sender_id])
    receiver = db.relationship('Usuario', foreign_keys=[receiver_id])

    def __repr__(self):
        return f"<Message {self.id} from {self.sender_id} to {self.receiver_id}>"

# Importaciones después de definir Message
from src.models.notification import Notification
from src.models.usuarios import Usuario