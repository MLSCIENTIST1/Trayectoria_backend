# src/api/profile/__init__.py
"""
BizFlow Studio - Profile API Module
Debug: Logs para verificar carga del módulo
"""

import logging

logger = logging.getLogger(__name__)

print("=" * 50)
print("📸 PROFILE MODULE: __init__.py INICIANDO")
print("=" * 50)

logger.info("=" * 50)
logger.info("📸 PROFILE MODULE: __init__.py cargado")
logger.info("=" * 50)

# Intentar importar avatar_api para ver si hay error
try:
    print("📸 Intentando importar avatar_api...")
    logger.info("📸 Intentando importar avatar_api...")
    
    from .avatar_api import avatar_api_bp
    
    print("✅ avatar_api_bp importado correctamente")
    logger.info("✅ avatar_api_bp importado correctamente")
    
except ImportError as e:
    print(f"❌ ImportError en avatar_api: {e}")
    logger.error(f"❌ ImportError en avatar_api: {e}")
    import traceback
    traceback.print_exc()
    
except Exception as e:
    print(f"❌ Error general en avatar_api: {e}")
    logger.error(f"❌ Error general en avatar_api: {e}")
    import traceback
    traceback.print_exc()

print("📸 PROFILE MODULE: __init__.py COMPLETADO")
logger.info("📸 PROFILE MODULE: __init__.py completado")