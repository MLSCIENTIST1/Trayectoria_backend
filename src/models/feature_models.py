# ═══════════════════════════════════════════════════════════════════════════════
# TUKOMERCIO - Modelos: Feature Flags + Planes
# ═══════════════════════════════════════════════════════════════════════════════
#
# Archivo: src/models/feature_models.py
# Versión: 2.0 — con check_feature_access + check_limit
# ═══════════════════════════════════════════════════════════════════════════════

from datetime import datetime
from src.models.database import db

import logging
logger = logging.getLogger(__name__)


class FeatureFlag(db.Model):
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
    
    plan_features   = db.relationship('PlanFeature', back_populates='plan', lazy='dynamic')
    negocios_plan   = db.relationship('NegocioPlan', back_populates='plan', lazy='dynamic')
    
    def get_feature_keys(self):
        return [pf.feature.key for pf in self.plan_features.all() if pf.feature]
    
    def has_feature(self, feature_key):
        return PlanFeature.query.join(FeatureFlag).filter(
            PlanFeature.plan_id == self.id,
            FeatureFlag.key == feature_key
        ).first() is not None
    
    def get_feature_limit(self, feature_key):
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
    __tablename__ = 'plan_features'
    
    id              = db.Column(db.Integer, primary_key=True)
    plan_id         = db.Column(db.Integer, db.ForeignKey('planes.id', ondelete='CASCADE'), nullable=False)
    feature_id      = db.Column(db.Integer, db.ForeignKey('feature_flags.id', ondelete='CASCADE'), nullable=False)
    limite          = db.Column(db.Integer)
    config_json     = db.Column(db.JSON, default={})
    
    plan            = db.relationship('Plan', back_populates='plan_features')
    feature         = db.relationship('FeatureFlag', back_populates='plan_features')
    
    __table_args__  = (db.UniqueConstraint('plan_id', 'feature_id'),)
    
    def __repr__(self):
        return f'<PlanFeature plan={self.plan_id} feature={self.feature_id} limite={self.limite}>'


class NegocioPlan(db.Model):
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
# HELPERS: Funciones de verificación de features
# ═══════════════════════════════════════════════════════════════════════════════

def check_negocio_feature(negocio_id, feature_key):
    """
    Verifica si un negocio tiene acceso a una feature.
    Retorna: { allowed: bool, limite: int|None, reason: str, current_plan: str }
    """
    feature = FeatureFlag.query.filter_by(key=feature_key).first()
    if not feature:
        return {'allowed': False, 'limite': None, 'reason': 'feature_not_found'}
    
    if not feature.activo_global:
        return {'allowed': False, 'limite': None, 'reason': 'feature_disabled_global'}
    
    from sqlalchemy import text
    result = db.session.execute(
        text("SELECT plan_key FROM negocios WHERE id_negocio = :nid"),
        {'nid': negocio_id}
    ).fetchone()
    
    if not result:
        return {'allowed': False, 'limite': None, 'reason': 'negocio_not_found'}
    
    plan_key = result[0] or 'basic'
    
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


def check_feature_access(feature_key, negocio_id):
    """
    Verificación SIMPLE: ¿el negocio tiene acceso a esta feature?
    Retorna: True o False
    
    Uso:
        if not check_feature_access('inv_videos', negocio_id):
            videos = []
    """
    try:
        result = check_negocio_feature(int(negocio_id), feature_key)
        return result.get('allowed', False)
    except Exception as e:
        logger.warning(f"⚠️ check_feature_access('{feature_key}', {negocio_id}): {e}")
        return True  # Fail-open


def check_limit(feature_key, negocio_id, model_class, filter_column):
    """
    Verifica si el negocio alcanzó el límite de una feature.
    
    Retorna:
        None → permitido
        (Response, status_code) → bloqueado, retornar directo
    
    Uso:
        limit_error = check_limit('crear_producto', negocio_id, ProductoCatalogo, 'negocio_id')
        if limit_error:
            return limit_error
    """
    from flask import jsonify
    
    try:
        result = check_negocio_feature(int(negocio_id), feature_key)
        
        if not result.get('allowed', False):
            reason = result.get('reason', 'unknown')
            
            if reason == 'feature_not_found':
                logger.warning(f"⚠️ check_limit: feature '{feature_key}' no encontrada en BD")
                return None  # Fail-open
            
            if reason == 'feature_disabled_global':
                return jsonify({
                    'success': False,
                    'error': 'FEATURE_DISABLED',
                    'message': 'Esta funcionalidad no está disponible actualmente',
                    'feature': feature_key
                }), 403
            
            return jsonify({
                'success': False,
                'error': 'PLAN_UPGRADE_REQUIRED',
                'message': 'Tu plan actual no incluye esta funcionalidad',
                'feature': feature_key,
                'current_plan': result.get('current_plan', 'basic')
            }), 403
        
        # Verificar límite
        limite = result.get('limite')
        if limite is None:
            return None  # Ilimitado
        
        try:
            count = model_class.query.filter(
                getattr(model_class, filter_column) == int(negocio_id)
            ).count()
        except Exception as e:
            logger.warning(f"⚠️ check_limit count error: {e}")
            return None  # Fail-open
        
        if count >= limite:
            return jsonify({
                'success': False,
                'error': 'LIMIT_REACHED',
                'message': f'Has alcanzado el límite de tu plan ({count}/{limite})',
                'feature': feature_key,
                'current_count': count,
                'limit': limite,
                'current_plan': result.get('current_plan', 'basic')
            }), 403
        
        return None  # Dentro del límite
        
    except Exception as e:
        logger.warning(f"⚠️ check_limit('{feature_key}', {negocio_id}): {e}")
        return None  # Fail-open