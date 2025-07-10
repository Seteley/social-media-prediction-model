# =============================================================================
# VISUALIZACIÓN Y ANÁLISIS GRÁFICO
# =============================================================================

"""
Módulo para generación de visualizaciones profesionales.
Incluye gráficos de métricas, comparaciones y análisis de resultados.
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict, List, Tuple, Optional, Any

class VisualizationManager:
    """
    Clase para manejar todas las visualizaciones del proyecto.
    """
    
    def __init__(self, style: str = 'seaborn-v0_8'):
        """
        Inicializa el manejador de visualizaciones.
        
        Args:
            style (str): Estilo de matplotlib
        """
        self.setup_style(style)
        
    def setup_style(self, style: str) -> None:
        """
        Configura el estilo de las visualizaciones.
        
        Args:
            style (str): Estilo a aplicar
        """
        plt.style.use(style)
        sns.set_palette("husl")
        plt.rcParams['figure.figsize'] = (12, 8)
        plt.rcParams['font.size'] = 12
        
    def plot_regression_metrics_individual(self, resultados_df: pd.DataFrame, 
                                         target_variable: str) -> List[plt.Figure]:
        """
        Genera gráficos individuales para cada métrica de regresión.
        
        Args:
            resultados_df (pd.DataFrame): DataFrame con resultados
            target_variable (str): Variable objetivo
            
        Returns:
            List[plt.Figure]: Lista de figuras generadas
        """
        if len(resultados_df) == 0:
            print("❌ No hay datos para visualizar")
            return []
        
        print(f"\n🎨 Generando visualizaciones individuales para mejor claridad...")
        
        figures = []
        
        # 1. GRÁFICO DE RMSE
        fig1 = self._plot_metric_bar(
            resultados_df, 'RMSE', target_variable,
            'RMSE (Root Mean Square Error)',
            'lightcoral', 'darkred',
            lower_is_better=True
        )
        figures.append(fig1)
        
        # 2. GRÁFICO DE MAE
        fig2 = self._plot_metric_bar(
            resultados_df, 'MAE', target_variable,
            'MAE (Mean Absolute Error)',
            'lightgreen', 'darkgreen',
            lower_is_better=True
        )
        figures.append(fig2)
        
        # 3. GRÁFICO DE R² SCORE
        fig3 = self._plot_metric_bar(
            resultados_df, 'R²', target_variable,
            'R² Score (Coeficiente de Determinación)',
            'lightblue', 'darkblue',
            lower_is_better=False
        )
        figures.append(fig3)
        
        # 4. GRÁFICO DE EXPLAINED VARIANCE SCORE
        if 'EVS' in resultados_df.columns:
            fig4 = self._plot_metric_bar(
                resultados_df, 'EVS', target_variable,
                'EVS (Explained Variance Score)',
                'lightyellow', 'orange',
                lower_is_better=False
            )
            figures.append(fig4)
        
        return figures
    
    def _plot_metric_bar(self, resultados_df: pd.DataFrame, metric: str, 
                        target_variable: str, ylabel: str, 
                        color: str, best_color: str, 
                        lower_is_better: bool = True) -> plt.Figure:
        """
        Genera un gráfico de barras para una métrica específica.
        
        Args:
            resultados_df (pd.DataFrame): DataFrame con resultados
            metric (str): Nombre de la métrica
            target_variable (str): Variable objetivo
            ylabel (str): Etiqueta del eje Y
            color (str): Color de las barras
            best_color (str): Color para la mejor barra
            lower_is_better (bool): Si menor valor es mejor
            
        Returns:
            plt.Figure: Figura generada
        """
        plt.figure(figsize=(12, 6))
        bars = plt.bar(resultados_df['Modelo'], resultados_df[metric], 
                      color=color, alpha=0.8, edgecolor=best_color, linewidth=1)
        
        plt.title(f'📊 {metric} por Modelo - Variable: {target_variable.upper()}', 
                  fontsize=14, fontweight='bold', pad=20)
        plt.ylabel(ylabel, fontsize=12)
        plt.xlabel('Modelos de Regresión', fontsize=12)
        plt.xticks(rotation=45, ha='right')
        plt.grid(True, alpha=0.3, axis='y')
        
        # Destacar el mejor modelo
        if lower_is_better:
            best_idx = resultados_df[metric].idxmin()
        else:
            best_idx = resultados_df[metric].idxmax()
        
        bars[best_idx].set_color(best_color)
        bars[best_idx].set_alpha(1.0)
        
        # Añadir valores en las barras
        for i, bar in enumerate(bars):
            height = bar.get_height()
            plt.text(bar.get_x() + bar.get_width()/2., height + height*0.01,
                    f'{height:.3f}', ha='center', va='bottom', fontsize=10)
        
        plt.tight_layout()
        plt.show()
        
        return plt.gcf()
    
    def plot_model_comparison_heatmap(self, resultados_df: pd.DataFrame) -> plt.Figure:
        """
        Genera un heatmap comparativo de todas las métricas.
        
        Args:
            resultados_df (pd.DataFrame): DataFrame con resultados
            
        Returns:
            plt.Figure: Figura del heatmap
        """
        if len(resultados_df) == 0:
            print("❌ No hay datos para el heatmap")
            return None
        
        print("🎨 Generando heatmap comparativo...")
        
        # Seleccionar métricas numéricas para el heatmap
        numeric_cols = ['RMSE', 'MAE', 'R²', 'EVS', 'CV_R²_mean']
        available_cols = [col for col in numeric_cols if col in resultados_df.columns]
        
        if not available_cols:
            print("❌ No hay métricas disponibles para el heatmap")
            return None
        
        # Preparar datos para heatmap
        heatmap_data = resultados_df.set_index('Modelo')[available_cols]
        
        # Normalizar datos para mejor visualización
        heatmap_norm = heatmap_data.copy()
        for col in available_cols:
            if col in ['RMSE', 'MAE']:  # Menor es mejor
                heatmap_norm[col] = 1 - (heatmap_data[col] - heatmap_data[col].min()) / (heatmap_data[col].max() - heatmap_data[col].min())
            else:  # Mayor es mejor
                heatmap_norm[col] = (heatmap_data[col] - heatmap_data[col].min()) / (heatmap_data[col].max() - heatmap_data[col].min())
        
        # Crear heatmap
        fig, ax = plt.subplots(figsize=(10, 8))
        sns.heatmap(heatmap_norm.T, annot=True, cmap='RdYlGn', fmt='.3f',
                   cbar_kws={'label': 'Rendimiento Normalizado (0-1)'}, ax=ax)
        
        plt.title('🔥 Heatmap Comparativo de Rendimiento de Modelos', 
                 fontsize=14, fontweight='bold', pad=20)
        plt.xlabel('Modelos de Machine Learning', fontsize=12)
        plt.ylabel('Métricas de Evaluación', fontsize=12)
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        plt.show()
        
        return fig
    
    def plot_performance_radar_chart(self, resultados_df: pd.DataFrame, 
                                   top_n: int = 5) -> plt.Figure:
        """
        Genera un gráfico radar para los mejores modelos.
        
        Args:
            resultados_df (pd.DataFrame): DataFrame con resultados
            top_n (int): Número de mejores modelos a mostrar
            
        Returns:
            plt.Figure: Figura del radar chart
        """
        if len(resultados_df) == 0:
            print("❌ No hay datos para el radar chart")
            return None
        
        print(f"🎨 Generando radar chart para los {top_n} mejores modelos...")
        
        # Seleccionar top modelos por R²
        top_models = resultados_df.nlargest(top_n, 'R²')
        
        # Métricas para el radar
        metrics = ['R²', 'RMSE', 'MAE', 'CV_R²_mean']
        available_metrics = [m for m in metrics if m in top_models.columns]
        
        if len(available_metrics) < 3:
            print("❌ No hay suficientes métricas para el radar chart")
            return None
        
        # Normalizar métricas
        radar_data = []
        for _, model in top_models.iterrows():
            model_scores = []
            for metric in available_metrics:
                if metric in ['RMSE', 'MAE']:  # Menor es mejor
                    score = 1 - (model[metric] - resultados_df[metric].min()) / (resultados_df[metric].max() - resultados_df[metric].min())
                else:  # Mayor es mejor
                    score = (model[metric] - resultados_df[metric].min()) / (resultados_df[metric].max() - resultados_df[metric].min())
                model_scores.append(score)
            radar_data.append(model_scores)
        
        # Crear radar chart
        angles = np.linspace(0, 2 * np.pi, len(available_metrics), endpoint=False).tolist()
        angles += angles[:1]  # Cerrar el círculo
        
        fig, ax = plt.subplots(figsize=(10, 10), subplot_kw=dict(projection='polar'))
        
        colors = plt.cm.Set1(np.linspace(0, 1, len(top_models)))
        
        for i, (_, model) in enumerate(top_models.iterrows()):
            values = radar_data[i] + radar_data[i][:1]  # Cerrar el círculo
            ax.plot(angles, values, 'o-', linewidth=2, label=model['Modelo'], color=colors[i])
            ax.fill(angles, values, alpha=0.25, color=colors[i])
        
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(available_metrics)
        ax.set_ylim(0, 1)
        ax.set_title(f'🎯 Radar Chart: Top {top_n} Modelos', 
                    fontsize=14, fontweight='bold', pad=30)
        ax.legend(loc='upper right', bbox_to_anchor=(1.2, 1.0))
        ax.grid(True)
        
        plt.tight_layout()
        plt.show()
        
        return fig
    
    def plot_clustering_comparison(self, clustering_results: Dict) -> plt.Figure:
        """
        Genera gráfico comparativo de clustering.
        
        Args:
            clustering_results (Dict): Resultados de clustering
            
        Returns:
            plt.Figure: Figura comparativa
        """
        print("🎨 Generando gráfico comparativo de clustering...")
        
        # Datos para comparación
        algorithms = ['K-Means', 'DBSCAN']
        silhouette_scores = [
            clustering_results['kmeans']['silhouette_score'],
            clustering_results['dbscan']['silhouette_score']
        ]
        n_clusters = [
            clustering_results['kmeans']['n_clusters'],
            clustering_results['dbscan']['n_clusters']
        ]
        
        # Crear subplot
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
        
        # Gráfico 1: Silhouette Scores
        bars1 = ax1.bar(algorithms, silhouette_scores, 
                       color=['lightblue', 'lightcoral'], 
                       edgecolor=['darkblue', 'darkred'], linewidth=2)
        ax1.set_title('📊 Silhouette Score por Algoritmo', fontsize=14, fontweight='bold')
        ax1.set_ylabel('Silhouette Score', fontsize=12)
        ax1.set_ylim(0, 1)
        ax1.grid(True, alpha=0.3, axis='y')
        
        # Añadir valores en las barras
        for bar, score in zip(bars1, silhouette_scores):
            height = bar.get_height()
            ax1.text(bar.get_x() + bar.get_width()/2., height + 0.01,
                    f'{score:.3f}', ha='center', va='bottom', fontsize=11, fontweight='bold')
        
        # Gráfico 2: Número de Clusters
        bars2 = ax2.bar(algorithms, n_clusters, 
                       color=['lightgreen', 'lightyellow'], 
                       edgecolor=['darkgreen', 'orange'], linewidth=2)
        ax2.set_title('📊 Número de Clusters', fontsize=14, fontweight='bold')
        ax2.set_ylabel('Número de Clusters', fontsize=12)
        ax2.grid(True, alpha=0.3, axis='y')
        
        # Añadir valores en las barras
        for bar, clusters in zip(bars2, n_clusters):
            height = bar.get_height()
            ax2.text(bar.get_x() + bar.get_width()/2., height + 0.05,
                    f'{clusters}', ha='center', va='bottom', fontsize=11, fontweight='bold')
        
        plt.tight_layout()
        plt.show()
        
        return fig
    
    def plot_feature_importance_analysis(self, data: pd.DataFrame, 
                                       features: List[str], 
                                       target: str) -> plt.Figure:
        """
        Genera análisis de correlaciones como proxy de importancia.
        
        Args:
            data (pd.DataFrame): DataFrame con datos
            features (List[str]): Lista de features
            target (str): Variable objetivo
            
        Returns:
            plt.Figure: Figura de correlaciones
        """
        print("🎨 Generando análisis de correlaciones...")
        
        # Calcular correlaciones con la variable objetivo
        correlations = []
        for feature in features:
            if feature != target and feature in data.columns:
                corr = data[feature].corr(data[target])
                correlations.append({'Feature': feature, 'Correlation': abs(corr)})
        
        if not correlations:
            print("❌ No se pueden calcular correlaciones")
            return None
        
        corr_df = pd.DataFrame(correlations).sort_values('Correlation', ascending=True)
        
        # Crear gráfico horizontal
        fig, ax = plt.subplots(figsize=(12, 8))
        bars = ax.barh(corr_df['Feature'], corr_df['Correlation'], 
                      color='skyblue', edgecolor='navy', linewidth=1)
        
        ax.set_title(f'🔍 Correlación de Features con {target.title()}', 
                    fontsize=14, fontweight='bold', pad=20)
        ax.set_xlabel('Correlación Absoluta', fontsize=12)
        ax.set_ylabel('Features', fontsize=12)
        ax.grid(True, alpha=0.3, axis='x')
        
        # Añadir valores
        for bar, corr in zip(bars, corr_df['Correlation']):
            width = bar.get_width()
            ax.text(width + 0.01, bar.get_y() + bar.get_height()/2,
                   f'{corr:.3f}', ha='left', va='center', fontsize=10)
        
        plt.tight_layout()
        plt.show()
        
        return fig
    
    def create_summary_dashboard(self, regression_results: pd.DataFrame,
                               clustering_results: Dict,
                               recommendation: Dict,
                               target_variable: str) -> plt.Figure:
        """
        Crea un dashboard resumen con los principales resultados.
        
        Args:
            regression_results (pd.DataFrame): Resultados de regresión
            clustering_results (Dict): Resultados de clustering
            recommendation (Dict): Recomendación de modelo
            target_variable (str): Variable objetivo
            
        Returns:
            plt.Figure: Dashboard completo
        """
        print("🎨 Creando dashboard resumen...")
        
        fig = plt.figure(figsize=(16, 12))
        
        # Layout del dashboard
        gs = fig.add_gridspec(3, 3, hspace=0.3, wspace=0.3)
        
        # 1. Top 5 modelos de regresión
        ax1 = fig.add_subplot(gs[0, :2])
        if len(regression_results) > 0:
            top_5 = regression_results.head(5)
            bars = ax1.bar(top_5['Modelo'], top_5['R²'], 
                          color='lightblue', edgecolor='darkblue')
            ax1.set_title('🏆 Top 5 Modelos de Regresión (R²)', fontweight='bold')
            ax1.set_ylabel('R² Score')
            ax1.tick_params(axis='x', rotation=45)
            ax1.grid(True, alpha=0.3, axis='y')
            
            # Destacar el mejor
            bars[0].set_color('gold')
            
            # Añadir valores
            for bar in bars:
                height = bar.get_height()
                ax1.text(bar.get_x() + bar.get_width()/2., height + 0.005,
                        f'{height:.3f}', ha='center', va='bottom', fontsize=9)
        
        # 2. Comparación de clustering
        ax2 = fig.add_subplot(gs[0, 2])
        if clustering_results:
            algorithms = ['K-Means', 'DBSCAN']
            silhouette_scores = [
                clustering_results['kmeans']['silhouette_score'],
                clustering_results['dbscan']['silhouette_score']
            ]
            ax2.bar(algorithms, silhouette_scores, 
                   color=['lightcoral', 'lightgreen'])
            ax2.set_title('🔵 Clustering\n(Silhouette Score)', fontweight='bold')
            ax2.set_ylabel('Score')
            ax2.tick_params(axis='x', rotation=45)
            ax2.grid(True, alpha=0.3, axis='y')
        
        # 3. Distribución de métricas
        ax3 = fig.add_subplot(gs[1, :])
        if len(regression_results) > 0:
            metrics = ['RMSE', 'MAE', 'R²']
            available_metrics = [m for m in metrics if m in regression_results.columns]
            
            if available_metrics:
                x = np.arange(len(regression_results))
                width = 0.25
                
                for i, metric in enumerate(available_metrics):
                    offset = (i - len(available_metrics)//2) * width
                    ax3.bar(x + offset, regression_results[metric], 
                           width, label=metric, alpha=0.7)
                
                ax3.set_title('📊 Distribución de Métricas por Modelo', fontweight='bold')
                ax3.set_xlabel('Modelos')
                ax3.set_ylabel('Valor de Métrica')
                ax3.set_xticks(x)
                ax3.set_xticklabels(regression_results['Modelo'], rotation=45, ha='right')
                ax3.legend()
                ax3.grid(True, alpha=0.3, axis='y')
        
        # 4. Información de recomendación
        ax4 = fig.add_subplot(gs[2, :])
        ax4.axis('off')
        
        if recommendation:
            info_text = f"""
