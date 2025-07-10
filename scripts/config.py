# =============================================================================
# CONFIGURACIÓN INICIAL Y LIBRERÍAS
# =============================================================================

"""
Configuración inicial del proyecto de análisis de engagement en Twitter.
Este módulo contiene todas las importaciones y configuraciones globales necesarias.
"""

import os
import glob
import pandas as pd
import numpy as np
import warnings

# Librerías de visualización
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.colors import ListedColormap

# Librerías de Machine Learning
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import (mean_squared_error, r2_score, silhouette_score, 
                           mean_absolute_error, median_absolute_error, 
                           explained_variance_score)

# Modelos de regresión
from sklearn.linear_model import LinearRegression, Ridge, Lasso
from sklearn.tree import DecisionTreeRegressor
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.neural_network import MLPRegressor
import xgboost as xgb

# Modelos de clustering
from sklearn.cluster import KMeans, DBSCAN

def setup_global_config():
    """
    Configura todas las opciones globales del proyecto.
    
    Returns:
        dict: Diccionario con información de configuración
    """
    # Configuración de pandas
    pd.set_option('display.max_columns', None)
    pd.set_option('display.width', None)
    pd.set_option('display.max_colwidth', 50)

    # Configuración de matplotlib y seaborn
    plt.style.use('seaborn-v0_8')
    sns.set_palette("husl")
    plt.rcParams['figure.figsize'] = (12, 8)
    plt.rcParams['font.size'] = 12

    # Supresión de warnings innecesarios
    warnings.filterwarnings("ignore", category=FutureWarning)
    warnings.filterwarnings("ignore", category=UserWarning)
    warnings.filterwarnings("ignore", category=DeprecationWarning)

    # Configuración de numpy para reproducibilidad
    np.random.seed(42)
    
    config_info = {
        'pandas_configured': True,
        'matplotlib_configured': True,
        'warnings_suppressed': True,
        'random_seed': 42,
        'timestamp': pd.Timestamp.now()
    }
    
    print("✅ Configuración inicial completada")
    print("📦 Librerías cargadas exitosamente")
    
    return config_info

# Configuración automática al importar el módulo
CONFIG_INFO = setup_global_config()

# Lista de cuentas de bancos disponibles
CUENTAS_DISPONIBLES = [
    'Interbank',
    'BanBif', 
    'BancodelaNacion',
    'bcrpoficial',
    'BancoPichincha',
    'bbva_peru',
    'BCPComunica',
    'ScotiabankPE'
]

# Variables de configuración del proyecto
PROJECT_CONFIG = {
    'data_folder': 'data',
    'file_patterns': {
        'clean': '*_clean.csv',
        'metricas': '*_metricas.csv'
    },
    'cuentas_disponibles': CUENTAS_DISPONIBLES,
    'default_target_variable': 'likes',
    'features_base': ['respuestas', 'retweets', 'likes', 'guardados', 'vistas'],
    'test_size': 0.2,
    'random_state': 42,
    'cv_folds': 5,
    'analisis_modes': ['individual', 'comparativo', 'consolidado'],
    'default_mode': 'consolidado'
}

# Configuración de modelos
MODELS_CONFIG = {
    'clustering': {
        'kmeans': {
            'n_clusters': 3,
            'random_state': 42,
            'n_init': 10,
            'max_iter': 300
        },
        'dbscan': {
            'eps': 1.5,
            'min_samples': 5,
            'metric': 'euclidean'
        }
    },
    'regression': {
        'models': {
            'Linear Regression': LinearRegression(),
            'Ridge': Ridge(alpha=1.0, random_state=42),
            'Lasso': Lasso(alpha=1.0, random_state=42, max_iter=1000),
            'Decision Tree': DecisionTreeRegressor(random_state=42, max_depth=10),
            'Random Forest': RandomForestRegressor(n_estimators=100, random_state=42, n_jobs=-1),
            'Gradient Boosting': GradientBoostingRegressor(random_state=42, n_estimators=100),
            'XGBoost': xgb.XGBRegressor(random_state=42, n_estimators=100, verbosity=0),
            'MLP': MLPRegressor(hidden_layer_sizes=(100, 50), max_iter=500, random_state=42)
        }
    }
}

# Configuración de scoring
SCORING_CONFIG = {
    'weights': {
        'RMSE': -1,    # Negativo porque menor es mejor
        'R²': 1,       # Positivo porque mayor es mejor
        'MAE': -1,     # Negativo porque menor es mejor
        'CV_R²_mean': 1  # Positivo porque mayor es mejor
    },
    'score_weights': {
        'RMSE_norm': 0.3,
        'R²_norm': 0.3,
        'MAE_norm': 0.2,
        'CV_R²_mean_norm': 0.2
    }
}
