# =============================================================================
# CARGA Y CONSOLIDACIÓN DE DATOS
# =============================================================================

"""
Módulo para la carga automática y consolidación de datos de Twitter.
Maneja archivos *_clean.csv y *_metricas.csv para múltiples cuentas bancarias.
"""

import os
import glob
import pandas as pd
from typing import Tuple, List, Dict, Optional, Union
from config import PROJECT_CONFIG, CUENTAS_DISPONIBLES

class MultiAccountDataLoader:
    """
    Clase para manejar la carga y consolidación de datos de múltiples cuentas de Twitter.
    Maneja tanto archivos clean como métricas.
    """
    
    def __init__(self, data_folder: str = None, cuentas_objetivo: Union[str, List[str]] = None):
        """
        Inicializa el cargador de datos.
        
        Args:
            data_folder (str): Carpeta donde buscar los datos
            cuentas_objetivo (Union[str, List[str]]): Cuentas específicas o 'todas'
        """
        self.data_folder = data_folder or PROJECT_CONFIG['data_folder']
        self.file_patterns = PROJECT_CONFIG['file_patterns']
        self.cuentas_disponibles = CUENTAS_DISPONIBLES
        
        # Configurar cuentas objetivo
        if cuentas_objetivo is None or cuentas_objetivo == 'todas':
            self.cuentas_objetivo = self.cuentas_disponibles
        elif isinstance(cuentas_objetivo, str):
            self.cuentas_objetivo = [cuentas_objetivo]
        else:
            self.cuentas_objetivo = cuentas_objetivo
            
        # Validar cuentas objetivo
        self._validate_target_accounts()
        
    def _validate_target_accounts(self) -> None:
        """
        Valida que las cuentas objetivo sean válidas.
        """
        invalid_accounts = [cuenta for cuenta in self.cuentas_objetivo 
                          if cuenta not in self.cuentas_disponibles]
        
        if invalid_accounts:
            print(f"⚠️ Cuentas no válidas encontradas: {invalid_accounts}")
            print(f"✅ Cuentas disponibles: {self.cuentas_disponibles}")
            # Filtrar solo las cuentas válidas
            self.cuentas_objetivo = [cuenta for cuenta in self.cuentas_objetivo 
                                   if cuenta in self.cuentas_disponibles]
        
        if not self.cuentas_objetivo:
            raise ValueError("No se encontraron cuentas válidas para procesar")
            
    def find_files_by_type(self, file_type: str) -> Dict[str, str]:
        """
        Busca archivos de un tipo específico (clean o metricas) para las cuentas objetivo.
        
        Args:
            file_type (str): Tipo de archivo ('clean' o 'metricas')
            
        Returns:
            Dict[str, str]: Diccionario con cuenta -> ruta_archivo
        """
        if file_type not in self.file_patterns:
            raise ValueError(f"Tipo de archivo no válido: {file_type}")
            
        pattern = self.file_patterns[file_type]
        search_pattern = os.path.join(self.data_folder, pattern)
        all_files = glob.glob(search_pattern)
        
        # Filtrar archivos para las cuentas objetivo
        account_files = {}
        for file_path in all_files:
            filename = os.path.basename(file_path)
            # Extraer nombre de cuenta del archivo
            for cuenta in self.cuentas_objetivo:
                if cuenta in filename:
                    account_files[cuenta] = file_path
                    break
        
        return account_files
    
    def load_account_data(self, cuenta: str, include_metricas: bool = True) -> Dict[str, pd.DataFrame]:
        """
        Carga datos de una cuenta específica (clean y opcionalmente métricas).
        
        Args:
            cuenta (str): Nombre de la cuenta
            include_metricas (bool): Si incluir datos de métricas
            
        Returns:
            Dict[str, pd.DataFrame]: Diccionario con 'clean' y opcionalmente 'metricas'
        """
        account_data = {}
        
        # Cargar datos clean
        clean_files = self.find_files_by_type('clean')
        if cuenta in clean_files:
            try:
                clean_df = pd.read_csv(clean_files[cuenta])
                # Asegurar que la columna 'usuario' existe
                if 'usuario' not in clean_df.columns:
                    clean_df['usuario'] = cuenta
                account_data['clean'] = clean_df
                print(f"   ✅ Clean data para {cuenta}: {clean_df.shape}")
            except Exception as e:
                print(f"   ❌ Error cargando clean data para {cuenta}: {e}")
        
        # Cargar datos de métricas si se solicita
        if include_metricas:
            metricas_files = self.find_files_by_type('metricas')
            if cuenta in metricas_files:
                try:
                    metricas_df = pd.read_csv(metricas_files[cuenta])
                    # Asegurar que la columna 'usuario' existe
                    if 'usuario' not in metricas_df.columns:
                        metricas_df['usuario'] = cuenta
                    account_data['metricas'] = metricas_df
                    print(f"   ✅ Métricas data para {cuenta}: {metricas_df.shape}")
                except Exception as e:
                    print(f"   ❌ Error cargando métricas para {cuenta}: {e}")
        
        return account_data
    
    def load_individual_account_data(self, cuenta: str) -> Dict[str, pd.DataFrame]:
        """
        Carga datos individuales de una cuenta específica.
        
        Args:
            cuenta (str): Nombre de la cuenta
            
        Returns:
            Dict[str, pd.DataFrame]: Datos de la cuenta
        """
        return self.load_account_data(cuenta, include_metricas=True)
    
    def consolidate_all_accounts(self, include_metricas: bool = True, mode: str = 'consolidado') -> Tuple[Dict, Dict]:
        """
        Consolida datos de todas las cuentas objetivo.
        
        Args:
            include_metricas (bool): Si incluir datos de métricas
            mode (str): Modo de consolidación ('consolidado', 'individual', 'comparativo')
            
        Returns:
            Tuple[Dict, Dict]: Datos consolidados e información del proceso
        """
        print(f"🔄 Consolidando datos para {len(self.cuentas_objetivo)} cuentas...")
        print(f"   • Modo: {mode}")
        print(f"   • Incluir métricas: {include_metricas}")
        
        all_data = {}
        consolidation_info = {
            'cuentas_procesadas': [],
            'cuentas_exitosas': [],
            'cuentas_fallidas': [],
            'mode': mode,
            'include_metricas': include_metricas
        }
        
        # Cargar datos para cada cuenta
        for cuenta in self.cuentas_objetivo:
            print(f"\n📂 Procesando cuenta: {cuenta}")
            consolidation_info['cuentas_procesadas'].append(cuenta)
            
            account_data = self.load_account_data(cuenta, include_metricas)
            
            if account_data:
                all_data[cuenta] = account_data
                consolidation_info['cuentas_exitosas'].append(cuenta)
            else:
                consolidation_info['cuentas_fallidas'].append(cuenta)
                print(f"   ⚠️ No se encontraron datos para {cuenta}")
        
        # Consolidar según el modo
        consolidated_data = self._consolidate_by_mode(all_data, mode)
        
        # Actualizar información
        consolidation_info['total_cuentas'] = len(self.cuentas_objetivo)
        consolidation_info['exitosas'] = len(consolidation_info['cuentas_exitosas'])
        consolidation_info['fallidas'] = len(consolidation_info['cuentas_fallidas'])
        
        print(f"\n✅ Consolidación completada:")
        print(f"   • Cuentas exitosas: {consolidation_info['exitosas']}")
        print(f"   • Cuentas fallidas: {consolidation_info['fallidas']}")
        
        return consolidated_data, consolidation_info
    
    def load_consolidated_data(self, target_accounts: List[str] = None, mode: str = 'consolidado') -> Dict[str, pd.DataFrame]:
        """
        Carga datos consolidados para cuentas específicas.
        
        Args:
            target_accounts (List[str]): Cuentas objetivo (opcional)
            mode (str): Modo de consolidación
            
        Returns:
            Dict[str, pd.DataFrame]: Datos consolidados
        """
        # Actualizar cuentas objetivo si se proporcionan
        if target_accounts:
            original_accounts = self.cuentas_objetivo
            self.cuentas_objetivo = target_accounts
            self._validate_target_accounts()
        
        try:
            # Consolidar datos
            consolidated_data, _ = self.consolidate_all_accounts(
                include_metricas=True,
                mode=mode
            )
            
            return consolidated_data
            
        finally:
            # Restaurar cuentas originales si se modificaron
            if target_accounts:
                self.cuentas_objetivo = original_accounts
    
    def _consolidate_by_mode(self, all_data: Dict, mode: str) -> Dict:
        """
        Aplica el modo de consolidación especificado.
        
        Args:
            all_data (Dict): Datos de todas las cuentas
            mode (str): Modo de consolidación
            
        Returns:
            Dict[str, pd.DataFrame]: Datos consolidados según el modo
        """
        if mode == 'individual':
            # Mantener datos separados por cuenta
            return all_data
            
        elif mode == 'comparativo':
            # Crear estructura para comparación entre cuentas
            comparative_data = {}
            
            # Consolidar clean data
            clean_dfs = []
            for cuenta, data in all_data.items():
                if 'clean' in data:
                    clean_dfs.append(data['clean'])
            
            if clean_dfs:
                comparative_data['clean_all'] = pd.concat(clean_dfs, ignore_index=True)
                
            # Consolidar métricas data
            metricas_dfs = []
            for cuenta, data in all_data.items():
                if 'metricas' in data:
                    metricas_dfs.append(data['metricas'])
                    
            if metricas_dfs:
                comparative_data['metricas_all'] = pd.concat(metricas_dfs, ignore_index=True)
                
            # Mantener también datos individuales para comparación
            comparative_data['individual'] = all_data
            
            return comparative_data
            
        else:  # mode == 'consolidado'
            # Consolidar todo en DataFrames únicos
            consolidated = {}
            
            # Consolidar clean data
            clean_dfs = []
            for cuenta, data in all_data.items():
                if 'clean' in data:
                    clean_dfs.append(data['clean'])
            
            if clean_dfs:
                consolidated['data_clean'] = pd.concat(clean_dfs, ignore_index=True)
                
            # Consolidar métricas data
            metricas_dfs = []
            for cuenta, data in all_data.items():
                if 'metricas' in data:
                    metricas_dfs.append(data['metricas'])
                    
            if metricas_dfs:
                consolidated['data_metricas'] = pd.concat(metricas_dfs, ignore_index=True)
            
            return consolidated
    
    def get_account_summary(self, consolidated_data: Dict) -> pd.DataFrame:
        """
        Genera resumen estadístico por cuenta.
        
        Args:
            consolidated_data (Dict): Datos consolidados
            
        Returns:
            pd.DataFrame: Resumen por cuenta
        """
        summary_data = []
        
        # Si es modo individual o comparativo con datos individuales
        if 'individual' in consolidated_data:
            individual_data = consolidated_data['individual']
        elif isinstance(list(consolidated_data.values())[0], dict):
            individual_data = consolidated_data
        else:
            # Para modo consolidado, extraer estadísticas del DataFrame unificado
            return self._create_summary_from_consolidated(consolidated_data)
        
        for cuenta, data in individual_data.items():
            cuenta_summary = {'cuenta': cuenta}
            
            if 'clean' in data:
                clean_df = data['clean']
                cuenta_summary.update({
                    'tweets_clean': len(clean_df),
                    'avg_likes': clean_df['likes'].mean() if 'likes' in clean_df.columns else 0,
                    'avg_retweets': clean_df['retweets'].mean() if 'retweets' in clean_df.columns else 0,
                    'avg_respuestas': clean_df['respuestas'].mean() if 'respuestas' in clean_df.columns else 0,
                })
                
            if 'metricas' in data:
                metricas_df = data['metricas']
                cuenta_summary.update({
                    'registros_metricas': len(metricas_df),
                })
                
            summary_data.append(cuenta_summary)
        
        return pd.DataFrame(summary_data)
    
    def _create_summary_from_consolidated(self, consolidated_data: Dict) -> pd.DataFrame:
        """
        Crea resumen desde datos consolidados.
        
        Args:
            consolidated_data (Dict): Datos consolidados
            
        Returns:
            pd.DataFrame: Resumen por cuenta
        """
        summary_data = []
        
        if 'data_clean' in consolidated_data:
            clean_df = consolidated_data['data_clean']
            summary_by_account = clean_df.groupby('usuario').agg({
                'likes': ['count', 'mean'],
                'retweets': 'mean',
                'respuestas': 'mean'
            }).round(2)
            
            summary_by_account.columns = ['tweets_clean', 'avg_likes', 'avg_retweets', 'avg_respuestas']
            summary_by_account = summary_by_account.reset_index()
            summary_by_account.rename(columns={'usuario': 'cuenta'}, inplace=True)
            
            return summary_by_account
        
        return pd.DataFrame()

