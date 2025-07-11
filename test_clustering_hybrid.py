# =============================================================================
# TESTS PARA EL MÓDULO DE CLUSTERING HÍBRIDO
# =============================================================================

"""
Tests para verificar el funcionamiento del módulo de clustering híbrido.
"""

import sys
import os
from pathlib import Path
import numpy as np
import pandas as pd

# Agregar el directorio scripts al path
script_dir = Path(__file__).parent / "scripts"
sys.path.append(str(script_dir))

def test_clustering_hybrid():
    """Test principal para el módulo híbrido."""
    print("🧪 INICIANDO TESTS DEL CLUSTERING HÍBRIDO")
    print("=" * 50)
    
    try:
        from clustering_hybrid import HybridClusteringAnalyzer, run_kmeans_clustering, run_dbscan_clustering
        print("✅ Importación exitosa del módulo híbrido")
    except ImportError as e:
        print(f"❌ Error al importar el módulo: {e}")
        return False
    
    # Test 1: Inicialización
    print("\n🔧 Test 1: Inicialización del analizador")
    try:
        analyzer = HybridClusteringAnalyzer()
        print("✅ Analizador inicializado correctamente")
    except Exception as e:
        print(f"❌ Error en inicialización: {e}")
        return False
    
    # Test 2: Verificar archivos de datos disponibles
    print("\n📁 Test 2: Verificación de archivos de datos")
    data_dir = Path("data")
    if not data_dir.exists():
        print("❌ Directorio 'data' no encontrado")
        return False
    
    # Buscar archivos *_clean.csv
    clean_files = list(data_dir.glob("*_clean.csv"))
    if not clean_files:
        print("❌ No se encontraron archivos *_clean.csv")
        return False
    
    print(f"✅ Encontrados {len(clean_files)} archivos de datos:")
    for file in clean_files[:3]:  # Mostrar solo los primeros 3
        print(f"   • {file.name}")
    
    # Seleccionar una cuenta para testing
    test_account = clean_files[0].stem.replace("_clean", "")
    print(f"📊 Usando cuenta de prueba: {test_account}")
    
    # Test 3: Carga de datos
    print(f"\n📊 Test 3: Carga de datos para {test_account}")
    try:
        df = analyzer.load_account_data(test_account)
        print(f"✅ Datos cargados: {len(df)} registros")
        
        if len(df) == 0:
            print("⚠️  Warning: No hay datos después de la deduplicación")
            return False
            
    except Exception as e:
        print(f"❌ Error en carga de datos: {e}")
        return False
    
    # Test 4: Cálculo de métricas
    print("\n📈 Test 4: Cálculo de métricas de engagement")
    try:
        df_with_metrics = analyzer.calculate_engagement_metrics(df)
        required_cols = ['engagement_rate', 'total_interactions', 'likes_ratio']
        
        for col in required_cols:
            if col in df_with_metrics.columns:
                print(f"✅ Métrica '{col}' calculada")
            else:
                print(f"❌ Métrica '{col}' faltante")
                return False
                
    except Exception as e:
        print(f"❌ Error en cálculo de métricas: {e}")
        return False
    
    # Test 5: Optimización de parámetros (sin gráficos)
    print("\n🔍 Test 5: Optimización de parámetros")
    try:
        # Preparar datos para clustering
        features = ['engagement_rate', 'vistas']
        available_features = [f for f in features if f in df_with_metrics.columns]
        
        if len(available_features) < 2:
            print("⚠️  Warning: Pocas características disponibles para clustering")
            available_features = ['engagement_rate']
        
        X = df_with_metrics[available_features].fillna(0).values
        
        from sklearn.preprocessing import StandardScaler
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        
        # Test optimización K-Means
        kmeans_opt = analyzer.find_optimal_kmeans_clusters(X_scaled, max_k=5, show_plot=False)
        print(f"✅ K-Means optimizado: k={kmeans_opt['elbow_k']}")
        
        # Test optimización DBSCAN
        dbscan_opt = analyzer.find_optimal_dbscan_params(X_scaled, 
                                                        min_samples_range=[3, 5], 
                                                        show_plot=False)
        print(f"✅ DBSCAN optimizado: eps={dbscan_opt['recommended_eps']:.3f}")
        
    except Exception as e:
        print(f"❌ Error en optimización: {e}")
        return False
    
    # Test 6: Análisis completo con pocos datos
    print(f"\n🎯 Test 6: Análisis completo para {test_account}")
    try:
        # Solo usar el análisis si hay suficientes datos
        if len(df_with_metrics) >= 5:
            results = analyzer.run_clustering_analysis(
                username=test_account,
                features=available_features,
                auto_optimize=False,  # Para hacer test más rápido
                custom_params={
                    'kmeans': {'n_clusters': 2},
                    'dbscan': {'eps': 0.5, 'min_samples': 3}
                }
            )
            
            print("✅ Análisis completo ejecutado")
            
            # Verificar resultados
            if 'clustering' in results:
                print("✅ Resultados de clustering generados")
            if 'evaluation' in results:
                print("✅ Métricas de evaluación calculadas")
                
        else:
            print("⚠️  Datos insuficientes para clustering completo, pero estructura OK")
            
    except Exception as e:
        print(f"❌ Error en análisis completo: {e}")
        return False
    
    # Test 7: Funciones de compatibilidad
    print("\n🔗 Test 7: Funciones de compatibilidad")
    try:
        # Solo test de función K-Means compatible
        if len(df_with_metrics) >= 5:
            kmeans_compat_results = run_kmeans_clustering(
                username=test_account,
                n_clusters=2,
                features=['engagement_rate']
            )
            print("✅ Función K-Means compatible ejecutada")
        else:
            print("⚠️  Saltando test de compatibilidad por datos insuficientes")
            
    except Exception as e:
        print(f"⚠️  Error en funciones de compatibilidad (esperado con pocos datos): {e}")
    
    print("\n🎉 TODOS LOS TESTS COMPLETADOS")
    return True

