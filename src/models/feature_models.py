# ═══════════════════════════════════════════════════════════════════════════════
# TUKOMERCIO - Modelos: Feature Flags + Planes
# ═══════════════════════════════════════════════════════════════════════════════
#
# INSTRUCCIONES:
# 1. Coloca este archivo en: src/models/feature_models.py
# 2. Importa en tu app o en tu models/__init__.py
# 3. Los modelos usan tu mismo `db` de SQLAlchemy
# ═══════════════════════════════════════════════════════════════════════════════

from datetime import datetime
from src.models import db  # Ajusta según tu import (puede ser from app import db)


class FeatureFlag(db.Model):
    """
    Feature Flag - Cada funcionalidad controlable de la app.
    
    Uso rápido:
        feature = FeatureFlag.query.filter_by(key='cartera').first()
        if feature and feature.activo_global:
            # La feature está encendida globalmente
    """
    __tablename__ = 'feature_flags'
    
    id              = db.Column(db.Integer, primary_key=True)
    key             = db.Column(db.String(100), unique=True, nullable=False)
    nombre          = db.Column(db.String(200), nullable=False)
    descripcion     = db.Column(db.Text)
    categoria       = db.Column(db.String(50), default='general')
    activo_global   = db.Column(db.Boolean, default=True)
    visible         = db.Column(db.Boolean, default=True)
    icono           = db.Column(db.String(50))
    orden           = db.Column(db.Integer, default=0)
    created_at      = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at      = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relación con plan_features
    plan_features   = db.relationship('PlanFeature', back_populates='feature', lazy='dynamic')
    
    def to_dict(self):
        return {
            'id': self.id,
            'key': self.key,
            'nombre': self.nombre,
            'descripcion': self.descripcion,
            'categoria': self.categoria,
            'activo_global': self.activo_global,
            'visible': self.visible,
            'icono': self.icono,
            'orden': self.orden
        }
    
    def __repr__(self):
        estado = "✅" if self.activo_global else "❌"
        return f'<Feature {estado} {self.key}>'


class Plan(db.Model):
    """
    Plan de suscripción (Basic, Pro, Premium, Delux).
    
    Uso rápido:
        plan = Plan.query.filter_by(key='pro').first()
        features_del_plan = plan.get_feature_keys()  # ['store_designer', 'gastos', ...]
    """
    __tablename__ = 'planes'
    
    id              = db.Column(db.Integer, primary_key=True)
    key             = db.Column(db.String(50), unique=True, nullable=False)
    nombre          = db.Column(db.String(100), nullable=False)
    descripcion     = db.Column(db.Text)
    precio_mensual  = db.Column(db.Numeric(12, 2), default=0)
    precio_anual    = db.Column(db.Numeric(12, 2), default=0)
    orden           = db.Column(db.Integer, default=0)
    color           = db.Column(db.String(7))
    icono           = db.Column(db.String(10))
    activo          = db.Column(db.Boolean, default=True)
    created_at      = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relaciones
    plan_features   = db.relationship('PlanFeature', back_populates='plan', lazy='dynamic')
    negocios_plan   = db.relationship('NegocioPlan', back_populates='plan', lazy='dynamic')
    
    def get_feature_keys(self):
        """Retorna lista de keys de features incluidas en este plan"""
        return [pf.feature.key for pf in self.plan_features.all() if pf.feature]
    
    def has_feature(self, feature_key):
        """¿Este plan incluye esta feature?"""
        return PlanFeature.query.join(FeatureFlag).filter(
            PlanFeature.plan_id == self.id,
            FeatureFlag.key == feature_key
        ).first() is not None
    
    def get_feature_limit(self, feature_key):
        """Obtener el límite de una feature en este plan (None = ilimitado)"""
        pf = PlanFeature.query.join(FeatureFlag).filter(
            PlanFeature.plan_id == self.id,
            FeatureFlag.key == feature_key
        ).first()
        return pf.limite if pf else 0
    
    def to_dict(self, include_features=False):
        data = {
            'id': self.id,
            'key': self.key,
            'nombre': self.nombre,
            'descripcion': self.descripcion,
            'precio_mensual': float(self.precio_mensual or 0),
            'precio_anual': float(self.precio_anual or 0),
            'orden': self.orden,
            'color': self.color,
            'icono': self.icono,
            'activo': self.activo
        }
        if include_features:
            data['features'] = []
            for pf in self.plan_features.all():
                if pf.feature:
                    data['features'].append({
                        'key': pf.feature.key,
                        'nombre': pf.feature.nombre,
                        'categoria': pf.feature.categoria,
                        'limite': pf.limite,
                        'config': pf.config_json
                    })
        return data
    
    def __repr__(self):
        return f'<Plan {self.icono} {self.nombre}>'


