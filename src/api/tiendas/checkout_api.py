"""
Checkout API - TuKomercio v3.1
Usa modelos SQLAlchemy existentes (Comprador, DireccionComprador, Pedido)
★ NUEVO: Crea notificación automática para la campanita
Ruta: /api/tiendas/<slug>/checkout
"""

from flask import Blueprint, request, jsonify
from flask_cors import cross_origin
import datetime

# Importar modelos existentes
from src.models import Comprador
from src.models import DireccionComprador
from src.models import Pedido 
from src.models.database import db

# ★ NUEVO: Importar modelo de notificaciones
try:
    from src.models.notification import Notification
    TIENE_NOTIFICACIONES = True
except ImportError:
    TIENE_NOTIFICACIONES = False
    print("⚠️ Modelo Notification no disponible - notificaciones desactivadas")

checkout_api_bp = Blueprint('checkout_api', __name__)

print("🏪 Módulo checkout_api v3.1 iniciando (con notificaciones)...")


@checkout_api_bp.route('/tiendas/<slug>/checkout', methods=['POST', 'OPTIONS'])
@cross_origin()
def procesar_checkout(slug):
    """
    Procesa un pedido de la tienda online usando los modelos SQLAlchemy existentes.
    ★ NUEVO: Crea notificación automática para la campanita del dueño.
    
    POST /api/tiendas/<slug>/checkout
    
    Body:
    {
        "negocio_id": 4,
        "comprador": {
            "nombre": "Juan Pérez",
            "telefono": "3001234567",
            "email": "juan@email.com"
        },
        "direccion": {
            "direccion_completa": "Calle 123 #45-67, Bogotá",
            "ciudad": "Bogotá",
            "departamento": "Cundinamarca",
            "tipo": "residencia"
        },
        "productos": [
            {
                "producto_id": 40,
                "nombre": "Producto X",
                "cantidad": 2,
                "precio_unitario": 50000
            }
        ],
        "subtotal": 100000,
        "costo_envio": 8000,
        "total": 108000,
        "metodo_pago": "efectivo",
        "notas": "Llamar antes de entregar"
    }
    """
    
    # Manejar preflight CORS
    if request.method == 'OPTIONS':
        return '', 204
    
    try:
        data = request.json
        
        print(f"\n📦 === CHECKOUT RECIBIDO ===")
        print(f"Tienda: {slug}")
        print(f"Negocio ID: {data.get('negocio_id')}")
        
        # Validar datos requeridos
        if not data:
            return jsonify({'success': False, 'error': 'No se recibieron datos'}), 400
        
        negocio_id = data.get('negocio_id')
        comprador_data = data.get('comprador', {})
        direccion_data = data.get('direccion', {})
        productos = data.get('productos', [])
        
        # Validaciones
        if not negocio_id:
            return jsonify({'success': False, 'error': 'negocio_id requerido'}), 400
        
        if not comprador_data.get('nombre'):
            return jsonify({'success': False, 'error': 'Nombre del comprador requerido'}), 400
        
        if not comprador_data.get('telefono'):
            return jsonify({'success': False, 'error': 'Teléfono requerido'}), 400
        
        if not productos:
            return jsonify({'success': False, 'error': 'Agrega al menos un producto'}), 400
        
        # ==========================================
        # 1. BUSCAR O CREAR COMPRADOR
        # ==========================================
        email = comprador_data.get('email', '').strip()
        telefono = comprador_data.get('telefono', '').strip()
        nombre = comprador_data.get('nombre', '').strip()
        
        # Buscar por email o teléfono
        comprador = None
        if email:
            comprador = Comprador.buscar_por_correo(email)
        
        if not comprador and telefono:
            comprador = Comprador.buscar_por_telefono(telefono)
        
        if comprador:
            print(f"✅ Comprador existente: {comprador.id_comprador} - {comprador.nombre}")
            
            # Actualizar información si es necesario
            if nombre and nombre != comprador.nombre:
                comprador.nombre = nombre
            if email and email != comprador.correo:
                comprador.correo = email
            if telefono and telefono != comprador.telefono:
                comprador.telefono = telefono
        else:
            # Crear nuevo comprador (invitado)
            print("🆕 Creando nuevo comprador...")
            
            if not email:
                # Generar email temporal si no se proporciona
                email = f"{telefono}@temp.tukomercio.com"
            
            comprador = Comprador.crear_invitado(
                nombre=nombre,
                correo=email,
                telefono=telefono
            )
            
            print(f"✅ Nuevo comprador creado: {comprador.nombre}")
        
        # ==========================================
        # 2. CREAR O BUSCAR DIRECCIÓN
        # ==========================================
        direccion = None
        
        if direccion_data and direccion_data.get('direccion_completa'):
            print("📍 Procesando dirección...")
            
            # Buscar si existe una dirección similar
            direcciones_existentes = comprador.direcciones.filter_by(activo=True).all()
            
            for d in direcciones_existentes:
                if (d.direccion_completa.lower().strip() == 
                    direccion_data.get('direccion_completa', '').lower().strip()):
                    direccion = d
                    print(f"✅ Dirección existente encontrada: {direccion.id_direccion}")
                    break
            
            if not direccion:
                # Crear nueva dirección usando el factory method del modelo
                direccion = DireccionComprador.crear_desde_checkout(
                    comprador_id=comprador.id_comprador,
                    direccion_data=direccion_data
                )
                db.session.add(direccion)
                print(f"✅ Nueva dirección creada")
        
        # ==========================================
        # 3. CREAR PEDIDO
        # ==========================================
        print("📝 Creando pedido...")
        
        # Preparar datos del negocio
        negocio_data = {
            'id': negocio_id,
            'slug': slug,
            'nombre': data.get('nombre_negocio', slug.capitalize())
        }
        
        # Crear pedido usando el método del modelo
        pedido = Pedido.crear_pedido(
            comprador=comprador,
            direccion=direccion,
            negocio_data=negocio_data,
            productos=productos,
            subtotal=data.get('subtotal', 0),
            costo_envio=data.get('costo_envio', 0),
            total=data.get('total', 0),
            metodo_pago=data.get('metodo_pago', 'efectivo'),
            notas_cliente=data.get('notas'),
            metodo_contacto='whatsapp',
            origen='web'
        )
        
        print(f"✅ Pedido creado: {pedido.codigo_pedido}")
        
        # ==========================================
        # ★ 4. CREAR NOTIFICACIÓN PARA LA CAMPANITA
        # ==========================================
        notificacion_creada = False
        if TIENE_NOTIFICACIONES:
            try:
                # Flush para obtener el ID del pedido
                db.session.flush()
                
                notificacion = Notification.crear_notificacion_pedido(pedido)
                notificacion_creada = True
                print(f"🔔 Notificación creada para campanita")
            except Exception as notif_error:
                print(f"⚠️ Error creando notificación (no crítico): {notif_error}")
                # No fallar el pedido por esto
        
        # ==========================================
        # 5. GUARDAR TODO EN LA BASE DE DATOS
        # ==========================================
        try:
            db.session.commit()
            print("✅ Transacción completada exitosamente")
            
        except Exception as commit_error:
            db.session.rollback()
            print(f"❌ Error al guardar en BD: {str(commit_error)}")
            raise commit_error
        
        # ==========================================
        # 6. PREPARAR RESPUESTA
        # ==========================================
        response_data = {
            'success': True,
            'message': '¡Pedido creado exitosamente!',
            'pedido': {
                'id_pedido': pedido.id_pedido,
                'numero_pedido': pedido.codigo_pedido,
                'codigo_pedido': pedido.codigo_pedido,
                'negocio_id': negocio_id,
                'total': float(data.get('total', 0)),
                'estado': pedido.estado,
                'fecha_creacion': pedido.fecha_pedido.isoformat()
            },
            'comprador': comprador.to_dict_checkout(),  # Incluye el token
            'notificacion_enviada': notificacion_creada  # ★ NUEVO
        }
        
        print(f"✅ Checkout completado: {pedido.codigo_pedido}")
        print(f"   Comprador: {comprador.nombre} (ID: {comprador.id_comprador})")
        print(f"   Token: {comprador.token_acceso}")
        print(f"   Total: ${data.get('total', 0):,}")
        print(f"   🔔 Notificación: {'Sí' if notificacion_creada else 'No'}\n")
        
        return jsonify(response_data), 201
        
    except ValueError as ve:
        print(f"❌ Error de validación: {str(ve)}")
        return jsonify({
            'success': False,
            'error': str(ve)
        }), 400
        
    except Exception as e:
        print(f"❌ Error general: {str(e)}")
        import traceback
        traceback.print_exc()
        
        # Rollback en caso de error
        try:
            db.session.rollback()
        except:
            pass
        
        return jsonify({
            'success': False,
            'error': f'Error procesando pedido: {str(e)}'
        }), 500


@checkout_api_bp.route('/tiendas/<slug>/checkout/test', methods=['GET'])
@cross_origin()
def test_checkout(slug):
    """Endpoint de prueba"""
    return jsonify({
        'success': True,
        'message': f'✅ Checkout funcionando para: {slug}',
        'endpoint': f'/api/tiendas/{slug}/checkout',
        'version': '3.1',
        'models': 'SQLAlchemy (Comprador, DireccionComprador, Pedido)',
        'notificaciones': TIENE_NOTIFICACIONES
    }), 200


@checkout_api_bp.route('/health', methods=['GET'])
def health():
    """Health check"""
    return jsonify({
        'status': 'online',
        'module': 'checkout_api',
        'version': '3.1',
        'database': 'SQLAlchemy',
        'notificaciones': TIENE_NOTIFICACIONES
    }), 200


print("✅ Módulo checkout_api v3.1 cargado correctamente")
print("   Modelos utilizados:")
print("   - Comprador (con token_acceso)")
print("   - DireccionComprador")
print("   - Pedido")
print(f"   - Notification: {'✅ Activo' if TIENE_NOTIFICACIONES else '❌ No disponible'}")