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
═══════════════════════════════════════════════════════════════════════════════
TUKOMERCIO - SERVICIO DE MÉTRICAS v1.1
Fase 0.5 - Cálculo automático de métricas para negocios
═══════════════════════════════════════════════════════════════════════════════

ACTUALIZACIÓN v1.1 (Enero 30, 2026):
- ELIMINADO: Ya no lee de contratos_simplificados (tabla legacy)
- SOLO USA: servicio + service_ratings (datos reales)

Calcula métricas basadas en:
- Tabla `servicio` (contratos donde el negocio es contratado)
- Tabla `service_ratings` (calificaciones recibidas)
"""

from datetime import datetime, timedelta
from sqlalchemy import text, func, or_, and_
from src.models.database import db
import logging

logger = logging.getLogger(__name__)

# ═══════════════════════════════════════════════════════════════════════════════
# NOMBRES LEGIBLES DE MÉTRICAS
# ═══════════════════════════════════════════════════════════════════════════════
NOMBRES_METRICAS = {
    'tasa_exito': 'Tasa de éxito',
    'satisfaccion': 'Satisfacción',
    'clientes_recurrentes': 'Clientes recurrentes',
    'tiempo_respuesta': 'Tiempo de respuesta',
    'proyectos_completados': 'Proyectos completados',
    'años_experiencia': 'Años de experiencia',
    'mejor_precio': 'Mejor precio',
    'entregas_anticipadas': 'Entregas a tiempo'
}


class MetricasService:
    """
    Servicio para calcular métricas de un negocio.
    Las métricas se calculan en tiempo real desde:
    - servicio (donde negocio_contratado_id = negocio_id)
    - service_ratings (calificaciones del servicio)
    """
    
    @staticmethod
    def calcular_metricas_negocio(negocio_id: int) -> dict:
        """
        Calcula todas las métricas disponibles para un negocio.
        
        Returns:
            dict con cada métrica y su valor/tendencia
        """
        try:
            metricas = {}
            
            # ═══════════════════════════════════════════════════════════
            # OBTENER ESTADÍSTICAS DE CONTRATOS (servicio + service_ratings)
            # ═══════════════════════════════════════════════════════════
            stats = MetricasService._get_stats_servicio(negocio_id)
            
            total_contratos = stats['total']
            total_completados = stats['completados']
            total_cancelados = stats['cancelados']
            promedio_cal = stats['promedio_calificacion']
            cinco_estrellas = stats['cinco_estrellas']
            entregas_anticipadas = stats['entregas_anticipadas']
            clientes_recurrentes = stats['clientes_recurrentes']
            tiempo_respuesta = stats.get('promedio_respuesta')
            
            # ═══════════════════════════════════════════════════════════
            # CALCULAR MÉTRICAS FINALES
            # ═══════════════════════════════════════════════════════════
            
            # 1. TASA DE ÉXITO
            if total_contratos > 0:
                tasa = round((total_completados / total_contratos) * 100)
                metricas['tasa_exito'] = {
                    'valor': f"{tasa}%",
                    'valor_raw': tasa,
                    'tendencia': 'up' if tasa >= 90 else ('neutral' if tasa >= 70 else 'down')
                }
            else:
                metricas['tasa_exito'] = {'valor': '---', 'valor_raw': None, 'tendencia': 'neutral'}
            
            # 2. SATISFACCIÓN
            if promedio_cal:
                metricas['satisfaccion'] = {
                    'valor': f"{promedio_cal:.1f}★",
                    'valor_raw': round(promedio_cal, 2),
                    'tendencia': 'up' if promedio_cal >= 4.5 else ('neutral' if promedio_cal >= 4.0 else 'down')
                }
            else:
                metricas['satisfaccion'] = {'valor': '---', 'valor_raw': None, 'tendencia': 'neutral'}
            
            # 3. CLIENTES RECURRENTES
            if total_contratos > 0 and clientes_recurrentes > 0:
                pct_recurrentes = round((clientes_recurrentes / total_contratos) * 100)
                metricas['clientes_recurrentes'] = {
                    'valor': f"{pct_recurrentes}%",
                    'valor_raw': pct_recurrentes,
                    'tendencia': 'up' if pct_recurrentes >= 30 else 'neutral'
                }
            else:
                metricas['clientes_recurrentes'] = {'valor': '---', 'valor_raw': None, 'tendencia': 'neutral'}
            
            # 4. TIEMPO DE RESPUESTA
            if tiempo_respuesta:
                if tiempo_respuesta < 1:
                    valor_tiempo = "<1h"
                elif tiempo_respuesta < 24:
                    valor_tiempo = f"{int(tiempo_respuesta)}h"
                else:
                    valor_tiempo = f"{int(tiempo_respuesta/24)}d"
                
                metricas['tiempo_respuesta'] = {
                    'valor': valor_tiempo,
                    'valor_raw': tiempo_respuesta,
                    'tendencia': 'up' if tiempo_respuesta <= 2 else ('neutral' if tiempo_respuesta <= 12 else 'down')
                }
            else:
                metricas['tiempo_respuesta'] = {'valor': '---', 'valor_raw': None, 'tendencia': 'neutral'}
            
            # 5. PROYECTOS COMPLETADOS
            metricas['proyectos_completados'] = {
                'valor': str(total_completados) if total_completados > 0 else '---',
                'valor_raw': total_completados,
                'tendencia': 'up' if total_completados >= 10 else 'neutral'
            }
            
            # 6. AÑOS DE EXPERIENCIA
            años = MetricasService._get_años_experiencia(negocio_id)
            if años >= 1:
                metricas['años_experiencia'] = {
                    'valor': f"{años}+ años",
                    'valor_raw': años,
                    'tendencia': 'neutral'
                }
            else:
                dias = MetricasService._get_dias_activo(negocio_id)
                metricas['años_experiencia'] = {
                    'valor': f"{dias} días" if dias > 0 else '---',
                    'valor_raw': dias / 365 if dias else None,
                    'tendencia': 'neutral'
                }
            
            # 7. ENTREGAS A TIEMPO / ANTICIPADAS
            if total_completados > 0 and entregas_anticipadas > 0:
                pct_anticipadas = round((entregas_anticipadas / total_completados) * 100)
                metricas['entregas_anticipadas'] = {
                    'valor': f"{pct_anticipadas}%",
                    'valor_raw': pct_anticipadas,
                    'tendencia': 'up' if pct_anticipadas >= 80 else 'neutral'
                }
            else:
                metricas['entregas_anticipadas'] = {'valor': '---', 'valor_raw': None, 'tendencia': 'neutral'}
            
            # 8. MEJOR PRECIO (placeholder - requiere comparación con competencia)
            metricas['mejor_precio'] = {'valor': '---', 'valor_raw': None, 'tendencia': 'neutral'}
            
            logger.info(f"✅ Métricas calculadas para negocio {negocio_id}: {total_contratos} contratos, {total_completados} completados")
            
            return metricas
            
        except Exception as e:
            logger.error(f"❌ Error calculando métricas para negocio {negocio_id}: {e}")
            import traceback
            traceback.print_exc()
            db.session.rollback()
            return MetricasService._get_metricas_vacias()
    
    
    @staticmethod
    def _get_stats_servicio(negocio_id: int) -> dict:
        """
        Obtiene estadísticas de la tabla servicio + service_ratings.
        Esta es la ÚNICA fuente de datos para métricas.
        """
        try:
            # Estadísticas básicas de contratos
            result = db.session.execute(text("""
                SELECT 
                    COUNT(*) as total,
                    COUNT(*) FILTER (WHERE estado = 'completado') as completados,
                    COUNT(*) FILTER (WHERE estado = 'cancelado') as cancelados,
                    COUNT(DISTINCT id_contratante) FILTER (WHERE estado = 'completado') as clientes_unicos,
                    COUNT(*) FILTER (
                        WHERE estado = 'completado' 
                        AND fecha_fin IS NOT NULL 
                        AND fecha_fin <= fecha_inicio + INTERVAL '1 day'
                    ) as entregas_rapidas
                FROM servicio
                WHERE negocio_contratado_id = :negocio_id
            """), {'negocio_id': negocio_id})
            
            row = result.fetchone()
            total = row[0] or 0
            completados = row[1] or 0
            cancelados = row[2] or 0
            clientes_unicos = row[3] or 0
            entregas_rapidas = row[4] or 0
            
            # Calcular clientes recurrentes (contratantes que aparecen más de una vez)
            recurrentes_result = db.session.execute(text("""
                SELECT COUNT(*) FROM (
                    SELECT id_contratante
                    FROM servicio
                    WHERE negocio_contratado_id = :negocio_id
                      AND estado = 'completado'
                      AND id_contratante IS NOT NULL
                    GROUP BY id_contratante
                    HAVING COUNT(*) > 1
                ) as recurrentes
            """), {'negocio_id': negocio_id})
            clientes_recurrentes = recurrentes_result.fetchone()[0] or 0
            
            # Obtener calificaciones desde service_ratings
            cal_result = db.session.execute(text("""
                SELECT 
                    AVG(sr.promedio_global) as promedio,
                    COUNT(*) FILTER (WHERE sr.promedio_global >= 4.8) as cinco_estrellas,
                    COUNT(*) as total_calificados
                FROM service_ratings sr
                JOIN servicio s ON sr.servicio_id = s.id_servicio
                WHERE s.negocio_contratado_id = :negocio_id
                  AND sr.promedio_global IS NOT NULL
            """), {'negocio_id': negocio_id})
            
            cal_row = cal_result.fetchone()
            
            return {
                'total': total,
                'completados': completados,
                'cancelados': cancelados,
                'promedio_calificacion': float(cal_row[0]) if cal_row and cal_row[0] else None,
                'cinco_estrellas': cal_row[1] or 0 if cal_row else 0,
                'total_calificados': cal_row[2] or 0 if cal_row else 0,
                'entregas_anticipadas': entregas_rapidas,
                'clientes_recurrentes': clientes_recurrentes,
                'promedio_respuesta': None  # TODO: implementar si se agrega campo
            }
            
        except Exception as e:
            logger.error(f"Error obteniendo stats servicio: {e}")
            db.session.rollback()
            return {
                'total': 0, 'completados': 0, 'cancelados': 0,
                'promedio_calificacion': None, 'cinco_estrellas': 0,
                'total_calificados': 0, 'entregas_anticipadas': 0,
                'clientes_recurrentes': 0, 'promedio_respuesta': None
            }
    
    
    @staticmethod
    def _get_años_experiencia(negocio_id: int) -> int:
        """Calcula años desde la creación del negocio"""
        try:
            result = db.session.execute(text("""
                SELECT fecha_creacion FROM negocios WHERE id_negocio = :id
            """), {'id': negocio_id})
            row = result.fetchone()
            
            if row and row[0]:
                dias = (datetime.now().date() - row[0].date()).days
                return dias // 365
            return 0
        except:
            db.session.rollback()
            return 0
    
    
    @staticmethod
    def _get_dias_activo(negocio_id: int) -> int:
        """Calcula días desde la creación del negocio"""
        try:
            result = db.session.execute(text("""
                SELECT fecha_creacion FROM negocios WHERE id_negocio = :id
            """), {'id': negocio_id})
            row = result.fetchone()
            
            if row and row[0]:
                return (datetime.now().date() - row[0].date()).days
            return 0
        except:
            db.session.rollback()
            return 0
    
    
    @staticmethod
    def _get_metricas_vacias() -> dict:
        """Retorna estructura de métricas vacías"""
        return {
            'tasa_exito': {'valor': '---', 'valor_raw': None, 'tendencia': 'neutral'},
            'satisfaccion': {'valor': '---', 'valor_raw': None, 'tendencia': 'neutral'},
            'clientes_recurrentes': {'valor': '---', 'valor_raw': None, 'tendencia': 'neutral'},
            'tiempo_respuesta': {'valor': '---', 'valor_raw': None, 'tendencia': 'neutral'},
            'proyectos_completados': {'valor': '---', 'valor_raw': None, 'tendencia': 'neutral'},
            'años_experiencia': {'valor': '---', 'valor_raw': None, 'tendencia': 'neutral'},
            'entregas_anticipadas': {'valor': '---', 'valor_raw': None, 'tendencia': 'neutral'},
            'mejor_precio': {'valor': '---', 'valor_raw': None, 'tendencia': 'neutral'}
        }
    
    
    @staticmethod
    def get_metrica_para_video(negocio_id: int, tipo_metrica: str) -> dict:
        """
        Obtiene una métrica específica para mostrar en un video.
        
        Args:
            negocio_id: ID del negocio
            tipo_metrica: Tipo de métrica (tasa_exito, satisfaccion, etc.)
            
        Returns:
            dict con nombre, valor, tendencia
        """
        if not tipo_metrica or tipo_metrica == 'ninguna':
            return None
        
        metricas = MetricasService.calcular_metricas_negocio(negocio_id)
        
        if tipo_metrica in metricas:
            metrica = metricas[tipo_metrica]
            return {
                'nombre': NOMBRES_METRICAS.get(tipo_metrica, tipo_metrica),
                'valor': metrica['valor'],
                'tendencia': metrica['tendencia']
            }
        
        return {
            'nombre': NOMBRES_METRICAS.get(tipo_metrica, 'Métrica'),
            'valor': '---',
            'tendencia': 'neutral'
        }


# ═══════════════════════════════════════════════════════════════════════════════
# FUNCIÓN HELPER PARA IMPORTAR FÁCILMENTE
# ═══════════════════════════════════════════════════════════════════════════════
def calcular_metricas_negocio(negocio_id: int) -> dict:
    """Wrapper para usar sin instanciar la clase"""
    return MetricasService.calcular_metricas_negocio(negocio_id)


def get_metrica_para_video(negocio_id: int, tipo_metrica: str) -> dict:
    """Wrapper para usar sin instanciar la clase"""
    return MetricasService.get_metrica_para_video(negocio_id, tipo_metrica)