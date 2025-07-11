# =============================================================================
# CARGA DE DATOS DESDE BASE DE DATOS POR CUENTA INDIVIDUAL
# =============================================================================

"""
Módulo para cargar datos específicos de cada cuenta desde la base de datos DuckDB.
Enfoque: Obtener datos de publicaciones y métricas para modelos de regresión.
"""

import pandas as pd
import numpy as np
from datetime import datetime
from .config import get_database_connection, get_available_accounts, TARGET_VARIABLE

class AccountDataLoader:
    """
    Cargador de datos para una cuenta específica desde la base de datos.
    """
    
    def __init__(self, account_name: str):
        """
        Inicializa el cargador para una cuenta específica.
        
        Args:
            account_name (str): Nombre de la cuenta de Twitter
        """
        self.account_name = account_name
        self.connection = None
        
    def load_account_data(self):
        """
        Carga datos de métricas para predicción de seguidores.
        
        Returns:
            dict: Diccionario con datos de métricas temporales
        """
        print(f"📊 Cargando datos de métricas para: {self.account_name}")
        
        try:
            self.connection = get_database_connection()
            
            # Query SQL enfocada en la tabla metrica con agregaciones de publicaciones
            query = """
            WITH publicaciones_stats AS (
                SELECT 
                    p.id_usuario,
                    DATE(p.fecha_publicacion) as fecha,
                    COUNT(*) as publicaciones_dia,
                    AVG(p.likes) as avg_likes_dia,
                    AVG(p.retweets) as avg_retweets_dia,
                    AVG(p.respuestas) as avg_respuestas_dia,
                    AVG(p.vistas) as avg_vistas_dia,
                    SUM(p.likes + p.retweets + p.respuestas) as total_engagement_dia
                FROM publicaciones p
                JOIN usuario u ON p.id_usuario = u.id_usuario
                WHERE u.cuenta = ?
                GROUP BY p.id_usuario, DATE(p.fecha_publicacion)
            )
            SELECT 
                m.id_metrica,
                m.hora as timestamp_metrica,
                m.seguidores,
                m.tweets as total_tweets,
                m.siguiendo,
                u.cuenta,
                u.nombre,
                COALESCE(ps.publicaciones_dia, 0) as publicaciones_dia,
                COALESCE(ps.avg_likes_dia, 0) as avg_likes_dia,
                COALESCE(ps.avg_retweets_dia, 0) as avg_retweets_dia,
                COALESCE(ps.avg_respuestas_dia, 0) as avg_respuestas_dia,
                COALESCE(ps.avg_vistas_dia, 0) as avg_vistas_dia,
                COALESCE(ps.total_engagement_dia, 0) as total_engagement_dia
            FROM metrica m
            JOIN usuario u ON m.id_usuario = u.id_usuario
            LEFT JOIN publicaciones_stats ps ON m.id_usuario = ps.id_usuario 
                AND DATE(m.hora) = ps.fecha
            WHERE u.cuenta = ?
            ORDER BY m.hora DESC
            """
            
            # Ejecutar query con el nombre de cuenta dos veces
            metrica_df = self.connection.execute(query, [self.account_name, self.account_name]).df()
            
            if metrica_df.empty:
                print(f"   ❌ No se encontraron datos de métricas para {self.account_name}")
                self.connection.close()
                return {'combined': pd.DataFrame(), 'account': self.account_name}
            
            # Procesar datos
            metrica_df = self._process_metrica_data(metrica_df)
            
            print(f"   ✅ Datos de métricas: {len(metrica_df)} registros")
            print(f"   ✅ Columnas disponibles: {list(metrica_df.columns)}")
            
            # Mostrar estadísticas de seguidores
            if 'seguidores' in metrica_df.columns:
                seguidores_stats = metrica_df['seguidores'].describe()
                print(f"   📊 Estadísticas de seguidores:")
                print(f"      - Media: {seguidores_stats['mean']:,.0f}")
                print(f"      - Min: {seguidores_stats['min']:,.0f}")
                print(f"      - Max: {seguidores_stats['max']:,.0f}")
                print(f"      - Std: {seguidores_stats['std']:,.2f}")
            
            self.connection.close()
            
            return {
                'combined': metrica_df,
                'account': self.account_name
            }
            
        except Exception as e:
            if self.connection:
                self.connection.close()
            print(f"❌ Error cargando datos para {self.account_name}: {e}")
            return {'combined': pd.DataFrame(), 'account': self.account_name}
    
    def _process_metrica_data(self, df):
        """
        Procesa los datos de métricas y agrega features derivadas para predicción de seguidores.
        
        Args:
            df (pd.DataFrame): Datos de métricas con estadísticas de publicaciones
            
        Returns:
            pd.DataFrame: Datos procesados con features adicionales
        """
        df = df.copy()
        
        # Limpiar datos nulos usando forward fill moderno
        df['seguidores'] = df['seguidores'].ffill().fillna(0)
        df['total_tweets'] = df['total_tweets'].ffill().fillna(0)
        df['siguiendo'] = df['siguiendo'].ffill().fillna(0)
        
        # Convertir fechas
        df['timestamp_metrica'] = pd.to_datetime(df['timestamp_metrica'])
        
        # Features temporales
        df['año'] = df['timestamp_metrica'].dt.year
        df['mes'] = df['timestamp_metrica'].dt.month
        df['dia_semana'] = df['timestamp_metrica'].dt.dayofweek
        df['hora'] = df['timestamp_metrica'].dt.hour
        df['dia_año'] = df['timestamp_metrica'].dt.dayofyear
        
        # Ordenar por tiempo para features de tendencia
        df = df.sort_values('timestamp_metrica')
        
        # Features de crecimiento/tendencia (diferencias temporales)
        df['seguidores_diff'] = df['seguidores'].diff().fillna(0)
        df['tweets_diff'] = df['total_tweets'].diff().fillna(0)
        df['siguiendo_diff'] = df['siguiendo'].diff().fillna(0)
        
        # Features de ratios
        df['ratio_seguidores_siguiendo'] = df['seguidores'] / (df['siguiendo'] + 1)
        df['ratio_seguidores_tweets'] = df['seguidores'] / (df['total_tweets'] + 1)
        
        # Features de engagement promedio
        df['engagement_rate_promedio'] = df['total_engagement_dia'] / (df['publicaciones_dia'] + 1)
        df['actividad_publicacion'] = df['publicaciones_dia']
        
        # Features de ventana móvil (últimos 7 registros)
        window_size = min(7, len(df))
        if window_size > 1:
            df['seguidores_ma7'] = df['seguidores'].rolling(window=window_size, min_periods=1).mean()
            df['seguidores_std7'] = df['seguidores'].rolling(window=window_size, min_periods=1).std().fillna(0)
            df['engagement_ma7'] = df['total_engagement_dia'].rolling(window=window_size, min_periods=1).mean()
        else:
            df['seguidores_ma7'] = df['seguidores']
            df['seguidores_std7'] = 0
            df['engagement_ma7'] = df['total_engagement_dia']
        
        # Features de posición temporal (normalizado)
        df['posicion_temporal'] = (df['timestamp_metrica'] - df['timestamp_metrica'].min()).dt.days
        
        return df
