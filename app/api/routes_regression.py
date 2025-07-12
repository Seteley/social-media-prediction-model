from fastapi import APIRouter, HTTPException, Depends, Query
from pathlib import Path
import json
import duckdb
import pandas as pd
import sys
from typing import Dict, Any
from app.api.schemas_regression import (
    TrainRegressionRequest, TrainRegressionResponse, ModelMetricsResponse
)
from app.auth.dependencies import auth_required
from app.auth.auth_service import auth_service
import ast

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

@router.get("/users",
    responses={
        200: {"description": "Lista de usuarios con modelos obtenida exitosamente"},
        401: {"description": "Token inválido, expirado o no proporcionado"}
    }
)
def list_users(current_user: Dict[str, Any] = Depends(auth_required)):
    """
    Lista los usuarios con modelos de regresión disponibles.
    
    **Requiere:** Token JWT válido
    
    **Códigos de respuesta:**
    - 200: Lista obtenida exitosamente  
    - 401: Sin autenticación (token faltante, inválido o expirado)
    """
    if not MODEL_BASE_PATH.exists():
        return []
    
    users = []
    for user_dir in MODEL_BASE_PATH.iterdir():
        if user_dir.is_dir() and (user_dir / "regresion.pkl").exists():
            users.append(user_dir.name)
    
    return users

@router.get("/available-accounts",
    responses={
        200: {"description": "Lista de cuentas disponibles obtenida exitosamente"},
        401: {"description": "Token inválido, expirado o no proporcionado"},
        500: {"description": "Error interno del servidor"}
    }
)
def list_available_accounts(current_user: Dict[str, Any] = Depends(auth_required)):
    """
    Lista todas las cuentas disponibles en la base de datos.
    
    **Requiere:** Token JWT válido
    
    **Códigos de respuesta:**
    - 200: Lista obtenida exitosamente
    - 401: Sin autenticación (token faltante, inválido o expirado)
    - 500: Error interno del servidor
    """
    try:
        if not verify_database():
            raise HTTPException(status_code=500, detail="Verificación de base de datos falló")
        
        accounts = get_available_accounts()
        return {"accounts": accounts, "total": len(accounts)}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error obteniendo cuentas: {str(e)}")

@router.get("/metrics/{username}", 
    response_model=ModelMetricsResponse,
    responses={
        200: {"description": "Métricas del modelo obtenidas exitosamente"},
        401: {"description": "Token inválido, expirado o no proporcionado"},
        403: {"description": "Sin acceso a la cuenta solicitada"},
        404: {"description": "Métricas no encontradas"},
        500: {"description": "Error interno del servidor"}
    }
)
def get_model_metrics(
    username: str,
    current_user: Dict[str, Any] = Depends(auth_required)
):
    """
    Obtiene las métricas del modelo de regresión de un usuario.
    
    **Requiere:** Token JWT válido y acceso a la cuenta
    
    **Códigos de respuesta:**
    - 200: Métricas obtenidas exitosamente
    - 401: Sin autenticación (token faltante, inválido o expirado)
    - 403: Sin acceso a la cuenta (empresa diferente)
    - 404: Métricas no encontradas
    - 500: Error interno
    """
    # Verificar acceso a la cuenta
    if not auth_service.user_has_access_to_account(current_user['empresa_id'], username):
        raise HTTPException(
            status_code=403,
            detail=f"No tiene acceso a la cuenta @{username}"
        )
    
    metrics_path = METRICAS_PATH / f"{username}.json"
    
    if not metrics_path.exists():
        raise HTTPException(
            status_code=404, 
            detail=f"Métricas para el usuario @{username} no encontradas."
        )
    
    try:
        with open(metrics_path, 'r', encoding='utf-8') as f:
            metrics_data = json.load(f)
        
        return ModelMetricsResponse(**metrics_data)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error cargando métricas: {str(e)}")

