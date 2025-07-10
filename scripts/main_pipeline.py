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
from config import PROJECT_CONFIG, CONFIG_INFO, CUENTAS_DISPONIBLES
from data_loader import MultiAccountDataLoader, load_and_prepare_data
from preprocessing import MultiAccountDataPreprocessor, preprocess_twitter_data
from clustering import perform_clustering_analysis
from regression_models import train_regression_models
from visualization import create_comprehensive_visualizations

class TwitterAnalysisPipeline:
    """
    Pipeline principal para análisis completo de datos de Twitter multi-cuenta.
    """
    
    def __init__(self, target_accounts: List[str] = None, 
                 target_variable: str = 'likes',
                 analysis_mode: str = 'consolidado'):
        """
        Inicializa el pipeline.
        
        Args:
            target_accounts (List[str]): Lista de cuentas objetivo o None para todas
            target_variable (str): Variable objetivo para regresión
            analysis_mode (str): Modo de análisis ('individual', 'comparativo', 'consolidado')
        """
        self.target_accounts = target_accounts or CUENTAS_DISPONIBLES
        self.target_variable = target_variable
        self.analysis_mode = analysis_mode
        self.results = {}
        self.timestamp = datetime.now()
        
        print("🚀 PIPELINE DE ANÁLISIS DE TWITTER MULTI-CUENTA")
        print("="*70)
        print(f"   • Cuentas objetivo: {self.target_accounts}")
        print(f"   • Variable objetivo: {target_variable}")
        print(f"   • Modo de análisis: {analysis_mode}")
        print(f"   • Timestamp: {self.timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
        
    def run_complete_analysis(self) -> Dict[str, Any]:
        """
        Ejecuta el pipeline completo de análisis multi-cuenta.
        
        Returns:
            Dict[str, Any]: Diccionario con todos los resultados
        """
        print("\n🔄 EJECUTANDO PIPELINE COMPLETO MULTI-CUENTA...")
        
        try:
            # 1. Carga de datos multi-cuenta
            self._step_1_load_multi_account_data()
            
            # 2. Preprocesamiento multi-cuenta
            self._step_2_preprocessing_multi_account()
            
            # 3. Análisis según el modo seleccionado
            if self.analysis_mode == 'individual':
                self._step_3_individual_analysis()
            elif self.analysis_mode == 'comparativo':
                self._step_3_comparative_analysis()
            else:  # consolidado
                self._step_3_consolidated_analysis()
            
            # 4. Resumen final
            self._step_4_final_summary()
            
            print("\n🎉 PIPELINE MULTI-CUENTA COMPLETADO EXITOSAMENTE")
            return self.results
            
        except Exception as e:
            print(f"\n❌ ERROR EN EL PIPELINE: {str(e)}")
            raise e
    
    
    def _step_1_load_multi_account_data(self) -> None:
        """
        Paso 1: Carga y preparación de datos multi-cuenta.
        """
        print("\n" + "="*70)
        print("📂 PASO 1: CARGA DE DATOS MULTI-CUENTA")
        print("="*70)
        
        # Inicializar loader
        loader = MultiAccountDataLoader()
        
        # Cargar datos consolidados
        consolidated_data = loader.load_consolidated_data(
            target_accounts=self.target_accounts,
            mode=self.analysis_mode
        )
        
        if not consolidated_data:
            raise ValueError("No se pudieron cargar datos para las cuentas especificadas")
        
        self.results['consolidated_data'] = consolidated_data
        self.results['loader_info'] = {
            'target_accounts': self.target_accounts,
            'analysis_mode': self.analysis_mode,
            'data_types': list(consolidated_data.keys())
        }
        
        # Mostrar información de carga
        for data_type, df in consolidated_data.items():
            print(f"✅ {data_type}: {df.shape}")
        
    def _step_2_preprocessing_multi_account(self) -> None:
        """
        Paso 2: Preprocesamiento multi-cuenta.
        """
        print("\n" + "="*70)
        print("🔧 PASO 2: PREPROCESAMIENTO MULTI-CUENTA")
        print("="*70)
        
        # Inicializar preprocessor
        preprocessor = MultiAccountDataPreprocessor()
        
        # Preprocesar datos consolidados
        preprocessing_results = preprocessor.preprocess_multi_account_data(
            self.results['consolidated_data'],
            target_accounts=self.target_accounts
        )
        
        self.results['preprocessing_results'] = preprocessing_results
        self.results['preprocessor'] = preprocessor
        
        # Mostrar resultados
        for data_type, result in preprocessing_results.items():
            if 'error' not in result:
                print(f"✅ {data_type}: {result['X_scaled'].shape}")
            else:
                print(f"❌ Error en {data_type}: {result['error']}")
        
    def _step_3_consolidated_analysis(self) -> None:
        """
        Paso 3: Análisis consolidado (todas las cuentas juntas).
        """
        print("\n" + "="*70)
        print("🔵 PASO 3: ANÁLISIS CONSOLIDADO")
        print("="*70)
        
        # Usar datos 'clean' como primarios, 'metricas' como complementarios
        primary_data_type = 'clean' if 'clean' in self.results['preprocessing_results'] else list(self.results['preprocessing_results'].keys())[0]
        primary_result = self.results['preprocessing_results'][primary_data_type]
        
        if 'error' in primary_result:
            print(f"❌ No se puede realizar análisis: {primary_result['error']}")
            return
        
        # Clustering
        clustering_results, clustering_analysis, data_with_clusters = perform_clustering_analysis(
            primary_result['X_scaled'],
            primary_result['data_enhanced']
        )
        
        # Regresión
        regression_results, regression_recommendation = train_regression_models(
            primary_result['data_enhanced'],
            primary_result['features'],
            target_variable=self.target_variable
        )
        
        # Visualizaciones
        if len(regression_results) > 0 and clustering_results:
            figures = create_comprehensive_visualizations(
                regression_results,
                clustering_results,
                regression_recommendation,
                primary_result['data_enhanced'],
                primary_result['features'],
                self.target_variable
            )
            self.results['visualizations'] = figures
        
        # Guardar resultados
        self.results['clustering_results'] = clustering_results
        self.results['clustering_analysis'] = clustering_analysis
        self.results['data_with_clusters'] = data_with_clusters
        self.results['regression_results'] = regression_results
        self.results['regression_recommendation'] = regression_recommendation
        self.results['primary_data_type'] = primary_data_type
        
        print(f"✅ Análisis consolidado completado usando datos '{primary_data_type}'")
        if regression_recommendation:
            print(f"   • Mejor modelo: {regression_recommendation['modelo']}")
            print(f"   • R² Score: {regression_recommendation['metrics']['R²']:.3f}")
    
    def _step_3_individual_analysis(self) -> None:
        """
        Paso 3: Análisis individual por cuenta.
        """
        print("\n" + "="*70)
        print("🔵 PASO 3: ANÁLISIS INDIVIDUAL POR CUENTA")
        print("="*70)
        
        individual_results = {}
        
        for account in self.target_accounts:
            print(f"\n📊 Analizando cuenta: {account}")
            
            # Cargar datos individuales para esta cuenta
            loader = MultiAccountDataLoader()
            account_data = loader.load_individual_account_data(account)
            
            if not account_data:
                print(f"   ⚠️ No hay datos para {account}")
                continue
            
            # Preprocesar datos de la cuenta
            preprocessor = MultiAccountDataPreprocessor()
            account_preprocessing = preprocessor.preprocess_multi_account_data(
                account_data, target_accounts=[account]
            )
            
            # Análisis para esta cuenta
            primary_data_type = 'clean' if 'clean' in account_preprocessing else list(account_preprocessing.keys())[0]
            primary_result = account_preprocessing[primary_data_type]
            
            if 'error' in primary_result:
                print(f"   ❌ Error en {account}: {primary_result['error']}")
                continue
            
            # Análisis de clustering y regresión para esta cuenta
            try:
                clustering_results, _, _ = perform_clustering_analysis(
                    primary_result['X_scaled'],
                    primary_result['data_enhanced']
                )
                
                regression_results, regression_recommendation = train_regression_models(
                    primary_result['data_enhanced'],
                    primary_result['features'],
                    target_variable=self.target_variable
                )
                
                individual_results[account] = {
                    'preprocessing': account_preprocessing,
                    'clustering': clustering_results,
                    'regression': regression_results,
                    'recommendation': regression_recommendation
                }
                
                print(f"   ✅ {account} analizado exitosamente")
                
            except Exception as e:
                print(f"   ❌ Error analizando {account}: {str(e)}")
        
        self.results['individual_results'] = individual_results
        print(f"\n✅ Análisis individual completado para {len(individual_results)} cuentas")
    
    def _step_3_comparative_analysis(self) -> None:
        """
        Paso 3: Análisis comparativo entre cuentas.
        """
        print("\n" + "="*70)
        print("🔵 PASO 3: ANÁLISIS COMPARATIVO")
        print("="*70)
        
        # Primero realizar análisis individual
        self._step_3_individual_analysis()
        
        # Luego análisis consolidado para comparación
        self._step_3_consolidated_analysis()
        
        # Análisis comparativo específico
        if 'individual_results' in self.results and self.results['individual_results']:
            comparative_metrics = self._generate_comparative_metrics()
            self.results['comparative_metrics'] = comparative_metrics
            
            print("✅ Análisis comparativo completado")
        else:
            print("⚠️ No hay suficientes datos individuales para comparación")
            
    def _generate_comparative_metrics(self) -> Dict:
        """
        Genera métricas comparativas entre cuentas.
        """
        comparative_data = {
            'account_performance': {},
            'model_performance': {},
            'engagement_metrics': {}
        }
        
        for account, results in self.results['individual_results'].items():
            if 'recommendation' in results and results['recommendation']:
                rec = results['recommendation']
                comparative_data['account_performance'][account] = {
                    'best_model': rec['modelo'],
                    'r2_score': rec['metrics']['R²'],
                    'rmse': rec['metrics']['RMSE'],
                    'samples': results['preprocessing']['clean']['info']['n_samples'] if 'clean' in results['preprocessing'] else 0
                }
        
        return comparative_data
        
    def _step_4_final_summary(self) -> None:
        """
        Paso 4: Resumen final y validación.
        """
        print("\n" + "="*70)
        print("� PASO 4: RESUMEN FINAL")
        print("="*70)
        
        summary = self._generate_final_summary()
        self.results['final_summary'] = summary
        
        self._print_final_summary(summary)
    
    def _generate_final_summary(self) -> Dict:
        """
        Genera un resumen completo del análisis.
        """
        summary = {
            'pipeline_info': {
                'target_accounts': self.target_accounts,
                'analysis_mode': self.analysis_mode,
                'target_variable': self.target_variable,
                'timestamp': self.timestamp.isoformat(),
                'duration': (datetime.now() - self.timestamp).total_seconds()
            },
            'data_summary': {},
            'analysis_summary': {},
            'recommendations': []
        }
        
        # Resumen de datos
        if 'consolidated_data' in self.results:
            summary['data_summary'] = {
                'data_types_loaded': list(self.results['consolidated_data'].keys()),
                'accounts_processed': self.target_accounts,
                'total_records': sum(df.shape[0] for df in self.results['consolidated_data'].values())
            }
        
        # Resumen de análisis según el modo
        if self.analysis_mode == 'individual' and 'individual_results' in self.results:
            summary['analysis_summary']['individual'] = {
                'accounts_analyzed': len(self.results['individual_results']),
                'successful_analyses': len([r for r in self.results['individual_results'].values() 
                                          if 'recommendation' in r and r['recommendation']])
            }
        
        if 'regression_recommendation' in self.results and self.results['regression_recommendation']:
            summary['analysis_summary']['best_model'] = self.results['regression_recommendation']
            summary['recommendations'].append(
                f"El mejor modelo es {self.results['regression_recommendation']['modelo']} "
                f"con R² = {self.results['regression_recommendation']['metrics']['R²']:.3f}"
            )
        
        return summary
    
    def _print_final_summary(self, summary: Dict) -> None:
        """
        Imprime el resumen final.
        """
        print("📋 RESUMEN DEL ANÁLISIS:")
        print(f"   • Modo: {summary['pipeline_info']['analysis_mode']}")
        print(f"   • Cuentas: {len(summary['pipeline_info']['target_accounts'])}")
        print(f"   • Duración: {summary['pipeline_info']['duration']:.2f}s")
        
        if 'data_summary' in summary:
            print(f"   • Registros totales: {summary['data_summary']['total_records']:,}")
            print(f"   • Tipos de datos: {summary['data_summary']['data_types_loaded']}")
        
        if summary['recommendations']:
            print("\n💡 RECOMENDACIONES:")
            for rec in summary['recommendations']:
                print(f"   • {rec}")

# Funciones de compatibilidad para uso legacy
def run_twitter_analysis(usuario_objetivo: str = 'Interbank', 
                        target_variable: str = 'likes') -> Dict[str, Any]:
    """
    Función de compatibilidad para ejecutar análisis de una sola cuenta.
    
    Args:
        usuario_objetivo (str): Usuario específico
        target_variable (str): Variable objetivo
        
    Returns:
        Dict[str, Any]: Resultados del análisis
    """
    pipeline = TwitterAnalysisPipeline(
        target_accounts=[usuario_objetivo],
        target_variable=target_variable,
        analysis_mode='individual'
    )
    return pipeline.run_complete_analysis()

def run_multi_account_analysis(target_accounts: List[str] = None,
                              target_variable: str = 'likes',
                              analysis_mode: str = 'consolidado') -> Dict[str, Any]:
    """
    Función principal para ejecutar análisis multi-cuenta.
    
    Args:
        target_accounts (List[str]): Lista de cuentas objetivo
        target_variable (str): Variable objetivo
        analysis_mode (str): Modo de análisis
        
    Returns:
        Dict[str, Any]: Resultados del análisis
    """
    pipeline = TwitterAnalysisPipeline(
        target_accounts=target_accounts,
        target_variable=target_variable,
        analysis_mode=analysis_mode
    )
    return pipeline.run_complete_analysis()

if __name__ == "__main__":
    print("🧪 EJEMPLO DE USO DEL PIPELINE MULTI-CUENTA")
    print("="*50)
    
    # Ejemplo 1: Análisis consolidado de todas las cuentas
    print("\n1️⃣ Análisis consolidado:")
    try:
        results_consolidated = run_multi_account_analysis(
            target_accounts=['Interbank', 'BanBif', 'BCPComunica'],
            analysis_mode='consolidado'
        )
        print("✅ Análisis consolidado completado")
    except Exception as e:
        print(f"❌ Error en análisis consolidado: {e}")
    
    # Ejemplo 2: Análisis comparativo
    print("\n2️⃣ Análisis comparativo:")
    try:
        results_comparative = run_multi_account_analysis(
            target_accounts=['Interbank', 'BanBif'],
            analysis_mode='comparativo'
        )
        print("✅ Análisis comparativo completado")
    except Exception as e:
        print(f"❌ Error en análisis comparativo: {e}")
    
    # Ejemplo 3: Análisis individual (compatibilidad)
    print("\n3️⃣ Análisis individual (compatibilidad):")
    try:
        results_individual = run_twitter_analysis('Interbank')
        print("✅ Análisis individual completado")
    except Exception as e:
        print(f"❌ Error en análisis individual: {e}")
