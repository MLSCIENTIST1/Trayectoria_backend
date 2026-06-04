"""
TuKomercio — Motor de Eventos de Gamificación (Hooks) v1.0
═══════════════════════════════════════════════════════════════════════════════

Este módulo es el CORAZÓN del sistema de gamificación. Conecta las acciones
reales del usuario (vender, crear productos, publicar tienda, iniciar sesión)
con el sistema de XP, misiones, badges y notificaciones.

PRINCIPIO DE DISEÑO INQUEBRANTABLE:
    Un fallo en la gamificación NUNCA debe romper la operación principal.
    Todos los hooks atrapan sus propias excepciones y hacen su propio commit.
    Si la gamificación falla, el pedido/producto/login siguen su curso normal.

USO (desde checkout_api, pedidos_api, etc.):
    from src.api.gamificacion.gamificacion_hooks import on_venta_completada
    celebracion = on_venta_completada(negocio_id, pedido=pedido)
    # celebracion → dict con lo que ganó el negocio (para que el front celebre)

© 2024-2026 Carlos Eduardo Huérfano Bermúdez. Todos los derechos reservados.
"""

import logging
from datetime import date, timedelta

from src.models.database import db

logger = logging.getLogger(__name__)

# ═══════════════════════════════════════════════════════════════════
# ECONOMÍA DE XP POR EVENTO (XP base, además de misiones/badges)
# ═══════════════════════════════════════════════════════════════════
# XP/TuKoins por evento. El DEFAULT vive en config_gamificacion; desde el panel
# de admin (A6) se puede sobreescribir en BD. _xp_eventos() devuelve el efectivo.
from src.models.colombia_data.ratings.config_gamificacion import (
    XP_EVENTOS_DEFAULT as XP_EVENTOS, get_xp_eventos as _xp_eventos,
    get_pool as _get_pool
)


# ═══════════════════════════════════════════════════════════════════
# HELPERS INTERNOS
# ═══════════════════════════════════════════════════════════════════

def _owner_user_id(negocio_id):
    """Obtiene el user_id del dueño del negocio (para notificaciones)."""
    try:
        from src.models.colombia_data.negocio import Negocio
        n = Negocio.query.get(negocio_id)
        return getattr(n, 'usuario_id', None) if n else None
    except Exception:
        return None


def _mision_ya_completada(negocio_id, codigo, tipo='diaria'):
    """True si la misión ya fue completada hoy (diaria) o esta semana (semanal)."""
    from src.models.colombia_data.ratings.negocio_gamificacion import NegocioMisionCompletada
    q = db.session.query(NegocioMisionCompletada).filter_by(
        negocio_id=negocio_id, mision_codigo=codigo)
    if tipo == 'diaria':
        q = q.filter(NegocioMisionCompletada.fecha == date.today())
    else:  # semanal: dentro de los últimos 7 días
        q = q.filter(NegocioMisionCompletada.fecha >= date.today() - timedelta(days=6))
    return db.session.query(q.exists()).scalar()


def _completar_mision(negocio_id, gami, mision, tipo='diaria'):
    """
    Registra una misión y otorga XP + TuKoins. Idempotente.
    Retorna dict de misión completada o None si ya estaba completada.
    """
    if _mision_ya_completada(negocio_id, mision['codigo'], tipo):
        return None

    from src.models.colombia_data.ratings.negocio_gamificacion import (
        NegocioMisionCompletada, bono_tukoins, multiplicador_xp
    )
    mult, _ = bono_tukoins()                      # S36: multiplicador por fecha (domingo x2)
    tukoins_final = (mision['tukoins'] or 0) * mult
    xp_mult = multiplicador_xp()                  # S38: evento especial (Semana del Tendero x3)
    xp_final = (mision['xp'] or 0) * xp_mult
    registro = NegocioMisionCompletada(
        negocio_id=negocio_id,
        gamificacion_id=gami.id,
        mision_codigo=mision['codigo'],
        fecha=date.today(),
        xp_ganado=xp_final,
        tukoins_ganados=tukoins_final,
        tipo=tipo,
    )
    db.session.add(registro)
    subio = gami.agregar_xp(xp_final, f"Misión: {mision['nombre']}")
    gami.agregar_tukoins(tukoins_final, f"Misión: {mision['nombre']}", db_session=db.session)
    return {
        'codigo':   mision['codigo'],
        'nombre':   mision['nombre'],
        'icono':    mision['icono'],
        'xp':       xp_final,
        'tukoins':  tukoins_final,
        'tipo':     tipo,
        'subio_nivel': subio,
    }


