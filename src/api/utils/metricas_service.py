"""
═══════════════════════════════════════════════════════════════════════════════
TUKOMERCIO - SERVICIO DE MÉTRICAS
Fase 0.5 - Cálculo automático de métricas para negocios
═══════════════════════════════════════════════════════════════════════════════

Calcula métricas basadas en:
- Tabla `servicio` (contratos donde el negocio es contratado)
- Tabla `service_ratings` (calificaciones recibidas)
- Tabla `contratos_simplificados` (registros manuales de admin)
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
    Las métricas se calculan en tiempo real o se cachean.
    """
    
    @staticmethod
    def calcular_metricas_negocio(negocio_id: int) -> dict:
        """
        Calcula todas las métricas disponibles para un negocio.
        Combina datos de:
        - servicio (donde negocio_contratado_id = negocio_id)
        - contratos_simplificados (para datos de admin)
        
        Returns:
            dict con cada métrica y su valor/tendencia
        """
        try:
            metricas = {}
            
            # ═══════════════════════════════════════════════════════════
            # OBTENER ESTADÍSTICAS DE CONTRATOS (servicio)
            # ═══════════════════════════════════════════════════════════
            stats_servicio = MetricasService._get_stats_servicio(negocio_id)
            
            # ═══════════════════════════════════════════════════════════
            # OBTENER ESTADÍSTICAS DE CONTRATOS SIMPLIFICADOS (admin)
            # ═══════════════════════════════════════════════════════════
            stats_simplificados = MetricasService._get_stats_simplificados(negocio_id)
            
            # ═══════════════════════════════════════════════════════════
            # COMBINAR ESTADÍSTICAS
            # ═══════════════════════════════════════════════════════════
            total_contratos = stats_servicio['total'] + stats_simplificados['total']
            total_completados = stats_servicio['completados'] + stats_simplificados['completados']
            total_cancelados = stats_servicio['cancelados'] + stats_simplificados['cancelados']
            
            # Promedios de calificación (ponderados por cantidad)
            if stats_servicio['promedio_calificacion'] and stats_simplificados['promedio_calificacion']:
                promedio_cal = (
                    (stats_servicio['promedio_calificacion'] * stats_servicio['total_calificados'] +
                     stats_simplificados['promedio_calificacion'] * stats_simplificados['total_calificados'])
                    / (stats_servicio['total_calificados'] + stats_simplificados['total_calificados'])
                )
            elif stats_servicio['promedio_calificacion']:
                promedio_cal = stats_servicio['promedio_calificacion']
            elif stats_simplificados['promedio_calificacion']:
                promedio_cal = stats_simplificados['promedio_calificacion']
            else:
                promedio_cal = None
            
            cinco_estrellas = stats_servicio['cinco_estrellas'] + stats_simplificados['cinco_estrellas']
            entregas_anticipadas = stats_servicio['entregas_anticipadas'] + stats_simplificados['entregas_anticipadas']
            clientes_recurrentes = stats_servicio['clientes_recurrentes'] + stats_simplificados['clientes_recurrentes']
            
            # Tiempo de respuesta (promedio)
            tiempo_respuesta = stats_simplificados.get('promedio_respuesta')
            
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
            
            logger.info(f"✅ Métricas calculadas para negocio {negocio_id}: {total_contratos} contratos")
            
            return metricas
            
        except Exception as e:
            logger.error(f"❌ Error calculando métricas para negocio {negocio_id}: {e}")
            import traceback
            traceback.print_exc()
            return MetricasService._get_metricas_vacias()
    
    
    @staticmethod
    def _get_stats_servicio(negocio_id: int) -> dict:
        """Obtiene estadísticas de la tabla servicio"""
        try:
            result = db.session.execute(text("""
                SELECT 
                    COUNT(*) as total,
                    COUNT(*) FILTER (WHERE estado = 'completado') as completados,
                    COUNT(*) FILTER (WHERE estado = 'cancelado') as cancelados
                FROM servicio
                WHERE negocio_contratado_id = :negocio_id
            """), {'negocio_id': negocio_id})
            
            row = result.fetchone()
            
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
                'total': row[0] or 0,
                'completados': row[1] or 0,
                'cancelados': row[2] or 0,
                'promedio_calificacion': float(cal_row[0]) if cal_row and cal_row[0] else None,
                'cinco_estrellas': cal_row[1] or 0 if cal_row else 0,
                'total_calificados': cal_row[2] or 0 if cal_row else 0,
                'entregas_anticipadas': 0,  # TODO: calcular desde fechas
                'clientes_recurrentes': 0   # TODO: calcular desde id_contratante duplicados
            }
            
        except Exception as e:
            logger.error(f"Error obteniendo stats servicio: {e}")
            return {
                'total': 0, 'completados': 0, 'cancelados': 0,
                'promedio_calificacion': None, 'cinco_estrellas': 0,
                'total_calificados': 0, 'entregas_anticipadas': 0,
                'clientes_recurrentes': 0
            }
    
    
    @staticmethod
    def _get_stats_simplificados(negocio_id: int) -> dict:
        """Obtiene estadísticas de la tabla contratos_simplificados"""
        try:
            # Verificar si la tabla existe
            check = db.session.execute(text("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_name = 'contratos_simplificados'
                )
            """))
            if not check.fetchone()[0]:
                return {
                    'total': 0, 'completados': 0, 'cancelados': 0,
                    'promedio_calificacion': None, 'cinco_estrellas': 0,
                    'total_calificados': 0, 'entregas_anticipadas': 0,
                    'clientes_recurrentes': 0, 'promedio_respuesta': None
                }
            
            result = db.session.execute(text("""
                SELECT 
                    COUNT(*) as total,
                    COUNT(*) FILTER (WHERE estado = 'completado') as completados,
                    COUNT(*) FILTER (WHERE estado = 'cancelado') as cancelados,
                    AVG(calificacion) FILTER (WHERE calificacion IS NOT NULL) as promedio,
                    COUNT(*) FILTER (WHERE calificacion = 5) as cinco_estrellas,
                    COUNT(*) FILTER (WHERE calificacion IS NOT NULL) as total_calificados,
                    COUNT(*) FILTER (WHERE entrega_anticipada = true) as anticipadas,
                    COUNT(*) FILTER (WHERE cliente_recurrente = true) as recurrentes,
                    AVG(tiempo_respuesta_horas) FILTER (WHERE tiempo_respuesta_horas IS NOT NULL) as promedio_respuesta
                FROM contratos_simplificados
                WHERE negocio_id = :negocio_id
            """), {'negocio_id': negocio_id})
            
            row = result.fetchone()
            
            return {
                'total': row[0] or 0,
                'completados': row[1] or 0,
                'cancelados': row[2] or 0,
                'promedio_calificacion': float(row[3]) if row[3] else None,
                'cinco_estrellas': row[4] or 0,
                'total_calificados': row[5] or 0,
                'entregas_anticipadas': row[6] or 0,
                'clientes_recurrentes': row[7] or 0,
                'promedio_respuesta': float(row[8]) if row[8] else None
            }
            
        except Exception as e:
            logger.error(f"Error obteniendo stats simplificados: {e}")
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