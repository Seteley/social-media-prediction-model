# =============================================================================
# PREPROCESAMIENTO Y FEATURE ENGINEERING
# =============================================================================

"""
Módulo para preprocesamiento de datos y creación de features.
Incluye limpieza, feature engineering y normalización de datos para múltiples cuentas.
Maneja tanto datos clean como métricas.
"""

import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from typing import Tuple, List, Dict, Optional, Union
from config import PROJECT_CONFIG, CUENTAS_DISPONIBLES

class MultiAccountDataPreprocessor:
    """
    Clase para manejar el preprocesamiento y feature engineering de datos multi-cuenta de Twitter.
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
        self.cuentas_disponibles = CUENTAS_DISPONIBLES
        
    def analyze_data_structure(self, consolidated_data: Dict[str, pd.DataFrame]) -> Dict:
        """
        Analiza la estructura de los datos consolidados.
        
        Args:
            consolidated_data (Dict[str, pd.DataFrame]): Datos consolidados
            
        Returns:
            Dict: Información sobre la estructura de datos
        """
        structure_info = {
            'data_types': list(consolidated_data.keys()),
            'total_dataframes': len(consolidated_data),
            'accounts_info': {},
            'columns_by_type': {}
        }
        
        print("📊 ANÁLISIS DE ESTRUCTURA DE DATOS")
        print("="*50)
        
        for data_type, df in consolidated_data.items():
            print(f"\n📈 {data_type.upper()}:")
            print(f"   • Shape: {df.shape}")
            print(f"   • Columnas: {list(df.columns)}")
            
            structure_info['columns_by_type'][data_type] = list(df.columns)
            
            if 'usuario' in df.columns:
                accounts = df['usuario'].unique()
                print(f"   • Cuentas: {list(accounts)}")
                structure_info['accounts_info'][data_type] = list(accounts)
                
                # Información por cuenta
                for cuenta in accounts:
                    cuenta_data = df[df['usuario'] == cuenta]
                    print(f"     - {cuenta}: {len(cuenta_data):,} registros")
        
        return structure_info
    
    def check_feature_availability(self, data: pd.DataFrame, data_type: str = 'clean') -> Tuple[List[str], List[str]]:
        """
        Verifica la disponibilidad de features en el dataset.
        
        Args:
            data (pd.DataFrame): DataFrame a verificar
            data_type (str): Tipo de datos ('clean', 'metricas')
            
        Returns:
            Tuple[List[str], List[str]]: Features disponibles y faltantes
        """
        # Adaptar features base según el tipo de datos
        if data_type == 'metricas':
            # Para datos de métricas, buscar columnas similares o agregadas
            features_base_adapted = self._adapt_features_for_metricas(data)
        else:
            features_base_adapted = self.features_base
        
        features_disponibles = [col for col in features_base_adapted if col in data.columns]
        features_faltantes = [col for col in features_base_adapted if col not in data.columns]
        
        print(f"📊 Análisis de features ({data_type}):")
        print(f"   ✅ Disponibles: {features_disponibles}")
        if features_faltantes:
            print(f"   ❌ Faltantes: {features_faltantes}")
            
        return features_disponibles, features_faltantes
    
    def _adapt_features_for_metricas(self, data: pd.DataFrame) -> List[str]:
        """
        Adapta las features base para datos de métricas.
        
        Args:
            data (pd.DataFrame): DataFrame de métricas
            
        Returns:
            List[str]: Features adaptadas
        """
        features_adapted = []
        
        # Mapeo de features estándar a posibles nombres en métricas
        feature_mapping = {
            'likes': ['likes', 'promedio_likes', 'total_likes', 'likes_avg'],
            'retweets': ['retweets', 'promedio_retweets', 'total_retweets', 'retweets_avg'],
            'respuestas': ['respuestas', 'promedio_respuestas', 'total_respuestas', 'respuestas_avg'],
            'guardados': ['guardados', 'promedio_guardados', 'total_guardados', 'guardados_avg'],
            'vistas': ['vistas', 'promedio_vistas', 'total_vistas', 'vistas_avg']
        }
        
        # Buscar features disponibles en los datos de métricas
        for base_feature in self.features_base:
            possible_names = feature_mapping.get(base_feature, [base_feature])
            for possible_name in possible_names:
                if possible_name in data.columns:
                    features_adapted.append(possible_name)
                    break
            else:
                # Si no se encuentra, usar el nombre base (se marcará como faltante)
                features_adapted.append(base_feature)
        
        # Añadir features específicas de métricas si están disponibles
        metricas_specific = [
            'engagement_rate', 'reach', 'impressions', 'follower_growth',
            'promedio_engagement', 'tasa_interaccion', 'alcance'
        ]
        
        for feature in metricas_specific:
            if feature in data.columns:
                features_adapted.append(feature)
        
        return features_adapted
    
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
    
    def preprocess_data(self, data: pd.DataFrame, data_type: str = 'clean') -> Tuple[np.ndarray, pd.DataFrame, List[str], Dict]:
        """
        Pipeline completo de preprocesamiento.
        
        Args:
            data (pd.DataFrame): DataFrame original
            data_type (str): Tipo de datos ('clean', 'metricas')
            
        Returns:
            Tuple: X_scaled, data_enhanced, features, info_completa
        """
        # 1. Verificar features disponibles
        features_disponibles, features_faltantes = self.check_feature_availability(data, data_type)
        
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
            'scaling_info': scaling_info,
            'data_type': data_type
        }
        
        print(f"\n✅ Preprocesamiento completado ({data_type}):")
        for key, value in self.features_info.items():
            if key not in ['statistics', 'scaling_info']:  # Evitar imprimir dict complejos
                print(f"   • {key}: {value}")
        
        return X_scaled, data_enhanced, features_disponibles, self.features_info
    
    def preprocess_multi_account_data(self, consolidated_data: Dict[str, pd.DataFrame], 
                                    target_accounts: List[str] = None) -> Dict[str, Tuple]:
        """
        Preprocesa datos de múltiples cuentas con soporte para clean y métricas.
        
        Args:
            consolidated_data (Dict[str, pd.DataFrame]): Datos consolidados por tipo
            target_accounts (List[str]): Cuentas objetivo (opcional)
            
        Returns:
            Dict[str, Tuple]: Resultados de preprocesamiento por tipo de datos
        """
        print("🔄 PREPROCESAMIENTO MULTI-CUENTA")
        print("="*50)
        
        # Analizar estructura de datos
        structure_info = self.analyze_data_structure(consolidated_data)
        
        results = {}
        
        for data_type, df in consolidated_data.items():
            print(f"\n📊 Procesando {data_type.upper()}...")
            
            # Filtrar por cuentas objetivo si se especifica
            if target_accounts and 'usuario' in df.columns:
                df_filtered = df[df['usuario'].isin(target_accounts)].copy()
                print(f"   • Filtrado por cuentas: {target_accounts}")
                print(f"   • Registros: {len(df)} → {len(df_filtered)}")
            else:
                df_filtered = df.copy()
            
            if len(df_filtered) == 0:
                print(f"   ⚠️ No hay datos para procesar en {data_type}")
                continue
            
            # Preprocesar datos
            try:
                X_scaled, data_enhanced, features, info = self.preprocess_data(df_filtered, data_type)
                
                results[data_type] = {
                    'X_scaled': X_scaled,
                    'data_enhanced': data_enhanced,
                    'features': features,
                    'info': info,
                    'structure_info': structure_info
                }
                
                print(f"   ✅ {data_type} procesado exitosamente")
                
            except Exception as e:
                print(f"   ❌ Error procesando {data_type}: {str(e)}")
                results[data_type] = {'error': str(e)}
        
        return results
    
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
    Función principal para preprocesar datos de Twitter (compatibilidad hacia atrás).
    
    Args:
        data (pd.DataFrame): DataFrame original
        features_base (List[str]): Features base (opcional)
        
    Returns:
        Tuple: X_scaled, data_enhanced, features, info_completa
    """
    preprocessor = MultiAccountDataPreprocessor(features_base=features_base)
    return preprocessor.preprocess_data(data)

