"""
Modelo Servicio (Contrato) - ACTUALIZADO con soporte B2B
TuKomercio Suite - BizScore

Cambios:
- Agregado soporte para negocios como contratante/contratado
- Agregado tipo_contrato (U2U, U2N, N2U, N2N)
- Agregado configuración de etapas por contrato
"""

from sqlalchemy import Column, Integer, String, Date, DateTime, ForeignKey, Boolean, Float, Text, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from src.models.database import db
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
logger.debug("Modelo Servicio v2.0 (con B2B) cargado correctamente.")


class Servicio(db.Model):
    __tablename__ = "servicio"

    # ═══════════════════════════════════════════════════════════
    # IDENTIFICACIÓN
    # ═══════════════════════════════════════════════════════════
    id_servicio = Column(Integer, primary_key=True)
    nombre_servicio = Column(String(200), nullable=True)
    descripcion = Column(Text, nullable=True)
    categoria = Column(Text, nullable=True)

    # ═══════════════════════════════════════════════════════════
    # FECHAS DEL CONTRATO
    # ═══════════════════════════════════════════════════════════
    fecha_solicitud = Column(Date, nullable=True)
    fecha_aceptacion = Column(Date, nullable=True)
    fecha_inicio = Column(Date, nullable=True)
    fecha_fin_estimada = Column(Date, nullable=True)
    fecha_fin = Column(Date, nullable=True)  # Fecha real de finalización

    # ═══════════════════════════════════════════════════════════
    # PARTES DEL CONTRATO - USUARIOS (existente)
    # ═══════════════════════════════════════════════════════════
    id_usuario = Column(Integer, ForeignKey('usuarios.id_usuario'), nullable=True)
    id_contratante = Column(Integer, ForeignKey('usuarios.id_usuario'), nullable=True)
    id_contratado = Column(Integer, ForeignKey('usuarios.id_usuario'), nullable=True)
    nombre_contratante = Column(String(200), nullable=True)

    # ═══════════════════════════════════════════════════════════
    # PARTES DEL CONTRATO - NEGOCIOS (NUEVO - B2B)
    # ═══════════════════════════════════════════════════════════
    negocio_contratante_id = Column(Integer, ForeignKey('negocios.id_negocio'), nullable=True)
    negocio_contratado_id = Column(Integer, ForeignKey('negocios.id_negocio'), nullable=True)
    
    # Tipo de contrato: U2U, U2N, N2U, N2N
    tipo_contrato = Column(String(10), nullable=True)
    # U2U = Usuario a Usuario
    # U2N = Usuario a Negocio (cliente compra en tienda)
    # N2U = Negocio a Usuario (empresa contrata freelancer)
    # N2N = Negocio a Negocio (B2B)

    # ═══════════════════════════════════════════════════════════
    # ESTADO Y PRECIO
    # ═══════════════════════════════════════════════════════════
    service_active = Column(Boolean, default=True)
    estado = Column(String(20), default='pendiente')
    # Estados: pendiente, activo, completado, cancelado, en_disputa
    
    precio = Column(Float, nullable=True)
    moneda = Column(String(3), default='COP')

    # ═══════════════════════════════════════════════════════════
    # CONFIGURACIÓN DE ETAPAS DE CALIFICACIÓN
    # ═══════════════════════════════════════════════════════════
    etapas_calificacion = Column(Integer, nullable=True)  # Legacy: número de etapas
    
    # NUEVO: Configuración detallada de etapas
    etapas_habilitadas = Column(JSON, default={
        "contratacion": True,
        "ejecucion": True,
        "finalizacion": True,
        "post_servicio": False
    })
    
    # Días después de finalizar para habilitar etapa 4
    dias_post_servicio = Column(Integer, default=7)
    
    # Si el contratado puede calificar al contratante
    calificacion_bidireccional = Column(Boolean, default=False)

    # ═══════════════════════════════════════════════════════════
    # CARACTERÍSTICAS DEL SERVICIO (existente)
    # ═══════════════════════════════════════════════════════════
    aditional_service = Column(String(234), nullable=True)
    viajar_dentro_pais = Column(Boolean, default=False)
    viajar_fuera_pais = Column(Boolean, default=False)
    domicilios = Column(Boolean, default=False)
    incluye_asesoria = Column(Boolean, default=False)
    requiere_presencia_cliente = Column(Boolean, default=False)
    experiencia_previa = Column(Boolean, default=False)
    facturacion_formal = Column(Boolean, default=False)
    modelos_negocio = Column(String(200), nullable=True)

    # ═══════════════════════════════════════════════════════════
    # QR DEL CONTRATO (NUEVO)
    # ═══════════════════════════════════════════════════════════
    qr_code = Column(String(100), unique=True, nullable=True)
    qr_data = Column(Text, nullable=True)  # Base64 del QR

    # ═══════════════════════════════════════════════════════════
    # UBICACIÓN
    # ═══════════════════════════════════════════════════════════
    ciudad_id = Column(Integer, ForeignKey('colombia.ciudad_id'), nullable=True)

    # ═══════════════════════════════════════════════════════════
    # TIMESTAMPS
    # ═══════════════════════════════════════════════════════════
    fecha_creacion = Column(DateTime, default=datetime.utcnow)
    fecha_actualizacion = Column(DateTime, onupdate=datetime.utcnow)

    # ═══════════════════════════════════════════════════════════
    # RELACIONES - USUARIOS
    # ═══════════════════════════════════════════════════════════
    contratante = relationship(
        "Usuario",
        foreign_keys=[id_contratante],
        back_populates="servicios_como_contratante"
    )
    contratado = relationship(
        "Usuario",
        foreign_keys=[id_contratado],
        back_populates="servicios_como_contratado"
    )
    
    # Relación muchos a muchos con usuarios
    usuarios = relationship(
        "Usuario",
        secondary="usuario_servicio",
        back_populates="servicios",
        lazy='select'
    )

    # ═══════════════════════════════════════════════════════════
    # RELACIONES - NEGOCIOS (NUEVO)
    # ═══════════════════════════════════════════════════════════
    negocio_contratante = relationship(
        "Negocio",
        foreign_keys=[negocio_contratante_id],
        backref="contratos_como_contratante"
    )
    negocio_contratado = relationship(
        "Negocio",
        foreign_keys=[negocio_contratado_id],
        backref="contratos_como_contratado"
    )

    # ═══════════════════════════════════════════════════════════
    # OTRAS RELACIONES
    # ═══════════════════════════════════════════════════════════
    etapas = relationship("Etapa", back_populates="servicio", cascade="all, delete-orphan")
    ciudad_rel = relationship("Colombia", backref="ciudad_servicios")
    calificaciones = relationship("ServiceRatings", back_populates="servicio")
    overall_scores = relationship("ServiceOverallScores", back_populates="servicio")

    # ═══════════════════════════════════════════════════════════
    # MÉTODOS HELPER
    # ═══════════════════════════════════════════════════════════
    def determinar_tipo_contrato(self):
        """Determina automáticamente el tipo de contrato basado en las partes"""
        tiene_usuario_contratante = self.id_contratante is not None
        tiene_negocio_contratante = self.negocio_contratante_id is not None
        tiene_usuario_contratado = self.id_contratado is not None
        tiene_negocio_contratado = self.negocio_contratado_id is not None
        
        if tiene_usuario_contratante and tiene_usuario_contratado:
            return 'U2U'
        elif tiene_usuario_contratante and tiene_negocio_contratado:
            return 'U2N'
        elif tiene_negocio_contratante and tiene_usuario_contratado:
            return 'N2U'
        elif tiene_negocio_contratante and tiene_negocio_contratado:
            return 'N2N'
        return None

    def etapa_habilitada(self, etapa: str) -> bool:
        """Verifica si una etapa está habilitada para este contrato"""
        if self.etapas_habilitadas:
            return self.etapas_habilitadas.get(etapa, False)
        return False

    # ═══════════════════════════════════════════════════════════
    # MÉTODOS CRUD
    # ═══════════════════════════════════════════════════════════
    @classmethod
    def leer(cls, session, id_servicio):
        return session.query(cls).filter_by(id_servicio=id_servicio).first()

    def actualizar(self, session, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)
        session.commit()

    @classmethod
    def eliminar(cls, session, id_servicio):
        servicio = cls.leer(session, id_servicio)
        if servicio:
            session.delete(servicio)
            session.commit()

    def serialize(self):
        return {
            "id_servicio": self.id_servicio,
            "nombre_servicio": self.nombre_servicio,
            "descripcion": self.descripcion,
            "categoria": self.categoria,
            "tipo_contrato": self.tipo_contrato,
            "estado": self.estado,
            "precio": self.precio,
            "moneda": self.moneda,
            "service_active": self.service_active,
            "etapas_habilitadas": self.etapas_habilitadas,
            "calificacion_bidireccional": self.calificacion_bidireccional,
            "fecha_inicio": self.fecha_inicio.isoformat() if self.fecha_inicio else None,
            "fecha_fin": self.fecha_fin.isoformat() if self.fecha_fin else None,
            # Partes
            "contratante": {
                "usuario_id": self.id_contratante,
                "negocio_id": self.negocio_contratante_id
            },
            "contratado": {
                "usuario_id": self.id_contratado,
                "negocio_id": self.negocio_contratado_id
            }
        }

    def serialize_completo(self):
        """Serialización completa con relaciones"""
        data = self.serialize()
        data.update({
            "contratante_info": self.contratante.serialize() if self.contratante else None,
            "contratado_info": self.contratado.serialize() if self.contratado else None,
            "negocio_contratante_info": self.negocio_contratante.serialize() if self.negocio_contratante else None,
            "negocio_contratado_info": self.negocio_contratado.serialize() if self.negocio_contratado else None,
        })
        return data