def _buscar_mision(pool, codigo):
    """Encuentra una misión por código en un pool."""
    for m in pool:
        if m['codigo'] == codigo:
            return m
    return None


def _contar_ventas_semana(negocio_id):
    """Cuenta pedidos entregados en los últimos 7 días. Nunca lanza."""
    try:
        try:
            from src.models.compradores.pedido import Pedido
        except ImportError:
            from src.api.compradores.pedidos_api import Pedido
        desde = date.today() - timedelta(days=6)
        return Pedido.query.filter(
            Pedido.negocio_id == negocio_id,
            Pedido.estado == 'entregado',
            Pedido.fecha_pedido >= desde,
        ).count()
    except Exception as e:
        logger.warning(f"[gamif] No se pudo contar ventas de la semana: {e}")
        return 0


def _crear_notif(negocio_id, user_id, tipo, titulo, mensaje, extra=None, prioridad='media'):
    """Crea una notificación de gamificación de forma segura."""
    if not user_id:
        return
    try:
        from src.api.notifications.notifications_api import Notification
        Notification.crear_notificacion_generica(
            negocio_id=negocio_id, user_id=user_id, tipo=tipo,
            titulo=titulo, mensaje=mensaje,
            referencia_tipo='gamificacion', prioridad=prioridad,
            action_url='/contabilidad/modulos/gamificacion.html',
            extra_data=extra or {},
        )
    except Exception as e:
        logger.warning(f"[gamif] No se pudo crear notificación {tipo}: {e}")


def _verificar_badges_seguro(negocio_id):
    """Corre la verificación de badges sin romper nada. Retorna lista de nuevos."""
    try:
        from src.api.utils.badge_verification_service import BadgeVerificationService
        resultado = BadgeVerificationService.verificar_badges(negocio_id)
        return resultado.get('nuevos', []) or []
    except Exception as e:
        logger.warning(f"[gamif] Verificación de badges falló (negocio {negocio_id}): {e}")
        return []


# ═══════════════════════════════════════════════════════════════════
# MOTOR CENTRAL
# ═══════════════════════════════════════════════════════════════════

def _procesar_evento(negocio_id, evento, misiones_diarias=None,
                     misiones_semanales=None, verificar_badges=True):
    """
    Núcleo del motor. Procesa un evento de gamificación de forma atómica
    y a prueba de fallos.

    Args:
        negocio_id:          ID del negocio
        evento:              clave en XP_EVENTOS (xp base del evento)
        misiones_diarias:    lista de códigos de misiones diarias a verificar
        misiones_semanales:  lista de (codigo, condicion_bool) a verificar
        verificar_badges:    si corre BadgeVerificationService

    Returns:
        dict 'celebracion' con todo lo que ganó el negocio, o None si falló.
    """
    try:
        from src.models.colombia_data.ratings.negocio_gamificacion import (
            NegocioGamificacion, POOL_MISIONES_DIARIAS, POOL_MISIONES_SEMANALES,
            multiplicador_xp, evento_especial
        )

        gami = NegocioGamificacion.obtener_o_crear(negocio_id, db.session)
        nivel_antes = gami.nivel
        xp_mult = multiplicador_xp()              # S38: evento especial activo (x2/x3)
        ev_activo = evento_especial()

        celebracion = {
            'negocio_id':      negocio_id,
            'evento':          evento,
            'xp_ganado':       0,
            'tukoins_ganados': 0,
            'subio_nivel':     False,
            'nivel_nuevo':     None,
            'nombre_nivel':    None,
            'misiones':        [],
            'badges_nuevos':   [],
            'evento_especial': ({'nombre': ev_activo['nombre'], 'icono': ev_activo['icono'],
                                 'xp_mult': ev_activo['xp_mult']} if ev_activo else None),
        }

        # 1) XP base del evento (×multiplicador si hay evento especial activo)
        cfg = _xp_eventos().get(evento, {'xp': 0, 'tukoins': 0})
        if cfg['xp']:
            xp_base = cfg['xp'] * xp_mult
            gami.agregar_xp(xp_base, f"Evento: {evento}")
            celebracion['xp_ganado'] += xp_base
        if cfg['tukoins']:
            gami.agregar_tukoins(cfg['tukoins'], f"Evento: {evento}", db_session=db.session)
            celebracion['tukoins_ganados'] += cfg['tukoins']

        # 2) Misiones diarias
        for codigo in (misiones_diarias or []):
            mision = _buscar_mision(_get_pool('diaria'), codigo)
            if not mision:
                continue
            res = _completar_mision(negocio_id, gami, mision, tipo='diaria')
            if res:
                celebracion['misiones'].append(res)
                celebracion['xp_ganado'] += res['xp']
                celebracion['tukoins_ganados'] += res['tukoins']

        # 3) Misiones semanales (solo si cumple la condición)
        for codigo, cumple in (misiones_semanales or []):
            if not cumple:
                continue
            mision = _buscar_mision(_get_pool('semanal'), codigo)
            if not mision:
                continue
            res = _completar_mision(negocio_id, gami, mision, tipo='semanal')
            if res:
                celebracion['misiones'].append(res)
                celebracion['xp_ganado'] += res['xp']
                celebracion['tukoins_ganados'] += res['tukoins']

        # 4) Nivel
        nivel_actual, nombre_nivel = gami.calcular_nivel()
        celebracion['nivel_nuevo'] = nivel_actual
        celebracion['nombre_nivel'] = nombre_nivel
        if nivel_actual > nivel_antes:
            celebracion['subio_nivel'] = True

        # Commit de XP/misiones ANTES de verificar badges
        # (badge service hace su propio commit)
        db.session.commit()

        # 5) Badges (el servicio hace su propio commit interno)
        if verificar_badges:
            nuevos = _verificar_badges_seguro(negocio_id)
            celebracion['badges_nuevos'] = nuevos

        # 6) Notificaciones de celebración
        _emitir_notificaciones(negocio_id, celebracion)

        return celebracion

    except Exception as e:
        logger.error(f"[gamif] Error procesando evento '{evento}' "
                     f"para negocio {negocio_id}: {e}", exc_info=True)
        try:
            db.session.rollback()
        except Exception:
            pass
        return None


