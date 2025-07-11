# =============================================================================
# MODELOS DE REGRESIÓN PARA PREDICCIÓN DE SEGUIDORES
# =============================================================================

"""
Módulo para implementación y evaluación de modelos de regresión por cuenta individual.
Enfoque: Predicción del número de seguidores usando métricas de engagement.
"""

import numpy as np
import pandas as pd
import joblib
from datetime import datetime
from pathlib import Path
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import (mean_squared_error, r2_score, mean_absolute_error, 
                           median_absolute_error, explained_variance_score)
from typing import Tuple, Dict, List, Optional, Any
from .config import (REGRESSION_MODELS, TARGET_VARIABLE, FEATURE_CONFIG, 
                    EVALUATION_METRICS, OUTPUT_CONFIG)

class AccountRegressionModel:
    """
    Clase para crear modelos de regresión específicos por cuenta de Twitter/X.
    Enfoque: Predicción del número de seguidores basado en métricas de engagement.
    """
    
    def __init__(self, account_name: str, target_variable: str = None):
        """
        Inicializa el modelo de regresión para una cuenta específica.
        
        Args:
            account_name (str): Nombre de la cuenta
            target_variable (str): Variable objetivo (por defecto: seguidores)
        """
        self.account_name = account_name
        self.target_variable = target_variable or TARGET_VARIABLE
        self.models = {}
        self.results = {}
        self.best_model = None
        self.trained_models = {}
        self.X_train = None
        self.X_test = None
        self.y_train = None
        self.y_test = None
        self.feature_names = None
        
        # Configuración por defecto
        self.config = {
            'test_size': 0.2,
            'random_state': 42,
            'cv_folds': 5
        }
        
    def setup_models(self) -> Dict:
        """
        Configura los modelos de regresión basados en la configuración.
        
        Returns:
            Dict: Diccionario con modelos configurados
        """
        print(f"🤖 Configurando modelos para cuenta: {self.account_name}")
        
        self.models = {}
        for name, config in REGRESSION_MODELS.items():
            model_class = config['model']
            params = config['params']
            self.models[name] = model_class(**params)
        
        print(f"   • Modelos configurados: {len(self.models)}")
        for name, config in REGRESSION_MODELS.items():
            print(f"     - {config['description']}")
        
        return self.models
    
    def prepare_data(self, data: pd.DataFrame) -> Tuple[pd.DataFrame, pd.Series]:
        """
        Prepara los datos para regresión.
        
        Args:
            data (pd.DataFrame): DataFrame con datos de la cuenta
            
        Returns:
            Tuple[pd.DataFrame, pd.Series]: X (features), y (target)
        """
        print(f"📊 Preparando datos para regresión de {self.account_name}")
        print(f"🎯 Variable objetivo: {self.target_variable}")
        
        # Verificar que la variable objetivo existe
        if self.target_variable not in data.columns:
            available_cols = data.columns.tolist()
            raise ValueError(f"Variable objetivo '{self.target_variable}' no encontrada. "
                           f"Columnas disponibles: {available_cols}")
        
        # Obtener todas las features disponibles excluyendo la variable objetivo
        all_features = []
        for feature_group in FEATURE_CONFIG.values():
            all_features.extend(feature_group)
        
        # Filtrar features que existen en los datos
        available_features = [col for col in all_features if col in data.columns and col != self.target_variable]
        
        if not available_features:
            raise ValueError("No se encontraron features válidas para el modelo")
        
        # Preparar X e y
        X = data[available_features].fillna(0)
        y = data[self.target_variable].fillna(0)
        
        # Guardar nombres de features
        self.feature_names = available_features
        
        # Estadísticas de la variable objetivo
        y_stats = {
            'count': len(y),
            'mean': y.mean(),
            'median': y.median(),
            'std': y.std(),
            'min': y.min(),
            'max': y.max()
        }
        
        print(f"   • Features utilizadas: {len(available_features)}")
        print(f"   • Muestras totales: {len(y):,}")
        print(f"   • Estadísticas de {self.target_variable}:")
        for key, value in y_stats.items():
            if isinstance(value, (int, float)):
                print(f"     - {key.title()}: {value:.2f}")
        
        return X, y
    
    def split_data(self, X: pd.DataFrame, y: pd.Series) -> None:
        """
        Divide los datos en entrenamiento y prueba.
        
        Args:
            X (pd.DataFrame): Features
            y (pd.Series): Variable objetivo
        """
        self.X_train, self.X_test, self.y_train, self.y_test = train_test_split(
            X, y, 
            test_size=self.config['test_size'], 
            random_state=self.config['random_state']
        )
        
        print(f"   • Datos de entrenamiento: {self.X_train.shape[0]:,} muestras")
        print(f"   • Datos de prueba: {self.X_test.shape[0]:,} muestras")
    
    def train_and_evaluate_models(self) -> pd.DataFrame:
        """
        Entrena y evalúa todos los modelos de regresión.
        
        Returns:
            pd.DataFrame: DataFrame con resultados de todos los modelos
        """
        if not self.models:
            self.setup_models()
        
        if self.X_train is None:
            raise ValueError("Datos no preparados. Ejecuta prepare_data() y split_data() primero.")
        
        print(f"\n⚡ Entrenando y evaluando modelos para {self.account_name}...")
        
        resultados = []
        
        for nombre, modelo in self.models.items():
            print(f"   🔄 Procesando {REGRESSION_MODELS[nombre]['description']}...")
            
            try:
                # Entrenamiento
                modelo.fit(self.X_train, self.y_train)
                
                # Guardar modelo entrenado
                self.trained_models[nombre] = modelo
                
                # Predicción
                y_pred = modelo.predict(self.X_test)
                
                # Calcular métricas
                metrics = self._calculate_metrics(self.y_test, y_pred, modelo)
                
                resultados.append({
                    'Modelo': REGRESSION_MODELS[nombre]['description'],
                    'Modelo_ID': nombre,
                    **metrics
                })
                
                print(f"      ✅ Completado - R²: {metrics['R²']:.3f}, RMSE: {metrics['RMSE']:.2f}")
                
            except Exception as e:
                print(f"      ❌ Error en {nombre}: {str(e)}")
        
        # Crear DataFrame de resultados
        results_df = pd.DataFrame(resultados)
        if len(results_df) > 0:
            results_df = results_df.sort_values(['R²'], ascending=[False])
            results_df = results_df.reset_index(drop=True)
        
        self.results = results_df
        return results_df
    
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
        
        # Validación cruzada
        try:
            cv_scores = cross_val_score(
                modelo, self.X_train, self.y_train, 
                cv=self.config['cv_folds'], 
                scoring='r2', 
                n_jobs=-1
            )
            cv_mean = cv_scores.mean()
            cv_std = cv_scores.std()
        except:
            cv_mean = r2
            cv_std = 0.0
        
        # Métricas adicionales
        mape = np.mean(np.abs((y_true - y_pred) / (y_true + 1e-8))) * 100
        
        return {
            'RMSE': rmse,
            'MAE': mae,
            'MedAE': medae,
            'R²': r2,
            'EVS': evs,
            'CV_R²_mean': cv_mean,
            'CV_R²_std': cv_std,
            'MAPE': mape
        }
    
    def get_best_model(self, weights: Dict[str, float] = None, maximize: List[str] = None) -> Dict:
        """
        Identifica el mejor modelo usando un score compuesto con todas las métricas disponibles.
        Las métricas se normalizan (min-max) para ser comparables.
        
        Args:
            weights (Dict[str, float]): Pesos para cada métrica (por defecto: igual para todas)
            maximize (List[str]): Lista de métricas a maximizar (por defecto: ['R²', 'EVS', 'CV_R²_mean'])
        
        Returns:
            Dict: Información del mejor modelo según el score compuesto
        """
        if len(self.results) == 0:
            return {}

        df = self.results.copy()
        metric_names = ['RMSE', 'MAE', 'MedAE', 'R²', 'EVS', 'CV_R²_mean', 'CV_R²_std', 'MAPE']
        # Usar solo métricas presentes
        used_metrics = [m for m in metric_names if m in df.columns]
        if not used_metrics:
            raise ValueError("No hay métricas válidas para calcular el score compuesto.")

        # Pesos por defecto: igual para todas
        if weights is None:
            weights = {m: 1/len(used_metrics) for m in used_metrics}
        # Métricas a maximizar
        if maximize is None:
            maximize = ['R²', 'EVS', 'CV_R²_mean']

        # Normalización min-max por métrica
        norm_df = pd.DataFrame()
        for m in used_metrics:
            vals = df[m].values.astype(float)
            if m in maximize:
                minv, maxv = np.min(vals), np.max(vals)
                norm = (vals - minv) / (maxv - minv) if maxv > minv else np.zeros_like(vals)
            else:
                minv, maxv = np.min(vals), np.max(vals)
                norm = (maxv - vals) / (maxv - minv) if maxv > minv else np.zeros_like(vals)
            norm_df[m] = norm

        # Calcular score compuesto
        df['ScoreCompuesto'] = sum(norm_df[m] * weights[m] for m in used_metrics)

        # Seleccionar el mejor modelo
        best_row = df.loc[df['ScoreCompuesto'].idxmax()]
        self.best_model = best_row['Modelo_ID']

        return {
            'model_id': best_row['Modelo_ID'],
            'model_name': best_row['Modelo'],
            'score_compuesto': best_row['ScoreCompuesto'],
            'metricas': {m: best_row[m] for m in used_metrics},
            'pesos': weights
        }
    
    def save_model(self, model_id: str = None, save_path: str = None) -> str:
        """
        Guarda el mejor modelo en la nueva estructura de directorios.
        
        Args:
            model_id (str): ID del modelo a guardar (por defecto: mejor modelo)
            save_path (str): Ruta donde guardar (por defecto: models/username/regresion.pkl)
            
        Returns:
            str: Ruta del archivo guardado
        """
        from .config import get_model_filepath
        
        # Usar mejor modelo si no se especifica
        if model_id is None:
            if self.best_model is None:
                self.get_best_model()
            model_id = self.best_model
        
        if model_id not in self.trained_models:
            raise ValueError(f"Modelo '{model_id}' no está entrenado")
        
        # Usar nueva estructura de directorios
        if save_path is None:
            save_path = get_model_filepath(self.account_name)
        
        # Guardar modelo
        model_data = {
            'model': self.trained_models[model_id],
            'feature_names': self.feature_names,
            'target_variable': self.target_variable,
            'account_name': self.account_name,
            'model_id': model_id,
            'timestamp': datetime.now(),
            'results': self.results.to_dict('records') if len(self.results) > 0 else []
        }
        
        joblib.dump(model_data, save_path)
        print(f"💾 Modelo guardado: {save_path}")
        
        return str(save_path)
    
    def generate_report(self) -> Dict:
        """
        Genera un reporte completo del análisis.
        
        Returns:
            Dict: Reporte completo
        """
        if len(self.results) == 0:
            return {}
        
        best_model_info = self.get_best_model()
        
        report = {
            'account_name': self.account_name,
            'target_variable': self.target_variable,
            'total_models': len(self.results),
            'best_model': best_model_info,
            'all_results': self.results.to_dict('records'),
            'feature_count': len(self.feature_names) if self.feature_names else 0,
            'features_used': self.feature_names,
            'training_samples': len(self.X_train) if self.X_train is not None else 0,
            'test_samples': len(self.X_test) if self.X_test is not None else 0,
            'timestamp': datetime.now().isoformat()
        }
        
        return report
    
    def print_results_summary(self, weights: Dict[str, float] = None) -> None:
        """
        Imprime resumen de resultados y muestra el mejor modelo según score compuesto.
        """
        if len(self.results) == 0:
            print(f"\n❌ No se pudieron entrenar modelos para {self.account_name}")
            return

        print(f"\n" + "="*100)
        print(f"📊 RESULTADOS DE REGRESIÓN - {self.account_name.upper()}")
        print(f"🎯 Variable objetivo: {self.target_variable}")
        print("="*100)

        # Mostrar resultados principales
        display_cols = ['Modelo', 'R²', 'RMSE', 'MAE', 'CV_R²_mean']
        available_cols = [col for col in display_cols if col in self.results.columns]
        print(self.results[available_cols].round(3).to_string(index=False))

        # Mejor modelo por score compuesto
        best_weighted = self.get_best_model(weights)
        if best_weighted:
            print(f"\n⭐ MEJOR MODELO (Score Compuesto): {best_weighted['model_name']}")
            print(f"   • Score: {best_weighted['score_compuesto']:.3f}")
            for m, v in best_weighted['metricas'].items():
                print(f"   • {m}: {v:.3f}")
            print(f"   • Pesos usados: {best_weighted['pesos']}")

        print(f"\n✅ Análisis completado para {self.account_name}")

