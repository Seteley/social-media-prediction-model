from fastapi import FastAPI
from app.api import clustering, routes_cluster, regression, routes_regression, auth_routes
from app.api.routes_crud import router as crud_router

app = FastAPI(
    title="Social Media Analytics API",
    description="API para modelos de clustering y regresión de redes sociales con autenticación JWT",
    version="3.0.0"
)

# Rutas de autenticación (sin prefijo para facilidad de uso)
app.include_router(auth_routes.router, tags=["Autenticación"])

# Rutas de clustering (predicción)
app.include_router(clustering.router, prefix="/clustering", tags=["Clustering"])
# Rutas de gestión de modelos de clustering  
app.include_router(routes_cluster.router, prefix="/clustering", tags=["Clustering-Management"])

# Rutas de regresión (predicción) - AHORA PROTEGIDAS CON JWT
app.include_router(regression.router, prefix="/regression", tags=["Regression"])
# Rutas de gestión de modelos de regresión
app.include_router(routes_regression.router, prefix="/regression", tags=["Regression-Management"])

# Rutas CRUD genéricas
app.include_router(crud_router)

@app.get("/")
def root():
    return {
        "message": "Social Media Analytics API funcionando con autenticación JWT",
        "version": "3.0.0",
        "authentication": "JWT Bearer Token requerido para endpoints protegidos",
        "endpoints": {
            "auth": "/auth (login, registro, info)",
            "clustering": "/clustering",
            "regression": "/regression (🔒 PROTEGIDO)",
            "docs": "/docs"
        },
        "getting_started": {
            "1": "POST /auth/login para obtener token",
            "2": "Usar header: Authorization: Bearer <token>",
            "3": "Acceder a endpoints protegidos"
        }
    }
