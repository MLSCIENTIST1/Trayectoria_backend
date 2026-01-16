# src/api/profile/__init__.py
"""
BizFlow Studio - Profile API Module
"""

import logging
logger = logging.getLogger(__name__)

print("📸 PROFILE MODULE: Cargando...")

try:
    from .avatar_api import avatar_api_bp
    print("✅ avatar_api_bp cargado correctamente")
except Exception as e:
    print(f"❌ Error cargando avatar_api: {e}")
    import traceback
    traceback.print_exc()

print("📸 PROFILE MODULE: Completado")