def _emitir_notificaciones(negocio_id, celebracion):
    """Genera las notificaciones según lo que ocurrió en el evento."""
    user_id = _owner_user_id(negocio_id)
    if not user_id:
        return

    # Subió de nivel
    if celebracion['subio_nivel']:
        _crear_notif(
            negocio_id, user_id, 'nivel_subido',
            f"¡Subiste a {celebracion['nombre_nivel']}!",
            f"Tu negocio alcanzó el nivel {celebracion['nivel_nuevo']}. ¡Sigue así!",
            extra={'nivel': celebracion['nivel_nuevo'], 'nombre_nivel': celebracion['nombre_nivel']},
            prioridad='alta',
        )

    # Misiones completadas
    for m in celebracion['misiones']:
        _crear_notif(
            negocio_id, user_id, 'mision_completada',
            f"{m['icono']} Misión completada: {m['nombre']}",
            f"Ganaste +{m['xp']} XP y +{m['tukoins']} TuKoins.",
            extra={'codigo': m['codigo'], 'xp': m['xp'], 'tukoins': m['tukoins']},
        )

    # Badges nuevos
    for b in celebracion['badges_nuevos']:
        _crear_notif(
            negocio_id, user_id, 'badge_nuevo',
            f"🏆 ¡Nueva insignia: {b.get('nombre', '')}!",
            f"Desbloqueaste una insignia de nivel {b.get('nivel', '')}. ¡Felicitaciones!",
            extra={'codigo': b.get('codigo'), 'nivel': b.get('nivel')},
            prioridad='alta',
        )

    try:
        db.session.commit()
    except Exception:
        db.session.rollback()


# ═══════════════════════════════════════════════════════════════════
# HOOKS PÚBLICOS — los llaman otros módulos
# ═══════════════════════════════════════════════════════════════════

def on_venta_completada(negocio_id, pedido=None):
    """
    Se dispara cuando un pedido pasa a estado 'entregado'.
    Otorga XP de venta, completa misiones de venta y verifica badges.
    """
    if not negocio_id:
        return None
    ventas_semana = _contar_ventas_semana(negocio_id)
    resultado = _procesar_evento(
        negocio_id,
        evento='venta_completada',
        misiones_diarias=['completar_venta'],
        misiones_semanales=[('ventas_semana_5', ventas_semana >= 5)],
        verificar_badges=True,
    )
    # ★ S29 — conversión de referido: si el dueño fue referido, premia al referidor
    try:
        owner = _owner_user_id(negocio_id)
        if owner:
            from src.api.gamificacion.gamificacion_api import procesar_conversion_referido
            procesar_conversion_referido(owner)
    except Exception as e:
        logger.warning(f"[gamif] conversión referido no crítica: {e}")
    return resultado


