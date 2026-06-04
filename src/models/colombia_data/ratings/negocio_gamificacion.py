"""
TuKomercio — Modelos de Gamificación v1.0
Rachas, Misiones, XP/Nivel, TuKoins y Tienda de Personalización

© 2024-2026 Carlos Eduardo Huérfano Bermúdez. Todos los derechos reservados.
"""

from sqlalchemy import (
    Column, Integer, String, Boolean, DateTime, Date, Float,
    ForeignKey, UniqueConstraint, Text
)
from sqlalchemy.orm import relationship
from datetime import datetime, date
from src.models.database import db


# ═══════════════════════════════════════════════════════════════════
# ECONOMÍA TUKOINS — bonos por fecha (S36)
# ═══════════════════════════════════════════════════════════════════
def bono_tukoins(fecha=None):
    """
    Devuelve (multiplicador, nombre_bono) de TuKoins para la fecha dada.
    Función PURA → testeable con fechas inyectadas.
      - Domingo: x2 "Domingo de TuKoins"
      - Resto:   x1 (sin bono)
    """
    if fecha is None:
        fecha = datetime.utcnow()
    # A9: la config del bono es editable desde el panel (gamif_config).
    try:
        from .config_gamificacion import calcular_bono, get_bono_config
        return calcular_bono(fecha, get_bono_config())
    except Exception:
        # Fallback al comportamiento por defecto (domingo x2)
        if fecha.weekday() == 6:
            return 2, 'Domingo de TuKoins'
        return 1, None


# ═══════════════════════════════════════════════════════════════════
# EVENTOS ESPECIALES — ventanas de fecha con XP multiplicado (S38)
# ═══════════════════════════════════════════════════════════════════
EVENTOS_ESPECIALES = [
    {'codigo': 'semana_tendero', 'nombre': 'Semana del Tendero', 'icono': '🛍️',
     'mes': 7, 'dia_ini': 1, 'dia_fin': 7, 'xp_mult': 3},
    {'codigo': 'aniversario', 'nombre': 'Aniversario TuKomercio', 'icono': '🎂',
     'mes': 7, 'dia_ini': 24, 'dia_fin': 31, 'xp_mult': 2},
    {'codigo': 'navidad_xp', 'nombre': 'Diciembre Mágico', 'icono': '🎄',
     'mes': 12, 'dia_ini': 15, 'dia_fin': 31, 'xp_mult': 2},
]


def evento_especial(fecha=None):
    """Devuelve el evento especial activo en 'fecha', o None. Función PURA."""
    if fecha is None:
        fecha = datetime.utcnow()
    for ev in EVENTOS_ESPECIALES:
        if fecha.month == ev['mes'] and ev['dia_ini'] <= fecha.day <= ev['dia_fin']:
            return ev
    return None


def multiplicador_xp(fecha=None):
    """Multiplicador de XP activo (1 si no hay evento). Función PURA."""
    ev = evento_especial(fecha)
    return ev['xp_mult'] if ev else 1


# ═══════════════════════════════════════════════════════════════════
# TABLA PRINCIPAL DE GAMIFICACIÓN POR NEGOCIO
# ═══════════════════════════════════════════════════════════════════

