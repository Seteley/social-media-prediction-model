#!/usr/bin/env python3
"""
Script para probar el endpoint de predicción simplificado.
Verifica que solo se devuelvan los campos: prediction, model_type, target_variable
"""

import requests
import json

# Configuración
BASE_URL = "http://localhost:8000"
USERNAME = "BanBif"  # Usuario de prueba

def test_prediction_endpoint():
    """Prueba el endpoint de predicción con fecha"""
    
    # Test 1: Usando parámetro fecha
    print("🧪 Test 1: Predicción usando parámetro 'fecha'")
    url = f"{BASE_URL}/regression/predict/{USERNAME}"
    params = {"fecha": "2025-07-11"}
    
    try:
        response = requests.get(url, params=params)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Respuesta recibida:")
            print(json.dumps(data, indent=2, ensure_ascii=False))
            
            # Verificar que solo tenga los campos esperados
            expected_fields = {"prediction", "model_type", "target_variable"}
            actual_fields = set(data.keys())
            
            if actual_fields == expected_fields:
                print("✅ ¡Perfecto! Solo contiene los campos requeridos.")
            else:
                print("❌ Error: Campos no coinciden")
                print(f"   Esperados: {expected_fields}")
                print(f"   Recibidos: {actual_fields}")
                extra = actual_fields - expected_fields
                missing = expected_fields - actual_fields
                if extra:
                    print(f"   Campos extra: {extra}")
                if missing:
                    print(f"   Campos faltantes: {missing}")
        else:
            print(f"❌ Error: {response.status_code}")
            print(response.text)
            
    except requests.exceptions.ConnectionError:
        print("❌ Error: No se pudo conectar al servidor. Asegúrate de que esté ejecutándose.")
        return False
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        return False
    
    print()
    
    # Test 2: Usando parámetros individuales
    print("🧪 Test 2: Predicción usando parámetros individuales")
    params = {
        "dia_semana": 4,  # Viernes
        "mes": 7,         # Julio
        "hora": 15        # 3 PM
    }
    
    try:
        response = requests.get(url, params=params)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Respuesta recibida:")
            print(json.dumps(data, indent=2, ensure_ascii=False))
            
            # Verificar campos nuevamente
            expected_fields = {"prediction", "model_type", "target_variable"}
            actual_fields = set(data.keys())
            
            if actual_fields == expected_fields:
                print("✅ ¡Perfecto! Solo contiene los campos requeridos.")
            else:
                print("❌ Error: Campos no coinciden")
                print(f"   Esperados: {expected_fields}")
                print(f"   Recibidos: {actual_fields}")
        else:
            print(f"❌ Error: {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    return True

def test_model_info():
    """Prueba el endpoint de información del modelo"""
    print("🧪 Test 3: Información del modelo")
    url = f"{BASE_URL}/regression/model-info/{USERNAME}"
    
    try:
        response = requests.get(url)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Información del modelo:")
            print(f"   Usuario: {data.get('username')}")
            print(f"   Variable objetivo: {data.get('target_variable')}")
            print(f"   Tipo de modelo: {data.get('model_type')}")
            print(f"   Features requeridas: {data.get('feature_names')}")
        else:
            print(f"❌ Error: {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    print("🚀 Probando endpoint de predicción simplificado...")
    print(f"URL base: {BASE_URL}")
    print(f"Usuario de prueba: {USERNAME}")
    print("=" * 50)
    
    success = test_prediction_endpoint()
    test_model_info()
    
    print("=" * 50)
    if success:
        print("✅ ¡Pruebas completadas! El endpoint está funcionando correctamente.")
        print("📋 Resumen:")
        print("   - Solo devuelve los campos esenciales: prediction, model_type, target_variable")
        print("   - Acepta tanto fecha (YYYY-MM-DD) como parámetros individuales")
        print("   - Respuesta limpia y simplificada")
    else:
        print("❌ Algunas pruebas fallaron. Revisa los logs arriba.")
