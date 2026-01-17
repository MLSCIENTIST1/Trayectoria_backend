"""
TRAYECTORIA ECOSISTEMA
Modelo: DireccionComprador
Descripción: Direcciones de envío de los compradores
Versión: 2.0 - Optimizado para checkout
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
    # ★ NUEVO: CONSTRUCTOR MEJORADO
    # ==========================================
    def __init__(self, **kwargs):
        """
        Constructor que facilita la creación desde el checkout.
        
        Permite usar tanto 'tipo_direccion' como 'tipo' (alias).
        """
        # Si se pasa 'tipo' en lugar de 'tipo_direccion', usarlo
        if 'tipo' in kwargs and 'tipo_direccion' not in kwargs:
            kwargs['tipo_direccion'] = kwargs.pop('tipo')
        
        # Si no hay tipo_direccion, usar residencia por defecto
        if 'tipo_direccion' not in kwargs:
            kwargs['tipo_direccion'] = 'residencia'
        
        # Validar tipo_direccion
        if kwargs['tipo_direccion'] not in self.TIPOS_DIRECCION:
            kwargs['tipo_direccion'] = 'residencia'
        
        super(DireccionComprador, self).__init__(**kwargs)
    
    # ==========================================
    # PROPIEDADES
    # ==========================================
    @property
    def tipo_info(self):
        """Retorna información del tipo de dirección."""
        return self.TIPOS_DIRECCION.get(self.tipo_direccion, self.TIPOS_DIRECCION['otro'])
    
    # ★ NUEVO: Alias para compatibilidad
    @property
    def tipo(self):
        """Alias de tipo_direccion para compatibilidad."""
        return self.tipo_direccion
    
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
    
    # ==========================================
    # MÉTODOS
    # ==========================================
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
            'id': self.id_direccion,  # ★ NUEVO: Alias para compatibilidad
            'comprador_id': self.comprador_id,
            
            # Tipo
            'tipo_direccion': self.tipo_direccion,
            'tipo': self.tipo_direccion,  # ★ NUEVO: Alias
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
    
    # ==========================================
    # ★ NUEVO: MÉTODOS DE CLASE
    # ==========================================
    @classmethod
    def crear_desde_checkout(cls, comprador_id, direccion_data):
        """
        Crea una dirección desde los datos del checkout.
        
        Args:
            comprador_id (int): ID del comprador
            direccion_data (dict): Datos de dirección del checkout
            
        Returns:
            DireccionComprador: Nueva dirección
        
        Ejemplo:
            direccion_data = {
                'direccion_completa': 'Calle 123 #45-67, Chapinero, Bogotá, Cundinamarca',
                'ciudad': 'Bogotá',
                'departamento': 'Cundinamarca',
                'tipo': 'residencia'
            }
        """
        # Parsear dirección completa si viene todo junto
        direccion_texto = direccion_data.get('direccion_completa', '')
        
        # Si viene dirección completa pero no los campos individuales,
        # intentar extraer ciudad y departamento del final
        if direccion_texto and not direccion_data.get('ciudad'):
            partes = direccion_texto.split(',')
            if len(partes) >= 2:
                # Última parte es departamento, penúltima es ciudad
                direccion_data['departamento'] = partes[-1].strip()
                direccion_data['ciudad'] = partes[-2].strip()
                # El resto es la dirección
                direccion_texto = ', '.join(partes[:-2])
        
        # Determinar si es primera dirección (para hacerla principal)
        es_primera = cls.query.filter_by(
            comprador_id=comprador_id,
            activo=True
        ).count() == 0
        
        direccion = cls(
            comprador_id=comprador_id,
            tipo_direccion=direccion_data.get('tipo', 'residencia'),
            direccion=direccion_texto or direccion_data.get('direccion', ''),
            ciudad=direccion_data.get('ciudad', ''),
            departamento=direccion_data.get('departamento', ''),
            barrio=direccion_data.get('barrio'),
            localidad=direccion_data.get('localidad'),
            complemento=direccion_data.get('complemento'),
            referencias=direccion_data.get('referencias'),
            codigo_postal=direccion_data.get('codigo_postal'),
            alias=direccion_data.get('alias'),
            nombre_establecimiento=direccion_data.get('nombre_establecimiento'),
            datos_especiales=direccion_data.get('datos_especiales', {}),
            latitud=direccion_data.get('latitud'),
            longitud=direccion_data.get('longitud'),
            es_principal=es_primera
        )
        
        return direccion
    
    @classmethod
    def get_tipos_direccion(cls):
        """Retorna los tipos de dirección disponibles."""
        return [
            {'value': k, **v}
            for k, v in cls.TIPOS_DIRECCION.items()
        ]
    
    @classmethod
    def validar_tipo(cls, tipo):
        """
        Valida que el tipo de dirección sea válido.
        
        Args:
            tipo (str): Tipo a validar
            
        Returns:
            bool: True si es válido
        """
        return tipo in cls.TIPOS_DIRECCION
    
    def __repr__(self):
        return f'<DireccionComprador {self.id_direccion}: {self.direccion_corta}>'


# ==========================================
# NOTAS DE USO
# ==========================================
"""
EJEMPLO DE USO EN CHECKOUT:

# Opción 1: Crear directamente
direccion = DireccionComprador(
    comprador_id=comprador.id,
    tipo='residencia',  # ← Acepta 'tipo' o 'tipo_direccion'
    direccion='Calle 123 #45-67',
    ciudad='Bogotá',
    departamento='Cundinamarca',
    barrio='Chapinero'
)

# Opción 2: Usar factory method (recomendado)
direccion = DireccionComprador.crear_desde_checkout(
    comprador_id=comprador.id,
    direccion_data={
        'direccion_completa': 'Calle 123 #45-67, Chapinero, Bogotá, Cundinamarca',
        'ciudad': 'Bogotá',
        'departamento': 'Cundinamarca',
        'tipo': 'residencia'
    }
)

db.session.add(direccion)
db.session.commit()

# Acceder al tipo
print(direccion.tipo)  # 'residencia' (funciona como alias)
print(direccion.tipo_direccion)  # 'residencia' (nombre real del campo)
"""