# =============================================================================
# PREPROCESAMIENTO Y FEATURE ENGINEERING
# =============================================================================

"""
Módulo para preprocesamiento de datos y creación de features.
Incluye limpieza, feature engineering y normalización de datos.
"""

import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from typing import Tuple, List, Dict, Optional
from config import PROJECT_CONFIG

class DataPreprocessor:
    """
    Clase para manejar el preprocesamiento y feature engineering de datos de Twitter.
    """
    
    def __init__(self, features_base: List[str] = None):
        """
        Inicializa el preprocesador.
        
        Args:
            features_base (List[str]): Lista de features base
        """
        self.features_base = features_base or PROJECT_CONFIG['features_base']
        self.scaler = StandardScaler()
        self.features_info = {}
        
    def check_feature_availability(self, data: pd.DataFrame) -> Tuple[List[str], List[str]]:
        """
        Verifica la disponibilidad de features en el dataset.
        
        Args:
            data (pd.DataFrame): DataFrame a verificar
            
        Returns:
            Tuple[List[str], List[str]]: Features disponibles y faltantes
        """
        features_disponibles = [col for col in self.features_base if col in data.columns]
        features_faltantes = [col for col in self.features_base if col not in data.columns]
        
        print("📊 Análisis de features disponibles:")
        print(f"   ✅ Disponibles: {features_disponibles}")
        if features_faltantes:
            print(f"   ❌ Faltantes: {features_faltantes}")
            
        return features_disponibles, features_faltantes
    
    def create_engineered_features(self, data: pd.DataFrame, features_disponibles: List[str]) -> Tuple[pd.DataFrame, List[str]]:
        """
        Crea features derivadas mediante feature engineering.
        
        Args:
            data (pd.DataFrame): DataFrame original
            features_disponibles (List[str]): Features disponibles
            
        Returns:
            Tuple[pd.DataFrame, List[str]]: DataFrame con nuevas features y lista de features engineered
        """
        print(f"\n🔧 Aplicando Feature Engineering...")
        
        data_enhanced = data.copy()
        features_engineered = []
        
        # 1. Longitud del contenido
        if 'contenido' in data_enhanced.columns:
            data_enhanced['longitud_tweet'] = data_enhanced['contenido'].astype(str).apply(len)
            features_disponibles.append('longitud_tweet')
            features_engineered.append('longitud_tweet')
            print("   ✅ Longitud del tweet calculada")
        
        # 2. Ratio de engagement
        required_cols = ['likes', 'retweets', 'vistas']
        if all(col in data_enhanced.columns for col in required_cols):
            data_enhanced['engagement_rate'] = (
                (data_enhanced['likes'] + data_enhanced['retweets']) / 
                (data_enhanced['vistas'] + 1)  # +1 para evitar división por cero
            )
            features_disponibles.append('engagement_rate')
            features_engineered.append('engagement_rate')
            print("   ✅ Ratio de engagement calculado")
        
        # 3. Score de interacción total
        interaction_cols = [col for col in ['respuestas', 'retweets', 'likes', 'guardados'] 
                           if col in data_enhanced.columns]
        if interaction_cols:
            data_enhanced['interaction_score'] = data_enhanced[interaction_cols].sum(axis=1)
            features_disponibles.append('interaction_score')
            features_engineered.append('interaction_score')
            print("   ✅ Score de interacción total calculado")
        
        # 4. Ratios adicionales
        if 'respuestas' in data_enhanced.columns and 'likes' in data_enhanced.columns:
            data_enhanced['respuestas_likes_ratio'] = (
                data_enhanced['respuestas'] / (data_enhanced['likes'] + 1)
            )
            features_disponibles.append('respuestas_likes_ratio')
            features_engineered.append('respuestas_likes_ratio')
            print("   ✅ Ratio respuestas/likes calculado")
        
        # 5. Features logarítmicas para variables con distribución sesgada
        log_candidates = ['vistas', 'likes', 'retweets']
        for col in log_candidates:
            if col in data_enhanced.columns:
                # Solo aplicar log si hay valores > 0
                if (data_enhanced[col] > 0).any():
                    log_col_name = f'log_{col}'
                    data_enhanced[log_col_name] = np.log1p(data_enhanced[col])  # log1p para manejar 0s
                    features_disponibles.append(log_col_name)
                    features_engineered.append(log_col_name)
                    print(f"   ✅ Feature logarítmica {log_col_name} calculada")
        
        return data_enhanced, features_engineered
    
    def prepare_feature_matrix(self, data: pd.DataFrame, features: List[str]) -> Tuple[pd.DataFrame, Dict]:
        """
        Prepara la matriz de features final.
        
        Args:
            data (pd.DataFrame): DataFrame con todas las features
            features (List[str]): Lista de features a usar
            
        Returns:
            Tuple[pd.DataFrame, Dict]: Matriz X y estadísticas
        """
        print(f"\n📋 Preparando matriz de features...")
        
        # Seleccionar features finales y manejar valores faltantes
        X = data[features].fillna(0)
        
        print(f"   • Features seleccionadas: {len(features)}")
        print(f"   • Dimensiones de X: {X.shape}")
        
        # Información estadística básica
        print(f"\n📈 Estadísticas descriptivas:")
        stats = X.describe()
        print(stats.round(2))
        
        # Detectar outliers (usando IQR)
        outliers_info = self._detect_outliers(X)
        
        statistics = {
            'shape': X.shape,
            'features_count': len(features),
            'null_values': X.isnull().sum().sum(),
            'outliers_info': outliers_info,
            'basic_stats': stats.to_dict()
        }
        
        return X, statistics
    
    def _detect_outliers(self, X: pd.DataFrame) -> Dict:
        """
        Detecta outliers usando el método IQR.
        
        Args:
            X (pd.DataFrame): Matriz de features
            
        Returns:
            Dict: Información sobre outliers
        """
        outliers_info = {}
        
        for column in X.columns:
            Q1 = X[column].quantile(0.25)
            Q3 = X[column].quantile(0.75)
            IQR = Q3 - Q1
            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR
            
            outliers = X[(X[column] < lower_bound) | (X[column] > upper_bound)]
            outliers_info[column] = {
                'count': len(outliers),
                'percentage': len(outliers) / len(X) * 100,
                'lower_bound': lower_bound,
                'upper_bound': upper_bound
            }
        
        return outliers_info
    
    def scale_features(self, X: pd.DataFrame) -> Tuple[np.ndarray, Dict]:
        """
        Aplica escalado estándar a las features.
        
        Args:
            X (pd.DataFrame): Matriz de features sin escalar
            
        Returns:
            Tuple[np.ndarray, Dict]: Features escaladas e información de escalado
        """
        print(f"\n⚡ Aplicando escalado estándar...")
        
        X_scaled = self.scaler.fit_transform(X)
        
        scaling_info = {
            'mean_before': X.mean().to_dict(),
            'std_before': X.std().to_dict(),
            'mean_after': X_scaled.mean(),
            'std_after': X_scaled.std(),
            'scaler_params': {
                'mean_': self.scaler.mean_.tolist(),
                'scale_': self.scaler.scale_.tolist()
            }
        }
        
        print(f"   ✅ Datos escalados exitosamente")
        print(f"   • Shape final: {X_scaled.shape}")
        print(f"   • Media post-escalado: {X_scaled.mean():.6f}")
        print(f"   • Desviación estándar post-escalado: {X_scaled.std():.6f}")
        
        return X_scaled, scaling_info
    
    def preprocess_data(self, data: pd.DataFrame) -> Tuple[np.ndarray, pd.DataFrame, List[str], Dict]:
        """
        Pipeline completo de preprocesamiento.
        
        Args:
            data (pd.DataFrame): DataFrame original
            
        Returns:
            Tuple: X_scaled, data_enhanced, features, info_completa
        """
        # 1. Verificar features disponibles
        features_disponibles, features_faltantes = self.check_feature_availability(data)
        
        # 2. Feature engineering
        data_enhanced, features_engineered = self.create_engineered_features(data, features_disponibles)
        
        # 3. Preparar matriz de features
        X, statistics = self.prepare_feature_matrix(data_enhanced, features_disponibles)
        
        # 4. Escalado
        X_scaled, scaling_info = self.scale_features(X)
        
        # 5. Guardar información completa
        self.features_info = {
            'features_utilizadas': features_disponibles,
            'features_originales': self.features_base,
            'features_engineered': features_engineered,
            'features_faltantes': features_faltantes,
            'n_samples': X.shape[0],
            'n_features': X.shape[1],
            'statistics': statistics,
            'scaling_info': scaling_info
        }
        
        print(f"\n✅ Preprocesamiento completado:")
        for key, value in self.features_info.items():
            if key not in ['statistics', 'scaling_info']:  # Evitar imprimir dict complejos
                print(f"   • {key}: {value}")
        
        return X_scaled, data_enhanced, features_disponibles, self.features_info
    
    def get_feature_importance_data(self, data_enhanced: pd.DataFrame, features: List[str]) -> pd.DataFrame:
        """
        Prepara datos para análisis de importancia de features.
        
        Args:
            data_enhanced (pd.DataFrame): DataFrame con features engineered
            features (List[str]): Lista de features
            
        Returns:
            pd.DataFrame: DataFrame listo para análisis de importancia
        """
        return data_enhanced[features].copy()

def preprocess_twitter_data(data: pd.DataFrame, 
                           features_base: List[str] = None) -> Tuple[np.ndarray, pd.DataFrame, List[str], Dict]:
    """
    Función principal para preprocesar datos de Twitter.
    
    Args:
        data (pd.DataFrame): DataFrame original
        features_base (List[str]): Features base (opcional)
        
    Returns:
        Tuple: X_scaled, data_enhanced, features, info_completa
    """
    preprocessor = DataPreprocessor(features_base=features_base)
    return preprocessor.preprocess_data(data)

if __name__ == "__main__":
    # Ejemplo de uso
    import sys
    sys.path.append('.')
    from data_loader import load_and_prepare_data
    
    # Cargar datos
    data, _ = load_and_prepare_data()
    
    # Preprocesar
    X_scaled, data_enhanced, features, info = preprocess_twitter_data(data)
    
    print(f"\n✅ Preprocesamiento completado. Shape de X_scaled: {X_scaled.shape}")
    print(f"Features utilizadas: {features}")