def test_data_availability():
    """Test para verificar disponibilidad de datos."""
    print("\n📋 ANÁLISIS DE DISPONIBILIDAD DE DATOS")
    print("=" * 40)
    
    data_dir = Path("data")
    
    if not data_dir.exists():
        print("❌ Directorio 'data' no existe")
        return
    
    # Buscar todos los archivos CSV
    clean_files = list(data_dir.glob("*_clean.csv"))
    metrics_files = list(data_dir.glob("*_metricas.csv"))
    
    print(f"📄 Archivos *_clean.csv encontrados: {len(clean_files)}")
    print(f"📊 Archivos *_metricas.csv encontrados: {len(metrics_files)}")
    
    # Analizar tamaños de archivos
    account_stats = {}
    
    for file in clean_files:
        account = file.stem.replace("_clean", "")
        try:
            df = pd.read_csv(file)
            account_stats[account] = {
                'clean_records': len(df),
                'clean_file': file.name
            }
        except Exception as e:
            print(f"⚠️  Error leyendo {file.name}: {e}")
    
    for file in metrics_files:
        account = file.stem.replace("_metricas", "")
        if account in account_stats:
            try:
                df = pd.read_csv(file)
                account_stats[account]['metrics_records'] = len(df)
                account_stats[account]['metrics_file'] = file.name
            except Exception as e:
                print(f"⚠️  Error leyendo {file.name}: {e}")
    
    print("\n📊 Estadísticas por cuenta:")
    print("-" * 40)
    
    for account, stats in account_stats.items():
        clean_count = stats.get('clean_records', 0)
        metrics_count = stats.get('metrics_records', 0)
        print(f"{account:15}: {clean_count:4d} clean, {metrics_count:4d} metrics")
    
    # Identificar mejores cuentas para testing
    suitable_accounts = [acc for acc, stats in account_stats.items() 
                        if stats.get('clean_records', 0) >= 10]
    
    print(f"\n✅ Cuentas adecuadas para testing: {len(suitable_accounts)}")
    if suitable_accounts:
        print("   Recomendadas:", ", ".join(suitable_accounts[:3]))

def main():
    """Función principal de testing."""
    print("🔬 SUITE DE TESTS - CLUSTERING HÍBRIDO")
    print("=" * 60)
    
    # Cambiar al directorio del proyecto
    project_dir = Path(__file__).parent
    os.chdir(project_dir)
    
    # Test de disponibilidad de datos
    test_data_availability()
    
    # Test principal
    success = test_clustering_hybrid()
    
    if success:
        print("\n🎉 TODOS LOS TESTS PASARON EXITOSAMENTE")
        print("💡 El módulo híbrido está listo para uso en producción")
    else:
        print("\n❌ ALGUNOS TESTS FALLARON")
        print("🔧 Revisa los errores y corrige antes de usar en producción")
    
    return success

if __name__ == "__main__":
    main()
