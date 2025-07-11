#!/usr/bin/env python3
# =============================================================================
# SCRIPT PARA EJECUTAR MODELOS DE REGRESIÓN INDIVIDUALES
# =============================================================================

"""
Script principal para ejecutar modelos de regresión por cuenta individual.
Carga datos desde la base de datos DuckDB y entrena modelos de predicción
del número de seguidores.
"""

import sys
import argparse
import json
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any

# Añadir directorio padre al path para imports
sys.path.append(str(Path(__file__).parent.parent))

# Imports locales - usando imports relativos
from .config import (get_available_accounts, verify_database, 
                     print_project_info, TARGET_VARIABLE, OUTPUT_CONFIG)
from .data_loader import AccountDataLoader
from .preprocessing import AccountPreprocessor
from .regression_models import train_account_regression_model

def parse_arguments():
    """
    Parsea argumentos de línea de comandos.
    
    Returns:
        argparse.Namespace: Argumentos parseados
    """
    parser = argparse.ArgumentParser(
        description="Entrena modelos de regresión para predicción de seguidores por cuenta",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos de uso:
  python run_individual.py --account BCPComunica
  python run_individual.py --list-accounts
  python run_individual.py --account bbva_peru --target seguidores --no-save
        """
    )
    
    parser.add_argument(
        '--account', '-a',
        type=str,
        help='Nombre de la cuenta a analizar'
    )
    
    parser.add_argument(
        '--list-accounts', '-l',
        action='store_true',
        help='Lista todas las cuentas disponibles'
    )
    
    parser.add_argument(
        '--target', '-t',
        type=str,
        default=TARGET_VARIABLE,
        help=f'Variable objetivo a predecir (default: {TARGET_VARIABLE})'
    )
    
    parser.add_argument(
        '--no-save',
        action='store_true',
        help='No guardar el modelo entrenado'
    )
    
    parser.add_argument(
        '--output-dir', '-o',
        type=str,
        help='Directorio de salida para resultados'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Salida detallada'
    )
    
    return parser.parse_args()

def list_available_accounts():
    """
    Lista todas las cuentas disponibles en la base de datos.
    """
    print("📋 Verificando cuentas disponibles...")
    
    if not verify_database():
        print("❌ Error: Base de datos no disponible")
        return False
    
    accounts = get_available_accounts()
    
    if not accounts:
        print("❌ No se encontraron cuentas en la base de datos")
        return False
    
    print(f"\n📊 Cuentas disponibles ({len(accounts)}):")
    for i, account in enumerate(accounts, 1):
        print(f"   {i:2d}. {account}")
    
    print(f"\n💡 Uso: python run_individual.py --account <nombre_cuenta>")
    return True

def validate_account(account_name: str) -> bool:
    """
    Valida que una cuenta existe en la base de datos.
    
    Args:
        account_name (str): Nombre de la cuenta
        
    Returns:
        bool: True si la cuenta existe
    """
    available_accounts = get_available_accounts()
    
    if account_name not in available_accounts:
        print(f"❌ Error: Cuenta '{account_name}' no encontrada")
        print(f"📋 Cuentas disponibles: {', '.join(available_accounts)}")
        return False
    
    return True

def load_account_data(account_name: str, verbose: bool = False) -> Optional[Any]:
    """
    Carga datos de una cuenta específica.
    
    Args:
        account_name (str): Nombre de la cuenta
        verbose (bool): Salida detallada
        
    Returns:
        pd.DataFrame o None: Datos de la cuenta
    """
    try:
        print(f"📥 Cargando datos para: {account_name}")
        
        # Crear loader de datos
        loader = AccountDataLoader(account_name)
        
        # Cargar datos
        data = loader.load_account_data()
        
        if data is None or len(data) == 0:
            print(f"❌ No se encontraron datos para la cuenta: {account_name}")
            return None
        
        print(f"✅ Datos cargados: {len(data)} registros")
        
        if verbose:
            print(f"📊 Columnas disponibles: {list(data.columns)}")
            print(f"📅 Rango de fechas: {data['fecha_publicacion'].min()} - {data['fecha_publicacion'].max()}")
        
        return data
        
    except Exception as e:
        print(f"❌ Error cargando datos para {account_name}: {e}")
        return None

def preprocess_account_data(account_name: str, data: Any, target_variable: str, verbose: bool = False) -> Optional[Any]:
    """
    Preprocesa datos de una cuenta.
    
    Args:
        account_name (str): Nombre de la cuenta
        data: DataFrame con datos
        target_variable (str): Variable objetivo
        verbose (bool): Salida detallada
        
    Returns:
        DataFrame o None: Datos preprocesados
    """
    try:
        print(f"🔧 Preprocesando datos para: {account_name}")
        
        # Crear preprocesador
        preprocessor = AccountPreprocessor(account_name, target_variable)
        
        # Preprocesar datos
        processed_data = preprocessor.preprocess_account_data(data)
        
        if processed_data is None or len(processed_data) == 0:
            print(f"❌ Error en preprocesamiento para: {account_name}")
            return None
        
        print(f"✅ Datos preprocesados: {len(processed_data)} registros")
        
        if verbose:
            print(f"📊 Features finales: {list(processed_data.columns)}")
            if target_variable in processed_data.columns:
                target_stats = processed_data[target_variable].describe()
                print(f"📈 Estadísticas de {target_variable}:")
                print(f"   - Media: {target_stats['mean']:.2f}")
                print(f"   - Mediana: {target_stats['50%']:.2f}")
                print(f"   - Min: {target_stats['min']:.2f}")
                print(f"   - Max: {target_stats['max']:.2f}")
        
        return processed_data
        
    except Exception as e:
        print(f"❌ Error en preprocesamiento para {account_name}: {e}")
        return None

def save_results_report(account_name: str, report: Dict, output_dir: str = None) -> str:
    """
    Guarda reporte de resultados en archivo JSON.
    
    Args:
        account_name (str): Nombre de la cuenta
        report (Dict): Reporte de resultados
        output_dir (str): Directorio de salida
        
    Returns:
        str: Ruta del archivo guardado
    """
    # Determinar directorio de salida
    if output_dir is None:
        output_dir = OUTPUT_CONFIG['reports_dir']
    
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Nombre del archivo
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{account_name}_regression_report_{timestamp}.json"
    file_path = output_path / filename
    
    # Guardar reporte
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False, default=str)
    
    print(f"📄 Reporte guardado: {file_path}")
    return str(file_path)

def run_individual_regression(account_name: str, target_variable: str = None, 
                            save_model: bool = True, output_dir: str = None,
                            verbose: bool = False) -> bool:
    """
    Ejecuta análisis de regresión completo para una cuenta.
    
    Args:
        account_name (str): Nombre de la cuenta
        target_variable (str): Variable objetivo
        save_model (bool): Si guardar el modelo
        output_dir (str): Directorio de salida
        verbose (bool): Salida detallada
        
    Returns:
        bool: True si fue exitoso
    """
    print(f"\n🚀 Iniciando análisis de regresión individual")
    print(f"📱 Cuenta: {account_name}")
    print(f"🎯 Variable objetivo: {target_variable or TARGET_VARIABLE}")
    print("="*80)
    
    try:
        # 1. Validar cuenta
        if not validate_account(account_name):
            return False
        
        # 2. Cargar datos
        data = load_account_data(account_name, verbose)
        if data is None:
            return False
        
        # 3. Preprocesar datos
        processed_data = preprocess_account_data(account_name, data, target_variable or TARGET_VARIABLE, verbose)
        if processed_data is None:
            return False
        
        # 4. Entrenar modelos
        print(f"\n🤖 Entrenando modelos de regresión...")
        model, report = train_account_regression_model(
            account_name, 
            processed_data, 
            target_variable, 
            save_model
        )
        
        if not report:
            print(f"❌ Error: No se generó reporte para {account_name}")
            return False
        
        # 5. Guardar reporte
        report_path = save_results_report(account_name, report, output_dir)
        
        # 6. Resumen final
        print(f"\n" + "="*80)
        print(f"✅ ANÁLISIS COMPLETADO EXITOSAMENTE")
        print(f"📱 Cuenta: {account_name}")
        print(f"🎯 Variable objetivo: {target_variable or TARGET_VARIABLE}")
        
        if 'best_model' in report and report['best_model']:
            best = report['best_model']
            print(f"🏆 Mejor modelo: {best['model_name']}")
            print(f"📊 R²: {best['r2_score']:.3f}")
            print(f"📉 RMSE: {best['rmse']:.2f}")
        
        print(f"📄 Reporte: {report_path}")
        print("="*80)
        
        return True
        
    except Exception as e:
        print(f"❌ Error en análisis de {account_name}: {e}")
        if verbose:
            import traceback
            traceback.print_exc()
        return False

def main():
    """
    Función principal.
    """
    # Mostrar información del proyecto
    print_project_info()
    
    # Parsear argumentos
    args = parse_arguments()
    
    # Verificar base de datos
    if not verify_database():
        print("❌ Error: Base de datos no disponible")
        sys.exit(1)
    
    # Listar cuentas si se solicita
    if args.list_accounts:
        if list_available_accounts():
            sys.exit(0)
        else:
            sys.exit(1)
    
    # Validar que se proporcionó una cuenta
    if not args.account:
        print("❌ Error: Debe especificar una cuenta con --account")
        print("💡 Use --list-accounts para ver cuentas disponibles")
        sys.exit(1)
    
    # Ejecutar análisis
    success = run_individual_regression(
        account_name=args.account,
        target_variable=args.target,
        save_model=not args.no_save,
        output_dir=args.output_dir,
        verbose=args.verbose
    )
    
    if success:
        print(f"\n🎉 Análisis completado exitosamente para: {args.account}")
        sys.exit(0)
    else:
        print(f"\n💥 Error en el análisis de: {args.account}")
        sys.exit(1)

if __name__ == "__main__":
    main()