def on_producto_creado(negocio_id):
    """Se dispara al crear un producto nuevo. (Se cablea en S3)"""
    if not negocio_id:
        return None
    return _procesar_evento(
        negocio_id,
        evento='producto_creado',
        misiones_diarias=['agregar_producto'],
        misiones_semanales=[],
        verificar_badges=True,
    )


def on_tienda_publicada(negocio_id):
    """Se dispara al publicar la tienda. (Se cablea en S4)"""
    if not negocio_id:
        return None
    return _procesar_evento(
        negocio_id,
        evento='tienda_publicada',
        misiones_diarias=[],
        misiones_semanales=[],
        verificar_badges=True,
    )


def on_video_subido(negocio_id):
    """Se dispara al subir un video al feed."""
    if not negocio_id:
        return None
    return _procesar_evento(
        negocio_id,
        evento='video_subido',
        misiones_diarias=['subir_video'],
        misiones_semanales=[],
        verificar_badges=True,
    )


def on_login_usuario(usuario_id):
    """
    Gamificación a nivel de PERSONA (S8). Se dispara al iniciar sesión.
    Actualiza la racha de login personal y otorga XP diario al creador.
    Independiente de los negocios — mide la trayectoria del emprendedor.
    """
    if not usuario_id:
        return None
    try:
        from src.models.colombia_data.ratings.usuario_gamificacion import UsuarioGamificacion
        gu = UsuarioGamificacion.obtener_o_crear(usuario_id, db.session)
        record_antes = gu.racha_login_max
        nivel_antes = gu.nivel

        avanzo_hoy = gu.actualizar_racha_login()

        cel = {
            'usuario_id': usuario_id,
            'evento': 'login_personal',
            'xp_ganado': 0,
            'subio_nivel': False,
            'nivel_nuevo': gu.nivel,
            'nombre_nivel': None,
            'racha_dias': gu.racha_login_dias,
            'racha_record': False,
        }

        if avanzo_hoy:
            gu.agregar_xp(5, "Login diario (creador)")
            cel['xp_ganado'] = 5
            nivel_actual, nombre_nivel = gu.calcular_nivel()
            cel['nivel_nuevo'] = nivel_actual
            cel['nombre_nivel'] = nombre_nivel
            cel['subio_nivel'] = nivel_actual > nivel_antes
            if gu.racha_login_dias > record_antes and gu.racha_login_dias >= 3:
                cel['racha_record'] = True

        db.session.commit()

        # Notificación de subida de nivel personal (usa el mismo tipo)
        if cel['subio_nivel']:
            _crear_notif(
                None, usuario_id, 'nivel_subido',
                f"¡Eres {cel['nombre_nivel']}!",
                f"Subiste al nivel {cel['nivel_nuevo']} como creador. ¡Sigue construyendo!",
                extra={'nivel': cel['nivel_nuevo'], 'ambito': 'usuario'},
                prioridad='alta',
            )
            try:
                db.session.commit()
            except Exception:
                db.session.rollback()

        return cel

    except Exception as e:
        logger.error(f"[gamif] Error en on_login_usuario {usuario_id}: {e}", exc_info=True)
        try:
            db.session.rollback()
        except Exception:
            pass
        return None


