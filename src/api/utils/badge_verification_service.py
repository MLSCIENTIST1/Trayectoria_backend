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

# Cupo de fundadores: los primeros N usuarios registrados son "Fundadores".
# Cambiar este número aquí ajusta el cupo de la insignia premium.
FUNDADOR_CUPO = 50


def temporadas_activas(hoy):
    """
    Dada una fecha, devuelve las temporadas ACTIVAS y su ventana [desde, hasta].
    Los badges de temporada solo son otorgables si HOY cae dentro de su ventana.
    Función pura → testeable con fechas inyectadas.
    """
    activas = {}
    y, m, d = hoy.year, hoy.month, hoy.day
    if m == 12:
        activas['ventas_navidad'] = (datetime(y, 12, 1), datetime(y, 12, 31, 23, 59, 59))
    if m == 9:
        activas['ventas_amor_amistad'] = (datetime(y, 9, 1), datetime(y, 9, 30, 23, 59, 59))
    if m == 5:
        activas['ventas_dia_madre'] = (datetime(y, 5, 1), datetime(y, 5, 31, 23, 59, 59))
    if m == 11 and 20 <= d <= 30:
        activas['ventas_black_friday'] = (datetime(y, 11, 20), datetime(y, 11, 30, 23, 59, 59))
    return activas


