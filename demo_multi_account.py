#!/usr/bin/env python3
# =============================================================================
# EJEMPLO DE USO DEL SISTEMA MULTI-CUENTA
# =============================================================================

"""
Script de ejemplo que demuestra cómo usar el nuevo sistema multi-cuenta.
Ejecutar desde el directorio raíz del proyecto.
"""

import os
import sys

# Añadir el directorio scripts al path
scripts_dir = os.path.join(os.path.dirname(__file__), 'scripts')
sys.path.insert(0, scripts_dir)

def ejemplo_basico():
    """Ejemplo básico de uso multi-cuenta."""
    print("🚀 EJEMPLO BÁSICO - SISTEMA MULTI-CUENTA")
    print("="*60)
    
    from scripts.data_loader import MultiAccountDataLoader
    from scripts.config import CUENTAS_DISPONIBLES
    
    # 1. Listar cuentas disponibles
    print(f"📋 Cuentas disponibles: {CUENTAS_DISPONIBLES}")
    
    # 2. Cargar datos de múltiples cuentas
    print("\n📂 Cargando datos multi-cuenta...")
    
    # Usar las primeras 3 cuentas como ejemplo
    test_accounts = CUENTAS_DISPONIBLES[:3]
    print(f"🎯 Cuentas seleccionadas: {test_accounts}")
    
    loader = MultiAccountDataLoader(cuentas_objetivo=test_accounts)
    
    # 3. Verificar archivos disponibles
    clean_files = loader.find_files_by_type('clean')
    metricas_files = loader.find_files_by_type('metricas')
    
    print(f"\n📊 ARCHIVOS ENCONTRADOS:")
    print(f"   • Clean: {len(clean_files)}")
    print(f"   • Métricas: {len(metricas_files)}")
    
    for cuenta in test_accounts:
        clean_ok = "✅" if cuenta in clean_files else "❌"
        metricas_ok = "✅" if cuenta in metricas_files else "❌"
        print(f"   • {cuenta}: Clean {clean_ok} Métricas {metricas_ok}")
    
    # 4. Cargar datos consolidados
    print(f"\n🔄 Cargando datos consolidados...")
    consolidated_data = loader.load_consolidated_data(
        target_accounts=test_accounts,
        mode='consolidado'
    )
    
    if consolidated_data:
        print(f"✅ Datos consolidados cargados exitosamente:")
        for data_type, df in consolidated_data.items():
            print(f"   • {data_type}: {df.shape}")
            
            # Mostrar información básica
            if 'usuario' in df.columns:
                cuentas_en_datos = df['usuario'].unique()
                print(f"     - Cuentas: {list(cuentas_en_datos)}")
                for cuenta in cuentas_en_datos:
                    count = len(df[df['usuario'] == cuenta])
                    print(f"     - {cuenta}: {count:,} registros")
    
    return consolidated_data

def ejemplo_preprocessing():
    """Ejemplo de preprocessing multi-cuenta."""
    print("\n🔧 EJEMPLO PREPROCESSING MULTI-CUENTA")
    print("="*60)
    
    from scripts.data_loader import MultiAccountDataLoader
    from scripts.preprocessing import MultiAccountDataPreprocessor
    from scripts.config import CUENTAS_DISPONIBLES
    
    # Cargar datos
    test_accounts = CUENTAS_DISPONIBLES[:2]  # Usar 2 cuentas para ejemplo
    print(f"📋 Preprocessing para: {test_accounts}")
    
    loader = MultiAccountDataLoader(cuentas_objetivo=test_accounts)
    consolidated_data = loader.load_consolidated_data(
        target_accounts=test_accounts,
        mode='consolidado'
    )
    
    if not consolidated_data:
        print("❌ No hay datos para preprocesar")
        return None
    
    # Preprocesar datos
    preprocessor = MultiAccountDataPreprocessor()
    results = preprocessor.preprocess_multi_account_data(
        consolidated_data,
        target_accounts=test_accounts
    )
    
    print(f"\n📊 RESULTADOS DEL PREPROCESSING:")
    for data_type, result in results.items():
        if 'error' not in result:
            print(f"✅ {data_type}:")
            print(f"   • X_scaled shape: {result['X_scaled'].shape}")
            print(f"   • Features: {len(result['features'])}")
            print(f"   • Features disponibles: {result['features'][:5]}...")  # Primeras 5
        else:
            print(f"❌ {data_type}: {result['error']}")
    
    return results

