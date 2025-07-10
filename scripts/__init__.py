# =============================================================================
# PAQUETE SCRIPTS - TWITTRACK ANALYSIS
# =============================================================================

"""
Paquete de scripts para análisis de Machine Learning en datos de Twitter.

Este paquete contiene todos los módulos necesarios para realizar un análisis
completo de datos de engagement en Twitter, incluyendo:

- Carga y preprocesamiento de datos
- Análisis de clustering (K-Means, DBSCAN)
- Modelos de regresión (8 algoritmos)
- Visualizaciones profesionales
- Pipeline integrado

Módulos disponibles:
    - config: Configuración y constantes del proyecto
    - data_loader: Carga y consolidación de datos
    - preprocessing: Preprocesamiento y feature engineering
    - clustering: Análisis de clustering
    - regression_models: Modelos de regresión
    - visualization: Visualizaciones y gráficos
    - main_pipeline: Pipeline principal integrado

Uso rápido:
    >>> from scripts.main_pipeline import run_twitter_analysis
    >>> resultados = run_twitter_analysis(usuario_objetivo='interbank')

Versión: 1.0
Autor: Proyecto TwitTrack
Fecha: 2025
"""

# Información del paquete
__version__ = "1.0.0"
__author__ = "Proyecto TwitTrack"
__email__ = "twittrack@proyecto.edu"
__description__ = "Scripts de análisis de Machine Learning para datos de Twitter"

# Importaciones principales para acceso rápido
from .config import PROJECT_CONFIG, MODELS_CONFIG, CONFIG_INFO
from .main_pipeline import run_twitter_analysis, TwitterAnalysisPipeline

# Importaciones opcionales para uso avanzado
try:
    from .data_loader import load_and_prepare_data, DataLoader
    from .preprocessing import preprocess_twitter_data, DataPreprocessor
    from .clustering import perform_clustering_analysis, ClusteringAnalyzer
    from .regression_models import train_regression_models, RegressionAnalyzer
    from .visualization import create_comprehensive_visualizations, VisualizationManager
except ImportError as e:
    print(f"⚠️ Advertencia: Algunas dependencias no están disponibles: {e}")

# Lista de módulos exportados
__all__ = [
    # Principales
    'run_twitter_analysis',
    'TwitterAnalysisPipeline',
    'PROJECT_CONFIG',
    'MODELS_CONFIG',
    
    # Avanzados
    'load_and_prepare_data',
    'preprocess_twitter_data', 
    'perform_clustering_analysis',
    'train_regression_models',
    'create_comprehensive_visualizations',
    
    # Clases
    'DataLoader',
    'DataPreprocessor', 
    'ClusteringAnalyzer',
    'RegressionAnalyzer',
    'VisualizationManager'
]

def get_package_info():
    """
    Retorna información del paquete.
    
    Returns:
        dict: Información del paquete
    """
    return {
        'version': __version__,
        'author': __author__,
        'description': __description__,
        'modules': __all__,
        'config_loaded': bool(PROJECT_CONFIG),
        'dependencies_ok': True  # Se podría verificar dinámicamente
    }

def quick_analysis(usuario='interbank', target='likes'):
    """
    Función de conveniencia para análisis rápido.
    
    Args:
        usuario (str): Usuario objetivo
        target (str): Variable objetivo
        
    Returns:
        dict: Resultados del análisis
    """
    print(f"🚀 Iniciando análisis rápido para {usuario} prediciendo {target}")
    return run_twitter_analysis(usuario_objetivo=usuario, target_variable=target)

# Mensaje de bienvenida al importar el paquete
print("📦 Paquete TwitTrack Scripts cargado exitosamente")
print(f"   Versión: {__version__}")
print(f"   Módulos disponibles: {len(__all__)}")
print(f"   Uso rápido: run_twitter_analysis()")
