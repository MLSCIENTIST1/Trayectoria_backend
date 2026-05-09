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

# ★ Cupones
try:
    from src.models.colombia_data.contabilidad.cupones import Cupon
    TIENE_CUPONES = True
except ImportError:
    TIENE_CUPONES = False
    print("⚠️ Modelo Cupon no disponible - cupones desactivados")

# ★ NUEVO: Importar modelo de notificaciones
try:
    from src.models.notification import Notification
    TIENE_NOTIFICACIONES = True
except ImportError:
    TIENE_NOTIFICACIONES = False
    print("⚠️ Modelo Notification no disponible - notificaciones desactivadas")

# ★ Email al tendero
try:
    from src.api.auth.password_reset_api import send_email_async
    from src.models.colombia_data.negocio import Negocio
    TIENE_EMAIL = True
except ImportError:
    TIENE_EMAIL = False
    print("⚠️ Email no disponible")

checkout_api_bp = Blueprint('checkout_api', __name__)

print("🏪 Módulo checkout_api v3.1 iniciando (con notificaciones)...")


# ══════════════════════════════════════════════════════════════════════════════
# EMAIL AL TENDERO — nuevo pedido
# ══════════════════════════════════════════════════════════════════════════════

def _fmt_cop(n):
    """Formatea número como peso colombiano."""
    try:
        return f"${int(float(n)):,}".replace(',', '.')
    except Exception:
        return f"${n}"


