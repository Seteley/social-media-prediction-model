# =============================================================================
# CARGA Y CONSOLIDACIÓN DE DATOS
# =============================================================================

"""
Módulo para la carga automática y consolidación de datos de Twitter.
Busca archivos *_clean.csv y los consolida en un DataFrame único.
"""

import os
import glob
import pandas as pd
from typing import Tuple, List, Dict, Optional
from config import PROJECT_CONFIG

class DataLoader:
    """
    Clase para manejar la carga y consolidación de datos de Twitter.
    """
    
    def __init__(self, data_folder: str = None, file_pattern: str = None):
        """
        Inicializa el cargador de datos.
        
        Args:
            data_folder (str): Carpeta donde buscar los datos
            file_pattern (str): Patrón de archivos a buscar
        """
        self.data_folder = data_folder or PROJECT_CONFIG['data_folder']
        self.file_pattern = file_pattern or PROJECT_CONFIG['file_pattern']
        
    def find_data_files(self) -> List[str]:
        """
        Busca archivos de datos limpios en la carpeta especificada.
        
        Returns:
            List[str]: Lista de rutas de archivos encontrados
            
        Raises:
            FileNotFoundError: Si no se encuentran archivos
        """
        search_pattern = os.path.join(self.data_folder, self.file_pattern)
        csv_files = glob.glob(search_pattern)
        
        if not csv_files:
            raise FileNotFoundError(
                f"❌ No se encontraron archivos {self.file_pattern} en la carpeta {self.data_folder}/.\n"
                "Asegúrate de que los datos estén procesados y guardados correctamente."
            )
        
        return csv_files
    
    def load_single_file(self, file_path: str) -> Tuple[pd.DataFrame, str]:
        """
        Carga un solo archivo CSV y extrae información del usuario.
        
        Args:
            file_path (str): Ruta del archivo a cargar
            
        Returns:
            Tuple[pd.DataFrame, str]: DataFrame cargado y nombre del usuario
        """
        # Extraer nombre del usuario del archivo
        usuario = os.path.basename(file_path).replace('_clean.csv', '')
        
        # Cargar datos
        df = pd.read_csv(file_path)
        df['usuario'] = usuario
        
        return df, usuario
    
    def consolidate_data(self) -> Tuple[pd.DataFrame, Dict]:
        """
        Consolida todos los archivos de datos en un DataFrame único.
        
        Returns:
            Tuple[pd.DataFrame, Dict]: DataFrame consolidado e información del proceso
        """
        csv_files = self.find_data_files()
        
        print(f"📁 Archivos encontrados: {len(csv_files)}")
        for file in csv_files:
            print(f"   • {os.path.basename(file)}")
        
        # Consolidación de datos
        usuarios = []
        dfs = []
        total_tweets = 0
        
        for file in csv_files:
            df, usuario = self.load_single_file(file)
            
            # Información del archivo
            print(f"📊 {usuario}: {len(df):,} tweets")
            total_tweets += len(df)
            
            # Almacenar
            dfs.append(df)
            usuarios.append(usuario)
        
        # Concatenar todos los DataFrames
        data = pd.concat(dfs, ignore_index=True)
        
        # Información de consolidación
        consolidation_info = {
            'total_usuarios': len(usuarios),
            'total_tweets': total_tweets,
            'shape': data.shape,
            'usuarios': usuarios,
            'archivos_procesados': len(csv_files)
        }
        
        print(f"\n✅ Datos consolidados exitosamente:")
        print(f"   • Total de usuarios: {len(usuarios)}")
        print(f"   • Total de tweets: {total_tweets:,}")
        print(f"   • Dimensiones finales: {data.shape}")
        print(f"   • Usuarios disponibles: {', '.join(usuarios)}")
        
        return data, consolidation_info
    
    def select_scope(self, data: pd.DataFrame, usuario_objetivo: str = 'interbank') -> Tuple[pd.DataFrame, str]:
        """
        Selecciona el scope de análisis (usuario específico o todos).
        
        Args:
            data (pd.DataFrame): DataFrame consolidado
            usuario_objetivo (str): Usuario específico o 'todos'
            
        Returns:
            Tuple[pd.DataFrame, str]: Datos filtrados y mensaje de scope
        """
        usuarios_disponibles = data['usuario'].unique()
        
        print("👥 Usuarios disponibles para análisis:")
        for i, usuario in enumerate(usuarios_disponibles, 1):
            tweets_count = len(data[data['usuario'] == usuario])
            print(f"   {i}. {usuario.capitalize()}: {tweets_count:,} tweets")
        
        print(f"\n📝 Para analizar todos los usuarios, usa: 'todos'")
        
        # Validación y filtrado
        if usuario_objetivo.lower() == 'todos':
            data_filtrada = data.copy()
            scope_msg = "🌍 Análisis de TODOS los usuarios"
        elif usuario_objetivo in usuarios_disponibles:
            data_filtrada = data[data['usuario'] == usuario_objetivo].copy()
            scope_msg = f"🎯 Análisis específico de: {usuario_objetivo.upper()}"
        else:
            available_options = ", ".join(usuarios_disponibles) + ", todos"
            raise ValueError(
                f"❌ Usuario '{usuario_objetivo}' no encontrado.\n"
                f"Opciones disponibles: {available_options}"
            )
        
        # Información del dataset filtrado
        print(f"\n{scope_msg}")
        print(f"📊 Datos seleccionados: {data_filtrada.shape[0]:,} tweets, {data_filtrada.shape[1]} columnas")
        
        # Estadísticas específicas del scope
        self._print_scope_statistics(data_filtrada, usuario_objetivo, usuarios_disponibles)
        
        return data_filtrada, scope_msg
    
    def _print_scope_statistics(self, data_filtrada: pd.DataFrame, usuario_objetivo: str, usuarios_disponibles: List[str]):
        """
        Imprime estadísticas específicas del scope seleccionado.
        
        Args:
            data_filtrada (pd.DataFrame): Datos filtrados
            usuario_objetivo (str): Usuario objetivo
            usuarios_disponibles (List[str]): Lista de usuarios disponibles
        """
        if usuario_objetivo.lower() != 'todos':
            if 'fecha_publicacion' in data_filtrada.columns:
                fecha_inicio = data_filtrada['fecha_publicacion'].min()
                fecha_fin = data_filtrada['fecha_publicacion'].max()
                print(f"📅 Período: {fecha_inicio} - {fecha_fin}")
            
            # Métricas promedio del usuario seleccionado
            metricas_cols = ['respuestas', 'retweets', 'likes', 'guardados', 'vistas']
            metricas_disponibles = [col for col in metricas_cols if col in data_filtrada.columns]
            
            if metricas_disponibles:
                print(f"\n📈 Métricas promedio del usuario {usuario_objetivo.title()}:")
                metricas_promedio = data_filtrada[metricas_disponibles].mean()
                for metrica, valor in metricas_promedio.items():
                    print(f"   • {metrica.title()}: {valor:.1f}")
        else:
            if 'fecha_publicacion' in data_filtrada.columns:
                fecha_min = data_filtrada['fecha_publicacion'].min()
                fecha_max = data_filtrada['fecha_publicacion'].max()
                print(f"📅 Período total del dataset: {fecha_min} - {fecha_max}")
            
            # Métricas por usuario cuando se analizan todos
            print(f"\n📈 Resumen por usuario:")
            for usuario in usuarios_disponibles:
                usuario_data = data_filtrada[data_filtrada['usuario'].str.upper() == usuario.upper()]
                if len(usuario_data) > 0:
                    print(f"   • {usuario.title()}: {len(usuario_data)} tweets")

