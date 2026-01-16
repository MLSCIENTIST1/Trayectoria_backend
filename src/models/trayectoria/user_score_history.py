# 🚀 BizFlow Studio DELUXE - Guía de Integración Backend

## 📋 Contenido

1. [Configuración del Backend Python](#1-configuración-del-backend-python)
2. [Estructura de Base de Datos](#2-estructura-de-base-de-datos)
3. [Integración con el Frontend](#3-integración-con-el-frontend)
4. [Endpoints Disponibles](#4-endpoints-disponibles)
5. [Testing y Desarrollo](#5-testing-y-desarrollo)

---

## 1. Configuración del Backend Python

### 1.1 Instalar Dependencias

```bash
# Crear entorno virtual (recomendado)
python -m venv venv

# Activar entorno virtual
# En Windows:
venv\Scripts\activate
# En Linux/Mac:
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt
```

### 1.2 Configurar Variables de Entorno

Crea un archivo `.env` en la raíz del proyecto:

```env
# .env
SECRET_KEY=tu-clave-secreta-super-segura-cambiar-en-produccion
JWT_SECRET_KEY=jwt-clave-secreta-cambiar-en-produccion
MONGODB_URI=mongodb://localhost:27017/
DATABASE_NAME=bizflow
UPLOAD_FOLDER=uploads
MAX_UPLOAD_SIZE=524288000  # 500MB
FLASK_ENV=development
```

### 1.3 Iniciar el Servidor

```bash
python backend_api.py
```

El servidor estará corriendo en `http://localhost:5000`

---

## 2. Estructura de Base de Datos

### 2.1 MongoDB Collections

#### **users** (Usuarios)
```javascript
{
  _id: ObjectId,
  nombre: "Carlos Mendoza",
  email: "carlos@example.com",
  password: "hash_bcrypt",
  ciudad: "Bogotá, Colombia",
  foto_url: "/uploads/avatars/user123.jpg",
  tagline: "Desarrollador Full Stack",
  verificado: true,
  fecha_registro: ISODate("2023-01-15"),
  badges: ["elite", "verified"],
  stats: {
    satisfaccion: 98,
    experiencia_anos: 2.4,
    tiempo_promedio_dias: 12,
    total_contratos: 127
  }
}
```

#### **scores** (Puntajes)
```javascript
{
  _id: ObjectId,
  user_id: "user123",
  contratante: 87,
  contratado: 92,
  global: 89,
  fecha: ISODate("2024-01-16"),
  cambios: {
    contratante: +3,
    contratado: +2,
    global: +2
  }
}
```

#### **score_history** (Historial de Scores)
```javascript
{
  _id: ObjectId,
  user_id: "user123",
  fecha: ISODate("2024-01-01"),
  score: 90,
  tipo: "contratado"  // contratante | contratado | global
}
```

#### **stages** (Etapas por usuario)
```javascript
{
  _id: ObjectId,
  user_id: "user123",
  stage_id: "e1",
  nombre: "Primer Contacto",
  score: 4.9,
  visible: true,
  metricas: [
    { label: "Velocidad", valor: "15 min", icono: "lightning-charge" },
    { label: "Profesionalismo", valor: "4.9", icono: "chat-heart" }
  ]
}
```

#### **badges** (Logros del usuario)
```javascript
{
  _id: ObjectId,
  user_id: "user123",
  badge_id: "primera-estrella",
  desbloqueado: true,
  fecha_desbloqueo: ISODate("2023-02-10")
}
```

#### **videos** (Videos del portfolio)
```javascript
{
  _id: ObjectId,
  user_id: "user123",
  titulo: "App E-commerce",
  descripcion: "Mi mejor trabajo",
  url: "/uploads/videos/video1.mp4",
  thumbnail: "/uploads/thumbnails/video1.jpg",
  duracion: "2:00:58",
  vistas: 1200,
  likes: 89,
  fecha: ISODate("2024-01-10"),
  metricas_asociadas: ["proyectos", "rating"],
  badges_asociados: ["perfeccionista", "rayo-veloz"]
}
```

#### **notifications** (Notificaciones)
```javascript
{
  _id: ObjectId,
  user_id: "user123",
  tipo: "score_up",
  titulo: "¡Tu score subió!",
  mensaje: "Tu puntaje aumentó de 90 a 92",
  icono: "graph-up-arrow",
  color: "#10b981",
  fecha: ISODate("2024-01-16T10:00:00Z"),
  leida: false
}
```

### 2.2 Crear Índices (Importante para Performance)

```javascript
// En MongoDB shell o MongoDB Compass
db.users.createIndex({ email: 1 }, { unique: true });
db.scores.createIndex({ user_id: 1, fecha: -1 });
db.score_history.createIndex({ user_id: 1, fecha: -1 });
db.videos.createIndex({ user_id: 1, fecha: -1 });
db.notifications.createIndex({ user_id: 1, fecha: -1, leida: 1 });
```

---

## 3. Integración con el Frontend

### 3.1 Agregar Scripts al HTML

Modifica tu archivo HTML para incluir los nuevos archivos JavaScript **antes** del cierre de `</body>`:

```html
<!-- Justo antes de tu script inline existente -->
<script src="api-service.js"></script>
<script src="data-manager.js"></script>

<!-- Tu script existente sigue aquí -->
<script>
(function() {
    'use strict';
    // ... tu código existente ...
})();
</script>
```

### 3.2 Actualizar Funciones Existentes

Algunas funciones necesitan modificarse para usar el backend:

#### Cambiar `setChartPeriod`:
```javascript
// ANTES
window.setChartPeriod = function(period, btn) {
    sounds.playClick();
    // ... código existente
};

// DESPUÉS
window.setChartPeriod = async function(period, btn) {
    sounds.playClick();
    document.querySelectorAll('.chart-filter').forEach(b => b.classList.remove('active'));
    btn.classList.add('active');
    await dataManager.setChartPeriod(period);
};
```

#### Cambiar `uploadAvatar`:
```javascript
// DESPUÉS de la línea: reader.onload = function(ev) {
document.getElementById('avatarInput').addEventListener('change', function(e) {
    var file = e.target.files[0];
    if (file) {
        dataManager.uploadAvatar(file);
    }
});
```

#### Cambiar `uploadVideo`:
```javascript
window.uploadVideo = async function() {
    sounds.playUpload();
    var title = document.getElementById('newVideoTitle').value || 'Nuevo Video';
    var fileInput = document.getElementById('videoInput');
    
    if (fileInput.files.length > 0) {
        await dataManager.uploadVideo({
            file: fileInput.files[0],
            title: title
        });
    }
    
    closeUploadModal();
    document.getElementById('newVideoTitle').value = '';
};
```

### 3.3 Configurar la URL del Backend

En `api-service.js`, cambia la URL base si tu backend no está en localhost:5000:

```javascript
// En producción, cambiar a tu dominio
const api = new BizFlowAPI('https://api.tudominio.com/api');
```

---

## 4. Endpoints Disponibles

### 🔐 Autenticación

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| POST | `/api/auth/login` | Login de usuario |
| POST | `/api/auth/register` | Registro de usuario |

### 👤 Perfil

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/api/users/<user_id>/profile` | Obtener perfil |
| PUT | `/api/users/<user_id>/profile` | Actualizar perfil |
| POST | `/api/users/<user_id>/avatar` | Subir avatar |

### 📊 Scores

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/api/users/<user_id>/scores` | Obtener scores |
| GET | `/api/users/<user_id>/scores/history?period=6m` | Historial |
| GET | `/api/users/<user_id>/percentile` | Obtener percentil |

### 📈 Métricas

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/api/users/<user_id>/metrics` | Todas las métricas |
| GET | `/api/users/<user_id>/metrics/<category>` | Por categoría |

### 🎯 Etapas

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/api/users/<user_id>/stages` | Obtener etapas |
| PATCH | `/api/users/<user_id>/stages/<stage_id>/visibility` | Cambiar visibilidad |

### 🏆 Badges

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/api/users/<user_id>/badges` | Obtener badges |
| GET | `/api/users/<user_id>/badges/progress` | Progreso de badges |

### 🎥 Videos

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/api/users/<user_id>/videos` | Lista de videos |
| POST | `/api/users/<user_id>/videos` | Subir video |
| PUT | `/api/users/<user_id>/videos/<video_id>` | Actualizar video |
| DELETE | `/api/users/<user_id>/videos/<video_id>` | Eliminar video |
| POST | `/api/users/<user_id>/videos/<video_id>/metrics` | Asociar métricas |
| POST | `/api/users/<user_id>/videos/<video_id>/badges` | Asociar badges |

### 🔔 Notificaciones

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/api/users/<user_id>/notifications` | Obtener notificaciones |
| PATCH | `/api/users/<user_id>/notifications/<notif_id>/read` | Marcar como leída |
| PATCH | `/api/users/<user_id>/notifications/read-all` | Marcar todas |

---

## 5. Testing y Desarrollo

### 5.1 Probar con cURL

#### Login:
```bash
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"carlos@example.com","password":"123456"}'
```

#### Obtener perfil (con token):
```bash
curl -X GET http://localhost:5000/api/users/user123/profile \
  -H "Authorization: Bearer TU_TOKEN_AQUI"
```

### 5.2 Datos de Prueba

Para desarrollo, puedes crear un script para poblar la base de datos:

```python
# seed_data.py
from pymongo import MongoClient
from datetime import datetime

client = MongoClient('mongodb://localhost:27017/')
db = client['bizflow']

# Usuario de prueba
db.users.insert_one({
    'nombre': 'Carlos Mendoza',
    'email': 'carlos@example.com',
    'password': 'hash_bcrypt',  # En producción usar generate_password_hash
    'ciudad': 'Bogotá, Colombia',
    'foto_url': None,
    'tagline': 'Desarrollador Full Stack',
    'verificado': True,
    'fecha_registro': datetime(2023, 1, 15),
    'badges': ['elite', 'verified'],
    'stats': {
        'satisfaccion': 98,
        'experiencia_anos': 2.4,
        'tiempo_promedio_dias': 12,
        'total_contratos': 127
    }
})

print("✅ Datos de prueba creados")
```

### 5.3 Activar CORS para Desarrollo

Si frontend y backend están en dominios diferentes, CORS ya está configurado en `backend_api.py`:

```python
from flask_cors import CORS
CORS(app)  # Permite todas las origins en desarrollo
```

Para producción, especifica origins permitidos:
```python
CORS(app, origins=['https://tudominio.com'])
```

---

## 📁 Estructura Final del Proyecto

```
bizflow-studio/
├── frontend/
│   ├── index.html              # Tu archivo HTML existente
│   ├── api-service.js          # ✨ NUEVO - Cliente API
│   ├── data-manager.js         # ✨ NUEVO - Gestor de datos
│   └── assets/
├── backend/
│   ├── backend_api.py          # ✨ NUEVO - API Python
│   ├── requirements.txt        # ✨ NUEVO - Dependencias
│   ├── .env                    # Configuración (crear)
│   └── uploads/                # Carpeta para archivos
│       ├── avatars/
│       ├── videos/
│       └── thumbnails/
└── README_INTEGRATION.md       # ✨ NUEVO - Esta guía
```

---

## 🔥 Quick Start (Desarrollo Local)

```bash
# 1. Clonar/Descargar el proyecto
cd bizflow-studio

# 2. Instalar MongoDB (si no lo tienes)
# Ver: https://www.mongodb.com/docs/manual/installation/

# 3. Backend
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python backend_api.py

# 4. Frontend (en otra terminal)
cd frontend
# Usar un servidor simple, por ejemplo:
python -m http.server 8000
# O si tienes Node.js instalado:
npx serve .

# 5. Abrir navegador
# http://localhost:8000
```

---

## 🚀 Deployment en Producción

### Backend (Python):
- **Heroku**: `git push heroku main`
- **Railway**: Conectar repo de GitHub
- **DigitalOcean**: Droplet con Gunicorn
- **AWS EC2**: Nginx + Gunicorn

### Frontend:
- **Vercel**: Conectar repo, deploy automático
- **Netlify**: Arrastrar carpeta o GitHub
- **GitHub Pages**: Solo archivos estáticos
- **AWS S3 + CloudFront**: Hosting + CDN

### Base de Datos:
- **MongoDB Atlas**: Free tier disponible
- **MongoDB Cloud**: Managed service
- **Self-hosted**: VPS con MongoDB

---

## 🛠️ Troubleshooting

### Error: CORS
```
Access to fetch at 'http://localhost:5000' from origin 'http://localhost:8000' 
has been blocked by CORS policy
```
**Solución**: Asegúrate de que `flask-cors` esté instalado y configurado.

### Error: 401 Unauthorized
**Solución**: Verifica que el token JWT esté siendo enviado correctamente en los headers.

### Error: No se cargan los datos
1. Verifica que el backend esté corriendo
2. Abre DevTools → Network → Verifica las peticiones
3. Revisa la consola por errores JavaScript

---

## 📞 Soporte

¿Problemas? ¿Preguntas?

1. Revisa los logs del backend: `python backend_api.py`
2. Revisa la consola del navegador (F12)
3. Verifica que MongoDB esté corriendo: `mongosh`

---

**¡Listo! Ahora tu aplicación está conectada con el backend en Python.** 🎉