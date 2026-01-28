"""
Colombia Data - Modelos de Datos Colombia
TuKomercio Suite
"""

print("=" * 60)
print("🇨🇴 COLOMBIA_DATA __INIT__.PY: INICIANDO CARGA")
print("=" * 60)

# ==========================================
# IMPORTS CON LOGS
# ==========================================

try:
    print("🔄 [1/7] Importando Feedback...")
    from .colombia_feedbacks import Feedback
    print("✅ [1/7] Feedback importado")
except Exception as e:
    print(f"❌ [1/7] Error importando Feedback: {e}")
    raise

try:
    print("🔄 [2/7] Importando MonetizationManagement...")
    from .monetization_management import MonetizationManagement
    print("✅ [2/7] MonetizationManagement importado")
except Exception as e:
    print(f"❌ [2/7] Error importando MonetizationManagement: {e}")
    raise

try:
    print("🔄 [3/7] Importando Colombia...")
    from .colombia_data import Colombia
    print("✅ [3/7] Colombia importado")
except Exception as e:
    print(f"❌ [3/7] Error importando Colombia: {e}")
    raise

try:
    print("🔄 [4/7] Importando NegocioPerfilConfig...")
    from .negocio_perfil_config import NegocioPerfilConfig
    print("✅ [4/7] NegocioPerfilConfig importado")
except Exception as e:
    print(f"❌ [4/7] Error importando NegocioPerfilConfig: {e}")
    raise

try:
    print("🔄 [5/7] Importando NegocioVideo...")
    from .negocio_video import NegocioVideo
    print("✅ [5/7] NegocioVideo importado")
except Exception as e:
    print(f"❌ [5/7] Error importando NegocioVideo: {e}")
    raise

try:
    print("🔄 [6/7] Importando Negocio...")
    from .negocio import Negocio
    print("✅ [6/7] Negocio importado")
except Exception as e:
    print(f"❌ [6/7] Error importando Negocio: {e}")
    raise

try:
    print("🔄 [7/7] Importando Sucursal...")
    from .sucursales import Sucursal
    print("✅ [7/7] Sucursal importado")
except Exception as e:
    print(f"❌ [7/7] Error importando Sucursal: {e}")
    raise

__all__ = [
    'Feedback',
    'MonetizationManagement',
    'Colombia',
    'NegocioPerfilConfig',
    'NegocioVideo',
    'Negocio',
    'Sucursal'
]

print("=" * 60)
print("🇨🇴 COLOMBIA_DATA __INIT__.PY: CARGA COMPLETADA")
print(f"🇨🇴 Modelos exportados: {__all__}")
print("=" * 60)