# ═══════════════════════════════════════════════════════════════════════════════
# TUKOMERCIO - API: Admin Features + Planes
# v2.0 - Usa Flask-Login (mismo auth que admin_api.py)
# ═══════════════════════════════════════════════════════════════════════════════

from flask import Blueprint, request, jsonify, g, make_response
from flask_login import current_user, login_required
from functools import wraps
from src.models import db
from src.models.feature_models import FeatureFlag, Plan, PlanFeature, NegocioPlan
from sqlalchemy import text
from datetime import datetime
import os
import logging

logger = logging.getLogger(__name__)

admin_features_bp = Blueprint('admin_features', __name__)


# ═══════════════════════════════════════════════════════════════════════════════
# CORS (idéntico a admin_api.py)
# ═══════════════════════════════════════════════════════════════════════════════

ALLOWED_ORIGINS = [
    "https://tuko.pages.dev",
    "https://trayectoria-rxdc1.web.app",
    "https://mitrayectoria.web.app",
    "http://localhost:5001",
    "http://localhost:5173",
    "http://localhost:3000"
]


@admin_features_bp.before_request
def handle_preflight():
    if request.method == 'OPTIONS':
        response = make_response('', 204)
        origin = request.headers.get('Origin', '')
        if origin in ALLOWED_ORIGINS:
            response.headers['Access-Control-Allow-Origin'] = origin
            response.headers['Access-Control-Allow-Credentials'] = 'true'
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS, PUT, DELETE'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, Accept'
        response.headers['Access-Control-Max-Age'] = '3600'
        return response


@admin_features_bp.after_request
def add_cors_headers(response):
    origin = request.headers.get('Origin', '')
    if origin in ALLOWED_ORIGINS:
        response.headers['Access-Control-Allow-Origin'] = origin
        response.headers['Access-Control-Allow-Credentials'] = 'true'
    return response


# ═══════════════════════════════════════════════════════════════════════════════
# AUTH (idéntico a admin_api.py - Flask-Login + psycopg2)
# ═══════════════════════════════════════════════════════════════════════════════

def get_current_user_email():
    if current_user.is_authenticated:
        return current_user.correo.lower() if current_user.correo else None
    return None


def is_admin(email):
    if not email:
        return False, None
    try:
        import psycopg2
        from psycopg2.extras import RealDictCursor
        DATABASE_URL = os.environ.get('DATABASE_URL')
        conn = psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)
        cur = conn.cursor()
        cur.execute("""
            SELECT id, email, nombre, rol, permisos, activo
            FROM administradores WHERE LOWER(email) = LOWER(%s) AND activo = true
        """, (email,))
        admin = cur.fetchone()
        cur.close()
        conn.close()
        if admin:
            return True, dict(admin)
        return False, None
    except Exception as e:
        logger.error(f"Error verificando admin: {e}")
        return False, None


def admin_required(f):
    @wraps(f)
    @login_required
    def decorated(*args, **kwargs):
        email = get_current_user_email()
        if not email:
            return jsonify({'error': 'No autorizado', 'is_admin': False}), 401
        is_adm, admin_data = is_admin(email)
        if not is_adm:
            return jsonify({'error': 'No eres administrador', 'is_admin': False}), 403
        g.user_email = email
        g.current_admin = admin_data
        return f(*args, **kwargs)
    return decorated


# ═══════════════════════════════════════════════════════════════════════════════
# FEATURE FLAGS CRUD
# ═══════════════════════════════════════════════════════════════════════════════

