# src/api/profile/__init__.py
"""
BizFlow Studio - Profile API Module
"""

import logging
logger = logging.getLogger(__name__)

print("=" * 60)
print("📸 PROFILE MODULE: INICIANDO CARGA...")
print("=" * 60)

# ==========================================
# AVATAR API
# ==========================================
try:
    print("📸 [1/2] Intentando cargar avatar_api...")
    from .avatar_api import avatar_api_bp
    print("✅ [1/2] avatar_api_bp cargado correctamente")
except Exception as e:
    print(f"❌ [1/2] Error cargando avatar_api: {e}")
    import traceback
    traceback.print_exc()

# ==========================================
# PERFIL PÚBLICO NEGOCIO API
# ==========================================
try:
    print("📸 [2/2] Intentando cargar perfil_publico_negocio_api...")
    from .perfil_publico_negocio_api import perfil_publico_negocio_bp
    print("✅ [2/2] perfil_publico_negocio_bp cargado correctamente")
except Exception as e:
    print(f"❌ [2/2] Error cargando perfil_publico_negocio_api: {e}")
    import traceback
    traceback.print_exc()

print("=" * 60)
print("📸 PROFILE MODULE: CARGA COMPLETADA")
print("=" * 60)