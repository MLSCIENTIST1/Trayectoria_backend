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
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, Accept, X-User-ID, X-Business-ID, X-Negocio-Id, X-Session-FP, Cache-Control, Pragma'

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


# ═══════════════════════════════════════════════════════════════════════════════
# FEATURE FLAGS v2 (A39): rollout por % + overrides por negocio
# ═══════════════════════════════════════════════════════════════════════════════
@admin_features_bp.route('/api/admin/features/<int:feature_id>/rollout', methods=['PUT', 'OPTIONS'])
@admin_required
def set_feature_rollout(feature_id):
    """PUT /api/admin/features/<id>/rollout  body: { rollout_pct: 0-100 }"""
    if request.method == 'OPTIONS':
        return jsonify({'success': True}), 200
    feature = FeatureFlag.query.get(feature_id)
    if not feature:
        return jsonify({'error': 'Feature no encontrada'}), 404
    try:
        pct = int((request.get_json(silent=True) or {}).get('rollout_pct'))
    except (TypeError, ValueError):
        return jsonify({'error': 'rollout_pct debe ser un número'}), 400
    if not (0 <= pct <= 100):
        return jsonify({'error': 'rollout_pct fuera de rango (0-100)'}), 400
    antes = feature.rollout_pct
    feature.rollout_pct = pct
    db.session.commit()
    try:
        from src.api.admin_api import registrar_auditoria
        registrar_auditoria('editar', 'feature_flag', feature_id,
                            {'key': feature.key, 'rollout_pct': {'antes': antes, 'despues': pct}})
    except Exception:
        pass
    logger.info(f"🎚️ Rollout de '{feature.key}' → {pct}% por {g.user_email}")
    return jsonify({'success': True, 'feature': feature.to_dict(),
                    'message': f"Rollout de '{feature.nombre}' al {pct}%"})


@admin_features_bp.route('/api/admin/features/<feature_key>/overrides', methods=['GET', 'OPTIONS'])
@admin_required
def list_feature_overrides(feature_key):
    """GET /api/admin/features/<key>/overrides → overrides por negocio de esa feature."""
    if request.method == 'OPTIONS':
        return jsonify({'success': True}), 200
    try:
        from src.models.feature_models import FeatureOverride
        from sqlalchemy import text as _t
        ovs = FeatureOverride.query.filter_by(feature_key=feature_key).order_by(FeatureOverride.created_at.desc()).all()
        # nombres de negocio
        ids = [o.negocio_id for o in ovs]
        nombres = {}
        if ids:
            for r in db.session.execute(_t(
                "SELECT id_negocio, nombre_negocio FROM negocios WHERE id_negocio = ANY(:ids)"),
                {'ids': ids}).fetchall():
                nombres[r[0]] = r[1]
        return jsonify({'success': True, 'overrides': [{
            'negocio_id': o.negocio_id, 'nombre': nombres.get(o.negocio_id, f'#{o.negocio_id}'),
            'habilitado': o.habilitado, 'created_by': o.created_by,
        } for o in ovs]})
    except Exception as e:
        logger.error(f"Error listando overrides {feature_key}: {e}")
        return jsonify({'success': False, 'error': str(e), 'overrides': []}), 200


@admin_features_bp.route('/api/admin/features/override', methods=['POST', 'OPTIONS'])
@admin_required
def upsert_feature_override():
    """POST /api/admin/features/override  body: { negocio_id, feature_key, habilitado }"""
    if request.method == 'OPTIONS':
        return jsonify({'success': True}), 200
    try:
        from src.models.feature_models import FeatureOverride, FeatureFlag as _FF
        data = request.get_json(silent=True) or {}
        try:
            nid = int(data.get('negocio_id'))
        except (TypeError, ValueError):
            return jsonify({'error': 'negocio_id inválido'}), 400
        fkey = (data.get('feature_key') or '').strip()
        if not fkey or not _FF.query.filter_by(key=fkey).first():
            return jsonify({'error': 'feature_key inválida'}), 400
        if not db.session.execute(text("SELECT 1 FROM negocios WHERE id_negocio=:n"), {'n': nid}).fetchone():
            return jsonify({'error': 'Negocio no encontrado'}), 404
        habilitado = bool(data.get('habilitado'))
        ov = FeatureOverride.query.filter_by(negocio_id=nid, feature_key=fkey).first()
        if ov:
            ov.habilitado = habilitado
        else:
            ov = FeatureOverride(negocio_id=nid, feature_key=fkey, habilitado=habilitado,
                                 created_by=g.user_email)
            db.session.add(ov)
        db.session.commit()
        try:
            from src.api.admin_api import registrar_auditoria
            registrar_auditoria('editar', 'feature_override', nid,
                                {'feature_key': fkey, 'habilitado': habilitado})
        except Exception:
            pass
        return jsonify({'success': True, 'message': f"Override de '{fkey}' para negocio {nid}: {'ON' if habilitado else 'OFF'}"})
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error en upsert_feature_override: {e}")
        return jsonify({'error': str(e)}), 500


@admin_features_bp.route('/api/admin/features/override', methods=['DELETE'])
@admin_required
def delete_feature_override():
    """DELETE /api/admin/features/override  body: { negocio_id, feature_key } → quita el override (vuelve a plan/rollout)."""
    try:
        from src.models.feature_models import FeatureOverride
        data = request.get_json(silent=True) or {}
        nid = int(data.get('negocio_id'))
        fkey = (data.get('feature_key') or '').strip()
        ov = FeatureOverride.query.filter_by(negocio_id=nid, feature_key=fkey).first()
        if not ov:
            return jsonify({'error': 'Override no encontrado'}), 404
        db.session.delete(ov)
        db.session.commit()
        try:
            from src.api.admin_api import registrar_auditoria
            registrar_auditoria('eliminar', 'feature_override', nid, {'feature_key': fkey})
        except Exception:
            pass
        return jsonify({'success': True, 'message': 'Override eliminado'})
    except (TypeError, ValueError):
        return jsonify({'error': 'datos inválidos'}), 400
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error en delete_feature_override: {e}")
        return jsonify({'error': str(e)}), 500


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

