#!/usr/bin/env python3
"""
Script simple para diagnosticar problemas de importación
"""

import sys
import traceback

print("🔍 DIAGNÓSTICO DE IMPORTACIÓN")
print("=" * 50)

# Test 1: Imports básicos
try:
    import uvicorn
    print("✅ uvicorn importado correctamente")
except Exception as e:
    print(f"❌ Error importando uvicorn: {e}")

try:
    import fastapi
    print("✅ fastapi importado correctamente")
except Exception as e:
    print(f"❌ Error importando fastapi: {e}")

try:
    import duckdb
    print("✅ duckdb importado correctamente")
except Exception as e:
    print(f"❌ Error importando duckdb: {e}")

# Test 2: Importar app
print("\n🔍 Probando importación de app...")
try:
    from app.main import app
    print("✅ app.main importado correctamente")
    print(f"📄 Tipo de app: {type(app)}")
except Exception as e:
    print(f"❌ Error importando app.main:")
    print(f"   {type(e).__name__}: {e}")
    traceback.print_exc()

# Test 3: Imports específicos del proyecto
print("\n🔍 Probando imports específicos...")

try:
    from app.auth.auth_service import auth_service
    print("✅ auth_service importado correctamente")
except Exception as e:
    print(f"❌ Error importando auth_service: {e}")

try:
    from app.auth.dependencies import auth_required
    print("✅ auth_required importado correctamente")
except Exception as e:
    print(f"❌ Error importando auth_required: {e}")

try:
    from app.api.regression import router as regression_router
    print("✅ regression router importado correctamente")
except Exception as e:
    print(f"❌ Error importando regression router: {e}")

print("\n🔍 Verificando archivos...")
import os
files_to_check = [
    "app/__init__.py",
    "app/main.py",
    "app/auth/__init__.py",
    "app/auth/auth_service.py",
    "app/auth/dependencies.py",
    "app/api/__init__.py",
    "app/api/regression.py"
]

for file_path in files_to_check:
    if os.path.exists(file_path):
        print(f"✅ {file_path} existe")
    else:
        print(f"❌ {file_path} NO existe")

print("\n✅ Diagnóstico completado")
