# ═══════════════════════════════════════════════════════════════════════════════
# MECALINK - Modelo de Mecánico a Domicilio
# Extensión de TuKomercio para servicios mecánicos
#
# © 2024-2026 Carlos Eduardo Huérfano Bermúdez. Todos los derechos reservados.
# ═══════════════════════════════════════════════════════════════════════════════

"""
MecaLink - Modelo de Mecánico a Domicilio

Este modelo extiende la funcionalidad de Negocio para mecánicos que ofrecen
servicios a domicilio. Se relaciona 1:1 con un negocio de categoría 'mecanico_domicilio'.

VERSIÓN 1.0 - Incluye:
- Zonas de cobertura
- Servicios ofrecidos (JSONB)
- Disponibilidad horaria
- Info de vehículo y herramientas
- Experiencia
- Sistema de calificaciones (preparado)
- Comisiones (preparado)
"""

import sqlalchemy as sa
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import JSONB, ARRAY
from src.models.database import db
from datetime import datetime


class MecanicoMecalink(db.Model):
    """
    Modelo para mecánicos a domicilio en la red MecaLink.
    Se relaciona 1:1 con un Negocio de tipo 'servicio' y categoría 'mecanico_domicilio'.
    """
    __tablename__ = 'mecanicos_mecalink'

    # ==========================================
    # IDENTIFICACIÓN
    # ==========================================
    id = sa.Column(sa.Integer, primary_key=True)
    
    # Relación con Negocio (1:1)
    negocio_id = sa.Column(
        sa.Integer,
        sa.ForeignKey('negocios.id_negocio', ondelete='CASCADE'),
        nullable=False,
        unique=True,  # 1:1 con negocio
        index=True
    )
    
    # ==========================================
    # COBERTURA GEOGRÁFICA
    # ==========================================
    # Texto libre de zonas (para mostrar)
    zonas_texto = sa.Column(sa.Text, nullable=True)
    
    # Array de zonas normalizadas (para búsquedas)
    # Ejemplo: ['usme', 'kennedy', 'bosa']
    zonas_array = sa.Column(ARRAY(sa.String(100)), default=[], nullable=True)
    
    # Ciudad principal de operación
    ciudad_operacion = sa.Column(sa.String(100), nullable=True, index=True)
    
    # ==========================================
    # SERVICIOS OFRECIDOS
    # ==========================================
    # Lista de servicios que ofrece
    # Ejemplo: ['cambio_aceite', 'diagnostico_scanner', 'revision_electrica']
    servicios = sa.Column(ARRAY(sa.String(50)), default=[], nullable=True)
    
    # Precios por servicio (opcional)
    # Formato JSONB: {
    #   "cambio_aceite": 85000,
    #   "diagnostico_scanner": 40000,
    #   ...
    # }
    precios_servicios = sa.Column(JSONB, default={}, nullable=True)
    
    # ==========================================
    # DISPONIBILIDAD
    # ==========================================
    disponibilidad_texto = sa.Column(sa.String(255), nullable=True)
    
    # Formato JSONB detallado (opcional para futuro):
    # {
    #   "lunes": {"desde": "08:00", "hasta": "18:00"},
    #   "sabado": {"desde": "08:00", "hasta": "12:00"},
    #   ...
    # }
    disponibilidad_detalle = sa.Column(JSONB, default={}, nullable=True)
    
    # ==========================================
    # CAPACIDADES
    # ==========================================
    tiene_vehiculo = sa.Column(sa.Boolean, default=False, nullable=False)
    tipo_vehiculo = sa.Column(sa.String(50), nullable=True)  # 'moto', 'carro', 'ambos'
    
    tiene_herramientas = sa.Column(sa.String(20), default='algunas', nullable=True)
    # Valores: 'completas', 'algunas', 'no'
    
    # Detalle de herramientas (opcional)
    herramientas_detalle = sa.Column(JSONB, default={}, nullable=True)
    
    # ==========================================
    # EXPERIENCIA Y PERFIL
    # ==========================================
    experiencia = sa.Column(sa.String(20), nullable=True)
    # Valores: 'menos_1', '1_3', '3_5', '5_10', 'mas_10'
    
    experiencia_anios = sa.Column(sa.Integer, nullable=True)  # Número exacto si lo dan
    
    especialidades = sa.Column(ARRAY(sa.String(100)), default=[], nullable=True)
    # Ej: ['motos', 'carros', 'diesel', 'electricos']
    
    certificaciones = sa.Column(sa.Text, nullable=True)
    # Texto libre para certificaciones SENA, etc.
    
    # ==========================================
    # SISTEMA DE CALIFICACIONES (MecaLink)
    # ==========================================
    calificacion_promedio = sa.Column(sa.Numeric(3, 2), default=0.00, nullable=False)
    total_calificaciones = sa.Column(sa.Integer, default=0, nullable=False)
    total_servicios = sa.Column(sa.Integer, default=0, nullable=False)
    
    # Desglose de calificaciones
    # {
    #   "puntualidad": 4.5,
    #   "calidad": 4.8,
    #   "precio": 4.2,
    #   "comunicacion": 4.6
    # }
    calificaciones_desglose = sa.Column(JSONB, default={}, nullable=True)
    
    # ==========================================
    # ESTADO EN MECALINK
    # ==========================================
    estado = sa.Column(sa.String(20), default='pendiente', nullable=False, index=True)
    # Valores: 'pendiente', 'activo', 'suspendido', 'inactivo'
    
    verificado_mecalink = sa.Column(sa.Boolean, default=False, nullable=False)
    fecha_verificacion = sa.Column(sa.DateTime, nullable=True)
    
    nivel = sa.Column(sa.String(20), default='nuevo', nullable=False)
    # Valores: 'nuevo', 'activo', 'experto', 'elite'
    # nuevo: 0-10 servicios
    # activo: 11-50 servicios
    # experto: 51-200 servicios
    # elite: 200+ servicios
    
    # ==========================================
    # COMISIONES (preparado para futuro)
    # ==========================================
    comision_porcentaje = sa.Column(sa.Numeric(5, 2), default=10.00, nullable=False)
    # Por defecto 10%
    
    total_comisiones_pagadas = sa.Column(sa.Numeric(12, 2), default=0.00, nullable=False)
    total_ingresos_generados = sa.Column(sa.Numeric(12, 2), default=0.00, nullable=False)
    
    # ==========================================
    # METADATA
    # ==========================================
    fecha_registro = sa.Column(sa.DateTime, default=datetime.utcnow, nullable=False)
    fecha_actualizacion = sa.Column(sa.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    notas_admin = sa.Column(sa.Text, nullable=True)  # Notas internas
    
    # ==========================================
    # RELACIONES
    # ==========================================
    negocio = relationship("Negocio", foreign_keys=[negocio_id], backref="mecalink_perfil")
    
    # ==========================================
    # CONSTRUCTOR
    # ==========================================
    
    def __init__(self, negocio_id, **kwargs):
        self.negocio_id = negocio_id
        
        # Cobertura
        self.zonas_texto = kwargs.get('zonas_texto', kwargs.get('zonas'))
        self.zonas_array = self._normalizar_zonas(self.zonas_texto)
        self.ciudad_operacion = kwargs.get('ciudad_operacion')
        
        # Servicios
        self.servicios = kwargs.get('servicios', [])
        self.precios_servicios = kwargs.get('precios_servicios', {})
        
        # Disponibilidad
        self.disponibilidad_texto = kwargs.get('disponibilidad_texto', kwargs.get('disponibilidad'))
        self.disponibilidad_detalle = kwargs.get('disponibilidad_detalle', {})
        
        # Capacidades
        self.tiene_vehiculo = kwargs.get('tiene_vehiculo') == 'si' or kwargs.get('tiene_vehiculo') == True
        self.tipo_vehiculo = kwargs.get('tipo_vehiculo')
        self.tiene_herramientas = kwargs.get('tiene_herramientas', 'algunas')
        self.herramientas_detalle = kwargs.get('herramientas_detalle', {})
        
        # Experiencia
        self.experiencia = kwargs.get('experiencia')
        self.experiencia_anios = self._calcular_anios(self.experiencia)
        self.especialidades = kwargs.get('especialidades', [])
        self.certificaciones = kwargs.get('certificaciones')
        
        # Estado inicial
        self.estado = 'pendiente'
        self.verificado_mecalink = False
        self.nivel = 'nuevo'
        self.comision_porcentaje = kwargs.get('comision_porcentaje', 10.00)
    
    # ==========================================
    # MÉTODOS PRIVADOS
    # ==========================================
    
    def _normalizar_zonas(self, zonas_texto):
        """Convierte texto de zonas a array normalizado para búsquedas."""
        if not zonas_texto:
            return []
        
        import re
        # Separar por comas, puntos, "y", etc.
        zonas = re.split(r'[,;.\n]+|\s+y\s+', zonas_texto.lower())
        # Limpiar y normalizar
        zonas_limpias = []
        for z in zonas:
            z = z.strip()
            # Remover tildes
            replacements = {'á': 'a', 'é': 'e', 'í': 'i', 'ó': 'o', 'ú': 'u', 'ñ': 'n'}
            for old, new in replacements.items():
                z = z.replace(old, new)
            if z and len(z) > 2:
                zonas_limpias.append(z)
        
        return list(set(zonas_limpias))  # Eliminar duplicados
    
    def _calcular_anios(self, experiencia_str):
        """Convierte string de experiencia a número aproximado de años."""
        if not experiencia_str:
            return None
        
        mapping = {
            'menos_1': 0,
            '1_3': 2,
            '3_5': 4,
            '5_10': 7,
            'mas_10': 12
        }
        return mapping.get(experiencia_str)
    
    # ==========================================
    # MÉTODOS DE NIVEL
    # ==========================================
    
    def actualizar_nivel(self):
        """Actualiza el nivel basado en servicios completados."""
        if self.total_servicios >= 200:
            self.nivel = 'elite'
        elif self.total_servicios >= 51:
            self.nivel = 'experto'
        elif self.total_servicios >= 11:
            self.nivel = 'activo'
        else:
            self.nivel = 'nuevo'
        return self.nivel
    
    def get_nivel_badge(self):
        """Retorna emoji y nombre del nivel."""
        badges = {
            'nuevo': ('⭐', 'Nuevo'),
            'activo': ('🔧', 'Activo'),
            'experto': ('🏆', 'Experto'),
            'elite': ('👑', 'Élite')
        }
        return badges.get(self.nivel, ('⭐', 'Nuevo'))
    
    # ==========================================
    # MÉTODOS DE SERVICIOS
    # ==========================================
    
    def ofrece_servicio(self, servicio):
        """Verifica si el mecánico ofrece un servicio específico."""
        return servicio in (self.servicios or [])
    
    def get_precio_servicio(self, servicio):
        """Obtiene el precio de un servicio específico."""
        if not self.precios_servicios:
            return None
        return self.precios_servicios.get(servicio)
    
    def get_servicios_con_precios(self):
        """Retorna lista de servicios con sus precios."""
        nombres_servicios = {
            'cambio_aceite': 'Cambio de aceite',
            'diagnostico_scanner': 'Diagnóstico con escáner',
            'revision_electrica': 'Revisión eléctrica',
            'cambio_bateria': 'Cambio de batería',
            'cambio_pastillas': 'Cambio pastillas de freno',
            'revision_previaje': 'Revisión pre-viaje',
            'auxilio_varamiento': 'Auxilio por varamiento',
            'otro_servicio': 'Otros servicios'
        }
        
        resultado = []
        for servicio in (self.servicios or []):
            resultado.append({
                'codigo': servicio,
                'nombre': nombres_servicios.get(servicio, servicio),
                'precio': self.get_precio_servicio(servicio)
            })
        return resultado
    
    # ==========================================
    # MÉTODOS DE COBERTURA
    # ==========================================
    
    def cubre_zona(self, zona):
        """Verifica si el mecánico cubre una zona específica."""
        if not zona or not self.zonas_array:
            return False
        
        zona_normalizada = zona.lower().strip()
        # Remover tildes
        replacements = {'á': 'a', 'é': 'e', 'í': 'i', 'ó': 'o', 'ú': 'u', 'ñ': 'n'}
        for old, new in replacements.items():
            zona_normalizada = zona_normalizada.replace(old, new)
        
        # Buscar coincidencia parcial
        for z in self.zonas_array:
            if zona_normalizada in z or z in zona_normalizada:
                return True
        return False
    
    # ==========================================
    # MÉTODOS DE CALIFICACIÓN
    # ==========================================
    
    def agregar_calificacion(self, calificacion, desglose=None):
        """
        Agrega una nueva calificación y recalcula el promedio.
        
        Args:
            calificacion (float): Calificación general (1-5)
            desglose (dict): Calificaciones específicas (opcional)
        """
        # Actualizar promedio
        total_actual = float(self.calificacion_promedio) * self.total_calificaciones
        self.total_calificaciones += 1
        self.calificacion_promedio = (total_actual + calificacion) / self.total_calificaciones
        
        # Actualizar desglose si se proporciona
        if desglose and isinstance(desglose, dict):
            if not self.calificaciones_desglose:
                self.calificaciones_desglose = {}
            
            for key, valor in desglose.items():
                if key in self.calificaciones_desglose:
                    # Promedio móvil
                    actual = self.calificaciones_desglose[key]
                    self.calificaciones_desglose[key] = (actual + valor) / 2
                else:
                    self.calificaciones_desglose[key] = valor
    
    def registrar_servicio_completado(self, monto=0):
        """Registra un servicio completado y actualiza estadísticas."""
        self.total_servicios += 1
        self.total_ingresos_generados += monto
        self.actualizar_nivel()
    
    # ==========================================
    # MÉTODOS DE ESTADO
    # ==========================================
    
    def activar(self):
        """Activa el mecánico en la red MecaLink."""
        self.estado = 'activo'
    
    def suspender(self, motivo=None):
        """Suspende temporalmente al mecánico."""
        self.estado = 'suspendido'
        if motivo:
            self.notas_admin = f"{self.notas_admin or ''}\n[SUSPENDIDO] {datetime.utcnow()}: {motivo}"
    
    def verificar(self):
        """Marca al mecánico como verificado."""
        self.verificado_mecalink = True
        self.fecha_verificacion = datetime.utcnow()
        if self.estado == 'pendiente':
            self.estado = 'activo'
    
    # ==========================================
    # SERIALIZACIÓN
    # ==========================================
    
    def to_dict(self, include_negocio=False):
        """Convierte el perfil MecaLink a diccionario."""
        nivel_emoji, nivel_nombre = self.get_nivel_badge()
        
        data = {
            "id": self.id,
            "negocio_id": self.negocio_id,
            
            # Cobertura
            "zonas_texto": self.zonas_texto,
            "zonas_array": self.zonas_array or [],
            "ciudad_operacion": self.ciudad_operacion,
            
            # Servicios
            "servicios": self.servicios or [],
            "servicios_detalle": self.get_servicios_con_precios(),
            "precios_servicios": self.precios_servicios or {},
            
            # Disponibilidad
            "disponibilidad_texto": self.disponibilidad_texto,
            "disponibilidad_detalle": self.disponibilidad_detalle or {},
            
            # Capacidades
            "tiene_vehiculo": self.tiene_vehiculo,
            "tipo_vehiculo": self.tipo_vehiculo,
            "tiene_herramientas": self.tiene_herramientas,
            
            # Experiencia
            "experiencia": self.experiencia,
            "experiencia_anios": self.experiencia_anios,
            "especialidades": self.especialidades or [],
            "certificaciones": self.certificaciones,
            
            # Calificaciones
            "calificacion_promedio": float(self.calificacion_promedio),
            "total_calificaciones": self.total_calificaciones,
            "total_servicios": self.total_servicios,
            "calificaciones_desglose": self.calificaciones_desglose or {},
            
            # Estado MecaLink
            "estado": self.estado,
            "verificado_mecalink": self.verificado_mecalink,
            "fecha_verificacion": self.fecha_verificacion.isoformat() if self.fecha_verificacion else None,
            "nivel": self.nivel,
            "nivel_emoji": nivel_emoji,
            "nivel_nombre": nivel_nombre,
            
            # Comisiones
            "comision_porcentaje": float(self.comision_porcentaje),
            "total_comisiones_pagadas": float(self.total_comisiones_pagadas),
            "total_ingresos_generados": float(self.total_ingresos_generados),
            
            # Metadata
            "fecha_registro": self.fecha_registro.isoformat() if self.fecha_registro else None,
            "fecha_actualizacion": self.fecha_actualizacion.isoformat() if self.fecha_actualizacion else None
        }
        
        # Incluir datos del negocio si se solicita
        if include_negocio and self.negocio:
            data["negocio"] = {
                "id": self.negocio.id_negocio,
                "nombre": self.negocio.nombre_negocio,
                "telefono": self.negocio.telefono,
                "whatsapp": self.negocio.whatsapp,
                "ciudad": self.negocio.ciudad,
                "logo_url": self.negocio.logo_url,
                "slug": self.negocio.slug
            }
        
        return data
    
    def to_dict_publico(self):
        """Versión pública del perfil (sin datos sensibles)."""
        nivel_emoji, nivel_nombre = self.get_nivel_badge()
        
        return {
            "id": self.id,
            "nombre": self.negocio.nombre_negocio if self.negocio else None,
            "ciudad": self.ciudad_operacion,
            "zonas": self.zonas_texto,
            "servicios": self.get_servicios_con_precios(),
            "disponibilidad": self.disponibilidad_texto,
            "calificacion": float(self.calificacion_promedio),
            "total_servicios": self.total_servicios,
            "nivel": nivel_nombre,
            "nivel_emoji": nivel_emoji,
            "verificado": self.verificado_mecalink,
            "tiene_vehiculo": self.tiene_vehiculo,
            "experiencia": self.experiencia,
            "whatsapp_link": self.negocio.get_whatsapp_link() if self.negocio else None,
            "logo_url": self.negocio.logo_url if self.negocio else None
        }
    
    def __repr__(self):
        return f'<MecanicoMecalink {self.id} - Negocio: {self.negocio_id}>'
    
    def __str__(self):
        if self.negocio:
            return f"MecaLink: {self.negocio.nombre_negocio}"
        return f"MecaLink #{self.id}"


# ═══════════════════════════════════════════════════════════════════════════════
# ÍNDICES ADICIONALES PARA BÚSQUEDAS EFICIENTES
# ═══════════════════════════════════════════════════════════════════════════════

# Crear índice GIN para búsqueda en arrays de zonas
# Ejecutar en migración:
# CREATE INDEX idx_mecanicos_zonas ON mecanicos_mecalink USING GIN (zonas_array);
# CREATE INDEX idx_mecanicos_servicios ON mecanicos_mecalink USING GIN (servicios);