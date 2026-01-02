from datetime import datetime
from src.models.database import db

class Message(db.Model):
    __tablename__ = 'message'

    id = db.Column(db.Integer, primary_key=True)
    notification_id = db.Column(db.Integer, db.ForeignKey('notification.id'), nullable=False)
    
    # ✅ CORRECCIÓN: Se cambia 'usuario.id_usuario' por 'usuarios.id_usuario'
    sender_id = db.Column(db.Integer, db.ForeignKey('usuarios.id_usuario'), nullable=False)
    receiver_id = db.Column(db.Integer, db.ForeignKey('usuarios.id_usuario'), nullable=False)
    
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    # ✅ Relaciones con mapeo explícito
    notification = db.relationship('Notification', back_populates='messages')
    
    # Se especifica la clase 'Usuario' y las foreign_keys para evitar ambigüedad
    sender = db.relationship('Usuario', foreign_keys=[sender_id], backref="messages_sent_list")
    receiver = db.relationship('Usuario', foreign_keys=[receiver_id], backref="messages_received_list")

    def __repr__(self):
        return f"<Message {self.id} from {self.sender_id} to {self.receiver_id}>"

    def serialize(self):
        return {
            "id": self.id,
            "notification_id": self.notification_id,
            "sender_id": self.sender_id,
            "receiver_id": self.receiver_id,
            "content": self.content,
            "timestamp": self.timestamp.isoformat()
        }

# Importaciones después de definir Message para evitar importación circular
from src.models.notification import Notification
from src.models.usuarios import Usuario