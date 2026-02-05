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
TUKOMERCIO - API DE CONTRATOS SIMPLIFICADOS (Admin)
Fase 0.5 - Registro manual de contratos para métricas y badges
═══════════════════════════════════════════════════════════════════════════════
"""

from flask import Blueprint, request, jsonify
from datetime import datetime
from src.models.database import db
from sqlalchemy import text
import logging

logger = logging.getLogger(__name__)

# Crear Blueprint
contratos_admin_api = Blueprint('contratos_admin_api', __name__)

# ═══════════════════════════════════════════════════════════════════════════════
# CORS CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════════
ALLOWED_ORIGINS = [
    "https://tuko.pages.dev",
    "https://tukomercio.pages.dev", 
    "https://trayectoria-rxdc1.web.app",
    "http://localhost:3000",
    "http://127.0.0.1:5500",
    "http://localhost:5500"
]

@contratos_admin_api.after_request
def add_cors_headers(response):
    origin = request.headers.get('Origin', '')
    if origin in ALLOWED_ORIGINS or origin.endswith('.pages.dev'):
        response.headers['Access-Control-Allow-Origin'] = origin
    else:
        response.headers['Access-Control-Allow-Origin'] = ALLOWED_ORIGINS[0]
    response.headers['Access-Control-Allow-Credentials'] = 'true'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, X-Admin-ID'
    return response

@contratos_admin_api.before_request
def handle_preflight():
    if request.method == 'OPTIONS':
        response = jsonify({'status': 'ok'})
        return response, 200


# ═══════════════════════════════════════════════════════════════════════════════
# HELPER: Verificar Admin
# ═══════════════════════════════════════════════════════════════════════════════
def get_admin_id():
    """Obtiene el ID del admin desde el header"""
    admin_id = request.headers.get('X-Admin-ID')
    if admin_id:
        try:
            return int(admin_id)
        except:
            pass
    return 1  # Default superadmin


# ═══════════════════════════════════════════════════════════════════════════════
# POST /api/admin/contratos - Crear contrato
# ═══════════════════════════════════════════════════════════════════════════════
@contratos_admin_api.route('', methods=['POST'])
def crear_contrato():
    """Crea un nuevo contrato simplificado"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'success': False, 'error': 'No se recibieron datos'}), 400
        
        # Validar campos requeridos
        if not data.get('negocio_id'):
            return jsonify({'success': False, 'error': 'negocio_id es requerido'}), 400
        if not data.get('cliente_nombre'):
            return jsonify({'success': False, 'error': 'cliente_nombre es requerido'}), 400
        
        # Verificar que el negocio existe
        negocio_check = db.session.execute(text(
            "SELECT id_negocio FROM negocios WHERE id_negocio = :id"
        ), {'id': data['negocio_id']})
        if not negocio_check.fetchone():
            return jsonify({'success': False, 'error': 'Negocio no encontrado'}), 404
        
        # Insertar contrato
        result = db.session.execute(text("""
            INSERT INTO contratos_simplificados (
                negocio_id, cliente_nombre, cliente_telefono, cliente_email,
                descripcion, categoria, monto, estado,
                calificacion, comentario,
                tiempo_respuesta_horas, entrega_anticipada, cliente_recurrente,
                fecha_inicio, fecha_fin, created_at, created_by
            ) VALUES (
                :negocio_id, :cliente_nombre, :cliente_telefono, :cliente_email,
                :descripcion, :categoria, :monto, :estado,
                :calificacion, :comentario,
                :tiempo_respuesta_horas, :entrega_anticipada, :cliente_recurrente,
                :fecha_inicio, :fecha_fin, NOW(), :created_by
            )
            RETURNING id, created_at
        """), {
            'negocio_id': data['negocio_id'],
            'cliente_nombre': data['cliente_nombre'],
            'cliente_telefono': data.get('cliente_telefono'),
            'cliente_email': data.get('cliente_email'),
            'descripcion': data.get('descripcion'),
            'categoria': data.get('categoria'),
            'monto': data.get('monto'),
            'estado': data.get('estado', 'completado'),
            'calificacion': data.get('calificacion'),
            'comentario': data.get('comentario'),
            'tiempo_respuesta_horas': data.get('tiempo_respuesta_horas'),
            'entrega_anticipada': data.get('entrega_anticipada', False),
            'cliente_recurrente': data.get('cliente_recurrente', False),
            'fecha_inicio': data.get('fecha_inicio', datetime.utcnow()),
            'fecha_fin': data.get('fecha_fin'),
            'created_by': get_admin_id()
        })
        
        row = result.fetchone()
        db.session.commit()
        
        logger.info(f"✅ Contrato {row[0]} creado para negocio {data['negocio_id']}")
        
        return jsonify({
            'success': True,
            'message': 'Contrato creado exitosamente',
            'data': {
                'id': row[0],
                'created_at': row[1].isoformat() if row[1] else None
            }
        }), 201
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"❌ Error creando contrato: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500