class NegocioGamificacion(db.Model):
    """
    Almacena el estado de gamificación de cada negocio:
    XP, nivel, TuKoins y racha de actividad.
    Se crea automáticamente la primera vez que el negocio interactúa.
    """
    __tablename__ = 'negocio_gamificacion'

    id          = Column(Integer, primary_key=True)
    negocio_id  = Column(Integer, ForeignKey('negocios.id_negocio', ondelete='CASCADE'),
                         unique=True, nullable=False)

    # ── XP y Nivel ──────────────────────────────────────────────
    xp_total    = Column(Integer, default=0, nullable=False)
    nivel       = Column(Integer, default=1, nullable=False)

    # ── TuKoins (moneda virtual) ─────────────────────────────────
    tukoins     = Column(Integer, default=0, nullable=False)

    # ── Prestigio (S33): veces que llegó a Leyenda y reinició ────
    prestigio   = Column(Integer, default=0, nullable=False)

    # ── Onboarding completado (S40) ──────────────────────────────
    onboarding_completado = Column(Boolean, default=False, nullable=False)

    # ── Racha de actividad (uso del dashboard) ───────────────────
    racha_actividad_dias  = Column(Integer, default=0, nullable=False)
    racha_actividad_max   = Column(Integer, default=0, nullable=False)
    racha_actividad_fecha = Column(Date, nullable=True)   # último día activo

    # ── Timestamps ───────────────────────────────────────────────
    created_at  = Column(DateTime, default=datetime.utcnow)
    updated_at  = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # ── Relaciones ───────────────────────────────────────────────
    negocio     = relationship('Negocio', backref='gamificacion', uselist=False)
    misiones    = relationship('NegocioMisionCompletada', back_populates='gamificacion',
                               cascade='all, delete-orphan')
    transacciones_tukoins = relationship('TuKoinTransaccion', back_populates='gamificacion',
                                         cascade='all, delete-orphan')

    # ── Nivel system ─────────────────────────────────────────────
    NIVELES = [
        (0,     1,  '🌱 Semilla'),
        (100,   2,  '🌱 Semilla II'),
        (250,   3,  '🌿 Brote'),
        (500,   4,  '🌿 Brote II'),
        (800,   5,  '🌿 Brote III'),
        (1500,  7,  '🌳 Árbol'),
        (3000,  10, '🌳 Árbol II'),
        (6000,  15, '🌳 Árbol Mayor'),
        (10000, 20, '🏆 Campeón'),
        (25000, 30, '🏆 Leyenda'),
    ]

    def calcular_nivel(self):
        """Recalcula nivel según XP total."""
        nivel_actual = 1
        nombre_actual = '🌱 Semilla'
        for xp_req, nivel, nombre in self.NIVELES:
            if self.xp_total >= xp_req:
                nivel_actual = nivel
                nombre_actual = nombre
        self.nivel = nivel_actual
        return nivel_actual, nombre_actual

    def xp_para_siguiente_nivel(self):
        """Devuelve (xp_actual_en_rango, xp_total_para_siguiente, nombre_siguiente)."""
        for i, (xp_req, nivel, nombre) in enumerate(self.NIVELES):
            if self.xp_total < xp_req:
                prev_xp = self.NIVELES[i - 1][0] if i > 0 else 0
                return (self.xp_total - prev_xp, xp_req - prev_xp, nombre)
        return (self.xp_total, self.xp_total, '🏆 Leyenda')

    def agregar_xp(self, cantidad: int, motivo: str = ''):
        """Agrega XP y recalcula nivel. Retorna True si subió de nivel."""
        nivel_antes = self.nivel
        self.xp_total = max(0, self.xp_total + cantidad)
        self.calcular_nivel()
        return self.nivel > nivel_antes

    @property
    def xp_maximo(self):
        """XP del último nivel (Leyenda)."""
        return self.NIVELES[-1][0]

    def puede_prestigiar(self):
        """True si alcanzó el XP máximo y puede reiniciar por prestigio."""
        return self.xp_total >= self.xp_maximo

    def prestigiar(self):
        """
        Reinicia el progreso a cambio de +1 estrella de prestigio.
        Retorna True si se aplicó; False si aún no es elegible.
        Conserva TuKoins (no se pierden).
        """
        if not self.puede_prestigiar():
            return False
        self.prestigio = (self.prestigio or 0) + 1
        self.xp_total = 0
        self.calcular_nivel()
        return True

    def agregar_tukoins(self, cantidad: int, concepto: str, db_session=None):
        """Agrega TuKoins y registra transacción."""
        self.tukoins = max(0, self.tukoins + cantidad)
        if db_session:
            tx = TuKoinTransaccion(
                negocio_id=self.negocio_id,
                tipo='ganado' if cantidad > 0 else 'gastado',
                concepto=concepto,
                cantidad=abs(cantidad),
                balance_tras=self.tukoins,
            )
            db_session.add(tx)

    def actualizar_racha_actividad(self):
        """Actualiza racha de actividad diaria. Llamar al inicio de sesión."""
        hoy = date.today()
        if self.racha_actividad_fecha is None:
            self.racha_actividad_dias = 1
        elif self.racha_actividad_fecha == hoy:
            return  # ya fue contada hoy
        elif (hoy - self.racha_actividad_fecha).days == 1:
            self.racha_actividad_dias += 1
        else:
            self.racha_actividad_dias = 1  # racha rota
        self.racha_actividad_fecha = hoy
        self.racha_actividad_max = max(self.racha_actividad_max, self.racha_actividad_dias)

    @staticmethod
    def obtener_o_crear(negocio_id, db_session):
        """Obtiene el registro o lo crea si no existe."""
        registro = db_session.query(NegocioGamificacion).filter_by(
            negocio_id=negocio_id).first()
        if not registro:
            registro = NegocioGamificacion(negocio_id=negocio_id)
            db_session.add(registro)
            db_session.flush()
        return registro

    def serialize(self):
        nivel_actual, nombre_nivel = self.calcular_nivel()
        xp_en_rango, xp_para_sig, nombre_siguiente = self.xp_para_siguiente_nivel()
        progreso_pct = round((xp_en_rango / xp_para_sig * 100) if xp_para_sig else 100, 1)
        return {
            'negocio_id':   self.negocio_id,
            'xp_total':     self.xp_total,
            'nivel':        nivel_actual,
            'nombre_nivel': nombre_nivel,
            'nivel_siguiente': nombre_siguiente,
            'xp_en_rango':  xp_en_rango,
            'xp_para_siguiente': xp_para_sig,
            'progreso_pct': progreso_pct,
            'tukoins':      self.tukoins,
            'prestigio':    self.prestigio or 0,
            'puede_prestigiar': self.puede_prestigiar(),
            'onboarding_completado': bool(self.onboarding_completado),
            'racha_actividad': {
                'dias':  self.racha_actividad_dias,
                'max':   self.racha_actividad_max,
                'fecha': self.racha_actividad_fecha.isoformat() if self.racha_actividad_fecha else None,
            },
        }


