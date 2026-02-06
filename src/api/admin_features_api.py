# ═══════════════════════════════════════════════════════════════════════════════
# TUKOMERCIO - API: Admin Features + Planes
# ═══════════════════════════════════════════════════════════════════════════════
#
# INSTRUCCIONES:
# 1. Coloca este archivo en: src/api/admin_features_api.py
# 2. Registra en tu __init__.py con safe_register
#
# ENDPOINTS:
#   GET    /api/admin/features              → Listar features (agrupadas por categoría)
#   PUT    /api/admin/features/<id>/toggle  → Activar/desactivar feature
#   PUT    /api/admin/features/<id>         → Editar feature
#   POST   /api/admin/features              → Crear feature nueva
#
#   GET    /api/admin/planes                → Listar planes con features
#   PUT    /api/admin/planes/<id>/features  → Actualizar features de un plan
#   PUT    /api/admin/negocios/<id>/plan    → Asignar plan a un negocio
#   GET    /api/admin/negocios/planes       → Listar negocios con su plan
# ═══════════════════════════════════════════════════════════════════════════════

from flask import Blueprint, jsonify, request, g
from src.extensions import db
from src.models.feature_models_fixed import FeatureFlag, Plan, PlanFeature, NegocioPlan
from sqlalchemy import text
from datetime import datetime

import logging
logger = logging.getLogger(__name__)

admin_features_bp = Blueprint('admin_features', __name__)


# ═══════════════════════════════════════════════════════════════════════════════
# MIDDLEWARE: Verificar que es admin (reutiliza tu lógica existente)
# ═══════════════════════════════════════════════════════════════════════════════

def require_admin(f):
    """Decorador para verificar que el usuario es admin"""
    from functools import wraps
    @wraps(f)
    def wrapper(*args, **kwargs):
        # Reutiliza tu lógica de admin_api.py
        from src.models.administrador import Administrador  # Ajusta el import
        
        # Obtener usuario del token (ajusta según tu auth)
        user_email = getattr(g, 'user_email', None) or getattr(g, 'current_user_email', None)
        
        if not user_email:
            # Intentar obtener del token
            auth_header = request.headers.get('Authorization', '')
            if auth_header.startswith('Bearer '):
                try:
                    import jwt
                    token = auth_header.split(' ')[1]
                    # Ajusta tu secret key
                    from flask import current_app
                    payload = jwt.decode(token, current_app.config.get('SECRET_KEY', 'secret'), algorithms=['HS256'])
                    user_email = payload.get('email') or payload.get('sub')
                except Exception:
                    pass
        
        if not user_email:
            return jsonify({'error': 'No autorizado'}), 401
        
        admin = Administrador.query.filter_by(email=user_email, activo=True).first()
        if not admin:
            return jsonify({'error': 'No eres administrador'}), 403
        
        g.current_admin = admin
        return f(*args, **kwargs)
    return wrapper


# ═══════════════════════════════════════════════════════════════════════════════
# FEATURE FLAGS CRUD
# ═══════════════════════════════════════════════════════════════════════════════

@admin_features_bp.route('/api/admin/features', methods=['GET'])
@require_admin
def list_features():
    """
    Listar todas las features agrupadas por categoría.
    Incluye qué planes tienen cada feature.
    """
    features = FeatureFlag.query.order_by(FeatureFlag.orden, FeatureFlag.categoria).all()
    
    # Agrupar por categoría
    categorias = {}
    for f in features:
        cat = f.categoria or 'general'
        if cat not in categorias:
            categorias[cat] = []
        
        # Obtener qué planes incluyen esta feature
        planes_con_feature = db.session.query(Plan.key, Plan.nombre, PlanFeature.limite).join(
            PlanFeature, PlanFeature.plan_id == Plan.id
        ).filter(
            PlanFeature.feature_id == f.id
        ).order_by(Plan.orden).all()
        
        feature_data = f.to_dict()
        feature_data['planes'] = [
            {'key': p.key, 'nombre': p.nombre, 'limite': p.limite}
            for p in planes_con_feature
        ]
        categorias[cat].append(feature_data)
    
    return jsonify({
        'success': True,
        'categorias': categorias,
        'total': len(features)
    })


