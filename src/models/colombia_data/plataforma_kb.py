"""
Base de conocimiento de la plataforma (tabla "oculta") — TuKomercio.

Tabla flexible `plataforma_kb` donde se acumula TODA la información de la
plataforma de forma organizada: marca/visual, categorías de ayuda, catálogo
de funcionalidades y novedades (changelog). Es la fuente que luego alimentará
el **Centro de Ayuda**, las **Novedades** y la página de información técnica.

Diseño: una sola tabla flexible (campo `datos` JSONB) para empezar a llenar sin
comprometer el esquema final. `publicado=FALSE` por defecto → "oculta" hasta que
construyamos las vistas públicas.

`tipo`: visual | categoria | feature | articulo | changelog
Seed idempotente (ON CONFLICT (clave) DO NOTHING) + a prueba de fallos.

© 2024-2026 Carlos Eduardo Huérfano Bermúdez. Todos los derechos reservados.
"""
import json
import logging
from datetime import datetime
from src.models.database import db
from sqlalchemy.dialects.postgresql import JSONB

logger = logging.getLogger(__name__)


class PlataformaKB(db.Model):
    __tablename__ = 'plataforma_kb'
    id         = db.Column(db.Integer, primary_key=True)
    tipo       = db.Column(db.String(30), nullable=False, default='feature', index=True)
    area       = db.Column(db.String(60), index=True)
    clave      = db.Column(db.String(120), unique=True, nullable=False)
    titulo     = db.Column(db.String(200), nullable=False)
    resumen    = db.Column(db.Text)
    contenido  = db.Column(db.Text)
    datos      = db.Column(JSONB, default=dict)
    orden      = db.Column(db.Integer, default=0)
    publicado  = db.Column(db.Boolean, default=False, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id, 'tipo': self.tipo, 'area': self.area, 'clave': self.clave,
            'titulo': self.titulo, 'resumen': self.resumen, 'contenido': self.contenido,
            'datos': self.datos or {}, 'orden': self.orden, 'publicado': self.publicado,
        }


