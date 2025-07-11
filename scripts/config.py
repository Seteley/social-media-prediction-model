# =============================================================================
# CONFIGURACIÓN PARA MODELOS DE REGRESIÓN POR CUENTA
# =============================================================================

"""
Configuración específica para modelos de regresión individuales por cuenta de Twitter.
Enfoque: Predicción basada en número de seguidores usando datos de base_de_datos.
"""

import os
import pandas as pd
import numpy as np
import warnings
import duckdb
from pathlib import Path

# Librerías de Machine Learning
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import (mean_squared_error, r2_score, mean_absolute_error,
                            median_absolute_error, explained_variance_score)

# Modelos de regresión
from sklearn.linear_model import LinearRegression, Ridge, Lasso
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.svm import SVR
from sklearn.neighbors import KNeighborsRegressor
from sklearn.tree import DecisionTreeRegressor

# Configuración de pandas y warnings
pd.set_option('display.max_columns', None)
pd.set_option('display.width', 1000)
warnings.filterwarnings('ignore')

print("✅ Configuración inicial completada")
print("📦 Librerías cargadas exitosamente")

# =============================================================================
# CONFIGURACIÓN DE LA BASE DE DATOS
# =============================================================================

DATABASE_CONFIG = {
    'path': 'data/base_de_datos/social_media.duckdb',
    'backup_path': 'data/base_de_datos/backup/',
    'scripts_path': 'data/base_de_datos/scripts/'
}

# =============================================================================
# CONFIGURACIÓN DE MODELOS DE REGRESIÓN
# =============================================================================

REGRESSION_MODELS = {
    'linear_regression': {
        'model': LinearRegression,
        'params': {},
        'description': 'Regresión Lineal Simple'
    },
    'ridge': {
        'model': Ridge,
        'params': {'alpha': 1.0, 'random_state': 42},
        'description': 'Regresión Ridge (L2)'
    },
    'lasso': {
        'model': Lasso,
        'params': {'alpha': 1.0, 'random_state': 42},
        'description': 'Regresión Lasso (L1)'
    },
    'random_forest': {
        'model': RandomForestRegressor,
        'params': {'n_estimators': 100, 'random_state': 42},
        'description': 'Random Forest'
    },
    'gradient_boosting': {
        'model': GradientBoostingRegressor,
        'params': {'n_estimators': 100, 'random_state': 42},
        'description': 'Gradient Boosting'
    },
    'svr': {
        'model': SVR,
        'params': {'kernel': 'rbf', 'C': 1.0},
        'description': 'Support Vector Regression'
    },
    'knn': {
        'model': KNeighborsRegressor,
        'params': {'n_neighbors': 5},
        'description': 'K-Nearest Neighbors'
    },
    'decision_tree': {
        'model': DecisionTreeRegressor,
        'params': {'random_state': 42},
        'description': 'Árbol de Decisión'
    }
}

# =============================================================================
# CONFIGURACIÓN DE EVALUACIÓN
# =============================================================================

EVALUATION_METRICS = {
    'rmse': lambda y_true, y_pred: np.sqrt(mean_squared_error(y_true, y_pred)),
    'mae': mean_absolute_error,
    'r2': r2_score,
    'explained_variance': explained_variance_score,
    'median_ae': median_absolute_error
}

# =============================================================================
# CONFIGURACIÓN DE FEATURES
# =============================================================================

TARGET_VARIABLE = 'seguidores'  # Variable objetivo: número de seguidores

FEATURE_CONFIG = {
    'publicaciones_features': [
        'respuestas', 'retweets', 'likes', 'guardados', 'vistas'
    ],
    'temporal_features': [
        'dia_semana', 'hora', 'mes'
    ],
    'derived_features': [
        'engagement_rate', 'total_interacciones', 'ratio_likes_vistas'
    ]
}

# =============================================================================
# CONFIGURACIÓN DE SALIDA
# =============================================================================

OUTPUT_CONFIG = {
    'metricas_dir': 'metricas/',          # Reportes JSON van aquí directamente
    'models_base_dir': 'models/',         # Base para carpetas por usuario  
    'model_filename': 'regresion.pkl',    # Nombre fijo del archivo del modelo
    'file_format': 'json'
}

# =============================================================================
# UTILIDADES DE BASE DE DATOS
# =============================================================================

def get_database_connection():
    """
    Obtiene conexión a la base de datos DuckDB.
    
    Returns:
        duckdb.Connection: Conexión a la base de datos
    """
    db_path = Path(DATABASE_CONFIG['path'])
    
    if not db_path.exists():
        raise FileNotFoundError(f"Base de datos no encontrada: {db_path}")
    
    return duckdb.connect(str(db_path))