# ═══════════════════════════════════════════════════════════════════
# MISIONES COMPLETADAS POR DÍA
# ═══════════════════════════════════════════════════════════════════

class NegocioMisionCompletada(db.Model):
    """Registro de misiones completadas por negocio y día."""
    __tablename__ = 'negocio_misiones_completadas'
    __table_args__ = (
        UniqueConstraint('negocio_id', 'mision_codigo', 'fecha', name='uq_mision_dia'),
    )

    id              = Column(Integer, primary_key=True)
    negocio_id      = Column(Integer, ForeignKey('negocios.id_negocio', ondelete='CASCADE'),
                             nullable=False)
    gamificacion_id = Column(Integer, ForeignKey('negocio_gamificacion.id', ondelete='CASCADE'),
                             nullable=True)
    mision_codigo   = Column(String(60), nullable=False)
    fecha           = Column(Date, nullable=False, default=date.today)
    xp_ganado       = Column(Integer, default=0)
    tukoins_ganados = Column(Integer, default=0)
    tipo            = Column(String(20), default='diaria')  # diaria | semanal
    created_at      = Column(DateTime, default=datetime.utcnow)

    gamificacion    = relationship('NegocioGamificacion', back_populates='misiones')


# ═══════════════════════════════════════════════════════════════════
# LEDGER DE TUKOINS
# ═══════════════════════════════════════════════════════════════════