@admin_features_bp.route('/api/admin/features/<int:feature_id>/toggle', methods=['PUT'])
@require_admin
def toggle_feature(feature_id):
    """
    Activar o desactivar una feature globalmente.
    Body opcional: { "activo_global": true/false, "visible": true/false }
    """
    feature = FeatureFlag.query.get(feature_id)
    if not feature:
        return jsonify({'error': 'Feature no encontrada'}), 404
    
    data = request.get_json(silent=True) or {}
    
    if 'activo_global' in data:
        feature.activo_global = data['activo_global']
    else:
        # Toggle automático
        feature.activo_global = not feature.activo_global
    
    if 'visible' in data:
        feature.visible = data['visible']
    
    db.session.commit()
    
    estado = "activada" if feature.activo_global else "desactivada"
    logger.info(f"🎛️ Feature '{feature.key}' {estado} por {g.current_admin.email}")
    
    return jsonify({
        'success': True,
        'feature': feature.to_dict(),
        'message': f"Feature '{feature.nombre}' {estado}"
    })


@admin_features_bp.route('/api/admin/features/<int:feature_id>', methods=['PUT'])
@require_admin
def update_feature(feature_id):
    """Editar datos de una feature (nombre, descripcion, icono, etc.)"""
    feature = FeatureFlag.query.get(feature_id)
    if not feature:
        return jsonify({'error': 'Feature no encontrada'}), 404
    
    data = request.get_json(silent=True) or {}
    
    # Campos editables (key NO se puede cambiar)
    for field in ['nombre', 'descripcion', 'categoria', 'icono', 'orden', 'activo_global', 'visible']:
        if field in data:
            setattr(feature, field, data[field])
    
    db.session.commit()
    
    return jsonify({
        'success': True,
        'feature': feature.to_dict()
    })


@admin_features_bp.route('/api/admin/features', methods=['POST'])
@require_admin
def create_feature():
    """Crear una nueva feature flag"""
    data = request.get_json(silent=True) or {}
    
    if not data.get('key') or not data.get('nombre'):
        return jsonify({'error': 'key y nombre son obligatorios'}), 400
    
    # Verificar que el key no exista
    if FeatureFlag.query.filter_by(key=data['key']).first():
        return jsonify({'error': f"Ya existe una feature con key '{data['key']}'"}), 400
    
    feature = FeatureFlag(
        key=data['key'],
        nombre=data['nombre'],
        descripcion=data.get('descripcion'),
        categoria=data.get('categoria', 'general'),
        activo_global=data.get('activo_global', True),
        visible=data.get('visible', True),
        icono=data.get('icono'),
        orden=data.get('orden', 0)
    )
    
    db.session.add(feature)
    db.session.commit()
    
    logger.info(f"🆕 Feature '{feature.key}' creada por {g.current_admin.email}")
    
    return jsonify({
        'success': True,
        'feature': feature.to_dict()
    }), 201


# ═══════════════════════════════════════════════════════════════════════════════
# PLANES CRUD
# ═══════════════════════════════════════════════════════════════════════════════

@admin_features_bp.route('/api/admin/planes', methods=['GET'])
@require_admin
def list_planes():
    """Listar todos los planes con sus features incluidas"""
    planes = Plan.query.order_by(Plan.orden).all()
    
    return jsonify({
        'success': True,
        'planes': [p.to_dict(include_features=True) for p in planes]
    })


@admin_features_bp.route('/api/admin/planes/<int:plan_id>/features', methods=['PUT'])
@require_admin
def update_plan_features(plan_id):
    """
    Actualizar las features de un plan.
    
    Body:
    {
        "features": [
            { "feature_key": "cartera", "limite": null },
            { "feature_key": "products", "limite": 100 },
            { "feature_key": "store_designer", "limite": null }
        ]
    }
    """
    plan = Plan.query.get(plan_id)
    if not plan:
        return jsonify({'error': 'Plan no encontrado'}), 404
    
    data = request.get_json(silent=True) or {}
    features_data = data.get('features', [])
    
    # Eliminar asignaciones anteriores de este plan
    PlanFeature.query.filter_by(plan_id=plan.id).delete()
    
    # Crear nuevas asignaciones
    for fd in features_data:
        feature = FeatureFlag.query.filter_by(key=fd.get('feature_key')).first()
        if feature:
            pf = PlanFeature(
                plan_id=plan.id,
                feature_id=feature.id,
                limite=fd.get('limite'),
                config_json=fd.get('config', {})
            )
            db.session.add(pf)
    
    db.session.commit()
    
    logger.info(f"📊 Plan '{plan.nombre}' actualizado con {len(features_data)} features por {g.current_admin.email}")
    
    return jsonify({
        'success': True,
        'plan': plan.to_dict(include_features=True),
        'message': f"Plan '{plan.nombre}' actualizado con {len(features_data)} features"
    })