🏆 MODELO RECOMENDADO: {recommendation['modelo']}

📊 MÉTRICAS PRINCIPALES:
• R² Score: {recommendation['metrics']['R²']:.3f}
• RMSE: {recommendation['metrics']['RMSE']:.3f}  
• MAE: {recommendation['metrics']['MAE']:.3f}
• CV R²: {recommendation['metrics']['CV_R²_mean']:.3f} ± {recommendation['metrics']['CV_R²_std']:.3f}

🎯 VARIABLE OBJETIVO: {target_variable.upper()}
📈 EXPLICACIÓN: El modelo explica {recommendation['metrics']['R²']*100:.1f}% de la variabilidad
⚡ RENDIMIENTO: Error promedio de {recommendation['metrics']['RMSE']:.1f} unidades
            """
            ax4.text(0.05, 0.95, info_text, transform=ax4.transAxes, 
                    fontsize=11, verticalalignment='top', 
                    bbox=dict(boxstyle="round,pad=0.5", facecolor="lightblue", alpha=0.8))
        
        plt.suptitle(f'📊 DASHBOARD RESUMEN - ANÁLISIS DE {target_variable.upper()}', 
                     fontsize=16, fontweight='bold', y=0.98)
        
        plt.tight_layout(rect=[0, 0, 1, 0.96])
        plt.show()
        
        return fig

def create_comprehensive_visualizations(regression_results: pd.DataFrame,
                                      clustering_results: Dict,
                                      recommendation: Dict,
                                      data: pd.DataFrame,
                                      features: List[str],
                                      target_variable: str) -> Dict[str, plt.Figure]:
    """
    Función principal para crear todas las visualizaciones.
    
    Args:
        regression_results (pd.DataFrame): Resultados de regresión
        clustering_results (Dict): Resultados de clustering
        recommendation (Dict): Recomendación de modelo
        data (pd.DataFrame): DataFrame con datos
        features (List[str]): Lista de features
        target_variable (str): Variable objetivo
        
    Returns:
        Dict[str, plt.Figure]: Diccionario con todas las figuras
    """
    viz_manager = VisualizationManager()
    figures = {}
    
    # Visualizaciones de regresión
    regression_figs = viz_manager.plot_regression_metrics_individual(regression_results, target_variable)
    for i, fig in enumerate(regression_figs):
        figures[f'regression_metric_{i+1}'] = fig
    
    # Heatmap comparativo
    heatmap_fig = viz_manager.plot_model_comparison_heatmap(regression_results)
    if heatmap_fig:
        figures['heatmap_comparison'] = heatmap_fig
    
    # Radar chart
    radar_fig = viz_manager.plot_performance_radar_chart(regression_results)
    if radar_fig:
        figures['radar_chart'] = radar_fig
    
    # Comparación de clustering
    if clustering_results:
        clustering_fig = viz_manager.plot_clustering_comparison(clustering_results)
        figures['clustering_comparison'] = clustering_fig
    
    # Análisis de features
    feature_fig = viz_manager.plot_feature_importance_analysis(data, features, target_variable)
    if feature_fig:
        figures['feature_importance'] = feature_fig
    
    # Dashboard resumen
    dashboard_fig = viz_manager.create_summary_dashboard(
        regression_results, clustering_results, recommendation, target_variable
    )
    figures['dashboard_summary'] = dashboard_fig
    
    print(f"\n✅ Se generaron {len(figures)} visualizaciones")
    
    return figures

if __name__ == "__main__":
    # Ejemplo de uso
    print("🎨 Módulo de visualización listo para usar")
    print("Importa las funciones necesarias y pasa los datos para generar visualizaciones.")
