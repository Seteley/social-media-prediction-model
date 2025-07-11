from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import pickle
import joblib
from pathlib import Path
import numpy as np
import pandas as pd
from datetime import datetime
from app.api.schemas_regression import (
    RegressionRequest, RegressionResponse, 
    PredictionRequest, PredictionResponse
)

router = APIRouter()

# --- Config ---
MODEL_BASE_PATH = Path("models")

@router.get("/predict/{username}", response_model=PredictionResponse)
def predict_single_get(username: str, fecha: str):
    """
    Realiza una predicción de regresión usando una fecha.
    
    Parámetros:
    - fecha: Fecha en formato YYYY-MM-DD (ej: 2025-07-11)
      Automáticamente extrae dia_semana, mes y asume hora=23
      Ejemplo: /predict/Interbank?fecha=2028-07-11
    """
    model_path = MODEL_BASE_PATH / username / "regresion.pkl"
    
    if not model_path.exists():
        raise HTTPException(
            status_code=404, 
            detail=f"Regression model for user {username} not found."
        )
    
    try:
        # Cargar modelo
        with open(model_path, "rb") as f:
            model_data = joblib.load(f)
        
        model = model_data['model']
        feature_names = model_data['feature_names']
        target_variable = model_data['target_variable']
        
        # Procesar fecha
        from datetime import datetime
        try:
            fecha_obj = datetime.strptime(fecha, "%Y-%m-%d")
            # Extraer componentes temporales
            dia_semana_calc = fecha_obj.weekday()  # 0=Lunes, 6=Domingo
            mes_calc = fecha_obj.month  # 1-12
            hora_calc = 23  # Fin del día por defecto
            
            input_features = {
                'dia_semana': dia_semana_calc,
                'hora': hora_calc,
                'mes': mes_calc
            }
            
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail="Formato de fecha inválido. Use YYYY-MM-DD (ej: 2025-07-11)"
            )
        
        # Verificar que todas las features requeridas estén disponibles
        missing_features = [f for f in feature_names if f not in input_features]
        
        if missing_features:
            raise HTTPException(
                status_code=400,
                detail=f"Features requeridas no disponibles: {missing_features}. Modelo requiere: {feature_names}"
            )
        
        # Preparar input usando solo las features que el modelo necesita
        input_array = np.array([[input_features[f] for f in feature_names]])
        
        # Realizar predicción
        prediction = model.predict(input_array)[0]
        
        # Respuesta simplificada - solo lo esencial
        return {
            "prediction": float(prediction),
            "model_type": type(model).__name__,
            "target_variable": target_variable
        }
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Prediction error: {str(e)}")

@router.post("/predict-batch", response_model=RegressionResponse)
def predict_regression_batch(req: RegressionRequest):
    """Realiza predicciones múltiples de regresión usando el modelo entrenado para un usuario."""
    model_path = MODEL_BASE_PATH / req.username / "regresion.pkl"
    
    if not model_path.exists():
        raise HTTPException(
            status_code=404, 
            detail=f"Regression model for user {req.username} not found."
        )
    
    try:
        # Cargar modelo
        with open(model_path, "rb") as f:
            model_data = joblib.load(f)
        
        model = model_data['model']
        feature_names = model_data['feature_names']
        target_variable = model_data['target_variable']
        
        # Preparar datos
        if isinstance(req.data[0], dict):
            # Si son diccionarios, convertir a DataFrame
            df = pd.DataFrame(req.data)
            
            # Usar solo las features que el modelo conoce
            missing_features = [f for f in feature_names if f not in df.columns]
            if missing_features:
                raise HTTPException(
                    status_code=400,
                    detail=f"Missing features: {missing_features}. Required: {feature_names}"
                )
            
            X = df[feature_names].fillna(0)
        else:
            # Si son listas, asumir que están en el orden correcto
            X = np.array(req.data)
            if X.shape[1] != len(feature_names):
                raise HTTPException(
                    status_code=400,
                    detail=f"Expected {len(feature_names)} features, got {X.shape[1]}"
                )
        
        # Realizar predicción
        predictions = model.predict(X)
        
        return RegressionResponse(
            predictions=predictions.tolist(),
            model_type=type(model).__name__,
            target_variable=target_variable
        )
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Prediction error: {str(e)}")



@router.get("/model-info/{username}")
def get_model_info(username: str):
    """Obtiene información del modelo de regresión guardado."""
    model_path = MODEL_BASE_PATH / username / "regresion.pkl"
    
    if not model_path.exists():
        raise HTTPException(
            status_code=404, 
            detail=f"Regression model for user {username} not found."
        )
    
    try:
        with open(model_path, "rb") as f:
            model_data = joblib.load(f)
        
        return {
            "username": model_data['account_name'],
            "target_variable": model_data['target_variable'],
            "model_type": type(model_data['model']).__name__,
            "feature_names": model_data['feature_names'],
            "model_id": model_data.get('model_id', 'unknown'),
            "timestamp": model_data.get('timestamp', 'unknown'),
            "results_count": len(model_data.get('results', []))
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading model info: {str(e)}")

@router.get("/features/{username}")
def get_required_features(username: str):
    """Obtiene las features requeridas para hacer predicciones con el modelo."""
    model_path = MODEL_BASE_PATH / username / "regresion.pkl"
    
    if not model_path.exists():
        raise HTTPException(
            status_code=404, 
            detail=f"Regression model for user {username} not found."
        )
    
    try:
        with open(model_path, "rb") as f:
            model_data = joblib.load(f)
        
        return {
            "username": username,
            "required_features": model_data['feature_names'],
            "target_variable": model_data['target_variable'],
            "model_type": type(model_data['model']).__name__,
            "example_url": f"/regression/predict/{username}?" + "&".join([f"{f}=0.0" for f in model_data['feature_names'][:3]]) + "..."
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading model features: {str(e)}")
