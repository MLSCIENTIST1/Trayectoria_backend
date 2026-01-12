"""
TRAYECTORIA ECOSISTEMA
Modelo: DireccionComprador
Descripción: Direcciones de envío de los compradores
"""

from datetime import datetime
from sqlalchemy.dialects.postgresql import JSONB
from src.models.database import db


class DireccionComprador(db.Model):
    """
    Modelo de Dirección de Comprador.
    
    Un comprador puede tener múltiples direcciones:
    - Residencia (casa, apartamento)
    - Oficina/Trabajo
    - Local comercial
    - Vereda (zona rural)
    - Kilómetro (carretera)
    - Centro penitenciario
    - Guarnición militar
    - Punto de recogida
    """
    __tablename__ = 'direcciones_comprador'
    
    # ==========================================
    # TIPOS DE DIRECCIÓN
    # ==========================================
    TIPOS_DIRECCION = {
        'residencia': {'label': 'Residencia', 'icon': '🏠', 'descripcion': 'Casa o apartamento'},
        'oficina': {'label': 'Oficina', 'icon': '🏢', 'descripcion': 'Lugar de trabajo'},
        'local_comercial': {'label': 'Local Comercial', 'icon': '🏪', 'descripcion': 'Tienda o negocio'},
        'vereda': {'label': 'Vereda', 'icon': '🌾', 'descripcion': 'Zona rural'},
        'kilometro': {'label': 'Kilómetro', 'icon': '📍', 'descripcion': 'Ubicación por kilómetro en carretera'},
        'centro_penitenciario': {'label': 'Centro Penitenciario', 'icon': '🔒', 'descripcion': 'Cárcel o centro de reclusión'},
        'guarnicion_militar': {'label': 'Guarnición Militar', 'icon': '🎖️', 'descripcion': 'Base o instalación militar'},
        'punto_recogida': {'label': 'Punto de Recogida', 'icon': '📦', 'descripcion': 'Punto acordado para recoger'},
        'otro': {'label': 'Otro', 'icon': '📌', 'descripcion': 'Otro tipo de ubicación'}
    }
    
    # ==========================================
    # CAMPOS PRINCIPALES
    # ==========================================
    id_direccion = db.Column(db.Integer, primary_key=True)
    comprador_id = db.Column(
        db.Integer, 
        db.ForeignKey('compradores.id_comprador', ondelete='CASCADE'),
        nullable=False,
        index=True
    )
    
    # Tipo y alias
    tipo_direccion = db.Column(db.String(50), nullable=False, default='residencia')
    alias = db.Column(db.String(50))  # "Mi casa", "Oficina", "Finca Los Naranjos"
    
    # ==========================================
    # UBICACIÓN GEOGRÁFICA
    # ==========================================
    pais = db.Column(db.String(50), default='Colombia')
    departamento = db.Column(db.String(100), nullable=False)
    ciudad = db.Column(db.String(100), nullable=False, index=True)
    localidad = db.Column(db.String(100))  # Para Bogotá: Kennedy, Suba, etc.
    barrio = db.Column(db.String(100))
    codigo_postal = db.Column(db.String(20))
    
    # ==========================================
    # DIRECCIÓN ESPECÍFICA
    # ==========================================
    direccion = db.Column(db.Text, nullable=False)  # Cra 10 #20-30 Apto 401
    complemento = db.Column(db.String(255))  # Torre B, Local 3, Interior 2
    referencias = db.Column(db.Text)  # "Edificio azul al lado del parque"
    
    # ==========================================
    # DATOS ESPECIALES (para tipos específicos)
    # ==========================================
    nombre_establecimiento = db.Column(db.String(150))  # "Centro Penitenciario La Picota"
    datos_especiales = db.Column(JSONB, default={})
    # Ejemplos:
    # Centro penitenciario: {"patio": "5", "pabellon": "A", "interno": "Juan Pérez"}
    # Guarnición militar: {"batallon": "...", "compania": "...", "destinatario": "..."}
    # Kilómetro: {"via": "Bogotá-Melgar", "kilometro": "45", "lado": "derecho"}
    # Vereda: {"corregimiento": "...", "finca": "..."}
    
    # ==========================================
    # COORDENADAS (opcional)
    # ==========================================
    latitud = db.Column(db.Numeric(10, 8))
    longitud = db.Column(db.Numeric(11, 8))
    
    # ==========================================
    # ESTADO
    # ==========================================
    es_principal = db.Column(db.Boolean, default=False)
    activo = db.Column(db.Boolean, default=True)
    
    # ==========================================
    # TIMESTAMPS
    # ==========================================
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    fecha_actualizacion = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # ==========================================
    # MÉTODOS
    # ==========================================
    @property
    def tipo_info(self):
        """Retorna información del tipo de dirección."""
        return self.TIPOS_DIRECCION.get(self.tipo_direccion, self.TIPOS_DIRECCION['otro'])
    
    @property
    def direccion_completa(self):
        """Genera la dirección completa formateada."""
        partes = []
        
        # Para tipos especiales, incluir nombre del establecimiento
        if self.nombre_establecimiento:
            partes.append(self.nombre_establecimiento)
        
        # Dirección principal
        partes.append(self.direccion)
        
        # Complemento
        if self.complemento:
            partes.append(self.complemento)
        
        # Barrio
        if self.barrio:
            partes.append(f"Barrio {self.barrio}")
        
        # Localidad (para ciudades grandes)
        if self.localidad:
            partes.append(f"Localidad {self.localidad}")
        
        # Ciudad y departamento
        partes.append(f"{self.ciudad}, {self.departamento}")
        
        # País si no es Colombia
        if self.pais and self.pais != 'Colombia':
            partes.append(self.pais)
        
        return ', '.join(partes)
    
    @property
    def direccion_corta(self):
        """Dirección resumida para mostrar en listas."""
        if self.alias:
            return f"{self.alias} - {self.ciudad}"
        return f"{self.direccion[:30]}... - {self.ciudad}"
    
    def set_como_principal(self):
        """Establece esta dirección como principal."""
        # Quitar principal de las otras direcciones del mismo comprador
        DireccionComprador.query.filter(
            DireccionComprador.comprador_id == self.comprador_id,
            DireccionComprador.id_direccion != self.id_direccion
        ).update({'es_principal': False})
        
        self.es_principal = True
    
    # ==========================================
    # SERIALIZACIÓN
    # ==========================================
    def to_dict(self):
        """Serializa la dirección a diccionario."""
        tipo_info = self.tipo_info
        
        return {
            'id_direccion': self.id_direccion,
            'comprador_id': self.comprador_id,
            
            # Tipo
            'tipo_direccion': self.tipo_direccion,
            'tipo_label': tipo_info['label'],
            'tipo_icon': tipo_info['icon'],
            'alias': self.alias,
            
            # Ubicación
            'pais': self.pais,
            'departamento': self.departamento,
            'ciudad': self.ciudad,
            'localidad': self.localidad,
            'barrio': self.barrio,
            'codigo_postal': self.codigo_postal,
            
            # Dirección
            'direccion': self.direccion,
            'complemento': self.complemento,
            'referencias': self.referencias,
            'direccion_completa': self.direccion_completa,
            'direccion_corta': self.direccion_corta,
            
            # Especiales
            'nombre_establecimiento': self.nombre_establecimiento,
            'datos_especiales': self.datos_especiales or {},
            
            # Coordenadas
            'latitud': float(self.latitud) if self.latitud else None,
            'longitud': float(self.longitud) if self.longitud else None,
            
            # Estado
            'es_principal': self.es_principal,
            'activo': self.activo,
            
            # Timestamps
            'fecha_creacion': self.fecha_creacion.isoformat() if self.fecha_creacion else None
        }
    
    def to_dict_pedido(self):
        """Datos para guardar en el pedido (snapshot completo)."""
        return {
            'tipo': self.tipo_direccion,
            'tipo_label': self.tipo_info['label'],
            'alias': self.alias,
            'pais': self.pais,
            'departamento': self.departamento,
            'ciudad': self.ciudad,
            'localidad': self.localidad,
            'barrio': self.barrio,
            'direccion': self.direccion,
            'complemento': self.complemento,
            'referencias': self.referencias,
            'nombre_establecimiento': self.nombre_establecimiento,
            'datos_especiales': self.datos_especiales or {},
            'direccion_completa': self.direccion_completa
        }
    
    @classmethod
    def get_tipos_direccion(cls):
        """Retorna los tipos de dirección disponibles."""
        return [
            {'value': k, **v}
            for k, v in cls.TIPOS_DIRECCION.items()
        ]
    
    def __repr__(self):
        return f'<DireccionComprador {self.id_direccion}: {self.direccion_corta}>'