# ═══════════════════════════════════════════════════════════════════════════════
# ASIGNACIÓN DE PLANES A NEGOCIOS
# ═══════════════════════════════════════════════════════════════════════════════

@admin_features_bp.route('/api/admin/negocios/<int:negocio_id>/plan', methods=['PUT'])
@require_admin
def assign_plan_to_negocio(negocio_id):
    """
    Asignar o cambiar el plan de un negocio.
    
    Body: { "plan_key": "pro", "notas": "Upgrade por promo" }
    """
    data = request.get_json(silent=True) or {}
    plan_key = data.get('plan_key')
    
    if not plan_key:
        return jsonify({'error': 'plan_key es obligatorio'}), 400
    
    # Verificar que el plan existe
    plan = Plan.query.filter_by(key=plan_key, activo=True).first()
    if not plan:
        return jsonify({'error': f"Plan '{plan_key}' no encontrado o inactivo"}), 404
    
    # Verificar que el negocio existe
    negocio = db.session.execute(
        text("SELECT id_negocio, nombre_negocio FROM negocios WHERE id_negocio = :nid"),
        {'nid': negocio_id}
    ).fetchone()
    
    if not negocio:
        return jsonify({'error': 'Negocio no encontrado'}), 404
    
    # Desactivar plan anterior
    NegocioPlan.query.filter_by(negocio_id=negocio_id, activo=True).update({'activo': False})
    
    # Crear nuevo registro de plan
    nuevo_plan = NegocioPlan(
        negocio_id=negocio_id,
        plan_id=plan.id,
        activo=True,
        asignado_por='admin',
        notas=data.get('notas', f'Asignado por {g.current_admin.email}')
    )
    db.session.add(nuevo_plan)
    
    # Actualizar cache en negocios
    db.session.execute(
        text("UPDATE negocios SET plan_key = :pk, plan_actual_id = :pid WHERE id_negocio = :nid"),
        {'pk': plan_key, 'pid': plan.id, 'nid': negocio_id}
    )
    
    db.session.commit()
    
    logger.info(f"📊 Negocio {negocio_id} ({negocio[1]}) → Plan '{plan.nombre}' por {g.current_admin.email}")
    
    return jsonify({
        'success': True,
        'negocio_id': negocio_id,
        'negocio_nombre': negocio[1],
        'plan': plan.to_dict(),
        'message': f"Plan '{plan.nombre}' asignado a '{negocio[1]}'"
    })


@admin_features_bp.route('/api/admin/negocios/planes', methods=['GET'])
@require_admin
def list_negocios_with_plans():
    """
    Listar negocios con su plan actual.
    Query params: ?plan=pro&page=1&limit=20
    """
    plan_filter = request.args.get('plan')
    page = int(request.args.get('page', 1))
    limit = int(request.args.get('limit', 20))
    offset = (page - 1) * limit
    
    # Query base
    query = """
        SELECT n.id_negocio, n.nombre_negocio, n.slug, n.plan_key, 
               n.activo, n.ciudad, p.nombre as plan_nombre, p.color as plan_color,
               p.icono as plan_icono
        FROM negocios n
        LEFT JOIN planes p ON n.plan_actual_id = p.id
    """
    params = {}
    
    if plan_filter:
        query += " WHERE n.plan_key = :plan"
        params['plan'] = plan_filter
    
    query += " ORDER BY n.fecha_registro DESC LIMIT :limit OFFSET :offset"
    params['limit'] = limit
    params['offset'] = offset
    
    negocios = db.session.execute(text(query), params).fetchall()
    
    # Contar total
    count_query = "SELECT COUNT(*) FROM negocios"
    if plan_filter:
        count_query += " WHERE plan_key = :plan"
    total = db.session.execute(text(count_query), params if plan_filter else {}).scalar()
    
    # Stats por plan
    stats = db.session.execute(text("""
        SELECT COALESCE(plan_key, 'basic') as plan, COUNT(*) as cantidad
        FROM negocios GROUP BY plan_key ORDER BY cantidad DESC
    """)).fetchall()
    
    return jsonify({
        'success': True,
        'negocios': [{
            'id': n[0],
            'nombre': n[1],
            'slug': n[2],
            'plan_key': n[3] or 'basic',
            'activo': n[4],
            'ciudad': n[5],
            'plan_nombre': n[6] or 'Basic',
            'plan_color': n[7] or '#22c55e',
            'plan_icono': n[8] or '🌱'
        } for n in negocios],
        'total': total,
        'page': page,
        'limit': limit,
        'stats_por_plan': [{'plan': s[0] or 'basic', 'cantidad': s[1]} for s in stats]
    })