def load_multi_account_data(cuentas_objetivo: Union[str, List[str]] = 'todas',
                          include_metricas: bool = True,
                          mode: str = 'consolidado',
                          data_folder: str = None) -> Tuple[Dict[str, pd.DataFrame], Dict, pd.DataFrame]:
    """
    Función principal para cargar datos de múltiples cuentas.
    
    Args:
        cuentas_objetivo (Union[str, List[str]]): Cuentas específicas o 'todas'
        include_metricas (bool): Si incluir datos de métricas
        mode (str): Modo de consolidación ('consolidado', 'individual', 'comparativo')
        data_folder (str): Carpeta de datos (opcional)
        
    Returns:
        Tuple: Datos consolidados, información del proceso, resumen por cuenta
    """
    loader = MultiAccountDataLoader(
        data_folder=data_folder,
        cuentas_objetivo=cuentas_objetivo
    )
    
    # Consolidar datos
    consolidated_data, consolidation_info = loader.consolidate_all_accounts(
        include_metricas=include_metricas,
        mode=mode
    )
    
    # Generar resumen
    summary = loader.get_account_summary(consolidated_data)
    
    # Vista previa
    print(f"\n📋 RESUMEN POR CUENTA:")
    if not summary.empty:
        print(summary.to_string(index=False))
    
    return consolidated_data, consolidation_info, summary