_PLANES_DEFAULT = [
    {'key': 'basic',   'nombre': 'Basic',   'descripcion': 'Plan gratuito',                  'precio_mensual': 0,       'precio_anual': 0,        'orden': 1, 'color': '#22c55e', 'icono': '🌱'},
    {'key': 'pro',     'nombre': 'Pro',     'descripcion': 'Plan profesional',                'precio_mensual': 49900,   'precio_anual': 479000,   'orden': 2, 'color': '#06b6d4', 'icono': '🚀'},
    {'key': 'premium', 'nombre': 'Premium', 'descripcion': 'Plan premium con más funciones', 'precio_mensual': 99900,   'precio_anual': 959000,   'orden': 3, 'color': '#a855f7', 'icono': '💎'},
    {'key': 'delux',   'nombre': 'Delux',   'descripcion': 'Plan empresarial completo',       'precio_mensual': 199900,  'precio_anual': 1919000,  'orden': 4, 'color': '#f59e0b', 'icono': '👑'},
]

def _seed_planes():
    """Crea los planes por defecto si la tabla está vacía."""
    try:
        if Plan.query.count() == 0:
            for p in _PLANES_DEFAULT:
                db.session.add(Plan(**p))
            db.session.commit()
            logger.info("✅ Planes sembrados automáticamente")
    except Exception as e:
        logger.error(f"Error sembrando planes: {e}")
        db.session.rollback()


@admin_features_bp.route('/api/admin/planes', methods=['GET', 'OPTIONS'])
@admin_required
def list_planes():
    _seed_planes()   # garantiza que existen los 4 planes
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


@admin_features_bp.route('/api/admin/planes/<int:plan_id>', methods=['PUT', 'OPTIONS'])
@admin_required
def update_plan_datos(plan_id):
    """
    PUT /api/admin/planes/<id>  (A34) — edita datos del plan:
    nombre, descripcion, precio_mensual, precio_anual, orden, color, icono, activo.
    """
    if request.method == 'OPTIONS':
        return jsonify({'success': True}), 200
    try:
        from src.models.feature_models import validar_plan_datos
        plan = Plan.query.get(plan_id)
        if not plan:
            return jsonify({'error': 'Plan no encontrado'}), 404
        ok, limpio, error = validar_plan_datos(request.get_json(silent=True) or {})
        if not ok:
            return jsonify({'error': error}), 400
        antes = {
            'nombre': plan.nombre, 'precio_mensual': float(plan.precio_mensual or 0),
            'precio_anual': float(plan.precio_anual or 0), 'activo': plan.activo,
            'color': plan.color, 'icono': plan.icono, 'orden': plan.orden,
        }
        for campo, valor in limpio.items():
            setattr(plan, campo, valor)
        db.session.commit()
        try:
            from src.api.admin_api import registrar_auditoria
            registrar_auditoria('editar', 'plan', plan_id, {'antes': antes, 'despues': limpio})
        except Exception:
            pass
        logger.info(f"💳 Plan {plan_id} ({plan.nombre}) editado por {g.user_email}")
        return jsonify({'success': True, 'plan': plan.to_dict(include_features=True),
                        'message': f"Plan '{plan.nombre}' actualizado"})
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error editando plan {plan_id}: {e}")
        return jsonify({'error': str(e)}), 500


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
    _seed_planes()   # asegura que existen los planes antes de buscar
    plan = Plan.query.filter_by(key=plan_key, activo=True).first()
    if not plan:
        return jsonify({'error': f"Plan '{plan_key}' no encontrado o inactivo"}), 404
    negocio = db.session.execute(text("SELECT id_negocio, nombre_negocio FROM negocios WHERE id_negocio = :nid"), {'nid': negocio_id}).fetchone()
    if not negocio:
        return jsonify({'error': 'Negocio no encontrado'}), 404

    # 1. Actualizar plan_key en negocios (columna segura que ya existe en DB)
    try:
        db.session.execute(text("UPDATE negocios SET plan_key = :pk WHERE id_negocio = :nid"), {'pk': plan_key, 'nid': negocio_id})
    except Exception as e:
        db.session.rollback()
        logger.error(f"❌ Error actualizando plan_key en negocios: {e}")
        return jsonify({'error': 'Error actualizando plan en base de datos'}), 500

    # 2. Intentar actualizar plan_actual_id (columna puede no existir en DB antigua)
    try:
        db.session.execute(text("UPDATE negocios SET plan_actual_id = :pid WHERE id_negocio = :nid"), {'pid': plan.id, 'nid': negocio_id})
    except Exception as e:
        logger.warning(f"⚠️ No se pudo actualizar plan_actual_id (columna puede no existir): {e}")
        db.session.rollback()
        # Re-ejecutar el update de plan_key que ya estaba bien
        db.session.execute(text("UPDATE negocios SET plan_key = :pk WHERE id_negocio = :nid"), {'pk': plan_key, 'nid': negocio_id})

    # 3. Intentar registrar historial en negocio_plan (tabla puede no existir)
    try:
        NegocioPlan.query.filter_by(negocio_id=negocio_id, activo=True).update({'activo': False})
        nuevo_plan = NegocioPlan(
            negocio_id=negocio_id, plan_id=plan.id, activo=True,
            asignado_por='admin',
            notas=data.get('notas') or f'Asignado por {g.user_email}'
        )
        db.session.add(nuevo_plan)
    except Exception as e:
        logger.warning(f"⚠️ No se pudo registrar historial NegocioPlan: {e}")

    db.session.commit()
    logger.info(f"📊 Negocio {negocio_id} → Plan '{plan.nombre}' por {g.user_email}")
    # A50: campanita automática al dueño por el cambio de plan (no crítico).
    try:
        from src.api.utils.notificaciones_service import notificar_negocio
        notificar_negocio(negocio_id, evento='plan_cambiado', ctx={'plan': plan.nombre})
    except Exception:
        pass
    return jsonify({'success': True, 'negocio_id': negocio_id, 'negocio_nombre': negocio[1], 'plan': plan.to_dict(), 'message': f"Plan '{plan.nombre}' asignado a '{negocio[1]}'"})


