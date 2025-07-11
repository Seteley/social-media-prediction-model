from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import pickle
from pathlib import Path
import numpy as np
import pandas as pd

router = APIRouter()

# --- Config ---
MODEL_BASE_PATH = Path("models")

class ClusteringRequest(BaseModel):
    username: str
    data: list  # List of dicts or list of lists (features)
    features: list = None  # Optional: feature names

class ClusteringResponse(BaseModel):
    labels: list
    n_clusters: int
    model_type: str

@router.post("/predict", response_model=ClusteringResponse)
def predict_clustering(req: ClusteringRequest):
    model_path = MODEL_BASE_PATH / req.username / "clustering.pkl"
    if not model_path.exists():
        raise HTTPException(status_code=404, detail=f"Model for user {req.username} not found.")
    # Load model
    with open(model_path, "rb") as f:
        model = pickle.load(f)
    # Prepare data
    X = np.array(req.data)
    # Predict
    try:
        labels = model.predict(X)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Prediction error: {str(e)}")
    n_clusters = len(set(labels))
    model_type = type(model).__name__
    return ClusteringResponse(labels=labels.tolist(), n_clusters=n_clusters, model_type=model_type)
