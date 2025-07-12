# =============================================================================
# ANÁLISIS DE CLUSTERING HÍBRIDO - VERSIÓN MEJORADA
# =============================================================================

"""
Módulo híbrido de clustering que combina las mejores características de:
1. El enfoque canónico orientado a objetos con soporte multi-cuenta
2. Los scripts específicos del compañero con análisis detallado

Características principales:
- Soporte multi-cuenta y multi-archivo (*_clean.csv, *_metricas.csv)
- Métodos explícitos para elbow/k-distance para determinar parámetros óptimos
- Múltiples métricas de evaluación (silhouette, davies_bouldin, calinski_harabasz)
- Deduplicación de tweets avanzada
- Visualizaciones mejoradas
- Análisis de engagement específico
- Soporte para DuckDB además de CSV
- Configuración flexible y extensible
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.cluster import KMeans, DBSCAN
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import silhouette_score, davies_bouldin_score, calinski_harabasz_score
from sklearn.neighbors import NearestNeighbors
from typing import Tuple, Dict, List, Optional, Union
import warnings
from pathlib import Path

try:
    import duckdb
    DUCKDB_AVAILABLE = True
except ImportError:
    DUCKDB_AVAILABLE = False
    warnings.warn("DuckDB no disponible. Solo se usarán archivos CSV.")




class HybridClusteringAnalyzer:
    """
    Analizador híbrido de clustering que combina las mejores características
    del enfoque canónico y los scripts específicos del compañero.
    """
    
    def __init__(self, config: Dict = None, data_source: str = 'csv'):
        """
        Inicializa el analizador híbrido de clustering.
        
        Args:
            config (Dict): Configuración de modelos
            data_source (str): Fuente de datos ('csv' o 'duckdb')
        """
        self.config = config if config is not None else {
            'kmeans': {'n_clusters': 5, 'random_state': 42, 'n_init': 10, 'max_iter': 300},
            'dbscan': {'eps': 0.5, 'min_samples': 5, 'metric': 'euclidean'}
        }
        self.data_source = data_source
        self.models = {}
        self.results = {}
        self.scalers = {}
        self.optimal_params = {}
        # Ya no es necesario el bloque de configuración por defecto adicional
    
    def load_account_data(self, username: str) -> pd.DataFrame:
        """
        Carga datos de una cuenta específica desde la base de datos DuckDB con deduplicación automática.
        
        Args:
            username (str): Nombre de la cuenta (ej: 'BCPComunica')
        
        Returns:
            pd.DataFrame: Datos cargados y deduplicados
        """
        print(f"📊 Cargando datos para {username} desde DuckDB...")
        if not DUCKDB_AVAILABLE:
            raise ImportError("DuckDB no está disponible. Instala duckdb para continuar.")
        return self._load_from_duckdb(username)
    
    
    def _load_from_duckdb(self, username: str) -> pd.DataFrame:
        """Carga datos desde DuckDB."""
        db_path = 'data/base_de_datos/social_media.duckdb'
        
        if not Path(db_path).exists():
            raise FileNotFoundError(f"Base de datos DuckDB no encontrada: {db_path}")
        
        query = f'''
            SELECT fecha_publicacion, contenido, respuestas, retweets, likes, guardados, vistas
            FROM (
                SELECT *,
                       ROW_NUMBER() OVER (PARTITION BY fecha_publicacion, contenido ORDER BY fecha_publicacion DESC) AS rn
                FROM publicaciones
                JOIN usuario ON publicaciones.id_usuario = usuario.id_usuario
                WHERE usuario.cuenta = '{username}'
            )
            WHERE rn = 1
        '''
        
        con = duckdb.connect(db_path)
        df = con.execute(query).fetchdf()
        con.close()
        
        return df.reset_index(drop=True)
    

    def calculate_engagement_metrics(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calcula métricas de engagement mejoradas.
        
        Args:
            df (pd.DataFrame): DataFrame con datos de Twitter
        
        Returns:
            pd.DataFrame: DataFrame con métricas calculadas
        """
        print("📈 Calculando métricas de engagement...")
        
        # Rellenar valores faltantes
        engagement_cols = ['respuestas', 'retweets', 'likes', 'guardados', 'vistas']
        df[engagement_cols] = df[engagement_cols].fillna(0)
        
        # Engagement rate
        df['engagement_rate'] = 0.0
        mask_vistas = df['vistas'] > 0
        df.loc[mask_vistas, 'engagement_rate'] = (
            df.loc[mask_vistas, 'respuestas'] +
            df.loc[mask_vistas, 'retweets'] +
            df.loc[mask_vistas, 'likes'] +
            df.loc[mask_vistas, 'guardados']
        ) / df.loc[mask_vistas, 'vistas']
        
        # Métricas adicionales
        df['total_interactions'] = df['respuestas'] + df['retweets'] + df['likes'] + df['guardados']
        df['likes_ratio'] = np.where(df['total_interactions'] > 0, 
                                   df['likes'] / df['total_interactions'], 0)
        df['retweets_ratio'] = np.where(df['total_interactions'] > 0, 
                                      df['retweets'] / df['total_interactions'], 0)
        
        # Normalización logarítmica para métricas con gran varianza
        for col in ['vistas', 'total_interactions']:
            df[f'log_{col}'] = np.log1p(df[col])
        
        print(f"   ✅ Métricas calculadas. Engagement promedio: {df['engagement_rate'].mean():.4f}")
        return df
    
    def find_optimal_kmeans_clusters(self, X: np.ndarray, max_k: int = 10, 
                                   show_plot: bool = True) -> Dict:
        """
        Encuentra el número óptimo de clusters usando método del codo y silhouette.
        
        Args:
            X (np.ndarray): Datos escalados para clustering
            max_k (int): Número máximo de clusters a probar
            show_plot (bool): Si mostrar gráficos
        
        Returns:
            Dict: Resultados del análisis de clusters óptimos
        """
        print(f"🔍 Buscando número óptimo de clusters (K-Means, k=1 a {max_k})...")
        
        K_range = range(1, max_k + 1)
        inertias = []
        silhouette_scores = []
        
        for k in K_range:
            kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
            labels = kmeans.fit_predict(X)
            inertias.append(kmeans.inertia_)
            
            # Silhouette solo para k > 1
            if k > 1:
                sil_score = silhouette_score(X, labels)
                silhouette_scores.append(sil_score)
            else:
                silhouette_scores.append(0)
        
        # Encontrar codo usando diferencias de segunda derivada
        if len(inertias) >= 3:
            diffs = np.diff(inertias)
            diff2 = np.diff(diffs)
            elbow_k = np.argmax(diff2) + 2  # +2 porque diff2 es 2 posiciones menos
        else:
            elbow_k = 3
        
        # Mejor k por silhouette (excluyendo k=1)
        if len(silhouette_scores) > 1:
            best_sil_k = np.argmax(silhouette_scores[1:]) + 2
        else:
            best_sil_k = 2
        
        if show_plot:
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
            
            # Método del codo
            ax1.plot(K_range, inertias, marker='o', linewidth=2, markersize=8)
            ax1.axvline(x=elbow_k, color='red', linestyle='--', alpha=0.7, 
                       label=f'Codo sugerido: k={elbow_k}')
            ax1.set_xlabel('Número de Clusters (k)')
            ax1.set_ylabel('Inercia (WCSS)')
            ax1.set_title('Método del Codo - K-Means')
            ax1.legend()
            ax1.grid(True, alpha=0.3)
            
            # Silhouette Score
            ax2.plot(K_range[1:], silhouette_scores[1:], marker='s', color='green',
                    linewidth=2, markersize=8)
            ax2.axvline(x=best_sil_k, color='green', linestyle='--', alpha=0.7,
                       label=f'Mejor silhouette: k={best_sil_k}')
            ax2.set_xlabel('Número de Clusters (k)')
            ax2.set_ylabel('Silhouette Score')
            ax2.set_title('Análisis Silhouette - K-Means')
            ax2.legend()
            ax2.grid(True, alpha=0.3)
            
            plt.tight_layout()
            plt.show()
        
        results = {
            'inertias': inertias,
            'silhouette_scores': silhouette_scores,
            'elbow_k': elbow_k,
            'best_silhouette_k': best_sil_k,
            'max_silhouette': max(silhouette_scores[1:]) if len(silhouette_scores) > 1 else 0
        }
        
        print(f"   📊 Codo sugerido: k={elbow_k}")
        print(f"   📊 Mejor silhouette: k={best_sil_k} (score: {results['max_silhouette']:.3f})")
        
        return results
    
    def find_optimal_dbscan_params(self, X: np.ndarray, min_samples_range: List[int] = None,
                                 show_plot: bool = True) -> Dict:
        """
        Encuentra parámetros óptimos para DBSCAN usando k-distance plot.
        
        Args:
            X (np.ndarray): Datos escalados para clustering
            min_samples_range (List[int]): Rango de min_samples a probar
            show_plot (bool): Si mostrar gráficos
        
        Returns:
            Dict: Parámetros sugeridos para DBSCAN
        """
        print("🔍 Analizando parámetros óptimos para DBSCAN...")
        
        if min_samples_range is None:
            #min_samples_range = [3, 5, 7, 10]
            min_samples_range = [4]
        
        results = {}
        
        if show_plot:
            #fig, axes = plt.subplots(2, 2, figsize=(14, 10))
            fig, ax = plt.subplots(1, 1, figsize=(14, 10))
            axes = [ax]
        
        for i, min_samples in enumerate(min_samples_range):
            # K-distance plot
            neighbors = NearestNeighbors(n_neighbors=min_samples)
            neighbors_fit = neighbors.fit(X)
            distances, indices = neighbors_fit.kneighbors(X)
            
            # Ordenar distancias al k-ésimo vecino más cercano
            k_distances = np.sort(distances[:, min_samples-1])
            
            # Encontrar punto de inflexión (estimación de eps)
            # Usar gradiente para encontrar el mayor cambio
            gradients = np.gradient(k_distances)
            suggested_eps_idx = np.argmax(gradients)
            suggested_eps = k_distances[suggested_eps_idx]
            
            results[min_samples] = {
                'distances': k_distances,
                'suggested_eps': suggested_eps,
                'eps_index': suggested_eps_idx
            }
            
            if show_plot and i < 4:
                ax = axes[i]
                ax.plot(k_distances, linewidth=2)
                ax.axhline(y=suggested_eps, color='red', linestyle='--', alpha=0.7,
                          label=f'Eps sugerido: {suggested_eps:.3f}')
                ax.set_xlabel('Puntos ordenados')
                ax.set_ylabel(f'Distancia al {min_samples}º vecino')
                ax.set_title(f'K-distance (min_samples={min_samples})')
                ax.legend()
                ax.grid(True, alpha=0.3)
        
        if show_plot:
            plt.tight_layout()
            plt.show()
        
        # Seleccionar parámetros recomendados (min_samples=5 como default)
        #recommended_min_samples = 5 if 5 in results else min_samples_range[0]
        recommended_min_samples = 4 if 4 in results else min_samples_range[0]
        recommended_eps = results[recommended_min_samples]['suggested_eps']
        
        final_results = {
            'all_results': results,
            'recommended_eps': recommended_eps,
            'recommended_min_samples': recommended_min_samples
        }
        
        print(f"   📊 Parámetros recomendados: eps={recommended_eps:.3f}, min_samples={recommended_min_samples}")
        
        return final_results
    
    def run_clustering_analysis(self, username: str, features: List[str] = None,
                              auto_optimize: bool = True, 
                              custom_params: Dict = None) -> Dict:
        """
        Ejecuta análisis completo de clustering para una cuenta.
        
        Args:
            username (str): Nombre de la cuenta
            features (List[str]): Características para clustering
            auto_optimize (bool): Si optimizar parámetros automáticamente
            custom_params (Dict): Parámetros personalizados para algoritmos
        
        Returns:
            Dict: Resultados completos del análisis
        """
        print(f"\n🚀 Iniciando análisis de clustering para {username}")
        print("=" * 60)
        
        # 1. Cargar datos
        df = self.load_account_data(username)
        df = self.calculate_engagement_metrics(df)
        
        # 2. Seleccionar características
        if features is None:
            features = ['engagement_rate', 'vistas']
            # Agregar más características si están disponibles
            additional_features = ['total_interactions', 'likes_ratio', 'retweets_ratio']
            for feat in additional_features:
                if feat in df.columns:
                    features.append(feat)
        
        print(f"📋 Características seleccionadas: {features}")
        
        # 3. Preparar datos
        X = df[features].fillna(0).values
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        
        self.scalers[username] = scaler
        
        # 4. Optimización de parámetros
        optimization_results = {}
        
        if auto_optimize:
            print("\n🔧 Optimizando parámetros...")
            
            # K-Means
            kmeans_opt = self.find_optimal_kmeans_clusters(X_scaled, show_plot=True)
            optimization_results['kmeans'] = kmeans_opt
            
            # DBSCAN
            dbscan_opt = self.find_optimal_dbscan_params(X_scaled, show_plot=True)
            optimization_results['dbscan'] = dbscan_opt
            
            # Actualizar parámetros
            if custom_params is None:
                custom_params = {}
            
            if 'kmeans' not in custom_params:
                custom_params['kmeans'] = {'n_clusters': kmeans_opt['elbow_k']}
            
            if 'dbscan' not in custom_params:
                custom_params['dbscan'] = {
                    'eps': dbscan_opt['recommended_eps'],
                    'min_samples': dbscan_opt['recommended_min_samples']
                }
        
        # 5. Aplicar clustering
        print("\n🎯 Aplicando algoritmos de clustering...")
        
        clustering_results = {}
        
        # K-Means por elbow
        kmeans_params_elbow = {'n_clusters': optimization_results['kmeans']['elbow_k'], 'random_state': 42, 'n_init': 10}
        kmeans_elbow = KMeans(**kmeans_params_elbow)
        df['cluster_kmeans_elbow'] = kmeans_elbow.fit_predict(X_scaled)
        clustering_results['kmeans_elbow'] = {
            'model': kmeans_elbow,
            'labels': df['cluster_kmeans_elbow'].values,
            'params': kmeans_params_elbow,
            'n_clusters': len(np.unique(df['cluster_kmeans_elbow']))
        }

        # K-Means por silhouette
        kmeans_params_sil = {'n_clusters': optimization_results['kmeans']['best_silhouette_k'], 'random_state': 42, 'n_init': 10}
        kmeans_sil = KMeans(**kmeans_params_sil)
        df['cluster_kmeans_silhouette'] = kmeans_sil.fit_predict(X_scaled)
        clustering_results['kmeans_silhouette'] = {
            'model': kmeans_sil,
            'labels': df['cluster_kmeans_silhouette'].values,
            'params': kmeans_params_sil,
            'n_clusters': len(np.unique(df['cluster_kmeans_silhouette']))
        }

        # DBSCAN
        dbscan_params = custom_params.get('dbscan', self.config.get('dbscan', {'eps': 0.5, 'min_samples': 5}))
        dbscan = DBSCAN(**dbscan_params)
        df['cluster_dbscan'] = dbscan.fit_predict(X_scaled)
        n_clusters_dbscan = len(set(df['cluster_dbscan'])) - (1 if -1 in df['cluster_dbscan'] else 0)
        n_noise = list(df['cluster_dbscan']).count(-1)
        clustering_results['dbscan'] = {
            'model': dbscan,
            'labels': df['cluster_dbscan'].values,
            'params': dbscan_params,
            'n_clusters': n_clusters_dbscan,
            'n_noise': n_noise
        }
        
        # 6. Evaluación
        print("\n📊 Evaluando resultados...")
        
        evaluation_results = self._evaluate_clustering(X_scaled, clustering_results)

        # 7. Visualizaciones
        print("\n🎨 Generando visualizaciones...")
        self._generate_visualizations_multi(df, X_scaled, clustering_results, features, username)

        # 8. Análisis de clusters
        cluster_analysis = self._analyze_clusters_multi(df, features, username)

        # Resultados finales
        final_results = {
            'username': username,
            'data': df,
            'features': features,
            'scaled_data': X_scaled,
            'optimization': optimization_results,
            'clustering': clustering_results,
            'evaluation': evaluation_results,
            'cluster_analysis': cluster_analysis,
            'scaler': scaler
        }

        self.results[username] = final_results

        print(f"\n✅ Análisis completado para {username}")
        self._print_summary(final_results)

        return final_results
    
    def _evaluate_clustering(self, X_scaled: np.ndarray, clustering_results: Dict) -> Dict:
        """Evalúa los resultados de clustering con múltiples métricas."""
        evaluation = {}
        
        for algorithm, results in clustering_results.items():
            labels = results['labels']
            n_clusters = results['n_clusters']
            
            if n_clusters > 1:
                # Silhouette Score
                sil_score = silhouette_score(X_scaled, labels)
                
                # Davies-Bouldin Index (menor es mejor)
                db_score = davies_bouldin_score(X_scaled, labels)
                
                # Calinski-Harabasz Index (mayor es mejor)
                ch_score = calinski_harabasz_score(X_scaled, labels)
                
                evaluation[algorithm] = {
                    'silhouette_score': sil_score,
                    'davies_bouldin_score': db_score,
                    'calinski_harabasz_score': ch_score,
                    'n_clusters': n_clusters
                }
                
                if algorithm == 'dbscan':
                    evaluation[algorithm]['n_noise'] = results['n_noise']
            else:
                evaluation[algorithm] = {
                    'silhouette_score': 0,
                    'davies_bouldin_score': float('inf'),
                    'calinski_harabasz_score': 0,
                    'n_clusters': n_clusters
                }
        
        return evaluation
    
    def _generate_visualizations_multi(self, df: pd.DataFrame, X_scaled: np.ndarray, 
                               clustering_results: Dict, features: List[str], username: str):
        """Genera visualizaciones para los 3 modelos de clustering."""
        # 1. Scatter plots de clusters
        if len(features) >= 2:
            fig, axes = plt.subplots(1, 3, figsize=(24, 6))
            # K-Means por elbow
            ax1 = axes[0]
            scatter1 = ax1.scatter(df[features[0]], df[features[1]], 
                                c=df['cluster_kmeans_elbow'], cmap='viridis', alpha=0.7)
            ax1.set_xlabel(features[0])
            ax1.set_ylabel(features[1])
            ax1.set_title(f'K-Means (elbow) - {username}')
            plt.colorbar(scatter1, ax=ax1)
            # K-Means por silhouette
            ax2 = axes[1]
            scatter2 = ax2.scatter(df[features[0]], df[features[1]], 
                                c=df['cluster_kmeans_silhouette'], cmap='viridis', alpha=0.7)
            ax2.set_xlabel(features[0])
            ax2.set_ylabel(features[1])
            ax2.set_title(f'K-Means (silhouette) - {username}')
            plt.colorbar(scatter2, ax=ax2)
            # DBSCAN
            ax3 = axes[2]
            scatter3 = ax3.scatter(df[features[0]], df[features[1]], 
                                c=df['cluster_dbscan'], cmap='viridis', alpha=0.7)
            ax3.set_xlabel(features[0])
            ax3.set_ylabel(features[1])
            ax3.set_title(f'DBSCAN - {username}')
            plt.colorbar(scatter3, ax=ax3)
            plt.tight_layout()
            plt.show()
        # 2. PCA visualization si hay más de 2 features
        if len(features) > 2:
            pca = PCA(n_components=2, random_state=42)
            X_pca = pca.fit_transform(X_scaled)
            fig, axes = plt.subplots(1, 3, figsize=(24, 6))
            # K-Means por elbow PCA
            ax1 = axes[0]
            scatter1 = ax1.scatter(X_pca[:, 0], X_pca[:, 1], 
                                c=df['cluster_kmeans_elbow'], cmap='viridis', alpha=0.7)
            ax1.set_xlabel(f'PC1 ({pca.explained_variance_ratio_[0]:.2%} varianza)')
            ax1.set_ylabel(f'PC2 ({pca.explained_variance_ratio_[1]:.2%} varianza)')
            ax1.set_title(f'K-Means (elbow, PCA) - {username}')
            plt.colorbar(scatter1, ax=ax1)
            # K-Means por silhouette PCA
            ax2 = axes[1]
            scatter2 = ax2.scatter(X_pca[:, 0], X_pca[:, 1], 
                                c=df['cluster_kmeans_silhouette'], cmap='viridis', alpha=0.7)
            ax2.set_xlabel(f'PC1 ({pca.explained_variance_ratio_[0]:.2%} varianza)')
            ax2.set_ylabel(f'PC2 ({pca.explained_variance_ratio_[1]:.2%} varianza)')
            ax2.set_title(f'K-Means (silhouette, PCA) - {username}')
            plt.colorbar(scatter2, ax=ax2)
            # DBSCAN PCA
            ax3 = axes[2]
            scatter3 = ax3.scatter(X_pca[:, 0], X_pca[:, 1], 
                                c=df['cluster_dbscan'], cmap='viridis', alpha=0.7)
            ax3.set_xlabel(f'PC1 ({pca.explained_variance_ratio_[0]:.2%} varianza)')
            ax3.set_ylabel(f'PC2 ({pca.explained_variance_ratio_[1]:.2%} varianza)')
            ax3.set_title(f'DBSCAN (PCA) - {username}')
            plt.colorbar(scatter3, ax=ax3)
            plt.tight_layout()
            plt.show()
    
    def _analyze_clusters_multi(self, df: pd.DataFrame, features: List[str], username: str) -> Dict:
        """Analiza las características de cada cluster para los 3 modelos."""
        analysis = {}
        for algorithm, cluster_col in [
            ('kmeans_elbow', 'cluster_kmeans_elbow'),
            ('kmeans_silhouette', 'cluster_kmeans_silhouette'),
            ('dbscan', 'cluster_dbscan')
        ]:
            if cluster_col not in df.columns:
                continue
            analysis[algorithm] = {}
            # Estadísticas por cluster
            cluster_stats = df.groupby(cluster_col)[features].agg(['mean', 'std', 'count'])
            analysis[algorithm]['cluster_stats'] = cluster_stats
            # Contenido representativo de cada cluster
            sample_content = {}
            for cluster_id in df[cluster_col].unique():
                if algorithm == 'dbscan' and cluster_id == -1:
                    continue
                cluster_tweets = df[df[cluster_col] == cluster_id]
                if len(cluster_tweets) > 0:
                    sample_content[cluster_id] = cluster_tweets['contenido'].head(3).tolist()
            analysis[algorithm]['sample_content'] = sample_content
            print(f"\n📋 Análisis de clusters - {algorithm.upper()} ({username})")
            print("-" * 50)
            for cluster_id in sorted(df[cluster_col].unique()):
                if algorithm == 'dbscan' and cluster_id == -1:
                    print(f"🔸 Ruido: {(df[cluster_col] == -1).sum()} tweets")
                else:
                    cluster_size = (df[cluster_col] == cluster_id).sum()
                    avg_engagement = df[df[cluster_col] == cluster_id]['engagement_rate'].mean()
                    print(f"🔸 Cluster {cluster_id}: {cluster_size} tweets, engagement promedio: {avg_engagement:.4f}")
        return analysis
    
    def _print_summary(self, results: Dict):
        """Imprime un resumen de los resultados."""
        username = results['username']
        evaluation = results['evaluation']
        print("\n📊 RESUMEN DE RESULTADOS")
        print("=" * 40)
        print(f"Cuenta: {username}")
        print(f"Total de tweets: {len(results['data'])}")
        print(f"Características: {', '.join(results['features'])}")
        print("\n🎯 Métricas de Evaluación:")
        for algorithm, metrics in evaluation.items():
            print(f"\n{algorithm.upper()}:")
            print(f"  • Clusters: {metrics['n_clusters']}")
            if 'n_noise' in metrics:
                print(f"  • Ruido: {metrics['n_noise']} tweets")
            print(f"  • Silhouette: {metrics['silhouette_score']:.3f}")
            print(f"  • Davies-Bouldin: {metrics['davies_bouldin_score']:.3f}")
            print(f"  • Calinski-Harabasz: {metrics['calinski_harabasz_score']:.1f}")
        # Imprimir el mejor modelo
        best_model = self.select_best_model(evaluation)
        print(f"\n🏆 Mejor modelo según métricas: {best_model.upper()}")

    def select_best_model(self, evaluation: dict) -> str:
        """
        Selecciona el mejor modelo de clustering basado en las métricas calculadas.
        Prioriza mayor silhouette, luego mayor calinski-harabasz, penaliza Davies-Bouldin y clusters únicos.
        Args:
            evaluation (dict): Diccionario de métricas de evaluación para cada modelo.
        Returns:
            str: Nombre del mejor modelo ('kmeans_elbow', 'kmeans_silhouette', 'dbscan')
        """
        # Filtrar modelos con más de 1 cluster
        candidates = {k: v for k, v in evaluation.items() if v['n_clusters'] > 1}
        if not candidates:
            return max(evaluation, key=lambda k: evaluation[k]['n_clusters'])
        # Ordenar por silhouette, luego calinski, penalizar Davies-Bouldin
        def score(m):
            v = candidates[m]
            # Penalizar Davies-Bouldin alto y clusters únicos
            return (
                v['silhouette_score'],
                v['calinski_harabasz_score'],
                -v['davies_bouldin_score'],
                v['n_clusters']
            )
        best = max(candidates, key=score)
        return best
    
    def compare_accounts(self, usernames: List[str], features: List[str] = None) -> Dict:
        """
        Compara el clustering entre múltiples cuentas.
        
        Args:
            usernames (List[str]): Lista de nombres de cuentas
            features (List[str]): Características para comparación
        
        Returns:
            Dict: Comparación entre cuentas
        """
        print(f"\n🔄 Comparando clustering entre {len(usernames)} cuentas...")
        
        comparison_results = {}
        
        for username in usernames:
            if username not in self.results:
                print(f"⚠️  Ejecutando análisis para {username}...")
                self.run_clustering_analysis(username, features)
            
            comparison_results[username] = self.results[username]['evaluation']
        
        # Crear tabla comparativa
        comparison_df = pd.DataFrame()
        
        for username, metrics in comparison_results.items():
            for algorithm, scores in metrics.items():
                row_data = {
                    'cuenta': username,
                    'algoritmo': algorithm,
                    'n_clusters': scores['n_clusters'],
                    'silhouette': scores['silhouette_score'],
                    'davies_bouldin': scores['davies_bouldin_score'],
                    'calinski_harabasz': scores['calinski_harabasz_score']
                }
                
                if 'n_noise' in scores:
                    row_data['n_noise'] = scores['n_noise']
                
                comparison_df = pd.concat([comparison_df, pd.DataFrame([row_data])], 
                                        ignore_index=True)
        
        print("\n📊 Tabla Comparativa:")
        print(comparison_df.to_string(index=False))
        
        return {
            'individual_results': comparison_results,
            'comparison_table': comparison_df
        }
    
    def save_results(self, username: str, output_dir: str = 'results'):
        def to_serializable(obj):
            """Recursively convert numpy types to native Python types for JSON serialization."""
            import numpy as np
            if isinstance(obj, dict):
                return {k: to_serializable(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [to_serializable(i) for i in obj]
            elif isinstance(obj, (np.integer,)):
                return int(obj)
            elif isinstance(obj, (np.floating,)):
                return float(obj)
            elif isinstance(obj, (np.ndarray,)):
                return obj.tolist()
            else:
                return obj
        """
        Guarda los resultados del análisis en archivos.
        
        Args:
            username (str): Nombre de la cuenta
            output_dir (str): Directorio de salida
        """
        if username not in self.results:
            print(f"❌ No hay resultados para {username}")
            return

        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)

        results = self.results[username]

        # Guardar datos con clusters
        data_with_clusters = results['data']
        data_with_clusters.to_csv(output_path / f"{username}_clustering_results.csv", index=False)

        # Guardar métricas de evaluación
        evaluation_df = pd.DataFrame(results['evaluation']).T
        evaluation_df.to_csv(output_path / f"{username}_evaluation_metrics.csv")

        # Guardar el mejor modelo como .pkl en models/<username>/clustering.pkl
        import pickle, json, duckdb
        best_model_name = self.select_best_model(results['evaluation'])
        best_model = results['clustering'][best_model_name]['model']
        best_params = results['clustering'][best_model_name]['params']
        best_eval = results['evaluation'][best_model_name]
        model_type = 'KMEANS' if 'kmeans' in best_model_name else 'DBSCAN'
        # Convertir a tipos serializables
        best_params_serializable = to_serializable(best_params)
        eval_dict = {k: best_eval[k] for k in ['silhouette_score','davies_bouldin_score','calinski_harabasz_score','n_clusters'] if k in best_eval}
        if 'n_noise' in best_eval:
            eval_dict['n_noise'] = best_eval['n_noise']
        eval_dict_serializable = to_serializable(eval_dict)
        param_str = json.dumps(best_params_serializable)
        eval_str = json.dumps(eval_dict_serializable)
        # Guardar modelo pkl
        model_dir = Path('models') / username
        model_dir.mkdir(parents=True, exist_ok=True)
        model_filename = 'clustering.pkl'
        model_path = model_dir / model_filename
        with open(model_path, 'wb') as f:
            pickle.dump(best_model, f)
        print(f"💾 Resultados guardados en {output_path}")
        print(f"💾 Mejor modelo guardado en {model_path}")

        # Guardar información en la base de datos DuckDB (tabla modelo, histórico)
        db_path = 'data/base_de_datos/social_media.duckdb'
        if Path(db_path).exists():
            con = duckdb.connect(db_path)
            # Obtener id_usuario
            id_usuario = con.execute(f"SELECT id_usuario FROM usuario WHERE cuenta = ?", [username]).fetchone()
            if id_usuario:
                id_usuario = id_usuario[0]
                # Insertar en modelo (histórico)
                con.execute('''
                    INSERT INTO modelo (id_usuario, tipo_modelo, parametros, fecha_entrenamiento, archivo_modelo, evaluacion)
                    VALUES (?, ?, ?, CURRENT_DATE, ?, ?)
                ''', [id_usuario, model_type, param_str, model_filename, eval_str])
                print(f"💾 Registro de modelo guardado en DuckDB para usuario {username}")
            else:
                print(f"⚠️ No se encontró id_usuario para {username} en DuckDB. No se guardó registro de modelo.")
            con.close()
        else:
            print(f"⚠️ No se encontró la base de datos DuckDB para guardar el modelo.")

# FUNCIONES DE UTILIDAD PARA COMPATIBILIDAD CON SCRIPTS EXISTENTES

def run_kmeans_clustering(username: str, n_clusters: int = 5, 
                         features: List[str] = None) -> Dict:
    """
    Función compatible con los scripts existentes del compañero.
    
    Args:
        username (str): Nombre de la cuenta
        n_clusters (int): Número de clusters para K-Means
        features (List[str]): Características para clustering
    
    Returns:
        Dict: Resultados del clustering
    """
    analyzer = HybridClusteringAnalyzer()
    
    custom_params = {
        'kmeans': {'n_clusters': n_clusters}
    }
    
    results = analyzer.run_clustering_analysis(
        username=username, 
        features=features,
        auto_optimize=False,
        custom_params=custom_params
    )
    
    return results

def run_dbscan_clustering(username: str, eps: float = 0.5, 
                         min_samples: int = 5, features: List[str] = None) -> Dict:
    """
    Función compatible con los scripts existentes del compañero.
    
    Args:
        username (str): Nombre de la cuenta
        eps (float): Parámetro eps para DBSCAN
        min_samples (int): Parámetro min_samples para DBSCAN
        features (List[str]): Características para clustering
    
    Returns:
        Dict: Resultados del clustering
    """
    analyzer = HybridClusteringAnalyzer()
    
    custom_params = {
        'kmeans': {'n_clusters': 3},  # Parámetro por defecto para K-Means
        'dbscan': {'eps': eps, 'min_samples': min_samples}
    }
    
    results = analyzer.run_clustering_analysis(
        username=username,
        features=features,
        auto_optimize=False,
        custom_params=custom_params
    )
    
    return results

# =============================================================================
# EJEMPLO DE USO
# =============================================================================

if __name__ == "__main__":
    # Ejemplo de uso del analizador híbrido
    
    # Inicializar analizador
    analyzer = HybridClusteringAnalyzer()
    #
    # Analizar una cuenta específica
    username = "BancoPichincha"
    results = analyzer.run_clustering_analysis(
        username=username,
        features=['engagement_rate', 'vistas'],
        auto_optimize=True
    )
    
    # Comparar múltiples cuentas
    #accounts = ["BCPComunica", "bbva_peru", "Interbank"]
    #comparison = analyzer.compare_accounts(accounts)
    
    # Guardar resultados
    analyzer.save_results(username)
    
    print("\n🎉 Análisis híbrido completado!")
