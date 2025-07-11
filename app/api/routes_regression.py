from fastapi import APIRouter, HTTPException
from pathlib import Path
import json
import duckdb
import pandas as pd
import sys
from app.api.schemas_regression import (
    TrainRegressionRequest, TrainRegressionResponse, ModelMetricsResponse
)

# Agregar path del proyecto para imports
PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(PROJECT_ROOT))

from scripts.data_loader import AccountDataLoader
from scripts.preprocessing import AccountPreprocessor
from scripts.regression_models import train_account_regression_model
from scripts.config import get_available_accounts, verify_database

router = APIRouter()

MODEL_BASE_PATH = Path("models")
METRICAS_PATH = Path("metricas")
DB_PATH = Path("data/base_de_datos/social_media.duckdb")

@router.get("/users")
def list_users():
    """Lista los usuarios con modelos de regresión disponibles."""
    if not MODEL_BASE_PATH.exists():
        return []
    
    users = []
    for user_dir in MODEL_BASE_PATH.iterdir():
        if user_dir.is_dir() and (user_dir / "regresion.pkl").exists():
            users.append(user_dir.name)
    
    return users

@router.get("/available-accounts")
def list_available_accounts():
    """Lista todas las cuentas disponibles en la base de datos."""
    try:
        if not verify_database():
            raise HTTPException(status_code=500, detail="Database verification failed")
        
        accounts = get_available_accounts()
        return {"accounts": accounts, "total": len(accounts)}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting accounts: {str(e)}")

@router.get("/metrics/{username}", response_model=ModelMetricsResponse)
def get_model_metrics(username: str):
    """Obtiene las métricas del modelo de regresión de un usuario."""
    metrics_path = METRICAS_PATH / f"{username}.json"
    
    if not metrics_path.exists():
        raise HTTPException(
            status_code=404, 
            detail=f"Metrics for user {username} not found."
        )
    
    try:
        with open(metrics_path, 'r', encoding='utf-8') as f:
            metrics_data = json.load(f)
        
        return ModelMetricsResponse(**metrics_data)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading metrics: {str(e)}")

@router.get("/history/{username}")
def get_model_history(username: str):
    """Obtiene el historial de entrenamientos para un usuario."""
    metrics_path = METRICAS_PATH / f"{username}.json"
    
    if not metrics_path.exists():
        raise HTTPException(
            status_code=404, 
            detail=f"No training history found for user {username}."
        )
    
    try:
        with open(metrics_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Extraer información histórica del reporte
        history = {
            "account_name": data.get("account_name", username),
            "target_variable": data.get("target_variable", "seguidores"),
            "last_training": data.get("timestamp", "unknown"),
            "best_model": data.get("best_model", {}),
            "total_models_tested": data.get("total_models", 0),
            "features_used": data.get("features_used", []),
            "performance_summary": {
                "best_r2": data.get("best_model", {}).get("r2_score", 0),
                "best_rmse": data.get("best_model", {}).get("rmse", 0),
                "best_mae": data.get("best_model", {}).get("mae", 0)
            }
        }
        
        return history
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading history: {str(e)}")

@router.get("/train/{username}", response_model=TrainRegressionResponse)
def train_regression_model(username: str, target_variable: str = "seguidores", test_size: float = 0.2, random_state: int = 42):
    """Entrena o reentrena el modelo de regresión para un usuario usando datos de DuckDB."""
    
    try:
        # Validar que la cuenta existe
        available_accounts = get_available_accounts()
        if username not in available_accounts:
            raise HTTPException(
                status_code=404, 
                detail=f"Account {username} not found. Available: {available_accounts}"
            )
        
        print(f"🚀 Training regression model for {username}")
        print(f"🎯 Target variable: {target_variable}")
        
        # 1. Cargar datos
        data_loader = AccountDataLoader()
        data_dict = data_loader.load_account_data(username)
        
        if not data_dict or 'combined' not in data_dict:
            raise HTTPException(
                status_code=400, 
                detail=f"No data found for account {username}"
            )
        
        data = data_dict['combined']
        print(f"📊 Data loaded: {len(data)} records")
        
        # 2. Preprocesar datos
        preprocessor = AccountPreprocessor(username, target_variable)
        processed_data, feature_names = preprocessor.process_account_data(data)
        
        if processed_data is None or len(processed_data) == 0:
            raise HTTPException(
                status_code=400, 
                detail=f"Error in data preprocessing for {username}"
            )
        
        print(f"🔧 Data preprocessed: {len(processed_data)} records, {len(feature_names)} features")
        
        # 3. Entrenar modelos
        model, report = train_account_regression_model(
            username, 
            processed_data, 
            target_variable, 
            save_model=True
        )
        
        if not report:
            raise HTTPException(
                status_code=500, 
                detail=f"Error training models for {username}"
            )
        
        # 4. Obtener información del mejor modelo
        best_model_info = report.get('best_model', {})
        model_path = f"models/{username}/regresion.pkl"
        
        return TrainRegressionResponse(
            message=f"Regression model trained successfully for {username}",
            best_model=best_model_info.get('model_name', 'Unknown'),
            metrics={
                "r2_score": best_model_info.get('r2_score', 0),
                "rmse": best_model_info.get('rmse', 0),
                "mae": best_model_info.get('mae', 0),
                "cv_r2": best_model_info.get('cv_r2', 0)
            },
            model_path=model_path,
            target_variable=target_variable,
            features_used=report.get('features_used', []),
            training_samples=report.get('training_samples', 0),
            test_samples=report.get('test_samples', 0)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Training error: {str(e)}")



@router.delete("/model/{username}")
def delete_model(username: str):
    """Elimina el modelo y métricas de un usuario."""
    model_path = MODEL_BASE_PATH / username / "regresion.pkl"
    metrics_path = METRICAS_PATH / f"{username}.json"
    
    deleted_files = []
    
    if model_path.exists():
        model_path.unlink()
        deleted_files.append(str(model_path))
    
    if metrics_path.exists():
        metrics_path.unlink()
        deleted_files.append(str(metrics_path))
    
    if not deleted_files:
        raise HTTPException(
            status_code=404, 
            detail=f"No model or metrics found for user {username}"
        )
    
    return {
        "message": f"Model deleted for user {username}",
        "deleted_files": deleted_files
    }

@router.get("/compare-models/{username}")
def compare_models(username: str):
    """Compara todos los modelos entrenados para un usuario."""
    metrics_path = METRICAS_PATH / f"{username}.json"
    
    if not metrics_path.exists():
        raise HTTPException(
            status_code=404, 
            detail=f"No model comparison data found for user {username}"
        )
    
    try:
        with open(metrics_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Extraer comparación de modelos
        all_results = data.get('all_results', [])
        best_model = data.get('best_model', {})
        
        # Ordenar por R² score descendente
        sorted_results = sorted(all_results, key=lambda x: x.get('R²', 0), reverse=True)
        
        return {
            "account_name": username,
            "target_variable": data.get('target_variable', 'seguidores'),
            "total_models": len(all_results),
            "best_model": best_model,
            "model_comparison": sorted_results,
            "features_used": data.get('features_used', [])
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error comparing models: {str(e)}")