class TuKoinTransaccion(db.Model):
    """Historial de movimientos de TuKoins."""
    __tablename__ = 'tukoins_transacciones'

    id              = Column(Integer, primary_key=True)
    negocio_id      = Column(Integer, ForeignKey('negocios.id_negocio', ondelete='CASCADE'),
                             nullable=False)
    gamificacion_id = Column(Integer, ForeignKey('negocio_gamificacion.id', ondelete='CASCADE'),
                             nullable=True)
    tipo            = Column(String(20), nullable=False)   # ganado | gastado
    concepto        = Column(String(200), nullable=False)
    cantidad        = Column(Integer, nullable=False)       # siempre positivo
    balance_tras    = Column(Integer, nullable=False)
    fecha           = Column(DateTime, default=datetime.utcnow)

    gamificacion    = relationship('NegocioGamificacion', back_populates='transacciones_tukoins')

    def serialize(self):
        return {
            'id':          self.id,
            'tipo':        self.tipo,
            'concepto':    self.concepto,
            'cantidad':    self.cantidad if self.tipo == 'ganado' else -self.cantidad,
            'balance_tras': self.balance_tras,
            'fecha':       self.fecha.isoformat() if self.fecha else None,
        }


# ═══════════════════════════════════════════════════════════════════
# TIENDA DE PERSONALIZACIÓN — CATÁLOGO DE ÍTEMS
# ═══════════════════════════════════════════════════════════════════

class TiendaItem(db.Model):
    """Ítems disponibles en la Tienda de TuKoins."""
    __tablename__ = 'tienda_items'

    id               = Column(Integer, primary_key=True)
    codigo           = Column(String(60), unique=True, nullable=False)
    nombre           = Column(String(100), nullable=False)
    descripcion      = Column(String(255), nullable=True)
    tipo             = Column(String(50), nullable=False)
    # tipos: marco_logo | tema_color | banner_tienda | sticker | badge_temporal | efecto_badge
    icono            = Column(String(10), default='🎁')
    precio_tukoins   = Column(Integer, nullable=False)
    nivel_requerido  = Column(Integer, default=1)
    css_value        = Column(Text, nullable=True)   # CSS o valor de personalización
    imagen_preview   = Column(String(500), nullable=True)
    activo           = Column(Boolean, default=True)
    created_at       = Column(DateTime, default=datetime.utcnow)

    compras          = relationship('TiendaCompra', back_populates='item')

    def serialize(self):
        return {
            'id':              self.id,
            'codigo':          self.codigo,
            'nombre':          self.nombre,
            'descripcion':     self.descripcion,
            'tipo':            self.tipo,
            'icono':           self.icono,
            'precio_tukoins':  self.precio_tukoins,
            'nivel_requerido': self.nivel_requerido,
            'css_value':       self.css_value,
            'imagen_preview':  self.imagen_preview,
        }


class TiendaCompra(db.Model):
    """Registro de compras en la tienda."""
    __tablename__ = 'tienda_compras'

    id               = Column(Integer, primary_key=True)
    negocio_id       = Column(Integer, ForeignKey('negocios.id_negocio', ondelete='CASCADE'),
                              nullable=False)
    item_id          = Column(Integer, ForeignKey('tienda_items.id'), nullable=False)
    tukoins_gastados = Column(Integer, nullable=False)
    activo           = Column(Boolean, default=True)   # False = "desequipado"
    fecha_compra     = Column(DateTime, default=datetime.utcnow)

    item             = relationship('TiendaItem', back_populates='compras')

    def serialize(self):
        return {
            'id':              self.id,
            'item':            self.item.serialize() if self.item else None,
            'tukoins_gastados': self.tukoins_gastados,
            'activo':          self.activo,
            'fecha_compra':    self.fecha_compra.isoformat() if self.fecha_compra else None,
        }


# ═══════════════════════════════════════════════════════════════════
# SEED DATA — ÍTEMS INICIALES DE LA TIENDA
# ═══════════════════════════════════════════════════════════════════

