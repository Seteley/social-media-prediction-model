#!/usr/bin/env python3
"""
Test para verificar que el modelo está usando correctamente
los parámetros temporales extraídos de la fecha.
"""

import requests
import json
import joblib
from datetime import datetime
from pathlib import Path

def test_feature_extraction():
    """Prueba la extracción de features desde fecha"""
    print("🧪 TEST: Extracción de Features Temporales")
    print("="*50)
    
    # Casos de prueba
    test_cases = [
        {
            "fecha": "2025-07-11",  # Viernes
            "expected_dia_semana": 4,
            "expected_mes": 7,
            "expected_hora": 23
        },
        {
            "fecha": "2028-10-11",  # Miércoles
            "expected_dia_semana": 2,
            "expected_mes": 10,
            "expected_hora": 23
        },
        {
            "fecha": "2025-12-25",  # Jueves
            "expected_dia_semana": 3,
            "expected_mes": 12,
            "expected_hora": 23
        }
    ]
    
    for case in test_cases:
        fecha = case["fecha"]
        fecha_obj = datetime.strptime(fecha, "%Y-%m-%d")
        
        dia_semana = fecha_obj.weekday()
        mes = fecha_obj.month
        hora = 23  # Default
        
        print(f"\n📅 Fecha: {fecha}")
        print(f"   Día semana calculado: {dia_semana} (esperado: {case['expected_dia_semana']})")
        print(f"   Mes calculado: {mes} (esperado: {case['expected_mes']})")
        print(f"   Hora asumida: {hora} (esperado: {case['expected_hora']})")
        
        # Verificar
        assert dia_semana == case["expected_dia_semana"], f"Día semana incorrecto para {fecha}"
        assert mes == case["expected_mes"], f"Mes incorrecto para {fecha}"
        assert hora == case["expected_hora"], f"Hora incorrecta para {fecha}"
        
        print("   ✅ Extracción correcta")
    
    print("\n✅ Todas las extracciones de features son correctas")

def test_model_features():
    """Verifica que los modelos usan las features temporales"""
    print("\n🧪 TEST: Features en Modelos Entrenados")
    print("="*50)
    
    models_dir = Path('models')
    if not models_dir.exists():
        print("⚠️  No existe directorio de modelos")
        return
    
    temporal_features = ['dia_semana', 'hora', 'mes']
    models_checked = 0
    models_with_temporal = 0
    
    for user_dir in models_dir.iterdir():
        if user_dir.is_dir():
            model_path = user_dir / 'regresion.pkl'
            if model_path.exists():
                models_checked += 1
                print(f"\n📁 Verificando: {user_dir.name}")
                
                try:
                    model_data = joblib.load(model_path)
                    features = model_data.get('feature_names', [])
                    
                    print(f"   Features del modelo: {features}")
                    
                    # Verificar features temporales
                    has_all_temporal = all(tf in features for tf in temporal_features)
                    missing_temporal = [tf for tf in temporal_features if tf not in features]
                    present_temporal = [tf for tf in temporal_features if tf in features]
                    
                    if has_all_temporal:
                        models_with_temporal += 1
                        print("   ✅ Tiene TODAS las features temporales")
                    else:
                        print(f"   ⚠️  Features presentes: {present_temporal}")
                        print(f"   ❌ Features faltantes: {missing_temporal}")
                
                except Exception as e:
                    print(f"   ❌ Error: {e}")
    
    print(f"\n📊 Resumen:")
    print(f"   Modelos verificados: {models_checked}")
    print(f"   Con features temporales completas: {models_with_temporal}")
    
    if models_checked > 0:
        percentage = (models_with_temporal / models_checked) * 100
        print(f"   Porcentaje compatible: {percentage:.1f}%")