def get_available_accounts():
    """
    Obtiene lista de cuentas disponibles en la base de datos.
    
    Returns:
        list: Lista de nombres de cuentas
    """
    try:
        conn = get_database_connection()
        
        query = """
        SELECT DISTINCT u.cuenta 
        FROM usuario u
        INNER JOIN publicaciones p ON u.id_usuario = p.id_usuario
        INNER JOIN metrica m ON u.id_usuario = m.id_usuario
        ORDER BY u.cuenta
        """
        
        result = conn.execute(query).fetchall()
        conn.close()
        
        return [row[0] for row in result]
        
    except Exception as e:
        print(f"❌ Error obteniendo cuentas: {e}")
        return []

def verify_database():
    """
    Verifica que la base de datos esté disponible y tenga datos.
    
    Returns:
        bool: True si la base de datos está OK
    """
    try:
        conn = get_database_connection()
        
        # Verificar tablas principales
        tables_query = "SHOW TABLES"
        tables = conn.execute(tables_query).fetchall()
        table_names = [table[0] for table in tables]
        
        required_tables = ['usuario', 'publicaciones', 'metrica']
        missing_tables = [t for t in required_tables if t not in table_names]
        
        if missing_tables:
            print(f"❌ Tablas faltantes: {missing_tables}")
            conn.close()
            return False
        
        # Verificar datos
        data_query = """
        SELECT COUNT(*) as total_records,
               COUNT(DISTINCT u.cuenta) as total_accounts
        FROM usuario u
        INNER JOIN publicaciones p ON u.id_usuario = p.id_usuario
        INNER JOIN metrica m ON u.id_usuario = m.id_usuario
        """
        
        result = conn.execute(data_query).fetchone()
        conn.close()
        
        total_records, total_accounts = result
        
        print(f"📊 Base de datos verificada:")
        print(f"   • Registros totales: {total_records}")
        print(f"   • Cuentas disponibles: {total_accounts}")
        
        return total_records > 0 and total_accounts > 0
        
    except Exception as e:
        print(f"❌ Error verificando base de datos: {e}")
        return False

# =============================================================================
# INFORMACIÓN DEL PROYECTO
# =============================================================================

PROJECT_INFO = {
    'name': 'Social Media Regression Models',
    'version': '3.0.0',
    'description': 'Modelos de regresión por cuenta individual basados en seguidores',
    'target': 'Predicción del número de seguidores',
    'data_source': 'DuckDB Database',
    'focus': 'Individual account analysis'
}

def print_project_info():
    """Imprime información del proyecto."""
    print(f"\n📋 {PROJECT_INFO['name']} v{PROJECT_INFO['version']}")
    print(f"🎯 {PROJECT_INFO['description']}")
    print(f"📊 Objetivo: {PROJECT_INFO['target']}")
    print(f"💾 Fuente: {PROJECT_INFO['data_source']}")
    print(f"🔍 Enfoque: {PROJECT_INFO['focus']}")

# =============================================================================
# UTILIDADES DE DIRECTORIOS Y ARCHIVOS
# =============================================================================

def get_user_model_dir(username: str) -> str:
    """
    Obtiene el directorio del modelo para un usuario específico.
    
    Args:
        username (str): Nombre de usuario/cuenta
        
    Returns:
        str: Ruta del directorio del modelo
    """
    import os
    model_dir = os.path.join(OUTPUT_CONFIG['models_base_dir'], username)
    os.makedirs(model_dir, exist_ok=True)
    return model_dir

def get_model_filepath(username: str) -> str:
    """
    Obtiene la ruta completa del archivo del modelo para un usuario.
    
    Args:
        username (str): Nombre de usuario/cuenta
        
    Returns:
        str: Ruta completa del archivo del modelo
    """
    import os
    model_dir = get_user_model_dir(username)
    return os.path.join(model_dir, OUTPUT_CONFIG['model_filename'])

def get_metrics_filepath(username: str) -> str:
    """
    Obtiene la ruta del archivo de métricas para un usuario.
    
    Args:
        username (str): Nombre de usuario/cuenta
        
    Returns:
        str: Ruta del archivo de métricas JSON
    """
    import os
    os.makedirs(OUTPUT_CONFIG['metricas_dir'], exist_ok=True)
    return os.path.join(OUTPUT_CONFIG['metricas_dir'], f"{username}.json")

def ensure_output_directories():
    """Asegura que existan los directorios de salida."""
    import os
    os.makedirs(OUTPUT_CONFIG['metricas_dir'], exist_ok=True)
    os.makedirs(OUTPUT_CONFIG['models_base_dir'], exist_ok=True)

# Verificar base de datos al importar
if __name__ == "__main__":
    print_project_info()
    
    if verify_database():
        accounts = get_available_accounts()
        print(f"✅ Cuentas disponibles: {accounts}")
    else:
        print("❌ Problemas con la base de datos")
else:
    # Verificación silenciosa al importar
    try:
        _db_ok = verify_database()
    except:
        _db_ok = False
