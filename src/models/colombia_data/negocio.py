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
#
# © 2024-2026 Carlos Eduardo Huérfano Bermúdez. Todos los derechos reservados.
# C.C.: 1.064.986.917 (Cereté, Córdoba, Colombia)
# Contacto: carlos-5100@hotmail.com | +57 322 818 8375
#
# ═══════════════════════════════════════════════════════════════════════════════

"""
BizFlow Studio - Modelo de Negocio
Gestión de negocios con soporte para micrositios

VERSIÓN 2.6 - Incluye:
- whatsapp, tipo_pagina, logo_url
- config_tienda (JSONB) para Store Designer
- QR del negocio (qr_negocio_url, qr_negocio_data)
- Perfil público (perfil_publico)
- 🆕 Email del negocio
- 🆕 Horario de atención (JSONB)
- 🆕 Video portafolio
- 🆕 Redes sociales (JSONB)
- 🆕 Sitio web externo
"""

import sqlalchemy as sa
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import JSONB
from src.models.database import db
from datetime import datetime


class Negocio(db.Model):
    """
    Modelo para gestión de negocios (empresas/comercios) en TuKomercio.
    Incluye soporte para micrositios personalizados, QR automático y redes sociales.
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
    # 🆕 CONTACTO EXTENDIDO (v2.6)
    # ==========================================
    email = sa.Column(sa.String(255), nullable=True)
    sitio_web = sa.Column(sa.String(500), nullable=True)  # URL externa del negocio
    
    # ==========================================
    # 🆕 HORARIO DE ATENCIÓN (v2.6)
    # ==========================================
    # Formato JSONB: {
    #   "lunes": {"abre": "08:00", "cierra": "18:00", "cerrado": false},
    #   "martes": {"abre": "08:00", "cierra": "18:00", "cerrado": false},
    #   ...
    #   "domingo": {"abre": null, "cierra": null, "cerrado": true}
    # }
    horario_atencion = sa.Column(JSONB, default={}, nullable=True)
    
    # ==========================================
    # 🆕 VIDEO PORTAFOLIO (v2.6)
    # ==========================================
    video_portafolio = sa.Column(sa.Text, nullable=True)  # URL de YouTube/Vimeo
    
    # ==========================================
    # 🆕 REDES SOCIALES (v2.6)
    # ==========================================
    # Formato JSONB: {
    #   "instagram": "@minegocio",
    #   "facebook": "minegocio",
    #   "tiktok": "@minegocio",
    #   "twitter": "@minegocio",
    #   "linkedin": "minegocio",
    #   "youtube": "minegocio"
    # }
    redes_sociales = sa.Column(JSONB, default={}, nullable=True)
    
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

    verificado = sa.Column(sa.Boolean, default=False, nullable=False)
    ciudad = sa.Column(sa.String(100), nullable=True)
    
    # ==========================================
    # QR DEL NEGOCIO
    # ==========================================
    qr_negocio_url = sa.Column(sa.Text, nullable=True)
    qr_negocio_data = sa.Column(sa.String(300), nullable=True)
    perfil_publico = sa.Column(sa.Boolean, default=True, nullable=False)
    
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
    ciudad_rel = relationship("Colombia", foreign_keys=[ciudad_id])
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
        self.ciudad = kwargs.get('ciudad')
        
        # 🆕 Contacto extendido (v2.6)
        self.email = kwargs.get('email')
        self.sitio_web = kwargs.get('sitio_web')
        
        # 🆕 Horario y redes (v2.6)
        self.horario_atencion = kwargs.get('horario_atencion', {})
        self.video_portafolio = kwargs.get('video_portafolio')
        self.redes_sociales = kwargs.get('redes_sociales', {})
        
        # Campos de micrositio
        self.whatsapp = kwargs.get('whatsapp')
        self.tipo_pagina = kwargs.get('tipo_pagina', 'landing')
        self.logo_url = kwargs.get('logo_url')
        self.color_tema = kwargs.get('color_tema', '#4cd137')
        self.plantilla_id = kwargs.get('plantilla_id')
        self.tiene_pagina = kwargs.get('tiene_pagina', False)
        
        # Store Designer
        self.config_tienda = kwargs.get('config_tienda', {})
        
        # QR y perfil público
        self.qr_negocio_url = kwargs.get('qr_negocio_url')
        self.qr_negocio_data = kwargs.get('qr_negocio_data')
        self.perfil_publico = kwargs.get('perfil_publico', True)
        
        # Verificado
        self.verificado = kwargs.get('verificado', False)
        
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
    # MÉTODOS DE QR Y PERFIL PÚBLICO
    # ==========================================
    
    def get_url_perfil_publico(self, base_url="https://tuko.pages.dev"):
        """Obtiene la URL del perfil público del negocio."""
        if self.slug:
            return f"{base_url}/negocio/negocio_perfil.html?slug={self.slug}"
        return None
    
    def generar_qr_data(self, base_url="https://tuko.pages.dev"):
        """Genera el dato que se codificará en el QR."""
        url = self.get_url_perfil_publico(base_url)
        if url:
            self.qr_negocio_data = url
        return url
    
    def set_qr_url(self, url):
        """Establece la URL del QR almacenado (Cloudinary)."""
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
    # 🆕 MÉTODOS DE REDES SOCIALES (v2.6)
    # ==========================================
    
    def get_social_link(self, red):
        """
        Genera el link completo para una red social.
        
        Args:
            red (str): Nombre de la red (instagram, facebook, tiktok, twitter, linkedin, youtube)
            
        Returns:
            str: URL completa o None
        """
        if not self.redes_sociales or red not in self.redes_sociales:
            return None
        
        username = self.redes_sociales.get(red, '').strip()
        if not username:
            return None
        
        # Limpiar @ si lo tiene
        username = username.lstrip('@')
        
        base_urls = {
            'instagram': f'https://instagram.com/{username}',
            'facebook': f'https://facebook.com/{username}',
            'tiktok': f'https://tiktok.com/@{username}',
            'twitter': f'https://twitter.com/{username}',
            'linkedin': f'https://linkedin.com/company/{username}',
            'youtube': f'https://youtube.com/@{username}'
        }
        
        return base_urls.get(red)
    
    def get_all_social_links(self):
        """Obtiene todos los links de redes sociales configurados."""
        if not self.redes_sociales:
            return {}
        
        links = {}
        for red in ['instagram', 'facebook', 'tiktok', 'twitter', 'linkedin', 'youtube']:
            link = self.get_social_link(red)
            if link:
                links[red] = link
        
        return links
    
    # ==========================================
    # 🆕 MÉTODOS DE HORARIO (v2.6)
    # ==========================================
    
    def get_horario_dia(self, dia):
        """
        Obtiene el horario de un día específico.
        
        Args:
            dia (str): Día de la semana (lunes, martes, etc.)
            
        Returns:
            dict: {'abre': '08:00', 'cierra': '18:00', 'cerrado': False}
        """
        if not self.horario_atencion:
            return None
        
        return self.horario_atencion.get(dia.lower())
    
    def esta_abierto_hoy(self):
        """Verifica si el negocio está abierto hoy (básico, sin hora exacta)."""
        from datetime import datetime
        
        dias = ['lunes', 'martes', 'miercoles', 'jueves', 'viernes', 'sabado', 'domingo']
        hoy = dias[datetime.now().weekday()]
        
        horario = self.get_horario_dia(hoy)
        if not horario:
            return None  # No hay horario configurado
        
        return not horario.get('cerrado', True)
    
    def get_horario_texto(self):
        """Obtiene el horario en formato legible."""
        if not self.horario_atencion:
            return "Horario no configurado"
        
        dias_orden = ['lunes', 'martes', 'miercoles', 'jueves', 'viernes', 'sabado', 'domingo']
        lineas = []
        
        for dia in dias_orden:
            horario = self.horario_atencion.get(dia, {})
            if horario.get('cerrado', True):
                lineas.append(f"{dia.capitalize()}: Cerrado")
            else:
                abre = horario.get('abre', '--:--')
                cierra = horario.get('cierra', '--:--')
                lineas.append(f"{dia.capitalize()}: {abre} - {cierra}")
        
        return '\n'.join(lineas)
    
    # ==========================================
    # 🆕 MÉTODOS DE VIDEO PORTAFOLIO (v2.6)
    # ==========================================
    
    def get_video_embed_url(self):
        """Convierte URL de video a formato embed."""
        if not self.video_portafolio:
            return None
        
        url = self.video_portafolio.strip()
        
        # YouTube
        if 'youtube.com/watch' in url:
            video_id = url.split('v=')[1].split('&')[0] if 'v=' in url else None
            if video_id:
                return f'https://www.youtube.com/embed/{video_id}'
        
        if 'youtu.be/' in url:
            video_id = url.split('youtu.be/')[1].split('?')[0]
            return f'https://www.youtube.com/embed/{video_id}'
        
        if 'youtube.com/shorts/' in url:
            video_id = url.split('shorts/')[1].split('?')[0]
            return f'https://www.youtube.com/embed/{video_id}'
        
        # Vimeo
        if 'vimeo.com/' in url:
            video_id = url.split('vimeo.com/')[1].split('?')[0]
            return f'https://player.vimeo.com/video/{video_id}'
        
        # Si ya es embed o no reconocido, devolver como está
        return url
    
    def tiene_video(self):
        """Verifica si el negocio tiene video portafolio."""
        return bool(self.video_portafolio)
    
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
            "ciudad": self.ciudad,
            "usuario_id": self.usuario_id,
            "activo": self.activo,
            "verificado": self.verificado,
            
            # 🆕 Contacto extendido (v2.6)
            "email": self.email,
            "sitio_web": self.sitio_web,
            
            # 🆕 Horario (v2.6)
            "horario_atencion": self.horario_atencion or {},
            "horario_texto": self.get_horario_texto(),
            "abierto_hoy": self.esta_abierto_hoy(),
            
            # 🆕 Video portafolio (v2.6)
            "video_portafolio": self.video_portafolio,
            "video_embed_url": self.get_video_embed_url(),
            "tiene_video": self.tiene_video(),
            
            # 🆕 Redes sociales (v2.6)
            "redes_sociales": self.redes_sociales or {},
            "social_links": self.get_all_social_links(),
            
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
            
            # QR del negocio
            "qr_negocio_url": self.qr_negocio_url,
            "qr_negocio_data": self.qr_negocio_data,
            "perfil_publico": self.perfil_publico,
            "tiene_qr": self.tiene_qr(),
            "url_perfil_publico": self.get_url_perfil_publico(),
            
            # Metadata
            "fecha_registro": self.fecha_registro.isoformat() if self.fecha_registro else None,
            "fecha_actualizacion": self.fecha_actualizacion.isoformat() if self.fecha_actualizacion else None
        }
        
        # Ciudad desde relación
        if hasattr(self, 'ciudad_rel') and self.ciudad_rel:
            data["nombre_ciudad"] = self.ciudad_rel.ciudad_nombre
            data["departamento"] = getattr(self.ciudad_rel, 'departamento', None)
        else:
            data["nombre_ciudad"] = self.ciudad
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