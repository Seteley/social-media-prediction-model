from fastapi import APIRouter, HTTPException, Depends
from pathlib import Path
import json
import duckdb
import pandas as pd
from typing import Dict, Any
from app.api.schemas_cluster import TrainClusteringRequest, TrainClusteringResponse
from app.auth.dependencies import auth_required
from app.auth.auth_service import auth_service
import importlib.util
import sys
import pickle
from sklearn.preprocessing import StandardScaler

MODELS_PATH = Path(__file__).resolve().parents[2] / "models"
sys.path.append(str(MODELS_PATH))
spec = importlib.util.spec_from_file_location("Mejor2Clustering", str(MODELS_PATH / "Mejor2Clustering.py"))
Mejor2Clustering = importlib.util.module_from_spec(spec)
spec.loader.exec_module(Mejor2Clustering)
HybridClusteringAnalyzer = Mejor2Clustering.HybridClusteringAnalyzer

router = APIRouter()
MODEL_BASE_PATH = Path("models")
DB_PATH = Path("data/base_de_datos/social_media.duckdb")

@router.get("/users",
    responses={
        200: {"description": "Lista de usuarios con modelos obtenida exitosamente"},
        401: {"description": "Token inválido, expirado o no proporcionado"}
    }
)
def list_users(current_user: Dict[str, Any] = Depends(auth_required)):
    """
    Lista los usuarios con modelos de clustering disponibles.
    
    **Requiere:** Token JWT válido
    
    **Códigos de respuesta:**
    - 200: Lista obtenida exitosamente  
    - 401: Sin autenticación (token faltante, inválido o expirado)
    """
    if not MODEL_BASE_PATH.exists():
        return []
    return [d.name for d in MODEL_BASE_PATH.iterdir() if d.is_dir() and (d/"clustering.pkl").exists()]

@router.get("/model-info/{username}",
    responses={
        200: {"description": "Información del modelo obtenida exitosamente"},
        401: {"description": "Token inválido, expirado o no proporcionado"},
        403: {"description": "Sin acceso a la cuenta solicitada"},
        404: {"description": "Modelo o base de datos no encontrada"}
    }
)
def model_info(username: str, current_user: Dict[str, Any] = Depends(auth_required)):
    """
    Devuelve metadatos del modelo de clustering de un usuario.
    
    **Requiere:** Token JWT válido y acceso a la cuenta
    
    **Códigos de respuesta:**
    - 200: Información obtenida exitosamente
    - 401: Sin autenticación (token faltante, inválido o expirado)
    - 403: Sin acceso a la cuenta (empresa diferente)
    - 404: Modelo o base de datos no encontrada
    """
    # Verificar acceso a la cuenta
    if not auth_service.user_has_access_to_account(current_user['empresa_id'], username):
        raise HTTPException(
            status_code=403,
            detail=f"No tiene acceso a la cuenta @{username}"
        )
    
    if not DB_PATH.exists():
        raise HTTPException(status_code=404, detail="Base de datos DuckDB no encontrada.")
    
    con = duckdb.connect(str(DB_PATH))
    row = con.execute("""
        SELECT tipo_modelo, parametros, fecha_entrenamiento, archivo_modelo, evaluacion
        FROM modelo m
        JOIN usuario u ON m.id_usuario = u.id_usuario
        WHERE u.cuenta = ?
        ORDER BY fecha_entrenamiento DESC, m.id_modelo DESC
        LIMIT 1
    """, [username]).fetchone()
    con.close()
    
    if not row:
        raise HTTPException(status_code=404, detail="No se encontró modelo para el usuario.")
    
    tipo_modelo, parametros, fecha_entrenamiento, archivo_modelo, evaluacion = row
    return {
        "tipo_modelo": tipo_modelo,
        "parametros": json.loads(parametros),
        "fecha_entrenamiento": str(fecha_entrenamiento),
        "archivo_modelo": archivo_modelo,
        "evaluacion": json.loads(evaluacion)
    }