def load_and_prepare_data(usuario_objetivo: str = 'interbank', 
                         data_folder: str = None) -> Tuple[pd.DataFrame, Dict]:
    """
    Función principal para cargar y preparar datos.
    
    Args:
        usuario_objetivo (str): Usuario específico o 'todos'
        data_folder (str): Carpeta de datos (opcional)
        
    Returns:
        Tuple[pd.DataFrame, Dict]: Datos preparados e información del proceso
    """
    loader = DataLoader(data_folder=data_folder)
    
    # Consolidar datos
    data_consolidada, consolidation_info = loader.consolidate_data()
    
    # Seleccionar scope
    data_filtrada, scope_msg = loader.select_scope(data_consolidada, usuario_objetivo)
    
    # Vista previa
    print(f"\n📋 Vista previa del dataset filtrado:")
    print(data_filtrada.head())
    
    # Información completa del proceso
    process_info = {
        **consolidation_info,
        'scope_message': scope_msg,
        'usuario_objetivo': usuario_objetivo,
        'shape_filtrada': data_filtrada.shape
    }
    
    return data_filtrada, process_info

if __name__ == "__main__":
    # Ejemplo de uso
    data, info = load_and_prepare_data(usuario_objetivo='interbank')
    print(f"\n✅ Proceso de carga completado. Shape final: {data.shape}")