# ═══════════════════════════════════════════════════════════════════════════════
# GET /api/admin/contratos - Listar contratos
# ═══════════════════════════════════════════════════════════════════════════════
@contratos_admin_api.route('', methods=['GET'])
def listar_contratos():
    """Lista contratos con filtros opcionales"""
    try:
        negocio_id = request.args.get('negocio_id', type=int)
        estado = request.args.get('estado')
        page = request.args.get('page', 1, type=int)
        limit = min(request.args.get('limit', 20, type=int), 100)
        offset = (page - 1) * limit
        
        # Construir query
        where_clauses = []
        params = {'limit': limit, 'offset': offset}
        
        if negocio_id:
            where_clauses.append("c.negocio_id = :negocio_id")
            params['negocio_id'] = negocio_id
        if estado:
            where_clauses.append("c.estado = :estado")
            params['estado'] = estado
        
        where_sql = " AND ".join(where_clauses) if where_clauses else "1=1"
        
        result = db.session.execute(text(f"""
            SELECT c.id, c.negocio_id, c.cliente_nombre, c.descripcion,
                   c.monto, c.estado, c.calificacion, c.fecha_inicio, c.created_at,
                   n.nombre_negocio
            FROM contratos_simplificados c
            JOIN negocios n ON c.negocio_id = n.id_negocio
            WHERE {where_sql}
            ORDER BY c.created_at DESC
            LIMIT :limit OFFSET :offset
        """), params)
        
        contratos = []
        for row in result.fetchall():
            contratos.append({
                'id': row[0],
                'negocio_id': row[1],
                'negocio_nombre': row[9],
                'cliente_nombre': row[2],
                'descripcion': row[3][:50] + '...' if row[3] and len(row[3]) > 50 else row[3],
                'monto': float(row[4]) if row[4] else None,
                'estado': row[5],
                'calificacion': row[6],
                'fecha_inicio': row[7].isoformat() if row[7] else None,
                'created_at': row[8].isoformat() if row[8] else None
            })
        
        # Contar total
        count_result = db.session.execute(text(f"""
            SELECT COUNT(*) FROM contratos_simplificados c WHERE {where_sql}
        """), params)
        total = count_result.scalar()
        
        return jsonify({
            'success': True,
            'data': {
                'contratos': contratos,
                'pagination': {
                    'page': page,
                    'limit': limit,
                    'total': total,
                    'pages': (total + limit - 1) // limit
                }
            }
        })
        
    except Exception as e:
        logger.error(f"❌ Error listando contratos: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


# ═══════════════════════════════════════════════════════════════════════════════
# GET /api/admin/contratos/<id> - Obtener contrato específico
# ═══════════════════════════════════════════════════════════════════════════════
@contratos_admin_api.route('/<int:contrato_id>', methods=['GET'])
def obtener_contrato(contrato_id):
    """Obtiene un contrato por ID"""
    try:
        result = db.session.execute(text("""
            SELECT c.*, n.nombre_negocio
            FROM contratos_simplificados c
            JOIN negocios n ON c.negocio_id = n.id_negocio
            WHERE c.id = :id
        """), {'id': contrato_id})
        
        row = result.fetchone()
        if not row:
            return jsonify({'success': False, 'error': 'Contrato no encontrado'}), 404
        
        return jsonify({
            'success': True,
            'data': {
                'id': row[0],
                'negocio_id': row[1],
                'negocio_nombre': row[-1],
                'cliente': {
                    'nombre': row[2],
                    'telefono': row[3],
                    'email': row[4]
                },
                'descripcion': row[5],
                'categoria': row[6],
                'monto': float(row[7]) if row[7] else None,
                'estado': row[8],
                'fecha_inicio': row[9].isoformat() if row[9] else None,
                'fecha_fin': row[10].isoformat() if row[10] else None,
                'calificacion': row[11],
                'comentario': row[12],
                'tiempo_respuesta_horas': row[13],
                'entrega_anticipada': row[14],
                'cliente_recurrente': row[15],
                'created_at': row[16].isoformat() if row[16] else None
            }
        })
        
    except Exception as e:
        logger.error(f"❌ Error obteniendo contrato: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


# ═══════════════════════════════════════════════════════════════════════════════
# PUT /api/admin/contratos/<id> - Actualizar contrato
# ═══════════════════════════════════════════════════════════════════════════════
@contratos_admin_api.route('/<int:contrato_id>', methods=['PUT'])
def actualizar_contrato(contrato_id):
    """Actualiza un contrato existente"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'error': 'No se recibieron datos'}), 400
        
        # Campos actualizables
        allowed_fields = [
            'cliente_nombre', 'cliente_telefono', 'cliente_email',
            'descripcion', 'categoria', 'monto', 'estado',
            'calificacion', 'comentario', 'tiempo_respuesta_horas',
            'entrega_anticipada', 'cliente_recurrente', 'fecha_inicio', 'fecha_fin'
        ]
        
        updates = []
        params = {'id': contrato_id}
        
        for field in allowed_fields:
            if field in data:
                updates.append(f"{field} = :{field}")
                params[field] = data[field]
        
        if not updates:
            return jsonify({'success': False, 'error': 'No hay campos para actualizar'}), 400
        
        updates.append("updated_at = NOW()")
        
        result = db.session.execute(text(f"""
            UPDATE contratos_simplificados 
            SET {', '.join(updates)}
            WHERE id = :id
            RETURNING id
        """), params)
        
        if not result.fetchone():
            return jsonify({'success': False, 'error': 'Contrato no encontrado'}), 404
        
        db.session.commit()
        logger.info(f"✅ Contrato {contrato_id} actualizado")
        
        return jsonify({'success': True, 'message': 'Contrato actualizado'})
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"❌ Error actualizando contrato: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


# ═══════════════════════════════════════════════════════════════════════════════
# DELETE /api/admin/contratos/<id> - Eliminar contrato
# ═══════════════════════════════════════════════════════════════════════════════
@contratos_admin_api.route('/<int:contrato_id>', methods=['DELETE'])
def eliminar_contrato(contrato_id):
    """Elimina un contrato"""
    try:
        result = db.session.execute(text("""
            DELETE FROM contratos_simplificados WHERE id = :id RETURNING id
        """), {'id': contrato_id})
        
        if not result.fetchone():
            return jsonify({'success': False, 'error': 'Contrato no encontrado'}), 404
        
        db.session.commit()
        logger.info(f"✅ Contrato {contrato_id} eliminado")
        
        return jsonify({'success': True, 'message': 'Contrato eliminado'})
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"❌ Error eliminando contrato: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


# ═══════════════════════════════════════════════════════════════════════════════
# GET /api/admin/contratos/estadisticas/<negocio_id> - Estadísticas
# ═══════════════════════════════════════════════════════════════════════════════
@contratos_admin_api.route('/estadisticas/<int:negocio_id>', methods=['GET'])
def estadisticas_negocio(negocio_id):
    """Obtiene estadísticas de contratos de un negocio"""
    try:
        result = db.session.execute(text("""
            SELECT 
                COUNT(*) as total,
                COUNT(*) FILTER (WHERE estado = 'completado') as completados,
                COUNT(*) FILTER (WHERE estado = 'cancelado') as cancelados,
                COUNT(*) FILTER (WHERE estado = 'en_progreso') as en_progreso,
                COUNT(*) FILTER (WHERE estado = 'pendiente') as pendientes,
                AVG(calificacion) FILTER (WHERE calificacion IS NOT NULL) as promedio_calificacion,
                COUNT(*) FILTER (WHERE calificacion = 5) as cinco_estrellas,
                COUNT(*) FILTER (WHERE entrega_anticipada = true) as entregas_anticipadas,
                COUNT(*) FILTER (WHERE cliente_recurrente = true) as clientes_recurrentes,
                AVG(tiempo_respuesta_horas) FILTER (WHERE tiempo_respuesta_horas IS NOT NULL) as promedio_respuesta,
                SUM(monto) FILTER (WHERE estado = 'completado') as total_facturado
            FROM contratos_simplificados
            WHERE negocio_id = :negocio_id
        """), {'negocio_id': negocio_id})
        
        row = result.fetchone()
        total = row[0] or 0
        completados = row[1] or 0
        
        return jsonify({
            'success': True,
            'data': {
                'negocio_id': negocio_id,
                'total_contratos': total,
                'por_estado': {
                    'completados': completados,
                    'cancelados': row[2] or 0,
                    'en_progreso': row[3] or 0,
                    'pendientes': row[4] or 0
                },
                'tasa_exito': round((completados / total * 100), 1) if total > 0 else 0,
                'promedio_calificacion': round(float(row[5]), 2) if row[5] else None,
                'cinco_estrellas': row[6] or 0,
                'entregas_anticipadas': row[7] or 0,
                'clientes_recurrentes': row[8] or 0,
                'promedio_respuesta_horas': round(float(row[9]), 1) if row[9] else None,
                'total_facturado': float(row[10]) if row[10] else 0
            }
        })
        
    except Exception as e:
        logger.error(f"❌ Error obteniendo estadísticas: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500


# ═══════════════════════════════════════════════════════════════════════════════
# POST /api/admin/contratos/seed/<negocio_id> - Crear contratos de prueba
# ═══════════════════════════════════════════════════════════════════════════════
@contratos_admin_api.route('/seed/<int:negocio_id>', methods=['POST'])
def seed_contratos_prueba(negocio_id):
    """
    Crea contratos de prueba para un negocio.
    Útil para testing de métricas.
    """
    try:
        data = request.get_json() or {}
        cantidad = min(data.get('cantidad', 10), 50)  # Máximo 50
        
        # Verificar negocio
        negocio_check = db.session.execute(text(
            "SELECT nombre_negocio FROM negocios WHERE id_negocio = :id"
        ), {'id': negocio_id})
        negocio_row = negocio_check.fetchone()
        
        if not negocio_row:
            return jsonify({'success': False, 'error': 'Negocio no encontrado'}), 404
        
        # Datos de prueba
        clientes = [
            ('Juan Pérez', '3001234567', 5, 'Excelente servicio'),
            ('María García', '3109876543', 5, 'Muy profesional'),
            ('Carlos López', '3201112233', 4, 'Buen trabajo'),
            ('Ana Martínez', '3154445566', 5, 'Súper recomendado'),
            ('Pedro Rodríguez', '3007778899', 4, 'Cumplido'),
            ('Laura Sánchez', '3112223344', 5, 'Increíble calidad'),
            ('Diego Torres', '3185556677', 5, 'El mejor'),
            ('Sofía Ramírez', '3008889900', 4, 'Muy bueno'),
            ('Miguel Herrera', '3121234567', 5, 'Perfecto'),
            ('Valentina Castro', '3159876543', 5, 'Lo recomiendo')
        ]
        
        categorias = ['instalación', 'reparación', 'mantenimiento', 'venta', 'asesoría']
        
        import random
        created_ids = []
        
        for i in range(cantidad):
            cliente = clientes[i % len(clientes)]
            
            result = db.session.execute(text("""
                INSERT INTO contratos_simplificados (
                    negocio_id, cliente_nombre, cliente_telefono,
                    descripcion, categoria, monto, estado,
                    calificacion, comentario,
                    tiempo_respuesta_horas, entrega_anticipada, cliente_recurrente,
                    fecha_inicio, fecha_fin, created_at, created_by
                ) VALUES (
                    :negocio_id, :cliente_nombre, :cliente_telefono,
                    :descripcion, :categoria, :monto, 'completado',
                    :calificacion, :comentario,
                    :tiempo_respuesta, :entrega_anticipada, :cliente_recurrente,
                    NOW() - INTERVAL ':dias days', NOW() - INTERVAL ':dias_fin days',
                    NOW(), :created_by
                )
                RETURNING id
            """), {
                'negocio_id': negocio_id,
                'cliente_nombre': cliente[0],
                'cliente_telefono': cliente[1],
                'descripcion': f'Servicio #{i+1} para {cliente[0]}',
                'categoria': random.choice(categorias),
                'monto': random.randint(50000, 500000),
                'calificacion': cliente[2],
                'comentario': cliente[3],
                'tiempo_respuesta': random.choice([1, 2, 3, 4, 6, 12]),
                'entrega_anticipada': random.choice([True, False, True]),  # 66% anticipada
                'cliente_recurrente': i > 5,  # Últimos son recurrentes
                'dias': random.randint(1, 60),
                'dias_fin': random.randint(0, 30),
                'created_by': get_admin_id()
            })
            
            created_ids.append(result.fetchone()[0])
        
        db.session.commit()
        
        logger.info(f"✅ {cantidad} contratos de prueba creados para negocio {negocio_id}")
        
        return jsonify({
            'success': True,
            'message': f'{cantidad} contratos de prueba creados para {negocio_row[0]}',
            'data': {
                'negocio_id': negocio_id,
                'negocio_nombre': negocio_row[0],
                'contratos_creados': len(created_ids),
                'ids': created_ids
            }
        }), 201
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"❌ Error creando contratos de prueba: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500