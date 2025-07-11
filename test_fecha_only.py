#!/usr/bin/env python3
"""
Test para verificar que el endpoint solo acepta el parámetro 'fecha'
y que los parámetros individuales ya no están disponibles.
"""

import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8000"
TEST_USERNAME = "Interbank"

def test_fecha_only():
    """Prueba que el endpoint solo acepta fechas"""
    print("🧪 TEST: Solo parámetro 'fecha'")
    print("="*50)
    
    # Test con fecha válida
    url = f"{BASE_URL}/regression/predict/{TEST_USERNAME}?fecha=2025-07-11"
    print(f"✅ Probando con fecha: {url}")
    
    try:
        response = requests.get(url)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ RESPUESTA EXITOSA:")
            print(json.dumps(data, indent=2, ensure_ascii=False))
            
            # Verificar estructura
            expected_fields = {"prediction", "model_type", "target_variable"}
            actual_fields = set(data.keys())
            if actual_fields == expected_fields:
                print("✅ Estructura correcta (solo 3 campos)")
            else:
                print(f"❌ Estructura incorrecta: {actual_fields}")
        else:
            print(f"❌ Error: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

def test_parametros_individuales_removed():
    """Verifica que los parámetros individuales ya no funcionen"""
    print("\n🧪 TEST: Parámetros individuales eliminados")
    print("="*50)
    
    # Intentar usar parámetros del modo 2 (deberían fallar)
    test_urls = [
        f"{BASE_URL}/regression/predict/{TEST_USERNAME}?dia_semana=2&mes=10&hora=15",
        f"{BASE_URL}/regression/predict/{TEST_USERNAME}?dia_semana=4&mes=7",
        f"{BASE_URL}/regression/predict/{TEST_USERNAME}?mes=12&hora=9"
    ]
    
    for url in test_urls:
        print(f"\n❌ Probando URL antigua: {url}")
        try:
            response = requests.get(url)
            print(f"Status: {response.status_code}")
            
            if response.status_code != 200:
                print("✅ Correctamente rechazado (parámetros individuales eliminados)")
                try:
                    error = response.json()
                    print(f"Mensaje: {error.get('detail', 'Error sin mensaje')}")
                except:
                    print(f"Texto: {response.text}")
            else:
                print("❌ PROBLEMA: Aún acepta parámetros individuales")
                
        except Exception as e:
            print(f"❌ Error: {e}")

def test_fecha_requerida():
    """Verifica que la fecha sea requerida"""
    print("\n🧪 TEST: Fecha es requerida")
    print("="*50)
    
    # Intentar sin parámetros
    url = f"{BASE_URL}/regression/predict/{TEST_USERNAME}"
    print(f"❌ Probando sin parámetros: {url}")
    
    try:
        response = requests.get(url)
        print(f"Status: {response.status_code}")
        
        if response.status_code != 200:
            print("✅ Correctamente rechazado (fecha requerida)")
            try:
                error = response.json()
                print(f"Mensaje: {error.get('detail', 'Error sin mensaje')}")
            except:
                print(f"Texto: {response.text}")
        else:
            print("❌ PROBLEMA: Acepta request sin fecha")
            
    except Exception as e:
        print(f"❌ Error: {e}")

def test_formatos_fecha():
    """Prueba diferentes formatos de fecha"""
    print("\n🧪 TEST: Validación de formatos de fecha")
    print("="*50)
    
    test_cases = [
        {"fecha": "2025-07-11", "descripcion": "Formato correcto", "esperado": 200},
        {"fecha": "2025/07/11", "descripcion": "Formato incorrecto (/)", "esperado": 400},
        {"fecha": "07-11-2025", "descripcion": "Formato incorrecto (MM-DD-YYYY)", "esperado": 400},
        {"fecha": "2025-13-01", "descripcion": "Mes inválido", "esperado": 400},
        {"fecha": "2025-07-32", "descripcion": "Día inválido", "esperado": 400},
        {"fecha": "texto", "descripcion": "Texto no fecha", "esperado": 400}
    ]
    
    for case in test_cases:
        url = f"{BASE_URL}/regression/predict/{TEST_USERNAME}?fecha={case['fecha']}"
        print(f"\n📅 {case['descripcion']}: {case['fecha']}")
        
        try:
            response = requests.get(url)
            print(f"Status: {response.status_code}")
            
            if response.status_code == case["esperado"]:
                print("✅ Comportamiento esperado")
                if response.status_code != 200:
                    try:
                        error = response.json()
                        print(f"Mensaje: {error.get('detail', 'Sin mensaje')}")
                    except:
                        pass
            else:
                print(f"❌ Esperado {case['esperado']}, obtuvo {response.status_code}")
                
        except Exception as e:
            print(f"❌ Error: {e}")

def main():
    print("🚀 VERIFICACIÓN: Endpoint solo acepta fechas")
    print(f"🔗 Servidor: {BASE_URL}")
    print(f"👤 Usuario de prueba: {TEST_USERNAME}")
    print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        # Verificar conectividad
        response = requests.get(f"{BASE_URL}/")
        if response.status_code != 200:
            print("❌ Servidor no disponible")
            return
        
        # Ejecutar pruebas
        test_fecha_only()
        test_parametros_individuales_removed()
        test_fecha_requerida()
        test_formatos_fecha()
        
        print("\n" + "="*60)
        print("🎉 VERIFICACIÓN COMPLETADA")
        print("📋 Resultados esperados:")
        print("   ✅ Solo acepta parámetro 'fecha'")
        print("   ❌ Rechaza parámetros individuales (dia_semana, mes, hora)")
        print("   ✅ Fecha es requerida")
        print("   ✅ Valida formato YYYY-MM-DD")
        print("   ✅ Respuesta simplificada (3 campos)")
        print("="*60)
        
    except requests.exceptions.ConnectionError:
        print("❌ Error: No se pudo conectar al servidor")
        print("   Para iniciarlo: python -m uvicorn app.main:app --reload")
    except Exception as e:
        print(f"❌ Error inesperado: {e}")

if __name__ == "__main__":
    main()
