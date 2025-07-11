# =============================================================================
# PAQUETE SCRIPTS - MODELOS DE REGRESIÓN POR CUENTA INDIVIDUAL
# =============================================================================

"""
Paquete especializado para modelos de regresión por cuenta individual de Twitter/X.

Versión 3.0 - Enfoque en predicción de seguidores usando base DuckDB.

MÓDULOS PRINCIPALES:
- config: Configuración de regresión y conexión a base de datos
- data_loader: Carga de datos desde DuckDB por cuenta
- preprocessing: Preprocesamiento para regresión
- regression_models: Modelos ML especializados en seguidores
- run_individual: Script principal para análisis por cuenta

CARACTERÍSTICAS:
✅ Análisis individual por cuenta
✅ Variable objetivo: número de seguidores
✅ 8 algoritmos de machine learning
✅ Guardado automático de modelos y reportes
✅ CLI completa con validaciones
"""

__version__ = "3.0.0"
__author__ = "Social Media Analytics Team"
✅ Optimización automática de parámetros
✅ Múltiples métricas de evaluación
✅ Deduplicación avanzada
✅ Visualizaciones comprehensivas
✅ Compatibilidad con scripts existentes

USO BÁSICO:
    from scripts.clustering_hybrid import HybridClusteringAnalyzer
    
    analyzer = HybridClusteringAnalyzer()
    results = analyzer.run_clustering_analysis('BCPComunica')

USO AVANZADO:
    from scripts import MultiAccountDataLoader, HybridClusteringAnalyzer
    
    loader = MultiAccountDataLoader()
    analyzer = HybridClusteringAnalyzer()
    results = analyzer.compare_accounts(['BCPComunica', 'bbva_peru'])
"""

# Información del paquete
__version__ = "2.0.0"
__author__ = "Social Media Analytics Team"
__description__ = "Optimized scripts for social media data analysis"
__status__ = "Production Ready"

# Importaciones principales
from .config import PROJECT_CONFIG, MODELS_CONFIG, CONFIG_INFO
from .data_loader import MultiAccountDataLoader
from .preprocessing import MultiAccountDataPreprocessor
from .clustering_hybrid import HybridClusteringAnalyzer, run_kmeans_clustering, run_dbscan_clustering
from .regression_models import RegressionAnalyzer
from .visualization import VisualizationManager

# Pipeline principal (opcional)
try:
    from .main_pipeline import TwitterAnalysisPipeline
    PIPELINE_AVAILABLE = True
except ImportError:
    PIPELINE_AVAILABLE = False

# Lista de exportaciones públicas
__all__ = [
    # Clases principales
    'HybridClusteringAnalyzer',
    'MultiAccountDataLoader', 
    'MultiAccountDataPreprocessor',
    'RegressionAnalyzer',
    'VisualizationManager',
    
    # Configuración
    'PROJECT_CONFIG',
    'MODELS_CONFIG', 
    'CONFIG_INFO',
    
    # Funciones de utilidad
    'run_kmeans_clustering',
    'run_dbscan_clustering',
]

# Agregar pipeline si está disponible
if PIPELINE_AVAILABLE:
    __all__.append('TwitterAnalysisPipeline')

def get_module_info():
    """
    Devuelve información detallada sobre los módulos disponibles.
    
    Returns:
        dict: Información de módulos
    """
    info = {
        'version': __version__,
        'modules': {
            'clustering_hybrid': 'Análisis de clustering híbrido con optimización automática',
            'config': 'Configuración centralizada del proyecto',
            'data_loader': 'Carga de datos multi-cuenta y multi-archivo', 
            'preprocessing': 'Preprocesamiento avanzado con deduplicación',
            'regression_models': 'Modelos de ML para predicción',
            'visualization': 'Visualizaciones profesionales',
            'main_pipeline': 'Pipeline principal integrado' if PIPELINE_AVAILABLE else 'No disponible'
        },
        'status': __status__,
        'features': [
            'Soporte multi-cuenta nativo',
            'Optimización automática de parámetros',
            'Múltiples métricas de evaluación',
            'Deduplicación avanzada de tweets',
            'Visualizaciones comprehensivas',
            'Compatibilidad con scripts existentes'
        ]
    }
    return info

def print_info():
    """Imprime información del paquete."""
    info = get_module_info()
    print(f"📦 {__description__}")
    print(f"🔖 Versión: {info['version']}")
    print(f"📊 Estado: {info['status']}")
    print("\n🔧 Módulos disponibles:")
    for module, description in info['modules'].items():
        status = "✅" if description != "No disponible" else "❌"
        print(f"   {status} {module}: {description}")
    print("\n⭐ Características:")
    for feature in info['features']:
        print(f"   • {feature}")

# Verificación de integridad al importar
def _verify_installation():
    """Verifica que todos los módulos principales estén disponibles."""
    required_modules = ['config', 'data_loader', 'preprocessing', 'clustering_hybrid']
    missing = []
    
    for module in required_modules:
        try:
            __import__(f'scripts.{module}', fromlist=[''])
        except ImportError:
            missing.append(module)
    
    if missing:
        print(f"⚠️  Módulos faltantes: {', '.join(missing)}")
        return False
    return True

# Ejecutar verificación al importar
_INSTALLATION_OK = _verify_installation()

if not _INSTALLATION_OK:
    print("❌ Instalación incompleta del paquete scripts")

# Solo mostrar info si se importa directamente
if __name__ == "__main__":
    print_info()
