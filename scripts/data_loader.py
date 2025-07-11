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
        Carga todos los datos de la cuenta desde la base de datos.
        
        Returns:
            dict: Diccionario con datos de publicaciones, métricas y combinados
        """
        print(f"📊 Cargando datos para la cuenta: {self.account_name}")
        
        try:
            self.connection = get_database_connection()
            
            # Cargar datos de publicaciones
            publicaciones_df = self._load_publicaciones()
            print(f"   ✅ Publicaciones cargadas: {len(publicaciones_df)} registros")
            
            # Cargar datos de métricas
            metricas_df = self._load_metricas()
            print(f"   ✅ Métricas cargadas: {len(metricas_df)} registros")
            
            # Combinar datos
            combined_df = self._combine_data(publicaciones_df, metricas_df)
            print(f"   ✅ Datos combinados: {len(combined_df)} registros")
            
            self.connection.close()
            
            return {
                'publicaciones': publicaciones_df,
                'metricas': metricas_df,
                'combined': combined_df,
                'account': self.account_name
            }
            
        except Exception as e:
            if self.connection:
                self.connection.close()
            print(f"❌ Error cargando datos para {self.account_name}: {e}")
            return None
    
    def _load_publicaciones(self):
        """Carga datos de publicaciones de la cuenta."""
        query = """
        SELECT 
            p.id_publicacion,
            p.fecha_publicacion,
            p.contenido,
            p.respuestas,
            p.retweets,
            p.likes,
            p.guardados,
            p.vistas
        FROM publicaciones p
        INNER JOIN usuario u ON p.id_usuario = u.id_usuario
        WHERE u.cuenta = ?
        ORDER BY p.fecha_publicacion
        """
        
        df = self.connection.execute(query, [self.account_name]).fetchdf()
        
        # Procesar fechas
        if not df.empty:
            df['fecha_publicacion'] = pd.to_datetime(df['fecha_publicacion'])
            
            # Agregar features temporales
            df['dia_semana'] = df['fecha_publicacion'].dt.dayofweek
            df['hora'] = df['fecha_publicacion'].dt.hour
            df['mes'] = df['fecha_publicacion'].dt.month
            
            # Rellenar valores nulos
            numeric_cols = ['respuestas', 'retweets', 'likes', 'guardados', 'vistas']
            for col in numeric_cols:
                df[col] = df[col].fillna(0)
        
        return df
    
    def _load_metricas(self):
        """Carga datos de métricas de la cuenta."""
        query = """
        SELECT 
            m.id_metrica,
            m.hora,
            m.seguidores,
            m.tweets,
            m.siguiendo
        FROM metrica m
        INNER JOIN usuario u ON m.id_usuario = u.id_usuario
        WHERE u.cuenta = ?
        ORDER BY m.hora
        """
        
        df = self.connection.execute(query, [self.account_name]).fetchdf()
        
        # Procesar fechas
        if not df.empty:
            df['hora'] = pd.to_datetime(df['hora'])
            
            # Rellenar valores nulos
            numeric_cols = ['seguidores', 'tweets', 'siguiendo']
            for col in numeric_cols:
                df[col] = df[col].fillna(df[col].median())
        
        return df
    
    def _combine_data(self, publicaciones_df, metricas_df):
        """
        Combina datos de publicaciones y métricas.
        
        Args:
            publicaciones_df: DataFrame de publicaciones
            metricas_df: DataFrame de métricas
            
        Returns:
            pd.DataFrame: Datos combinados
        """
        if publicaciones_df.empty or metricas_df.empty:
            print("⚠️  Datos insuficientes para combinar")
            return pd.DataFrame()
        
        # Usar la métrica más reciente para cada publicación
        # (en una implementación real, podrías hacer un join temporal más sofisticado)
        latest_metric = metricas_df.iloc[-1]  # Métrica más reciente
        
        # Agregar métricas a publicaciones
        combined = publicaciones_df.copy()
        combined['seguidores'] = latest_metric['seguidores']
        combined['total_tweets'] = latest_metric['tweets']
        combined['siguiendo'] = latest_metric['siguiendo']
        
        # Calcular features derivadas
        combined = self._calculate_derived_features(combined)
        
        return combined
    
    def _calculate_derived_features(self, df):
        """
        Calcula features derivadas para el análisis.
        
        Args:
            df: DataFrame con datos base
            
        Returns:
            pd.DataFrame: DataFrame con features adicionales
        """
        # Engagement rate
        df['engagement_rate'] = 0.0
        mask_vistas = df['vistas'] > 0
        df.loc[mask_vistas, 'engagement_rate'] = (
            df.loc[mask_vistas, 'respuestas'] +
            df.loc[mask_vistas, 'retweets'] +
            df.loc[mask_vistas, 'likes'] +
            df.loc[mask_vistas, 'guardados']
        ) / df.loc[mask_vistas, 'vistas']
        
        # Total de interacciones
        df['total_interacciones'] = (
            df['respuestas'] + df['retweets'] + 
            df['likes'] + df['guardados']
        )
        
        # Ratio likes/vistas
        df['ratio_likes_vistas'] = 0.0
        df.loc[mask_vistas, 'ratio_likes_vistas'] = (
            df.loc[mask_vistas, 'likes'] / df.loc[mask_vistas, 'vistas']
        )
        
        # Longitud del contenido
        df['longitud_contenido'] = df['contenido'].str.len().fillna(0)
        
        # Ratio de engagement por seguidor
        df['engagement_per_follower'] = 0.0
        mask_seguidores = df['seguidores'] > 0
        df.loc[mask_seguidores, 'engagement_per_follower'] = (
            df.loc[mask_seguidores, 'total_interacciones'] / 
            df.loc[mask_seguidores, 'seguidores']
        )
        
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
        Obtiene resumen de todas las cuentas disponibles.
        
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
                        'total_publicaciones': len(df),
                        'seguidores': df['seguidores'].iloc[-1] if 'seguidores' in df.columns else 0,
                        'engagement_promedio': df['engagement_rate'].mean(),
                        'likes_promedio': df['likes'].mean(),
                        'vistas_promedio': df['vistas'].mean(),
                        'fecha_primera_pub': df['fecha_publicacion'].min(),
                        'fecha_ultima_pub': df['fecha_publicacion'].max()
                    }
                    
                    summary_data.append(summary)
                    
            except Exception as e:
                print(f"⚠️  Error procesando {account}: {e}")
                continue
        
        return pd.DataFrame(summary_data)

# =============================================================================
# FUNCIONES DE UTILIDAD
# =============================================================================

def load_account_for_regression(account_name: str):
    """
    Carga datos de una cuenta específica listos para regresión.
    
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
    
    # Seleccionar features para regresión
    feature_columns = [
        'respuestas', 'retweets', 'likes', 'guardados', 'vistas',
        'dia_semana', 'hora', 'mes',
        'engagement_rate', 'total_interacciones', 'ratio_likes_vistas',
        'longitud_contenido', 'engagement_per_follower'
    ]
    
    # Filtrar features que existen y tienen variación
    available_features = []
    for col in feature_columns:
        if col in df.columns and df[col].var() > 0:
            available_features.append(col)
    
    if len(available_features) == 0:
        print(f"❌ No hay features válidas para {account_name}")
        return None, None, None, None
    
    X = df[available_features].fillna(0)
    y = df[TARGET_VARIABLE].fillna(df[TARGET_VARIABLE].median())
    
    data_info = {
        'account': account_name,
        'total_samples': len(df),
        'features_count': len(available_features),
        'target_mean': y.mean(),
        'target_std': y.std()
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