@admin_features_bp.route('/api/admin/negocios/planes', methods=['GET', 'OPTIONS'])
@admin_required
def list_negocios_with_plans():
    plan_filter = request.args.get('plan')
    estado_filter = request.args.get('estado')   # 'activo' | 'inactivo'
    buscar = request.args.get('buscar', '').strip()
    page = int(request.args.get('page', 1))
    limit = int(request.args.get('limit', 50))
    offset = (page - 1) * limit

    # A30: nunca mostrar negocios en papelera en el listado normal.
    conditions = ["COALESCE(n.eliminado, FALSE) = FALSE"]
    params = {}

    if plan_filter:
        conditions.append("n.plan_key = :plan")
        params['plan'] = plan_filter
    if estado_filter == 'activo':
        conditions.append("n.activo = true")
    elif estado_filter == 'inactivo':
        conditions.append("n.activo = false")
    if buscar:
        conditions.append("(n.nombre_negocio ILIKE :buscar OR n.slug ILIKE :buscar OR n.ciudad ILIKE :buscar OR u.correo ILIKE :buscar)")
        params['buscar'] = f'%{buscar}%'

    where = ("WHERE " + " AND ".join(conditions)) if conditions else ""

    query = f"""
        SELECT n.id_negocio, n.nombre_negocio, n.slug, n.plan_key,
               n.activo, n.ciudad, p.nombre as plan_nombre, p.color as plan_color, p.icono as plan_icono,
               n.email, n.whatsapp, n.telefono, n.fecha_registro,
               u.correo as dueno_email,
               (SELECT COUNT(*) FROM productos_catalogo pc WHERE pc.negocio_id = n.id_negocio) as num_productos,
               (SELECT COUNT(*) FROM pedidos pd WHERE pd.negocio_id = n.id_negocio) as num_pedidos
        FROM negocios n
        LEFT JOIN planes p ON p.key = COALESCE(n.plan_key, 'basic')
        LEFT JOIN usuarios u ON u.id_usuario = n.usuario_id
        {where}
        ORDER BY n.fecha_registro DESC
        LIMIT :limit OFFSET :offset
    """
    params['limit'] = limit
    params['offset'] = offset

    negocios = db.session.execute(text(query), params).fetchall()

    count_query = f"""
        SELECT COUNT(*) FROM negocios n
        LEFT JOIN usuarios u ON u.id_usuario = n.usuario_id
        {where}
    """
    count_params = {k: v for k, v in params.items() if k not in ('limit', 'offset')}
    total = db.session.execute(text(count_query), count_params).scalar()

    stats = db.session.execute(text(
        "SELECT COALESCE(plan_key, 'basic') as plan, COUNT(*) as cantidad FROM negocios GROUP BY plan_key ORDER BY cantidad DESC"
    )).fetchall()

    def _fmt_fecha(dt):
        if not dt:
            return None
        try:
            return dt.strftime('%Y-%m-%d')
        except Exception:
            return str(dt)[:10]

    # Enriquecer con datos de suscripción (tolerante a fallos)
    ids = [n[0] for n in negocios]
    subs_map = _enriquecer_con_suscripcion(ids)

    return jsonify({
        'success': True,
        'negocios': [{
            'id': n[0], 'nombre': n[1], 'slug': n[2], 'plan_key': n[3] or 'basic',
            'activo': n[4], 'ciudad': n[5],
            'plan_nombre': n[6] or 'Basic', 'plan_color': n[7] or '#22c55e', 'plan_icono': n[8] or '🌱',
            'email': n[9], 'whatsapp': n[10], 'telefono': n[11],
            'fecha_registro': _fmt_fecha(n[12]),
            'dueno_email': n[13],
            'num_productos': int(n[14] or 0),
            'num_pedidos': int(n[15] or 0),
            # ── Suscripción ──────────────────────────────────────
            **subs_map.get(n[0], {
                'estado_suscripcion': None,
                'dias_restantes':     None,
                'vence_pronto':       False,
                'es_trial':           None,
                'fecha_vencimiento':  None,
            }),
        } for n in negocios],
        'total': total, 'page': page, 'limit': limit,
        'stats_por_plan': [{'plan': s[0] or 'basic', 'cantidad': s[1]} for s in stats]
    })


@admin_features_bp.route('/api/admin/negocios/<int:negocio_id>/info', methods=['GET', 'OPTIONS'])
@admin_required
def get_negocio_info(negocio_id):
    """Información detallada de un negocio para el modal del panel admin."""
    row = db.session.execute(text("""
        SELECT n.id_negocio, n.nombre_negocio, n.slug, n.plan_key, n.activo, n.ciudad,
               n.email, n.whatsapp, n.telefono, n.categoria, n.fecha_registro,
               u.correo as dueno_email, u.nombre as dueno_nombre,
               p.nombre as plan_nombre, p.color as plan_color,
               COALESCE(NULLIF(n.tipo_pagina, ''), 'ecommerce') as tipo_pagina,
               (SELECT COUNT(*) FROM productos_catalogo pc WHERE pc.negocio_id = n.id_negocio) as num_productos,
               (SELECT COUNT(*) FROM pedidos pd WHERE pd.negocio_id = n.id_negocio) as num_pedidos,
               (SELECT COUNT(*) FROM pedidos pd WHERE pd.negocio_id = n.id_negocio AND pd.estado = 'entregado') as pedidos_entregados
        FROM negocios n
        LEFT JOIN planes p ON p.key = COALESCE(n.plan_key, 'basic')
        LEFT JOIN usuarios u ON u.id_usuario = n.usuario_id
        WHERE n.id_negocio = :nid
    """), {'nid': negocio_id}).fetchone()

    if not row:
        return jsonify({'error': 'Negocio no encontrado'}), 404

    def _fmt(dt):
        try:
            return dt.strftime('%Y-%m-%d %H:%M') if dt else None
        except Exception:
            return str(dt)[:16] if dt else None

    return jsonify({
        'success': True,
        'negocio': {
            'id': row[0], 'nombre': row[1], 'slug': row[2], 'plan_key': row[3] or 'basic',
            'activo': row[4], 'ciudad': row[5],
            'email': row[6], 'whatsapp': row[7], 'telefono': row[8],
            'categoria': row[9], 'fecha_registro': _fmt(row[10]),
            'dueno_email': row[11], 'dueno_nombre': row[12],
            'plan_nombre': row[13] or 'Basic', 'plan_color': row[14] or '#22c55e',
            'tipo_pagina': row[15] or 'ecommerce',
            'num_productos': int(row[16] or 0),
            'num_pedidos': int(row[17] or 0),
            'pedidos_entregados': int(row[18] or 0),
        }
    })


