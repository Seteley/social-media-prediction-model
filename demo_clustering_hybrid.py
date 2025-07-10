# =============================================================================
# DEMOSTRACIÓN DEL CLUSTERING HÍBRIDO
# =============================================================================

"""
Script de demostración del nuevo módulo de clustering híbrido que combina
las mejores características del enfoque canónico y los scripts del compañero.
"""

import sys
from pathlib import Path

# Agregar el directorio scripts al path
script_dir = Path(__file__).parent / "scripts"
sys.path.append(str(script_dir))

from clustering_hybrid import HybridClusteringAnalyzer, run_kmeans_clustering, run_dbscan_clustering

def demo_basic_usage():
    """Demuestra el uso básico del analizador híbrido."""
    print("\n🚀 DEMOSTRACIÓN 1: USO BÁSICO")
    print("=" * 50)
    
    # Inicializar analizador
    analyzer = HybridClusteringAnalyzer()
    
    # Analizar una cuenta con optimización automática
    username = "BCPComunica"
    
    print(f"Analizando cuenta: {username}")
    
    try:
        results = analyzer.run_clustering_analysis(
            username=username,
            features=['engagement_rate', 'vistas'],
            auto_optimize=True
        )
        
        print("✅ Análisis completado exitosamente")
        return results
        
    except FileNotFoundError as e:
        print(f"❌ Error: {e}")
        print("💡 Asegúrate de que existan los archivos de datos para esta cuenta")
        return None
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        return None

def demo_multiple_accounts():
    """Demuestra el análisis de múltiples cuentas."""
    print("\n🔄 DEMOSTRACIÓN 2: MÚLTIPLES CUENTAS")
    print("=" * 50)
    
    # Lista de cuentas bancarias disponibles
    accounts = [
        "BCPComunica",
        "bbva_peru", 
        "Interbank",
        "ScotiabankPE"
    ]
    
    analyzer = HybridClusteringAnalyzer()
    
    successful_analyses = []
    
    for username in accounts:
        print(f"\n📊 Analizando {username}...")
        try:
            results = analyzer.run_clustering_analysis(
                username=username,
                features=['engagement_rate', 'vistas', 'total_interactions'],
                auto_optimize=True
            )
            successful_analyses.append(username)
            print(f"   ✅ {username} analizado correctamente")
            
        except FileNotFoundError:
            print(f"   ⚠️  {username}: Archivos no encontrados")
        except Exception as e:
            print(f"   ❌ {username}: Error - {e}")
    
    # Comparar cuentas analizadas exitosamente
    if len(successful_analyses) > 1:
        print(f"\n🔍 Comparando {len(successful_analyses)} cuentas...")
        comparison = analyzer.compare_accounts(successful_analyses)
        
        print("\n📊 Resultados de la comparación:")
        print(comparison['comparison_table'].to_string(index=False))
    
    return successful_analyses

def demo_custom_parameters():
    """Demuestra el uso con parámetros personalizados."""
    print("\n⚙️  DEMOSTRACIÓN 3: PARÁMETROS PERSONALIZADOS")
    print("=" * 50)
    
    analyzer = HybridClusteringAnalyzer()
    
    username = "BCPComunica"
    
    # Parámetros personalizados sin optimización automática
    custom_params = {
        'kmeans': {'n_clusters': 4},
        'dbscan': {'eps': 0.3, 'min_samples': 3}
    }
    
    try:
        results = analyzer.run_clustering_analysis(
            username=username,
            features=['engagement_rate', 'vistas', 'likes_ratio'],
            auto_optimize=False,
            custom_params=custom_params
        )
        
        print("✅ Análisis con parámetros personalizados completado")
        return results
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def demo_compatibility_functions():
    """Demuestra las funciones de compatibilidad con scripts existentes."""
    print("\n🔗 DEMOSTRACIÓN 4: COMPATIBILIDAD CON SCRIPTS EXISTENTES")
    print("=" * 50)
    
    username = "BCPComunica"
    
    try:
        # Usar función compatible con K-Means del compañero
        print("🔵 Ejecutando K-Means compatible...")
        kmeans_results = run_kmeans_clustering(
            username=username,
            n_clusters=3,
            features=['engagement_rate', 'vistas']
        )
        
        print("✅ K-Means compatible ejecutado")
        
        # Usar función compatible con DBSCAN del compañero
        print("\n🔴 Ejecutando DBSCAN compatible...")
        dbscan_results = run_dbscan_clustering(
            username=username,
            eps=0.4,
            min_samples=4,
            features=['engagement_rate']
        )
        
        print("✅ DBSCAN compatible ejecutado")
        
        return {'kmeans': kmeans_results, 'dbscan': dbscan_results}
        
    except Exception as e:
        print(f"❌ Error en funciones de compatibilidad: {e}")
        return None

