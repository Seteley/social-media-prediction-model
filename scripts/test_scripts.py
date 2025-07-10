# =============================================================================
# SCRIPT DE PRUEBA Y VALIDACIÓN
# =============================================================================

"""
Script para validar que todos los módulos se importan correctamente.
Ejecuta un test básico de funcionalidad de cada componente.
"""

import sys
import os

def test_imports():
    """
    Prueba que todos los módulos se puedan importar correctamente.
    """
    print("🧪 INICIANDO PRUEBAS DE IMPORTACIÓN")
    print("="*50)
    
    tests_passed = 0
    tests_total = 0
    
    # Test 1: Config
    try:
        from config import PROJECT_CONFIG, MODELS_CONFIG, CONFIG_INFO
        print("✅ config.py - Importación exitosa")
        print(f"   - Configuración de proyecto cargada: {bool(PROJECT_CONFIG)}")
        tests_passed += 1
    except Exception as e:
        print(f"❌ config.py - Error: {e}")
    tests_total += 1
    
    # Test 2: Data Loader
    try:
        from data_loader import DataLoader, load_and_prepare_data
        print("✅ data_loader.py - Importación exitosa")
        print(f"   - Clase DataLoader disponible: {DataLoader}")
        tests_passed += 1
    except Exception as e:
        print(f"❌ data_loader.py - Error: {e}")
    tests_total += 1
    
    # Test 3: Preprocessing
    try:
        from preprocessing import DataPreprocessor, preprocess_twitter_data
        print("✅ preprocessing.py - Importación exitosa")
        print(f"   - Clase DataPreprocessor disponible: {DataPreprocessor}")
        tests_passed += 1
    except Exception as e:
        print(f"❌ preprocessing.py - Error: {e}")
    tests_total += 1
    
    # Test 4: Clustering
    try:
        from clustering import ClusteringAnalyzer, perform_clustering_analysis
        print("✅ clustering.py - Importación exitosa")
        print(f"   - Clase ClusteringAnalyzer disponible: {ClusteringAnalyzer}")
        tests_passed += 1
    except Exception as e:
        print(f"❌ clustering.py - Error: {e}")
    tests_total += 1
    
    # Test 5: Regression Models
    try:
        from regression_models import RegressionAnalyzer, train_regression_models
        print("✅ regression_models.py - Importación exitosa")
        print(f"   - Clase RegressionAnalyzer disponible: {RegressionAnalyzer}")
        tests_passed += 1
    except Exception as e:
        print(f"❌ regression_models.py - Error: {e}")
    tests_total += 1
    
    # Test 6: Visualization
    try:
        from visualization import VisualizationManager, create_comprehensive_visualizations
        print("✅ visualization.py - Importación exitosa")
        print(f"   - Clase VisualizationManager disponible: {VisualizationManager}")
        tests_passed += 1
    except Exception as e:
        print(f"❌ visualization.py - Error: {e}")
    tests_total += 1
    
    # Test 7: Main Pipeline
    try:
        from main_pipeline import TwitterAnalysisPipeline, run_twitter_analysis
        print("✅ main_pipeline.py - Importación exitosa")
        print(f"   - Clase TwitterAnalysisPipeline disponible: {TwitterAnalysisPipeline}")
        tests_passed += 1
    except Exception as e:
        print(f"❌ main_pipeline.py - Error: {e}")
    tests_total += 1
    
    print(f"\n📊 RESUMEN DE PRUEBAS:")
    print(f"   • Pruebas pasadas: {tests_passed}/{tests_total}")
    print(f"   • Porcentaje de éxito: {tests_passed/tests_total*100:.1f}%")
    
    if tests_passed == tests_total:
        print("🎉 ¡TODAS LAS PRUEBAS PASARON! Scripts listos para usar.")
        return True
    else:
        print("⚠️ Algunas pruebas fallaron. Revisar dependencias.")
        return False