@router.get("/metrics/{username}",
    responses={
        200: {"description": "Métricas del modelo obtenidas exitosamente"},
        401: {"description": "Token inválido, expirado o no proporcionado"},
        403: {"description": "Sin acceso a la cuenta solicitada"},
        404: {"description": "Modelo o base de datos no encontrada"}
    }
)
def model_metrics(username: str, current_user: Dict[str, Any] = Depends(auth_required)):
    """
    Devuelve las métricas de evaluación del modelo de clustering de un usuario.
    
    **Requiere:** Token JWT válido y acceso a la cuenta
    
    **Códigos de respuesta:**
    - 200: Métricas obtenidas exitosamente
    - 401: Sin autenticación (token faltante, inválido o expirado)
    - 403: Sin acceso a la cuenta (empresa diferente)
    - 404: Modelo o base de datos no encontrada
    """
    # Verificar acceso a la cuenta
    if not auth_service.user_has_access_to_account(current_user['empresa_id'], username):
        raise HTTPException(
            status_code=403,
            detail=f"No tiene acceso a la cuenta @{username}"
        )
    
    if not DB_PATH.exists():
        raise HTTPException(status_code=404, detail="Base de datos DuckDB no encontrada.")
    
    con = duckdb.connect(str(DB_PATH))
    row = con.execute("""
        SELECT evaluacion
        FROM modelo m
        JOIN usuario u ON m.id_usuario = u.id_usuario
        WHERE u.cuenta = ?
        ORDER BY fecha_entrenamiento DESC, m.id_modelo DESC
        LIMIT 1
    """, [username]).fetchone()
    con.close()
    
    if not row:
        raise HTTPException(status_code=404, detail="No se encontró modelo para el usuario.")
    
    return json.loads(row[0])

@router.get("/history/{username}",
    responses={
        200: {"description": "Historial de modelos obtenido exitosamente"},
        401: {"description": "Token inválido, expirado o no proporcionado"},
        403: {"description": "Sin acceso a la cuenta solicitada"},
        404: {"description": "Modelo o base de datos no encontrada"}
    }
)
def model_history(username: str, current_user: Dict[str, Any] = Depends(auth_required)):
    """
    Devuelve el historial de modelos entrenados para un usuario.
    
    **Requiere:** Token JWT válido y acceso a la cuenta
    
    **Códigos de respuesta:**
    - 200: Historial obtenido exitosamente
    - 401: Sin autenticación (token faltante, inválido o expirado)
    - 403: Sin acceso a la cuenta (empresa diferente)
    - 404: Modelo o base de datos no encontrada
    """
    # Verificar acceso a la cuenta
    if not auth_service.user_has_access_to_account(current_user['empresa_id'], username):
        raise HTTPException(
            status_code=403,
            detail=f"No tiene acceso a la cuenta @{username}"
        )
    
    if not DB_PATH.exists():
        raise HTTPException(status_code=404, detail="Base de datos DuckDB no encontrada.")
    
    con = duckdb.connect(str(DB_PATH))
    rows = con.execute("""
        SELECT tipo_modelo, parametros, fecha_entrenamiento, archivo_modelo, evaluacion
        FROM modelo m
        JOIN usuario u ON m.id_usuario = u.id_usuario
        WHERE u.cuenta = ?
        ORDER BY fecha_entrenamiento DESC, m.id_modelo DESC
    """, [username]).fetchall()
    con.close()
    
    history = []
    for row in rows:
        tipo_modelo, parametros, fecha_entrenamiento, archivo_modelo, evaluacion = row
        history.append({
            "tipo_modelo": tipo_modelo,
            "parametros": json.loads(parametros),
            "fecha_entrenamiento": str(fecha_entrenamiento),
            "archivo_modelo": archivo_modelo,
            "evaluacion": json.loads(evaluacion)
        })
    return history