def _html_email_nuevo_pedido(pedido, negocio, comprador, productos_payload,
                              subtotal, descuento, costo_envio, total):
    """Genera el HTML del email de nuevo pedido para el tendero."""
    nombre_negocio = getattr(negocio, 'nombre_negocio', None) or getattr(negocio, 'nombre', 'Tu negocio')
    codigo = pedido.codigo_pedido
    fecha = pedido.fecha_pedido.strftime('%d/%m/%Y %H:%M') if pedido.fecha_pedido else '—'
    cliente = comprador.nombre or '—'
    telefono = comprador.telefono or '—'
    correo_cliente = comprador.correo or '—'
    metodo_pago = (pedido.metodo_pago or 'efectivo').capitalize()
    notas = pedido.notas_cliente or ''
    slug = getattr(negocio, 'slug', '')

    # Filas de productos
    filas_productos = ''
    for p in (productos_payload or []):
        nom = p.get('nombre', 'Producto')
        qty = p.get('cantidad', p.get('qty', 1))
        precio = float(p.get('precio_unitario', p.get('precio', 0)))
        filas_productos += f"""
        <tr>
          <td style="padding:10px 12px;border-bottom:1px solid #f0f0f0;font-size:14px;color:#333;">{nom}</td>
          <td style="padding:10px 12px;border-bottom:1px solid #f0f0f0;font-size:14px;color:#666;text-align:center;">{qty}</td>
          <td style="padding:10px 12px;border-bottom:1px solid #f0f0f0;font-size:14px;color:#333;text-align:right;font-weight:600;">{_fmt_cop(precio * qty)}</td>
        </tr>"""

    # Fila descuento
    fila_descuento = ''
    if descuento and float(descuento) > 0:
        fila_descuento = f"""
        <tr>
          <td colspan="2" style="padding:8px 12px;font-size:13px;color:#D63329;">🏷️ Descuento</td>
          <td style="padding:8px 12px;font-size:13px;color:#D63329;text-align:right;font-weight:600;">-{_fmt_cop(descuento)}</td>
        </tr>"""

    # Fila envío
    fila_envio = ''
    if costo_envio and float(costo_envio) > 0:
        fila_envio = f"""
        <tr>
          <td colspan="2" style="padding:8px 12px;font-size:13px;color:#2563EB;">🚚 Envío</td>
          <td style="padding:8px 12px;font-size:13px;color:#2563EB;text-align:right;font-weight:600;">{_fmt_cop(costo_envio)}</td>
        </tr>"""

    link_pedidos = f"https://tuko.pages.dev/contabilidad/modulos/pedidos.html"
    link_wa = f"https://wa.me/57{telefono.replace(' ','').replace('-','').lstrip('0')}?text=Hola+{cliente.split()[0]}%2C+recibimos+tu+pedido+{codigo}+%F0%9F%93%A6"

    return f"""<!DOCTYPE html>
<html lang="es">
<head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1"></head>
<body style="margin:0;padding:0;background:#f5f5f5;font-family:'Segoe UI',Arial,sans-serif;">
  <div style="max-width:560px;margin:32px auto;background:#fff;border-radius:16px;overflow:hidden;box-shadow:0 4px 24px rgba(0,0,0,0.10);">

    <!-- Header -->
    <div style="background:linear-gradient(135deg,#D63329 0%,#A8251C 100%);padding:28px 32px;text-align:center;">
      <div style="font-size:11px;letter-spacing:3px;text-transform:uppercase;color:rgba(255,255,255,0.7);margin-bottom:6px;">TuKomercio · {nombre_negocio}</div>
      <div style="font-size:26px;font-weight:900;color:#fff;letter-spacing:1px;">🛒 Nuevo pedido recibido</div>
      <div style="margin-top:10px;display:inline-block;background:rgba(255,255,255,0.15);border-radius:20px;padding:5px 16px;font-size:13px;color:#fff;font-weight:700;letter-spacing:1px;">{codigo}</div>
    </div>

    <!-- Info cliente -->
    <div style="padding:24px 32px 0;">
      <div style="font-size:11px;font-weight:700;letter-spacing:2px;text-transform:uppercase;color:#D63329;margin-bottom:12px;">Comprador</div>
      <table width="100%" cellpadding="0" cellspacing="0">
        <tr>
          <td style="padding:6px 0;font-size:13px;color:#999;width:120px;">Nombre</td>
          <td style="padding:6px 0;font-size:14px;color:#1a1a1a;font-weight:600;">{cliente}</td>
        </tr>
        <tr>
          <td style="padding:6px 0;font-size:13px;color:#999;">Teléfono</td>
          <td style="padding:6px 0;font-size:14px;color:#1a1a1a;">{telefono}</td>
        </tr>
        <tr>
          <td style="padding:6px 0;font-size:13px;color:#999;">Correo</td>
          <td style="padding:6px 0;font-size:14px;color:#1a1a1a;">{correo_cliente}</td>
        </tr>
        <tr>
          <td style="padding:6px 0;font-size:13px;color:#999;">Pago</td>
          <td style="padding:6px 0;font-size:14px;color:#1a1a1a;">{metodo_pago}</td>
        </tr>
        <tr>
          <td style="padding:6px 0;font-size:13px;color:#999;">Fecha</td>
          <td style="padding:6px 0;font-size:14px;color:#1a1a1a;">{fecha}</td>
        </tr>
        {'<tr><td style="padding:6px 0;font-size:13px;color:#999;">Notas</td><td style="padding:6px 0;font-size:14px;color:#555;font-style:italic;">' + notas + '</td></tr>' if notas else ''}
      </table>
    </div>

    <!-- Productos -->
    <div style="padding:20px 32px 0;">
      <div style="font-size:11px;font-weight:700;letter-spacing:2px;text-transform:uppercase;color:#D63329;margin-bottom:12px;">Detalle del pedido</div>
      <table width="100%" cellpadding="0" cellspacing="0" style="border:1px solid #f0f0f0;border-radius:10px;overflow:hidden;">
        <thead>
          <tr style="background:#fafafa;">
            <th style="padding:10px 12px;font-size:11px;color:#999;text-align:left;font-weight:700;letter-spacing:1px;text-transform:uppercase;">Producto</th>
            <th style="padding:10px 12px;font-size:11px;color:#999;text-align:center;font-weight:700;letter-spacing:1px;text-transform:uppercase;">Cant.</th>
            <th style="padding:10px 12px;font-size:11px;color:#999;text-align:right;font-weight:700;letter-spacing:1px;text-transform:uppercase;">Subtotal</th>
          </tr>
        </thead>
        <tbody>
          {filas_productos}
          {fila_descuento}
          {fila_envio}
          <tr style="background:#fff5f5;">
            <td colspan="2" style="padding:14px 12px;font-size:13px;color:#999;font-weight:700;letter-spacing:1px;text-transform:uppercase;">TOTAL</td>
            <td style="padding:14px 12px;font-size:20px;color:#D63329;font-weight:900;text-align:right;">{_fmt_cop(total)}</td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- CTAs -->
    <div style="padding:24px 32px;display:flex;gap:12px;flex-direction:column;">
      <a href="{link_pedidos}" style="display:block;text-align:center;background:linear-gradient(135deg,#D63329,#A8251C);color:#fff;text-decoration:none;padding:13px 24px;border-radius:10px;font-size:14px;font-weight:700;">
        📋 Ver en el panel de pedidos
      </a>
      <a href="{link_wa}" style="display:block;text-align:center;background:linear-gradient(135deg,#25D366,#128C7E);color:#fff;text-decoration:none;padding:13px 24px;border-radius:10px;font-size:14px;font-weight:700;">
        💬 Responder por WhatsApp
      </a>
    </div>

    <!-- Footer -->
    <div style="background:#f9f9f9;padding:16px 32px;text-align:center;border-top:1px solid #f0f0f0;">
      <div style="font-size:11px;color:#bbb;letter-spacing:1px;text-transform:uppercase;">TuKomercio · {nombre_negocio} · {fecha}</div>
    </div>

  </div>
</body>
</html>"""


