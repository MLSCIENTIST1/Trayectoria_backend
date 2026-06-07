"""
Centro de Ayuda — CRUD de administración (panel).  Fase 3: M3.3.

Permite crear/editar/eliminar/publicar entradas de `plataforma_kb` desde el panel
admin SIN tocar código. Protegido por `@requiere_permiso('centro_ayuda')` y auditado.

url_prefix: /api/admin/ayuda
  GET    /entradas?tipo=&area=&q=    → lista (incluye NO publicadas)
  GET    /entrada/<id>               → una entrada
  POST   /entrada                    → crear
  PUT    /entrada/<id>               → editar
  DELETE /entrada/<id>               → eliminar
  POST   /entrada/<id>/publicar      → alternar publicado

© 2024-2026 Carlos Eduardo Huérfano Bermúdez.
"""
import logging
from flask import Blueprint, jsonify, request, g
from src.models.database import db
from src.models.colombia_data.plataforma_kb import PlataformaKB
from src.api.admin_api import requiere_permiso, registrar_auditoria

logger = logging.getLogger(__name__)
centro_ayuda_admin_bp = Blueprint('centro_ayuda_admin', __name__, url_prefix='/api/admin/ayuda')

TIPOS_VALIDOS = {'visual', 'categoria', 'feature', 'articulo', 'changelog'}


def validar_entrada_kb(data, parcial=False):
    """Función PURA: valida un payload de entrada KB. Devuelve lista de errores."""
    errores = []
    if (not parcial) or ('tipo' in data):
        if data.get('tipo') not in TIPOS_VALIDOS:
            errores.append(f"tipo inválido (válidos: {sorted(TIPOS_VALIDOS)})")
    if (not parcial) or ('clave' in data):
        if not str(data.get('clave') or '').strip():
            errores.append("clave requerida")
    if (not parcial) or ('titulo' in data):
        if not str(data.get('titulo') or '').strip():
            errores.append("titulo requerido")
    return errores


@centro_ayuda_admin_bp.route('/entradas', methods=['GET'])
@requiere_permiso('centro_ayuda')
def listar():
    q = PlataformaKB.query
    tipo = request.args.get('tipo')
    area = request.args.get('area')
    busq = (request.args.get('q') or '').strip()
    if tipo: q = q.filter(PlataformaKB.tipo == tipo)
    if area: q = q.filter(PlataformaKB.area == area)
    if busq: q = q.filter(PlataformaKB.titulo.ilike(f"%{busq}%"))
    items = q.order_by(PlataformaKB.tipo, PlataformaKB.orden, PlataformaKB.titulo).limit(500).all()
    return jsonify({'success': True, 'entradas': [i.to_dict() for i in items], 'total': len(items)})


@centro_ayuda_admin_bp.route('/entrada/<int:eid>', methods=['GET'])
@requiere_permiso('centro_ayuda')
def obtener(eid):
    e = PlataformaKB.query.get(eid)
    if not e:
        return jsonify({'success': False, 'error': 'No encontrada'}), 404
    return jsonify({'success': True, 'entrada': e.to_dict()})


@centro_ayuda_admin_bp.route('/entrada', methods=['POST'])
@requiere_permiso('centro_ayuda')
def crear():
    data = request.get_json() or {}
    errores = validar_entrada_kb(data)
    if errores:
        return jsonify({'success': False, 'errores': errores}), 400
    if PlataformaKB.query.filter_by(clave=data['clave'].strip()).first():
        return jsonify({'success': False, 'error': 'La clave ya existe'}), 409
    try:
        e = PlataformaKB(
            tipo=data['tipo'], area=(data.get('area') or None), clave=data['clave'].strip(),
            titulo=data['titulo'].strip(), resumen=data.get('resumen'), contenido=data.get('contenido'),
            datos=data.get('datos') or {}, orden=int(data.get('orden') or 0),
            publicado=bool(data.get('publicado', False)))
        db.session.add(e); db.session.commit()
        registrar_auditoria('crear', 'centro_ayuda', e.id, {'clave': e.clave, 'tipo': e.tipo})
        return jsonify({'success': True, 'entrada': e.to_dict()}), 201
    except Exception as ex:
        db.session.rollback()
        logger.error(f"[kb-admin] crear: {ex}")
        return jsonify({'success': False, 'error': str(ex)}), 500


@centro_ayuda_admin_bp.route('/entrada/<int:eid>', methods=['PUT', 'PATCH'])
@requiere_permiso('centro_ayuda')
def editar(eid):
    e = PlataformaKB.query.get(eid)
    if not e:
        return jsonify({'success': False, 'error': 'No encontrada'}), 404
    data = request.get_json() or {}
    errores = validar_entrada_kb(data, parcial=True)
    if errores:
        return jsonify({'success': False, 'errores': errores}), 400
    try:
        for campo in ('tipo', 'area', 'titulo', 'resumen', 'contenido', 'datos'):
            if campo in data:
                setattr(e, campo, data[campo])
        if 'orden' in data:     e.orden = int(data.get('orden') or 0)
        if 'publicado' in data: e.publicado = bool(data['publicado'])
        db.session.commit()
        registrar_auditoria('editar', 'centro_ayuda', e.id, {'clave': e.clave})
        return jsonify({'success': True, 'entrada': e.to_dict()})
    except Exception as ex:
        db.session.rollback()
        logger.error(f"[kb-admin] editar: {ex}")
        return jsonify({'success': False, 'error': str(ex)}), 500


@centro_ayuda_admin_bp.route('/entrada/<int:eid>', methods=['DELETE'])
@requiere_permiso('centro_ayuda')
def eliminar(eid):
    e = PlataformaKB.query.get(eid)
    if not e:
        return jsonify({'success': False, 'error': 'No encontrada'}), 404
    clave = e.clave
    try:
        db.session.delete(e); db.session.commit()
        registrar_auditoria('eliminar', 'centro_ayuda', eid, {'clave': clave})
        return jsonify({'success': True})
    except Exception as ex:
        db.session.rollback()
        logger.error(f"[kb-admin] eliminar: {ex}")
        return jsonify({'success': False, 'error': str(ex)}), 500


@centro_ayuda_admin_bp.route('/entrada/<int:eid>/publicar', methods=['POST'])
@requiere_permiso('centro_ayuda')
def publicar(eid):
    e = PlataformaKB.query.get(eid)
    if not e:
        return jsonify({'success': False, 'error': 'No encontrada'}), 404
    try:
        e.publicado = not bool(e.publicado)
        db.session.commit()
        registrar_auditoria('activar' if e.publicado else 'desactivar', 'centro_ayuda', e.id, {'clave': e.clave, 'publicado': e.publicado})
        return jsonify({'success': True, 'publicado': e.publicado})
    except Exception as ex:
        db.session.rollback()
        logger.error(f"[kb-admin] publicar: {ex}")
        return jsonify({'success': False, 'error': str(ex)}), 500
