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
- Análisis individual por cuenta
- Variable objetivo: número de seguidores
- 8 algoritmos de machine learning
- Guardado automático de modelos y reportes
- CLI completa con validaciones
"""

__version__ = "3.0.0"
__author__ = "Social Media Analytics Team"
__description__ = "Individual account regression models for follower prediction"

# Imports principales
try:
    from .config import (REGRESSION_MODELS, TARGET_VARIABLE, FEATURE_CONFIG, 
                        OUTPUT_CONFIG, PROJECT_INFO, print_project_info,
                        verify_database, get_available_accounts)
    
    from .data_loader import AccountDataLoader, MultiAccountLoader
    from .preprocessing import AccountPreprocessor, BatchPreprocessor
    from .regression_models import AccountRegressionModel, train_account_regression_model
    
    # Variables disponibles
    __all__ = [
        'REGRESSION_MODELS', 'TARGET_VARIABLE', 'FEATURE_CONFIG', 'OUTPUT_CONFIG',
        'PROJECT_INFO', 'print_project_info', 'verify_database', 'get_available_accounts',
        'AccountDataLoader', 'MultiAccountLoader',
        'AccountPreprocessor', 'BatchPreprocessor', 
        'AccountRegressionModel', 'train_account_regression_model'
    ]
    
    _imports_successful = True
    
except ImportError as e:
    print(f"⚠️  Advertencia: Error importando módulos: {e}")
    _imports_successful = False
    __all__ = []

def get_package_info():
    """
    Devuelve información del paquete.
    
    Returns:
        dict: Información del paquete
    """
    return {
        'name': 'scripts',
        'version': __version__,
        'description': __description__,
        'modules': __all__ if _imports_successful else [],
        'status': 'OK' if _imports_successful else 'Import Error'
    }

def print_package_info():
    """Imprime información del paquete."""
    info = get_package_info()
    print(f"\n📦 Paquete: {info['name']} v{info['version']}")
    print(f"📝 Descripción: {info['description']}")
    print(f"📊 Estado: {info['status']}")
    print(f"🔧 Módulos: {len(info['modules'])}")
    
    if info['modules']:
        print("📋 Módulos disponibles:")
        for module in info['modules'][:10]:  # Mostrar solo los primeros 10
            print(f"   • {module}")
        if len(info['modules']) > 10:
            print(f"   ... y {len(info['modules']) - 10} más")

if __name__ == "__main__":
    print_package_info()
    if _imports_successful:
        print_project_info()
    else:
        print("❌ Algunos módulos no se pudieron importar")