@admin_features_bp.route('/api/admin/negocios/<int:negocio_id>/notificacion', methods=['POST', 'OPTIONS'])
@admin_required
def enviar_notificacion_negocio(negocio_id):
    """Envía una notificación al dueño del negocio desde el panel admin."""
    data = request.get_json(silent=True) or {}
    titulo = data.get('titulo', '').strip()
    mensaje = data.get('mensaje', '').strip()
    prioridad = data.get('prioridad', 'media')

    if not mensaje:
        return jsonify({'error': 'El mensaje es obligatorio'}), 400

    negocio = db.session.execute(text(
        "SELECT id_negocio, nombre_negocio, usuario_id FROM negocios WHERE id_negocio = :nid"
    ), {'nid': negocio_id}).fetchone()
    if not negocio:
        return jsonify({'error': 'Negocio no encontrado'}), 404

    usuario_id = negocio[2]
    if not usuario_id:
        return jsonify({'error': 'El negocio no tiene dueño asignado'}), 400

    try:
        from src.models.notification import Notification
        notif = Notification(
            user_id=usuario_id,
            negocio_id=negocio_id,
            type='sistema',
            titulo=titulo or f'Mensaje de TuKomercio Admin',
            message=mensaje,
            prioridad=prioridad if prioridad in ('alta', 'media', 'baja') else 'media',
        )
        db.session.add(notif)
        db.session.commit()
        logger.info(f"🔔 Notificación enviada a negocio {negocio_id} por admin {g.user_email}")
        return jsonify({'success': True, 'message': 'Notificación enviada correctamente'})
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error enviando notificación a negocio {negocio_id}: {e}")
        return jsonify({'error': 'Error al enviar notificación'}), 500


@admin_features_bp.route('/api/admin/negocios/<int:negocio_id>/estado', methods=['PUT', 'OPTIONS'])
@admin_required
def toggle_estado_negocio(negocio_id):
    """Activa o desactiva (lista negra) un negocio."""
    data = request.get_json(silent=True) or {}
    nuevo_estado = data.get('activo')

    negocio = db.session.execute(text(
        "SELECT id_negocio, nombre_negocio, activo FROM negocios WHERE id_negocio = :nid"
    ), {'nid': negocio_id}).fetchone()
    if not negocio:
        return jsonify({'error': 'Negocio no encontrado'}), 404

    if nuevo_estado is None:
        nuevo_estado = not negocio[2]

    db.session.execute(text(
        "UPDATE negocios SET activo = :estado WHERE id_negocio = :nid"
    ), {'estado': nuevo_estado, 'nid': negocio_id})
    db.session.commit()

    accion = "activado" if nuevo_estado else "puesto en lista negra"
    logger.info(f"🔴 Negocio {negocio_id} ({negocio[1]}) {accion} por admin {g.user_email}")
    return jsonify({'success': True, 'activo': nuevo_estado, 'message': f"Negocio '{negocio[1]}' {accion}"})


@admin_features_bp.route('/api/admin/negocios/<int:negocio_id>/productos', methods=['DELETE', 'OPTIONS'])
@admin_required
def eliminar_productos_negocio(negocio_id):
    """Elimina todos los productos del catálogo de un negocio."""
    negocio = db.session.execute(text(
        "SELECT id_negocio, nombre_negocio FROM negocios WHERE id_negocio = :nid"
    ), {'nid': negocio_id}).fetchone()
    if not negocio:
        return jsonify({'error': 'Negocio no encontrado'}), 404

    try:
        result = db.session.execute(text(
            "DELETE FROM productos_catalogo WHERE negocio_id = :nid"
        ), {'nid': negocio_id})
        eliminados = result.rowcount
        db.session.commit()
        logger.warning(f"🗑️ {eliminados} productos eliminados del negocio {negocio_id} por admin {g.user_email}")
        return jsonify({'success': True, 'eliminados': eliminados, 'message': f"{eliminados} productos eliminados"})
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error eliminando productos del negocio {negocio_id}: {e}")
        return jsonify({'error': 'Error al eliminar productos'}), 500


@admin_features_bp.route('/api/admin/negocios/<int:negocio_id>/reset', methods=['POST', 'OPTIONS'])
@admin_required
def reset_negocio(negocio_id):
    """
    Reset completo del negocio: elimina pedidos, productos, transacciones y movimientos de stock.
    El negocio y su dueño NO se eliminan.
    """
    negocio = db.session.execute(text(
        "SELECT id_negocio, nombre_negocio FROM negocios WHERE id_negocio = :nid"
    ), {'nid': negocio_id}).fetchone()
    if not negocio:
        return jsonify({'error': 'Negocio no encontrado'}), 404

    resumen = {}
    try:
        r = db.session.execute(text("DELETE FROM pedidos WHERE negocio_id = :nid"), {'nid': negocio_id})
        resumen['pedidos'] = r.rowcount
        r = db.session.execute(text("DELETE FROM productos_catalogo WHERE negocio_id = :nid"), {'nid': negocio_id})
        resumen['productos'] = r.rowcount
        r = db.session.execute(text("DELETE FROM transacciones_operativas WHERE negocio_id = :nid"), {'nid': negocio_id})
        resumen['transacciones'] = r.rowcount
        r = db.session.execute(text("DELETE FROM movimientos_stock WHERE negocio_id = :nid"), {'nid': negocio_id})
        resumen['movimientos_stock'] = r.rowcount
        db.session.commit()
        logger.warning(f"⚠️ RESET NEGOCIO {negocio_id} ({negocio[1]}) por admin {g.user_email}: {resumen}")
        return jsonify({'success': True, 'resumen': resumen, 'message': f"Negocio '{negocio[1]}' reseteado"})
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error reseteando negocio {negocio_id}: {e}")
        return jsonify({'error': f'Error durante el reset: {str(e)}'}), 500


