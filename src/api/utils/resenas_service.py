"""
Servicio de moderación de reseñas a nivel plataforma (Admin Panel — Sprint A43).

Helpers PUROS para normalizar emails y detectar reseñas potencialmente
abusivas/falsas (heurística simple). La moderación real (aprobar/ocultar/banear)
vive en los endpoints admin.

© 2024-2026 Carlos Eduardo Huérfano Bermúdez. Todos los derechos reservados.
"""


def normalizar_email(email):
    """Normaliza un email para comparar baneos. Función PURA."""
    return (email or '').strip().lower()


def evaluar_resena_sospechosa(r):
    """
    Heurística simple para marcar reseñas a revisar. Función PURA.
    'r' = {rating, comentario, titulo, verificado}.
    Devuelve {sospechosa: bool, motivos: [str]}.
    """
    r = r or {}
    motivos = []
    try:
        rating = int(r.get('rating') or 0)
    except (TypeError, ValueError):
        rating = 0
    comentario = (r.get('comentario') or '').strip()
    verificado = bool(r.get('verificado'))

    if not verificado:
        motivos.append('no_verificada')
    if len(comentario) < 10:
        motivos.append('comentario_minimo')
    if rating in (1, 5) and len(comentario) < 10:
        motivos.append('extremo_sin_texto')
    if not (1 <= rating <= 5):
        motivos.append('rating_invalido')

    return {'sospechosa': len(motivos) > 0, 'motivos': motivos}
