#!/usr/bin/env python3
"""
Script de prueba para verificar el funcionamiento del sistema multi-cuenta.
"""

import os
import sys

def test_imports():
    """Test básico de importaciones."""
    print("🧪 TEST 1: IMPORTACIONES")
    print("-" * 40)
    
    try:
        from config import CUENTAS_DISPONIBLES, PROJECT_CONFIG
        print("✅ config.py importado")
        
        from data_loader import MultiAccountDataLoader
        print("✅ data_loader.py importado")
        
        from preprocessing import MultiAccountDataPreprocessor
        print("✅ preprocessing.py importado")
        
        from main_pipeline import TwitterAnalysisPipeline
        print("✅ main_pipeline.py importado")
        
        print(f"✅ Cuentas disponibles: {CUENTAS_DISPONIBLES}")
        return True
        
    except Exception as e:
        print(f"❌ Error en importaciones: {e}")
        return False

def test_data_availability():
    """Test de disponibilidad de archivos de datos."""
    print("\n🧪 TEST 2: DISPONIBILIDAD DE DATOS")
    print("-" * 40)
    
    try:
        from config import PROJECT_CONFIG
        import glob
        
        data_folder = PROJECT_CONFIG['data_folder']
        
        # Buscar archivos clean
        clean_pattern = os.path.join(data_folder, "*_clean.csv")
        clean_files = glob.glob(clean_pattern)
        print(f"📊 Archivos clean: {len(clean_files)}")
        
        # Buscar archivos métricas
        metricas_pattern = os.path.join(data_folder, "*_metricas.csv")
        metricas_files = glob.glob(metricas_pattern)
        print(f"📈 Archivos métricas: {len(metricas_files)}")
        
        total_files = len(clean_files) + len(metricas_files)
        print(f"📁 Total archivos: {total_files}")
        
        return total_files > 0
        
    except Exception as e:
        print(f"❌ Error verificando datos: {e}")
        return False

def test_basic_loading():
    """Test básico de carga de datos."""
    print("\n🧪 TEST 3: CARGA BÁSICA DE DATOS")
    print("-" * 40)
    
    try:
        from data_loader import MultiAccountDataLoader
        from config import CUENTAS_DISPONIBLES
        
        # Test con una cuenta específica
        test_account = CUENTAS_DISPONIBLES[0]
        print(f"📋 Testing con cuenta: {test_account}")
        
        loader = MultiAccountDataLoader(cuentas_objetivo=[test_account])
        
        # Buscar archivos
        clean_files = loader.find_files_by_type('clean')
        metricas_files = loader.find_files_by_type('metricas')
        
        print(f"📁 Clean files para {test_account}: {len(clean_files)}")
        print(f"📁 Métricas files para {test_account}: {len(metricas_files)}")
        
        if clean_files or metricas_files:
            print("✅ Archivos encontrados para la cuenta")
            return True
        else:
            print("⚠️ No se encontraron archivos para la cuenta")
            return False
            
    except Exception as e:
        print(f"❌ Error en carga básica: {e}")
        return False

def test_compatibility():
    """Test de compatibilidad con funciones legacy."""
    print("\n🧪 TEST 4: COMPATIBILIDAD LEGACY")
    print("-" * 40)
    
    try:
        from data_loader import load_and_prepare_data
        from config import CUENTAS_DISPONIBLES
        
        test_account = CUENTAS_DISPONIBLES[0]
        print(f"🔄 Testing load_and_prepare_data con {test_account}...")
        
        data, info = load_and_prepare_data(usuario_objetivo=test_account)
        
        if not data.empty:
            print(f"✅ Función legacy funciona: {data.shape}")
            return True
        else:
            print("⚠️ Función legacy retorna datos vacíos")
            return False
            
    except Exception as e:
        print(f"❌ Error en compatibility test: {e}")
        return False

def run_all_tests():
    """Ejecuta todos los tests."""
    print("🚀 EJECUTANDO TESTS MULTI-CUENTA")
    print("=" * 50)
    
    tests = [
        ("Importaciones", test_imports),
        ("Disponibilidad", test_data_availability),
        ("Carga Básica", test_basic_loading),
        ("Compatibilidad", test_compatibility)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ Error crítico en {test_name}: {e}")
            results.append((test_name, False))
    
    # Resumen final
    print("\n" + "=" * 50)
    print("📊 RESUMEN DE TESTS")
    print("=" * 50)
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} | {test_name}")
        if result:
            passed += 1
    
    print(f"\n🎯 RESULTADO: {passed}/{len(tests)} tests pasaron")
    
    if passed == len(tests):
        print("🎉 ¡TODOS LOS TESTS PASARON!")
        print("📦 Sistema multi-cuenta listo para usar")
    elif passed >= 2:
        print("👍 FUNCIONALIDAD BÁSICA OPERATIVA")
        print("⚠️ Algunos componentes pueden necesitar ajustes")
    else:
        print("⚠️ REQUIERE ATENCIÓN")
        print("🔧 Varios componentes necesitan revisión")
    
    return passed >= 2  # Al menos la mitad deben pasar

if __name__ == "__main__":
    # Ejecutar en el directorio correcto
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    
    # Ejecutar tests
    success = run_all_tests()
    
    # Mensaje final
    if success:
        print("\n✅ Sistema multi-cuenta está funcionando")
        print("🚀 Puedes proceder con el análisis")
    else:
        print("\n❌ Sistema requiere configuración adicional")
        print("📋 Revisa los datos y dependencias")
    
    sys.exit(0 if success else 1)
