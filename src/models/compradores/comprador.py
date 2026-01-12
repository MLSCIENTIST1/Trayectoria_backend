"""
TRAYECTORIA ECOSISTEMA
Modelo: Comprador
Descripción: Usuarios que compran en las tiendas del ecosistema
"""

from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.dialects.postgresql import JSONB
from src.models.database import db


class Comprador(db.Model):
    """
    Modelo de Comprador - Usuarios que compran en las tiendas.
    
    Un comprador puede:
    - Comprar como invitado (sin contraseña)
    - Registrarse para guardar sus datos
    - Tener múltiples direcciones de envío
    - Comprar en cualquier tienda del ecosistema Trayectoria
    """
    __tablename__ = 'compradores'
    
    # ==========================================
    # CAMPOS PRINCIPALES
    # ==========================================
    id_comprador = db.Column(db.Integer, primary_key=True)
    
    # Datos personales
    nombre = db.Column(db.String(100), nullable=False)
    apellidos = db.Column(db.String(100))
    correo = db.Column(db.String(150), unique=True, nullable=False, index=True)
    telefono = db.Column(db.String(20), nullable=False, index=True)
    password_hash = db.Column(db.String(255))  # NULL si es invitado
    
    # Identificación (opcional, para facturación)
    tipo_documento = db.Column(db.String(20))  # CC, CE, NIT, Pasaporte
    numero_documento = db.Column(db.String(30), index=True)
    
    # ==========================================
    # ESTADO DE LA CUENTA
    # ==========================================
    es_registrado = db.Column(db.Boolean, default=False)  # TRUE si creó cuenta con contraseña
    verificado = db.Column(db.Boolean, default=False)  # TRUE si verificó correo
    activo = db.Column(db.Boolean, default=True)
    
    # ==========================================
    # PREFERENCIAS
    # ==========================================
    acepta_marketing = db.Column(db.Boolean, default=False)
    preferencias = db.Column(JSONB, default={})  # Notificaciones, idioma, etc.
    
    # ==========================================
    # METADATA Y ESTADÍSTICAS
    # ==========================================
    fecha_registro = db.Column(db.DateTime, default=datetime.utcnow)
    ultima_compra = db.Column(db.DateTime)
    total_compras = db.Column(db.Integer, default=0)
    total_gastado = db.Column(db.Numeric(12, 2), default=0)
    
    # ==========================================
    # RELACIONES
    # ==========================================
    direcciones = db.relationship(
        'DireccionComprador',
        backref='comprador',
        lazy='dynamic',
        cascade='all, delete-orphan'
    )
    
    pedidos = db.relationship(
        'Pedido',
        backref='comprador',
        lazy='dynamic'
    )
    
    # ==========================================
    # MÉTODOS DE CONTRASEÑA
    # ==========================================
    def set_password(self, password):
        """Establece la contraseña hasheada."""
        self.password_hash = generate_password_hash(password)
        self.es_registrado = True
    
    def check_password(self, password):
        """Verifica la contraseña."""
        if not self.password_hash:
            return False
        return check_password_hash(self.password_hash, password)
    
    # ==========================================
    # MÉTODOS DE UTILIDAD
    # ==========================================
    @property
    def nombre_completo(self):
        """Retorna el nombre completo."""
        if self.apellidos:
            return f"{self.nombre} {self.apellidos}"
        return self.nombre
    
    @property
    def tiene_cuenta(self):
        """Indica si tiene cuenta registrada (no es solo invitado)."""
        return self.es_registrado and self.password_hash is not None
    
    def get_direccion_principal(self):
        """Obtiene la dirección principal del comprador."""
        return self.direcciones.filter_by(es_principal=True, activo=True).first()
    
    def get_direcciones_activas(self):
        """Obtiene todas las direcciones activas."""
        return self.direcciones.filter_by(activo=True).all()
    
    def registrar_compra(self, monto):
        """Actualiza estadísticas después de una compra."""
        self.total_compras = (self.total_compras or 0) + 1
        self.total_gastado = (self.total_gastado or 0) + monto
        self.ultima_compra = datetime.utcnow()
    
    # ==========================================
    # SERIALIZACIÓN
    # ==========================================
    def to_dict(self, include_direcciones=False):
        """Serializa el comprador a diccionario."""
        data = {
            'id_comprador': self.id_comprador,
            'nombre': self.nombre,
            'apellidos': self.apellidos,
            'nombre_completo': self.nombre_completo,
            'correo': self.correo,
            'telefono': self.telefono,
            'tipo_documento': self.tipo_documento,
            'numero_documento': self.numero_documento,
            'es_registrado': self.es_registrado,
            'verificado': self.verificado,
            'activo': self.activo,
            'acepta_marketing': self.acepta_marketing,
            'fecha_registro': self.fecha_registro.isoformat() if self.fecha_registro else None,
            'ultima_compra': self.ultima_compra.isoformat() if self.ultima_compra else None,
            'total_compras': self.total_compras or 0,
            'total_gastado': float(self.total_gastado or 0)
        }
        
        if include_direcciones:
            data['direcciones'] = [d.to_dict() for d in self.get_direcciones_activas()]
            data['direccion_principal'] = None
            dir_principal = self.get_direccion_principal()
            if dir_principal:
                data['direccion_principal'] = dir_principal.to_dict()
        
        return data
    
    def to_dict_pedido(self):
        """Datos mínimos para guardar en el pedido (snapshot)."""
        return {
            'id_comprador': self.id_comprador,
            'nombre': self.nombre_completo,
            'correo': self.correo,
            'telefono': self.telefono,
            'documento': f"{self.tipo_documento} {self.numero_documento}" if self.numero_documento else None
        }
    
    # ==========================================
    # MÉTODOS DE CLASE
    # ==========================================
    @classmethod
    def buscar_por_correo(cls, correo):
        """Busca un comprador por correo."""
        return cls.query.filter_by(correo=correo.lower().strip()).first()
    
    @classmethod
    def buscar_por_telefono(cls, telefono):
        """Busca un comprador por teléfono."""
        # Limpiar teléfono de espacios y caracteres
        telefono_limpio = ''.join(filter(str.isdigit, telefono))
        return cls.query.filter(
            cls.telefono.contains(telefono_limpio[-10:])  # Últimos 10 dígitos
        ).first()
    
    @classmethod
    def crear_invitado(cls, nombre, correo, telefono, apellidos=None):
        """Crea un comprador como invitado (sin contraseña)."""
        # Verificar si ya existe
        existente = cls.buscar_por_correo(correo)
        if existente:
            return existente
        
        comprador = cls(
            nombre=nombre,
            apellidos=apellidos,
            correo=correo.lower().strip(),
            telefono=telefono,
            es_registrado=False
        )
        db.session.add(comprador)
        return comprador
    
    @classmethod
    def crear_registrado(cls, nombre, correo, telefono, password, apellidos=None):
        """Crea un comprador con cuenta registrada."""
        comprador = cls(
            nombre=nombre,
            apellidos=apellidos,
            correo=correo.lower().strip(),
            telefono=telefono
        )
        comprador.set_password(password)
        db.session.add(comprador)
        return comprador
    
    def __repr__(self):
        return f'<Comprador {self.id_comprador}: {self.nombre_completo}>'