def ejemplo_pipeline_basico():
    """Ejemplo básico del pipeline multi-cuenta."""
    print("\n🚀 EJEMPLO PIPELINE MULTI-CUENTA")
    print("="*60)
    
    from scripts.main_pipeline import run_multi_account_analysis
    from scripts.config import CUENTAS_DISPONIBLES
    
    # Análisis consolidado de pocas cuentas para demo
    test_accounts = CUENTAS_DISPONIBLES[:2]
    print(f"📋 Ejecutando análisis para: {test_accounts}")
    
    try:
        # Ejecutar análisis consolidado
        print(f"\n🔄 Iniciando análisis consolidado...")
        
        results = run_multi_account_analysis(
            target_accounts=test_accounts,
            target_variable='likes',
            analysis_mode='consolidado'
        )
        
        if results:
            print(f"\n✅ ANÁLISIS COMPLETADO EXITOSAMENTE!")
            
            # Mostrar resumen de resultados
            if 'final_summary' in results:
                summary = results['final_summary']
                print(f"📊 RESUMEN:")
                print(f"   • Modo: {summary['pipeline_info']['analysis_mode']}")
                print(f"   • Cuentas: {len(summary['pipeline_info']['target_accounts'])}")
                
                if 'data_summary' in summary:
                    data_sum = summary['data_summary']
                    print(f"   • Registros totales: {data_sum['total_records']:,}")
                
                if summary['recommendations']:
                    print(f"\n💡 RECOMENDACIONES:")
                    for rec in summary['recommendations']:
                        print(f"   • {rec}")
        
        return results
        
    except Exception as e:
        print(f"❌ Error en el pipeline: {e}")
        return None

def mostrar_funcionalidades():
    """Muestra las nuevas funcionalidades del sistema multi-cuenta."""
    print("\n🎯 NUEVAS FUNCIONALIDADES MULTI-CUENTA")
    print("="*60)
    
    print("""
📦 CARACTERÍSTICAS PRINCIPALES:

1. 🏦 SOPORTE MULTI-CUENTA:
   • 8 cuentas bancarias soportadas
   • Análisis individual, comparativo o consolidado
   • Manejo automático de múltiples archivos

2. 📊 DOBLE TIPO DE DATOS:
   • Archivos *_clean.csv (datos de tweets limpios)
   • Archivos *_metricas.csv (métricas agregadas)
   • Combinación inteligente de ambos tipos

3. 🔧 PREPROCESSING AVANZADO:
   • Feature engineering automático
   • Adaptación por tipo de datos
   • Escalado y normalización

4. 🚀 PIPELINE FLEXIBLE:
   • Modo individual: análisis por cuenta
   • Modo comparativo: comparación entre cuentas  
   • Modo consolidado: análisis unificado

5. 🔄 COMPATIBILIDAD:
   • Funciones legacy siguen funcionando
   • Transición suave desde versión anterior
   • APIs retrocompatibles

📋 CUENTAS SOPORTADAS:
""")
    
    from scripts.config import CUENTAS_DISPONIBLES
    for i, cuenta in enumerate(CUENTAS_DISPONIBLES, 1):
        print(f"   {i}. {cuenta}")
    
    print(f"""
🎯 MODOS DE ANÁLISIS:

• INDIVIDUAL: Analiza cada cuenta por separado
  run_multi_account_analysis(target_accounts=['Interbank'], analysis_mode='individual')

• COMPARATIVO: Compara múltiples cuentas
  run_multi_account_analysis(target_accounts=['Interbank', 'BanBif'], analysis_mode='comparativo')

• CONSOLIDADO: Análisis unificado de todas las cuentas
  run_multi_account_analysis(target_accounts=None, analysis_mode='consolidado')

🔧 EJEMPLOS DE USO:
   Ver funciones en este script para ejemplos completos.
""")

if __name__ == "__main__":
    # Verificar que estamos en el directorio correcto
    if not os.path.exists('data') or not os.path.exists('scripts'):
        print("❌ Error: Ejecutar desde el directorio raíz del proyecto")
        print("📁 Debe contener las carpetas 'data/' y 'scripts/'")
        sys.exit(1)
    
    print("🎯 DEMOSTRACIÓN DEL SISTEMA MULTI-CUENTA")
    print("="*70)
    
    # Mostrar funcionalidades
    mostrar_funcionalidades()
    
    # Ejecutar ejemplos
    try:
        # Ejemplo 1: Carga básica
        consolidated_data = ejemplo_basico()
        
        # Ejemplo 2: Preprocessing (solo si hay datos)
        if consolidated_data:
            preprocessing_results = ejemplo_preprocessing()
        
        # Ejemplo 3: Pipeline completo (comentado para demo rápida)
        # pipeline_results = ejemplo_pipeline_basico()
        
        print(f"\n🎉 DEMOSTRACIÓN COMPLETADA")
        print(f"✅ Sistema multi-cuenta operativo y listo para usar")
        print(f"📚 Consulta la documentación en scripts/README.md para más detalles")
        
    except Exception as e:
        print(f"\n❌ Error durante la demostración: {e}")
        print(f"🔧 Verifica que todas las dependencias estén instaladas")
        sys.exit(1)