TIENDA_ITEMS_SEED = [
    # ── Marcos de logo ──────────────────────────────────────────
    {
        'codigo': 'marco_fuego',
        'nombre': 'Marco Fuego 🔥',
        'descripcion': 'Borde animado en llamas para tu logo',
        'tipo': 'marco_logo',
        'icono': '🔥',
        'precio_tukoins': 100,
        'nivel_requerido': 3,
        'css_value': 'border: 3px solid; border-image: linear-gradient(#ff4500,#ff8c00,#ffd700) 1; box-shadow: 0 0 12px #ff4500;',
    },
    {
        'codigo': 'marco_diamante',
        'nombre': 'Marco Diamante 💎',
        'descripcion': 'Bordes de cristal brillante',
        'tipo': 'marco_logo',
        'icono': '💎',
        'precio_tukoins': 200,
        'nivel_requerido': 5,
        'css_value': 'border: 3px solid #00d4ff; box-shadow: 0 0 18px rgba(0,212,255,0.6);',
    },
    {
        'codigo': 'marco_dorado',
        'nombre': 'Marco Dorado 🌟',
        'descripcion': 'El marco más prestigioso',
        'tipo': 'marco_logo',
        'icono': '🌟',
        'precio_tukoins': 500,
        'nivel_requerido': 10,
        'css_value': 'border: 3px solid gold; box-shadow: 0 0 20px gold, 0 0 40px rgba(255,215,0,0.4);',
    },
    # ── Stickers de perfil ──────────────────────────────────────
    {
        'codigo': 'sticker_veloz',
        'nombre': 'Sticker ⚡ Veloz',
        'descripcion': 'Muestra que entregas rápido',
        'tipo': 'sticker',
        'icono': '⚡',
        'precio_tukoins': 50,
        'nivel_requerido': 1,
        'css_value': '⚡',
    },
    {
        'codigo': 'sticker_confiable',
        'nombre': 'Sticker 💯 Confiable',
        'descripcion': 'Sello de 100% confiabilidad',
        'tipo': 'sticker',
        'icono': '💯',
        'precio_tukoins': 75,
        'nivel_requerido': 2,
        'css_value': '💯',
    },
    {
        'codigo': 'sticker_top',
        'nombre': 'Sticker 🏆 Top Vendedor',
        'descripcion': 'Para los mejores del ranking',
        'tipo': 'sticker',
        'icono': '🏆',
        'precio_tukoins': 200,
        'nivel_requerido': 7,
        'css_value': '🏆',
    },
    # ── Banner de tienda ────────────────────────────────────────
    {
        'codigo': 'banner_oferta',
        'nombre': 'Banner "Ofertas del Día" 🎉',
        'descripcion': 'Banner llamativo para tu tienda online',
        'tipo': 'banner_tienda',
        'icono': '🎉',
        'precio_tukoins': 150,
        'nivel_requerido': 3,
        'css_value': 'background: linear-gradient(135deg,#f59e0b,#ef4444); color:#fff; font-weight:700;',
    },
    {
        'codigo': 'banner_premium',
        'nombre': 'Banner Premium ✨',
        'descripcion': 'Diseño premium con efecto de lujo',
        'tipo': 'banner_tienda',
        'icono': '✨',
        'precio_tukoins': 300,
        'nivel_requerido': 7,
        'css_value': 'background: linear-gradient(135deg,#1e1b4b,#7c3aed); color:#f0edff; font-weight:700; border: 1px solid rgba(167,139,250,0.4);',
    },
    # ── Efectos de badge ────────────────────────────────────────
    {
        'codigo': 'efecto_brillo',
        'nombre': 'Efecto Brillo para Badges ⭐',
        'descripcion': 'Tus badges brillan con una animación',
        'tipo': 'efecto_badge',
        'icono': '⭐',
        'precio_tukoins': 120,
        'nivel_requerido': 5,
        'css_value': 'animation: badgePulse 2s ease-in-out infinite; filter: drop-shadow(0 0 6px currentColor);',
    },

    # ════════ AMPLIACIÓN S15 ════════
    # ── Marcos de logo adicionales ──
    {
        'codigo': 'marco_neon', 'nombre': 'Marco Neón 💜', 'descripcion': 'Borde neón vibrante',
        'tipo': 'marco_logo', 'icono': '💜', 'precio_tukoins': 130, 'nivel_requerido': 4,
        'css_value': 'border:3px solid #a855f7; box-shadow:0 0 16px rgba(168,85,247,0.7);',
    },
    {
        'codigo': 'marco_esmeralda', 'nombre': 'Marco Esmeralda 💚', 'descripcion': 'Verde lujoso',
        'tipo': 'marco_logo', 'icono': '💚', 'precio_tukoins': 160, 'nivel_requerido': 5,
        'css_value': 'border:3px solid #10b981; box-shadow:0 0 16px rgba(16,185,129,0.6);',
    },
    {
        'codigo': 'marco_arcoiris', 'nombre': 'Marco Arcoíris 🌈', 'descripcion': 'Degradado multicolor animado',
        'tipo': 'marco_logo', 'icono': '🌈', 'precio_tukoins': 350, 'nivel_requerido': 8,
        'css_value': 'border:3px solid; border-image:linear-gradient(90deg,#f00,#ff0,#0f0,#0ff,#00f,#f0f) 1;',
    },
    # ── Temas de color para la tienda pública ──
    {
        'codigo': 'tema_oceano', 'nombre': 'Tema Océano 🌊', 'descripcion': 'Paleta azul fresca para tu tienda',
        'tipo': 'tema_color', 'icono': '🌊', 'precio_tukoins': 180, 'nivel_requerido': 4,
        'css_value': '{"primary":"#0ea5e9","accent":"#06b6d4","bg":"#f0f9ff"}',
    },
    {
        'codigo': 'tema_atardecer', 'nombre': 'Tema Atardecer 🌅', 'descripcion': 'Tonos cálidos naranja-rosa',
        'tipo': 'tema_color', 'icono': '🌅', 'precio_tukoins': 180, 'nivel_requerido': 4,
        'css_value': '{"primary":"#f97316","accent":"#ec4899","bg":"#fff7ed"}',
    },
    {
        'codigo': 'tema_bosque', 'nombre': 'Tema Bosque 🌿', 'descripcion': 'Verdes naturales y orgánicos',
        'tipo': 'tema_color', 'icono': '🌿', 'precio_tukoins': 180, 'nivel_requerido': 4,
        'css_value': '{"primary":"#16a34a","accent":"#65a30d","bg":"#f7fee7"}',
    },
    {
        'codigo': 'tema_medianoche', 'nombre': 'Tema Medianoche 🌙', 'descripcion': 'Modo oscuro elegante',
        'tipo': 'tema_color', 'icono': '🌙', 'precio_tukoins': 250, 'nivel_requerido': 6,
        'css_value': '{"primary":"#6366f1","accent":"#a855f7","bg":"#0f172a"}',
    },
    # ── Stickers adicionales ──
    {
        'codigo': 'sticker_eco', 'nombre': 'Sticker 🌱 Eco', 'descripcion': 'Negocio sostenible',
        'tipo': 'sticker', 'icono': '🌱', 'precio_tukoins': 60, 'nivel_requerido': 2, 'css_value': '🌱',
    },
    {
        'codigo': 'sticker_premium', 'nombre': 'Sticker 👑 Premium', 'descripcion': 'Calidad premium',
        'tipo': 'sticker', 'icono': '👑', 'precio_tukoins': 220, 'nivel_requerido': 7, 'css_value': '👑',
    },
    # ── Banner adicional ──
    {
        'codigo': 'banner_nuevo', 'nombre': 'Banner "Recién Llegado" 🆕', 'descripcion': 'Anuncia novedades',
        'tipo': 'banner_tienda', 'icono': '🆕', 'precio_tukoins': 120, 'nivel_requerido': 2,
        'css_value': 'background:linear-gradient(135deg,#3b82f6,#06b6d4); color:#fff; font-weight:700;',
    },
    # ── Fondos de perfil ──
    {
        'codigo': 'fondo_geometrico', 'nombre': 'Fondo Geométrico 🔷', 'descripcion': 'Patrón moderno para tu perfil',
        'tipo': 'banner_tienda', 'icono': '🔷', 'precio_tukoins': 140, 'nivel_requerido': 3,
        'css_value': 'background:repeating-linear-gradient(45deg,#1e293b,#1e293b 10px,#0f172a 10px,#0f172a 20px);',
    },
]