if __name__ == "__main__":
    # Ejemplo de uso para testing
    import sys
    sys.path.append('.')
    from data_loader import MultiAccountDataLoader
    
    # Cargar datos de ejemplo
    loader = MultiAccountDataLoader()
    
    # Ejemplo 1: Cargar datos consolidados
    print("🧪 EJEMPLO 1: Datos consolidados")
    consolidated_data = loader.load_consolidated_data(mode='consolidado')
    
    if consolidated_data:
        preprocessor = MultiAccountDataPreprocessor()
        results = preprocessor.preprocess_multi_account_data(consolidated_data)
        
        print(f"\n✅ Resultados obtenidos para {len(results)} tipos de datos")
        for data_type, result in results.items():
            if 'error' not in result:
                print(f"   • {data_type}: {result['X_scaled'].shape}")
    
    # Ejemplo 2: Datos individuales (compatibilidad)
    print("\n🧪 EJEMPLO 2: Compatibilidad con datos individuales")
    try:
        from data_loader import load_and_prepare_data
        data, _ = load_and_prepare_data()
        X_scaled, data_enhanced, features, info = preprocess_twitter_data(data)
        print(f"✅ Preprocesamiento compatible completado. Shape: {X_scaled.shape}")
    except Exception as e:
        print(f"⚠️ Error en compatibilidad: {e}")
        print("   (Esto es esperado si no hay datos legacy disponibles)")
