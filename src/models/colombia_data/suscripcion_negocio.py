"""
TuKomercio — Modelo de Suscripciones de Negocios
=================================================
Registra el ciclo de vida de cada negocio:
  trial → activa → gracia → vencida | cancelada

Cada negocio tiene UNA suscripción activa y un historial completo.
"""

import sqlalchemy as sa
from sqlalchemy.orm import relationship
from src.models.database import db
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

# ─────────────────────────────────────────────────────────────────────────────
# CONSTANTES
# ─────────────────────────────────────────────────────────────────────────────
DIAS_TRIAL_DEFAULT    = 30   # primer mes gratis
DIAS_GRACIA_DEFAULT   = 3    # días extra post-vencimiento antes de bloquear
DIAS_ALERTA_PRONTO    = 7    # avisar cuando quedan ≤ N días

ESTADOS_VALIDOS = {'trial', 'activa', 'gracia', 'vencida', 'cancelada', 'pausada'}


# ─────────────────────────────────────────────────────────────────────────────
# MODELO
# ─────────────────────────────────────────────────────────────────────────────
class SuscripcionNegocio(db.Model):
    """
    Suscripción mensual de un negocio a la plataforma TuKomercio.

    Estados:
      trial     — período de prueba gratuito activo
      activa    — suscripción paga vigente
      gracia    — venció pero dentro del período de gracia (N días extra)
      vencida   — venció y pasó el período de gracia
      cancelada — cancelada manualmente por admin o usuario
      pausada   — suspendida temporalmente (ej. pago en disputa)
    """
    __tablename__ = 'suscripciones_negocio'

    id         = sa.Column(sa.Integer, primary_key=True)

    negocio_id = sa.Column(
        sa.Integer,
        sa.ForeignKey('negocios.id_negocio', ondelete='CASCADE'),
        nullable=False,
        index=True
    )

    # Plan asociado (puede ser NULL si aún no eligió plan pago)
    plan_id = sa.Column(
        sa.Integer,
        sa.ForeignKey('planes.id', ondelete='SET NULL'),
        nullable=True
    )

    # ──────────────────────────────────────────────
    # ESTADO
    # ──────────────────────────────────────────────
    estado = sa.Column(
        sa.String(20),
        nullable=False,
        default='trial',
        index=True
    )

    # ──────────────────────────────────────────────
    # TRIAL (primer mes gratis)
    # ──────────────────────────────────────────────
    es_trial            = sa.Column(sa.Boolean, nullable=False, default=True)
    fecha_inicio_trial  = sa.Column(sa.DateTime, nullable=True)
    fecha_fin_trial     = sa.Column(sa.DateTime, nullable=True)

    # ──────────────────────────────────────────────
    # SUSCRIPCIÓN PAGA
    # ──────────────────────────────────────────────
    fecha_inicio      = sa.Column(sa.DateTime, nullable=True)   # inicio del período pago actual
    fecha_fin         = sa.Column(sa.DateTime, nullable=True)   # fin del período pago actual
    fecha_renovacion  = sa.Column(sa.DateTime, nullable=True)   # próxima renovación esperada

    # ──────────────────────────────────────────────
    # CONTROL
    # ──────────────────────────────────────────────
    dias_gracia           = sa.Column(sa.Integer, default=DIAS_GRACIA_DEFAULT, nullable=False)
    renovacion_automatica = sa.Column(sa.Boolean, default=False, nullable=False)
    trial_usado           = sa.Column(sa.Boolean, default=False, nullable=False)
    # trial_usado = True impide que el admin regale otro trial (a menos que lo override)

    # ──────────────────────────────────────────────
    # NOTIFICACIONES — tracking anti-duplicado
    # ──────────────────────────────────────────────
    # dict con las fechas en que se enviaron los emails de alerta.
    # Claves: trial_7d, trial_3d, trial_gracia, trial_vencida,
    #         sus_7d, sus_3d, sus_gracia, sus_vencida
    # Valor: ISO datetime str si se envió, None si no.
    alertas_enviadas = sa.Column(sa.JSON, nullable=True, default=dict)

    # ──────────────────────────────────────────────
    # AUDITORÍA
    # ──────────────────────────────────────────────
    creado_por   = sa.Column(sa.String(50), default='sistema')
    # 'sistema' | 'admin:<email>' | 'usuario'
    modificado_por = sa.Column(sa.String(50), nullable=True)
    notas        = sa.Column(sa.Text, nullable=True)

    created_at   = sa.Column(sa.DateTime, default=datetime.utcnow, nullable=False)
    updated_at   = sa.Column(sa.DateTime, default=datetime.utcnow,
                             onupdate=datetime.utcnow, nullable=False)

    # ──────────────────────────────────────────────
    # RELACIONES
    # ──────────────────────────────────────────────
    negocio = relationship(
        'Negocio',
        backref=db.backref('suscripcion', uselist=False, lazy='select')
    )
    plan = relationship('Plan', lazy='select')

    # ──────────────────────────────────────────────
    # PROPIEDADES CALCULADAS
    # ──────────────────────────────────────────────
    @property
    def estado_actual(self) -> str:
        """
        Calcula el estado real basándose en las fechas actuales.
        Siempre es más confiable que el campo `estado` guardado.
        """
        ahora = datetime.utcnow()

        if self.estado == 'cancelada':
            return 'cancelada'

        if self.estado == 'pausada':
            return 'pausada'

        # ── período de trial ──
        if self.es_trial and self.fecha_fin_trial:
            if ahora <= self.fecha_fin_trial:
                return 'trial'
            # venció el trial → ¿está en gracia?
            fin_gracia = self.fecha_fin_trial + timedelta(days=self.dias_gracia or DIAS_GRACIA_DEFAULT)
            if ahora <= fin_gracia:
                return 'gracia'
            return 'vencida'

        # ── suscripción paga ──
        if self.fecha_fin:
            if ahora <= self.fecha_fin:
                return 'activa'
            fin_gracia = self.fecha_fin + timedelta(days=self.dias_gracia or DIAS_GRACIA_DEFAULT)
            if ahora <= fin_gracia:
                return 'gracia'
            return 'vencida'

        return self.estado or 'vencida'

    @property
    def dias_restantes(self) -> int | None:
        """
        Días que quedan en el período activo (trial o suscripción paga).
        Retorna 0 si vencido, None si no hay fecha de fin configurada.
        """
        ahora = datetime.utcnow()
        fecha_ref = None

        if self.es_trial and self.fecha_fin_trial:
            fecha_ref = self.fecha_fin_trial
        elif self.fecha_fin:
            fecha_ref = self.fecha_fin

        if fecha_ref is None:
            return None
        delta = fecha_ref - ahora
        return max(0, delta.days)

    @property
    def vence_pronto(self) -> bool:
        """True si quedan ≤ DIAS_ALERTA_PRONTO días y no está vencida."""
        dias = self.dias_restantes
        if dias is None:
            return False
        estado = self.estado_actual
        return estado in ('trial', 'activa') and dias <= DIAS_ALERTA_PRONTO

    @property
    def fecha_vencimiento(self):
        """Fecha de vencimiento relevante (trial o suscripción paga)."""
        if self.es_trial and self.fecha_fin_trial:
            return self.fecha_fin_trial
        return self.fecha_fin

    # ──────────────────────────────────────────────
    # MÉTODOS DE NEGOCIO
    # ──────────────────────────────────────────────
    def iniciar_trial(self, dias: int = DIAS_TRIAL_DEFAULT, creado_por: str = 'sistema'):
        """Activa el período de prueba gratuito."""
        ahora = datetime.utcnow()
        self.es_trial           = True
        self.trial_usado        = True
        self.fecha_inicio_trial = ahora
        self.fecha_fin_trial    = ahora + timedelta(days=dias)
        self.estado             = 'trial'
        self.creado_por         = creado_por
        logger.info(f"🆓 Trial iniciado: negocio_id={self.negocio_id} "
                    f"vence={self.fecha_fin_trial.date()}")

    def activar_suscripcion(self, plan_id: int, dias: int = 30,
                            creado_por: str = 'admin', notas: str = None):
        """Activa o renueva una suscripción paga."""
        ahora = datetime.utcnow()
        self.plan_id       = plan_id
        self.es_trial      = False
        self.fecha_inicio  = ahora
        self.fecha_fin     = ahora + timedelta(days=dias)
        self.fecha_renovacion = self.fecha_fin
        self.estado        = 'activa'
        self.modificado_por = creado_por
        if notas:
            self.notas = notas
        logger.info(f"✅ Suscripción activada: negocio_id={self.negocio_id} "
                    f"plan_id={plan_id} vence={self.fecha_fin.date()}")

    def extender(self, dias: int = 30, creado_por: str = 'admin', notas: str = None):
        """Extiende el período activo (trial o suscripción paga) en N días."""
        from datetime import datetime as _dt
        ahora = _dt.utcnow()

        if self.es_trial and self.fecha_fin_trial:
            base = max(self.fecha_fin_trial, ahora)
            self.fecha_fin_trial = base + timedelta(days=dias)
            logger.info(f"⏳ Trial extendido: negocio_id={self.negocio_id} "
                        f"nueva fecha fin={self.fecha_fin_trial.date()}")
        else:
            base = max(self.fecha_fin, ahora) if self.fecha_fin else ahora
            self.fecha_fin = base + timedelta(days=dias)
            self.fecha_renovacion = self.fecha_fin
            logger.info(f"⏳ Suscripción extendida: negocio_id={self.negocio_id} "
                        f"nueva fecha fin={self.fecha_fin.date()}")

        self.estado = self.estado_actual   # recalcular
        self.modificado_por = creado_por
        if notas:
            self.notas = notas

    def cancelar(self, creado_por: str = 'admin', notas: str = None):
        """Cancela la suscripción."""
        self.estado = 'cancelada'
        self.modificado_por = creado_por
        if notas:
            self.notas = notas
        logger.info(f"❌ Suscripción cancelada: negocio_id={self.negocio_id}")

    def pausar(self, creado_por: str = 'admin', notas: str = None):
        """Pausa temporalmente (pago en disputa, etc.)."""
        self.estado = 'pausada'
        self.modificado_por = creado_por
        if notas:
            self.notas = notas

    def dar_trial_segunda_oportunidad(self, dias: int = DIAS_TRIAL_DEFAULT,
                                      creado_por: str = 'admin'):
        """Admin puede regalar otro trial aunque trial_usado=True."""
        self.trial_usado = True   # marcar igualmente
        self.iniciar_trial(dias=dias, creado_por=creado_por)

    # ──────────────────────────────────────────────
    # SERIALIZACIÓN
    # ──────────────────────────────────────────────
    def to_dict(self, include_negocio: bool = False) -> dict:
        estado_c = self.estado_actual
        dias_r   = self.dias_restantes

        data = {
            'id':                    self.id,
            'negocio_id':            self.negocio_id,
            'plan_id':               self.plan_id,
            'plan_key':              self.plan.key if self.plan else None,
            'plan_nombre':           self.plan.nombre if self.plan else None,

            # Estado
            'estado':                self.estado,          # campo BD (puede estar desactualizado)
            'estado_actual':         estado_c,             # calculado en tiempo real
            'dias_restantes':        dias_r,
            'vence_pronto':          self.vence_pronto,
            'fecha_vencimiento':     self.fecha_vencimiento.isoformat() if self.fecha_vencimiento else None,

            # Trial
            'es_trial':              self.es_trial,
            'trial_usado':           self.trial_usado,
            'fecha_inicio_trial':    self.fecha_inicio_trial.isoformat() if self.fecha_inicio_trial else None,
            'fecha_fin_trial':       self.fecha_fin_trial.isoformat() if self.fecha_fin_trial else None,

            # Suscripción paga
            'fecha_inicio':          self.fecha_inicio.isoformat() if self.fecha_inicio else None,
            'fecha_fin':             self.fecha_fin.isoformat() if self.fecha_fin else None,
            'fecha_renovacion':      self.fecha_renovacion.isoformat() if self.fecha_renovacion else None,

            # Control
            'dias_gracia':           self.dias_gracia,
            'renovacion_automatica': self.renovacion_automatica,

            # Auditoría
            'creado_por':            self.creado_por,
            'modificado_por':        self.modificado_por,
            'notas':                 self.notas,
            'alertas_enviadas':      self.alertas_enviadas or {},
            'created_at':            self.created_at.isoformat() if self.created_at else None,
            'updated_at':            self.updated_at.isoformat() if self.updated_at else None,
        }

        if include_negocio and self.negocio:
            data['negocio'] = {
                'nombre': self.negocio.nombre_negocio,
                'slug':   self.negocio.slug,
                'email':  self.negocio.email,
            }

        return data

    def __repr__(self):
        return (f'<SuscripcionNegocio negocio={self.negocio_id} '
                f'estado={self.estado_actual} '
                f'dias_restantes={self.dias_restantes}>')


# ─────────────────────────────────────────────────────────────────────────────
# FUNCIÓN DE CONVENIENCIA
# ─────────────────────────────────────────────────────────────────────────────
def iniciar_trial_para_negocio(negocio_id: int,
                                plan_key: str = 'basic',
                                dias: int = DIAS_TRIAL_DEFAULT,
                                creado_por: str = 'sistema') -> 'SuscripcionNegocio':
    """
    Crea y persiste una suscripción trial para un negocio recién creado.
    Llama a db.session.flush() para obtener el ID sin hacer commit.
    """
    from src.models.feature_models import Plan
    from src.models.database import db as _db

    plan = Plan.query.filter_by(key=plan_key, activo=True).first()

    suscripcion = SuscripcionNegocio(
        negocio_id=negocio_id,
        plan_id=plan.id if plan else None,
    )
    suscripcion.iniciar_trial(dias=dias, creado_por=creado_por)

    _db.session.add(suscripcion)
    _db.session.flush()   # ID disponible, sin commit

    logger.info(f"🆓 Trial creado para negocio {negocio_id}: "
                f"plan={plan_key} días={dias}")
    return suscripcion
