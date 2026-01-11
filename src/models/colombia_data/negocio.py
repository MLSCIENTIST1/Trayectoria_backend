"""
BizFlow Studio - Modelo de Negocio
Gestión de negocios con soporte para micrositios

VERSIÓN PARCHADA - Incluye:
- whatsapp, tipo_pagina, logo_url
"""

import sqlalchemy as sa
from sqlalchemy.orm import relationship
from src.models.database import db
from datetime import datetime


class Negocio(db.Model):
    """
    Modelo para gestión de negocios (empresas/comercios) en BizFlow.
    Incluye soporte para micrositios personalizados.
    """
    __tablename__ = 'negocios'

    # ==========================================
    # IDENTIFICACIÓN Y DATOS BÁSICOS
    # ==========================================
    id_negocio = sa.Column(sa.Integer, primary_key=True)
    nombre_negocio = sa.Column(sa.String(150), nullable=False, index=True)
    descripcion = sa.Column(sa.Text, nullable=True)
    direccion = sa.Column(sa.String(255), nullable=True)
    telefono = sa.Column(sa.String(20), nullable=True)
    categoria = sa.Column(sa.String(100), nullable=True, index=True)
    
    # ==========================================
    # MICROSITIO / PÁGINA WEB
    # ==========================================
    tiene_pagina = sa.Column(sa.Boolean, default=False, nullable=False)
    plantilla_id = sa.Column(sa.String(50), nullable=True)  # 'p1', 'p2', 'p3', etc.
    slug = sa.Column(sa.String(100), unique=True, nullable=True, index=True)  # URL amigable
    color_tema = sa.Column(sa.String(20), default="#4cd137")
    
    # ==========================================
    # NUEVOS CAMPOS - MICROSITIO EXTENDIDO
    # ==========================================
    whatsapp = sa.Column(sa.String(20), nullable=True)  # Número de WhatsApp para contacto
    tipo_pagina = sa.Column(sa.String(50), default='landing', nullable=True)  # 'landing', 'catalogo', 'tienda'
    logo_url = sa.Column(sa.Text, nullable=True)  # URL del logo del negocio
    
    # ==========================================
    # METADATA
    # ==========================================
    fecha_registro = sa.Column(sa.DateTime, default=datetime.utcnow, nullable=False)
    fecha_actualizacion = sa.Column(sa.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    activo = sa.Column(sa.Boolean, default=True, nullable=False)
    
    # ==========================================
    # CLAVES FORÁNEAS
    # ==========================================
    ciudad_id = sa.Column(
        sa.Integer, 
        sa.ForeignKey('colombia.ciudad_id', ondelete='SET NULL'),
        nullable=True
    )
    usuario_id = sa.Column(
        sa.Integer,
        sa.ForeignKey('usuarios.id_usuario', ondelete='CASCADE'),
        nullable=False,
        index=True
    )
    
    # ==========================================
    # RELACIONES
    # ==========================================
    ciudad = relationship("Colombia", foreign_keys=[ciudad_id])
    dueno = relationship("Usuario", foreign_keys=[usuario_id])
    
    # Relación con sucursales (cascade delete)
    sucursales = relationship(
        "Sucursal",
        back_populates="negocio",
        cascade="all, delete-orphan",
        lazy='dynamic'  # Para queries eficientes
    )
    
    # Relación con productos del catálogo
    productos = relationship(
        "ProductoCatalogo",
        back_populates="negocio",
        cascade="all, delete-orphan",
        lazy='dynamic'
    )
    
    # Relación con transacciones
    transacciones = relationship(
        "TransaccionOperativa",
        back_populates="negocio",
        cascade="all, delete-orphan",
        lazy='dynamic'
    )

    # ==========================================
    # MÉTODOS
    # ==========================================
    
    def __init__(self, nombre_negocio, usuario_id, **kwargs):
        """
        Constructor del negocio.
        
        Args:
            nombre_negocio (str): Nombre del negocio
            usuario_id (int): ID del usuario propietario
            **kwargs: Campos adicionales
        """
        self.nombre_negocio = nombre_negocio
        self.usuario_id = usuario_id
        
        # Campos opcionales básicos
        self.descripcion = kwargs.get('descripcion')
        self.direccion = kwargs.get('direccion')
        self.telefono = kwargs.get('telefono')
        self.categoria = kwargs.get('categoria', 'General')
        self.ciudad_id = kwargs.get('ciudad_id')
        
        # Campos de micrositio
        self.whatsapp = kwargs.get('whatsapp')
        self.tipo_pagina = kwargs.get('tipo_pagina', 'landing')
        self.logo_url = kwargs.get('logo_url')
        self.color_tema = kwargs.get('color_tema', '#4cd137')
        self.plantilla_id = kwargs.get('plantilla_id')
        self.tiene_pagina = kwargs.get('tiene_pagina', False)
        
        # Generar slug si no se proporciona
        if not kwargs.get('slug'):
            self.slug = self._generar_slug(nombre_negocio)
        else:
            self.slug = kwargs.get('slug')
    
    def _generar_slug(self, nombre):
        """
        Genera un slug URL-friendly desde el nombre del negocio.
        
        Args:
            nombre (str): Nombre del negocio
            
        Returns:
            str: Slug generado
        """
        import re
        # Convertir a minúsculas
        slug = nombre.lower()
        
        # Reemplazar caracteres especiales
        replacements = {
            'á': 'a', 'é': 'e', 'í': 'i', 'ó': 'o', 'ú': 'u',
            'ñ': 'n', 'ü': 'u',
            ' ': '-', '_': '-', '.': '-'
        }
        
        for old, new in replacements.items():
            slug = slug.replace(old, new)
        
        # Eliminar caracteres no permitidos
        slug = re.sub(r'[^a-z0-9-]', '', slug)
        
        # Eliminar guiones múltiples
        slug = re.sub(r'-+', '-', slug)
        
        # Eliminar guiones al inicio y final
        slug = slug.strip('-')
        
        return slug[:100]  # Limitar longitud
    
    def activar_pagina(self, plantilla_id='p1', tipo_pagina='landing'):
        """
        Activa el micrositio del negocio.
        
        Args:
            plantilla_id (str): ID de la plantilla a usar
            tipo_pagina (str): Tipo de página ('landing', 'catalogo', 'tienda')
        """
        self.tiene_pagina = True
        self.plantilla_id = plantilla_id
        self.tipo_pagina = tipo_pagina
        
        if not self.slug:
            self.slug = self._generar_slug(self.nombre_negocio)
    
    def desactivar_pagina(self):
        """Desactiva el micrositio del negocio."""
        self.tiene_pagina = False
    
    def get_url_sitio(self):
        """
        Obtiene la URL del micrositio.
        
        Returns:
            str or None: URL del sitio o None si no tiene
        """
        if self.tiene_pagina and self.slug:
            return f"/sitio/{self.slug}"
        return None
    
    def get_whatsapp_link(self, mensaje=None):
        """
        Genera el link de WhatsApp para contacto.
        
        Args:
            mensaje (str): Mensaje predeterminado (opcional)
            
        Returns:
            str or None: URL de WhatsApp o None si no tiene número
        """
        if not self.whatsapp:
            return None
        
        # Limpiar número (solo dígitos)
        numero = ''.join(filter(str.isdigit, self.whatsapp))
        
        # Agregar código de país si no lo tiene (Colombia = 57)
        if len(numero) == 10:
            numero = f"57{numero}"
        
        url = f"https://wa.me/{numero}"
        
        if mensaje:
            from urllib.parse import quote
            url += f"?text={quote(mensaje)}"
        
        return url
    
    def to_dict(self, include_relations=False):
        """
        Convierte el negocio a diccionario.
        
        Args:
            include_relations (bool): Si incluir sucursales y productos
            
        Returns:
            dict: Datos del negocio
        """
        data = {
            "id": self.id_negocio,
            "id_negocio": self.id_negocio,
            "nombre_negocio": self.nombre_negocio,
            "descripcion": self.descripcion,
            "direccion": self.direccion,
            "telefono": self.telefono,
            "categoria": self.categoria,
            "ciudad_id": self.ciudad_id,
            "usuario_id": self.usuario_id,
            "activo": self.activo,
            
            # Micrositio
            "tiene_pagina": self.tiene_pagina,
            "plantilla_id": self.plantilla_id,
            "slug": self.slug,
            "color_tema": self.color_tema,
            "url_sitio": self.get_url_sitio(),
            
            # Nuevos campos de micrositio
            "whatsapp": self.whatsapp,
            "tipo_pagina": self.tipo_pagina,
            "logo_url": self.logo_url,
            "whatsapp_link": self.get_whatsapp_link(),
            
            # Metadata
            "fecha_registro": self.fecha_registro.isoformat() if self.fecha_registro else None,
            "fecha_actualizacion": self.fecha_actualizacion.isoformat() if self.fecha_actualizacion else None
        }
        
        # Ciudad
        if self.ciudad:
            data["nombre_ciudad"] = self.ciudad.ciudad_nombre
            data["departamento"] = getattr(self.ciudad, 'departamento', None)
        else:
            data["nombre_ciudad"] = None
            data["departamento"] = None
        
        # Relaciones opcionales
        if include_relations:
            data["sucursales_count"] = self.sucursales.count()
            data["productos_count"] = self.productos.count()
        
        return data
    
    def serialize(self):
        """Alias de to_dict() para compatibilidad."""
        return self.to_dict()
    
    def __repr__(self):
        return f'<Negocio {self.nombre_negocio} (ID: {self.id_negocio})>'
    
    def __str__(self):
        return self.nombre_negocio