# Nuevo endpoint GET para entrenar usando datos de DuckDB
@router.get("/train/{username}", 
    response_model=TrainClusteringResponse,
    responses={
        200: {"description": "Modelo entrenado exitosamente"},
        401: {"description": "Token inválido, expirado o no proporcionado"},
        403: {"description": "Sin acceso a la cuenta solicitada"},
        404: {"description": "Datos no encontrados para la cuenta"},
        400: {"description": "Error en el entrenamiento del modelo"}
    }
)
def train_clustering_duckdb(username: str, current_user: Dict[str, Any] = Depends(auth_required)):
    """
    Entrena o reentrena el modelo de clustering para un usuario usando los datos de DuckDB.
    
    **Requiere:** Token JWT válido y acceso a la cuenta
    
    **Códigos de respuesta:**
    - 200: Modelo entrenado exitosamente
    - 401: Sin autenticación (token faltante, inválido o expirado)
    - 403: Sin acceso a la cuenta (empresa diferente)
    - 404: Datos no encontrados para la cuenta
    - 400: Error en el entrenamiento del modelo
    """
    # Verificar acceso a la cuenta
    if not auth_service.user_has_access_to_account(current_user['empresa_id'], username):
        raise HTTPException(
            status_code=403,
            detail=f"No tiene acceso a la cuenta @{username}"
        )
    
    try:
        analyzer = HybridClusteringAnalyzer()
        # Carga automática desde DuckDB
        df = analyzer.load_account_data(username)
        
        if df.empty:
            raise HTTPException(
                status_code=404,
                detail=f"No se encontraron datos para la cuenta @{username}"
            )
        
        features = ["engagement_rate", "vistas"]
        results = analyzer.run_clustering_analysis(
            username=username,
            features=features,
            auto_optimize=True
        )
        analyzer.save_results(username)
        best_model = analyzer.select_best_model(results['evaluation'])
        metrics = results['evaluation'][best_model]
        model_path = str(Path("models") / username / "clustering.pkl")
        return TrainClusteringResponse(
            message=f"Modelo de clustering entrenado para {username}",
            best_model=best_model,
            metrics=metrics,
            model_path=model_path
        )
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Error al entrenar el modelo: {str(e)}"
        )

# Endpoint para obtener clusters y ejemplos de contenido usando el modelo guardado
@router.get("/clusters/{username}",
    responses={
        200: {"description": "Clusters y contenido obtenidos exitosamente"},
        401: {"description": "Token inválido, expirado o no proporcionado"},
        403: {"description": "Sin acceso a la cuenta solicitada"},
        404: {"description": "Modelo no encontrado para el usuario"},
        400: {"description": "Error al predecir clusters"}
    }
)
def get_clusters_content(username: str, current_user: Dict[str, Any] = Depends(auth_required)):
    """
    Devuelve los clusters y ejemplos de contenido usando el modelo pkl guardado.
    
    **Requiere:** Token JWT válido y acceso a la cuenta
    
    **Códigos de respuesta:**
    - 200: Clusters y contenido obtenidos exitosamente
    - 401: Sin autenticación (token faltante, inválido o expirado)
    - 403: Sin acceso a la cuenta (empresa diferente)
    - 404: Modelo no encontrado para el usuario
    - 400: Error al predecir clusters
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
            detail=f"Modelo no encontrado para el usuario @{username}."
        )
    
    try:
        # Cargar modelo
        with open(model_path, "rb") as f:
            model = pickle.load(f)
        
        analyzer = HybridClusteringAnalyzer()
        df = analyzer.load_account_data(username)
        
        if df.empty:
            raise HTTPException(
                status_code=404,
                detail=f"No se encontraron datos para la cuenta @{username}"
            )
        
        features = ["engagement_rate", "vistas"]
        
        # Calcular métricas de engagement si no existen
        if "engagement_rate" not in df.columns or "vistas" not in df.columns:
            df = analyzer.calculate_engagement_metrics(df)
        
        X = df[features].fillna(0).values
        
        # Escalar los datos igual que en entrenamiento
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        
        # Predecir clusters
        labels = model.predict(X_scaled)
        df["cluster"] = labels
        
        clusters = []
        for cluster_id in sorted(set(labels)):
            cluster_df = df[df["cluster"] == cluster_id]
            # Convertir cada fila a dict (incluyendo todas las columnas)
            publicaciones = cluster_df.to_dict(orient="records")
            clusters.append({
                "cluster": int(cluster_id),
                "publicaciones": publicaciones
            })
        return {"clusters": clusters}
        
    except Exception as e:
        raise HTTPException(
            status_code=400, 
            detail=f"Error al predecir clusters: {str(e)}"
        )
