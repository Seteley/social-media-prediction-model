from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
import pickle
from pathlib import Path
import numpy as np
import pandas as pd
from app.auth.dependencies import get_current_user

router = APIRouter()

# --- Config ---
MODEL_BASE_PATH = Path("models")

class ClusteringRequest(BaseModel):
    data: list  # List of dicts or list of lists (features)
    features: list = None  # Optional: feature names

class ClusteringResponse(BaseModel):
    labels: list
    n_clusters: int
    model_type: str

@router.post("/predict/{username}", 
    response_model=ClusteringResponse,
    responses={
        200: {"description": "Clustering realizado exitosamente"},
        401: {"description": "Token inválido, expirado o no proporcionado"},
        403: {"description": "Sin acceso a la cuenta solicitada"},
        404: {"description": "Modelo de clustering no encontrado"},
        400: {"description": "Error en los datos de entrada"}
    }
)
def predict_clustering(
    username: str,
    req: ClusteringRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Predicción de clustering con autenticación JWT y control de acceso por empresa
    
    **Códigos de respuesta:**
    - 200: Clustering exitoso
    - 401: Sin autenticación (token faltante, inválido o expirado)
    - 403: Sin acceso a la cuenta (empresa diferente)
    - 404: Modelo no encontrado
    - 400: Error en datos de entrada
    
    - Requiere autenticación JWT válida
    - Solo permite acceso a modelos de la misma empresa del usuario autenticado
    - username: cuenta de la empresa (ej: 'Interbank', 'BCP', etc.)
    """
    # Verificar acceso a la empresa
    from app.auth.dependencies import verify_company_access
    verify_company_access(current_user, username)
    
    model_path = MODEL_BASE_PATH / username / "clustering.pkl"
    if not model_path.exists():
        raise HTTPException(
            status_code=404, 
            detail=f"Modelo de clustering para {username} no encontrado."
        )
    
    # Load model
    with open(model_path, "rb") as f:
        model = pickle.load(f)
    
    # Prepare data
    X = np.array(req.data)
    
    # Predict
    try:
        labels = model.predict(X)
    except Exception as e:
        raise HTTPException(
            status_code=400, 
            detail=f"Error en predicción de clustering: {str(e)}"
        )
    
    n_clusters = len(set(labels))
    model_type = type(model).__name__
    
    return ClusteringResponse(
        labels=labels.tolist(), 
        n_clusters=n_clusters, 
        model_type=model_type
    )
