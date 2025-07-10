# =============================================================================
# MODELOS DE REGRESIÓN
# =============================================================================

"""
Módulo para implementación y evaluación de modelos de regresión.
Incluye 8 algoritmos de ML con evaluación comparativa completa.
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import (mean_squared_error, r2_score, mean_absolute_error, 
                           median_absolute_error, explained_variance_score)
from typing import Tuple, Dict, List, Optional, Any
from config import MODELS_CONFIG, PROJECT_CONFIG, SCORING_CONFIG

class RegressionAnalyzer:
    """
    Clase para análisis completo de modelos de regresión en datos de Twitter.
    """
    
    def __init__(self, target_variable: str = None, config: Dict = None):
        """
        Inicializa el analizador de regresión.
        
        Args:
            target_variable (str): Variable objetivo
            config (Dict): Configuración de modelos
        """
        self.target_variable = target_variable or PROJECT_CONFIG['default_target_variable']
        self.config = config or MODELS_CONFIG['regression']
        self.models = {}
        self.results = []
        self.X_train = None
        self.X_test = None
        self.y_train = None
        self.y_test = None
        
    def setup_models(self) -> Dict:
        """
        Configura los modelos de regresión.
        
        Returns:
            Dict: Diccionario con modelos configurados
        """
        print("🤖 Configurando modelos de regresión...")
        
        self.models = self.config['models'].copy()
        
        print(f"   • Modelos configurados: {len(self.models)}")
        for nombre in self.models.keys():
            print(f"     - {nombre}")
        
        return self.models
    
    def prepare_regression_data(self, data: pd.DataFrame, features: List[str]) -> Tuple[pd.DataFrame, pd.Series, Dict]:
        """
        Prepara los datos para regresión.
        
        Args:
            data (pd.DataFrame): DataFrame con todas las features
            features (List[str]): Lista de features disponibles
            
        Returns:
            Tuple[pd.DataFrame, pd.Series, Dict]: X, y, statistics
        """
        print(f"🎯 Variable objetivo seleccionada: {self.target_variable}")
        
        # Validar que la variable objetivo existe
        if self.target_variable not in data.columns:
            available_targets = [col for col in ['likes', 'retweets', 'respuestas', 'vistas', 'guardados'] 
                               if col in data.columns]
            raise ValueError(f"Variable objetivo '{self.target_variable}' no encontrada. "
                           f"Disponibles: {available_targets}")
        
        print(f"\n📊 Preparando datos para regresión...")
        
        # Variables predictoras (excluir la variable objetivo de los features)
        features_regresion = [col for col in features if col != self.target_variable]
        X_reg = data[features_regresion].fillna(0)
        y = data[self.target_variable].fillna(0)
        
        # Estadísticas de la variable objetivo
        y_stats = {
            'count': len(y),
            'mean': y.mean(),
            'median': y.median(),
            'std': y.std(),
            'min': y.min(),
            'max': y.max(),
            'skewness': y.skew(),
            'kurtosis': y.kurtosis()
        }
        
        print(f"   • Features para regresión: {len(features_regresion)}")
        print(f"   • Features utilizadas: {features_regresion}")
        print(f"   • Muestras totales: {len(y):,}")
        print(f"   • Estadísticas de variable objetivo:")
        for key, value in y_stats.items():
            if isinstance(value, (int, float)):
                print(f"     - {key.title()}: {value:.2f}")
            else:
                print(f"     - {key.title()}: {value}")
        
        return X_reg, y, y_stats
    
    def split_data(self, X: pd.DataFrame, y: pd.Series, 
                  test_size: float = None, random_state: int = None) -> None:
        """
        Divide los datos en entrenamiento y prueba.
        
        Args:
            X (pd.DataFrame): Features
            y (pd.Series): Variable objetivo
            test_size (float): Proporción para test
            random_state (int): Semilla aleatoria
        """
        test_size = test_size or PROJECT_CONFIG['test_size']
        random_state = random_state or PROJECT_CONFIG['random_state']
        
        self.X_train, self.X_test, self.y_train, self.y_test = train_test_split(
            X, y, test_size=test_size, random_state=random_state, stratify=None
        )
        
        print(f"   • Datos de entrenamiento: {self.X_train.shape[0]:,} muestras")
        print(f"   • Datos de prueba: {self.X_test.shape[0]:,} muestras")
    
    def train_and_evaluate_models(self) -> List[Dict]:
        """
        Entrena y evalúa todos los modelos de regresión.
        
        Returns:
            List[Dict]: Lista con resultados de todos los modelos
        """
        if not self.models:
            self.setup_models()
        
        if self.X_train is None:
            raise ValueError("Datos no preparados. Ejecuta split_data() primero.")
        
        print(f"\n⚡ Entrenando y evaluando modelos...")
        
        resultados = []
        
        for nombre, modelo in self.models.items():
            print(f"   🔄 Procesando {nombre}...")
            
            try:
                # Entrenamiento
                modelo.fit(self.X_train, self.y_train)
                
                # Predicción
                y_pred = modelo.predict(self.X_test)
                
                # Limpieza de datos (manejar NaN y valores infinitos)
                mask = np.isfinite(y_pred) & np.isfinite(self.y_test) & ~pd.isna(self.y_test)
                y_test_clean = self.y_test[mask]
                y_pred_clean = y_pred[mask]
                
                # Calcular métricas solo si hay datos válidos
                if len(y_test_clean) > 0:
                    metrics = self._calculate_metrics(y_test_clean, y_pred_clean, modelo)
                    
                    resultados.append({
                        'Modelo': nombre,
                        **metrics,
                        'Muestras_válidas': len(y_test_clean)
                    })
                    
                    print(f"      ✅ Completado - R²: {metrics['R²']:.3f}, RMSE: {metrics['RMSE']:.2f}")
                else:
                    print(f"      ❌ Sin datos válidos para evaluación")
                    
            except Exception as e:
                print(f"      ❌ Error en {nombre}: {str(e)}")
        
        self.results = resultados
        return resultados
    
    def _calculate_metrics(self, y_true: np.ndarray, y_pred: np.ndarray, modelo: Any) -> Dict:
        """
        Calcula todas las métricas de evaluación.
        
        Args:
            y_true (np.ndarray): Valores reales
            y_pred (np.ndarray): Predicciones
            modelo (Any): Modelo entrenado
            
        Returns:
            Dict: Diccionario con todas las métricas
        """
        # Métricas básicas
        rmse = np.sqrt(mean_squared_error(y_true, y_pred))
        mae = mean_absolute_error(y_true, y_pred)
        medae = median_absolute_error(y_true, y_pred)
        r2 = r2_score(y_true, y_pred)
        evs = explained_variance_score(y_true, y_pred)
        
        # Validación cruzada para mayor robustez
        cv_folds = PROJECT_CONFIG['cv_folds']
        cv_scores = cross_val_score(modelo, self.X_train, self.y_train, 
                                  cv=cv_folds, scoring='r2', n_jobs=-1)
        cv_mean = cv_scores.mean()
        cv_std = cv_scores.std()
        
        # Métricas adicionales
        mape = np.mean(np.abs((y_true - y_pred) / (y_true + 1e-8))) * 100  # MAPE with small epsilon
        residuals = y_true - y_pred
        residuals_std = np.std(residuals)
        
        return {
            'RMSE': rmse,
            'MAE': mae,
            'MedAE': medae,
            'R²': r2,
            'EVS': evs,
            'CV_R²_mean': cv_mean,
            'CV_R²_std': cv_std,
            'MAPE': mape,
            'Residuals_Std': residuals_std
        }
    
    def create_results_dataframe(self, resultados: List[Dict]) -> pd.DataFrame:
        """
        Crea DataFrame con los resultados ordenados.
        
        Args:
            resultados (List[Dict]): Lista de resultados
            
        Returns:
            pd.DataFrame: DataFrame ordenado por rendimiento
        """
        if not resultados:
            return pd.DataFrame()
        
        resultados_df = pd.DataFrame(resultados)
        
        # Ordenar por RMSE (ascendente) y luego por R² (descendente)
        resultados_df = resultados_df.sort_values(['RMSE', 'R²'], ascending=[True, False])
        resultados_df = resultados_df.reset_index(drop=True)
        
        return resultados_df
    
    def print_results_summary(self, resultados_df: pd.DataFrame) -> None:
        """
        Imprime resumen de resultados.
        
        Args:
            resultados_df (pd.DataFrame): DataFrame con resultados
        """
        if len(resultados_df) == 0:
            print(f"\n❌ No se pudieron entrenar modelos exitosamente")
            return
        
        print(f"\n" + "="*100)
        print(f"📊 RESULTADOS DE REGRESIÓN - Variable objetivo: {self.target_variable.upper()}")
        print("="*100)
        
        # Mostrar resultados formateados
        display_cols = ['Modelo', 'RMSE', 'MAE', 'MedAE', 'R²', 'EVS', 'CV_R²_mean']
        available_cols = [col for col in display_cols if col in resultados_df.columns]
        print(resultados_df[available_cols].round(3).to_string(index=False))
        
        print(f"\n✅ Entrenamiento completado: {len(resultados_df)} modelos evaluados")
    
    def find_best_models(self, resultados_df: pd.DataFrame) -> Dict:
        """
        Identifica los mejores modelos por cada métrica.
        
        Args:
            resultados_df (pd.DataFrame): DataFrame con resultados
            
        Returns:
            Dict: Mejores modelos por métrica
        """
        if len(resultados_df) == 0:
            return {}
        
        mejor_rmse = resultados_df.loc[resultados_df['RMSE'].idxmin()]
        mejor_r2 = resultados_df.loc[resultados_df['R²'].idxmax()]
        mejor_mae = resultados_df.loc[resultados_df['MAE'].idxmin()]
        mejor_cv = resultados_df.loc[resultados_df['CV_R²_mean'].idxmax()]
        
        best_models = {
            'rmse': mejor_rmse,
            'r2': mejor_r2,
            'mae': mejor_mae,
            'cv': mejor_cv
        }
        
        print(f"\n🏆 MEJORES MODELOS POR MÉTRICA:")
        print(f"   🎯 Menor RMSE: {mejor_rmse['Modelo']} ({mejor_rmse['RMSE']:.3f})")
        print(f"   📈 Mayor R²: {mejor_r2['Modelo']} ({mejor_r2['R²']:.3f})")
        print(f"   📉 Menor MAE: {mejor_mae['Modelo']} ({mejor_mae['MAE']:.3f})")
        print(f"   🔄 Mejor CV R²: {mejor_cv['Modelo']} ({mejor_cv['CV_R²_mean']:.3f} ± {mejor_cv['CV_R²_std']:.3f})")
        
        return best_models
    
    def generate_model_recommendation(self, resultados_df: pd.DataFrame) -> Dict:
        """
        Genera recomendación automática de modelo.
        
        Args:
            resultados_df (pd.DataFrame): DataFrame con resultados
            
        Returns:
            Dict: Recomendación y justificación
        """
        if len(resultados_df) == 0:
            return {}
        
        # Sistema de puntuación múltiple usando configuración
        scoring_weights = SCORING_CONFIG['weights']
        score_weights = SCORING_CONFIG['score_weights']
        
        # Normalizar métricas y calcular score compuesto
        resultados_norm = resultados_df.copy()
        for metric in scoring_weights.keys():
            if metric in resultados_df.columns:
                if scoring_weights[metric] == 1:  # Mayor es mejor
                    min_val = resultados_df[metric].min()
                    max_val = resultados_df[metric].max()
                    if max_val > min_val:
                        resultados_norm[f'{metric}_norm'] = (resultados_df[metric] - min_val) / (max_val - min_val)
                    else:
                        resultados_norm[f'{metric}_norm'] = 1.0
                else:  # Menor es mejor
                    min_val = resultados_df[metric].min()
                    max_val = resultados_df[metric].max()
                    if max_val > min_val:
                        resultados_norm[f'{metric}_norm'] = (max_val - resultados_df[metric]) / (max_val - min_val)
                    else:
                        resultados_norm[f'{metric}_norm'] = 1.0
        
        # Score compuesto
        score_cols = [col for col in score_weights.keys() if col in resultados_norm.columns]
        if score_cols:
            resultados_norm['Score_Compuesto'] = sum(
                resultados_norm[col] * score_weights[col] for col in score_cols
            )
        else:
            # Fallback simple si no hay columnas de score
            resultados_norm['Score_Compuesto'] = resultados_norm['R²']
        
        mejor_modelo_idx = resultados_norm['Score_Compuesto'].idxmax()
        mejor_modelo = resultados_norm.loc[mejor_modelo_idx]
        
        recommendation = {
            'modelo': mejor_modelo['Modelo'],
            'metrics': {
                'RMSE': mejor_modelo['RMSE'],
                'R²': mejor_modelo['R²'],
                'MAE': mejor_modelo['MAE'],
                'CV_R²_mean': mejor_modelo['CV_R²_mean'],
                'CV_R²_std': mejor_modelo['CV_R²_std']
            },
            'score_compuesto': mejor_modelo['Score_Compuesto']
        }
        
        # Generar justificación
        justificacion = self._generate_justification(recommendation, mejor_modelo)
        recommendation['justificacion'] = justificacion
        
        return recommendation
    
    def _generate_justification(self, recommendation: Dict, modelo_info: pd.Series) -> str:
        """
        Genera justificación detallada del modelo recomendado.
        
        Args:
            recommendation (Dict): Información de recomendación
            modelo_info (pd.Series): Información del modelo
            
        Returns:
            str: Justificación detallada
        """
        rmse = modelo_info['RMSE']
        r2 = modelo_info['R²']
        mae = modelo_info['MAE']
        cv_mean = modelo_info['CV_R²_mean']
        cv_std = modelo_info['CV_R²_std']
        nombre = modelo_info['Modelo']
        
        justificacion = f"""