def seed_tienda_items(db_session, actualizar=True):
    """
    Siembra/actualiza el catálogo de items de la tienda TuKoins de forma
    idempotente (upsert por 'codigo'). Antes el seed solo corría si la tabla
    estaba vacía → los items nuevos nunca entraban. Esto lo arregla.
    Returns: dict {creados, actualizados, total}
    """
    creados = 0
    actualizados = 0
    existentes = {i.codigo: i for i in db_session.query(TiendaItem).all()}
    _campos_act = ('nombre', 'descripcion', 'tipo', 'icono',
                   'precio_tukoins', 'nivel_requerido', 'css_value')
    for data in TIENDA_ITEMS_SEED:
        ex = existentes.get(data['codigo'])
        if ex is None:
            db_session.add(TiendaItem(**data))
            creados += 1
        elif actualizar:
            cambio = False
            for c in _campos_act:
                if c in data and getattr(ex, c, None) != data[c]:
                    setattr(ex, c, data[c]); cambio = True
            if cambio:
                actualizados += 1
    db_session.commit()
    return {'creados': creados, 'actualizados': actualizados, 'total': len(TIENDA_ITEMS_SEED)}


# ═══════════════════════════════════════════════════════════════════
# POOL DE MISIONES — DEFINICIÓN ESTÁTICA
# ═══════════════════════════════════════════════════════════════════

