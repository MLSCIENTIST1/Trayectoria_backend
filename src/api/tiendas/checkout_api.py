"""
Checkout API - TuKomercio v2.0
Procesa pedidos de tiendas online
Ruta: /api/tiendas/<slug>/checkout
"""

from flask import Blueprint, request, jsonify
from flask_cors import cross_origin
import datetime
import random
import string

# ⚠️ IMPORTANTE: El nombre DEBE ser 'checkout_api_bp'
checkout_api_bp = Blueprint('checkout_api', __name__)

print("🏪 Módulo checkout_api iniciando...")


def generate_order_number():
    """Genera número de pedido único"""
    date_str = datetime.datetime.now().strftime('%Y%m%d')
    random_str = ''.join(random.choices(string.digits, k=4))
    return f"TK-{date_str}-{random_str}"


@checkout_api_bp.route('/tiendas/<slug>/checkout', methods=['POST', 'OPTIONS'])
@cross_origin()
def procesar_checkout(slug):
    """
    Procesa un pedido de tienda online
    
    POST /api/tiendas/<slug>/checkout
    
    Payload esperado:
    {
        "negocio_id": 4,
        "comprador": {"nombre": "...", "telefono": "...", "email": "..."},
        "direccion": {"direccion_completa": "...", "ciudad": "...", ...},
        "productos": [{"producto_id": 40, "nombre": "...", "cantidad": 1, "precio_unitario": 50000}],
        "subtotal": 50000,
        "costo_envio": 8000,
        "total": 58000,
        "metodo_pago": "efectivo",
        "notas": "..."
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
        print(f"Comprador: {data.get('comprador', {}).get('nombre')}")
        print(f"Total: ${data.get('total', 0):,}")
        
        # Validar datos requeridos
        if not data:
            return jsonify({'success': False, 'error': 'No se recibieron datos'}), 400
        
        negocio_id = data.get('negocio_id')
        comprador = data.get('comprador', {})
        productos = data.get('productos', [])
        
        if not negocio_id:
            return jsonify({'success': False, 'error': 'negocio_id requerido'}), 400
        
        if not comprador.get('nombre'):
            return jsonify({'success': False, 'error': 'Nombre del comprador requerido'}), 400
        
        if not comprador.get('telefono'):
            return jsonify({'success': False, 'error': 'Teléfono requerido'}), 400
        
        if not productos:
            return jsonify({'success': False, 'error': 'Agrega al menos un producto'}), 400
        
        # Generar número de pedido
        numero_pedido = generate_order_number()
        
        # Conectar a base de datos
        try:
            from src.utils.db import get_db_connection
            conn = get_db_connection()
            cursor = conn.cursor()
            
            print("✅ Conexión a BD establecida")
            
            # 1. COMPRADOR - Buscar o crear
            cursor.execute("""
                SELECT id_comprador FROM compradores 
                WHERE telefono = %s OR email = %s
                LIMIT 1
            """, (comprador.get('telefono'), comprador.get('email')))
            
            result = cursor.fetchone()
            
            if result:
                comprador_id = result[0]
                print(f"✅ Comprador existente: {comprador_id}")
                
                # Actualizar datos
                cursor.execute("""
                    UPDATE compradores 
                    SET nombre = %s, email = %s, fecha_ultima_compra = NOW()
                    WHERE id_comprador = %s
                """, (comprador.get('nombre'), comprador.get('email'), comprador_id))
            else:
                # Crear nuevo
                cursor.execute("""
                    INSERT INTO compradores (nombre, telefono, email, fecha_registro)
                    VALUES (%s, %s, %s, NOW())
                    RETURNING id_comprador
                """, (comprador.get('nombre'), comprador.get('telefono'), comprador.get('email')))
                
                comprador_id = cursor.fetchone()[0]
                print(f"✅ Nuevo comprador: {comprador_id}")
            
            # 2. DIRECCIÓN - Guardar si existe
            direccion_id = None
            direccion_data = data.get('direccion', {})
            
            if direccion_data and direccion_data.get('direccion_completa'):
                cursor.execute("""
                    INSERT INTO direcciones_comprador 
                    (comprador_id, direccion_completa, ciudad, departamento, tipo)
                    VALUES (%s, %s, %s, %s, %s)
                    ON CONFLICT DO NOTHING
                    RETURNING id_direccion
                """, (
                    comprador_id,
                    direccion_data.get('direccion_completa'),
                    direccion_data.get('ciudad'),
                    direccion_data.get('departamento'),
                    direccion_data.get('tipo', 'residencia')
                ))
                
                result = cursor.fetchone()
                if result:
                    direccion_id = result[0]
                    print(f"✅ Dirección guardada: {direccion_id}")
            
            # 3. PEDIDO - Crear
            cursor.execute("""
                INSERT INTO pedidos 
                (numero_pedido, negocio_id, comprador_id, direccion_id,
                 subtotal, costo_envio, total, metodo_pago, estado, notas,
                 fecha_creacion, fecha_actualizacion)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, 'pendiente', %s, NOW(), NOW())
                RETURNING id_pedido
            """, (
                numero_pedido,
                negocio_id,
                comprador_id,
                direccion_id,
                data.get('subtotal', 0),
                data.get('costo_envio', 0),
                data.get('total', 0),
                data.get('metodo_pago', 'efectivo'),
                data.get('notas')
            ))
            
            pedido_id = cursor.fetchone()[0]
            print(f"✅ Pedido creado: {pedido_id} - {numero_pedido}")
            
            # 4. DETALLE DEL PEDIDO - Agregar productos
            for producto in productos:
                cursor.execute("""
                    INSERT INTO detalle_pedido 
                    (pedido_id, producto_id, cantidad, precio_unitario, subtotal)
                    VALUES (%s, %s, %s, %s, %s)
                """, (
                    pedido_id,
                    producto.get('producto_id'),
                    producto.get('cantidad', 1),
                    producto.get('precio_unitario', 0),
                    producto.get('cantidad', 1) * producto.get('precio_unitario', 0)
                ))
            
            print(f"✅ {len(productos)} productos agregados")
            
            # COMMIT
            conn.commit()
            print("✅ Transacción completada")
            
            # Preparar respuesta
            response_data = {
                'id_pedido': pedido_id,
                'numero_pedido': numero_pedido,
                'negocio_id': negocio_id,
                'comprador_id': comprador_id,
                'total': data.get('total', 0),
                'estado': 'pendiente',
                'fecha': datetime.datetime.now().isoformat()
            }
            
            cursor.close()
            conn.close()
            
            print(f"✅ Checkout completado: {numero_pedido}\n")
            
            return jsonify({
                'success': True,
                'message': '¡Pedido creado exitosamente!',
                'pedido': response_data
            }), 201
            
        except Exception as db_error:
            if 'conn' in locals():
                conn.rollback()
                conn.close()
            
            print(f"❌ Error en BD: {str(db_error)}")
            import traceback
            traceback.print_exc()
            
            raise db_error
        
    except Exception as e:
        print(f"❌ Error general: {str(e)}")
        import traceback
        traceback.print_exc()
        
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
        'version': '2.0'
    }), 200


@checkout_api_bp.route('/health', methods=['GET'])
def health():
    """Health check"""
    return jsonify({
        'status': 'online',
        'module': 'checkout_api',
        'version': '2.0'
    }), 200


print("✅ Módulo checkout_api cargado correctamente")
print("   Rutas disponibles:")
print("   - POST /api/tiendas/<slug>/checkout")
print("   - GET  /api/tiendas/<slug>/checkout/test")