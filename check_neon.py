# -*- coding: utf-8 -*-
from run import create_app
from src.models.database import db
from sqlalchemy import inspect

app = create_app()
with app.app_context():
    inspector = inspect(db.engine)
    tablas = inspector.get_table_names()
    print(f"✅ Conexión exitosa a la rama de Neon.")
    print(f"📊 Tablas encontradas: {tablas}")
    
    if 'usuario' in tablas:
        # Intentar contar cuántos usuarios hay
        from sqlalchemy import text
        result = db.session.execute(text("SELECT count(*) FROM usuario")).scalar()
        print(f"👤 Usuarios registrados actualmente: {result}")