def train_account_regression_model(account_name: str, data: pd.DataFrame, 
                                  target_variable: str = None,
                                  save_model: bool = True) -> Tuple[AccountRegressionModel, Dict]:
    """
    Función principal para entrenar modelos de regresión para una cuenta.
    
    Args:
        account_name (str): Nombre de la cuenta
        data (pd.DataFrame): DataFrame con datos de la cuenta
        target_variable (str): Variable objetivo
        save_model (bool): Si guardar el mejor modelo
        
    Returns:
        Tuple[AccountRegressionModel, Dict]: Modelo entrenado y reporte
    """
    print(f"\n🚀 Iniciando análisis de regresión para: {account_name}")
    
    # Crear modelo
    model = AccountRegressionModel(account_name, target_variable)
    
    # Preparar datos
    X, y = model.prepare_data(data)
    
    # Dividir datos
    model.split_data(X, y)
    
    # Entrenar y evaluar modelos
    results_df = model.train_and_evaluate_models()
    
    # Mostrar resultados
    model.print_results_summary()
    
    # Guardar mejor modelo si se solicita
    if save_model and len(results_df) > 0:
        try:
            saved_path = model.save_model()
            print(f"💾 Modelo guardado en: {saved_path}")
        except Exception as e:
            print(f"❌ Error guardando modelo: {e}")
    
    # Generar reporte
    report = model.generate_report()
    
    return model, report

if __name__ == "__main__":
    print("🔧 Módulo de modelos de regresión cargado")
    print("📋 Uso: train_account_regression_model(account_name, data)")
