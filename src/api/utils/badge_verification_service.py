"""
═══════════════════════════════════════════════════════════════════════════════
TUKOMERCIO - BadgeVerificationService v1.1
Verificación y asignación automática de badges para negocios
═══════════════════════════════════════════════════════════════════════════════

USO:
    from src.api.utils.badge_verification_service import BadgeVerificationService
    
    # Verificar todos los badges de un negocio
    resultado = BadgeVerificationService.verificar_badges(negocio_id=4)
    # → {'verificados': 21, 'nuevos': ['perfeccionista', 'veterano'], 'total_obtenidos': 10}
    
    # Llamar después de:
    # - Completar un servicio
    # - Recibir una calificación
    # - Subir un video

CRITERIOS SOPORTADOS:
    ✅ contratos_completados  → COUNT servicio completados
    ✅ calificaciones_5       → COUNT ratings con promedio >= 4.8
    ✅ trabajos_perfectos     → COUNT ratings con promedio >= 4.8
    ✅ entregas_anticipadas   → COUNT entregas dentro de plazo
    ✅ clientes_recurrentes   → COUNT clientes con >1 contrato
    ✅ contratos_sin_disputa  → COUNT completados sin disputa
    ✅ videos_subidos         → COUNT videos del negocio
    ✅ verificado             → negocio.verificado
    ✅ cuenta_creada          → Siempre 1 (badge de bienvenida)
    ✅ perfil_completo        → logo + descripcion + whatsapp
    ✅ tiene_direccion        → Tiene dirección
    ✅ tiene_whatsapp         → Tiene WhatsApp
    ⚠️ tiempo_respuesta_hrs  → Pendiente (no hay campo aún)
    ⚠️ percentil             → Pendiente (requiere comparación entre negocios)
"""

from datetime import datetime
from sqlalchemy import text
from src.models.database import db
import logging

logger = logging.getLogger(__name__)


