from pydantic import BaseModel
from typing import List, Optional, Dict, Any

class TrainClusteringRequest(BaseModel):
    username: str
    data: List[Dict[str, Any]]  # List of dicts with features
    features: Optional[List[str]] = None
    auto_optimize: bool = True
    custom_params: Optional[Dict[str, Any]] = None

class TrainClusteringResponse(BaseModel):
    message: str
    best_model: str
    metrics: Dict[str, Any]
    model_path: str
