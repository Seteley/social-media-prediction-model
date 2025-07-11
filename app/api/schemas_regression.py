from pydantic import BaseModel
from typing import List, Optional, Dict, Any

class RegressionRequest(BaseModel):
    username: str
    data: List[Dict[str, Any]]  # List of dicts with features
    features: Optional[List[str]] = None  # Optional: feature names

class RegressionResponse(BaseModel):
    predictions: List[float]
    model_type: str
    target_variable: str
    confidence_intervals: Optional[List[Dict[str, float]]] = None

class TrainRegressionRequest(BaseModel):
    username: str
    data: Optional[List[Dict[str, Any]]] = None  # Optional: if not provided, loads from DuckDB
    target_variable: Optional[str] = "seguidores"  # Default target
    test_size: Optional[float] = 0.2
    random_state: Optional[int] = 42

class TrainRegressionResponse(BaseModel):
    message: str
    best_model: str
    metrics: Dict[str, Any]
    model_path: str
    target_variable: str
    features_used: List[str]
    training_samples: int
    test_samples: int

class ModelMetricsResponse(BaseModel):
    account_name: str
    target_variable: str
    best_model: Dict[str, Any]
    all_results: List[Dict[str, Any]]
    feature_count: int
    features_used: List[str]
    training_samples: int
    test_samples: int
    timestamp: str

class PredictionRequest(BaseModel):
    username: str
    input_data: Dict[str, Any]  # Single input for prediction

class PredictionResponse(BaseModel):
    prediction: float
    model_type: str
    target_variable: str
