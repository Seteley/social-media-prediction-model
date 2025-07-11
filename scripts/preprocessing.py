# =============================================================================
# PREPROCESAMIENTO PARA MODELOS DE REGRESIÓN POR CUENTA
# =============================================================================

"""
Módulo de preprocesamiento específico para modelos de regresión por cuenta individual.
Enfoque: Preparar datos para predicción de número de seguidores.
"""

import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler, RobustScaler, MinMaxScaler
from sklearn.feature_selection import SelectKBest, f_regression
from .config import TARGET_VARIABLE, FEATURE_CONFIG

class AccountPreprocessor:
    """
    Preprocesador para datos de una cuenta específica.
    """
    
    def __init__(self, account_name: str = None, target_variable: str = None, 
                 scaling_method='standard', feature_selection=True):
        """
        Inicializa el preprocesador.
        
        Args:
            account_name (str): Nombre de la cuenta (opcional)
            target_variable (str): Variable objetivo (opcional)
            scaling_method (str): Método de escalado ('standard', 'robust', 'minmax')
            feature_selection (bool): Si aplicar selección de features
        """
        self.account_name = account_name
        self.target_variable = target_variable or TARGET_VARIABLE
        self.scaling_method = scaling_method
        self.feature_selection = feature_selection
        self.scaler = None
        self.feature_selector = None
        self.selected_features = None
        
        # Configurar scaler
        if scaling_method == 'standard':
            self.scaler = StandardScaler()
        elif scaling_method == 'robust':
            self.scaler = RobustScaler()
        elif scaling_method == 'minmax':
            self.scaler = MinMaxScaler()
        else:
            raise ValueError(f"Método de escalado no válido: {scaling_method}")
    
    def fit_transform(self, X, y):
        """
        Ajusta el preprocesador y transforma los datos.
        
        Args:
            X (pd.DataFrame): Features
            y (pd.Series): Target variable
            
        Returns:
            tuple: (X_processed, feature_names, preprocessing_info)
        """
        print(f"🔧 Preprocesando datos...")
        print(f"   📊 Shape inicial: {X.shape}")
        
        # 1. Limpiar datos
        X_clean, y_clean = self._clean_data(X, y)
        print(f"   🧹 Shape después de limpieza: {X_clean.shape}")
        
        # 2. Crear features adicionales
        X_enhanced = self._create_additional_features(X_clean)
        print(f"   ⚙️  Shape después de feature engineering: {X_enhanced.shape}")
        
        # 3. Selección de features
        if self.feature_selection and len(X_enhanced.columns) > 5:
            X_selected = self._select_features(X_enhanced, y_clean)
            print(f"   🎯 Shape después de selección: {X_selected.shape}")
        else:
            X_selected = X_enhanced
            self.selected_features = list(X_enhanced.columns)
        
        # 4. Escalado
        X_scaled = self._scale_features(X_selected)
        print(f"   📏 Escalado completado con {self.scaling_method}")
        
        # Información del preprocesamiento
        preprocessing_info = {
            'original_shape': X.shape,
            'final_shape': X_scaled.shape,
            'features_removed': set(X.columns) - set(self.selected_features),
            'scaling_method': self.scaling_method,
            'samples_removed': len(X) - len(X_scaled)
        }
        
        return X_scaled, self.selected_features, preprocessing_info
    
    def transform(self, X):
        """
        Transforma nuevos datos usando el preprocesador ajustado.
        
        Args:
            X (pd.DataFrame): Features a transformar
            
        Returns:
            np.ndarray: Features transformadas
        """
        if self.scaler is None:
            raise ValueError("El preprocesador debe ser ajustado primero con fit_transform()")
        
        # Aplicar las mismas transformaciones
        X_clean = X.fillna(X.median())
        X_enhanced = self._create_additional_features(X_clean)
        
        # Seleccionar solo las features que se usaron en el entrenamiento
        X_selected = X_enhanced[self.selected_features]
        
        # Escalar
        X_scaled = self.scaler.transform(X_selected)
        
        return X_scaled
    
    def _clean_data(self, X, y):
        """Limpia los datos removiendo outliers y valores problemáticos."""
        # Combinar X y y para limpieza conjunta
        data = X.copy()
        data[TARGET_VARIABLE] = y
        
        # Remover filas con target nulo o negativo
        data = data[data[TARGET_VARIABLE].notna()]
        data = data[data[TARGET_VARIABLE] >= 0]
        
        # Remover outliers extremos en target (más de 3 desviaciones estándar)
        target_mean = data[TARGET_VARIABLE].mean()
        target_std = data[TARGET_VARIABLE].std()
        outlier_threshold = 3
        
        data = data[
            (data[TARGET_VARIABLE] >= target_mean - outlier_threshold * target_std) &
            (data[TARGET_VARIABLE] <= target_mean + outlier_threshold * target_std)
        ]
        
        # Separar X y y limpiados
        y_clean = data[TARGET_VARIABLE]
        X_clean = data.drop(columns=[TARGET_VARIABLE])
        
        # Rellenar valores faltantes en X
        for col in X_clean.columns:
            if X_clean[col].dtype in ['int64', 'float64']:
                X_clean[col] = X_clean[col].fillna(X_clean[col].median())
            else:
                X_clean[col] = X_clean[col].fillna(X_clean[col].mode()[0] if not X_clean[col].mode().empty else 0)
        
        return X_clean, y_clean
    
    def _create_additional_features(self, X):
        """Crea features adicionales para mejorar el modelo."""
        X_enhanced = X.copy()
        
        # Features de ratios
        if 'likes' in X.columns and 'vistas' in X.columns:
            X_enhanced['likes_per_view'] = X_enhanced['likes'] / (X_enhanced['vistas'] + 1)
        
        if 'retweets' in X.columns and 'likes' in X.columns:
            X_enhanced['retweet_like_ratio'] = X_enhanced['retweets'] / (X_enhanced['likes'] + 1)
        
        if 'respuestas' in X.columns and 'total_interacciones' in X.columns:
            X_enhanced['reply_interaction_ratio'] = X_enhanced['respuestas'] / (X_enhanced['total_interacciones'] + 1)
        
        # Features logarítmicas para variables con gran varianza
        log_features = ['vistas', 'likes', 'total_interacciones']
        for feature in log_features:
            if feature in X.columns:
                X_enhanced[f'log_{feature}'] = np.log1p(X_enhanced[feature])
        
        # Features cuadráticas para engagement
        if 'engagement_rate' in X.columns:
            X_enhanced['engagement_rate_squared'] = X_enhanced['engagement_rate'] ** 2
        
        # Features temporales mejoradas
        if 'hora' in X.columns:
            X_enhanced['es_hora_pico'] = X_enhanced['hora'].apply(lambda x: 1 if x in [12, 19, 20, 21] else 0)
        
        if 'dia_semana' in X.columns:
            X_enhanced['es_fin_semana'] = X_enhanced['dia_semana'].apply(lambda x: 1 if x in [5, 6] else 0)
        
        return X_enhanced
    
    def _select_features(self, X, y, k=10):
        """Selecciona las mejores features usando SelectKBest."""
        # Ajustar k al número de features disponibles
        k = min(k, len(X.columns))
        
        self.feature_selector = SelectKBest(f_regression, k=k)
        X_selected = self.feature_selector.fit_transform(X, y)
        
        # Obtener nombres de features seleccionadas
        selected_indices = self.feature_selector.get_support(indices=True)
        self.selected_features = [X.columns[i] for i in selected_indices]
        
        return pd.DataFrame(X_selected, columns=self.selected_features, index=X.index)
    
    def _scale_features(self, X):
        """Escala las features usando el método especificado."""
        X_scaled = self.scaler.fit_transform(X)
        return X_scaled
    
    def get_feature_importance_scores(self):
        """
        Obtiene los scores de importancia de features.
        
        Returns:
            pd.DataFrame: Scores de importancia
        """
        if self.feature_selector is None:
            return None
        
        scores = self.feature_selector.scores_
        selected_indices = self.feature_selector.get_support(indices=True)
        
        importance_df = pd.DataFrame({
            'feature': self.selected_features,
            'score': scores[selected_indices]
        }).sort_values('score', ascending=False)
        
        return importance_df
    
    def process_account_data(self, data: pd.DataFrame):
        """
        Procesa los datos de una cuenta específica para regresión.
        
        Args:
            data (pd.DataFrame): Datos de la cuenta
            
        Returns:
            tuple: (processed_data, feature_names)
        """
        print(f"🔧 Procesando datos para regresión de {self.account_name or 'cuenta'}")
        
        # Generar features temporales
        data_enhanced = self._create_temporal_features(data.copy())
        
        # Generar features derivadas
        data_enhanced = self._create_derived_features(data_enhanced)
        
        # Limpiar datos
        data_clean = self._clean_data(data_enhanced)
        
        # Obtener lista de features disponibles
        all_features = []
        for feature_group in FEATURE_CONFIG.values():
            all_features.extend(feature_group)
        
        # Filtrar features que existen en los datos
        available_features = [col for col in all_features if col in data_clean.columns]
        
        print(f"   ✅ Features generadas: {len(available_features)}")
        print(f"   ✅ Registros procesados: {len(data_clean)}")
        
        return data_clean, available_features
    
    def _create_temporal_features(self, data: pd.DataFrame) -> pd.DataFrame:
        """Crea features temporales."""
        if 'fecha_publicacion' in data.columns:
            data['fecha_publicacion'] = pd.to_datetime(data['fecha_publicacion'])
            data['dia_semana'] = data['fecha_publicacion'].dt.dayofweek
            data['hora'] = data['fecha_publicacion'].dt.hour
            data['mes'] = data['fecha_publicacion'].dt.month
        
        return data
    
    def _create_derived_features(self, data: pd.DataFrame) -> pd.DataFrame:
        """Crea features derivadas."""
        # Engagement rate
        if all(col in data.columns for col in ['likes', 'retweets', 'respuestas', 'vistas']):
            data['total_interacciones'] = data['likes'] + data['retweets'] + data['respuestas']
            data['engagement_rate'] = data['total_interacciones'] / (data['vistas'] + 1)
            data['ratio_likes_vistas'] = data['likes'] / (data['vistas'] + 1)
        
        return data
    
    def _clean_data(self, data: pd.DataFrame) -> pd.DataFrame:
        """Limpia los datos."""
        # Llenar valores nulos
        numeric_cols = data.select_dtypes(include=[np.number]).columns
        data[numeric_cols] = data[numeric_cols].fillna(0)
        
        # Remover valores infinitos
        data = data.replace([np.inf, -np.inf], 0)
        
        return data