def enviar_email_nuevo_pedido(pedido, negocio, comprador, productos_payload,
                               subtotal, descuento, costo_envio, total):
    """Fire-and-forget: envía email al tendero en background thread."""
    if not TIENE_EMAIL:
        return
    try:
        email_negocio = getattr(negocio, 'email', None) or getattr(negocio, 'correo', None)
        if not email_negocio:
            print(f"⚠️ Email: negocio {negocio.id_negocio} no tiene correo configurado")
            return
        nombre_negocio = getattr(negocio, 'nombre_negocio', None) or 'Tu negocio'
        html = _html_email_nuevo_pedido(
            pedido, negocio, comprador, productos_payload,
            subtotal, descuento, costo_envio, total
        )
        send_email_async(
            email_negocio,
            f"🛒 Nuevo pedido {pedido.codigo_pedido} — {nombre_negocio}",
            html
        )
        print(f"📧 Email en cola → {email_negocio}")
    except Exception as e:
        print(f"⚠️ Email nuevo pedido falló (no crítico): {e}")


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
        
        # ==========================================
        # ★ CUPÓN: calcular descuento antes del pedido
        # ==========================================
        descuento_aplicado = 0.0
        cupon_usado = None
        codigo_cupon = str(data.get('codigo_cupon', '') or '').strip().upper()

        if codigo_cupon and TIENE_CUPONES:
            try:
                cupon_obj = Cupon.query.filter_by(
                    negocio_id=negocio_id, codigo=codigo_cupon
                ).first()
                if cupon_obj:
                    subtotal_val = float(data.get('subtotal', 0))
                    valido, _ = cupon_obj.es_valido(subtotal_val)
                    if valido:
                        descuento_aplicado = cupon_obj.calcular_descuento(subtotal_val)
                        cupon_usado = cupon_obj
                        print(f"🎟️  Cupón '{codigo_cupon}' aplicado — descuento: ${descuento_aplicado:,.0f}")
            except Exception as cupon_err:
                print(f"⚠️ Error aplicando cupón (no crítico): {cupon_err}")

        subtotal_final = float(data.get('subtotal', 0))
        costo_envio_final = float(data.get('costo_envio', 0))
        total_final = max(0, subtotal_final - descuento_aplicado + costo_envio_final)

        # Crear pedido usando el método del modelo
        pedido = Pedido.crear_pedido(
            comprador=comprador,
            direccion=direccion,
            negocio_data=negocio_data,
            productos=productos,
            subtotal=subtotal_final,
            costo_envio=costo_envio_final,
            total=total_final,
            metodo_pago=data.get('metodo_pago', 'efectivo'),
            notas_cliente=data.get('notas'),
            metodo_contacto='whatsapp',
            origen='web'
        )

        # Guardar el descuento en el pedido
        if descuento_aplicado > 0:
            pedido.descuento = descuento_aplicado

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

            # ==========================================
            # ★ EMAIL AL TENDERO (fire-and-forget, post-commit)
            # ==========================================
            if TIENE_EMAIL:
                try:
                    negocio_obj = Negocio.query.get(negocio_id)
                    if negocio_obj:
                        enviar_email_nuevo_pedido(
                            pedido       = pedido,
                            negocio      = negocio_obj,
                            comprador    = comprador,
                            productos_payload = productos,
                            subtotal     = subtotal_final,
                            descuento    = descuento_aplicado,
                            costo_envio  = costo_envio_final,
                            total        = total_final
                        )
                except Exception as email_err:
                    print(f"⚠️ Email al tendero falló (no crítico): {email_err}")

            # Incrementar usos del cupón (post-commit, no crítico)
            if cupon_usado:
                try:
                    cupon_usado.usos_actuales = (cupon_usado.usos_actuales or 0) + 1
                    db.session.commit()
                    print(f"🎟️  Cupón '{cupon_usado.codigo}' — usos: {cupon_usado.usos_actuales}")
                except Exception as cu_err:
                    print(f"⚠️ No se pudo incrementar uso del cupón: {cu_err}")

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
                'subtotal': subtotal_final,
                'descuento': descuento_aplicado,
                'costo_envio': costo_envio_final,
                'total': total_final,
                'estado': pedido.estado,
                'fecha_creacion': pedido.fecha_pedido.isoformat()
            },
            'comprador': comprador.to_dict_checkout(),
            'notificacion_enviada': notificacion_creada,
            # ★ Info del cupón aplicado
            'cupon_aplicado': {
                'codigo': cupon_usado.codigo,
                'descuento': descuento_aplicado
            } if cupon_usado else None
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