@admin_features_bp.route('/api/admin/negocios/<int:negocio_id>', methods=['DELETE', 'OPTIONS'])
@admin_required
def eliminar_negocio(negocio_id):
    """
    Eliminación completa del negocio (hard delete en cascada).
    El usuario dueño NO se elimina.
    """
    negocio = db.session.execute(text(
        "SELECT id_negocio, nombre_negocio FROM negocios WHERE id_negocio = :nid"
    ), {'nid': negocio_id}).fetchone()
    if not negocio:
        return jsonify({'error': 'Negocio no encontrado'}), 404

    confirmacion = (request.get_json(silent=True) or {}).get('confirmar')
    if confirmacion != f'ELIMINAR-{negocio_id}':
        return jsonify({'error': 'Confirmación incorrecta. Envía confirmar="ELIMINAR-{id}"'}), 400

    try:
        nid = negocio_id
        # Limpiar FKs sin ondelete=CASCADE antes del DELETE principal
        db.session.execute(text("DELETE FROM transacciones_operativas WHERE negocio_id = :nid"), {'nid': nid})
        db.session.execute(text("DELETE FROM movimientos_stock    WHERE negocio_id = :nid"), {'nid': nid})
        db.session.execute(text("DELETE FROM categorias_producto  WHERE negocio_id = :nid"), {'nid': nid})
        db.session.execute(text("UPDATE notification SET negocio_id = NULL WHERE negocio_id = :nid"), {'nid': nid})
        db.session.execute(text("UPDATE servicio SET negocio_contratante_id = NULL WHERE negocio_contratante_id = :nid"), {'nid': nid})
        db.session.execute(text("UPDATE servicio SET negocio_contratado_id  = NULL WHERE negocio_contratado_id  = :nid"), {'nid': nid})

        db.session.execute(text("DELETE FROM negocios WHERE id_negocio = :nid"), {'nid': nid})
        db.session.commit()
        logger.warning(f"❌ NEGOCIO {negocio_id} ({negocio[1]}) ELIMINADO por admin {g.user_email}")
        return jsonify({'success': True, 'message': f"Negocio '{negocio[1]}' eliminado permanentemente"})
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error eliminando negocio {negocio_id}: {e}")
        return jsonify({'error': f'Error eliminando negocio: {str(e)}'}), 500


# ═══════════════════════════════════════════════════════════════════════════════
# ENDPOINTS DE SUSCRIPCIONES — ADMIN
# ═══════════════════════════════════════════════════════════════════════════════