# ──────────────────────────────────────────────────────────────────────────
# SEED INICIAL — info de la plataforma (se irá ampliando sprint a sprint)
# ──────────────────────────────────────────────────────────────────────────
SEED_KB = [
    # ── MARCA / VISUAL ──────────────────────────────────────────────────
    {'tipo': 'visual', 'area': 'marca', 'clave': 'sistema-diseno', 'orden': 0,
     'titulo': 'Sistema de diseño TuKomercio',
     'resumen': 'Identidad visual oficial: logo, tipografías y paleta de color.',
     'datos': {
        'logo': '/assets/img/tuko-logo.gif',
        'tipografia': {'wordmark': 'Orbitron', 'titulos': 'Sora', 'texto': 'Plus Jakarta Sans'},
        'colores': {
            'indigo': '#4F46E5', 'indigo_dark': '#4338CA', 'violeta': '#7C3AED',
            'gradiente': ['#667eea', '#764ba2'], 'tinta': '#0F172A', 'slate': '#64748B',
            'indigo_soft': '#EEF2FF', 'ambar': '#F59E0B', 'whatsapp': '#25D366'},
     }},

    # ── CATEGORÍAS del Centro de Ayuda ──────────────────────────────────
    {'tipo': 'categoria', 'area': 'ayuda', 'clave': 'cat-primeros-pasos', 'titulo': 'Primeros pasos', 'resumen': 'Crea tu tienda y empieza a vender.', 'datos': {'icono': 'bi-rocket-takeoff-fill'}, 'orden': 1},
    {'tipo': 'categoria', 'area': 'ayuda', 'clave': 'cat-diseno', 'titulo': 'Diseña tu tienda', 'resumen': 'Logo, colores, portada y el Diseñador.', 'datos': {'icono': 'bi-palette-fill'}, 'orden': 2},
    {'tipo': 'categoria', 'area': 'ayuda', 'clave': 'cat-productos', 'titulo': 'Productos e inventario', 'resumen': 'Sube productos, controla stock y precios.', 'datos': {'icono': 'bi-box-seam-fill'}, 'orden': 3},
    {'tipo': 'categoria', 'area': 'ayuda', 'clave': 'cat-pedidos', 'titulo': 'Pedidos y envíos', 'resumen': 'Recibe pedidos, estados y fletes.', 'datos': {'icono': 'bi-bag-check-fill'}, 'orden': 4},
    {'tipo': 'categoria', 'area': 'ayuda', 'clave': 'cat-pagos', 'titulo': 'Pagos y cobros', 'resumen': 'Wompi, Nequi, contra entrega y más.', 'datos': {'icono': 'bi-credit-card-2-front-fill'}, 'orden': 5},
    {'tipo': 'categoria', 'area': 'ayuda', 'clave': 'cat-vender-mas', 'titulo': 'Vende más', 'resumen': 'WhatsApp, promociones y Dora IA.', 'datos': {'icono': 'bi-megaphone-fill'}, 'orden': 6},
    {'tipo': 'categoria', 'area': 'ayuda', 'clave': 'cat-premios', 'titulo': 'Premios y logros', 'resumen': 'Sube de nivel, gana insignias y TuKoins.', 'datos': {'icono': 'bi-trophy-fill'}, 'orden': 7},
    {'tipo': 'categoria', 'area': 'ayuda', 'clave': 'cat-cuenta', 'titulo': 'Mi cuenta y plan', 'resumen': 'Contraseña, datos, plan y facturación.', 'datos': {'icono': 'bi-gear-fill'}, 'orden': 8},

    # ── CATÁLOGO DE FUNCIONALIDADES (resumen; se ampliará) ──────────────
    {'tipo': 'feature', 'area': 'tienda', 'clave': 'f-crear-tienda', 'titulo': 'Crear tu tienda online', 'resumen': 'Wizard guiado: nombre, categoría, logo y URL pública lista para compartir.', 'datos': {'icono': '🏬'}, 'orden': 10},
    {'tipo': 'feature', 'area': 'tienda', 'clave': 'f-store-designer', 'titulo': 'Store Designer', 'resumen': 'Editor visual: logo, colores, tipografía, portada y secciones, con vista previa.', 'datos': {'icono': '🎨'}, 'orden': 11},
    {'tipo': 'feature', 'area': 'catalogo', 'clave': 'f-catalogo', 'titulo': 'Catálogo de productos', 'resumen': 'CRUD de productos con imágenes, precio, costo, stock y variantes.', 'datos': {'icono': '📦'}, 'orden': 12},
    {'tipo': 'feature', 'area': 'catalogo', 'clave': 'f-inventario', 'titulo': 'Inventario y stock', 'resumen': 'Control de stock en tiempo real, alertas de bajo stock y kardex auditable.', 'datos': {'icono': '📊'}, 'orden': 13},
    {'tipo': 'feature', 'area': 'catalogo', 'clave': 'f-carga-csv', 'titulo': 'Carga masiva CSV/Excel', 'resumen': 'Importa muchos productos de una vez desde un archivo.', 'datos': {'icono': '📄'}, 'orden': 14},
    {'tipo': 'feature', 'area': 'pedidos', 'clave': 'f-checkout', 'titulo': 'Checkout y envíos', 'resumen': 'Carrito, datos del comprador, transportadoras y fletes por ciudad.', 'datos': {'icono': '🛒'}, 'orden': 15},
    {'tipo': 'feature', 'area': 'pedidos', 'clave': 'f-gestion-pedidos', 'titulo': 'Gestión de pedidos', 'resumen': 'Listar, ver detalle, cambiar estados (incluido salto directo) y corregir.', 'datos': {'icono': '📋'}, 'orden': 16},
    {'tipo': 'feature', 'area': 'pedidos', 'clave': 'f-resumen-pedido', 'titulo': 'Resumen de pedido (Magic Link)', 'resumen': 'Enlace que el cliente ve para seguir su pedido; con preview en WhatsApp.', 'datos': {'icono': '🔗'}, 'orden': 17},
    {'tipo': 'feature', 'area': 'pedidos', 'clave': 'f-crm', 'titulo': 'CRM de compradores', 'resumen': 'Clientes, historial de pedidos y Magic Links sin contraseña.', 'datos': {'icono': '👥'}, 'orden': 18},
    {'tipo': 'feature', 'area': 'finanzas', 'clave': 'f-contabilidad', 'titulo': 'Contabilidad', 'resumen': 'Ventas, compras, gastos, ingresos y balance del negocio.', 'datos': {'icono': '💰'}, 'orden': 19},
    {'tipo': 'feature', 'area': 'finanzas', 'clave': 'f-reportes', 'titulo': 'Reportes y facturación', 'resumen': 'Reportes por período, exportación y facturas con consecutivo.', 'datos': {'icono': '🧾'}, 'orden': 20},
    {'tipo': 'feature', 'area': 'pagos', 'clave': 'f-wompi', 'titulo': 'Pagos en línea (Wompi)', 'resumen': 'Cobra con tarjeta/PSE; cada negocio configura sus llaves.', 'datos': {'icono': '💳'}, 'orden': 21},
    {'tipo': 'feature', 'area': 'pagos', 'clave': 'f-cupones', 'titulo': 'Cupones de descuento', 'resumen': 'Crea cupones y el checkout los valida.', 'datos': {'icono': '🎟️'}, 'orden': 22},
    {'tipo': 'feature', 'area': 'notificaciones', 'clave': 'f-campanita', 'titulo': 'Campanita de notificaciones', 'resumen': 'Avisos en tiempo real: nuevos pedidos, pagos, stock bajo y más.', 'datos': {'icono': '🔔'}, 'orden': 23},
    {'tipo': 'feature', 'area': 'notificaciones', 'clave': 'f-web-push', 'titulo': 'Notificaciones push', 'resumen': 'Recibe avisos aunque tengas la app cerrada (escritorio y celular).', 'datos': {'icono': '📲'}, 'orden': 24},
    {'tipo': 'feature', 'area': 'ia', 'clave': 'f-dora-ia', 'titulo': 'Dora IA', 'resumen': 'Asistente que describe productos, genera promos, analiza ventas y más.', 'datos': {'icono': '✨'}, 'orden': 25},
    {'tipo': 'feature', 'area': 'gamificacion', 'clave': 'f-gamificacion', 'titulo': 'Gamificación', 'resumen': 'XP, 30 niveles, rachas, misiones, ligas, retos y duelos.', 'datos': {'icono': '🏆'}, 'orden': 26},
    {'tipo': 'feature', 'area': 'gamificacion', 'clave': 'f-insignias', 'titulo': 'Insignias (49 badges)', 'resumen': 'Logros automáticos con 5 niveles, visibles en tu perfil público.', 'datos': {'icono': '🥇'}, 'orden': 27},
    {'tipo': 'feature', 'area': 'gamificacion', 'clave': 'f-tukoins', 'titulo': 'TuKoins y tienda de premios', 'resumen': 'Moneda virtual que ganas y canjeas por recompensas.', 'datos': {'icono': '🪙'}, 'orden': 28},
    {'tipo': 'feature', 'area': 'marketing', 'clave': 'f-qr', 'titulo': 'Códigos QR', 'resumen': 'QR de tu tienda y perfil para imprimir y compartir.', 'datos': {'icono': '🔳'}, 'orden': 29},
    {'tipo': 'feature', 'area': 'marketing', 'clave': 'f-preview-whatsapp', 'titulo': 'Vista previa al compartir', 'resumen': 'Tus enlaces de tienda/producto/pedido salen con foto en WhatsApp.', 'datos': {'icono': '🟢'}, 'orden': 30},
    {'tipo': 'feature', 'area': 'verticales', 'clave': 'f-verticales', 'titulo': 'Verticales: Taller, Restaurante, MecaLink', 'resumen': 'Módulos especializados por tipo de negocio.', 'datos': {'icono': '🧰'}, 'orden': 31},
    {'tipo': 'feature', 'area': 'admin', 'clave': 'f-panel-admin', 'titulo': 'Panel de administración', 'resumen': 'Suite para administrar toda la plataforma sin tocar código (51 módulos).', 'datos': {'icono': '🛠️'}, 'orden': 32},

    # ── NOVEDADES / CHANGELOG (curado, lenguaje de tendero) ─────────────
    {'tipo': 'changelog', 'area': 'novedades', 'clave': 'cl-2026-06-preview-whatsapp', 'titulo': 'Tus enlaces ahora se ven con foto en WhatsApp', 'resumen': 'Al compartir un producto o el resumen de un pedido, aparece la imagen de tu tienda.', 'datos': {'tipo': 'nuevo', 'fecha': '2026-06', 'version': '2.21'}, 'orden': 1},
    {'tipo': 'changelog', 'area': 'novedades', 'clave': 'cl-2026-06-push', 'titulo': 'Notificaciones automáticas y push', 'resumen': 'Te avisamos de pedidos, planes e insignias, incluso con la app cerrada.', 'datos': {'tipo': 'nuevo', 'fecha': '2026-06', 'version': '2.21'}, 'orden': 2},
    {'tipo': 'changelog', 'area': 'novedades', 'clave': 'cl-2026-06-estados', 'titulo': 'Marca pedidos como entregado en un clic', 'resumen': 'Ahora puedes saltar directo a cualquier estado del pedido, con confirmación.', 'datos': {'tipo': 'mejora', 'fecha': '2026-06', 'version': '2.21'}, 'orden': 3},
    {'tipo': 'changelog', 'area': 'novedades', 'clave': 'cl-2026-06-carga-tienda', 'titulo': 'Tu tienda carga con tu logo', 'resumen': 'Pantalla de carga más rápida y con la identidad de tu negocio.', 'datos': {'tipo': 'mejora', 'fecha': '2026-06', 'version': '2.21'}, 'orden': 4},
    {'tipo': 'changelog', 'area': 'novedades', 'clave': 'cl-2026-06-img-compartir', 'titulo': 'Elige tu imagen para compartir', 'resumen': 'Desde el Diseñador eliges la imagen que aparece al compartir tus enlaces.', 'datos': {'tipo': 'nuevo', 'fecha': '2026-06', 'version': '2.21'}, 'orden': 5},
    {'tipo': 'changelog', 'area': 'novedades', 'clave': 'cl-2026-06-panel', 'titulo': 'Panel de administración completo', 'resumen': 'Administra toda la plataforma sin tocar código.', 'datos': {'tipo': 'nuevo', 'fecha': '2026-06', 'version': '2.20'}, 'orden': 6},

    # ── GUÍAS (artículos) — Fase 2, contenido inicial ───────────────────
    {'tipo': 'articulo', 'area': 'tienda', 'clave': 'guia-crear-tienda', 'publicado': True, 'orden': 1,
     'titulo': '¿Cómo creo mi tienda online?', 'resumen': 'En pocos minutos tienes tu tienda lista para vender.',
     'datos': {'categoria': 'cat-primeros-pasos', 'icono': '🚀'},
     'contenido': ('Crear tu tienda en TuKomercio es muy rápido:\n\n'
                   '1. Inicia sesión y entra a "Mis Negocios".\n'
                   '2. Toca "Crear emprendimiento" y escribe el nombre de tu negocio, la categoría y tu ciudad.\n'
                   '3. Sube tu logo (opcional, pero se ve más profesional).\n'
                   '4. Guarda. ¡Listo! TuKomercio te genera automáticamente la dirección de tu tienda y un código QR.\n\n'
                   'Después puedes personalizar colores, portada y más desde el Diseñador. '
                   'Tu tienda queda en una dirección tipo tukomercio.co/tienda/tu-negocio para compartir por WhatsApp.')},
    {'tipo': 'articulo', 'area': 'negocio', 'clave': 'guia-configurar-negocio', 'publicado': True, 'orden': 2,
     'titulo': 'Configura los datos de tu negocio', 'resumen': 'Nombre, WhatsApp, logo y envíos: lo básico para vender bien.',
     'datos': {'categoria': 'cat-primeros-pasos', 'icono': '⚙️'},
     'contenido': ('Para que tu tienda inspire confianza y los pedidos lleguen bien, completa:\n\n'
                   '• Nombre y descripción del negocio.\n'
                   '• Número de WhatsApp (por ahí te escriben y confirmas pedidos).\n'
                   '• Logo de tu marca.\n'
                   '• Configuración de envíos: define desde qué monto el envío es gratis y las tarifas por ciudad.\n\n'
                   'Todo esto se edita desde el panel de tu negocio y se refleja al instante en tu tienda pública.')},
    {'tipo': 'articulo', 'area': 'marketing', 'clave': 'guia-publicar-compartir', 'publicado': True, 'orden': 3,
     'titulo': 'Publica y comparte tu tienda', 'resumen': 'Lleva tu tienda a tus clientes por WhatsApp y redes.',
     'datos': {'categoria': 'cat-primeros-pasos', 'icono': '📣'},
     'contenido': ('Cuando tu tienda esté lista:\n\n'
                   '1. Copia el enlace de tu tienda (lo ves en "Mi Página Web") o usa el código QR.\n'
                   '2. Compártelo por WhatsApp, Instagram o Facebook. Al pegarlo, aparece con tu logo y nombre.\n'
                   '3. Imprime el QR y pégalo en tu local o en tus empaques.\n\n'
                   'Cada producto y cada pedido también tienen su propio enlace para compartir, ¡y salen con foto!')},
    {'tipo': 'articulo', 'area': 'tienda', 'clave': 'guia-usar-designer', 'publicado': True, 'orden': 1,
     'titulo': 'Personaliza tu tienda con el Diseñador', 'resumen': 'Colores, logo, portada y tipografía a tu gusto.',
     'datos': {'categoria': 'cat-diseno', 'icono': '🎨'},
     'contenido': ('El Diseñador te deja dejar tu tienda con la cara de tu marca:\n\n'
                   '• Logo: súbelo y elige su forma y tamaño.\n'
                   '• Colores: define el color principal de tu tienda.\n'
                   '• Portada (banner) y secciones visibles.\n'
                   '• Imagen para enlaces compartidos: la que sale en WhatsApp al compartir.\n\n'
                   'Los cambios se ven en la vista previa. Recuerda Guardar y recargar tu tienda para verlos publicados.')},
    {'tipo': 'articulo', 'area': 'catalogo', 'clave': 'guia-subir-productos', 'publicado': True, 'orden': 1,
     'titulo': '¿Cómo subo mis productos?', 'resumen': 'Agrega productos con foto, precio y stock.',
     'datos': {'categoria': 'cat-productos', 'icono': '📦'},
     'contenido': ('Para llenar tu catálogo:\n\n'
                   '1. Entra a "Inventario" o "Mi Catálogo".\n'
                   '2. Toca "Agregar producto" y escribe nombre, precio, costo y stock.\n'
                   '3. Sube hasta 5 fotos (la primera es la principal). Las fotos pesadas se optimizan solas.\n'
                   '4. Elige o crea una categoría para organizarlo.\n'
                   '5. Guarda. Tu producto aparece de inmediato en tu tienda.\n\n'
                   '¿Tienes muchos productos? Usa la carga masiva por CSV/Excel para subirlos todos de una vez.')},
    {'tipo': 'articulo', 'area': 'pedidos', 'clave': 'guia-recibir-pedidos', 'publicado': True, 'orden': 1,
     'titulo': 'Recibe y gestiona tus pedidos', 'resumen': 'Del pedido nuevo hasta "entregado", paso a paso.',
     'datos': {'categoria': 'cat-pedidos', 'icono': '🛒'},
     'contenido': ('Cuando un cliente compra, te llega una notificación en la campanita. Luego:\n\n'
                   '1. Abre "Pedidos", toca el pedido para ver qué pidió y los datos de envío.\n'
                   '2. Confírmalo (descuenta stock automáticamente).\n'
                   '3. Avanza el estado: Preparando → Enviado → Entregado. Puedes saltar directo a un estado con confirmación.\n'
                   '4. Al marcar "Enviado", TuKomercio te arma un mensaje de WhatsApp listo para avisarle al cliente con la guía.\n\n'
                   'El cliente puede seguir su pedido con el enlace de resumen que le compartes.')},

    # ── Diseño (más) ────────────────────────────────────────────────────
    {'tipo': 'articulo', 'area': 'tienda', 'clave': 'guia-imagen-compartir', 'publicado': True, 'orden': 2,
     'titulo': 'Elige la imagen que sale al compartir', 'resumen': 'La foto que aparece en WhatsApp al compartir tu tienda o un pedido.',
     'datos': {'categoria': 'cat-diseno', 'icono': '🖼️'},
     'contenido': ('En el Diseñador → sección "SEO & Posicionamiento" → "Imagen para enlaces compartidos":\n\n'
                   '1. Sube una imagen (ideal 1200×630 px).\n2. Guarda.\n\n'
                   'Esa imagen aparecerá cuando compartas tu tienda o el resumen de un pedido por WhatsApp/Facebook. '
                   'Si no eliges una, se usa tu portada o tu logo. Ojo: WhatsApp recuerda los enlaces, así que prueba con uno nuevo para ver el cambio.')},

    # ── Productos (más) ─────────────────────────────────────────────────
    {'tipo': 'articulo', 'area': 'catalogo', 'clave': 'guia-fotos-variantes', 'publicado': True, 'orden': 2,
     'titulo': 'Fotos y variantes de producto', 'resumen': 'Buenas fotos y opciones como talla o color.',
     'datos': {'categoria': 'cat-productos', 'icono': '📸'},
     'contenido': ('Fotos: sube hasta 5 por producto; la primera es la principal. Usa fondo limpio y buena luz. '
                   'No te preocupes por el peso: TuKomercio las optimiza.\n\n'
                   'Variantes: si tu producto viene en tallas, colores o materiales, agrégalas. El comprador elige su combinación antes de añadir al carrito.')},
    {'tipo': 'articulo', 'area': 'catalogo', 'clave': 'guia-stock-precios', 'publicado': True, 'orden': 3,
     'titulo': 'Controla stock y precios', 'resumen': 'Mantén tu inventario al día y evita vender lo agotado.',
     'datos': {'categoria': 'cat-productos', 'icono': '📊'},
     'contenido': ('En "Inventario" ves el stock de todo en tiempo real, con alertas de stock bajo (amarillo) y agotado (rojo). '
                   'Puedes ajustar el stock a mano o dejar que se descuente solo con cada venta/pedido. '
                   'Define precio de venta y precio de costo para ver tu margen real en los reportes.')},
    {'tipo': 'articulo', 'area': 'catalogo', 'clave': 'guia-carga-masiva', 'publicado': True, 'orden': 4,
     'titulo': 'Sube muchos productos de una vez (CSV)', 'resumen': 'Importa tu catálogo completo desde Excel/CSV.',
     'datos': {'categoria': 'cat-productos', 'icono': '📄'},
     'contenido': ('Si tienes muchos productos, usa la carga masiva:\n\n'
                   '1. Entra a "Carga masiva" en el módulo de inventario.\n'
                   '2. Sube tu archivo CSV o Excel con columnas: nombre, precio, stock, SKU, costo y categoría.\n'
                   '3. Revisa el reporte: te dice cuántos se crearon y si alguno tuvo error.\n\n'
                   'Ideal para arrancar rápido sin cargar producto por producto.')},

    # ── Pedidos (más) ───────────────────────────────────────────────────
    {'tipo': 'articulo', 'area': 'pedidos', 'clave': 'guia-envios-fletes', 'publicado': True, 'orden': 2,
     'titulo': 'Configura envíos y fletes', 'resumen': 'Define transportadoras, tarifas y envío gratis.',
     'datos': {'categoria': 'cat-pedidos', 'icono': '🚚'},
     'contenido': ('En la configuración de envíos de tu negocio puedes:\n\n'
                   '• Definir desde qué monto el envío es GRATIS.\n'
                   '• Poner tarifas por ciudad y transportadora (Servientrega, Coordinadora, Interrapidísimo, etc.).\n'
                   '• Ofrecer "Recoger en tienda".\n\n'
                   'Si una ciudad no tiene tarifa, el checkout muestra "A confirmar con el vendedor" para no frenar la venta. '
                   'Cuando ajustas un flete a mano, TuKomercio te ofrece guardarlo para la próxima.')},
    {'tipo': 'articulo', 'area': 'pedidos', 'clave': 'guia-devoluciones', 'publicado': True, 'orden': 3,
     'titulo': 'Devoluciones', 'resumen': 'Cómo registrar una devolución y reponer stock.',
     'datos': {'categoria': 'cat-pedidos', 'icono': '↩️'},
     'contenido': ('Si un cliente devuelve un producto, regístralo desde el pedido (o como devolución libre si no hay pedido). '
                   'El stock vuelve a tu inventario automáticamente y queda el motivo en el historial para tu control.')},

    # ── Pagos ───────────────────────────────────────────────────────────
    {'tipo': 'articulo', 'area': 'pagos', 'clave': 'guia-wompi', 'publicado': True, 'orden': 1,
     'titulo': 'Cobra en línea con Wompi', 'resumen': 'Recibe pagos con tarjeta y PSE en tu tienda.',
     'datos': {'categoria': 'cat-pagos', 'icono': '💳'},
     'contenido': ('Para cobrar en línea conecta tu cuenta de Wompi:\n\n'
                   '1. Crea tu cuenta en Wompi y obtén tus llaves (pública y privada).\n'
                   '2. En tu panel, sección de pagos, pega tus llaves.\n'
                   '3. ¡Listo! En el checkout el cliente podrá pagar con tarjeta o PSE, y el pedido se confirma solo cuando el pago llega.')},
    {'tipo': 'articulo', 'area': 'pagos', 'clave': 'guia-cupones', 'publicado': True, 'orden': 2,
     'titulo': 'Crea cupones de descuento', 'resumen': 'Premia a tus clientes con códigos de descuento.',
     'datos': {'categoria': 'cat-pagos', 'icono': '🎟️'},
     'contenido': ('Crea cupones desde tu panel (monto o porcentaje de descuento). El cliente escribe el código en el carrito '
                   'y el checkout aplica el descuento automáticamente. Útil para promociones y para recuperar clientes.')},
    {'tipo': 'articulo', 'area': 'pagos', 'clave': 'guia-metodos-pago', 'publicado': True, 'orden': 3,
     'titulo': 'Métodos de pago disponibles', 'resumen': 'Efectivo, Nequi, transferencia, tarjeta y más.',
     'datos': {'categoria': 'cat-pagos', 'icono': '💵'},
     'contenido': ('Tu tienda soporta varios métodos: efectivo contra entrega, Nequi, Daviplata, transferencia bancaria, '
                   'tarjeta débito/crédito y PSE (estos últimos con Wompi). El cliente elige al hacer el checkout.')},

    # ── Vender más ──────────────────────────────────────────────────────
    {'tipo': 'articulo', 'area': 'marketing', 'clave': 'guia-whatsapp', 'publicado': True, 'orden': 1,
     'titulo': 'Vende por WhatsApp', 'resumen': 'El canal favorito de tus clientes, integrado.',
     'datos': {'categoria': 'cat-vender-mas', 'icono': '💬'},
     'contenido': ('TuKomercio vive conectado a WhatsApp:\n\n'
                   '• Botón de WhatsApp en tu tienda para que te escriban.\n'
                   '• Al enviar un pedido, mensaje listo para avisarle al cliente con la guía.\n'
                   '• Comparte tu tienda, productos y pedidos por WhatsApp (¡salen con foto!).')},
    {'tipo': 'articulo', 'area': 'ia', 'clave': 'guia-dora-ia', 'publicado': True, 'orden': 2,
     'titulo': 'Usa a Dora IA', 'resumen': 'Tu asistente: describe productos, crea promos y analiza ventas.',
     'datos': {'categoria': 'cat-vender-mas', 'icono': '✨'},
     'contenido': ('Dora es tu asistente con inteligencia artificial. Puede:\n\n'
                   '• Escribir la descripción de un producto por ti.\n'
                   '• Generar textos de promoción para WhatsApp/Instagram.\n'
                   '• Analizar tus ventas y darte ideas.\n'
                   '• Sugerir un precio de venta.\n\n'
                   'La encuentras dentro de tu panel. (Disponible según tu plan.)')},
    {'tipo': 'articulo', 'area': 'marketing', 'clave': 'guia-qr', 'publicado': True, 'orden': 3,
     'titulo': 'Tu código QR', 'resumen': 'Lleva clientes a tu tienda desde el mundo físico.',
     'datos': {'categoria': 'cat-vender-mas', 'icono': '🔳'},
     'contenido': ('TuKomercio genera un código QR de tu tienda. Descárgalo e imprímelo en tu local, tarjetas, volantes o empaques. '
                   'Quien lo escanee llega directo a tu tienda online.')},

    # ── Premios y logros ────────────────────────────────────────────────
    {'tipo': 'articulo', 'area': 'gamificacion', 'clave': 'guia-niveles-xp', 'publicado': True, 'orden': 1,
     'titulo': 'Niveles, XP y misiones', 'resumen': 'Gana experiencia usando la plataforma y sube de nivel.',
     'datos': {'categoria': 'cat-premios', 'icono': '⭐'},
     'contenido': ('Cada acción en tu negocio (vender, subir productos, entrar a diario) te da XP y te sube de nivel '
                   '(de Semilla a Leyenda). Completa misiones diarias, semanales y mensuales para ganar más XP y TuKoins. '
                   'Todo aparece en tu Dashboard de gamificación.')},
    {'tipo': 'articulo', 'area': 'gamificacion', 'clave': 'guia-insignias-tukoins', 'publicado': True, 'orden': 2,
     'titulo': 'Insignias y TuKoins', 'resumen': 'Logros para tu perfil y una moneda para canjear premios.',
     'datos': {'categoria': 'cat-premios', 'icono': '🥇'},
     'contenido': ('Insignias: las ganas automáticamente al lograr metas (ventas, antigüedad, calificaciones…) y se muestran '
                   'en tu perfil público como sello de confianza.\n\n'
                   'TuKoins: la moneda que ganas con misiones y ventas. Cánjeala en la tienda de premios por plantillas, '
                   'destacados y más.')},

    # ── Cuenta y plan ───────────────────────────────────────────────────
    {'tipo': 'articulo', 'area': 'cuenta', 'clave': 'guia-contrasena', 'publicado': True, 'orden': 1,
     'titulo': 'Cambiar o recuperar tu contraseña', 'resumen': 'Recupera el acceso a tu cuenta.',
     'datos': {'categoria': 'cat-cuenta', 'icono': '🔒'},
     'contenido': ('¿Olvidaste tu contraseña? En la pantalla de inicio de sesión toca "¿Olvidaste tu contraseña?", '
                   'escribe tu correo y te llega un enlace para crear una nueva (revisa también spam). '
                   'Desde tu perfil también puedes actualizar tus datos.')},
    {'tipo': 'articulo', 'area': 'planes', 'clave': 'guia-plan', 'publicado': True, 'orden': 2,
     'titulo': 'Tu plan y qué incluye', 'resumen': 'Básico, Pro, Premium y Deluxe.',
     'datos': {'categoria': 'cat-cuenta', 'icono': '💎'},
     'contenido': ('TuKomercio tiene varios planes que desbloquean más funciones: Básico, Pro, Premium y Deluxe '
                   '(más productos, dropshipping, IA, personalización avanzada, etc.). '
                   'Puedes ver y cambiar tu plan desde tu panel.')},

    # ── Fase 2 (2ª tanda) — completar categorías ────────────────────────
    {'tipo': 'articulo', 'area': 'tienda', 'clave': 'guia-instalar-app', 'publicado': True, 'orden': 4,
     'titulo': 'Instala TuKomercio como app', 'resumen': 'Ten tu tienda a un toque en el celular.',
     'datos': {'categoria': 'cat-primeros-pasos'},
     'contenido': ('TuKomercio funciona como app (PWA). En el celular, abre tu panel en el navegador y toca '
                   '"Agregar a pantalla de inicio" (Android) o el botón Compartir → "Agregar a inicio" (iPhone). '
                   'Así entras de un toque, como cualquier app.')},
    {'tipo': 'articulo', 'area': 'tienda', 'clave': 'guia-colores-marca', 'publicado': True, 'orden': 3,
     'titulo': 'Colores y tipografía de tu tienda', 'resumen': 'Dale la cara de tu marca.',
     'datos': {'categoria': 'cat-diseno'},
     'contenido': ('En el Diseñador eliges el color principal de tu tienda y la tipografía. Usa colores que '
                   'representen tu marca y que contrasten bien para que se lea fácil. La vista previa te muestra '
                   'cómo va quedando antes de guardar.')},
    {'tipo': 'articulo', 'area': 'tienda', 'clave': 'guia-portada-banner', 'publicado': True, 'orden': 4,
     'titulo': 'Portada y banner de bienvenida', 'resumen': 'Lo primero que ve tu cliente.',
     'datos': {'categoria': 'cat-diseno'},
     'contenido': ('Sube una portada/banner atractivo con tu mejor producto o una frase corta. Es lo primero '
                   'que ve quien entra a tu tienda, así que que cuente quién eres y qué vendes.')},
    {'tipo': 'articulo', 'area': 'tienda', 'clave': 'guia-plantillas', 'publicado': True, 'orden': 5,
     'titulo': 'Elige tu plantilla', 'resumen': 'Distintos estilos según tu negocio.',
     'datos': {'categoria': 'cat-diseno'},
     'contenido': ('TuKomercio tiene varias plantillas (catálogo, estilos para distintos rubros, etc.). '
                   'Elige la que mejor le quede a tu negocio desde "Mi Página Web" / el Diseñador. '
                   'Puedes cambiarla cuando quieras sin perder tus productos.')},
    {'tipo': 'articulo', 'area': 'catalogo', 'clave': 'guia-categorias', 'publicado': True, 'orden': 5,
     'titulo': 'Organiza con categorías', 'resumen': 'Que tu cliente encuentre rápido.',
     'datos': {'categoria': 'cat-productos'},
     'contenido': ('Crea categorías (ej. "Ropa", "Accesorios", "Ofertas") y asigna tus productos. '
                   'Las categorías aparecen como filtros en tu tienda y ayudan a que el cliente encuentre lo que busca.')},
    {'tipo': 'articulo', 'area': 'catalogo', 'clave': 'guia-dropshipping', 'publicado': True, 'orden': 6,
     'titulo': 'Dropshipping: importa catálogos', 'resumen': 'Vende sin tener el inventario en casa.',
     'datos': {'categoria': 'cat-productos'},
     'contenido': ('Si trabajas con proveedores (Mastershop, Dropi o CSV), puedes importar sus catálogos y aplicar '
                   'un margen automático. Luego sincronizas precios y stock. (Disponible según tu plan.)')},
    {'tipo': 'articulo', 'area': 'pedidos', 'clave': 'guia-corregir-pedido', 'publicado': True, 'orden': 4,
     'titulo': 'Corrige un pedido', 'resumen': 'Cuando el cliente pide cambiar algo.',
     'datos': {'categoria': 'cat-pedidos'},
     'contenido': ('¿El cliente llamó a cambiar algo? Desde el pedido puedes editar productos, total, datos de '
                   'envío, agregar la guía/transportadora y notas internas. Todo queda registrado.')},
    {'tipo': 'articulo', 'area': 'pedidos', 'clave': 'guia-aprobar-campanita', 'publicado': True, 'orden': 5,
     'titulo': 'Aprueba pedidos desde la campanita', 'resumen': 'Confirma sin salir del panel.',
     'datos': {'categoria': 'cat-pedidos'},
     'contenido': ('Cuando llega un pedido, desde la campanita puedes aprobarlo (crea la venta y descuenta stock) '
                   'o rechazarlo con un motivo. Rápido, sin entrar al módulo de pedidos.')},
    {'tipo': 'articulo', 'area': 'pedidos', 'clave': 'guia-clientes-magic', 'publicado': True, 'orden': 6,
     'titulo': 'Tus clientes (CRM y Magic Link)', 'resumen': 'Conoce y fideliza a quien te compra.',
     'datos': {'categoria': 'cat-pedidos'},
     'contenido': ('En el CRM ves tus clientes y su historial de compras. Con los "Magic Links" tu cliente puede '
                   'ver sus pedidos sin crear cuenta ni contraseña. Ideal para dar buen servicio y que vuelvan.')},
    {'tipo': 'articulo', 'area': 'marketing', 'clave': 'guia-resenas', 'publicado': True, 'orden': 4,
     'titulo': 'Reseñas de productos', 'resumen': 'La opinión de tus clientes vende por ti.',
     'datos': {'categoria': 'cat-vender-mas'},
     'contenido': ('Tus compradores pueden dejar reseñas con estrellas en tus productos. Tú las moderas '
                   '(aprobar/ocultar). Las buenas reseñas dan confianza y ayudan a vender más.')},
    {'tipo': 'articulo', 'area': 'marketing', 'clave': 'guia-feed-videos', 'publicado': True, 'orden': 5,
     'titulo': 'Muéstrate en el Feed de videos', 'resumen': 'Tipo Reels, para que te descubran.',
     'datos': {'categoria': 'cat-vender-mas'},
     'contenido': ('Sube videos cortos de tus productos o tu negocio. Aparecen en el feed público de TuKomercio '
                   '(estilo Reels) y en tu perfil, para que más gente te descubra.')},
    {'tipo': 'articulo', 'area': 'gamificacion', 'clave': 'guia-ligas-retos', 'publicado': True, 'orden': 3,
     'titulo': 'Ligas, retos y duelos', 'resumen': 'Compite y motívate vendiendo.',
     'datos': {'categoria': 'cat-premios'},
     'contenido': ('Compite en ligas con negocios parecidos al tuyo, participa en el reto del mes y rétate en '
                   'duelos 1v1. Es una forma divertida de motivarte a vender más, con recompensas.')},
    {'tipo': 'articulo', 'area': 'gamificacion', 'clave': 'guia-referidos', 'publicado': True, 'orden': 4,
     'titulo': 'Invita y gana (referidos)', 'resumen': 'Trae otros tenderos y gana recompensas.',
     'datos': {'categoria': 'cat-premios'},
     'contenido': ('Tienes un código/enlace de referido. Cuando alguien que invitaste hace su primera venta, '
                   'ganas XP y TuKoins automáticamente. Comparte tu enlace con otros tenderos.')},
    {'tipo': 'articulo', 'area': 'cuenta', 'clave': 'guia-perfil', 'publicado': True, 'orden': 3,
     'titulo': 'Tu perfil y datos', 'resumen': 'Mantén tu información al día.',
     'datos': {'categoria': 'cat-cuenta'},
     'contenido': ('Desde tu perfil actualizas tu nombre, ciudad, foto y datos de contacto. Mantenerlos al día '
                   'ayuda a que tus clientes confíen y a que el soporte te atienda mejor.')},
    {'tipo': 'articulo', 'area': 'negocio', 'clave': 'guia-sucursales', 'publicado': True, 'orden': 4,
     'titulo': 'Maneja varias sucursales', 'resumen': '¿Más de un local? Contrólalos por separado.',
     'datos': {'categoria': 'cat-cuenta'},
     'contenido': ('Si tienes varios locales, crea sucursales: cada una con su dirección, teléfono e inventario. '
                   'Así llevas las ventas y el stock de cada punto por separado. (Según tu plan.)')},

    # ── Fase 2 (4ª tanda) — cierre de contenido (~45 guías) ──────────────
    {'tipo': 'articulo', 'area': 'negocio', 'clave': 'guia-tu-panel', 'publicado': True, 'orden': 5,
     'titulo': 'Conoce tu panel', 'resumen': 'El tablero desde donde controlas todo.',
     'datos': {'categoria': 'cat-primeros-pasos'},
     'contenido': ('Tu panel es el centro de tu negocio: ves ventas del día, pedidos pendientes, stock bajo, '
                   'tu nivel y misiones. Desde el menú llegas a Inventario, Pedidos, Diseñador, Reportes y más. '
                   'Dale un vistazo cada mañana para no perderte nada.')},
    {'tipo': 'articulo', 'area': 'negocio', 'clave': 'guia-verificar-negocio', 'publicado': True, 'orden': 6,
     'titulo': 'Consigue el sello Verificado', 'resumen': 'Más confianza = más ventas.',
     'datos': {'categoria': 'cat-primeros-pasos'},
     'contenido': ('El sello ✓ Verificado le dice a tus clientes que tu negocio es real y confiable. '
                   'Completa los datos de tu negocio, mantén buenas calificaciones y cumple con tus pedidos. '
                   'Aparece en tu tienda y en la franja de confianza.')},
    {'tipo': 'articulo', 'area': 'pedidos', 'clave': 'guia-avisar-cliente', 'publicado': True, 'orden': 7,
     'titulo': 'Avísale al cliente por WhatsApp', 'resumen': 'Mensaje listo con la guía de envío.',
     'datos': {'categoria': 'cat-pedidos'},
     'contenido': ('Al marcar un pedido como "Enviado", TuKomercio arma un mensaje de WhatsApp con el resumen y la '
                   'guía de la transportadora. Solo revisas y envías. El cliente queda informado y tranquilo, y '
                   'puede seguir su pedido con el enlace.')},
    {'tipo': 'articulo', 'area': 'pagos', 'clave': 'guia-contraentrega', 'publicado': True, 'orden': 4,
     'titulo': 'Pago contra entrega', 'resumen': 'Cobra al entregar, sin complicaciones.',
     'datos': {'categoria': 'cat-pagos'},
     'contenido': ('El contra entrega es el favorito en Colombia: el cliente paga cuando recibe. Actívalo como '
                   'método de pago en tu tienda. Consejo: confirma el pedido por WhatsApp antes de despachar para '
                   'evitar devoluciones.')},
    {'tipo': 'articulo', 'area': 'marketing', 'clave': 'guia-compartir-producto', 'publicado': True, 'orden': 6,
     'titulo': 'Comparte un producto con foto', 'resumen': 'Su enlace se ve con imagen en WhatsApp.',
     'datos': {'categoria': 'cat-vender-mas'},
     'contenido': ('Cada producto tiene su propio enlace. Cópialo y compártelo: en WhatsApp aparece con la foto, el '
                   'nombre y el precio. Ideal para responder "¿cuánto vale?" con un solo mensaje que vende.')},
    {'tipo': 'articulo', 'area': 'marketing', 'clave': 'guia-promociones', 'publicado': True, 'orden': 7,
     'titulo': 'Crea ofertas y promociones', 'resumen': 'Atrae clientes con descuentos.',
     'datos': {'categoria': 'cat-vender-mas'},
     'contenido': ('Pon precios de oferta a tus productos, crea cupones de descuento y arma combos. Comunícalo en '
                   'tus estados de WhatsApp y redes. Las promociones por tiempo limitado crean urgencia y venden.')},
    {'tipo': 'articulo', 'area': 'gamificacion', 'clave': 'guia-tienda-premios', 'publicado': True, 'orden': 5,
     'titulo': 'Canjea tus TuKoins', 'resumen': 'Gasta lo que ganas en la tienda de premios.',
     'datos': {'categoria': 'cat-premios'},
     'contenido': ('En la tienda de premios canjeas tus TuKoins por beneficios: plantillas, destacar tu tienda, '
                   'personalizaciones y más. Entre más usas TuKomercio y más vendes, más TuKoins acumulas.')},
    {'tipo': 'articulo', 'area': 'cuenta', 'clave': 'guia-soporte', 'publicado': True, 'orden': 5,
     'titulo': '¿Necesitas ayuda? Contáctanos', 'resumen': 'Estamos para ayudarte a vender más.',
     'datos': {'categoria': 'cat-cuenta'},
     'contenido': ('Si algo no te funciona o tienes dudas, escríbenos por WhatsApp desde el botón del Centro de '
                   'Ayuda. También puedes reportar un problema desde tu panel. Te respondemos lo antes posible.')},
]


