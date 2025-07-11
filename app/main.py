from fastapi import FastAPI
from app.api import clustering, routes_cluster

app = FastAPI(title="Clustering Model API")

# Rutas de clustering (predicción)
app.include_router(clustering.router, prefix="/clustering", tags=["Clustering"])
# Rutas de gestión de modelos de clustering
app.include_router(routes_cluster.router, prefix="/clustering", tags=["Clustering-Info"])

@app.get("/")
def root():
    return {"message": "API funcionando"}
