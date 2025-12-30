# -*- coding: utf-8 -*-
from src.models.database import db
from src.models.usuarios import Usuario
from src.models.colombia_data.colombia_data import Colombia
import logging
from flask import Blueprint, jsonify, request
from sqlalchemy.exc import SQLAlchemyError

# Configuración del Logger
logger = logging.getLogger(__name__)

# Blueprint para la API de registro de usuarios
register_user_bp = Blueprint('register_user_bp', __name__)

@register_user_bp.route('/register_user', methods=['POST'])
def register_user():
    """
    API para registrar nuevos usuarios sincronizada con el modelo Usuario y Neon Cloud.
    """
    logger.info("Procesando solicitud POST para registrar usuario.")

    try:
        # 1. Obtener los datos enviados
        data = request.get_json()
        logger.debug(f"Datos recibidos: {data}")

        # 2. Validación de datos obligatorios
        required_fields = [
            'nombre', 'apellidos', 'correo', 'profesion',
            'cedula', 'celular', 'ciudad', 'contrasenia', 'confirmar_contrasenia'
        ]
        missing_fields = [field for field in required_fields if field not in data or not data[field]]
        if missing_fields:
            return jsonify({'error': f"Faltan datos requeridos: {', '.join(missing_fields)}"}), 400

        # 3. Validación de coincidencia de contraseñas
        if data['contrasenia'].strip() != data['confirmar_contrasenia'].strip():
            return jsonify({'error': 'Las contraseñas no coinciden.'}), 400

        # 4. Verificar si el usuario ya existe (por correo o cédula)
        if Usuario.query.filter_by(correo=data['correo']).first():
            return jsonify({'error': 'El correo ya está registrado.'}), 409
        
        if Usuario.query.filter_by(cedula=data['cedula']).first():
            return jsonify({'error': 'La cédula ya está registrada.'}), 409

        # 5. Buscar el ID de la ciudad en la tabla Colombia
        # Nota: Asegúrate de que la tabla 'colombia' tenga datos en Neon
        ciudad_obj = Colombia.query.filter_by(ciudad_nombre=data['ciudad'].strip()).first()
        if not ciudad_obj:
            logger.warning(f"Ciudad no encontrada: {data['ciudad']}")
            return jsonify({'error': 'La ciudad ingresada no es válida en nuestro sistema.'}), 400

        # 6. Crear la instancia del Usuario
        # Usamos los nombres de argumentos que definiste en el __init__ de usuarios.py
        new_user = Usuario(
            nombre=data['nombre'],
            apellidos=data['apellidos'],
            correo=data['correo'],
            profesion=data['profesion'],
            cedula=data['cedula'],
            celular=data['celular'],
            ciudad=ciudad_obj.ciudad_id  # Esto llena el campo ciudad_id del __init__
        )

        # 7. Hashear y asignar la contraseña usando el método del modelo
        new_user.set_password(data['contrasenia'].strip())
        
        # 8. IMPORTANTE: Tu modelo exige 'confirmacion_contrasenia' como NO NULA (nullable=False)
        # Por lo tanto, debemos asignarle el hash también para que la DB no de error.
        new_user.confirmacion_contrasenia = new_user.contrasenia

        # 9. Guardar en la base de datos (Neon Cloud)
        db.session.add(new_user)
        db.session.commit()

        logger.info(f"✅ Usuario registrado exitosamente: {new_user.correo}")
        return jsonify({'message': '¡Te has registrado exitosamente!'}), 201

    except SQLAlchemyError as e:
        logger.error(f"❌ Error de base de datos: {e}")
        db.session.rollback()
        return jsonify({'error': 'Error de conexión con la base de datos.'}), 500

    except Exception as e:
        logger.exception("❌ Error inesperado durante el registro.")
        return jsonify({'error': 'Ocurrió un error interno.'}), 500