def seed_plataforma_kb():
    """Inserta el seed inicial de forma idempotente. A prueba de fallos."""
    from sqlalchemy import text
    try:
        n = 0
        for e in SEED_KB:
            db.session.execute(text("""
                INSERT INTO plataforma_kb
                    (tipo, area, clave, titulo, resumen, contenido, datos, orden, publicado, created_at, updated_at)
                VALUES
                    (:tipo, :area, :clave, :titulo, :resumen, :contenido, CAST(:datos AS JSONB), :orden, :publicado, NOW(), NOW())
                ON CONFLICT (clave) DO NOTHING
            """), {
                'tipo': e.get('tipo', 'feature'), 'area': e.get('area'),
                'clave': e['clave'], 'titulo': e['titulo'],
                'resumen': e.get('resumen'), 'contenido': e.get('contenido'),
                'datos': json.dumps(e.get('datos', {})),
                'orden': e.get('orden', 0), 'publicado': e.get('publicado', False),
            })
            n += 1
        db.session.commit()

        # Publicación inicial ÚNICA del contenido curado. Guardada por un flag en
        # config_global → solo corre una vez; después el panel manda (no re-publica).
        try:
            ya = db.session.execute(text("SELECT 1 FROM config_global WHERE clave = 'kb_publicacion_inicial'")).fetchone()
            if not ya:
                db.session.execute(text(
                    "UPDATE plataforma_kb SET publicado = TRUE WHERE tipo IN ('categoria','feature','articulo','changelog')"))
                db.session.execute(text(
                    "INSERT INTO config_global (clave, valor, updated_at) "
                    "VALUES ('kb_publicacion_inicial', CAST('true' AS JSONB), NOW()) ON CONFLICT (clave) DO NOTHING"))
                db.session.commit()
                logger.info("✅ plataforma_kb: publicación inicial del contenido curado")
        except Exception as _pe:
            db.session.rollback()
            logger.warning(f"[plataforma_kb] publicación inicial omitida: {_pe}")

        # Migración única de íconos de categoría a Bootstrap Icons (filas ya seedeadas).
        try:
            ya2 = db.session.execute(text("SELECT 1 FROM config_global WHERE clave = 'kb_iconos_bi_v1'")).fetchone()
            if not ya2:
                iconos = {e['clave']: e['datos']['icono'] for e in SEED_KB
                          if e.get('tipo') == 'categoria' and (e.get('datos') or {}).get('icono')}
                for ck, ic in iconos.items():
                    db.session.execute(text(
                        "UPDATE plataforma_kb SET datos = jsonb_set(COALESCE(datos,'{}'::jsonb), '{icono}', to_jsonb(CAST(:ic AS text))) "
                        "WHERE clave = :c"), {'ic': ic, 'c': ck})
                db.session.execute(text(
                    "INSERT INTO config_global (clave, valor, updated_at) "
                    "VALUES ('kb_iconos_bi_v1', CAST('true' AS JSONB), NOW()) ON CONFLICT (clave) DO NOTHING"))
                db.session.commit()
                logger.info("✅ plataforma_kb: íconos de categoría migrados a Bootstrap Icons")
        except Exception as _ie:
            db.session.rollback()
            logger.warning(f"[plataforma_kb] migración de íconos omitida: {_ie}")
        return n
    except Exception as ex:
        db.session.rollback()
        logger.warning(f"[plataforma_kb] seed no crítico: {ex}")
        return 0