@admin_features_bp.route('/api/admin/features', methods=['GET', 'OPTIONS'])
@admin_required
def list_features():
    features = FeatureFlag.query.order_by(FeatureFlag.orden, FeatureFlag.categoria).all()
    categorias = {}
    for f in features:
        cat = f.categoria or 'general'
        if cat not in categorias:
            categorias[cat] = []
        planes_con_feature = db.session.query(Plan.key, Plan.nombre, PlanFeature.limite).join(
            PlanFeature, PlanFeature.plan_id == Plan.id
        ).filter(PlanFeature.feature_id == f.id).order_by(Plan.orden).all()
        feature_data = f.to_dict()
        feature_data['planes'] = [{'key': p.key, 'nombre': p.nombre, 'limite': p.limite} for p in planes_con_feature]
        categorias[cat].append(feature_data)
    return jsonify({'success': True, 'categorias': categorias, 'total': len(features)})


@admin_features_bp.route('/api/admin/features/<int:feature_id>/toggle', methods=['PUT', 'OPTIONS'])
@admin_required
def toggle_feature(feature_id):
    feature = FeatureFlag.query.get(feature_id)
    if not feature:
        return jsonify({'error': 'Feature no encontrada'}), 404
    data = request.get_json(silent=True) or {}
    if 'activo_global' in data:
        feature.activo_global = data['activo_global']
    else:
        feature.activo_global = not feature.activo_global
    if 'visible' in data:
        feature.visible = data['visible']
    db.session.commit()
    estado = "activada" if feature.activo_global else "desactivada"
    logger.info(f"🎛️ Feature '{feature.key}' {estado} por {g.user_email}")
    return jsonify({'success': True, 'feature': feature.to_dict(), 'message': f"Feature '{feature.nombre}' {estado}"})


@admin_features_bp.route('/api/admin/features/<int:feature_id>', methods=['PUT', 'OPTIONS'])
@admin_required
def update_feature(feature_id):
    feature = FeatureFlag.query.get(feature_id)
    if not feature:
        return jsonify({'error': 'Feature no encontrada'}), 404
    data = request.get_json(silent=True) or {}
    for field in ['nombre', 'descripcion', 'categoria', 'icono', 'orden', 'activo_global', 'visible']:
        if field in data:
            setattr(feature, field, data[field])
    db.session.commit()
    return jsonify({'success': True, 'feature': feature.to_dict()})


@admin_features_bp.route('/api/admin/features', methods=['POST', 'OPTIONS'])
@admin_required
def create_feature():
    data = request.get_json(silent=True) or {}
    if not data.get('key') or not data.get('nombre'):
        return jsonify({'error': 'key y nombre son obligatorios'}), 400
    if FeatureFlag.query.filter_by(key=data['key']).first():
        return jsonify({'error': f"Ya existe feature con key '{data['key']}'"}), 400
    feature = FeatureFlag(
        key=data['key'], nombre=data['nombre'],
        descripcion=data.get('descripcion'), categoria=data.get('categoria', 'general'),
        activo_global=data.get('activo_global', True), visible=data.get('visible', True),
        icono=data.get('icono'), orden=data.get('orden', 0)
    )
    db.session.add(feature)
    db.session.commit()
    return jsonify({'success': True, 'feature': feature.to_dict()}), 201


# ═══════════════════════════════════════════════════════════════════════════════
# PLANES CRUD
# ═══════════════════════════════════════════════════════════════════════════════

@admin_features_bp.route('/api/admin/planes', methods=['GET', 'OPTIONS'])
@admin_required
def list_planes():
    planes = Plan.query.order_by(Plan.orden).all()
    return jsonify({'success': True, 'planes': [p.to_dict(include_features=True) for p in planes]})


@admin_features_bp.route('/api/admin/planes/<int:plan_id>/features', methods=['PUT', 'OPTIONS'])
@admin_required
def update_plan_features(plan_id):
    plan = Plan.query.get(plan_id)
    if not plan:
        return jsonify({'error': 'Plan no encontrado'}), 404
    data = request.get_json(silent=True) or {}
    features_data = data.get('features', [])
    PlanFeature.query.filter_by(plan_id=plan.id).delete()
    for fd in features_data:
        feature = FeatureFlag.query.filter_by(key=fd.get('feature_key')).first()
        if feature:
            pf = PlanFeature(plan_id=plan.id, feature_id=feature.id, limite=fd.get('limite'), config_json=fd.get('config', {}))
            db.session.add(pf)
    db.session.commit()
    return jsonify({'success': True, 'plan': plan.to_dict(include_features=True), 'message': f"Plan '{plan.nombre}' actualizado"})