class BatchPreprocessor:
    """
    Preprocesador para múltiples cuentas de forma consistente.
    """
    
    def __init__(self, scaling_method='standard'):
        """
        Inicializa el preprocesador batch.
        
        Args:
            scaling_method (str): Método de escalado
        """
        self.scaling_method = scaling_method
        self.preprocessors = {}
    
    def process_multiple_accounts(self, accounts_data):
        """
        Procesa datos de múltiples cuentas.
        
        Args:
            accounts_data (dict): Datos de múltiples cuentas
            
        Returns:
            dict: Datos procesados por cuenta
        """
        processed_data = {}
        
        print(f"🔄 Procesando {len(accounts_data)} cuentas...")
        
        for account, data in accounts_data.items():
            try:
                print(f"\n📊 Procesando cuenta: {account}")
                
                # Extraer X y y
                df = data['combined']
                
                feature_columns = [col for col in df.columns 
                                 if col not in ['fecha_publicacion', 'contenido', TARGET_VARIABLE]]
                
                X = df[feature_columns]
                y = df[TARGET_VARIABLE]
                
                # Crear preprocesador para esta cuenta
                preprocessor = AccountPreprocessor(scaling_method=self.scaling_method)
                
                # Procesar
                X_processed, features, info = preprocessor.fit_transform(X, y)
                
                # Guardar resultados
                processed_data[account] = {
                    'X': X_processed,
                    'y': y.values,
                    'features': features,
                    'preprocessor': preprocessor,
                    'info': info,
                    'original_data': df
                }
                
                print(f"   ✅ Procesado: {info['final_shape']} shape final")
                
            except Exception as e:
                print(f"   ❌ Error procesando {account}: {e}")
                continue
        
        self.preprocessors = {account: data['preprocessor'] 
                            for account, data in processed_data.items()}
        
        return processed_data