@router.get("/history/{username}",
    responses={
        200: {"description": "Historial de entrenamientos obtenido exitosamente"},
        401: {"description": "Token inválido, expirado o no proporcionado"},
        403: {"description": "Sin acceso a la cuenta solicitada"},
        404: {"description": "Historial no encontrado"},
        500: {"description": "Error interno del servidor"}
    }
)
def get_model_history(
    username: str,
    current_user: Dict[str, Any] = Depends(auth_required)
):
    """
    Obtiene el historial de entrenamientos para un usuario.
    
    **Requiere:** Token JWT válido y acceso a la cuenta
    
    **Códigos de respuesta:**
    - 200: Historial obtenido exitosamente
    - 401: Sin autenticación (token faltante, inválido o expirado)
    - 403: Sin acceso a la cuenta (empresa diferente)
    - 404: Historial no encontrado
    - 500: Error interno
    """
    # Verificar acceso a la cuenta
    if not auth_service.user_has_access_to_account(current_user['empresa_id'], username):
        raise HTTPException(
            status_code=403,
            detail=f"No tiene acceso a la cuenta @{username}"
        )
    
    metrics_path = METRICAS_PATH / f"{username}.json"
    
    if not metrics_path.exists():
        raise HTTPException(
            status_code=404, 
            detail=f"No se encontró historial de entrenamientos para @{username}."
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
        raise HTTPException(status_code=500, detail=f"Error cargando historial: {str(e)}")

@router.get("/train/{username}", 
    response_model=TrainRegressionResponse,
    responses={
        200: {"description": "Modelo entrenado exitosamente"},
        401: {"description": "Token inválido, expirado o no proporcionado"},
        403: {"description": "Sin acceso a la cuenta solicitada"},
        404: {"description": "Usuario no encontrado"},
        500: {"description": "Error interno en el entrenamiento"}
    }
)
def train_regression_model(
    username: str,
    target_variable: str = Query("seguidores", description="Variable objetivo"),
    metric_weights: str = Query(None, description="Pesos para métricas en formato JSON, ej: {'R²':0.5,'RMSE':0.3,'MAE':0.2}"),
    current_user: Dict[str, Any] = Depends(auth_required)
):
    """
    Entrena modelos de regresión para una cuenta y selecciona el mejor modelo según score compuesto si se especifican pesos.
    Permite personalizar la importancia de cada métrica.
    """
    # Verificar acceso a la cuenta
    if not auth_service.user_has_access_to_account(current_user['empresa_id'], username):
        raise HTTPException(
            status_code=403,
            detail=f"No tiene acceso a la cuenta @{username}"
        )
    
    try:
        # Validar que la cuenta existe
        available_accounts = get_available_accounts()
        if username not in available_accounts:
            raise HTTPException(
                status_code=404, 
                detail=f"Cuenta @{username} no encontrada. Disponibles: {available_accounts}"
            )

        print(f"🚀 Training regression model for {username}")
        print(f"🎯 Target variable: {target_variable}")
        
        # 1. Cargar datos
        data_loader = AccountDataLoader()
        data_dict = data_loader.load_account_data(username)
        
        if not data_dict or 'combined' not in data_dict:
            raise HTTPException(
                status_code=404, 
                detail=f"No se encontraron datos para la cuenta @{username}"
            )
        
        data = data_dict['combined']
        print(f"📊 Data loaded: {len(data)} records")
        
        # 2. Preprocesar datos
        preprocessor = AccountPreprocessor(username, target_variable)
        processed_data, feature_names = preprocessor.process_account_data(data)
        
        if processed_data is None or len(processed_data) == 0:
            raise HTTPException(
                status_code=400, 
                detail=f"Error en el preprocesamiento de datos para @{username}"
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
                detail=f"Error en el entrenamiento de modelos para @{username}"
            )

        # 4. Obtener información del mejor modelo
        best_model_info = report.get('best_model', {})
        best_model_weighted = None
        weights = None
        if metric_weights:
            try:
                weights = ast.literal_eval(metric_weights)
                best_model_weighted = model.get_best_model_weighted(weights)
            except Exception as e:
                raise HTTPException(status_code=400, detail=f"Error en los pesos de métricas: {e}")

        model_path = f"models/{username}/regresion.pkl"

        # Si se usaron pesos, devolver ambos resultados
        if best_model_weighted:
            return TrainRegressionResponse(
                message=f"Modelo de regresión entrenado exitosamente para @{username} (score compuesto)",
                best_model=best_model_weighted.get('model_name', 'Unknown'),
                metrics={
                    "score_compuesto": best_model_weighted.get('score_compuesto', 0),
                    **best_model_weighted.get('metricas', {})
                },
                model_path=model_path,
                target_variable=target_variable,
                features_used=report.get('features_used', []),
                training_samples=report.get('training_samples', 0),
                test_samples=report.get('test_samples', 0)
            )
        else:
            return TrainRegressionResponse(
                message=f"Modelo de regresión entrenado exitosamente para @{username}",
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
        raise HTTPException(status_code=500, detail=f"Error de entrenamiento: {str(e)}")



@router.delete("/model/{username}",
    responses={
        200: {"description": "Modelo eliminado exitosamente"},
        401: {"description": "Token inválido, expirado o no proporcionado"},
        403: {"description": "Sin acceso a la cuenta solicitada"},
        404: {"description": "Modelo no encontrado"}
    }
)
def delete_model(
    username: str,
    current_user: Dict[str, Any] = Depends(auth_required)
):
    """
    Elimina el modelo y métricas de un usuario.
    
    **Requiere:** Token JWT válido y acceso a la cuenta
    
    **Códigos de respuesta:**
    - 200: Modelo eliminado exitosamente
    - 401: Sin autenticación (token faltante, inválido o expirado)
    - 403: Sin acceso a la cuenta (empresa diferente)
    - 404: Modelo no encontrado
    """
    # Verificar acceso a la cuenta
    if not auth_service.user_has_access_to_account(current_user['empresa_id'], username):
        raise HTTPException(
            status_code=403,
            detail=f"No tiene acceso a la cuenta @{username}"
        )
    
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
            detail=f"No se encontró modelo o métricas para @{username}"
        )
    
    return {
        "message": f"Modelo eliminado para @{username}",
        "deleted_files": deleted_files
    }

@router.get("/compare-models/{username}",
    responses={
        200: {"description": "Comparación de modelos obtenida exitosamente"},
        401: {"description": "Token inválido, expirado o no proporcionado"},
        403: {"description": "Sin acceso a la cuenta solicitada"},
        404: {"description": "Datos de comparación no encontrados"},
        500: {"description": "Error interno del servidor"}
    }
)
def compare_models(
    username: str,
    current_user: Dict[str, Any] = Depends(auth_required)
):
    """
    Compara todos los modelos entrenados para un usuario.
    
    **Requiere:** Token JWT válido y acceso a la cuenta
    
    **Códigos de respuesta:**
    - 200: Comparación obtenida exitosamente
    - 401: Sin autenticación (token faltante, inválido o expirado)
    - 403: Sin acceso a la cuenta (empresa diferente)
    - 404: Datos de comparación no encontrados
    - 500: Error interno
    """
    # Verificar acceso a la cuenta
    if not auth_service.user_has_access_to_account(current_user['empresa_id'], username):
        raise HTTPException(
            status_code=403,
            detail=f"No tiene acceso a la cuenta @{username}"
        )
    
    metrics_path = METRICAS_PATH / f"{username}.json"
    
    if not metrics_path.exists():
        raise HTTPException(
            status_code=404, 
            detail=f"No se encontraron datos de comparación para @{username}"
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
        raise HTTPException(status_code=500, detail=f"Error comparando modelos: {str(e)}")
