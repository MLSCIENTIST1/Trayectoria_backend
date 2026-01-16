# ============================================
# ENDPOINT PARA ACTUALIZAR AVATAR
# Agregar a tu archivo de rutas de usuarios
# ============================================

# Si usas Flask:
# ----------------------------------------

from flask import Blueprint, request, jsonify
from functools import wraps
# Importa tu conexión a Neon y decorador de autenticación

@users_bp.route('/api/users/<int:user_id>/avatar', methods=['PATCH'])
@token_required  # Tu decorador de autenticación
def update_avatar(current_user, user_id):
    """
    Actualiza la foto de perfil del usuario
    
    Body esperado:
    {
        "foto_url": "https://res.cloudinary.com/dp50v0bwj/image/upload/v1234/avatars/abc123.jpg"
    }
    """
    
    # Verificar que el usuario solo pueda actualizar su propio avatar
    if current_user.id != user_id:
        return jsonify({
            'success': False,
            'error': 'No autorizado'
        }), 403
    
    data = request.get_json()
    
    if not data or 'foto_url' not in data:
        return jsonify({
            'success': False,
            'error': 'foto_url es requerido'
        }), 400
    
    foto_url = data['foto_url']
    
    # Validar que sea una URL de Cloudinary válida
    if not foto_url.startswith('https://res.cloudinary.com/'):
        return jsonify({
            'success': False,
            'error': 'URL de imagen no válida'
        }), 400
    
    try:
        # Actualizar en base de datos Neon
        # Opción 1: Si usas SQLAlchemy
        current_user.foto_url = foto_url
        db.session.commit()
        
        # Opción 2: Si usas psycopg2 directamente
        # cursor.execute(
        #     "UPDATE usuarios SET foto_url = %s WHERE id = %s",
        #     (foto_url, user_id)
        # )
        # conn.commit()
        
        return jsonify({
            'success': True,
            'message': 'Avatar actualizado correctamente',
            'data': {
                'foto_url': foto_url
            }
        }), 200
        
    except Exception as e:
        print(f"Error actualizando avatar: {e}")
        return jsonify({
            'success': False,
            'error': 'Error interno del servidor'
        }), 500


# ============================================
# Si usas FastAPI:
# ============================================

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, HttpUrl

router = APIRouter()

class AvatarUpdate(BaseModel):
    foto_url: HttpUrl

@router.patch("/api/users/{user_id}/avatar")
async def update_avatar(
    user_id: int, 
    avatar_data: AvatarUpdate,
    current_user = Depends(get_current_user)  # Tu dependencia de auth
):
    """
    Actualiza la foto de perfil del usuario
    """
    
    # Verificar autorización
    if current_user.id != user_id:
        raise HTTPException(status_code=403, detail="No autorizado")
    
    foto_url = str(avatar_data.foto_url)
    
    # Validar URL de Cloudinary
    if not foto_url.startswith('https://res.cloudinary.com/'):
        raise HTTPException(status_code=400, detail="URL de imagen no válida")
    
    try:
        # Actualizar en Neon (usando asyncpg o similar)
        await db.execute(
            "UPDATE usuarios SET foto_url = $1 WHERE id = $2",
            foto_url, user_id
        )
        
        return {
            "success": True,
            "message": "Avatar actualizado correctamente",
            "data": {"foto_url": foto_url}
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================
# SQL para verificar/crear la columna
# ============================================

"""
-- Verificar si la columna existe
SELECT column_name 
FROM information_schema.columns 
WHERE table_name = 'usuarios' AND column_name = 'foto_url';

-- Si no existe, crearla:
ALTER TABLE usuarios 
ADD COLUMN IF NOT EXISTS foto_url VARCHAR(500) DEFAULT NULL;

-- Crear índice para búsquedas más rápidas (opcional)
CREATE INDEX IF NOT EXISTS idx_usuarios_foto_url ON usuarios(foto_url);
"""


# ============================================
# Ejemplo de modelo SQLAlchemy (si lo usas)
# ============================================

"""
class Usuario(db.Model):
    __tablename__ = 'usuarios'
    
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    profesion = db.Column(db.String(100))
    ciudad = db.Column(db.String(100))
    foto_url = db.Column(db.String(500), nullable=True)  # ← Campo para avatar
    fecha_registro = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'nombre': self.nombre,
            'email': self.email,
            'profesion': self.profesion,
            'ciudad': self.ciudad,
            'foto_url': self.foto_url,
            'fecha_registro': self.fecha_registro.isoformat() if self.fecha_registro else None
        }
"""