@admin_features_bp.route('/api/admin/negocios/<int:negocio_id>/suscripcion', methods=['GET', 'OPTIONS'])
@admin_required
def get_suscripcion_negocio(negocio_id):
    """
    GET /api/admin/negocios/{id}/suscripcion
    Retorna el estado completo de la suscripción de un negocio.
    """
    try:
        from src.models.colombia_data.suscripcion_negocio import SuscripcionNegocio
        sus = SuscripcionNegocio.query.filter_by(negocio_id=negocio_id).first()
        if not sus:
            return jsonify({'success': False, 'error': 'Sin suscripción registrada',
                            'negocio_id': negocio_id}), 404
        return jsonify({'success': True, 'suscripcion': sus.to_dict(include_negocio=True)})
    except Exception as e:
        logger.error(f"Error get_suscripcion_negocio {negocio_id}: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500


@admin_features_bp.route('/api/admin/negocios/<int:negocio_id>/suscripcion', methods=['PUT', 'OPTIONS'])
@admin_required
def update_suscripcion_negocio(negocio_id):
    """
    PUT /api/admin/negocios/{id}/suscripcion
    Actualiza la suscripción de un negocio.

    Body JSON:
      accion      — 'activar' | 'extender' | 'cancelar' | 'pausar' | 'trial'
      plan_key    — 'basic' | 'pro' | 'premium' | 'delux'  (para accion=activar)
      dias        — int (para activar/extender/trial, default 30)
      notas       — str (opcional, para auditoría)
    """
    try:
        from src.models.colombia_data.suscripcion_negocio import (
            SuscripcionNegocio, iniciar_trial_para_negocio, DIAS_TRIAL_DEFAULT
        )
        data   = request.get_json(silent=True) or {}
        accion = data.get('accion', '').strip().lower()
        dias   = int(data.get('dias', 30))
        notas  = data.get('notas') or f'Modificado por {g.user_email}'

        sus = SuscripcionNegocio.query.filter_by(negocio_id=negocio_id).first()

        if accion == 'trial':
            # Regalar trial (segunda oportunidad o primera vez)
            if sus is None:
                sus = iniciar_trial_para_negocio(
                    negocio_id=negocio_id, dias=dias,
                    creado_por=f'admin:{g.user_email}'
                )
            else:
                sus.dar_trial_segunda_oportunidad(
                    dias=dias, creado_por=f'admin:{g.user_email}'
                )
                sus.notas = notas

        elif accion == 'activar':
            plan_key = data.get('plan_key', 'basic')
            _seed_planes()
            plan = Plan.query.filter_by(key=plan_key, activo=True).first()
            if not plan:
                return jsonify({'error': f"Plan '{plan_key}' no encontrado"}), 404
            if sus is None:
                sus = SuscripcionNegocio(negocio_id=negocio_id)
                db.session.add(sus)
                db.session.flush()
            sus.activar_suscripcion(
                plan_id=plan.id, dias=dias,
                creado_por=f'admin:{g.user_email}', notas=notas
            )
            # Sincronizar plan_key en la tabla negocios
            db.session.execute(
                text("UPDATE negocios SET plan_key=:pk WHERE id_negocio=:nid"),
                {'pk': plan_key, 'nid': negocio_id}
            )

        elif accion == 'extender':
            if sus is None:
                return jsonify({'error': 'No hay suscripción para extender'}), 404
            sus.extender(dias=dias, creado_por=f'admin:{g.user_email}', notas=notas)

        elif accion == 'cancelar':
            if sus is None:
                return jsonify({'error': 'No hay suscripción'}), 404
            sus.cancelar(creado_por=f'admin:{g.user_email}', notas=notas)

        elif accion == 'pausar':
            if sus is None:
                return jsonify({'error': 'No hay suscripción'}), 404
            sus.pausar(creado_por=f'admin:{g.user_email}', notas=notas)

        else:
            return jsonify({'error': f"Acción desconocida: '{accion}'. "
                            "Use: activar | extender | cancelar | pausar | trial"}), 400

        db.session.commit()
        logger.info(f"📋 Suscripción negocio {negocio_id} → accion={accion} por {g.user_email}")
        return jsonify({'success': True, 'suscripcion': sus.to_dict()})

    except Exception as e:
        db.session.rollback()
        logger.error(f"Error update_suscripcion_negocio {negocio_id}: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500


@admin_features_bp.route('/api/admin/suscripciones/alertas', methods=['GET', 'OPTIONS'])
@admin_required
def get_alertas_suscripciones():
    """
    GET /api/admin/suscripciones/alertas
    Retorna negocios con suscripción que vence pronto o ya venció.

    Query params:
      dias_pronto  — int (default 7): negocios que vencen en ≤ N días
      limite       — int (default 50)
    """
    try:
        from src.models.colombia_data.suscripcion_negocio import SuscripcionNegocio
        from datetime import datetime, timedelta
        ahora = datetime.utcnow()
        dias_pronto = int(request.args.get('dias_pronto', 7))
        limite      = int(request.args.get('limite', 50))

        # Negocios cuyo trial vence en ≤ dias_pronto días (o ya venció)
        fecha_alerta = ahora + timedelta(days=dias_pronto)

        vencen_pronto = SuscripcionNegocio.query.filter(
            SuscripcionNegocio.estado.in_(['trial', 'activa']),
            SuscripcionNegocio.fecha_fin_trial <= fecha_alerta
        ).limit(limite).all()

        vencen_pronto_paga = SuscripcionNegocio.query.filter(
            SuscripcionNegocio.estado == 'activa',
            SuscripcionNegocio.fecha_fin <= fecha_alerta,
            SuscripcionNegocio.fecha_fin_trial.is_(None)
        ).limit(limite).all()

        ya_vencidas = SuscripcionNegocio.query.filter(
            SuscripcionNegocio.estado.in_(['vencida', 'gracia'])
        ).limit(limite).all()

        def _fmt(sus_list):
            return [s.to_dict(include_negocio=True) for s in sus_list]

        return jsonify({
            'success': True,
            'vencen_pronto_trial':    _fmt(vencen_pronto),
            'vencen_pronto_paga':     _fmt(vencen_pronto_paga),
            'ya_vencidas':            _fmt(ya_vencidas),
            'total_alerta': (
                len(vencen_pronto) + len(vencen_pronto_paga) + len(ya_vencidas)
            ),
            'generado_en': ahora.isoformat(),
        })
    except Exception as e:
        logger.error(f"Error get_alertas_suscripciones: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500


@admin_features_bp.route('/api/admin/suscripciones/resumen', methods=['GET', 'OPTIONS'])
@admin_required
def get_resumen_suscripciones():
    """
    GET /api/admin/suscripciones/resumen
    Dashboard rápido: conteo por estado, MRR estimado, conversiones.
    """
    try:
        from src.models.colombia_data.suscripcion_negocio import SuscripcionNegocio
        from sqlalchemy import func

        conteos = db.session.query(
            SuscripcionNegocio.estado,
            func.count(SuscripcionNegocio.id).label('total')
        ).group_by(SuscripcionNegocio.estado).all()

        resumen = {row.estado: row.total for row in conteos}

        # MRR estimado (suscripciones activas × precio mensual del plan)
        mrr_result = db.session.execute(text("""
            SELECT COALESCE(SUM(pl.precio_mensual), 0) as mrr
            FROM suscripciones_negocio s
            JOIN planes pl ON pl.id = s.plan_id
            WHERE s.estado = 'activa'
              AND (s.fecha_fin IS NULL OR s.fecha_fin >= NOW())
        """)).fetchone()

        return jsonify({
            'success':      True,
            'por_estado':   resumen,
            'mrr_estimado': float(mrr_result[0] if mrr_result else 0),
            'total_negocios': sum(resumen.values()),
        })
    except Exception as e:
        logger.error(f"Error get_resumen_suscripciones: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500


# También actualizar list_negocios_with_plans para incluir datos de suscripción
# (patch no-destructivo: si la tabla no existe, devuelve datos sin suscripción)
def _enriquecer_con_suscripcion(negocio_ids: list) -> dict:
    """
    Helper: retorna dict {negocio_id: {estado_actual, dias_restantes, ...}}
    para una lista de IDs de negocio.
    """
    if not negocio_ids:
        return {}
    try:
        from src.models.colombia_data.suscripcion_negocio import SuscripcionNegocio
        subs = SuscripcionNegocio.query.filter(
            SuscripcionNegocio.negocio_id.in_(negocio_ids)
        ).all()
        return {
            s.negocio_id: {
                'estado_suscripcion': s.estado_actual,
                'dias_restantes':     s.dias_restantes,
                'vence_pronto':       s.vence_pronto,
                'es_trial':          s.es_trial,
                'fecha_vencimiento':  s.fecha_vencimiento.isoformat() if s.fecha_vencimiento else None,
            }
            for s in subs
        }
    except Exception as _e:
        logger.warning(f"⚠️ No se pudo enriquecer con suscripciones: {_e}")
        return {}


# ═══════════════════════════════════════════════════════════════════════════════
# 💳 PAGOS DE SUSCRIPCIÓN
# ═══════════════════════════════════════════════════════════════════════════════

@admin_features_bp.route('/api/admin/negocios/<int:negocio_id>/pagos', methods=['GET', 'OPTIONS'])
@admin_required
def listar_pagos_negocio(negocio_id):
    """Lista el historial de pagos de un negocio, del más reciente al más antiguo."""
    try:
        from src.models.colombia_data.pago_suscripcion import PagoSuscripcion
        pagos = (PagoSuscripcion.query
                 .filter_by(negocio_id=negocio_id)
                 .order_by(PagoSuscripcion.created_at.desc())
                 .limit(50)
                 .all())
        return jsonify({
            'success': True,
            'data': [p.to_dict() for p in pagos],
            'total': len(pagos),
        }), 200
    except Exception as e:
        logger.error(f'❌ Error listando pagos negocio {negocio_id}: {e}')
        return jsonify({'success': False, 'error': str(e)}), 500


@admin_features_bp.route('/api/admin/negocios/<int:negocio_id>/pagos', methods=['POST', 'OPTIONS'])
@admin_required
def registrar_pago_negocio(negocio_id):
    """
    Registra un pago manual de suscripción.
    Body: { monto, metodo_pago, estado?, referencia?, comprobante_url?,
             periodo_inicio?, periodo_fin?, notas?, activar_suscripcion? }

    Si activar_suscripcion=true (default), también activa/extiende la suscripción
    automáticamente según los días del período.
    """
    from src.models.colombia_data.pago_suscripcion import PagoSuscripcion
    from src.models.colombia_data.suscripcion_negocio import SuscripcionNegocio
    from src.models.feature_models import Plan

    body = request.get_json() or {}
    monto = body.get('monto')
    if monto is None:
        return jsonify({'success': False, 'error': 'monto es obligatorio'}), 400

    try:
        # Obtener o crear suscripción
        sus = SuscripcionNegocio.query.filter_by(negocio_id=negocio_id).first()
        if not sus:
            return jsonify({'success': False, 'error': 'Negocio sin suscripción registrada'}), 404

        # Calcular días del período si se proveen fechas
        dias_periodo = 30  # default
        periodo_inicio = None
        periodo_fin    = None
        if body.get('periodo_inicio') and body.get('periodo_fin'):
            from datetime import datetime as _dt
            pi = _dt.fromisoformat(body['periodo_inicio'])
            pf = _dt.fromisoformat(body['periodo_fin'])
            dias_periodo = max(1, (pf - pi).days)
            periodo_inicio = pi
            periodo_fin    = pf

        # Crear el registro de pago
        admin_email = getattr(current_user, 'email', getattr(current_user, 'correo', 'admin'))
        pago = PagoSuscripcion(
            suscripcion_id  = sus.id,
            negocio_id      = negocio_id,
            monto           = float(monto),
            moneda          = body.get('moneda', 'COP'),
            metodo_pago     = body.get('metodo_pago', 'transferencia'),
            estado          = body.get('estado', 'completado'),
            referencia      = body.get('referencia'),
            comprobante_url = body.get('comprobante_url'),
            periodo_inicio  = periodo_inicio,
            periodo_fin     = periodo_fin,
            notas           = body.get('notas'),
            registrado_por  = f'admin:{admin_email}',
        )
        db.session.add(pago)

        # ★ Fase 3: canje de TuKoins como abono (opcional). Descuenta del saldo del
        #   negocio respetando el tope; el pago queda con desglose efectivo + TuKoins.
        try:
            tukoins_canje = int(body.get('tukoins_canje') or 0)
        except (TypeError, ValueError):
            tukoins_canje = 0
        if tukoins_canje > 0:
            from src.api.gamificacion.gamificacion_api import aplicar_canje_plan
            ok_c, res_c, err_c = aplicar_canje_plan(negocio_id, tukoins_canje, float(monto), db.session)
            if not ok_c:
                db.session.rollback()
                return jsonify({'success': False, 'error': err_c}), 400
            pago.tukoins_aplicados = res_c['tukoins']
            _desglose = (f"Abonado con TuKoins: ${res_c['monto_cop']:,.0f} ({res_c['tukoins']} TK) "
                         f"+ efectivo ${res_c['monto_efectivo']:,.0f}")
            pago.notas = ((pago.notas + ' | ') if pago.notas else '') + _desglose

        # Activar/extender suscripción automáticamente si el pago está completado
        activar = body.get('activar_suscripcion', True)
        if activar and pago.estado == 'completado':
            plan_key = body.get('plan_key', 'basic')
            plan = Plan.query.filter_by(key=plan_key, activo=True).first()

            # Limpiar alertas del ciclo anterior para que vuelvan a enviarse
            sus.alertas_enviadas = {}
            from sqlalchemy.orm.attributes import flag_modified
            flag_modified(sus, 'alertas_enviadas')

            if sus.es_trial or sus.estado in ('vencida', 'cancelada', 'pausada', 'gracia'):
                # Activar como suscripción paga nueva
                sus.activar_suscripcion(
                    plan_id    = plan.id if plan else sus.plan_id,
                    dias       = dias_periodo,
                    creado_por = f'admin:{admin_email}',
                    notas      = f'Activada al registrar pago #{pago.id}',
                )
            else:
                # Extender suscripción activa
                sus.extender(
                    dias       = dias_periodo,
                    creado_por = f'admin:{admin_email}',
                    notas      = f'Extendida al registrar pago #{pago.id}',
                )

        db.session.commit()
        logger.info(f'✅ Pago registrado: negocio={negocio_id} monto={monto} método={pago.metodo_pago}')

        # ★ Punto de enganche único: confirmar el pago. Si es el PRIMER pago
        #   completado del negocio, dispara la recompensa de referido (nivel 2).
        #   Mañana este mismo hook lo llamará el webhook de Wompi (origen='wompi').
        try:
            if pago.estado == 'completado':
                completados = PagoSuscripcion.query.filter_by(
                    negocio_id=negocio_id, estado='completado').count()
                es_primer_pago = (completados == 1)
                from src.api.gamificacion.gamificacion_hooks import on_pago_confirmado
                on_pago_confirmado(negocio_id, es_primer_pago=es_primer_pago, origen='manual')
        except Exception as _hook_e:
            logger.warning(f'[pago] enganche on_pago_confirmado no crítico: {_hook_e}')

        return jsonify({
            'success': True,
            'data':    pago.to_dict(),
            'message': 'Pago registrado correctamente',
        }), 201

    except Exception as e:
        db.session.rollback()
        logger.error(f'❌ Error registrando pago: {e}', exc_info=True)
        return jsonify({'success': False, 'error': str(e)}), 500


@admin_features_bp.route('/api/admin/negocios/<int:negocio_id>/tukoins-canje', methods=['GET', 'OPTIONS'])
@admin_required
def info_canje_tukoins(negocio_id):
    """Fase 3: saldo de TuKoins del negocio + parámetros de canje (para el form de pago)."""
    if request.method == 'OPTIONS':
        return jsonify({'ok': True}), 200
    try:
        from src.models.colombia_data.ratings.negocio_gamificacion import NegocioGamificacion
        from src.models.colombia_data.ratings.config_gamificacion import get_tukoins_canje_config
        gn = NegocioGamificacion.query.filter_by(negocio_id=negocio_id).first()
        cfg = get_tukoins_canje_config()
        return jsonify({
            'success': True,
            'saldo':          int(gn.tukoins) if gn else 0,
            'cop_por_tukoin': cfg.get('cop_por_tukoin', 10),
            'tope_pct':       cfg.get('tope_pct', 50),
        }), 200
    except Exception as e:
        logger.error(f'Error info_canje_tukoins: {e}')
        return jsonify({'success': True, 'saldo': 0, 'cop_por_tukoin': 10, 'tope_pct': 50}), 200


@admin_features_bp.route('/api/admin/pagos/<int:pago_id>', methods=['PUT', 'OPTIONS'])
@admin_required
def actualizar_pago(pago_id):
    """
    Actualiza un pago existente.
    Body: { estado?, referencia?, comprobante_url?, notas? }
    """
    from src.models.colombia_data.pago_suscripcion import PagoSuscripcion
    body = request.get_json() or {}
    try:
        pago = PagoSuscripcion.query.get(pago_id)
        if not pago:
            return jsonify({'success': False, 'error': 'Pago no encontrado'}), 404

        if 'estado'          in body: pago.estado          = body['estado']
        if 'referencia'      in body: pago.referencia      = body['referencia']
        if 'comprobante_url' in body: pago.comprobante_url = body['comprobante_url']
        if 'notas'           in body: pago.notas           = body['notas']

        db.session.commit()
        return jsonify({'success': True, 'data': pago.to_dict()}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500


@admin_features_bp.route('/api/admin/pagos', methods=['GET', 'OPTIONS'])
@admin_required
def listar_todos_pagos():
    """
    Lista todos los pagos (para reporte general).
    Query params: negocio_id, estado, limit (default 100)
    """
    from src.models.colombia_data.pago_suscripcion import PagoSuscripcion
    try:
        q = PagoSuscripcion.query
        if request.args.get('negocio_id'):
            q = q.filter_by(negocio_id=int(request.args['negocio_id']))
        if request.args.get('estado'):
            q = q.filter_by(estado=request.args['estado'])
        limit = min(int(request.args.get('limit', 100)), 500)
        pagos = q.order_by(PagoSuscripcion.created_at.desc()).limit(limit).all()

        total_monto = sum(float(p.monto) for p in pagos if p.estado == 'completado')
        return jsonify({
            'success': True,
            'data': [p.to_dict() for p in pagos],
            'total': len(pagos),
            'total_cobrado_cop': total_monto,
        }), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


# ═══════════════════════════════════════════════════════════════════════════════
# 📧 ALERTAS POR EMAIL — CRON MANUAL
# ═══════════════════════════════════════════════════════════════════════════════

@admin_features_bp.route('/api/admin/suscripciones/enviar-alertas', methods=['POST', 'OPTIONS'])
@admin_required
def disparar_alertas_email():
    """
    Dispara manualmente el cron de emails de suscripción.
    Útil para:
      • Probar el sistema de alertas
      • Ejecutar vía cron externo (Render Cron Jobs → POST con API key de admin)

    Respuesta:
      {
        total_revisadas, total_emails_enviados, total_errores,
        detalle: [ {negocio_id, alerta, email, ok, detalle} ]
      }
    """
    try:
        from src.services.suscripcion_email_service import enviar_alertas_suscripcion
        # Se ejecuta en el contexto Flask ya activo (sin pasar app)
        resultado = enviar_alertas_suscripcion(app=None)
        return jsonify({
            'success': True,
            'data': resultado,
        }), 200
    except Exception as e:
        logger.error(f'❌ Error en cron de alertas email: {e}', exc_info=True)
        return jsonify({'success': False, 'error': str(e)}), 500


# ═══════════════════════════════════════════════════════════════════════════════
# ENDPOINTS PÚBLICOS (sin auth de admin)
# ═══════════════════════════════════════════════════════════════════════════════

@admin_features_bp.route('/api/features/my', methods=['GET', 'OPTIONS'])
def get_my_features():
    negocio_id = request.headers.get('X-Negocio-Id') or request.args.get('negocio_id')
    
    # Intentar obtener negocio del usuario autenticado
    if not negocio_id:
        try:
            if current_user and hasattr(current_user, 'is_authenticated') and current_user.is_authenticated:
                result = db.session.execute(
                    text("SELECT id_negocio FROM negocios WHERE usuario_id = :uid LIMIT 1"),
                    {'uid': current_user.id}
                ).fetchone()
                if result:
                    negocio_id = result[0]
        except Exception as e:
            logger.warning(f"⚠️ get_my_features: No se pudo obtener usuario: {e}")

    # Obtener plan del negocio (None si no tiene negocio)
    plan_key = None
    if negocio_id:
        try:
            negocio = db.session.execute(
                text("SELECT plan_key FROM negocios WHERE id_negocio = :nid"),
                {'nid': int(negocio_id)}
            ).fetchone()
            plan_key = (negocio[0] if negocio else None) or 'basic'
        except Exception as e:
            logger.warning(f"⚠️ get_my_features: Error consultando negocio {negocio_id}: {e}")
            plan_key = 'basic'

    # Obtener TODAS las features visibles
    all_features = FeatureFlag.query.filter_by(visible=True).order_by(FeatureFlag.orden).all()

    # Obtener features incluidas en el plan (vacío si no hay plan)
    plan_feature_map = {}
    if plan_key:
        try:
            plan_features = db.session.query(
                FeatureFlag.key, PlanFeature.limite, PlanFeature.config_json
            ).join(
                PlanFeature, PlanFeature.feature_id == FeatureFlag.id
            ).join(
                Plan, Plan.id == PlanFeature.plan_id
            ).filter(Plan.key == plan_key).all()
            plan_feature_map = {pf[0]: {'limite': pf[1], 'config': pf[2]} for pf in plan_features}
        except Exception as e:
            logger.warning(f"⚠️ get_my_features: Error consultando plan_features: {e}")

    # Construir respuesta
    features_response = []
    for f in all_features:
        in_plan = f.key in plan_feature_map

        if not f.activo_global:
            # Desactivado globalmente → oculto para TODOS
            allowed = False
            locked_reason = 'disabled'
        elif not plan_key:
            # Sin negocio → mostrar con candado
            allowed = False
            locked_reason = 'upgrade'
        elif in_plan:
            # Activo y en su plan → permitido
            allowed = True
            locked_reason = None
        else:
            # Activo pero no en su plan → candado
            allowed = False
            locked_reason = 'upgrade'

        features_response.append({
            'key': f.key,
            'nombre': f.nombre,
            'categoria': f.categoria,
            'icono': f.icono,
            'allowed': allowed,
            'limite': plan_feature_map[f.key]['limite'] if in_plan else None,
            'locked_reason': locked_reason
        })

    return jsonify({
        'success': True,
        'plan': plan_key or 'none',
        'features': features_response
    })

@admin_features_bp.route('/api/features/negocio/<int:negocio_id>', methods=['GET', 'OPTIONS'])
def get_negocio_plan(negocio_id):
    """
    Endpoint público para consultar el plan de un negocio.
    Usado por el Store Designer para el plan gating.
    """
    try:
        negocio = db.session.execute(
            text("SELECT plan_key FROM negocios WHERE id_negocio = :nid"),
            {'nid': negocio_id}
        ).fetchone()
        
        if not negocio:
            return jsonify({'error': 'Negocio no encontrado'}), 404
        
        plan_key = negocio[0] or 'basic'
        
        return jsonify({
            'success': True,
            'plan': plan_key,
            'plan_key': plan_key
        })
    except Exception as e:
        logger.error(f"Error obteniendo plan de negocio {negocio_id}: {e}")
        return jsonify({'plan': 'basic', 'plan_key': 'basic'})
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