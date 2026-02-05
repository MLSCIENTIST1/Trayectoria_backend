# ═══════════════════════════════════════════════════════════════════════════════
# ███████╗██╗   ██╗██╗  ██╗ ██████╗ ███╗   ███╗███████╗██████╗  ██████╗██╗ ██████╗ 
# ╚══██╔══╝██║   ██║██║ ██╔╝██╔═══██╗████╗ ████║██╔════╝██╔══██╗██╔════╝██║██╔═══██╗
#    ██║   ██║   ██║█████╔╝ ██║   ██║██╔████╔██║█████╗  ██████╔╝██║     ██║██║   ██║
#    ██║   ██║   ██║██╔═██╗ ██║   ██║██║╚██╔╝██║██╔══╝  ██╔══██╗██║     ██║██║   ██║
#    ██║   ╚██████╔╝██║  ██╗╚██████╔╝██║ ╚═╝ ██║███████╗██║  ██║╚██████╗██║╚██████╔╝
#    ╚═╝    ╚═════╝ ╚═╝  ╚═╝ ╚═════╝ ╚═╝     ╚═╝╚══════╝╚═╝  ╚═╝ ╚═════╝╚═╝ ╚═════╝ 
# ═══════════════════════════════════════════════════════════════════════════════
#
# TUKOMERCIO - Plataforma de Comercio Electrónico, Gamificación y Gestión Empresarial
# Anteriormente conocido como: Trayectoria / BizFlow Studio
#
# ═══════════════════════════════════════════════════════════════════════════════
# AVISO DE PROPIEDAD INTELECTUAL Y DERECHOS DE AUTOR
# ═══════════════════════════════════════════════════════════════════════════════
#
# © 2024-2026 Carlos Eduardo Huérfano Bermúdez. Todos los derechos reservados.
#
# TITULAR DE DERECHOS:
#   Nombre:     Carlos Eduardo Huérfano Bermúdez
#   C.C.:       1.064.986.917 (Cereté, Córdoba, Colombia)
#   Contacto:   carlos-5100@hotmail.com | +57 322 818 8375
#   Ubicación:  Bogotá D.C., Colombia
#
# INFORMACIÓN DEL PROYECTO:
#   Nombre:     TuKomercio
#   Inicio:     Julio 24, 2024
#   Repositorio: github.com/routeres (routeres@gmail.com)
#
# ═══════════════════════════════════════════════════════════════════════════════
# TÉRMINOS DE USO Y RESTRICCIONES
# ═══════════════════════════════════════════════════════════════════════════════
#
# Este código fuente es CONFIDENCIAL y constituye un SECRETO COMERCIAL.
#
# QUEDA ESTRICTAMENTE PROHIBIDO sin autorización ESCRITA del titular:
#
#   1. Copiar, reproducir o duplicar este código, total o parcialmente
#   2. Modificar, adaptar o crear obras derivadas
#   3. Distribuir, publicar, sublicenciar o transferir a terceros
#   4. Usar para desarrollo de productos competidores
#   5. Realizar ingeniería inversa, descompilar o desensamblar
#   6. Remover o alterar este aviso de propiedad intelectual
#
# El acceso a este código NO otorga ninguna licencia implícita o explícita.
#
# ═══════════════════════════════════════════════════════════════════════════════
# PROTECCIÓN LEGAL
# ═══════════════════════════════════════════════════════════════════════════════
#
# Este software está protegido por:
#
#   • Ley 23 de 1982 - Derechos de Autor (Colombia)
#   • Ley 1915 de 2018 - Modernización Derechos de Autor (Colombia)
#   • Decisión Andina 351 de 1993 - Régimen Común sobre Derecho de Autor
#   • Convenio de Berna para la Protección de Obras Literarias y Artísticas
#   • Tratado OMPI sobre Derecho de Autor (WCT)
#   • Acuerdo ADPIC/TRIPS - Organización Mundial del Comercio
#
# SANCIONES POR INFRACCIÓN:
#   • Civiles: Indemnización por daños y perjuicios (Art. 57, Ley 23/1982)
#   • Penales: Prisión de 4 a 8 años y multa (Art. 271, Código Penal Colombiano)
#
# ═══════════════════════════════════════════════════════════════════════════════
# JURISDICCIÓN
# ═══════════════════════════════════════════════════════════════════════════════
#
# Cualquier disputa será resuelta exclusivamente por los tribunales de
# Bogotá D.C., Colombia, bajo las leyes de la República de Colombia.
#
# ═══════════════════════════════════════════════════════════════════════════════
#
# Para solicitar autorización de uso: carlos-5100@hotmail.com
#
# ═══════════════════════════════════════════════════════════════════════════════