def test_basic_functionality():
    """
    Prueba funcionalidad básica sin ejecutar análisis completo.
    """
    print(f"\n🧪 PROBANDO FUNCIONALIDAD BÁSICA")
    print("="*50)
    
    try:
        # Test configuración
        from config import PROJECT_CONFIG
        print(f"✅ Variables de configuración: {len(PROJECT_CONFIG)} items")
        
        # Test instanciación de clases
        from data_loader import DataLoader
        loader = DataLoader()
        print(f"✅ DataLoader instanciado correctamente")
        
        from preprocessing import DataPreprocessor
        preprocessor = DataPreprocessor()
        print(f"✅ DataPreprocessor instanciado correctamente")
        
        from clustering import ClusteringAnalyzer
        cluster_analyzer = ClusteringAnalyzer()
        print(f"✅ ClusteringAnalyzer instanciado correctamente")
        
        from regression_models import RegressionAnalyzer
        regression_analyzer = RegressionAnalyzer()
        print(f"✅ RegressionAnalyzer instanciado correctamente")
        
        from visualization import VisualizationManager
        viz_manager = VisualizationManager()
        print(f"✅ VisualizationManager instanciado correctamente")
        
        from main_pipeline import TwitterAnalysisPipeline
        pipeline = TwitterAnalysisPipeline()
        print(f"✅ TwitterAnalysisPipeline instanciado correctamente")
        
        print(f"\n🎉 TODAS LAS CLASES SE INSTANCIARON CORRECTAMENTE")
        return True
        
    except Exception as e:
        print(f"❌ Error en prueba de funcionalidad: {e}")
        return False

def check_data_availability():
    """
    Verifica si hay datos disponibles para análisis.
    """
    print(f"\n🧪 VERIFICANDO DISPONIBILIDAD DE DATOS")
    print("="*50)
    
    try:
        import glob
        data_files = glob.glob('data/*_clean.csv')
        
        if data_files:
            print(f"✅ Archivos de datos encontrados: {len(data_files)}")
            for file in data_files[:5]:  # Mostrar máximo 5
                print(f"   • {os.path.basename(file)}")
            if len(data_files) > 5:
                print(f"   • ... y {len(data_files)-5} más")
            return True
        else:
            print("⚠️ No se encontraron archivos *_clean.csv en data/")
            print("   Los scripts funcionarán pero necesitarás datos para análisis real")
            return False
            
    except Exception as e:
        print(f"❌ Error verificando datos: {e}")
        return False

def test_dependencies():
    """
    Verifica que todas las dependencias estén instaladas.
    """
    print(f"\n🧪 VERIFICANDO DEPENDENCIAS")
    print("="*50)
    
    required_packages = [
        'pandas', 'numpy', 'matplotlib', 'seaborn', 
        'sklearn', 'xgboost'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package} - NO INSTALADO")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n⚠️ Paquetes faltantes: {', '.join(missing_packages)}")
        print(f"Instalar con: pip install {' '.join(missing_packages)}")
        return False
    else:
        print(f"\n✅ Todas las dependencias están instaladas")
        return True

def main():
    """
    Función principal de pruebas.
    """
    print("🚀 VALIDACIÓN COMPLETA DE SCRIPTS TWITTRACK")
    print("="*60)
    
    # Ejecutar todas las pruebas
    import_success = test_imports()
    functionality_success = test_basic_functionality()
    data_available = check_data_availability()
    dependencies_ok = test_dependencies()
    
    # Resumen final
    print(f"\n📊 RESUMEN FINAL DE VALIDACIÓN")
    print("="*60)
    print(f"✅ Importaciones: {'PASS' if import_success else 'FAIL'}")
    print(f"✅ Funcionalidad: {'PASS' if functionality_success else 'FAIL'}")
    print(f"✅ Datos: {'DISPONIBLES' if data_available else 'NO ENCONTRADOS'}")
    print(f"✅ Dependencias: {'COMPLETAS' if dependencies_ok else 'INCOMPLETAS'}")
    
    if import_success and functionality_success and dependencies_ok:
        print(f"\n🎉 VALIDACIÓN EXITOSA - Scripts listos para usar")
        if data_available:
            print(f"💡 Puedes ejecutar: python main_pipeline.py")
        else:
            print(f"💡 Asegúrate de tener datos en data/*_clean.csv para análisis real")
    else:
        print(f"\n⚠️ VALIDACIÓN INCOMPLETA - Revisar errores arriba")
    
    return import_success and functionality_success and dependencies_ok

if __name__ == "__main__":
    success = main()
