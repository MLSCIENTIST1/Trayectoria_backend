"""
TuKomercio - Inicialización del Sistema de Trayectoria
Ejecutar UNA SOLA VEZ para crear tablas y poblar badges
"""

import sys
import os

# Agregar el directorio raíz al path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from src import create_app
from src.models.database import db
from src.models.trayectoria.badge import Badge
from src.models.trayectoria.user_score import UserScore
from src.models.trayectoria.user_badge import UserBadge
from src.models.trayectoria.user_metric import UserMetric
from src.models.trayectoria.user_stage_score import UserStageScore
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def init_trayectoria():
    """Inicializa el sistema de trayectoria"""
    
    app = create_app()
    
    with app.app_context():
        logger.info("="*70)
        logger.info("🎯 INICIALIZANDO SISTEMA DE TRAYECTORIA - TUKOMERCIO")
        logger.info("="*70)
        
        # 1. Crear todas las tablas
        logger.info("\n📊 Creando tablas de trayectoria...")
        try:
            db.create_all()
            logger.info("✅ Tablas creadas/verificadas exitosamente")
        except Exception as e:
            logger.error(f"❌ Error creando tablas: {e}")
            return
        
        # 2. Verificar si ya existen badges
        badges_existentes = Badge.query.count()
        
        if badges_existentes > 0:
            logger.info(f"ℹ️  Ya existen {badges_existentes} badges en el sistema")
            logger.info("   Si deseas recrearlos, elimínalos manualmente de la BD primero")
        else:
            # Crear badges
            logger.info("\n🏆 Inicializando catálogo de badges...")
            badges_creados = Badge.inicializar_badges_sistema()
            logger.info(f"✅ {badges_creados} badges creados")
        
        # 3. Verificar tablas creadas
        logger.info("\n📋 Verificando tablas creadas:")
        inspector = db.inspect(db.engine)
        tablas_trayectoria = [
            'user_scores',
            'user_score_history',
            'user_stage_scores',
            'badges',
            'user_badges',
            'user_metrics',
            'portfolio_videos'
        ]
        
        tablas_encontradas = 0
        for tabla in tablas_trayectoria:
            if tabla in inspector.get_table_names():
                logger.info(f"   ✅ {tabla}")
                tablas_encontradas += 1
            else:
                logger.warning(f"   ⚠️  {tabla} no encontrada")
        
        # 4. Mostrar badges creados
        if Badge.query.count() > 0:
            logger.info("\n🏆 Badges disponibles:")
            badges = Badge.query.order_by(Badge.orden).all()
            for badge in badges:
                logger.info(f"   {badge.emoji} {badge.nombre} - {badge.descripcion}")
        
        logger.info("\n" + "="*70)
        logger.info("🎉 SISTEMA DE TRAYECTORIA INICIALIZADO")
        logger.info("="*70)
        logger.info(f"\n✅ {tablas_encontradas}/{len(tablas_trayectoria)} tablas verificadas")
        logger.info(f"✅ {Badge.query.count()} badges disponibles")
        logger.info("\n📝 PRÓXIMOS PASOS:")
        logger.info("   1. El sistema está listo")
        logger.info("   2. Para cada usuario nuevo, se inicializará automáticamente:")
        logger.info("      - Scores (contratante, contratado, global)")
        logger.info("      - 4 Etapas (E1-E4)")
        logger.info("      - Métricas básicas")
        logger.info("      - Relación con badges (todos bloqueados)")
        logger.info("\n   3. Para inicializar un usuario existente:")
        logger.info("      python init_trayectoria.py <ID_USUARIO>")
        logger.info("\n✨ ¡Todo listo para usar!")
        