# ═══════════════════════════════════════════════════════════════════════════════
# ASIGNACIÓN DE PLANES A NEGOCIOS
# ═══════════════════════════════════════════════════════════════════════════════

@admin_features_bp.route('/api/admin/negocios/<int:negocio_id>/plan', methods=['PUT', 'OPTIONS'])
@admin_required
def assign_plan_to_negocio(negocio_id):
    data = request.get_json(silent=True) or {}
    plan_key = data.get('plan_key')
    if not plan_key:
        return jsonify({'error': 'plan_key es obligatorio'}), 400
    plan = Plan.query.filter_by(key=plan_key, activo=True).first()
    if not plan:
        return jsonify({'error': f"Plan '{plan_key}' no encontrado"}), 404
    negocio = db.session.execute(text("SELECT id_negocio, nombre_negocio FROM negocios WHERE id_negocio = :nid"), {'nid': negocio_id}).fetchone()
    if not negocio:
        return jsonify({'error': 'Negocio no encontrado'}), 404
    NegocioPlan.query.filter_by(negocio_id=negocio_id, activo=True).update({'activo': False})
    nuevo_plan = NegocioPlan(negocio_id=negocio_id, plan_id=plan.id, activo=True, asignado_por='admin', notas=data.get('notas', f'Asignado por {g.user_email}'))
    db.session.add(nuevo_plan)
    db.session.execute(text("UPDATE negocios SET plan_key = :pk, plan_actual_id = :pid WHERE id_negocio = :nid"), {'pk': plan_key, 'pid': plan.id, 'nid': negocio_id})
    db.session.commit()
    logger.info(f"📊 Negocio {negocio_id} → Plan '{plan.nombre}' por {g.user_email}")
    return jsonify({'success': True, 'negocio_id': negocio_id, 'negocio_nombre': negocio[1], 'plan': plan.to_dict(), 'message': f"Plan '{plan.nombre}' asignado a '{negocio[1]}'"})


@admin_features_bp.route('/api/admin/negocios/planes', methods=['GET', 'OPTIONS'])
@admin_required
def list_negocios_with_plans():
    plan_filter = request.args.get('plan')
    page = int(request.args.get('page', 1))
    limit = int(request.args.get('limit', 20))
    offset = (page - 1) * limit
    
    query = """
        SELECT n.id_negocio, n.nombre_negocio, n.slug, n.plan_key,
               n.activo, n.ciudad, p.nombre as plan_nombre, p.color as plan_color, p.icono as plan_icono
        FROM negocios n LEFT JOIN planes p ON n.plan_actual_id = p.id
    """
    params = {}
    if plan_filter:
        query += " WHERE n.plan_key = :plan"
        params['plan'] = plan_filter
    query += " ORDER BY n.fecha_registro DESC LIMIT :limit OFFSET :offset"
    params['limit'] = limit
    params['offset'] = offset
    
    negocios = db.session.execute(text(query), params).fetchall()
    count_query = "SELECT COUNT(*) FROM negocios"
    if plan_filter:
        count_query += " WHERE plan_key = :plan"
    total = db.session.execute(text(count_query), {'plan': plan_filter} if plan_filter else {}).scalar()
    stats = db.session.execute(text("SELECT COALESCE(plan_key, 'basic') as plan, COUNT(*) as cantidad FROM negocios GROUP BY plan_key ORDER BY cantidad DESC")).fetchall()
    
    return jsonify({
        'success': True,
        'negocios': [{'id': n[0], 'nombre': n[1], 'slug': n[2], 'plan_key': n[3] or 'basic', 'activo': n[4], 'ciudad': n[5], 'plan_nombre': n[6] or 'Basic', 'plan_color': n[7] or '#22c55e', 'plan_icono': n[8] or '🌱'} for n in negocios],
        'total': total, 'page': page, 'limit': limit,
        'stats_por_plan': [{'plan': s[0] or 'basic', 'cantidad': s[1]} for s in stats]
    })


