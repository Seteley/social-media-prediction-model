from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
import pickle
from pathlib import Path
import numpy as np
import pandas as pd
from typing import Dict, Any
from app.auth.dependencies import auth_required
from app.auth.auth_service import auth_service

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
    current_user: Dict[str, Any] = Depends(auth_required)
):
    """
    Predicción de clustering con autenticación JWT y control de acceso por empresa
    
    **Requiere:** Token JWT válido y acceso a la cuenta
    
    Parámetros:
    - username: Nombre de la cuenta (debe pertenecer a tu empresa)
    - req: Datos para clustering en formato JSON
    
    **Headers requeridos:**
    - Authorization: Bearer {token_jwt}
    
    **Códigos de respuesta:**
    - 200: Clustering exitoso
    - 401: Sin autenticación (token faltante, inválido o expirado)
    - 403: Sin acceso a la cuenta (empresa diferente)
    - 404: Modelo no encontrado
    - 400: Error en datos de entrada
    
    **Ejemplos:**
    - Usuario admin_interbank puede acceder a username="Interbank"
    - Usuario admin_bcp puede acceder a username="BCPComunica"
    - Acceso cruzado devuelve 403 Forbidden
    """
    # Verificar acceso a la cuenta
    if not auth_service.user_has_access_to_account(current_user['empresa_id'], username):
        raise HTTPException(
            status_code=403,
            detail=f"No tiene acceso a la cuenta @{username}"
        )
    
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
