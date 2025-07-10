# =============================================================================
# PIPELINE PRINCIPAL DE ANÁLISIS
# =============================================================================

"""
Script principal que orquesta todo el análisis de Machine Learning.
Integra carga de datos, preprocesamiento, clustering, regresión y visualización.
"""

import pandas as pd
import numpy as np
from datetime import datetime
from typing import Dict, Tuple, List, Optional, Any

# Importar módulos del proyecto
from config import PROJECT_CONFIG, CONFIG_INFO
from data_loader import load_and_prepare_data
from preprocessing import preprocess_twitter_data
from clustering import perform_clustering_analysis
from regression_models import train_regression_models
from visualization import create_comprehensive_visualizations

class TwitterAnalysisPipeline:
    """
    Pipeline principal para análisis completo de datos de Twitter.
    """
    
    def __init__(self, usuario_objetivo: str = 'interbank', 
                 target_variable: str = 'likes'):
        """
        Inicializa el pipeline.
        
        Args:
            usuario_objetivo (str): Usuario específico o 'todos'
            target_variable (str): Variable objetivo para regresión
        """
        self.usuario_objetivo = usuario_objetivo
        self.target_variable = target_variable
        self.results = {}
        self.timestamp = datetime.now()
        
        print("🚀 INICIANDO PIPELINE DE ANÁLISIS DE TWITTER")
        print("="*60)
        print(f"   • Usuario objetivo: {usuario_objetivo}")
        print(f"   • Variable objetivo: {target_variable}")
        print(f"   • Timestamp: {self.timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
        
    def run_complete_analysis(self) -> Dict[str, Any]:
        """
        Ejecuta el pipeline completo de análisis.
        
        Returns:
            Dict[str, Any]: Diccionario con todos los resultados
        """
        print("\n🔄 EJECUTANDO PIPELINE COMPLETO...")
        
        try:
            # 1. Carga de datos
            self._step_1_load_data()
            
            # 2. Preprocesamiento
            self._step_2_preprocessing()
            
            # 3. Análisis de clustering
            self._step_3_clustering()
            
            # 4. Modelos de regresión
            self._step_4_regression()
            
            # 5. Visualizaciones
            self._step_5_visualizations()
            
            # 6. Resumen final
            self._step_6_final_summary()
            
            print("\n🎉 PIPELINE COMPLETADO EXITOSAMENTE")
            return self.results
            
        except Exception as e:
            print(f"\n❌ ERROR EN EL PIPELINE: {str(e)}")
            raise e
    
    def _step_1_load_data(self) -> None:
        """
        Paso 1: Carga y preparación de datos.
        """
        print("\n" + "="*60)
        print("📂 PASO 1: CARGA DE DATOS")
        print("="*60)
        
        data, data_info = load_and_prepare_data(
            usuario_objetivo=self.usuario_objetivo
        )
        
        self.results['data_raw'] = data
        self.results['data_info'] = data_info
        
        print(f"✅ Datos cargados: {data.shape}")
        
    def _step_2_preprocessing(self) -> None:
        """
        Paso 2: Preprocesamiento y feature engineering.
        """
        print("\n" + "="*60)
        print("🔧 PASO 2: PREPROCESAMIENTO")
        print("="*60)
        
        X_scaled, data_enhanced, features, preprocess_info = preprocess_twitter_data(
            self.results['data_raw']
        )
        
        self.results['X_scaled'] = X_scaled
        self.results['data_enhanced'] = data_enhanced
        self.results['features'] = features
        self.results['preprocess_info'] = preprocess_info
        
        print(f"✅ Features preparadas: {len(features)}")
        print(f"✅ Datos escalados: {X_scaled.shape}")
        
    def _step_3_clustering(self) -> None:
        """
        Paso 3: Análisis de clustering.
        """
        print("\n" + "="*60)
        print("🔵 PASO 3: ANÁLISIS DE CLUSTERING")
        print("="*60)
        
        clustering_results, clustering_analysis, data_with_clusters = perform_clustering_analysis(
            self.results['X_scaled'],
            self.results['data_enhanced']
        )
        
        self.results['clustering_results'] = clustering_results
        self.results['clustering_analysis'] = clustering_analysis
        self.results['data_with_clusters'] = data_with_clusters
        
        print(f"✅ Clustering completado")
        print(f"   • K-Means: {clustering_results['kmeans']['n_clusters']} clusters")
        print(f"   • DBSCAN: {clustering_results['dbscan']['n_clusters']} clusters")
        
    def _step_4_regression(self) -> None:
        """
        Paso 4: Modelos de regresión.
        """
        print("\n" + "="*60)
        print("📈 PASO 4: MODELOS DE REGRESIÓN")
        print("="*60)
        
        regression_results, regression_recommendation = train_regression_models(
            self.results['data_enhanced'],
            self.results['features'],
            target_variable=self.target_variable
        )
        
        self.results['regression_results'] = regression_results
        self.results['regression_recommendation'] = regression_recommendation
        
        print(f"✅ Regresión completada")
        if regression_recommendation:
            print(f"   • Mejor modelo: {regression_recommendation['modelo']}")
            print(f"   • R² Score: {regression_recommendation['metrics']['R²']:.3f}")
        
    def _step_5_visualizations(self) -> None:
        """
        Paso 5: Generación de visualizaciones.
        """
        print("\n" + "="*60)
        print("🎨 PASO 5: VISUALIZACIONES")
        print("="*60)
        
        # Solo generar visualizaciones si hay resultados válidos
        if (len(self.results['regression_results']) > 0 and 
            self.results['clustering_results']):
            
            figures = create_comprehensive_visualizations(
                self.results['regression_results'],
                self.results['clustering_results'],
                self.results['regression_recommendation'],
                self.results['data_enhanced'],
                self.results['features'],
                self.target_variable
            )
            
            self.results['visualizations'] = figures
            print(f"✅ Visualizaciones generadas: {len(figures)}")
        else:
            print("⚠️ Omitiendo visualizaciones: datos insuficientes")
    
    def _step_6_final_summary(self) -> None:
        """
        Paso 6: Resumen final y validación.
        """
        print("\n" + "="*60)
        print("📊 PASO 6: RESUMEN FINAL")
        print("="*60)
        
        summary = self._generate_final_summary()
        self.results['final_summary'] = summary
        
        self._print_final_summary(summary)
        
    def _generate_final_summary(self) -> Dict[str, Any]:
        """
        Genera resumen final del análisis.
        
        Returns:
            Dict[str, Any]: Resumen completo
        """
        summary = {
            'timestamp': self.timestamp,
            'usuario_objetivo': self.usuario_objetivo,
            'target_variable': self.target_variable,
            'config_info': CONFIG_INFO
        }
        
        # Información de datos
        if 'data_info' in self.results:
            summary['data_summary'] = {
                'total_tweets': self.results['data_info']['total_tweets'],
                'total_usuarios': self.results['data_info']['total_usuarios'],
                'shape_final': self.results['data_info']['shape_filtrada']
            }
        
        # Información de features
        if 'preprocess_info' in self.results:
            summary['features_summary'] = {
                'total_features': self.results['preprocess_info']['n_features'],
                'features_engineered': len(self.results['preprocess_info']['features_engineered']),
                'features_originales': len(self.results['preprocess_info']['features_originales'])
            }
        
        # Mejores resultados
        if 'clustering_analysis' in self.results:
            summary['best_clustering'] = {
                'algoritmo': self.results['clustering_analysis']['mejor_algoritmo'],
                'silhouette_score': self.results['clustering_analysis']['mejor_score']
            }
        
        if 'regression_recommendation' in self.results and self.results['regression_recommendation']:
            summary['best_regression'] = {
                'modelo': self.results['regression_recommendation']['modelo'],
                'r2_score': self.results['regression_recommendation']['metrics']['R²'],
                'rmse': self.results['regression_recommendation']['metrics']['RMSE']
            }
        
        # Cumplimiento de objetivos
        summary['objectives_met'] = self._check_objectives_compliance()
        
        return summary
    
    def _check_objectives_compliance(self) -> Dict[str, bool]:
        """
        Verifica el cumplimiento de objetivos del proyecto.
        
        Returns:
            Dict[str, bool]: Estado de cumplimiento
        """
        compliance = {
            'modelos_implementados': False,
            'clustering_completado': False,
            'regresion_completada': False,
            'metricas_evaluadas': False,
            'justificacion_generada': False,
            'visualizaciones_creadas': False
        }
        
        # Verificar modelos implementados (2 clustering + 8 regresión = 10)
        clustering_count = 2 if 'clustering_results' in self.results else 0
        regression_count = len(self.results.get('regression_results', []))
        total_models = clustering_count + regression_count
        compliance['modelos_implementados'] = total_models >= 10
        
        # Verificar clustering
        compliance['clustering_completado'] = 'clustering_results' in self.results
        
        # Verificar regresión
        compliance['regresion_completada'] = len(self.results.get('regression_results', [])) >= 8
        
        # Verificar métricas
        if 'regression_results' in self.results:
            required_metrics = ['RMSE', 'MAE', 'R²']
            available_metrics = list(self.results['regression_results'].columns)
            compliance['metricas_evaluadas'] = all(m in available_metrics for m in required_metrics)
        
        # Verificar justificación
        compliance['justificacion_generada'] = (
            'regression_recommendation' in self.results and 
            self.results['regression_recommendation'] is not None
        )
        
        # Verificar visualizaciones
        compliance['visualizaciones_creadas'] = 'visualizations' in self.results
        
        return compliance
    
    def _print_final_summary(self, summary: Dict[str, Any]) -> None:
        """
        Imprime el resumen final.
        
        Args:
            summary (Dict[str, Any]): Resumen a imprimir
        """
        print("\n🎯 RESUMEN EJECUTIVO DEL ANÁLISIS:")
        
        if 'data_summary' in summary:
            data_sum = summary['data_summary']
            print(f"   • Dataset: {data_sum['total_tweets']:,} tweets de {data_sum['total_usuarios']} usuarios")
        
        if 'features_summary' in summary:
            feat_sum = summary['features_summary']
            print(f"   • Features: {feat_sum['total_features']} total ({feat_sum['features_engineered']} engineered)")
        
        if 'best_clustering' in summary:
            clust_sum = summary['best_clustering']
            print(f"   • Mejor clustering: {clust_sum['algoritmo']} (Silhouette: {clust_sum['silhouette_score']:.3f})")
        
        if 'best_regression' in summary:
            reg_sum = summary['best_regression']
            print(f"   • Mejor regresión: {reg_sum['modelo']} (R²: {reg_sum['r2_score']:.3f})")
        
        print(f"\n✅ CUMPLIMIENTO DE OBJETIVOS:")
        compliance = summary['objectives_met']
        for objetivo, cumplido in compliance.items():
            status = "✅" if cumplido else "❌"
            print(f"   {status} {objetivo.replace('_', ' ').title()}")
        
        # Porcentaje de cumplimiento
        cumplimiento_pct = sum(compliance.values()) / len(compliance) * 100
        print(f"\n📊 NIVEL DE CUMPLIMIENTO: {cumplimiento_pct:.1f}%")
        
        if cumplimiento_pct >= 80:
            print("🎉 ¡EXCELENTE! Proyecto completado satisfactoriamente")
        elif cumplimiento_pct >= 60:
            print("👍 BUENO: Objetivos principales cumplidos")
        else:
            print("⚠️ REQUIERE ATENCIÓN: Algunos objetivos no cumplidos")
    
    def export_results_summary(self, filename: str = None) -> str:
        """
        Exporta un resumen de resultados a archivo de texto.
        
        Args:
            filename (str): Nombre del archivo (opcional)
            
        Returns:
            str: Contenido del resumen
        """
        if filename is None:
            timestamp_str = self.timestamp.strftime('%Y%m%d_%H%M%S')
            filename = f"analisis_twitter_resumen_{timestamp_str}.txt"
        
        content = f"""
RESUMEN DE ANÁLISIS DE TWITTER - {self.timestamp.strftime('%Y-%m-%d %H:%M:%S')}
{'='*80}

CONFIGURACIÓN:
- Usuario objetivo: {self.usuario_objetivo}
- Variable objetivo: {self.target_variable}

DATOS PROCESADOS:
- Total tweets: {self.results['data_info']['total_tweets']:,}
- Total usuarios: {self.results['data_info']['total_usuarios']}
- Features utilizadas: {len(self.results['features'])}

RESULTADOS DE CLUSTERING:
- K-Means: {self.results['clustering_results']['kmeans']['n_clusters']} clusters, Silhouette: {self.results['clustering_results']['kmeans']['silhouette_score']:.3f}
- DBSCAN: {self.results['clustering_results']['dbscan']['n_clusters']} clusters, Silhouette: {self.results['clustering_results']['dbscan']['silhouette_score']:.3f}
- Mejor algoritmo: {self.results['clustering_analysis']['mejor_algoritmo']}

RESULTADOS DE REGRESIÓN:
"""
        
        if len(self.results['regression_results']) > 0:
            content += f"- Modelos evaluados: {len(self.results['regression_results'])}\n"
            if self.results['regression_recommendation']:
                rec = self.results['regression_recommendation']
                content += f"- Mejor modelo: {rec['modelo']}\n"
                content += f"- R² Score: {rec['metrics']['R²']:.3f}\n"
                content += f"- RMSE: {rec['metrics']['RMSE']:.3f}\n"
        
        content += f"""
CUMPLIMIENTO DE OBJETIVOS:
"""
        compliance = self.results['final_summary']['objectives_met']
        for obj, status in compliance.items():
            content += f"- {obj.replace('_', ' ').title()}: {'✅' if status else '❌'}\n"
        
        # Guardar archivo
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"📄 Resumen exportado a: {filename}")
        except Exception as e:
            print(f"⚠️ Error al exportar resumen: {e}")
        
        return content