SEASONAL_METRICS = ['ventas_navidad', 'ventas_amor_amistad', 'ventas_dia_madre', 'ventas_black_friday']


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
            # ORDEN DE REGISTRO DEL NEGOCIO (arregla badge 'pioneer')
            # Posición del negocio = cuántos negocios se crearon hasta este.
            # ═══════════════════════════════════════════
            try:
                result = db.session.execute(text("""
                    SELECT COUNT(*)
                    FROM negocios
                    WHERE id_negocio <= :nid
                """), {'nid': negocio_id})
                metricas['orden_registro'] = result.fetchone()[0] or 999999
            except Exception:
                metricas['orden_registro'] = 999999

            # ═══════════════════════════════════════════
            # ES FUNDADOR (insignia premium)
            # 1 si el DUEÑO está entre los primeros FUNDADOR_CUPO usuarios
            # registrados (cuenta usuarios reales, robusto ante gaps de id).
            # ═══════════════════════════════════════════
            try:
                result = db.session.execute(text("""
                    SELECT u.id_usuario
                    FROM negocios n
                    JOIN usuarios u ON n.usuario_id = u.id_usuario
                    WHERE n.id_negocio = :nid
                """), {'nid': negocio_id})
                row = result.fetchone()
                if row and row[0] is not None:
                    owner_id = row[0]
                    cnt = db.session.execute(text("""
                        SELECT COUNT(*) FROM usuarios WHERE id_usuario <= :oid
                    """), {'oid': owner_id}).fetchone()[0] or 999999
                    metricas['es_fundador'] = 1 if cnt <= FUNDADOR_CUPO else 0
                else:
                    metricas['es_fundador'] = 0
            except Exception as e:
                logger.warning(f"No se pudo calcular es_fundador: {e}")
                metricas['es_fundador'] = 0

            # ═══════════════════════════════════════════
            # E-COMMERCE · PEDIDOS COMPLETADOS (S9)
            # ═══════════════════════════════════════════
            try:
                result = db.session.execute(text("""
                    SELECT COUNT(*) FROM pedidos
                    WHERE negocio_id = :nid AND estado = 'entregado'
                """), {'nid': negocio_id})
                metricas['pedidos_completados'] = result.fetchone()[0] or 0
            except Exception:
                metricas['pedidos_completados'] = 0

            # ═══════════════════════════════════════════
            # E-COMMERCE · VENTAS EN COP (S10)
            # Ingreso del negocio = subtotal - descuento (excluye envío).
            # ═══════════════════════════════════════════
            try:
                result = db.session.execute(text("""
                    SELECT COALESCE(SUM(COALESCE(subtotal,0) - COALESCE(descuento,0)), 0)
                    FROM pedidos
                    WHERE negocio_id = :nid AND estado = 'entregado'
                """), {'nid': negocio_id})
                metricas['ventas_cop'] = float(result.fetchone()[0] or 0)
            except Exception:
                metricas['ventas_cop'] = 0

            # ═══════════════════════════════════════════
            # E-COMMERCE · ENTREGAS NETAS SIN DEVOLUCIÓN (S10)
            # ═══════════════════════════════════════════
            try:
                entregados = metricas.get('pedidos_completados', 0)
                devs = db.session.execute(text("""
                    SELECT COUNT(*) FROM pedidos
                    WHERE negocio_id = :nid AND estado = 'devuelto'
                """), {'nid': negocio_id}).fetchone()[0] or 0
                metricas['pedidos_sin_devolucion'] = max(0, entregados - devs)
            except Exception:
                metricas['pedidos_sin_devolucion'] = 0

            # ═══════════════════════════════════════════
            # CATÁLOGO · PRODUCTOS ACTIVOS (S10)
            # ═══════════════════════════════════════════
            try:
                result = db.session.execute(text("""
                    SELECT COUNT(*) FROM productos_catalogo
                    WHERE negocio_id = :nid AND activo = true
                """), {'nid': negocio_id})
                metricas['productos_activos'] = result.fetchone()[0] or 0
            except Exception:
                metricas['productos_activos'] = 0

            # ═══════════════════════════════════════════
            # CALIDAD · CALIFICACIÓN CON MÍNIMO DE RESEÑAS (S10)
            # Solo "cuenta" si hay >= 10 reseñas; si no, 0 (no califica).
            # ═══════════════════════════════════════════
            try:
                row = db.session.execute(text("""
                    SELECT COUNT(*) AS n, COALESCE(AVG(rating), 0) AS prom
                    FROM producto_reviews
                    WHERE negocio_id = :nid
                """), {'nid': negocio_id}).fetchone()
                total_reviews = row[0] or 0
                promedio = float(row[1] or 0)
                metricas['calificacion_calificada'] = promedio if total_reviews >= 10 else 0
            except Exception:
                metricas['calificacion_calificada'] = 0

            # ═══════════════════════════════════════════
            # CREADOR · MÉTRICAS DEL DUEÑO (S11)
            # negocios que tiene el dueño + antigüedad de su cuenta
            # ═══════════════════════════════════════════
            try:
                row = db.session.execute(text("""
                    SELECT u.id_usuario, u.created_at
                    FROM negocios n
                    JOIN usuarios u ON n.usuario_id = u.id_usuario
                    WHERE n.id_negocio = :nid
                """), {'nid': negocio_id}).fetchone()
                if row and row[0] is not None:
                    owner_id = row[0]
                    owner_created = row[1]
                    metricas['negocios_del_owner'] = db.session.execute(text("""
                        SELECT COUNT(*) FROM negocios WHERE usuario_id = :oid
                    """), {'oid': owner_id}).fetchone()[0] or 0
                    if owner_created:
                        try:
                            dias = (datetime.utcnow() - owner_created).days
                            metricas['dias_registrado_owner'] = max(0, dias)
                        except Exception:
                            metricas['dias_registrado_owner'] = 0
                    else:
                        metricas['dias_registrado_owner'] = 0
                else:
                    metricas['negocios_del_owner'] = 0
                    metricas['dias_registrado_owner'] = 0
            except Exception as e:
                logger.warning(f"No se pudieron calcular métricas de creador: {e}")
                metricas['negocios_del_owner'] = 0
                metricas['dias_registrado_owner'] = 0

            # ═══════════════════════════════════════════
            # SECRETOS · MÉTRICAS TEMPORALES (S12)  [PostgreSQL]
            # Cada una en su try/except: si falla, queda en 0 (no se otorga).
            # ═══════════════════════════════════════════

            # Noctámbulo: ventas entregadas entre 00:00 y 04:59
            try:
                metricas['ventas_madrugada'] = db.session.execute(text("""
                    SELECT COUNT(*) FROM pedidos
                    WHERE negocio_id = :nid AND estado = 'entregado'
                      AND EXTRACT(HOUR FROM fecha_pedido) < 5
                """), {'nid': negocio_id}).fetchone()[0] or 0
            except Exception:
                metricas['ventas_madrugada'] = 0

            # Velocista: máximo de pedidos entregados en un mismo día
            try:
                metricas['max_pedidos_dia'] = db.session.execute(text("""
                    SELECT COALESCE(MAX(c), 0) FROM (
                        SELECT COUNT(*) AS c FROM pedidos
                        WHERE negocio_id = :nid AND estado = 'entregado'
                        GROUP BY DATE(fecha_pedido)
                    ) t
                """), {'nid': negocio_id}).fetchone()[0] or 0
            except Exception:
                metricas['max_pedidos_dia'] = 0

            # Cumpleañero: vendió el día del aniversario del negocio (mismo MM-DD)
            try:
                metricas['ventas_aniversario'] = db.session.execute(text("""
                    SELECT COUNT(*) FROM pedidos p
                    JOIN negocios n ON p.negocio_id = n.id_negocio
                    WHERE p.negocio_id = :nid AND p.estado = 'entregado'
                      AND n.fecha_registro IS NOT NULL
                      AND to_char(p.fecha_pedido, 'MM-DD') = to_char(n.fecha_registro, 'MM-DD')
                """), {'nid': negocio_id}).fetchone()[0] or 0
            except Exception:
                metricas['ventas_aniversario'] = 0

            # Guerrero de fin de semana: ventas entregadas en sábado/domingo
            try:
                metricas['ventas_fin_semana'] = db.session.execute(text("""
                    SELECT COUNT(*) FROM pedidos
                    WHERE negocio_id = :nid AND estado = 'entregado'
                      AND EXTRACT(DOW FROM fecha_pedido) IN (0, 6)
                """), {'nid': negocio_id}).fetchone()[0] or 0
            except Exception:
                metricas['ventas_fin_semana'] = 0

            # ═══════════════════════════════════════════
            # TEMPORADA (S13) — solo otorgables DURANTE la fecha especial
            # ═══════════════════════════════════════════
            activas = temporadas_activas(datetime.utcnow())
            for metrica in SEASONAL_METRICS:
                if metrica in activas:
                    desde, hasta = activas[metrica]
                    try:
                        metricas[metrica] = db.session.execute(text("""
                            SELECT COUNT(*) FROM pedidos
                            WHERE negocio_id = :nid AND estado = 'entregado'
                              AND fecha_pedido >= :desde AND fecha_pedido <= :hasta
                        """), {'nid': negocio_id, 'desde': desde, 'hasta': hasta}).fetchone()[0] or 0
                    except Exception:
                        metricas[metrica] = 0
                else:
                    metricas[metrica] = 0  # fuera de temporada → no otorgable

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