class MultiAccountLoader:
    """
    Cargador para múltiples cuentas.
    """
    
    def __init__(self):
        """Inicializa el cargador multi-cuenta."""
        self.available_accounts = get_available_accounts()
        
    def load_all_accounts(self):
        """
        Carga datos de todas las cuentas disponibles.
        
        Returns:
            dict: Diccionario con datos de cada cuenta
        """
        print(f"🔄 Cargando datos de {len(self.available_accounts)} cuentas...")
        
        all_data = {}
        
        for account in self.available_accounts:
            loader = AccountDataLoader(account)
            account_data = loader.load_account_data()
            
            if account_data:
                all_data[account] = account_data
                print(f"   ✅ {account}: {len(account_data['combined'])} registros")
            else:
                print(f"   ❌ {account}: Error en carga")
        
        print(f"📊 Total cuentas cargadas exitosamente: {len(all_data)}")
        return all_data
    
    def get_account_summary(self):
        """
        Obtiene resumen de todas las cuentas disponibles basado en métricas.
        
        Returns:
            pd.DataFrame: DataFrame con resumen por cuenta
        """
        summary_data = []
        
        for account in self.available_accounts:
            try:
                loader = AccountDataLoader(account)
                data = loader.load_account_data()
                
                if data and not data['combined'].empty:
                    df = data['combined']
                    
                    summary = {
                        'cuenta': account,
                        'total_registros_metrica': len(df),
                        'seguidores_actual': df['seguidores'].iloc[-1] if 'seguidores' in df.columns and not df['seguidores'].empty else 0,
                        'seguidores_promedio': df['seguidores'].mean() if 'seguidores' in df.columns else 0,
                        'crecimiento_seguidores': df['seguidores_diff'].sum() if 'seguidores_diff' in df.columns else 0,
                        'total_tweets': df['total_tweets'].iloc[-1] if 'total_tweets' in df.columns and not df['total_tweets'].empty else 0,
                        'siguiendo': df['siguiendo'].iloc[-1] if 'siguiendo' in df.columns and not df['siguiendo'].empty else 0,
                        'publicaciones_promedio_dia': df['publicaciones_dia'].mean() if 'publicaciones_dia' in df.columns else 0,
                        'engagement_promedio_dia': df['total_engagement_dia'].mean() if 'total_engagement_dia' in df.columns else 0,
                        'fecha_primera_metrica': df['timestamp_metrica'].min() if 'timestamp_metrica' in df.columns else None,
                        'fecha_ultima_metrica': df['timestamp_metrica'].max() if 'timestamp_metrica' in df.columns else None
                    }
                    
                    summary_data.append(summary)
                else:
                    # Agregar cuenta con datos vacíos
                    summary = {
                        'cuenta': account,
                        'total_registros_metrica': 0,
                        'seguidores_actual': 0,
                        'seguidores_promedio': 0,
                        'crecimiento_seguidores': 0,
                        'total_tweets': 0,
                        'siguiendo': 0,
                        'publicaciones_promedio_dia': 0,
                        'engagement_promedio_dia': 0,
                        'fecha_primera_metrica': None,
                        'fecha_ultima_metrica': None
                    }
                    summary_data.append(summary)
                    
            except Exception as e:
                print(f"⚠️  Error procesando {account}: {e}")
                # Agregar cuenta con error
                summary = {
                    'cuenta': account,
                    'total_registros_metrica': -1,  # Indicador de error
                    'seguidores_actual': 0,
                    'seguidores_promedio': 0,
                    'crecimiento_seguidores': 0,
                    'total_tweets': 0,
                    'siguiendo': 0,
                    'publicaciones_promedio_dia': 0,
                    'engagement_promedio_dia': 0,
                    'fecha_primera_metrica': None,
                    'fecha_ultima_metrica': None
                }
                summary_data.append(summary)
                continue
        
        return pd.DataFrame(summary_data)