# =============================================================================
# FUNCIONES DE UTILIDAD
# =============================================================================

def preprocess_account_data(X, y, account_name="unknown", scaling_method='standard'):
    """
    Función simple para preprocesar datos de una cuenta.
    
    Args:
        X (pd.DataFrame): Features
        y (pd.Series): Target
        account_name (str): Nombre de la cuenta
        scaling_method (str): Método de escalado
        
    Returns:
        dict: Datos procesados
    """
    print(f"🔧 Preprocesando datos para {account_name}...")
    
    preprocessor = AccountPreprocessor(scaling_method=scaling_method)
    X_processed, features, info = preprocessor.fit_transform(X, y)
    
    return {
        'X': X_processed,
        'y': y.values,
        'features': features,
        'preprocessor': preprocessor,
        'info': info
    }

def get_preprocessing_summary(preprocessing_info):
    """
    Genera un resumen del preprocesamiento.
    
    Args:
        preprocessing_info (dict): Información del preprocesamiento
        
    Returns:
        str: Resumen formateado
    """
    info = preprocessing_info
    
    summary = f"""
📋 RESUMEN DE PREPROCESAMIENTO
{'=' * 40}
📊 Shape original: {info['original_shape']}
🎯 Shape final: {info['final_shape']}
🗑️  Muestras removidas: {info['samples_removed']}
🔧 Features removidas: {len(info['features_removed'])}
📏 Método de escalado: {info['scaling_method']}
    """
    
    if info['features_removed']:
        summary += f"\n🚫 Features eliminadas: {list(info['features_removed'])[:5]}..."
    
    return summary

# =============================================================================
# EJEMPLO DE USO
# =============================================================================

if __name__ == "__main__":
    print("🧪 Probando preprocesamiento...")
    
    # Crear datos de prueba
    np.random.seed(42)
    n_samples = 100
    
    test_data = pd.DataFrame({
        'likes': np.random.poisson(50, n_samples),
        'retweets': np.random.poisson(10, n_samples),
        'vistas': np.random.poisson(1000, n_samples),
        'engagement_rate': np.random.normal(0.05, 0.02, n_samples),
        'hora': np.random.randint(0, 24, n_samples),
        'dia_semana': np.random.randint(0, 7, n_samples)
    })
    
    test_target = np.random.normal(10000, 2000, n_samples)
    test_target = np.maximum(test_target, 0)  # Asegurar valores positivos
    
    # Probar preprocesamiento
    result = preprocess_account_data(test_data, test_target, "test_account")
    
    print(f"✅ Preprocesamiento completado")
    print(f"📊 Shape procesada: {result['X'].shape}")
    print(f"🎯 Features seleccionadas: {len(result['features'])}")
    print(f"📋 Features: {result['features'][:5]}...")
    
    # Mostrar resumen
    print(get_preprocessing_summary(result['info']))