def init_usuario(usuario_id):
    """
    Inicializa la trayectoria para un usuario existente
    """
    app = create_app()
    
    with app.app_context():
        logger.info(f"\n🧪 Inicializando trayectoria para usuario {usuario_id}")
        
        from src.models.usuarios import Usuario
        
        # Verificar que el usuario existe
        usuario = Usuario.query.get(usuario_id)
        if not usuario:
            logger.error(f"❌ Usuario {usuario_id} no encontrado en la base de datos")
            return
        
        logger.info(f"   Usuario encontrado: {usuario.nombre}")
        
        # 1. Verificar/Crear score
        user_score = UserScore.query.filter_by(usuario_id=usuario_id).first()
        if user_score:
            logger.info("   ℹ️  Score ya existe, actualizando...")
            user_score.score_contratante = 87
            user_score.score_contratado = 92
            user_score.score_global = 89
            user_score.tendencia_contratante = 3
            user_score.tendencia_contratado = 2
            user_score.tendencia_global = 2
            user_score.percentil = 92
        else:
            logger.info("   📊 Creando scores...")
            user_score = UserScore(
                usuario_id=usuario_id,
                score_contratante=87,
                score_contratado=92,
                score_global=89,
                tendencia_contratante=3,
                tendencia_contratado=2,
                tendencia_global=2,
                percentil=92
            )
            db.session.add(user_score)
        
        db.session.commit()
        
        # 2. Inicializar etapas
        etapas_existentes = UserStageScore.query.filter_by(usuario_id=usuario_id).count()
        if etapas_existentes == 0:
            logger.info("   🎯 Creando etapas...")
            UserStageScore.inicializar_etapas_usuario(usuario_id)
        else:
            logger.info(f"   ℹ️  Ya existen {etapas_existentes} etapas")
        
        # 3. Inicializar métricas
        metricas_existentes = UserMetric.query.filter_by(usuario_id=usuario_id).count()
        if metricas_existentes == 0:
            logger.info("   📈 Creando métricas...")
            UserMetric.inicializar_metricas_usuario(usuario_id)
            
            # Actualizar con valores de ejemplo
            UserMetric.actualizar_metrica(usuario_id, 'proyectos_completados', 95, '+8 este mes', 'positive')
            UserMetric.actualizar_metrica(usuario_id, 'tiempo_promedio_dias', 12, '-2 días', 'positive')
            UserMetric.actualizar_metrica(usuario_id, 'rating_promedio', 4.8, 'Top 5%', 'positive')
            UserMetric.actualizar_metrica(usuario_id, 'clientes_recurrentes', 34, '36%', 'positive')
        else:
            logger.info(f"   ℹ️  Ya existen {metricas_existentes} métricas")
        
        # 4. Inicializar badges
        badges_usuario = UserBadge.query.filter_by(usuario_id=usuario_id).count()
        if badges_usuario == 0:
            logger.info("   🏆 Asociando badges...")
            UserBadge.inicializar_badges_usuario(usuario_id)
            
            # Desbloquear algunos badges de ejemplo
            UserBadge.desbloquear_badge(usuario_id, 'primera-estrella', 'Inicialización de prueba')
            UserBadge.desbloquear_badge(usuario_id, 'rayo-veloz', 'Inicialización de prueba')
            UserBadge.desbloquear_badge(usuario_id, 'perfeccionista', 'Inicialización de prueba')
            UserBadge.desbloquear_badge(usuario_id, 'cliente-fiel', 'Inicialización de prueba')
            UserBadge.desbloquear_badge(usuario_id, 'estrella-ascenso', 'Inicialización de prueba')
        else:
            logger.info(f"   ℹ️  Ya tiene {badges_usuario} badges asociados")
        
        logger.info(f"\n✅ Trayectoria inicializada para usuario {usuario_id}")
        logger.info("   - Scores: Contratante=87, Contratado=92, Global=89")
        logger.info("   - Etapas: 4 etapas")
        logger.info("   - Métricas: 8 métricas")
        logger.info("   - Badges: 5 desbloqueados de ejemplo")


if __name__ == '__main__':
    if len(sys.argv) > 1:
        # Si se pasa un ID de usuario, inicializar solo ese usuario
        try:
            usuario_id = int(sys.argv[1])
            init_usuario(usuario_id)
        except ValueError:
            logger.error("❌ El ID de usuario debe ser un número")
    else:
        # Inicializar sistema completo
        init_trayectoria()