def demo_advanced_features():
    """Demuestra características avanzadas del analizador híbrido."""
    print("\n🎯 DEMOSTRACIÓN 5: CARACTERÍSTICAS AVANZADAS")
    print("=" * 50)
    
    analyzer = HybridClusteringAnalyzer()
    
    username = "BCPComunica"
    
    try:
        # Cargar datos y calcular métricas
        print("📊 Cargando datos y calculando métricas avanzadas...")
        df = analyzer.load_account_data(username)
        df = analyzer.calculate_engagement_metrics(df)
        
        print(f"   ✅ Cargados {len(df)} tweets deduplicados")
        print(f"   📈 Engagement promedio: {df['engagement_rate'].mean():.4f}")
        print(f"   📊 Métricas calculadas: {[col for col in df.columns if 'ratio' in col or 'log_' in col]}")
        
        # Preparar datos para clustering
        features = ['engagement_rate', 'vistas', 'total_interactions', 'likes_ratio']
        X = df[features].fillna(0).values
        
        from sklearn.preprocessing import StandardScaler
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        
        # Demostrar optimización de parámetros
        print("\n🔍 Optimizando parámetros K-Means...")
        kmeans_opt = analyzer.find_optimal_kmeans_clusters(X_scaled, max_k=8, show_plot=False)
        print(f"   📊 Codo sugerido: k={kmeans_opt['elbow_k']}")
        print(f"   📊 Mejor silhouette: k={kmeans_opt['best_silhouette_k']}")
        
        print("\n🔍 Optimizando parámetros DBSCAN...")
        dbscan_opt = analyzer.find_optimal_dbscan_params(X_scaled, show_plot=False)
        print(f"   📊 Eps recomendado: {dbscan_opt['recommended_eps']:.3f}")
        print(f"   📊 Min_samples recomendado: {dbscan_opt['recommended_min_samples']}")
        
        return {'optimization': {'kmeans': kmeans_opt, 'dbscan': dbscan_opt}}
        
    except Exception as e:
        print(f"❌ Error en características avanzadas: {e}")
        return None

def demo_data_sources():
    """Demuestra el soporte para múltiples fuentes de datos."""
    print("\n💾 DEMOSTRACIÓN 6: MÚLTIPLES FUENTES DE DATOS")
    print("=" * 50)
    
    username = "BCPComunica"
    
    # Probar con CSV (por defecto)
    print("📄 Probando fuente de datos: CSV")
    try:
        analyzer_csv = HybridClusteringAnalyzer(data_source='csv')
        df_csv = analyzer_csv.load_account_data(username)
        print(f"   ✅ CSV: {len(df_csv)} registros cargados")
    except Exception as e:
        print(f"   ❌ CSV: Error - {e}")
    
    # Probar con DuckDB (si está disponible)
    print("\n🦆 Probando fuente de datos: DuckDB")
    try:
        analyzer_duck = HybridClusteringAnalyzer(data_source='duckdb')
        df_duck = analyzer_duck.load_account_data(username)
        print(f"   ✅ DuckDB: {len(df_duck)} registros cargados")
    except Exception as e:
        print(f"   ⚠️  DuckDB: {e}")

def main():
    """Función principal que ejecuta todas las demostraciones."""
    print("🎯 DEMOSTRACIÓN DEL CLUSTERING HÍBRIDO")
    print("=" * 60)
    print("Este script demuestra las capacidades del nuevo módulo de clustering híbrido")
    print("que combina las mejores características del enfoque canónico y los scripts del compañero.")
    
    # Lista de demostraciones
    demos = [
        ("Uso Básico", demo_basic_usage),
        ("Múltiples Cuentas", demo_multiple_accounts),
        ("Parámetros Personalizados", demo_custom_parameters),
        ("Compatibilidad", demo_compatibility_functions),
        ("Características Avanzadas", demo_advanced_features),
        ("Múltiples Fuentes", demo_data_sources)
    ]
    
    results = {}
    
    for demo_name, demo_func in demos:
        try:
            print(f"\n{'='*20} {demo_name.upper()} {'='*20}")
            result = demo_func()
            results[demo_name] = result
            
        except KeyboardInterrupt:
            print(f"\n⏹️  Demostración interrumpida por el usuario")
            break
        except Exception as e:
            print(f"\n❌ Error en {demo_name}: {e}")
            continue
    
    print("\n🎉 DEMOSTRACIÓN COMPLETADA")
    print("=" * 60)
    print("📋 Resumen:")
    
    for demo_name, result in results.items():
        status = "✅ Exitoso" if result is not None else "❌ Falló"
        print(f"   • {demo_name}: {status}")
    
    print("\n💡 El módulo híbrido está listo para su uso en producción!")
    print("📚 Consulta clustering_hybrid.py para más detalles sobre la implementación.")

if __name__ == "__main__":
    main()
