# =============================================================================
# ANÁLISIS DE CLUSTERING
# =============================================================================

"""
Módulo para implementación y análisis de algoritmos de clustering.
Incluye K-Means, DBSCAN, evaluación de métricas y visualizaciones.
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans, DBSCAN
from sklearn.decomposition import PCA
from sklearn.metrics import silhouette_score
from typing import Tuple, Dict, List, Optional
from config import MODELS_CONFIG

class ClusteringAnalyzer:
    """
    Clase para análisis completo de clustering en datos de Twitter.
    """
    
    def __init__(self, config: Dict = None):
        """
        Inicializa el analizador de clustering.
        
        Args:
            config (Dict): Configuración de modelos
        """
        self.config = config or MODELS_CONFIG['clustering']
        self.models = {}
        self.results = {}
        self.pca = None
        
    def setup_models(self) -> Dict:
        """
        Configura los modelos de clustering.
        
        Returns:
            Dict: Diccionario con modelos configurados
        """
        print("🔄 Configurando modelos de clustering...")
        
        # K-Means
        print("\n🔵 Configurando K-Means...")
        self.models['kmeans'] = KMeans(**self.config['kmeans'])
        
        # DBSCAN
        print("🔴 Configurando DBSCAN...")
        self.models['dbscan'] = DBSCAN(**self.config['dbscan'])
        
        return self.models
    
    def fit_clustering_models(self, X_scaled: np.ndarray) -> Dict:
        """
        Entrena los modelos de clustering.
        
        Args:
            X_scaled (np.ndarray): Datos escalados
            
        Returns:
            Dict: Resultados del clustering
        """
        print("\n⚡ Entrenando modelos de clustering...")
        
        if not self.models:
            self.setup_models()
        
        results = {}
        
        # K-Means
        print("\n🔵 Entrenando K-Means...")
        labels_kmeans = self.models['kmeans'].fit_predict(X_scaled)
        n_clusters_kmeans = len(np.unique(labels_kmeans))
        silhouette_kmeans = silhouette_score(X_scaled, labels_kmeans)
        
        results['kmeans'] = {
            'labels': labels_kmeans,
            'n_clusters': n_clusters_kmeans,
            'silhouette_score': silhouette_kmeans,
            'inertia': self.models['kmeans'].inertia_,
            'cluster_centers': self.models['kmeans'].cluster_centers_
        }
        
        # DBSCAN
        print("🔴 Entrenando DBSCAN...")
        labels_dbscan = self.models['dbscan'].fit_predict(X_scaled)
        n_clusters_dbscan = len(np.unique(labels_dbscan[labels_dbscan != -1]))  # Excluir ruido
        n_noise_dbscan = np.sum(labels_dbscan == -1)
        
        # Calcular silhouette solo si hay más de 1 cluster
        silhouette_dbscan = (silhouette_score(X_scaled, labels_dbscan) 
                            if n_clusters_dbscan > 1 else -1)
        
        results['dbscan'] = {
            'labels': labels_dbscan,
            'n_clusters': n_clusters_dbscan,
            'n_noise': n_noise_dbscan,
            'silhouette_score': silhouette_dbscan,
            'core_samples': self.models['dbscan'].core_sample_indices_,
            'components': self.models['dbscan'].components_ if hasattr(self.models['dbscan'], 'components_') else None
        }
        
        self.results = results
        return results
    
    def print_clustering_results(self, results: Dict) -> None:
        """
        Imprime los resultados del clustering.
        
        Args:
            results (Dict): Resultados del clustering
        """
        print("\n" + "="*60)
        print("📈 RESULTADOS DEL CLUSTERING")
        print("="*60)
        
        # K-Means
        kmeans_results = results['kmeans']
        print(f"\n🔵 K-MEANS:")
        print(f"   • Clusters formados: {kmeans_results['n_clusters']}")
        print(f"   • Silhouette Score: {kmeans_results['silhouette_score']:.3f}")
        print(f"   • Inercia: {kmeans_results['inertia']:.2f}")
        
        # DBSCAN
        dbscan_results = results['dbscan']
        print(f"\n🔴 DBSCAN:")
        print(f"   • Clusters formados: {dbscan_results['n_clusters']}")
        print(f"   • Puntos de ruido: {dbscan_results['n_noise']} ({dbscan_results['n_noise']/len(kmeans_results['labels'])*100:.1f}%)")
        print(f"   • Silhouette Score: {dbscan_results['silhouette_score']:.3f}")
        
        # Distribución de clusters
        print(f"\n📊 DISTRIBUCIÓN DE CLUSTERS:")
        
        # K-Means distribution
        print(f"\nK-Means:")
        conteo_kmeans = pd.Series(kmeans_results['labels']).value_counts().sort_index()
        for cluster, count in conteo_kmeans.items():
            percentage = count / len(kmeans_results['labels']) * 100
            print(f"   Cluster {cluster}: {count:,} tweets ({percentage:.1f}%)")
        
        # DBSCAN distribution
        print(f"\nDBSCAN:")
        conteo_dbscan = pd.Series(dbscan_results['labels']).value_counts().sort_index()
        for cluster, count in conteo_dbscan.items():
            percentage = count / len(dbscan_results['labels']) * 100
            if cluster == -1:
                print(f"   Ruido: {count:,} tweets ({percentage:.1f}%)")
            else:
                print(f"   Cluster {cluster}: {count:,} tweets ({percentage:.1f}%)")
    
    def prepare_pca_visualization(self, X_scaled: np.ndarray) -> Tuple[np.ndarray, Dict]:
        """
        Prepara datos para visualización con PCA.
        
        Args:
            X_scaled (np.ndarray): Datos escalados
            
        Returns:
            Tuple[np.ndarray, Dict]: Datos PCA e información de varianza
        """
        print("🎨 Preparando datos para visualización con PCA...")
        
        self.pca = PCA(n_components=2, random_state=42)
        X_pca = self.pca.fit_transform(X_scaled)
        
        # Información de varianza explicada
        varianza_explicada = self.pca.explained_variance_ratio_
        pca_info = {
            'varianza_pc1': varianza_explicada[0],
            'varianza_pc2': varianza_explicada[1],
            'varianza_total': varianza_explicada.sum(),
            'components': self.pca.components_
        }
        
        print(f"\n📊 Información de PCA:")
        print(f"   • Varianza explicada PC1: {varianza_explicada[0]:.1%}")
        print(f"   • Varianza explicada PC2: {varianza_explicada[1]:.1%}")
        print(f"   • Varianza total explicada: {varianza_explicada.sum():.1%}")
        
        return X_pca, pca_info
    
    def plot_clusters_professional(self, X_pca: np.ndarray, labels: np.ndarray, 
                                  title: str, algorithm_name: str, 
                                  varianza_explicada: np.ndarray) -> plt.Figure:
        """
        Genera visualización profesional de clusters con PCA.
        
        Args:
            X_pca (np.ndarray): Datos reducidos con PCA
            labels (np.ndarray): Etiquetas de cluster
            title (str): Título del gráfico
            algorithm_name (str): Nombre del algoritmo
            varianza_explicada (np.ndarray): Varianza explicada por PCA
            
        Returns:
            plt.Figure: Figura de matplotlib
        """
        # Configurar figura
        fig, ax = plt.subplots(figsize=(12, 8))
        
        # Obtener clusters únicos
        unique_clusters = np.unique(labels)
        n_clusters = len(unique_clusters[unique_clusters != -1])  # Excluir ruido si existe
        
        # Paleta de colores profesional
        colors = plt.cm.Set1(np.linspace(0, 1, max(n_clusters, 3)))
        
        # Plot por cluster
        for i, cluster in enumerate(unique_clusters):
            if cluster == -1:  # Ruido en DBSCAN
                mask = labels == cluster
                ax.scatter(X_pca[mask, 0], X_pca[mask, 1], 
                          c='gray', marker='x', s=50, alpha=0.6, 
                          label=f'Ruido ({np.sum(mask)} puntos)')
            else:
                mask = labels == cluster
                ax.scatter(X_pca[mask, 0], X_pca[mask, 1], 
                          c=[colors[i]], s=60, alpha=0.7, 
                          label=f'Cluster {cluster} ({np.sum(mask)} puntos)')
        
        # Configuración del gráfico
        ax.set_xlabel(f'Componente Principal 1 ({varianza_explicada[0]:.1%} varianza)', fontsize=12)
        ax.set_ylabel(f'Componente Principal 2 ({varianza_explicada[1]:.1%} varianza)', fontsize=12)
        ax.set_title(f'{title}\n{algorithm_name}', fontsize=14, fontweight='bold', pad=20)
        ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        ax.grid(True, alpha=0.3)
        
        # Estilo profesional
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        
        plt.tight_layout()
        plt.show()
        
        return fig
    
    def visualize_clustering_results(self, X_pca: np.ndarray, results: Dict, 
                                   pca_info: Dict) -> Tuple[plt.Figure, plt.Figure]:
        """
        Genera visualizaciones de los resultados de clustering.
        
        Args:
            X_pca (np.ndarray): Datos PCA
            results (Dict): Resultados del clustering
            pca_info (Dict): Información de PCA
            
        Returns:
            Tuple[plt.Figure, plt.Figure]: Figuras de K-Means y DBSCAN
        """
        print(f"\n🎨 Generando visualizaciones...")
        
        varianza_explicada = np.array([pca_info['varianza_pc1'], pca_info['varianza_pc2']])
        
        # Visualización K-Means
        fig1 = self.plot_clusters_professional(
            X_pca, results['kmeans']['labels'], 
            '🔵 Análisis de Clustering con K-Means', 
            f'K-Means (k={results["kmeans"]["n_clusters"]}, Silhouette={results["kmeans"]["silhouette_score"]:.3f})',
            varianza_explicada
        )
        
        # Visualización DBSCAN
        fig2 = self.plot_clusters_professional(
            X_pca, results['dbscan']['labels'], 
            '🔴 Análisis de Clustering con DBSCAN', 
            f'DBSCAN (clusters={results["dbscan"]["n_clusters"]}, ruido={results["dbscan"]["n_noise"]}, Silhouette={results["dbscan"]["silhouette_score"]:.3f})',
            varianza_explicada
        )
        
        return fig1, fig2
    
    def generate_comparative_analysis(self, results: Dict) -> Dict:
        """
        Genera análisis comparativo de los algoritmos.
        
        Args:
            results (Dict): Resultados del clustering
            
        Returns:
            Dict: Análisis comparativo y recomendación
        """
        print("\n" + "="*80)
        print("🔍 ANÁLISIS COMPARATIVO DE CLUSTERING")
        print("="*80)
        
        # Tabla comparativa
        comparison_data = {
            'Algoritmo': ['K-Means', 'DBSCAN'],
            'Clusters': [results['kmeans']['n_clusters'], results['dbscan']['n_clusters']],
            'Silhouette Score': [results['kmeans']['silhouette_score'], results['dbscan']['silhouette_score']],
            'Puntos de Ruido': [0, results['dbscan']['n_noise']],
            '% Ruido': [0, results['dbscan']['n_noise']/len(results['kmeans']['labels'])*100]
        }
        
        comparison_df = pd.DataFrame(comparison_data)
        print(comparison_df.to_string(index=False, float_format='%.3f'))
        
        # Recomendación automática
        print(f"\n🎯 RECOMENDACIÓN AUTOMÁTICA:")
        
        if results['kmeans']['silhouette_score'] > results['dbscan']['silhouette_score']:
            mejor_algoritmo = "K-Means"
            mejor_score = results['kmeans']['silhouette_score']
            justificacion = (f"K-Means logra una mejor separación de clusters (Silhouette: {results['kmeans']['silhouette_score']:.3f}) "
                            f"comparado con DBSCAN (Silhouette: {results['dbscan']['silhouette_score']:.3f}). "
                            f"Los {results['kmeans']['n_clusters']} clusters están bien definidos y balanceados.")
        else:
            mejor_algoritmo = "DBSCAN"
            mejor_score = results['dbscan']['silhouette_score']
            justificacion = (f"DBSCAN logra una mejor separación de clusters (Silhouette: {results['dbscan']['silhouette_score']:.3f}) "
                            f"comparado con K-Means (Silhouette: {results['kmeans']['silhouette_score']:.3f}). "
                            f"Además, identifica {results['dbscan']['n_noise']} puntos como ruido, lo que puede ser valioso "
                            f"para detectar tweets atípicos.")
        
        recommendation = {
            'mejor_algoritmo': mejor_algoritmo,
            'mejor_score': mejor_score,
            'justificacion': justificacion,
            'comparison_table': comparison_df
        }
        
        print(f"\n✅ Algoritmo recomendado: {mejor_algoritmo}")
        print(f"📊 Silhouette Score: {mejor_score:.3f}")
        print(f"💡 Justificación: {justificacion}")
        
        return recommendation
    
    def add_cluster_labels_to_data(self, data: pd.DataFrame, results: Dict) -> pd.DataFrame:
        """
        Añade las etiquetas de cluster al DataFrame original.
        
        Args:
            data (pd.DataFrame): DataFrame original
            results (Dict): Resultados del clustering
            
        Returns:
            pd.DataFrame: DataFrame con etiquetas de cluster
        """
        data_with_clusters = data.copy()
        data_with_clusters['cluster_kmeans'] = results['kmeans']['labels']
        data_with_clusters['cluster_dbscan'] = results['dbscan']['labels']
        
        return data_with_clusters

    def find_optimal_k_elbow(self, X_scaled: np.ndarray, k_range: range = None) -> Tuple[int, Dict]:
        """
        Encuentra el número óptimo de clusters usando el método del codo.
        
        Args:
            X_scaled (np.ndarray): Datos escalados
            k_range (range): Rango de k a evaluar
            
        Returns:
            Tuple[int, Dict]: k óptimo e información del análisis
        """
        print("📈 Aplicando método del codo para encontrar k óptimo...")
        
        if k_range is None:
            k_range = range(2, 11)
        
        inercias = []
        silhouettes = []
        k_values = list(k_range)
        
        for k in k_values:
            # Entrenar K-Means con k clusters
            kmeans_temp = KMeans(n_clusters=k, random_state=42, n_init=10)
            labels_temp = kmeans_temp.fit_predict(X_scaled)
            
            # Calcular métricas
            inercias.append(kmeans_temp.inertia_)
            silhouettes.append(silhouette_score(X_scaled, labels_temp))
            
            print(f"   k={k}: Inercia={kmeans_temp.inertia_:.2f}, Silhouette={silhouettes[-1]:.3f}")
        
        # Encontrar el codo usando la segunda derivada
        optimal_k = self._find_elbow_point(k_values, inercias)
        
        # También encontrar k con mejor silhouette
        best_silhouette_k = k_values[np.argmax(silhouettes)]
        
        elbow_info = {
            'k_values': k_values,
            'inercias': inercias,
            'silhouettes': silhouettes,
            'optimal_k_elbow': optimal_k,
            'optimal_k_silhouette': best_silhouette_k,
            'recommended_k': best_silhouette_k  # Preferir silhouette sobre codo
        }
        
        print(f"\n🎯 Análisis de k óptimo:")
        print(f"   • K por método del codo: {optimal_k}")
        print(f"   • K por mejor silhouette: {best_silhouette_k}")
        print(f"   • K recomendado: {elbow_info['recommended_k']}")
        
        return elbow_info['recommended_k'], elbow_info
    
    def _find_elbow_point(self, k_values: List[int], inercias: List[float]) -> int:
        """
        Encuentra el punto del codo usando la segunda derivada.
        
        Args:
            k_values (List[int]): Valores de k
            inercias (List[float]): Valores de inercia
            
        Returns:
            int: k óptimo según el método del codo
        """
        # Calcular la segunda derivada
        if len(inercias) < 3:
            return k_values[0]
        
        # Normalizar las diferencias
        diffs = np.diff(inercias)
        second_diffs = np.diff(diffs)
        
        # El codo es donde la segunda derivada es máxima (más negativa)
        elbow_idx = np.argmax(second_diffs) + 1  # +1 porque perdimos un elemento en cada diff
        
        return k_values[elbow_idx] if elbow_idx < len(k_values) else k_values[-1]
    
    def plot_elbow_analysis(self, elbow_info: Dict) -> plt.Figure:
        """
        Genera gráficos del análisis del método del codo.
        
        Args:
            elbow_info (Dict): Información del análisis del codo
            
        Returns:
            plt.Figure: Figura con los gráficos
        """
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
        
        k_values = elbow_info['k_values']
        inercias = elbow_info['inercias']
        silhouettes = elbow_info['silhouettes']
        
        # Gráfico del método del codo
        ax1.plot(k_values, inercias, marker='o', linewidth=2, markersize=8)
        ax1.axvline(x=elbow_info['optimal_k_elbow'], color='red', linestyle='--', 
                   label=f'Codo k={elbow_info["optimal_k_elbow"]}')
        ax1.set_xlabel('Número de Clusters (k)')
        ax1.set_ylabel('Inercia (WCSS)')
        ax1.set_title('Método del Codo')
        ax1.grid(True, alpha=0.3)
        ax1.legend()
        
        # Gráfico de Silhouette Score
        ax2.plot(k_values, silhouettes, marker='s', linewidth=2, markersize=8, color='green')
        ax2.axvline(x=elbow_info['optimal_k_silhouette'], color='red', linestyle='--',
                   label=f'Mejor Silhouette k={elbow_info["optimal_k_silhouette"]}')
        ax2.set_xlabel('Número de Clusters (k)')
        ax2.set_ylabel('Silhouette Score')
        ax2.set_title('Análisis de Silhouette Score')
        ax2.grid(True, alpha=0.3)
        ax2.legend()
        
        plt.tight_layout()
        return fig

def perform_clustering_analysis(X_scaled: np.ndarray, 
                              data: pd.DataFrame = None,
                              config: Dict = None) -> Tuple[Dict, Dict, pd.DataFrame]:
    """
    Función principal para realizar análisis completo de clustering.
    
    Args:
        X_scaled (np.ndarray): Datos escalados
        data (pd.DataFrame): DataFrame original (opcional)
        config (Dict): Configuración de modelos (opcional)
        
    Returns:
        Tuple[Dict, Dict, pd.DataFrame]: Resultados, análisis comparativo, datos con clusters
    """
    analyzer = ClusteringAnalyzer(config=config)
    
    # Entrenar modelos
    results = analyzer.fit_clustering_models(X_scaled)
    
    # Imprimir resultados
    analyzer.print_clustering_results(results)
    
    # Preparar visualización
    X_pca, pca_info = analyzer.prepare_pca_visualization(X_scaled)
    
    # Generar visualizaciones
    fig1, fig2 = analyzer.visualize_clustering_results(X_pca, results, pca_info)
    
    # Análisis comparativo
    comparative_analysis = analyzer.generate_comparative_analysis(results)
    
    # Añadir clusters a datos si se proporcionan
    data_with_clusters = None
    if data is not None:
        data_with_clusters = analyzer.add_cluster_labels_to_data(data, results)
    
    print(f"\n✅ Análisis de clustering completado exitosamente")
    
    return results, comparative_analysis, data_with_clusters

if __name__ == "__main__":
    # Ejemplo de uso
    import sys
    sys.path.append('.')
    from data_loader import load_and_prepare_data
    from preprocessing import preprocess_twitter_data
    
    # Cargar y preprocesar datos
    data, _ = load_and_prepare_data()
    X_scaled, data_enhanced, features, _ = preprocess_twitter_data(data)
    
    # Realizar análisis de clustering
    results, analysis, data_clustered = perform_clustering_analysis(X_scaled, data_enhanced)
    
    print(f"\n✅ Ejemplo completado. Clusters K-Means: {results['kmeans']['n_clusters']}")
