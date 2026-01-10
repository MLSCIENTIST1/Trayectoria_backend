# -*- coding: utf-8 -*-
"""
BizFlow Studio - API de Registro de Usuarios
Con validación flexible de ciudades (case-insensitive, sin acentos)
"""

from src.models.database import db
from src.models.usuarios import Usuario
from src.models.colombia_data.colombia_data import Colombia
import logging
import unicodedata
import re
from flask import Blueprint, jsonify, request
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import func

# Configuración del Logger
logger = logging.getLogger(__name__)

# Blueprint para la API de registro de usuarios
register_user_bp = Blueprint('register_user_bp', __name__)


def normalizar_texto(texto):
    """
    Normaliza texto removiendo acentos y convirtiendo a minúsculas.
    'Bogotá' -> 'bogota'
    'Medellín' -> 'medellin'
    """
    if not texto:
        return ""
    
    # Convertir a minúsculas
    texto = texto.lower().strip()
    
    # Remover acentos
    texto = unicodedata.normalize('NFD', texto)
    texto = ''.join(c for c in texto if unicodedata.category(c) != 'Mn')
    
    # Remover caracteres especiales excepto espacios
    texto = re.sub(r'[^a-z0-9\s]', '', texto)
    
    return texto


def buscar_ciudad_flexible(nombre_ciudad):
    """
    Busca una ciudad de forma flexible:
    1. Búsqueda exacta (case-insensitive)
    2. Búsqueda sin acentos
    3. Búsqueda parcial
    
    Args:
        nombre_ciudad: Nombre de la ciudad ingresado por el usuario
        
    Returns:
        Colombia: Objeto ciudad o None
    """
    if not nombre_ciudad:
        return None
    
    nombre_limpio = nombre_ciudad.strip()
    nombre_normalizado = normalizar_texto(nombre_ciudad)
    
    logger.debug(f"Buscando ciudad: '{nombre_limpio}' -> normalizado: '{nombre_normalizado}'")
    
    # 1. Búsqueda exacta (case-insensitive)
    ciudad = Colombia.query.filter(
        func.lower(Colombia.ciudad_nombre) == nombre_limpio.lower()
    ).first()
    
    if ciudad:
        logger.debug(f"Ciudad encontrada (exacta): {ciudad.ciudad_nombre}")
        return ciudad
    
    # 2. Búsqueda con ILIKE (parcial, case-insensitive)
    ciudad = Colombia.query.filter(
        Colombia.ciudad_nombre.ilike(f"%{nombre_limpio}%")
    ).first()
    
    if ciudad:
        logger.debug(f"Ciudad encontrada (parcial): {ciudad.ciudad_nombre}")
        return ciudad
    
    # 3. Búsqueda por coincidencia normalizada (sin acentos)
    # Traemos todas las ciudades y comparamos normalizadas
    todas_ciudades = Colombia.query.all()
    for c in todas_ciudades:
        if normalizar_texto(c.ciudad_nombre) == nombre_normalizado:
            logger.debug(f"Ciudad encontrada (normalizada): {c.ciudad_nombre}")
            return c
    
    # 4. Búsqueda parcial normalizada
    for c in todas_ciudades:
        if nombre_normalizado in normalizar_texto(c.ciudad_nombre):
            logger.debug(f"Ciudad encontrada (parcial normalizada): {c.ciudad_nombre}")
            return c
    
    logger.warning(f"Ciudad no encontrada: '{nombre_ciudad}'")
    return None