POOL_MISIONES_DIARIAS = [
    {
        'codigo':      'completar_venta',
        'nombre':      'Completa 1 venta',
        'descripcion': 'Registra un pedido como entregado hoy',
        'icono':       '🛒',
        'xp':          20,
        'tukoins':     10,
        'tipo':        'diaria',
        'auto':        True,   # se verifica automáticamente en la BD
        'dificultad':  'media',
    },
    {
        'codigo':      'agregar_producto',
        'nombre':      'Agrega 1 producto',
        'descripcion': 'Añade un producto nuevo a tu inventario',
        'icono':       '📦',
        'xp':          15,
        'tukoins':     5,
        'tipo':        'diaria',
        'auto':        True,
        'dificultad':  'facil',
    },
    {
        'codigo':      'subir_video',
        'nombre':      'Sube 1 video',
        'descripcion': 'Comparte un video de tu negocio',
        'icono':       '🎬',
        'xp':          25,
        'tukoins':     10,
        'tipo':        'diaria',
        'auto':        True,
        'dificultad':  'media',
    },
    {
        'codigo':      'actualizar_perfil',
        'nombre':      'Actualiza tu perfil',
        'descripcion': 'Edita algo en la info de tu negocio hoy',
        'icono':       '✏️',
        'xp':          15,
        'tukoins':     5,
        'tipo':        'diaria',
        'auto':        True,
        'dificultad':  'facil',
    },
    {
        'codigo':      'compartir_redes',
        'nombre':      'Comparte en redes',
        'descripcion': 'Comparte tu tienda en Instagram o WhatsApp',
        'icono':       '📲',
        'xp':          10,
        'tukoins':     5,
        'tipo':        'diaria',
        'auto':        False,  # manual
        'dificultad':  'facil',
    },
    {
        'codigo':      'responder_cliente',
        'nombre':      'Responde a un cliente',
        'descripcion': 'Atiende una notificación o mensaje de cliente',
        'icono':       '💬',
        'xp':          10,
        'tukoins':     5,
        'tipo':        'diaria',
        'auto':        False,
        'dificultad':  'facil',
    },
    # ── Ampliación S14 (más variedad en la rotación diaria) ──
    {
        'codigo': 'vender_3', 'nombre': 'Cierra 3 ventas hoy',
        'descripcion': 'Entrega 3 pedidos en el mismo día',
        'icono': '🔥', 'xp': 45, 'tukoins': 20, 'tipo': 'diaria',
        'auto': True, 'dificultad': 'alta',
    },
    {
        'codigo': 'dos_productos', 'nombre': 'Agrega 2 productos',
        'descripcion': 'Suma dos productos nuevos a tu catálogo hoy',
        'icono': '📦', 'xp': 25, 'tukoins': 10, 'tipo': 'diaria',
        'auto': True, 'dificultad': 'media',
    },
    {
        'codigo': 'compartir_producto', 'nombre': 'Comparte un producto',
        'descripcion': 'Comparte un producto de tu tienda en redes',
        'icono': '🔗', 'xp': 12, 'tukoins': 6, 'tipo': 'diaria',
        'auto': False, 'dificultad': 'facil',
    },
    {
        'codigo': 'revisar_inventario', 'nombre': 'Revisa tu inventario',
        'descripcion': 'Verifica tus niveles de stock del día',
        'icono': '📋', 'xp': 10, 'tukoins': 5, 'tipo': 'diaria',
        'auto': False, 'dificultad': 'facil',
    },
    {
        'codigo': 'responder_resena', 'nombre': 'Responde una reseña',
        'descripcion': 'Agradece o responde la reseña de un cliente',
        'icono': '⭐', 'xp': 12, 'tukoins': 6, 'tipo': 'diaria',
        'auto': False, 'dificultad': 'facil',
    },
    {
        'codigo': 'revisar_pedidos', 'nombre': 'Gestiona tus pedidos',
        'descripcion': 'Revisa y actualiza el estado de tus pedidos',
        'icono': '🚚', 'xp': 10, 'tukoins': 5, 'tipo': 'diaria',
        'auto': False, 'dificultad': 'facil',
    },
]