# ═══════════════════════════════════════════════════════════════════════════════
# ENDPOINTS PÚBLICOS (para el frontend de cada negocio)
# ═══════════════════════════════════════════════════════════════════════════════

@admin_features_bp.route('/api/features/my', methods=['GET'])
def get_my_features():
    """
    Obtener las features disponibles para el negocio actual.
    El frontend llama esto una vez al cargar la app y cachea el resultado.
    
    Header requerido: Authorization: Bearer <token>
    Header opcional:  X-Negocio-Id: <id>
    """
    # Obtener negocio_id del contexto (ajusta según tu auth)
    negocio_id = request.headers.get('X-Negocio-Id') or request.args.get('negocio_id')
    
    if not negocio_id:
        # Intentar obtener del token
        auth_header = request.headers.get('Authorization', '')
        if auth_header.startswith('Bearer '):
            try:
                import jwt
                from flask import current_app
                token = auth_header.split(' ')[1]
                payload = jwt.decode(token, current_app.config.get('SECRET_KEY', 'secret'), algorithms=['HS256'])
                negocio_id = payload.get('negocio_id')
            except Exception:
                pass
    
    if not negocio_id:
        return jsonify({'error': 'negocio_id requerido'}), 400
    
    # Obtener plan del negocio
    negocio = db.session.execute(
        text("SELECT plan_key FROM negocios WHERE id_negocio = :nid"),
        {'nid': int(negocio_id)}
    ).fetchone()
    
    plan_key = (negocio[0] if negocio else None) or 'basic'
    
    # Obtener TODAS las features visibles
    all_features = FeatureFlag.query.filter_by(visible=True).order_by(FeatureFlag.orden).all()
    
    # Obtener features del plan del negocio
    plan_features = db.session.query(
        FeatureFlag.key, PlanFeature.limite, PlanFeature.config_json
    ).join(
        PlanFeature, PlanFeature.feature_id == FeatureFlag.id
    ).join(
        Plan, Plan.id == PlanFeature.plan_id
    ).filter(
        Plan.key == plan_key
    ).all()
    
    plan_feature_map = {pf[0]: {'limite': pf[1], 'config': pf[2]} for pf in plan_features}
    
    # Construir respuesta
    features_response = []
    for f in all_features:
        in_plan = f.key in plan_feature_map
        features_response.append({
            'key': f.key,
            'nombre': f.nombre,
            'categoria': f.categoria,
            'icono': f.icono,
            'visible': f.visible,
            'allowed': f.activo_global and in_plan,  # Activo global + en su plan
            'limite': plan_feature_map[f.key]['limite'] if in_plan else None,
            'locked_reason': None if (f.activo_global and in_plan) else 
                            'disabled' if not f.activo_global else 'upgrade'
        })
    
    return jsonify({
        'success': True,
        'plan': plan_key,
        'features': features_response
    })


@admin_features_bp.route('/api/features/check/<feature_key>', methods=['GET'])
def check_feature(feature_key):
    """
    Verificar acceso rápido a una feature específica.
    GET /api/features/check/cartera?negocio_id=5
    """
    negocio_id = request.args.get('negocio_id') or request.headers.get('X-Negocio-Id')
    
    if not negocio_id:
        return jsonify({'error': 'negocio_id requerido'}), 400
    
    from src.models.feature_models_fixed import check_negocio_feature
    result = check_negocio_feature(int(negocio_id), feature_key)
    
    return jsonify(result)


@admin_features_bp.route('/api/planes', methods=['GET'])
def list_public_planes():
    """
    Listar planes disponibles (para página de pricing pública).
    No requiere autenticación.
    """
    planes = Plan.query.filter_by(activo=True).order_by(Plan.orden).all()
    
    return jsonify({
        'success': True,
        'planes': [p.to_dict(include_features=True) for p in planes]
    })