# Mantener compatibilidad con la función anterior
def load_and_prepare_data(usuario_objetivo: str = 'todas', 
                         data_folder: str = None) -> Tuple[pd.DataFrame, Dict]:
    """
    Función de compatibilidad con la interfaz anterior.
    
    Args:
        usuario_objetivo (str): Usuario específico o 'todas'
        data_folder (str): Carpeta de datos
        
    Returns:
        Tuple[pd.DataFrame, Dict]: Datos y información
    """
    # Convertir a lista si es una cuenta específica
    if usuario_objetivo == 'todas':
        cuentas = 'todas'
    else:
        cuentas = [usuario_objetivo]
    
    consolidated_data, info, summary = load_multi_account_data(
        cuentas_objetivo=cuentas,
        include_metricas=False,  # Solo clean para compatibilidad
        mode='consolidado',
        data_folder=data_folder
    )
    
    # Retornar solo datos clean para compatibilidad
    data = consolidated_data.get('data_clean', pd.DataFrame())
    
    return data, info

if __name__ == "__main__":
    # Ejemplo de uso con múltiples cuentas
    print("🧪 EJEMPLO DE USO - CARGA MULTI-CUENTA")
    print("="*50)
    
    # Ejemplo 1: Cargar todas las cuentas
    print("\n1. Cargando todas las cuentas...")
    data_all, info_all, summary_all = load_multi_account_data(
        cuentas_objetivo='todas',
        include_metricas=True,
        mode='consolidado'
    )
    
    # Ejemplo 2: Cargar cuentas específicas
    print("\n2. Cargando cuentas específicas...")
    cuentas_bancarias = ['Interbank', 'BanBif', 'bbva_peru']
    data_banks, info_banks, summary_banks = load_multi_account_data(
        cuentas_objetivo=cuentas_bancarias,
        include_metricas=True,
        mode='comparativo'
    )
    
    # Ejemplo 3: Compatibilidad con función anterior
    print("\n3. Usando función de compatibilidad...")
    data_compat, info_compat = load_and_prepare_data(usuario_objetivo='Interbank')
    
    print(f"\n✅ Ejemplos completados exitosamente")