class BadgeVerificationService:
    """
    Servicio que verifica si un negocio cumple los criterios para cada badge
    y asigna automáticamente los que correspondan.
    """
    
    @staticmethod
    def verificar_badges(negocio_id: int) -> dict:
        """
        Verifica TODOS los badges del catálogo contra las métricas del negocio.
        Asigna automáticamente los badges que cumplan criterios.
        
        Args:
            negocio_id: ID del negocio a verificar
            
        Returns:
            dict con resultados: verificados, nuevos badges, errores
        """
        try:
            logger.info(f"🔍 Verificando badges para negocio {negocio_id}")
            
            # 1. Obtener métricas actuales del negocio
            metricas = BadgeVerificationService._calcular_metricas_para_badges(negocio_id)
            logger.info(f"   📊 Métricas: {metricas}")
            
            # 2. Obtener catálogo de badges activos
            badges_catalogo = BadgeVerificationService._get_catalogo_badges()
            
            # 3. Obtener badges que ya tiene el negocio
            badges_obtenidos = BadgeVerificationService._get_badges_obtenidos(negocio_id)
            
            # 4. Verificar cada badge
            nuevos = []
            errores = []
            
            for badge in badges_catalogo:
                badge_id = badge['id']
                codigo = badge['codigo']
                criterio_tipo = badge['criterio_tipo']
                criterio_valor = badge['criterio_valor']
                criterio_operador = badge['criterio_operador']
                
                # Skip si ya lo tiene
                if badge_id in badges_obtenidos:
                    continue
                
                # Obtener valor actual de la métrica
                valor_actual = metricas.get(criterio_tipo)
                
                if valor_actual is None:
                    # Criterio no soportado aún (tiempo_respuesta_hrs, percentil)
                    continue
                
                # Evaluar si cumple el criterio
                cumple = BadgeVerificationService._evaluar_criterio(
                    valor_actual, criterio_operador, criterio_valor
                )
                
                if cumple:
                    # Asignar badge
                    exito = BadgeVerificationService._asignar_badge(
                        negocio_id, badge_id, valor_actual, codigo
                    )
                    if exito:
                        nuevos.append({
                            'codigo': codigo,
                            'nombre': badge['nombre'],
                            'nivel': badge['nivel'],
                            'valor_actual': valor_actual,
                            'criterio': f"{criterio_tipo} {criterio_operador} {criterio_valor}"
                        })
                        logger.info(f"   🏆 NUEVO badge: {codigo} (valor: {valor_actual} {criterio_operador} {criterio_valor})")
                    else:
                        errores.append(codigo)
            
            resultado = {
                'negocio_id': negocio_id,
                'verificados': len(badges_catalogo),
                'ya_obtenidos': len(badges_obtenidos),
                'nuevos': nuevos,
                'total_nuevos': len(nuevos),
                'total_obtenidos': len(badges_obtenidos) + len(nuevos),
                'errores': errores
            }
            
            if nuevos:
                logger.info(f"   ✅ {len(nuevos)} badges nuevos asignados a negocio {negocio_id}")
            else:
                logger.info(f"   ℹ️ Sin badges nuevos para negocio {negocio_id}")
            
            return resultado
            
        except Exception as e:
            logger.error(f"❌ Error verificando badges para negocio {negocio_id}: {e}")
            import traceback
            traceback.print_exc()
            db.session.rollback()
            return {
                'negocio_id': negocio_id,
                'error': str(e),
                'verificados': 0,
                'nuevos': [],
                'total_nuevos': 0
            }
    
    
    @staticmethod
    def _calcular_metricas_para_badges(negocio_id: int) -> dict:
        """
        Calcula todas las métricas necesarias para evaluar badges.
        Retorna un dict con cada criterio_tipo y su valor actual.
        """
        metricas = {}
        
        try:
            # ═══════════════════════════════════════════
            # CONTRATOS COMPLETADOS
            # ═══════════════════════════════════════════
            result = db.session.execute(text("""
                SELECT COUNT(*) 
                FROM servicio 
                WHERE negocio_contratado_id = :nid 
                  AND estado = 'completado'
            """), {'nid': negocio_id})
            metricas['contratos_completados'] = result.fetchone()[0] or 0
            
            # ═══════════════════════════════════════════
            # CALIFICACIONES DE 5 ESTRELLAS (promedio >= 4.8)
            # ═══════════════════════════════════════════
            result = db.session.execute(text("""
                SELECT COUNT(*) 
                FROM service_ratings sr
                JOIN servicio s ON sr.servicio_id = s.id_servicio
                WHERE s.negocio_contratado_id = :nid
                  AND sr.promedio_global >= 4.8
            """), {'nid': negocio_id})
            cinco_estrellas = result.fetchone()[0] or 0
            metricas['calificaciones_5'] = cinco_estrellas
            metricas['trabajos_perfectos'] = cinco_estrellas  # Mismo criterio
            
            # ═══════════════════════════════════════════
            # ENTREGAS ANTICIPADAS (dentro de plazo)
            # ═══════════════════════════════════════════
            result = db.session.execute(text("""
                SELECT COUNT(*) 
                FROM servicio 
                WHERE negocio_contratado_id = :nid
                  AND estado = 'completado'
                  AND fecha_fin IS NOT NULL
                  AND fecha_fin <= fecha_inicio + INTERVAL '1 day'
            """), {'nid': negocio_id})
            metricas['entregas_anticipadas'] = result.fetchone()[0] or 0
            
            # ═══════════════════════════════════════════
            # CLIENTES RECURRENTES (>1 contrato)
            # ═══════════════════════════════════════════
            result = db.session.execute(text("""
                SELECT COUNT(*) FROM (
                    SELECT id_contratante
                    FROM servicio
                    WHERE negocio_contratado_id = :nid
                      AND estado = 'completado'
                      AND id_contratante IS NOT NULL
                    GROUP BY id_contratante
                    HAVING COUNT(*) > 1
                ) as recurrentes
            """), {'nid': negocio_id})
            metricas['clientes_recurrentes'] = result.fetchone()[0] or 0
            
            # ═══════════════════════════════════════════
            # CONTRATOS SIN DISPUTA
            # ═══════════════════════════════════════════
            result = db.session.execute(text("""
                SELECT COUNT(*) 
                FROM servicio 
                WHERE negocio_contratado_id = :nid
                  AND estado = 'completado'
                  AND (disputa IS NULL OR disputa = false)
            """), {'nid': negocio_id})
            metricas['contratos_sin_disputa'] = result.fetchone()[0] or 0
            
            # ═══════════════════════════════════════════
            # VIDEOS SUBIDOS
            # ═══════════════════════════════════════════
            try:
                result = db.session.execute(text("""
                    SELECT COUNT(*) 
                    FROM negocio_videos 
                    WHERE negocio_id = :nid
                      AND visible = true
                """), {'nid': negocio_id})
                metricas['videos_subidos'] = result.fetchone()[0] or 0
            except Exception:
                metricas['videos_subidos'] = 0
            
            # ═══════════════════════════════════════════
            # VERIFICADO
            # ═══════════════════════════════════════════
            try:
                result = db.session.execute(text("""
                    SELECT verificado 
                    FROM negocios 
                    WHERE id_negocio = :nid
                """), {'nid': negocio_id})
                row = result.fetchone()
                metricas['verificado'] = 1 if (row and row[0]) else 0
            except Exception:
                metricas['verificado'] = 0
            
            # ═══════════════════════════════════════════
            # BADGES BÁSICOS (NO dependen de ventas)
            # ═══════════════════════════════════════════
            
            # Cuenta creada (siempre 1 si existe el negocio)
            metricas['cuenta_creada'] = 1
            
            # Perfil completo (tiene logo + descripción + whatsapp)
            try:
                result = db.session.execute(text("""
                    SELECT 
                        CASE WHEN logo_url IS NOT NULL AND logo_url != '' THEN 1 ELSE 0 END +
                        CASE WHEN descripcion IS NOT NULL AND descripcion != '' THEN 1 ELSE 0 END +
                        CASE WHEN whatsapp IS NOT NULL AND whatsapp != '' THEN 1 ELSE 0 END
                        as campos_completos
                    FROM negocios 
                    WHERE id_negocio = :nid
                """), {'nid': negocio_id})
                row = result.fetchone()
                # Perfil completo = 3 campos llenos (logo + descripcion + whatsapp)
                metricas['perfil_completo'] = 1 if (row and row[0] >= 3) else 0
            except Exception:
                metricas['perfil_completo'] = 0
            
            # Tiene dirección
            try:
                result = db.session.execute(text("""
                    SELECT CASE WHEN direccion IS NOT NULL AND direccion != '' THEN 1 ELSE 0 END
                    FROM negocios 
                    WHERE id_negocio = :nid
                """), {'nid': negocio_id})
                row = result.fetchone()
                metricas['tiene_direccion'] = row[0] if row else 0
            except Exception:
                metricas['tiene_direccion'] = 0
            
            # Tiene WhatsApp
            try:
                result = db.session.execute(text("""
                    SELECT CASE WHEN whatsapp IS NOT NULL AND whatsapp != '' THEN 1 ELSE 0 END
                    FROM negocios 
                    WHERE id_negocio = :nid
                """), {'nid': negocio_id})
                row = result.fetchone()
                metricas['tiene_whatsapp'] = row[0] if row else 0
            except Exception:
                metricas['tiene_whatsapp'] = 0
            
            # ═══════════════════════════════════════════
            # NO SOPORTADOS AÚN (retorna None → se skipean)
            # ═══════════════════════════════════════════
            # metricas['tiempo_respuesta_hrs'] = None
            # metricas['percentil'] = None
            
        except Exception as e:
            logger.error(f"Error calculando métricas para badges: {e}")
            db.session.rollback()
        
        return metricas
    
    
    @staticmethod
    def _get_catalogo_badges() -> list:
        """Obtiene todos los badges activos del catálogo."""
        try:
            result = db.session.execute(text("""
                SELECT id, codigo, nombre, criterio_tipo, criterio_valor, 
                       criterio_operador, nivel, max_otorgamientos
                FROM negocio_badges 
                WHERE activo = true
                ORDER BY id
            """))
            
            badges = []
            for row in result.fetchall():
                badges.append({
                    'id': row[0],
                    'codigo': row[1],
                    'nombre': row[2],
                    'criterio_tipo': row[3],
                    'criterio_valor': float(row[4]) if row[4] else 0,
                    'criterio_operador': row[5] or '>=',
                    'nivel': row[6] or 1,
                    'max_otorgamientos': row[7]
                })
            
            return badges
            
        except Exception as e:
            logger.error(f"Error obteniendo catálogo de badges: {e}")
            return []
    
    
    @staticmethod
    def _get_badges_obtenidos(negocio_id: int) -> set:
        """Obtiene IDs de badges que el negocio ya tiene."""
        try:
            result = db.session.execute(text("""
                SELECT badge_id 
                FROM negocio_badges_obtenidos 
                WHERE negocio_id = :nid 
                  AND activo = true
            """), {'nid': negocio_id})
            
            return {row[0] for row in result.fetchall()}
            
        except Exception as e:
            logger.error(f"Error obteniendo badges obtenidos: {e}")
            return set()
    
    
    @staticmethod
    def _evaluar_criterio(valor_actual, operador: str, valor_requerido) -> bool:
        """Evalúa si un valor cumple con el criterio del badge."""
        try:
            valor_actual = float(valor_actual)
            valor_requerido = float(valor_requerido)
            
            if operador == '>=':
                return valor_actual >= valor_requerido
            elif operador == '<=':
                return valor_actual <= valor_requerido
            elif operador == '==':
                return valor_actual == valor_requerido
            elif operador == '>':
                return valor_actual > valor_requerido
            elif operador == '<':
                return valor_actual < valor_requerido
            elif operador == '!=':
                return valor_actual != valor_requerido
            else:
                logger.warning(f"Operador desconocido: {operador}")
                return False
                
        except (ValueError, TypeError):
            return False
    
    
    @staticmethod
    def _asignar_badge(negocio_id: int, badge_id: int, valor_actual, codigo: str) -> bool:
        """Inserta un badge en negocio_badges_obtenidos."""
        try:
            db.session.execute(text("""
                INSERT INTO negocio_badges_obtenidos 
                    (negocio_id, badge_id, fecha_obtencion, valor_al_desbloquear, 
                     contexto, notificado, visto, activo)
                VALUES 
                    (:nid, :bid, NOW(), :valor, :contexto, false, false, true)
                ON CONFLICT DO NOTHING
            """), {
                'nid': negocio_id,
                'bid': badge_id,
                'valor': valor_actual,
                'contexto': f'Auto-verificado: {codigo} (valor: {valor_actual})'
            })
            
            # Actualizar contador en catálogo
            db.session.execute(text("""
                UPDATE negocio_badges 
                SET total_otorgados = COALESCE(total_otorgados, 0) + 1
                WHERE id = :bid
            """), {'bid': badge_id})
            
            db.session.commit()
            return True
            
        except Exception as e:
            logger.error(f"Error asignando badge {badge_id} a negocio {negocio_id}: {e}")
            db.session.rollback()
            return False
    
    
    # ═══════════════════════════════════════════════════════════════════
    # HELPERS PARA INTEGRAR EN OTROS ENDPOINTS
    # ═══════════════════════════════════════════════════════════════════
    
    @staticmethod
    def verificar_despues_de_servicio(negocio_id: int) -> dict:
        """
        Llamar después de que un servicio se marca como completado.
        Verifica solo badges relacionados con contratos.
        """
        return BadgeVerificationService.verificar_badges(negocio_id)
    
    
    @staticmethod
    def verificar_despues_de_calificacion(negocio_id: int) -> dict:
        """
        Llamar después de que se recibe una calificación.
        Verifica solo badges relacionados con ratings.
        """
        return BadgeVerificationService.verificar_badges(negocio_id)
    
    
    @staticmethod
    def verificar_despues_de_video(negocio_id: int) -> dict:
        """
        Llamar después de subir un video.
        Verifica solo badges de contenido.
        """
        return BadgeVerificationService.verificar_badges(negocio_id)


