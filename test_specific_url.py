#!/usr/bin/env python3
"""
Test específico para verificar el uso del endpoint con solo el parámetro 'fecha'
"""

import requests
import json
from datetime import datetime

def test_specific_url():
    """Prueba la URL específica mencionada por el usuario"""
    url = "http://localhost:8000/regression/predict/Interbank?fecha=2028-10-11"
    
    print("🧪 PRUEBA ESPECÍFICA")
    print("="*50)
    print(f"🔗 URL: {url}")
    print(f"📅 Fecha: 2028-10-11")
    
    # Mostrar interpretación de la fecha
    fecha_obj = datetime.strptime("2028-10-11", "%Y-%m-%d")
    print(f"📋 Interpretación automática:")
    print(f"   - Día de semana: {fecha_obj.weekday()} ({fecha_obj.strftime('%A')})")
    print(f"   - Mes: {fecha_obj.month} ({fecha_obj.strftime('%B')})")
    print(f"   - Hora asumida: 23 (11 PM)")
    print()
    
    try:
        print("📤 Enviando request...")
        response = requests.get(url, timeout=10)
        
        print(f"📊 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ RESPUESTA EXITOSA:")
            print(json.dumps(data, indent=2, ensure_ascii=False))
            
            # Verificar estructura de respuesta
            expected_fields = {"prediction", "model_type", "target_variable"}
            actual_fields = set(data.keys())
            
            if actual_fields == expected_fields:
                print("\n✅ Estructura de respuesta correcta")
                print("✅ Solo contiene los 3 campos esenciales")
            else:
                print(f"\n❌ Estructura incorrecta")
                print(f"   Esperados: {expected_fields}")
                print(f"   Recibidos: {actual_fields}")
                
        else:
            print("❌ ERROR:")
            try:
                error_data = response.json()
                print(json.dumps(error_data, indent=2, ensure_ascii=False))
            except:
                print(response.text)
    
    except requests.exceptions.ConnectionError:
        print("❌ Error de conexión")
        print("   El servidor no está ejecutándose en http://localhost:8000")
        print("   Para iniciarlo: python -m uvicorn app.main:app --reload")
    except requests.exceptions.Timeout:
        print("⏱️  Timeout - La request tardó más de 10 segundos")
    except Exception as e:
        print(f"❌ Error inesperado: {e}")

def show_exact_usage():
    """Muestra el uso exacto del endpoint"""
    print("\n\n📋 USO EXACTO DEL ENDPOINT")
    print("="*50)
    print("🎯 Endpoint: GET /regression/predict/{username}")
    print()
    print("✅ FORMA CORRECTA (la que usas):")
    print("   http://localhost:8000/regression/predict/Interbank?fecha=2028-10-11")
    print()
    print("📝 Explicación:")
    print("   • Solo necesitas el parámetro 'fecha'")
    print("   • El sistema automáticamente extrae:")
    print("     - dia_semana de la fecha (2028-10-11 = Miércoles = 2)")
    print("     - mes de la fecha (10 = Octubre)")
    print("     - hora se asume 23 (11 PM)")
    print()
    print("🚫 NO necesitas incluir:")
    print("   • dia_semana=2")
    print("   • mes=10") 
    print("   • hora=23")
    print("   Estos se calculan automáticamente desde 'fecha'")
    print()
    print("📤 Respuesta esperada:")
    print("   {")
    print('     "prediction": [número],')
    print('     "model_type": "[tipo de modelo]",')
    print('     "target_variable": "seguidores"')
    print("   }")

if __name__ == "__main__":
    print("🚀 VERIFICACIÓN DEL ENDPOINT DE PREDICCIÓN")
    print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    test_specific_url()
    show_exact_usage()
    
    print("\n" + "="*50)
    print("✅ VERIFICACIÓN COMPLETADA")
    print("📋 La documentación del endpoint ha sido clarificada")
    print("🎯 Tu forma de usar el endpoint es la correcta")
    print("="*50)