def on_login(negocio_id):
    """
    Se dispara al iniciar sesión. Actualiza racha de actividad y XP diario.
    (Se cablea en S2)
    """
    if not negocio_id:
        return None
    try:
        from src.models.colombia_data.ratings.negocio_gamificacion import NegocioGamificacion
        gami = NegocioGamificacion.obtener_o_crear(negocio_id, db.session)
        racha_antes = gami.racha_actividad_dias
        record_antes = gami.racha_actividad_max

        # Solo otorga XP de login una vez al día (la racha controla esto)
        ya_activo_hoy = gami.racha_actividad_fecha == date.today()
        gami.actualizar_racha_actividad()

        celebracion = {
            'negocio_id': negocio_id,
            'evento': 'login_diario',
            'xp_ganado': 0, 'tukoins_ganados': 0,
            'subio_nivel': False, 'misiones': [], 'badges_nuevos': [],
            'racha_dias': gami.racha_actividad_dias,
            'racha_record': False,
        }

        if not ya_activo_hoy:
            nivel_antes = gami.nivel
            cfg = _xp_eventos().get('login_diario', {'xp': 5, 'tukoins': 1})
            gami.agregar_xp(cfg['xp'], "Login diario")
            gami.agregar_tukoins(cfg['tukoins'], "Login diario", db_session=db.session)
            celebracion['xp_ganado'] = cfg['xp']
            celebracion['tukoins_ganados'] = cfg['tukoins']
            nivel_actual, nombre_nivel = gami.calcular_nivel()
            celebracion['nivel_nuevo'] = nivel_actual
            celebracion['nombre_nivel'] = nombre_nivel
            celebracion['subio_nivel'] = nivel_actual > nivel_antes

        # ¿Nuevo récord de racha?
        if gami.racha_actividad_dias > record_antes and gami.racha_actividad_dias >= 3:
            celebracion['racha_record'] = True

        db.session.commit()

        # Notificaciones
        if not ya_activo_hoy and celebracion['subio_nivel']:
            _emitir_notificaciones(negocio_id, celebracion)
        if celebracion['racha_record']:
            user_id = _owner_user_id(negocio_id)
            _crear_notif(
                negocio_id, user_id, 'racha_record',
                f"🔥 ¡Racha de {gami.racha_actividad_dias} días!",
                "Nuevo récord de actividad. ¡No la rompas!",
                extra={'dias': gami.racha_actividad_dias},
            )
            try:
                db.session.commit()
            except Exception:
                db.session.rollback()

        return celebracion

    except Exception as e:
        logger.error(f"[gamif] Error en on_login negocio {negocio_id}: {e}", exc_info=True)
        try:
            db.session.rollback()
        except Exception:
            pass
        return None


# Recompensa por completar el onboarding (S40)
XP_ONBOARDING = 150
TUKOINS_ONBOARDING = 50


def on_onboarding_completado(negocio_id):
    """
    Se dispara cuando el negocio termina el onboarding guiado (S40).
    Idempotente: solo recompensa la PRIMERA vez. Otorga XP (con multiplicador
    de evento especial), TuKoins y desbloquea el badge "Setup Completo".
    A prueba de fallos. Retorna celebracion o None.
    """
    if not negocio_id:
        return None
    try:
        from src.models.colombia_data.ratings.negocio_gamificacion import (
            NegocioGamificacion, multiplicador_xp
        )
        gami = NegocioGamificacion.obtener_o_crear(negocio_id, db.session)

        # Idempotencia: si ya estaba completado, no recompensa de nuevo
        if gami.onboarding_completado:
            return {
                'negocio_id': negocio_id, 'evento': 'onboarding_completado',
                'ya_completado': True, 'xp_ganado': 0, 'tukoins_ganados': 0,
                'subio_nivel': False, 'misiones': [], 'badges_nuevos': [],
            }

        nivel_antes = gami.nivel
        xp_mult = multiplicador_xp()
        xp_final = XP_ONBOARDING * xp_mult

        gami.onboarding_completado = True
        gami.agregar_xp(xp_final, "Onboarding completado")
        gami.agregar_tukoins(TUKOINS_ONBOARDING, "Onboarding completado", db_session=db.session)

        nivel_actual, nombre_nivel = gami.calcular_nivel()
        celebracion = {
            'negocio_id': negocio_id,
            'evento': 'onboarding_completado',
            'ya_completado': False,
            'xp_ganado': xp_final,
            'tukoins_ganados': TUKOINS_ONBOARDING,
            'subio_nivel': nivel_actual > nivel_antes,
            'nivel_nuevo': nivel_actual,
            'nombre_nivel': nombre_nivel,
            'misiones': [],
            'badges_nuevos': [],
        }

        db.session.commit()

        # Verifica/otorga el badge "Setup Completo" (ya hay flag persistido)
        celebracion['badges_nuevos'] = _verificar_badges_seguro(negocio_id)

        # Notificaciones (nivel + badges)
        try:
            _emitir_notificaciones(negocio_id, celebracion)
        except Exception:
            pass

        return celebracion

    except Exception as e:
        logger.error(f"[gamif] Error en on_onboarding_completado negocio {negocio_id}: {e}", exc_info=True)
        try:
            db.session.rollback()
        except Exception:
            pass
        return None
