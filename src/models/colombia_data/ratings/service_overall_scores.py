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



from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from src.models.database import db
import logging

# Configuración de logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
logger.debug("Modelo ServiceOverallScores cargado correctamente.")

class ServiceOverallScores(db.Model):
    __tablename__ = "service_overall_scores"

    # Identificador principal
    id_score = Column(Integer, primary_key=True)

    # Clave foránea relacionada con el servicio - Tabla 'servicio' (singular)
    servicio_id = Column(Integer, ForeignKey('servicio.id_servicio', ondelete='CASCADE'), nullable=False)

    # Puntajes
    puntaje_global_servicio = Column(Float, nullable=False)
    puntaje_global_usuario = Column(Float, nullable=True)
    puntaje_global_contratante = Column(Float, nullable=True)
    puntaje_global_contratado = Column(Float, nullable=True)

    # Promedios de duración
    promedio_duracion_horas = Column(Float, nullable=True)
    promedio_duracion_dias = Column(Float, nullable=True)
    promedio_duracion_meses = Column(Float, nullable=True)
    promedio_duracion_total = Column(Float, nullable=True)

    # Calificaciones más comunes
    calificativo_mas_recibido_como_contratante = Column(String(50), nullable=True)
    calificativo_mas_recibido_como_contratado = Column(String(50), nullable=True)

    # Totales
    veces_volverian_a_ser_contratados = Column(Integer, nullable=True)
    veces_volverian_a_ser_contratantes = Column(Integer, nullable=True)
    total_calificaciones_recibidas = Column(Integer, nullable=True)
    total_calificaciones_hechas = Column(Integer, nullable=True)

    # Métodos de conexión
    cantidad_veces_qr = Column(Integer, nullable=True)
    cantidad_veces_manual = Column(Integer, nullable=True)

    # Coincidencias en calificaciones como contratante
    coincidencias_calificacion_1_contratante = Column(Integer, nullable=True)
    coincidencias_calificacion_2_contratante = Column(Integer, nullable=True)
    coincidencias_calificacion_3_contratante = Column(Integer, nullable=True)
    porcentaje_coincidencia_contratante = Column(Float, nullable=True)
    peso_calificacion_contratante = Column(Float, nullable=True)

    # Coincidencias en calificaciones como contratado
    coincidencias_calificacion_1_contratado = Column(Integer, nullable=True)
    coincidencias_calificacion_2_contratado = Column(Integer, nullable=True)
    coincidencias_calificacion_3_contratado = Column(Integer, nullable=True)
    porcentaje_coincidencia_contratado = Column(Float, nullable=True)
    peso_calificacion_contratado = Column(Float, nullable=True)

    # Calificaciones positivas y negativas
    suma_calificaciones_positivas = Column(Integer, nullable=True)
    suma_calificaciones_negativas = Column(Integer, nullable=True)

    # Peso de las calificaciones según usuarios verificados
    peso_calificacion_verificado = Column(Float, nullable=True)
    peso_calificacion_no_verificado = Column(Float, nullable=True)

    # Cantidad de calificaciones
    numero_calificaciones = Column(Integer, nullable=False)

    # Fecha de última actualización
    fecha_ultima_actualizacion = Column(DateTime, onupdate=datetime.utcnow, nullable=True)

    # Relaciones
    ratings = relationship("ServiceRatings", back_populates="overall_score")
    servicio = relationship("Servicio", back_populates="overall_scores")

    def serialize(self):
        return {
            "id_score": self.id_score,
            "servicio_id": self.servicio_id,
            "puntaje_global_servicio": self.puntaje_global_servicio,
            "numero_calificaciones": self.numero_calificaciones,
            "ultima_actualizacion": self.fecha_ultima_actualizacion.isoformat() if self.fecha_ultima_actualizacion else None
        }

# Importación diferida para evitar ciclos
from src.models.servicio import Servicio
from src.models.colombia_data.ratings.service_ratings import ServiceRatings