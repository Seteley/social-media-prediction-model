from fastapi import APIRouter, HTTPException
from pathlib import Path
import json
import duckdb
import pandas as pd
from app.api.schemas_cluster import TrainClusteringRequest, TrainClusteringResponse
import importlib.util
import sys
MODELS_PATH = Path(__file__).resolve().parents[2] / "models"
sys.path.append(str(MODELS_PATH))
spec = importlib.util.spec_from_file_location("Mejor2Clustering", str(MODELS_PATH / "Mejor2Clustering.py"))
Mejor2Clustering = importlib.util.module_from_spec(spec)
spec.loader.exec_module(Mejor2Clustering)
HybridClusteringAnalyzer = Mejor2Clustering.HybridClusteringAnalyzer

router = APIRouter()
MODEL_BASE_PATH = Path("models")
DB_PATH = Path("data/base_de_datos/social_media.duckdb")

@router.get("/users")
def list_users():
    """Lista los usuarios con modelos de clustering disponibles."""
    if not MODEL_BASE_PATH.exists():
        return []
    return [d.name for d in MODEL_BASE_PATH.iterdir() if d.is_dir() and (d/"clustering.pkl").exists()]

@router.get("/model-info/{username}")
def model_info(username: str):
    """Devuelve metadatos del modelo de clustering de un usuario."""
    if not DB_PATH.exists():
        raise HTTPException(status_code=404, detail="DuckDB database not found.")
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
        raise HTTPException(status_code=404, detail="No model found for user.")
    tipo_modelo, parametros, fecha_entrenamiento, archivo_modelo, evaluacion = row
    return {
        "tipo_modelo": tipo_modelo,
        "parametros": json.loads(parametros),
        "fecha_entrenamiento": str(fecha_entrenamiento),
        "archivo_modelo": archivo_modelo,
        "evaluacion": json.loads(evaluacion)
    }

@router.get("/metrics/{username}")
def model_metrics(username: str):
    """Devuelve las métricas de evaluación del modelo de clustering de un usuario."""
    if not DB_PATH.exists():
        raise HTTPException(status_code=404, detail="DuckDB database not found.")
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
        raise HTTPException(status_code=404, detail="No model found for user.")
    return json.loads(row[0])

@router.get("/history/{username}")
def model_history(username: str):
    """Devuelve el historial de modelos entrenados para un usuario."""
    if not DB_PATH.exists():
        raise HTTPException(status_code=404, detail="DuckDB database not found.")
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
@router.get("/train/{username}", response_model=TrainClusteringResponse)
def train_clustering_duckdb(username: str):
    """Entrena o reentrena el modelo de clustering para un usuario usando los datos de DuckDB."""
    analyzer = HybridClusteringAnalyzer()
    # Carga automática desde DuckDB
    df = analyzer.load_account_data(username)
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

# Endpoint para obtener clusters y ejemplos de contenido usando el modelo guardado
@router.get("/clusters/{username}")
def get_clusters_content(username: str):
    """Devuelve los clusters y ejemplos de contenido usando el modelo pkl guardado."""
    import pickle
    model_path = MODEL_BASE_PATH / username / "clustering.pkl"
    if not model_path.exists():
        raise HTTPException(status_code=404, detail="Modelo no encontrado para el usuario.")
    # Cargar modelo
    with open(model_path, "rb") as f:
        model = pickle.load(f)
    analyzer = HybridClusteringAnalyzer()
    df = analyzer.load_account_data(username)
    features = ["engagement_rate", "vistas"]
    # Calcular métricas de engagement si no existen
    if "engagement_rate" not in df.columns or "vistas" not in df.columns:
        df = analyzer.calculate_engagement_metrics(df)
    X = df[features].fillna(0).values
    # Escalar los datos igual que en entrenamiento
    from sklearn.preprocessing import StandardScaler
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    # Predecir clusters
    try:
        labels = model.predict(X_scaled)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error al predecir clusters: {str(e)}")
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

# (El resto del archivo ya está correcto y limpio. No hay duplicados ni bloques mal indentados.)
