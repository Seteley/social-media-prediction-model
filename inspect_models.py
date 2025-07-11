#!/usr/bin/env python3
"""
Script para inspeccionar los modelos de regresión entrenados
y ver qué features están usando realmente.
"""

import joblib
import json
from pathlib import Path

def inspect_models():
    """Inspecciona los modelos entrenados y sus features"""
    print("🔍 INSPECCIÓN DE MODELOS DE REGRESIÓN")
    print("="*50)
    
    models_dir = Path('models')
    if not models_dir.exists():
        print("❌ No existe el directorio 'models'")
        return
    
    users_found = 0
    
    for user_dir in models_dir.iterdir():
        if user_dir.is_dir():
            model_path = user_dir / 'regresion.pkl'
            if model_path.exists():
                users_found += 1
                print(f"\n📁 Usuario: {user_dir.name}")
                print("-" * 30)
                
                try:
                    # Cargar modelo
                    model_data = joblib.load(model_path)
                    
                    # Información básica
                    target = model_data.get('target_variable', 'N/A')
                    features = model_data.get('feature_names', [])
                    model_type = type(model_data.get('model', None)).__name__
                    account = model_data.get('account_name', 'N/A')
                    
                    print(f"🎯 Variable objetivo: {target}")
                    print(f"🔧 Features utilizadas: {features}")
                    print(f"🤖 Tipo de modelo: {model_type}")
                    print(f"📊 Cuenta: {account}")
                    
                    # Verificar si las features incluyen temporales
                    temporal_features = ['dia_semana', 'hora', 'mes']
                    has_temporal = any(f in features for f in temporal_features)
                    
                    if has_temporal:
                        print("✅ Incluye features temporales:")
                        for tf in temporal_features:
                            if tf in features:
                                print(f"   - {tf} ✅")
                            else:
                                print(f"   - {tf} ❌")
                    else:
                        print("❌ NO incluye features temporales")
                    
                    # Información adicional si está disponible
                    if 'timestamp' in model_data:
                        print(f"⏰ Entrenado: {model_data['timestamp']}")
                    
                    if 'results' in model_data:
                        results = model_data['results']
                        if results:
                            best_score = max(results, key=lambda x: x.get('R²', 0))
                            print(f"📈 Mejor R²: {best_score.get('R²', 0):.4f}")
                    
                except Exception as e:
                    print(f"❌ Error cargando modelo: {e}")
    
    if users_found == 0:
        print("❌ No se encontraron modelos entrenados")
    else:
        print(f"\n✅ Total usuarios con modelos: {users_found}")

def check_metrics():
    """Revisa los archivos de métricas para más información"""
    print("\n\n🔍 INSPECCIÓN DE MÉTRICAS")
    print("="*50)
    
    metrics_dir = Path('metricas')
    if not metrics_dir.exists():
        print("❌ No existe el directorio 'metricas'")
        return
    
    for metrics_file in metrics_dir.glob('*.json'):
        print(f"\n📄 Archivo: {metrics_file.name}")
        print("-" * 30)
        
        try:
            with open(metrics_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            account = data.get('account_name', 'N/A')
            target = data.get('target_variable', 'N/A')
            features = data.get('features_used', [])
            best_model = data.get('best_model', {})
            
            print(f"📊 Cuenta: {account}")
            print(f"🎯 Variable objetivo: {target}")
            print(f"🔧 Features utilizadas: {features}")
            
            if best_model:
                print(f"🏆 Mejor modelo: {best_model.get('model_name', 'N/A')}")
                print(f"📈 R²: {best_model.get('r2_score', 0):.4f}")
                print(f"📉 RMSE: {best_model.get('rmse', 0):.2f}")
            
        except Exception as e:
            print(f"❌ Error leyendo métricas: {e}")

def analyze_temporal_usage():
    """Analiza específicamente el uso de features temporales"""
    print("\n\n🔍 ANÁLISIS DE FEATURES TEMPORALES")
    print("="*50)
    
    temporal_features = ['dia_semana', 'hora', 'mes']
    models_with_temporal = 0
    total_models = 0
    
    models_dir = Path('models')
    if models_dir.exists():
        for user_dir in models_dir.iterdir():
            if user_dir.is_dir():
                model_path = user_dir / 'regresion.pkl'
                if model_path.exists():
                    total_models += 1
                    try:
                        model_data = joblib.load(model_path)
                        features = model_data.get('feature_names', [])
                        
                        has_temporal = any(f in features for f in temporal_features)
                        if has_temporal:
                            models_with_temporal += 1
                            print(f"✅ {user_dir.name}: Usa features temporales")
                        else:
                            print(f"❌ {user_dir.name}: NO usa features temporales")
                            
                    except Exception as e:
                        print(f"❌ {user_dir.name}: Error - {e}")
    
    print(f"\n📊 Resumen:")
    print(f"   Total modelos: {total_models}")
    print(f"   Con features temporales: {models_with_temporal}")
    print(f"   Sin features temporales: {total_models - models_with_temporal}")
    
    if total_models > 0:
        percentage = (models_with_temporal / total_models) * 100
        print(f"   Porcentaje con temporales: {percentage:.1f}%")

if __name__ == "__main__":
    inspect_models()
    check_metrics()
    analyze_temporal_usage()
    
    print("\n" + "="*50)
    print("🎯 CONCLUSIÓN:")
    print("Si los modelos usan dia_semana, hora, mes como features,")
    print("entonces el endpoint está funcionando correctamente al")
    print("extraer estos valores desde el parámetro 'fecha'.")
    print("="*50)
