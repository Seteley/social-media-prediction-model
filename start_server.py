#!/usr/bin/env python3
"""
Script directo para iniciar la API sin problemas de terminal
"""

import sys
import os

# Agregar directorio actual al path
sys.path.insert(0, os.getcwd())

try:
    print("🚀 Iniciando servidor...")
    
    # Test import primero
    print("📦 Probando imports...")
    from app.main import app
    print("✅ App importada correctamente")
    
    # Iniciar servidor
    import uvicorn
    print("🌐 Iniciando uvicorn en localhost:8000...")
    uvicorn.run(app, host="127.0.0.1", port=8000, reload=True)
    
except ImportError as e:
    print(f"❌ Error de importación: {e}")
    print("Ejecutando diagnóstico...")
    
    try:
        from app.api import auth_routes
        print("✅ auth_routes OK")
    except Exception as e2:
        print(f"❌ auth_routes: {e2}")
    
    try:
        from app.api import regression
        print("✅ regression OK")
    except Exception as e2:
        print(f"❌ regression: {e2}")
        
except Exception as e:
    print(f"❌ Error general: {e}")
    import traceback
    traceback.print_exc()