POOL_MISIONES_SEMANALES = [
    {
        'codigo':      'ventas_semana_5',
        'nombre':      'Completa 5 ventas esta semana',
        'descripcion': 'Cinco pedidos entregados en 7 días',
        'icono':       '🏅',
        'xp':          100,
        'tukoins':     50,
        'tipo':        'semanal',
        'auto':        True,
        'dificultad':  'alta',
    },
    {
        'codigo':      'videos_semana_3',
        'nombre':      'Sube 3 videos esta semana',
        'descripcion': 'Sé un creador de contenido activo',
        'icono':       '🎥',
        'xp':          75,
        'tukoins':     35,
        'tipo':        'semanal',
        'auto':        True,
        'dificultad':  'media',
    },
    {
        'codigo':      'productos_semana_5',
        'nombre':      'Agrega 5 productos esta semana',
        'descripcion': 'Expande tu catálogo con nuevos productos',
        'icono':       '📋',
        'xp':          60,
        'tukoins':     30,
        'tipo':        'semanal',
        'auto':        True,
        'dificultad':  'media',
    },
]

# ═══════════════════════════════════════════════════════════════════
# POOL DE MISIONES MENSUALES (S14) — objetivos grandes de mes calendario
# Se auto-completan al consultar el dashboard (igual que las semanales).
# ═══════════════════════════════════════════════════════════════════
POOL_MISIONES_MENSUALES = [
    {
        'codigo': 'ventas_mes_20', 'nombre': 'Cierra 20 ventas este mes',
        'descripcion': 'Veinte pedidos entregados en el mes',
        'icono': '🏆', 'xp': 300, 'tukoins': 150, 'tipo': 'mensual',
        'auto': True, 'dificultad': 'alta',
    },
    {
        'codigo': 'productos_mes_15', 'nombre': 'Agrega 15 productos este mes',
        'descripcion': 'Haz crecer tu catálogo con 15 productos nuevos',
        'icono': '📦', 'xp': 180, 'tukoins': 90, 'tipo': 'mensual',
        'auto': True, 'dificultad': 'media',
    },
    {
        'codigo': 'videos_mes_8', 'nombre': 'Sube 8 videos este mes',
        'descripcion': 'Mantente activo como creador de contenido',
        'icono': '🎥', 'xp': 200, 'tukoins': 100, 'tipo': 'mensual',
        'auto': True, 'dificultad': 'media',
    },
]