@register_user_bp.route('/register_user', methods=['POST', 'OPTIONS'])
def register_user():
    """
    API para registrar nuevos usuarios.
    Soporta búsqueda flexible de ciudades (sin importar mayúsculas/acentos).
    """
    # Manejar preflight CORS
    if request.method == 'OPTIONS':
        return jsonify({"success": True}), 200
    
    logger.info("📝 Procesando solicitud de registro de usuario")

    try:
        # 1. Obtener los datos enviados
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No se recibieron datos'}), 400
        
        logger.debug(f"Datos recibidos: {data}")

        # 2. Validación de datos obligatorios
        required_fields = [
            'nombre', 'apellidos', 'correo', 'profesion',
            'cedula', 'celular', 'ciudad', 'contrasenia', 'confirmar_contrasenia'
        ]
        missing_fields = [field for field in required_fields if field not in data or not str(data.get(field, '')).strip()]
        
        if missing_fields:
            logger.warning(f"Campos faltantes: {missing_fields}")
            return jsonify({'error': f"Faltan datos requeridos: {', '.join(missing_fields)}"}), 400

        # 3. Normalizar correo
        correo = data['correo'].strip().lower()

        # 4. Validación de formato de correo
        if '@' not in correo or '.' not in correo:
            return jsonify({'error': 'El formato del correo no es válido'}), 400

        # 5. Validación de coincidencia de contraseñas
        password = data['contrasenia'].strip()
        confirm_password = data['confirmar_contrasenia'].strip()
        
        if password != confirm_password:
            return jsonify({'error': 'Las contraseñas no coinciden'}), 400
        
        if len(password) < 6:
            return jsonify({'error': 'La contraseña debe tener al menos 6 caracteres'}), 400

        # 6. Verificar si el usuario ya existe (por correo)
        if Usuario.query.filter_by(correo=correo).first():
            logger.warning(f"Correo ya registrado: {correo}")
            return jsonify({'error': 'El correo ya está registrado'}), 409
        
        # 7. Verificar si la cédula ya existe
        cedula = str(data['cedula']).strip()
        if Usuario.query.filter_by(cedula=cedula).first():
            logger.warning(f"Cédula ya registrada: {cedula}")
            return jsonify({'error': 'La cédula ya está registrada'}), 409

        # 8. Buscar ciudad de forma FLEXIBLE
        ciudad_obj = buscar_ciudad_flexible(data['ciudad'])
        
        if not ciudad_obj:
            # Dar sugerencias al usuario
            ciudades_similares = Colombia.query.filter(
                Colombia.ciudad_nombre.ilike(f"%{data['ciudad'][:3]}%")
            ).limit(5).all()
            
            sugerencias = [c.ciudad_nombre for c in ciudades_similares]
            
            error_msg = f"No encontramos la ciudad '{data['ciudad']}'"
            if sugerencias:
                error_msg += f". ¿Quisiste decir: {', '.join(sugerencias)}?"
            
            logger.warning(f"Ciudad no válida: {data['ciudad']}")
            return jsonify({'error': error_msg}), 400

        logger.info(f"Ciudad encontrada: {ciudad_obj.ciudad_nombre} (ID: {ciudad_obj.ciudad_id})")

        # 9. Crear la instancia del Usuario
        new_user = Usuario(
            nombre=data['nombre'].strip().title(),
            apellidos=data['apellidos'].strip().title(),
            correo=correo,
            profesion=data['profesion'].strip(),
            cedula=cedula,
            celular=str(data['celular']).strip(),
            ciudad=ciudad_obj.ciudad_id
        )

        # 10. Hashear y asignar la contraseña
        new_user.set_password(password)
        
        # 11. Asignar confirmación de contraseña (requerido por el modelo)
        new_user.confirmacion_contrasenia = new_user.contrasenia

        # 12. Guardar en la base de datos
        db.session.add(new_user)
        db.session.commit()

        logger.info(f"✅ Usuario registrado: {new_user.correo} (ID: {new_user.id_usuario})")
        
        return jsonify({
            'success': True,
            'message': '¡Te has registrado exitosamente!',
            'user_id': new_user.id_usuario
        }), 201

    except SQLAlchemyError as e:
        logger.error(f"❌ Error de base de datos: {e}")
        db.session.rollback()
        return jsonify({'error': 'Error de conexión con la base de datos'}), 500

    except Exception as e:
        logger.exception("❌ Error inesperado durante el registro")
        db.session.rollback()
        return jsonify({'error': 'Ocurrió un error interno'}), 500