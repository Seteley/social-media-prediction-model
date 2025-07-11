#!/usr/bin/env python3
"""
Script para agregar gradualmente los routers y encontrar el problema
"""

from fastapi import FastAPI
import sys
import os

# Agregar directorio actual al path
sys.path.insert(0, os.getcwd())

print("🔍 DIAGNÓSTICO GRADUAL DE ROUTERS")
print("=" * 50)

app = FastAPI(
    title="Social Media Analytics API - Gradual Test",
    description="Testing routers one by one",
    version="3.0.0-test"
)

@app.get("/")
def root():
    return {"message": "Base app working"}

# Test 1: Auth routes
try:
    print("1️⃣  Probando auth_routes...")
    from app.api import auth_routes
    app.include_router(auth_routes.router, tags=["Autenticación"])
    print("✅ auth_routes agregado exitosamente")
except Exception as e:
    print(f"❌ Error con auth_routes: {e}")

# Test 2: Clustering
try:
    print("2️⃣  Probando clustering...")
    from app.api import clustering
    app.include_router(clustering.router, prefix="/clustering", tags=["Clustering"])
    print("✅ clustering agregado exitosamente")
except Exception as e:
    print(f"❌ Error con clustering: {e}")

# Test 3: Regression
try:
    print("3️⃣  Probando regression...")
    from app.api import regression
    app.include_router(regression.router, prefix="/regression", tags=["Regression"])
    print("✅ regression agregado exitosamente")
except Exception as e:
    print(f"❌ Error con regression: {e}")

# Test 4: Routes cluster
try:
    print("4️⃣  Probando routes_cluster...")
    from app.api import routes_cluster
    app.include_router(routes_cluster.router, prefix="/clustering", tags=["Clustering-Management"])
    print("✅ routes_cluster agregado exitosamente")
except Exception as e:
    print(f"❌ Error con routes_cluster: {e}")

# Test 5: Routes regression
try:
    print("5️⃣  Probando routes_regression...")
    from app.api import routes_regression
    app.include_router(routes_regression.router, prefix="/regression", tags=["Regression-Management"])
    print("✅ routes_regression agregado exitosamente")
except Exception as e:
    print(f"❌ Error con routes_regression: {e}")

# Test 6: CRUD routes
try:
    print("6️⃣  Probando routes_crud...")
    from app.api.routes_crud import router as crud_router
    app.include_router(crud_router)
    print("✅ routes_crud agregado exitosamente")
except Exception as e:
    print(f"❌ Error con routes_crud: {e}")

print("\n🚀 Iniciando servidor con routers que funcionan...")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000, reload=False)
