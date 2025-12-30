from alembic import op
import sqlalchemy as sa
from src.models.database import db
from sqlalchemy.orm import relationship
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

logger.debug("Modelo de estadisticas recogidas colombia cargado correctamente.")


# Modelo Colombia
class Colombia(db.Model):
    __tablename__ = 'colombia'

    ciudad_id = sa.Column(sa.Integer, primary_key=True)
    ciudad_nombre = sa.Column(sa.String(100), nullable=True)
    servicios_insatisfechos = sa.Column(sa.Integer, nullable=True)
    servicio_mayor_valor = sa.Column(sa.Text, nullable=True, default="no disponible")
    servicio_menor_valor = sa.Column(sa.Text, nullable=True)
    precio_promedio_servicios = sa.Column(sa.Float, nullable=True)
    servicio_mas_ofrecido = sa.Column(sa.Text, nullable=True)
    servicio_menos_ofrecido = sa.Column(sa.Text, nullable=True)

    porcentaje_niñez = sa.Column(sa.Float, nullable=True)
    porcentaje_adolescencia_temprana = sa.Column(sa.Float, nullable=True)
    porcentaje_adolescencia_tardia = sa.Column(sa.Float, nullable=True)
    porcentaje_adultez_joven = sa.Column(sa.Float, nullable=True)
    porcentaje_adultez_media = sa.Column(sa.Float, nullable=True)
    porcentaje_pre_jubilacion = sa.Column(sa.Float, nullable=True)
    porcentaje_vejez_temprana = sa.Column(sa.Float, nullable=True)
    porcentaje_vejez_avanzada = sa.Column(sa.Float, nullable=True)

    usuarios_1_servicio = sa.Column(sa.Integer, nullable=True)
    usuarios_2_servicios = sa.Column(sa.Integer, nullable=True)
    usuarios_3_servicios = sa.Column(sa.Integer, nullable=True)
    usuarios_4_servicios = sa.Column(sa.Integer, nullable=True)
    usuarios_5_servicios = sa.Column(sa.Integer, nullable=True)
    usuarios_foto_perfil = sa.Column(sa.Integer, nullable=True)
    usuarios_solicitudes_baja = sa.Column(sa.Integer, nullable=True)
    feedbacks_plataforma = sa.Column(sa.Integer, nullable=True)
    promedio_ingresos_diarios = sa.Column(sa.Float, nullable=True)

    servicio_mas_contratado = sa.Column(sa.Text, nullable=True)
    servicio_menos_contratado = sa.Column(sa.Text, nullable=True)
    precio_minimo_promedio_ofertado = sa.Column(sa.Float, nullable=True)
    precio_maximo_promedio_ofertado = sa.Column(sa.Float, nullable=True)
    precio_minimo_promedio_contratado = sa.Column(sa.Float, nullable=True)
    precio_maximo_promedio_contratado = sa.Column(sa.Float, nullable=True)

    tasa_crecimiento_usuarios = sa.Column(sa.Float, nullable=True)
    tasa_retencion_usuarios = sa.Column(sa.Float, nullable=True)
    tasa_churn_usuarios = sa.Column(sa.Float, nullable=True)
    servicios_emergentes = sa.Column(sa.Text, nullable=True)
    ratio_contratados_vs_ofrecidos = sa.Column(sa.Float, nullable=True)
    porcentaje_freelancers = sa.Column(sa.Float, nullable=True)

ciudad_servicios= relationship("Servicio", backref="colombia")

def upgrade():
    # Crear la tabla Colombia
    op.create_table(
        'colombia',
        sa.Column('ciudad_id', sa.Integer, primary_key=True),
        sa.Column('ciudad_nombre', sa.String(100), nullable=True),
        sa.Column('servicios_insatisfechos', sa.Integer, nullable=True),
        sa.Column('servicio_mayor_valor', sa.Text, nullable=True),
        sa.Column('servicio_menor_valor', sa.Text, nullable=True),
        sa.Column('precio_promedio_servicios', sa.Float, nullable=True),
        sa.Column('servicio_mas_ofrecido', sa.Text, nullable=True),
        sa.Column('servicio_menos_ofrecido', sa.Text, nullable=True),
        sa.Column('porcentaje_niñez', sa.Float, nullable=True),
        sa.Column('porcentaje_adolescencia_temprana', sa.Float, nullable=True),
        sa.Column('porcentaje_adolescencia_tardia', sa.Float, nullable=True),
        sa.Column('porcentaje_adultez_joven', sa.Float, nullable=True),
        sa.Column('porcentaje_adultez_media', sa.Float, nullable=True),
        sa.Column('porcentaje_pre_jubilacion', sa.Float, nullable=True),
        sa.Column('porcentaje_vejez_temprana', sa.Float, nullable=True),
        sa.Column('porcentaje_vejez_avanzada', sa.Float, nullable=True),
        sa.Column('usuarios_1_servicio', sa.Integer, nullable=True),
        sa.Column('usuarios_2_servicios', sa.Integer, nullable=True),
        sa.Column('usuarios_3_servicios', sa.Integer, nullable=True),
        sa.Column('usuarios_4_servicios', sa.Integer, nullable=True),
        sa.Column('usuarios_5_servicios', sa.Integer, nullable=True),
        sa.Column('usuarios_foto_perfil', sa.Integer, nullable=True),
        sa.Column('usuarios_solicitudes_baja', sa.Integer, nullable=True),
        sa.Column('feedbacks_plataforma', sa.Integer, nullable=True),
        sa.Column('promedio_ingresos_diarios', sa.Float, nullable=True),
        sa.Column('servicio_mas_contratado', sa.Text, nullable=True),
        sa.Column('servicio_menos_contratado', sa.Text, nullable=True),
        sa.Column('precio_minimo_promedio_ofertado', sa.Float, nullable=True),
        sa.Column('precio_maximo_promedio_ofertado', sa.Float, nullable=True),
        sa.Column('precio_minimo_promedio_contratado', sa.Float, nullable=True),
        sa.Column('precio_maximo_promedio_contratado', sa.Float, nullable=True),
        sa.Column('tasa_crecimiento_usuarios', sa.Float, nullable=True),
        sa.Column('tasa_retencion_usuarios', sa.Float, nullable=True),
        sa.Column('tasa_churn_usuarios', sa.Float, nullable=True),
        sa.Column('servicios_emergentes', sa.Text, nullable=True),
        sa.Column('ratio_contratados_vs_ofrecidos', sa.Float, nullable=True),
        sa.Column('porcentaje_freelancers', sa.Float, nullable=True),
    )

    
    

    for ciudad_nombre in ciudades:
        op.execute(f"INSERT INTO colombia (ciudad_nombre) VALUES ('{ciudad_nombre}');")

def downgrade():
    op.drop_table('colombia')