El modelo {nombre} es recomendado por las siguientes razones:

🔹 PRECISIÓN: RMSE de {rmse:.3f} indica un error promedio de {rmse:.1f} unidades en la predicción de {self.target_variable}.

🔹 EXPLICACIÓN: R² de {r2:.3f} significa que el modelo explica {r2*100:.1f}% de la variabilidad en {self.target_variable}.

🔹 ROBUSTEZ: Error absoluto medio (MAE) de {mae:.3f} muestra consistencia en las predicciones.

🔹 ESTABILIDAD: Validación cruzada R² de {cv_mean:.3f} ± {cv_std:.3f} indica {"alta" if cv_std < 0.05 else "moderada"} estabilidad.

🔹 INTERPRETACIÓN: {"Alta interpretabilidad" if nombre in ["Linear Regression", "Decision Tree", "Ridge", "Lasso"] else "Modelo de caja negra con alta capacidad predictiva"}.
        """
        return justificacion.strip()

def train_regression_models(data: pd.DataFrame, features: List[str], 
                          target_variable: str = None,
                          config: Dict = None) -> Tuple[pd.DataFrame, Dict]:
    """
    Función principal para entrenar modelos de regresión.
    
    Args:
        data (pd.DataFrame): DataFrame con datos
        features (List[str]): Lista de features
        target_variable (str): Variable objetivo
        config (Dict): Configuración de modelos
        
    Returns:
        Tuple[pd.DataFrame, Dict]: Resultados y recomendación
    """
    analyzer = RegressionAnalyzer(target_variable=target_variable, config=config)
    
    # Preparar datos
    X_reg, y, y_stats = analyzer.prepare_regression_data(data, features)
    
    # Dividir datos
    analyzer.split_data(X_reg, y)
    
    # Entrenar y evaluar modelos
    resultados = analyzer.train_and_evaluate_models()
    
    # Crear DataFrame de resultados
    resultados_df = analyzer.create_results_dataframe(resultados)
    
    # Imprimir resumen
    analyzer.print_results_summary(resultados_df)
    
    # Encontrar mejores modelos
    best_models = analyzer.find_best_models(resultados_df)
    
    # Generar recomendación
    recommendation = analyzer.generate_model_recommendation(resultados_df)
    
    if recommendation:
        print(f"\n🏆 MODELO RECOMENDADO: {recommendation['modelo']}")
        print(f"📊 Métricas del modelo recomendado:")
        for metric, value in recommendation['metrics'].items():
            print(f"   • {metric}: {value:.3f}")
        print(f"   • Score Compuesto: {recommendation['score_compuesto']:.3f}")
        
        print(f"\n💡 JUSTIFICACIÓN:")
        print(recommendation['justificacion'])
    
    return resultados_df, recommendation

if __name__ == "__main__":
    # Ejemplo de uso
    import sys
    sys.path.append('.')
    from data_loader import load_and_prepare_data
    from preprocessing import preprocess_twitter_data
    
    # Cargar y preprocesar datos
    data, _ = load_and_prepare_data()
    X_scaled, data_enhanced, features, _ = preprocess_twitter_data(data)
    
    # Entrenar modelos de regresión
    results_df, recommendation = train_regression_models(data_enhanced, features, target_variable='likes')
    
    print(f"\n✅ Ejemplo completado. Mejor modelo: {recommendation['modelo'] if recommendation else 'N/A'}")