# ═══════════════════════════════════════════════════════════════════════
# FUNCIÓN WRAPPER
# ═══════════════════════════════════════════════════════════════════════
def verificar_badges_negocio(negocio_id: int) -> dict:
    """Wrapper para usar sin instanciar la clase."""
    return BadgeVerificationService.verificar_badges(negocio_id)

# ═══════════════════════════════════════════════════════════════════════
# BLUEPRINT - ENDPOINTS ADMIN PARA BADGES
# ═══════════════════════════════════════════════════════════════════════
from flask import Blueprint, jsonify

badge_verification_bp = Blueprint('badge_verification', __name__)


@badge_verification_bp.route('/verificar/<int:negocio_id>', methods=['GET'])
def verificar_badges_endpoint(negocio_id):
    """
    GET /api/admin/badges/verificar/<negocio_id>
    Ejecuta verificación de badges para un negocio.
    """
    try:
        resultado = BadgeVerificationService.verificar_badges(negocio_id)
        return jsonify({
            'status': 'success',
            'data': resultado
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@badge_verification_bp.route('/status/<int:negocio_id>', methods=['GET'])
def badge_status_endpoint(negocio_id):
    """
    GET /api/admin/badges/status/<negocio_id>
    Muestra badges obtenidos y progreso hacia los siguientes.
    """
    try:
        metricas = BadgeVerificationService._calcular_metricas_para_badges(negocio_id)
        badges_catalogo = BadgeVerificationService._get_catalogo_badges()
        badges_obtenidos = BadgeVerificationService._get_badges_obtenidos(negocio_id)
        
        status = []
        for badge in badges_catalogo:
            valor_actual = metricas.get(badge['criterio_tipo'])
            valor_requerido = badge['criterio_valor']
            obtenido = badge['id'] in badges_obtenidos
            
            progreso = 0
            if valor_actual is not None and valor_requerido > 0:
                progreso = min(100, round((valor_actual / valor_requerido) * 100))
            
            status.append({
                'codigo': badge['codigo'],
                'nombre': badge['nombre'],
                'nivel': badge['nivel'],
                'obtenido': obtenido,
                'valor_actual': valor_actual,
                'valor_requerido': valor_requerido,
                'progreso': 100 if obtenido else progreso
            })
        
        return jsonify({
            'status': 'success',
            'negocio_id': negocio_id,
            'total_obtenidos': len(badges_obtenidos),
            'badges': status
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500