# =============================================================================
# FUNCIONES DE UTILIDAD
# =============================================================================

def load_account_for_regression(account_name: str):
    """
    Carga datos de una cuenta específica listos para regresión de seguidores.
    
    Args:
        account_name (str): Nombre de la cuenta
        
    Returns:
        tuple: (X, y, feature_names, data_info)
    """
    loader = AccountDataLoader(account_name)
    data = loader.load_account_data()
    
    if not data or data['combined'].empty:
        return None, None, None, None
    
    df = data['combined']
    
    # Seleccionar features para regresión de seguidores
    feature_columns = [
        'total_tweets', 'siguiendo', 'dia_semana', 'hora', 'mes', 'dia_año',
        'seguidores_diff', 'tweets_diff', 'siguiendo_diff',
        'ratio_seguidores_siguiendo', 'ratio_seguidores_tweets',
        'publicaciones_dia', 'avg_likes_dia', 'avg_retweets_dia', 
        'avg_respuestas_dia', 'avg_vistas_dia', 'total_engagement_dia',
        'engagement_rate_promedio', 'actividad_publicacion',
        'seguidores_ma7', 'seguidores_std7', 'engagement_ma7',
        'posicion_temporal'
    ]
    
    # Filtrar features que existen y tienen variación
    available_features = []
    for col in feature_columns:
        if col in df.columns and df[col].var() > 0:
            available_features.append(col)
    
    if len(available_features) == 0:
        print(f"❌ No hay features válidas para {account_name}")
        return None, None, None, None
    
    # Remover outliers extremos en seguidores (opcional)
    Q1 = df[TARGET_VARIABLE].quantile(0.25)
    Q3 = df[TARGET_VARIABLE].quantile(0.75)
    IQR = Q3 - Q1
    lower_bound = Q1 - 1.5 * IQR
    upper_bound = Q3 + 1.5 * IQR
    
    # Filtrar solo outliers extremos, mantener la mayoría de datos
    mask = (df[TARGET_VARIABLE] >= lower_bound) & (df[TARGET_VARIABLE] <= upper_bound)
    if mask.sum() > len(df) * 0.8:  # Si perdemos menos del 20% de datos
        df = df[mask]
    
    X = df[available_features].fillna(0)
    y = df[TARGET_VARIABLE].fillna(df[TARGET_VARIABLE].median())
    
    data_info = {
        'account': account_name,
        'total_samples': len(df),
        'features_count': len(available_features),
        'target_mean': y.mean(),
        'target_std': y.std(),
        'target_range': y.max() - y.min(),
        'time_span': df['timestamp_metrica'].max() - df['timestamp_metrica'].min()
    }
    
    return X, y, available_features, data_info

def get_accounts_summary():
    """
    Obtiene resumen rápido de todas las cuentas.
    
    Returns:
        pd.DataFrame: Resumen de cuentas
    """
    loader = MultiAccountLoader()
    return loader.get_account_summary()

# =============================================================================
# EJEMPLO DE USO
# =============================================================================

if __name__ == "__main__":
    print("🧪 Probando carga de datos...")
    
    # Obtener cuentas disponibles
    accounts = get_available_accounts()
    print(f"📋 Cuentas disponibles: {accounts}")
    
    if accounts:
        # Probar con la primera cuenta
        test_account = accounts[0]
        print(f"\n🔍 Probando con cuenta: {test_account}")
        
        # Cargar datos para regresión
        X, y, features, info = load_account_for_regression(test_account)
        
        if X is not None:
            print(f"✅ Datos cargados exitosamente:")
            print(f"   • Muestras: {info['total_samples']}")
            print(f"   • Features: {info['features_count']}")
            print(f"   • Target promedio: {info['target_mean']:.2f}")
            print(f"   • Features disponibles: {features[:5]}...")  # Mostrar primeros 5
        else:
            print("❌ Error cargando datos")
        
        # Obtener resumen de todas las cuentas
        print(f"\n📊 Resumen de todas las cuentas:")
        summary = get_accounts_summary()
        if not summary.empty:
            print(summary.to_string(index=False))
        else:
            print("❌ No se pudo generar resumen")
    else:
        print("❌ No hay cuentas disponibles en la base de datos")