def run_twitter_analysis(usuario_objetivo: str = 'interbank',
                        target_variable: str = 'likes',
                        export_summary: bool = True) -> Dict[str, Any]:
    """
    Función principal para ejecutar el análisis completo.
    
    Args:
        usuario_objetivo (str): Usuario específico o 'todos'
        target_variable (str): Variable objetivo para regresión
        export_summary (bool): Si exportar resumen a archivo
        
    Returns:
        Dict[str, Any]: Resultados completos del análisis
    """
    # Crear y ejecutar pipeline
    pipeline = TwitterAnalysisPipeline(
        usuario_objetivo=usuario_objetivo,
        target_variable=target_variable
    )
    
    results = pipeline.run_complete_analysis()
    
    # Exportar resumen si se solicita
    if export_summary:
        pipeline.export_results_summary()
    
    return results

if __name__ == "__main__":
    # Ejecución principal
    print("🚀 EJECUTANDO ANÁLISIS COMPLETO DE TWITTER")
    print("="*60)
    
    # Configuración principal (puedes modificar estos valores)
    USUARIO = 'interbank'  # Opciones: 'interbank', 'todos', etc.
    TARGET = 'likes'       # Opciones: 'likes', 'retweets', 'respuestas', etc.
    
    try:
        # Ejecutar análisis
        resultados = run_twitter_analysis(
            usuario_objetivo=USUARIO,
            target_variable=TARGET,
            export_summary=True
        )
        
        print(f"\n🎉 ANÁLISIS COMPLETADO EXITOSAMENTE")
        print(f"📊 Resultados disponibles en la variable 'resultados'")
        print(f"📄 Resumen exportado a archivo")
        
    except Exception as e:
        print(f"\n❌ ERROR DURANTE LA EJECUCIÓN: {str(e)}")
        print("Por favor, verifica que los datos estén disponibles y las dependencias instaladas.")
        raise e
