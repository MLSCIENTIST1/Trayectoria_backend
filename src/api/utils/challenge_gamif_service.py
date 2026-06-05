"""
Servicio de integración Challenges ↔ Gamificación (Admin Panel — Sprint A28).

Otorga XP + TuKoins del sistema de gamificación cuando:
  - una participación de challenge se APRUEBA (premio por participar), y
  - un challenge se FINALIZA (premio mayor al ganador = más votos entre aprobadas).

IDEMPOTENTE y a prueba de fallos:
  - challenge_participaciones.gamif_otorgado evita premiar dos veces la misma
    participación (aunque el admin alterne aprobar/rechazar/aprobar).
  - challenges.gamif_premiado evita premiar dos veces al ganador.
  - Todo va en try/except: si la gamificación falla, NO rompe la moderación.

© 2024-2026 Carlos Eduardo Huérfano Bermúdez. Todos los derechos reservados.
"""
import logging
from sqlalchemy import text as _t

logger = logging.getLogger(__name__)


def premiar_participacion_aprobada(db_session, participacion_id):
    """
    Premia (una sola vez) a un negocio cuya participación quedó 'aprobado'.
    Devuelve dict de recompensa o None si no aplica. No lanza.
    """
    try:
        from src.models.colombia_data.ratings.config_gamificacion import get_challenge_rewards
        from src.models.colombia_data.ratings.negocio_gamificacion import NegocioGamificacion

        row = db_session.execute(_t("""
            SELECT negocio_id, estado, COALESCE(gamif_otorgado, FALSE)
            FROM challenge_participaciones WHERE id = :id
        """), {'id': participacion_id}).fetchone()
        if not row:
            return None
        negocio_id, estado, otorgado = row[0], row[1], row[2]
        if estado != 'aprobado' or otorgado or not negocio_id:
            return None

        rw = get_challenge_rewards()
        gami = NegocioGamificacion.obtener_o_crear(negocio_id, db_session)
        if rw['xp_participar']:
            gami.agregar_xp(rw['xp_participar'], "Challenge: participación aprobada")
        if rw['tukoins_participar']:
            gami.agregar_tukoins(rw['tukoins_participar'], "Challenge: participación aprobada",
                                 db_session=db_session)
        db_session.execute(_t(
            "UPDATE challenge_participaciones SET gamif_otorgado = TRUE WHERE id = :id"),
            {'id': participacion_id})
        db_session.commit()
        return {'negocio_id': negocio_id, 'xp': rw['xp_participar'], 'tukoins': rw['tukoins_participar']}
    except Exception as e:
        logger.warning(f"[challenge-gamif] premio participación no crítico: {e}")
        try:
            db_session.rollback()
        except Exception:
            pass
        return None


def finalizar_y_premiar(db_session, challenge_id):
    """
    Marca el challenge como 'finalizado' y premia (una sola vez) al ganador
    (negocio con más votos entre participaciones aprobadas). Idempotente.
    Devuelve dict con el resultado. No lanza (salvo challenge inexistente → dict error).
    """
    from src.models.colombia_data.ratings.config_gamificacion import get_challenge_rewards
    from src.models.colombia_data.ratings.negocio_gamificacion import NegocioGamificacion

    ch = db_session.execute(_t("""
        SELECT estado, COALESCE(gamif_premiado, FALSE) FROM challenges WHERE id = :id
    """), {'id': challenge_id}).fetchone()
    if not ch:
        return {'success': False, 'error': 'Challenge no encontrado'}
    estado_antes, premiado = ch[0], ch[1]

    # Ganador = más votos entre participaciones aprobadas.
    win = db_session.execute(_t("""
        SELECT cp.negocio_id, COUNT(cv.id) AS votos
        FROM challenge_participaciones cp
        LEFT JOIN challenge_votos cv ON cv.participacion_id = cp.id
        WHERE cp.challenge_id = :id AND cp.estado = 'aprobado'
        GROUP BY cp.negocio_id
        ORDER BY votos DESC
        LIMIT 1
    """), {'id': challenge_id}).fetchone()

    db_session.execute(_t("UPDATE challenges SET estado = 'finalizado' WHERE id = :id"),
                       {'id': challenge_id})

    resultado = {'success': True, 'challenge_id': challenge_id,
                 'estado_antes': estado_antes, 'ya_premiado': bool(premiado),
                 'ganador': None}

    if not premiado and win and win[0]:
        nid, votos = win[0], win[1]
        rw = get_challenge_rewards()
        gami = NegocioGamificacion.obtener_o_crear(nid, db_session)
        if rw['xp_ganador']:
            gami.agregar_xp(rw['xp_ganador'], f"Challenge {challenge_id} ganado")
        if rw['tukoins_ganador']:
            gami.agregar_tukoins(rw['tukoins_ganador'], f"Challenge {challenge_id} ganado",
                                 db_session=db_session)
        db_session.execute(_t("UPDATE challenges SET gamif_premiado = TRUE WHERE id = :id"),
                           {'id': challenge_id})
        nombre = db_session.execute(_t(
            "SELECT nombre_negocio FROM negocios WHERE id_negocio = :nid"),
            {'nid': nid}).scalar()
        resultado['ganador'] = {'negocio_id': nid, 'nombre': nombre or f'#{nid}',
                                'votos': int(votos or 0),
                                'xp': rw['xp_ganador'], 'tukoins': rw['tukoins_ganador']}

    db_session.commit()
    return resultado
