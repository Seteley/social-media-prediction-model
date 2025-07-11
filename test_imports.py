#!/usr/bin/env python3
"""
Test simple para encontrar problemas de importación
"""

print("Testing imports step by step...")

try:
    print("1. Testing fastapi...")
    from fastapi import FastAPI
    print("✅ FastAPI OK")
except Exception as e:
    print(f"❌ FastAPI error: {e}")
    exit(1)

try:
    print("2. Testing auth_routes...")
    from app.api import auth_routes
    print("✅ auth_routes OK")
except Exception as e:
    print(f"❌ auth_routes error: {e}")

try:
    print("3. Testing clustering...")
    from app.api import clustering
    print("✅ clustering OK")
except Exception as e:
    print(f"❌ clustering error: {e}")

try:
    print("4. Testing regression...")
    from app.api import regression
    print("✅ regression OK")
except Exception as e:
    print(f"❌ regression error: {e}")

try:
    print("5. Testing routes_regression...")
    from app.api import routes_regression
    print("✅ routes_regression OK")
except Exception as e:
    print(f"❌ routes_regression error: {e}")

try:
    print("6. Testing routes_cluster...")
    from app.api import routes_cluster
    print("✅ routes_cluster OK")
except Exception as e:
    print(f"❌ routes_cluster error: {e}")

try:
    print("7. Testing crud routes...")
    from app.api.routes_crud import router as crud_router
    print("✅ crud_router OK")
except Exception as e:
    print(f"❌ crud_router error: {e}")

try:
    print("8. Testing full app...")
    from app.main import app
    print("✅ app imported successfully!")
    print(f"App type: {type(app)}")
except Exception as e:
    print(f"❌ app import error: {e}")
    import traceback
    traceback.print_exc()

print("Done!")