class PlanFeature(db.Model):
    """
    Relación Plan ↔ Feature con límites opcionales.
    
    Ejemplo: PlanFeature(plan_id=1, feature_id=3, limite=15)
    Significa: "Basic puede usar 'products' con máximo 15 productos"
    """
    __tablename__ = 'plan_features'
    
    id              = db.Column(db.Integer, primary_key=True)
    plan_id         = db.Column(db.Integer, db.ForeignKey('planes.id', ondelete='CASCADE'), nullable=False)
    feature_id      = db.Column(db.Integer, db.ForeignKey('feature_flags.id', ondelete='CASCADE'), nullable=False)
    limite          = db.Column(db.Integer)          # NULL = ilimitado
    config_json     = db.Column(db.JSON, default={})
    
    # Relaciones
    plan            = db.relationship('Plan', back_populates='plan_features')
    feature         = db.relationship('FeatureFlag', back_populates='plan_features')
    
    # Unique constraint
    __table_args__  = (db.UniqueConstraint('plan_id', 'feature_id'),)
    
    def __repr__(self):
        return f'<PlanFeature plan={self.plan_id} feature={self.feature_id} limite={self.limite}>'


class NegocioPlan(db.Model):
    """
    Historial de planes asignados a un negocio.
    Solo 1 registro debe tener activo=TRUE por negocio.
    
    Uso:
        plan_activo = NegocioPlan.query.filter_by(negocio_id=5, activo=True).first()
    """
    __tablename__ = 'negocio_plan'
    
    id              = db.Column(db.Integer, primary_key=True)
    negocio_id      = db.Column(db.Integer, db.ForeignKey('negocios.id_negocio', ondelete='CASCADE'), nullable=False)
    plan_id         = db.Column(db.Integer, db.ForeignKey('planes.id'), nullable=False)
    fecha_inicio    = db.Column(db.DateTime, default=datetime.utcnow)
    fecha_fin       = db.Column(db.DateTime)
    activo          = db.Column(db.Boolean, default=True)
    asignado_por    = db.Column(db.String(50), default='admin')
    notas           = db.Column(db.Text)
    created_at      = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relación
    plan            = db.relationship('Plan', back_populates='negocios_plan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'negocio_id': self.negocio_id,
            'plan': self.plan.to_dict() if self.plan else None,
            'fecha_inicio': self.fecha_inicio.isoformat() if self.fecha_inicio else None,
            'fecha_fin': self.fecha_fin.isoformat() if self.fecha_fin else None,
            'activo': self.activo,
            'asignado_por': self.asignado_por,
            'notas': self.notas
        }


# ═══════════════════════════════════════════════════════════════════════════════
# HELPER: Función para verificar features de un negocio
# ═══════════════════════════════════════════════════════════════════════════════

def check_negocio_feature(negocio_id, feature_key):
    """
    Verifica si un negocio tiene acceso a una feature.
    Retorna: { allowed: bool, limite: int|None, reason: str }
    
    Uso:
        result = check_negocio_feature(5, 'cartera')
        if result['allowed']:
            # Tiene acceso
            limite = result['limite']  # None = ilimitado, 15 = max 15
    """
    # 1. Verificar feature flag global
    feature = FeatureFlag.query.filter_by(key=feature_key).first()
    if not feature:
        return {'allowed': False, 'limite': None, 'reason': 'feature_not_found'}
    
    if not feature.activo_global:
        return {'allowed': False, 'limite': None, 'reason': 'feature_disabled_global'}
    
    # 2. Obtener plan del negocio (importar modelo dinámicamente para evitar circular imports)
    from sqlalchemy import text
    result = db.session.execute(
        text("SELECT plan_key FROM negocios WHERE id_negocio = :nid"),
        {'nid': negocio_id}
    ).fetchone()
    
    if not result:
        return {'allowed': False, 'limite': None, 'reason': 'negocio_not_found'}
    
    plan_key = result[0] or 'basic'
    
    # 3. Verificar si el plan incluye la feature
    plan_feature = PlanFeature.query.join(Plan).join(FeatureFlag).filter(
        Plan.key == plan_key,
        FeatureFlag.key == feature_key
    ).first()
    
    if not plan_feature:
        return {'allowed': False, 'limite': None, 'reason': 'plan_upgrade_required', 'current_plan': plan_key}
    
    return {
        'allowed': True,
        'limite': plan_feature.limite,
        'config': plan_feature.config_json,
        'current_plan': plan_key
    }