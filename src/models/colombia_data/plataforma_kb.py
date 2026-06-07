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
    {'tipo': 'categoria', 'area': 'ayuda', 'clave': 'cat-primeros-pasos', 'titulo': 'Primeros pasos', 'resumen': 'Crea tu tienda y empieza a vender.', 'datos': {'icono': '🚀'}, 'orden': 1},
    {'tipo': 'categoria', 'area': 'ayuda', 'clave': 'cat-diseno', 'titulo': 'Diseña tu tienda', 'resumen': 'Logo, colores, portada y el Diseñador.', 'datos': {'icono': '🎨'}, 'orden': 2},
    {'tipo': 'categoria', 'area': 'ayuda', 'clave': 'cat-productos', 'titulo': 'Productos e inventario', 'resumen': 'Sube productos, controla stock y precios.', 'datos': {'icono': '📦'}, 'orden': 3},
    {'tipo': 'categoria', 'area': 'ayuda', 'clave': 'cat-pedidos', 'titulo': 'Pedidos y envíos', 'resumen': 'Recibe pedidos, estados y fletes.', 'datos': {'icono': '🛒'}, 'orden': 4},
    {'tipo': 'categoria', 'area': 'ayuda', 'clave': 'cat-pagos', 'titulo': 'Pagos y cobros', 'resumen': 'Wompi, Nequi, contra entrega y más.', 'datos': {'icono': '💳'}, 'orden': 5},
    {'tipo': 'categoria', 'area': 'ayuda', 'clave': 'cat-vender-mas', 'titulo': 'Vende más', 'resumen': 'WhatsApp, promociones y Dora IA.', 'datos': {'icono': '📣'}, 'orden': 6},
    {'tipo': 'categoria', 'area': 'ayuda', 'clave': 'cat-premios', 'titulo': 'Premios y logros', 'resumen': 'Sube de nivel, gana insignias y TuKoins.', 'datos': {'icono': '🏆'}, 'orden': 7},
    {'tipo': 'categoria', 'area': 'ayuda', 'clave': 'cat-cuenta', 'titulo': 'Mi cuenta y plan', 'resumen': 'Contraseña, datos, plan y facturación.', 'datos': {'icono': '⚙️'}, 'orden': 8},

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
        return n
    except Exception as ex:
        db.session.rollback()
        logger.warning(f"[plataforma_kb] seed no crítico: {ex}")
        return 0