"""
BizFlow Studio - Modelo de Negocio
Gestión de negocios con soporte para micrositios

VERSIÓN 2.5 - Incluye:
- whatsapp, tipo_pagina, logo_url
- config_tienda (JSONB) para Store Designer
- 🆕 QR del negocio (qr_negocio_url, qr_negocio_data)
- 🆕 Perfil público (perfil_publico)
- 🔄 URL actualizada para perfil público
"""

import sqlalchemy as sa
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import JSONB
from src.models.database import db
from datetime import datetime


class Negocio(db.Model):
    """
    Modelo para gestión de negocios (empresas/comercios) en BizFlow.
    Incluye soporte para micrositios personalizados y QR automático.
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
    plantilla_id = sa.Column(sa.String(50), nullable=True)
    slug = sa.Column(sa.String(100), unique=True, nullable=True, index=True)
    color_tema = sa.Column(sa.String(20), default="#4cd137")
    
    # ==========================================
    # CAMPOS EXTENDIDOS MICROSITIO
    # ==========================================
    whatsapp = sa.Column(sa.String(20), nullable=True)
    tipo_pagina = sa.Column(sa.String(50), default='landing', nullable=True)
    logo_url = sa.Column(sa.Text, nullable=True)
    
    # ==========================================
    # 🎨 STORE DESIGNER - Configuración JSON
    # ==========================================
    config_tienda = sa.Column(JSONB, default={}, nullable=True)

    verificado = sa.Column(sa.Boolean, default=False, nullable=False)  # Negocio verificado
    ciudad = sa.Column(sa.String(100), nullable=True)  # Ciudad para rankings/filtros
    
    # ==========================================
    # 🆕 QR DEL NEGOCIO
    # ==========================================
    qr_negocio_url = sa.Column(sa.Text, nullable=True)  # URL del QR en Cloudinary
    qr_negocio_data = sa.Column(sa.String(300), nullable=True)  # Dato codificado en el QR
    perfil_publico = sa.Column(sa.Boolean, default=True, nullable=False)  # Visible públicamente
    
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
    
    sucursales = relationship(
        "Sucursal",
        back_populates="negocio",
        cascade="all, delete-orphan",
        lazy='dynamic'
    )
    
    productos = relationship(
        "ProductoCatalogo",
        back_populates="negocio",
        cascade="all, delete-orphan",
        lazy='dynamic'
    )
    
    transacciones = relationship(
        "TransaccionOperativa",
        back_populates="negocio",
        cascade="all, delete-orphan",
        lazy='dynamic'
    )

    # ==========================================
    # CONSTRUCTOR
    # ==========================================
    
    def __init__(self, nombre_negocio, usuario_id, **kwargs):
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
        
        # Store Designer
        self.config_tienda = kwargs.get('config_tienda', {})
        
        # 🆕 QR y perfil público
        self.qr_negocio_url = kwargs.get('qr_negocio_url')
        self.qr_negocio_data = kwargs.get('qr_negocio_data')
        self.perfil_publico = kwargs.get('perfil_publico', True)
        
        # Generar slug si no se proporciona
        if not kwargs.get('slug'):
            self.slug = self._generar_slug(nombre_negocio)
        else:
            self.slug = kwargs.get('slug')
    
    # ==========================================
    # MÉTODOS PRIVADOS
    # ==========================================
    
    def _generar_slug(self, nombre):
        """Genera un slug URL-friendly desde el nombre del negocio."""
        import re
        slug = nombre.lower()
        
        replacements = {
            'á': 'a', 'é': 'e', 'í': 'i', 'ó': 'o', 'ú': 'u',
            'ñ': 'n', 'ü': 'u',
            ' ': '-', '_': '-', '.': '-'
        }
        
        for old, new in replacements.items():
            slug = slug.replace(old, new)
        
        slug = re.sub(r'[^a-z0-9-]', '', slug)
        slug = re.sub(r'-+', '-', slug)
        slug = slug.strip('-')
        
        return slug[:100]
    
    # ==========================================
    # MÉTODOS DE PÁGINA
    # ==========================================
    
    def activar_pagina(self, plantilla_id='p1', tipo_pagina='landing'):
        """Activa el micrositio del negocio."""
        self.tiene_pagina = True
        self.plantilla_id = plantilla_id
        self.tipo_pagina = tipo_pagina
        
        if not self.slug:
            self.slug = self._generar_slug(self.nombre_negocio)
    
    def desactivar_pagina(self):
        """Desactiva el micrositio del negocio."""
        self.tiene_pagina = False
    
    def get_url_sitio(self):
        """Obtiene la URL del micrositio."""
        if self.tiene_pagina and self.slug:
            return f"/sitio/{self.slug}"
        return None
    
    # ==========================================
    # 🆕 MÉTODOS DE QR Y PERFIL PÚBLICO
    # ==========================================
    
    def get_url_perfil_publico(self, base_url="https://tuko.pages.dev"):
        """
        Obtiene la URL del perfil público del negocio.
        Esta es la URL que se codifica en el QR.
        
        Args:
            base_url (str): URL base de la plataforma
            
        Returns:
            str: URL del perfil público
        """
        if self.slug:
            return f"{base_url}/negocio/negocio_perfil.html?slug={self.slug}"
        return None
    
    def generar_qr_data(self, base_url="https://tuko.pages.dev"):
        """
        Genera el dato que se codificará en el QR.
        
        Args:
            base_url (str): URL base de la plataforma
            
        Returns:
            str: URL a codificar en el QR
        """
        url = self.get_url_perfil_publico(base_url)
        if url:
            self.qr_negocio_data = url
        return url
    
    def set_qr_url(self, url):
        """
        Establece la URL del QR almacenado (Cloudinary).
        
        Args:
            url (str): URL de la imagen QR
        """
        self.qr_negocio_url = url
    
    def tiene_qr(self):
        """Verifica si el negocio tiene QR generado."""
        return bool(self.qr_negocio_url)
    
    # ==========================================
    # MÉTODOS DE WHATSAPP
    # ==========================================
    
    def get_whatsapp_link(self, mensaje=None):
        """Genera el link de WhatsApp para contacto."""
        if not self.whatsapp:
            return None
        
        numero = ''.join(filter(str.isdigit, self.whatsapp))
        
        if len(numero) == 10:
            numero = f"57{numero}"
        
        url = f"https://wa.me/{numero}"
        
        if mensaje:
            from urllib.parse import quote
            url += f"?text={quote(mensaje)}"
        
        return url
    
    # ==========================================
    # SERIALIZACIÓN
    # ==========================================
    
    def to_dict(self, include_relations=False):
        """Convierte el negocio a diccionario."""
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

            "verificado": self.verificado,
            "ciudad": self.ciudad,
            
            # Micrositio
            "tiene_pagina": self.tiene_pagina,
            "plantilla_id": self.plantilla_id,
            "slug": self.slug,
            "color_tema": self.color_tema,
            "url_sitio": self.get_url_sitio(),
            
            # Campos extendidos micrositio
            "whatsapp": self.whatsapp,
            "tipo_pagina": self.tipo_pagina,
            "logo_url": self.logo_url,
            "whatsapp_link": self.get_whatsapp_link(),
            
            # Store Designer
            "config_tienda": self.config_tienda or {},
            
            # 🆕 QR del negocio
            "qr_negocio_url": self.qr_negocio_url,
            "qr_negocio_data": self.qr_negocio_data,
            "perfil_publico": self.perfil_publico,
            "tiene_qr": self.tiene_qr(),
            "url_perfil_publico": self.get_url_perfil_publico(),
            
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