from fastapi import FastAPI
from app.api import clustering, routes_cluster, regression, routes_regression
from app.api.routes_crud import router as crud_router

app = FastAPI(
    title="Social Media Analytics API",
    description="API para modelos de clustering y regresión de redes sociales",
    version="3.0.0"
)


# Rutas de clustering (predicción)
app.include_router(clustering.router, prefix="/clustering", tags=["Clustering"])
# Rutas de gestión de modelos de clustering  
app.include_router(routes_cluster.router, prefix="/clustering", tags=["Clustering-Management"])

# Rutas de regresión (predicción)
app.include_router(regression.router, prefix="/regression", tags=["Regression"])
# Rutas de gestión de modelos de regresión
app.include_router(routes_regression.router, prefix="/regression", tags=["Regression-Management"])

# Rutas CRUD genéricas
app.include_router(crud_router)

@app.get("/")
def root():
    return {
        "message": "Social Media Analytics API funcionando",
        "version": "3.0.0",
        "endpoints": {
            "clustering": "/clustering",
            "regression": "/regression",
            "docs": "/docs"
        }
    }