# ═══════════════════════════════════════════════════════════════════════════════
# ENDPOINTS PÚBLICOS (sin auth de admin)
# ═══════════════════════════════════════════════════════════════════════════════

@admin_features_bp.route('/api/features/my', methods=['GET', 'OPTIONS'])
def get_my_features():
    negocio_id = request.headers.get('X-Negocio-Id') or request.args.get('negocio_id')
    if not negocio_id and current_user.is_authenticated:
        result = db.session.execute(text("SELECT id_negocio FROM negocios WHERE usuario_id = :uid LIMIT 1"), {'uid': current_user.id}).fetchone()
        if result:
            negocio_id = result[0]

    # Si hay negocio, obtener su plan; si no, plan = None (sin negocio)
    plan_key = None
    if negocio_id:
        negocio = db.session.execute(text("SELECT plan_key FROM negocios WHERE id_negocio = :nid"), {'nid': int(negocio_id)}).fetchone()
        plan_key = (negocio[0] if negocio else None) or 'basic'

    all_features = FeatureFlag.query.filter_by(visible=True).order_by(FeatureFlag.orden).all()

    # Obtener features del plan (vacío si no hay negocio/plan)
    plan_feature_map = {}
    if plan_key:
        plan_features = db.session.query(FeatureFlag.key, PlanFeature.limite, PlanFeature.config_json).join(
            PlanFeature, PlanFeature.feature_id == FeatureFlag.id
        ).join(Plan, Plan.id == PlanFeature.plan_id).filter(Plan.key == plan_key).all()
        plan_feature_map = {pf[0]: {'limite': pf[1], 'config': pf[2]} for pf in plan_features}

    features_response = []
    for f in all_features:
        in_plan = f.key in plan_feature_map

        # Si activo_global=false → disabled (oculto para TODOS, con o sin negocio)
        # Si activo_global=true pero no tiene negocio → upgrade
        # Si activo_global=true y tiene negocio pero no en plan → upgrade
        # Si activo_global=true y en plan → allowed
        if not f.activo_global:
            locked_reason = 'disabled'
            allowed = False
        elif not plan_key:
            # Sin negocio: mostrar como upgrade (no ocultar)
            locked_reason = 'upgrade'
            allowed = False
        elif in_plan:
            locked_reason = None
            allowed = True
        else:
            locked_reason = 'upgrade'
            allowed = False

        features_response.append({
            'key': f.key, 'nombre': f.nombre, 'categoria': f.categoria, 'icono': f.icono,
            'allowed': allowed,
            'limite': plan_feature_map[f.key]['limite'] if in_plan else None,
            'locked_reason': locked_reason
        })
    return jsonify({'success': True, 'plan': plan_key or 'none', 'features': features_response})


@admin_features_bp.route('/api/features/check/<feature_key>', methods=['GET', 'OPTIONS'])
def check_feature(feature_key):
    negocio_id = request.args.get('negocio_id') or request.headers.get('X-Negocio-Id')
    if not negocio_id:
        return jsonify({'error': 'negocio_id requerido'}), 400
    from src.models.feature_models import check_negocio_feature
    return jsonify(check_negocio_feature(int(negocio_id), feature_key))


@admin_features_bp.route('/api/planes', methods=['GET', 'OPTIONS'])
def list_public_planes():
    planes = Plan.query.filter_by(activo=True).order_by(Plan.orden).all()
    return jsonify({'success': True, 'planes': [p.to_dict(include_features=True) for p in planes]})