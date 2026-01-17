"""
TRAYECTORIA ECOSISTEMA
Modelo: Comprador
Descripción: Usuarios que compran en las tiendas del ecosistema
Actualizado: Sistema de Magic Links (token_acceso) + Conversión opcional a Usuario
"""

from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.dialects.postgresql import JSONB
from src.models.database import db
import uuid


class Comprador(db.Model):
    """
    Modelo de Comprador - Usuarios que compran en las tiendas.
    
    Un comprador puede:
    - Comprar como invitado (sin contraseña)
    - Registrarse para guardar sus datos
    - Tener múltiples direcciones de envío
    - Comprar en cualquier tienda del ecosistema Trayectoria
    - [NUEVO] Acceder a sus pedidos mediante Magic Link (token único)
    - [NUEVO] Convertirse en usuario completo de la plataforma
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
    # ★ NUEVO: SISTEMA DE MAGIC LINKS
    # ==========================================
    token_acceso = db.Column(db.String(100), unique=True, nullable=False, index=True)
    # Token único para acceso sin contraseña
    # Permite compartir link: /p/{token} o /comprador/{token}
    # Se genera automáticamente al crear el comprador
    
    # ==========================================
    # ★ NUEVO: CONVERSIÓN A USUARIO COMPLETO
    # ==========================================
    usuario_id = db.Column(
        db.Integer,
        db.ForeignKey('usuarios.id_usuario', ondelete='SET NULL'),
        nullable=True,
        index=True
    )
    # NULL = Es solo comprador
    # NOT NULL = Se convirtió en usuario completo de la plataforma
    # Permite acceso a todas las funcionalidades (crear negocios, etc.)
    
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
    
    # ★ NUEVO: Relación con Usuario (si se convirtió)
    usuario = db.relationship(
        'Usuario',
        foreign_keys=[usuario_id],
        backref='comprador_profile'
    )
    
    # ==========================================
    # CONSTRUCTOR MEJORADO
    # ==========================================
    def __init__(self, **kwargs):
        """
        Constructor que genera token automáticamente si no existe.
        """
        super(Comprador, self).__init__(**kwargs)
        
        # ★ NUEVO: Generar token si no se proporcionó
        if not self.token_acceso:
            self.token_acceso = str(uuid.uuid4())
    
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
    
    # ★ NUEVO: Propiedad calculada para total de pedidos
    @property
    def total_pedidos(self):
        """
        Retorna el total de pedidos del comprador.
        Calculado dinámicamente desde la relación.
        """
        return self.pedidos.count()
    
    # ★ NUEVO: Propiedad para verificar si es usuario completo
    @property
    def es_usuario_completo(self):
        """Indica si el comprador se convirtió en usuario de la plataforma."""
        return self.usuario_id is not None
    
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
    
    # ★ NUEVO: Método para generar nuevo token
    def regenerar_token(self):
        """
        Regenera el token de acceso.
        Útil por seguridad si el link se comparte inadecuadamente.
        """
        self.token_acceso = str(uuid.uuid4())
        return self.token_acceso
    
    # ★ NUEVO: Método para convertir a usuario completo
    def convertir_a_usuario(self, usuario_id):
        """
        Convierte el comprador en usuario completo de la plataforma.
        
        Args:
            usuario_id (int): ID del usuario creado
            
        Returns:
            bool: True si la conversión fue exitosa
        """
        if self.es_usuario_completo:
            return False  # Ya es usuario
        
        self.usuario_id = usuario_id
        db.session.commit()
        return True
    
    # ==========================================
    # SERIALIZACIÓN
    # ==========================================
    def to_dict(self, include_direcciones=False, include_token=False):
        """
        Serializa el comprador a diccionario.
        
        Args:
            include_direcciones (bool): Si incluir direcciones
            include_token (bool): Si incluir token de acceso (usar con cuidado)
        """
        data = {
            'id_comprador': self.id_comprador,
            'id': self.id_comprador,  # Alias para compatibilidad
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
            'total_gastado': float(self.total_gastado or 0),
            # ★ NUEVO: Campos adicionales
            'total_pedidos': self.total_pedidos,
            'es_usuario_completo': self.es_usuario_completo
        }
        
        # ★ NUEVO: Incluir token solo si se solicita explícitamente
        if include_token:
            data['token'] = self.token_acceso
            data['token_acceso'] = self.token_acceso
        
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
    
    # ★ NUEVO: Serialización para API de checkout
    def to_dict_checkout(self):
        """
        Datos para respuesta de checkout.
        Incluye token para seguimiento.
        """
        return {
            'id': self.id_comprador,
            'nombre': self.nombre_completo,
            'telefono': self.telefono,
            'email': self.correo,
            'token': self.token_acceso,
            'es_nuevo': self.total_compras == 0,
            'total_pedidos': self.total_pedidos
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
    
    # ★ NUEVO: Buscar por token
    @classmethod
    def buscar_por_token(cls, token):
        """
        Busca un comprador por su token de acceso.
        
        Args:
            token (str): Token de acceso
            
        Returns:
            Comprador o None
        """
        return cls.query.filter_by(token_acceso=token, activo=True).first()
    
    @classmethod
    def crear_invitado(cls, nombre, correo, telefono, apellidos=None):
        """
        Crea un comprador como invitado (sin contraseña).
        El token se genera automáticamente en __init__.
        """
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
            # token_acceso se genera automáticamente en __init__
        )
        db.session.add(comprador)
        return comprador
    
    @classmethod
    def crear_registrado(cls, nombre, correo, telefono, password, apellidos=None):
        """
        Crea un comprador con cuenta registrada.
        El token se genera automáticamente en __init__.
        """
        comprador = cls(
            nombre=nombre,
            apellidos=apellidos,
            correo=correo.lower().strip(),
            telefono=telefono
            # token_acceso se genera automáticamente en __init__
        )
        comprador.set_password(password)
        db.session.add(comprador)
        return comprador
    
    def __repr__(self):
        return f'<Comprador {self.id_comprador}: {self.nombre_completo}>'


# ==========================================
# NOTAS DE MIGRACIÓN
# ==========================================
"""
Para aplicar estos cambios a la base de datos:

1. Crear migración:
   alembic revision --autogenerate -m "Agregar token_acceso y usuario_id a compradores"

2. La migración debe incluir:
   - Agregar columna token_acceso (String 100, unique, nullable=False)
   - Agregar columna usuario_id (Integer, FK a usuarios.id_usuario, nullable=True)
   - Crear índice en token_acceso
   - Crear índice en usuario_id
   - Crear foreign key constraint
   - Generar tokens para compradores existentes:
     UPDATE compradores SET token_acceso = gen_random_uuid()::text WHERE token_acceso IS NULL

3. Aplicar migración:
   alembic upgrade head

Ver GUIA_INTEGRACION.md para detalles completos.
"""