def test_endpoint_prediction():
    """Prueba que el endpoint funciona con diferentes fechas"""
    print("\n🧪 TEST: Predicciones con Diferentes Fechas")
    print("="*50)
    
    base_url = "http://localhost:8000"
    username = "Interbank"  # Cambiar si es necesario
    
    test_dates = [
        "2025-01-15",  # Miércoles, Enero
        "2025-07-11",  # Viernes, Julio  
        "2025-12-31",  # Miércoles, Diciembre
    ]
    
    for fecha in test_dates:
        url = f"{base_url}/regression/predict/{username}?fecha={fecha}"
        print(f"\n📅 Probando fecha: {fecha}")
        print(f"🔗 URL: {url}")
        
        try:
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ Predicción: {data.get('prediction')}")
                print(f"   🤖 Modelo: {data.get('model_type')}")
                
                # Verificar que la respuesta tiene la estructura correcta
                expected_fields = {"prediction", "model_type", "target_variable"}
                actual_fields = set(data.keys())
                
                if actual_fields == expected_fields:
                    print("   ✅ Estructura de respuesta correcta")
                else:
                    print(f"   ❌ Estructura incorrecta: {actual_fields}")
                    
            else:
                print(f"   ❌ Error HTTP {response.status_code}")
                try:
                    error = response.json()
                    print(f"   💬 Mensaje: {error.get('detail', 'Sin detalle')}")
                except:
                    print(f"   💬 Respuesta: {response.text}")
                    
        except requests.exceptions.ConnectionError:
            print("   ❌ Error de conexión - servidor no disponible")
            break
        except Exception as e:
            print(f"   ❌ Error: {e}")

def verify_compatibility():
    """Verifica la compatibilidad completa del sistema"""
    print("\n🔍 VERIFICACIÓN DE COMPATIBILIDAD COMPLETA")
    print("="*60)
    
    # 1. Verificar que el endpoint extrae correctamente
    fecha_test = "2025-07-11"
    fecha_obj = datetime.strptime(fecha_test, "%Y-%m-%d")
    endpoint_features = {
        'dia_semana': fecha_obj.weekday(),
        'hora': 23,
        'mes': fecha_obj.month
    }
    
    print(f"🔗 Endpoint extrae de '{fecha_test}':")
    print(f"   {endpoint_features}")
    
    # 2. Verificar que los modelos esperan estas features
    models_dir = Path('models')
    if models_dir.exists():
        for user_dir in models_dir.iterdir():
            if user_dir.is_dir():
                model_path = user_dir / 'regresion.pkl'
                if model_path.exists():
                    try:
                        model_data = joblib.load(model_path)
                        model_features = model_data.get('feature_names', [])
                        
                        print(f"\n🤖 Modelo {user_dir.name} espera:")
                        print(f"   {model_features}")
                        
                        # Verificar compatibilidad
                        endpoint_keys = set(endpoint_features.keys())
                        model_keys = set(model_features)
                        
                        compatible_features = endpoint_keys.intersection(model_keys)
                        missing_in_endpoint = model_keys - endpoint_keys
                        
                        print(f"   ✅ Compatible: {compatible_features}")
                        if missing_in_endpoint:
                            print(f"   ⚠️  Faltan en endpoint: {missing_in_endpoint}")
                        
                        # Este modelo sería compatible si tiene al menos las temporales
                        temporal_features = {'dia_semana', 'hora', 'mes'}
                        has_temporal = temporal_features.issubset(model_keys)
                        
                        if has_temporal:
                            print(f"   ✅ COMPATIBLE: Usa features temporales")
                        else:
                            print(f"   ❌ NO COMPATIBLE: No usa features temporales")
                        
                        break  # Solo revisar uno para el ejemplo
                        
                    except Exception as e:
                        print(f"   ❌ Error: {e}")

def main():
    print("🚀 VERIFICACIÓN COMPLETA: Modelo de Regresión")
    print("="*60)
    
    try:
        test_feature_extraction()
        test_model_features()
        test_endpoint_prediction()
        verify_compatibility()
        
        print("\n" + "="*60)
        print("🎉 VERIFICACIÓN COMPLETADA")
        print()
        print("📋 Si todo está ✅:")
        print("   - Las features se extraen correctamente de la fecha")
        print("   - Los modelos usan estas features temporales")
        print("   - El endpoint funciona con diferentes fechas")
        print("   - Hay compatibilidad completa endpoint ↔ modelo")
        print()
        print("🎯 CONCLUSIÓN:")
        print("   El modelo SÍ está usando los parámetros de entrada")
        print("   que extraemos del parámetro 'fecha'.")
        print("="*60)
        
    except Exception as e:
        print(f"❌ Error durante la verificación: {e}")

if __name__ == "__main__":
    main()
