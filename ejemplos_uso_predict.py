#!/usr/bin/env python3
"""
Ejemplos prácticos del endpoint GET /regression/predict/{username}
Demuestra los dos modos de uso y clarifica la documentación
"""

import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8000"

def test_fecha_mode():
    """Prueba el MODO 1: Usando solo el parámetro 'fecha'"""
    print("🎯 MODO 1: Usando parámetro 'fecha'")
    print("="*50)
    
    # Ejemplos con diferentes fechas
    test_dates = [
        "2025-07-11",  # Viernes, Julio
        "2028-10-11",  # Miércoles, Octubre  
        "2025-12-25",  # Jueves, Diciembre
        "2026-01-01"   # Jueves, Enero
    ]
    
    for date in test_dates:
        url = f"{BASE_URL}/regression/predict/Interbank?fecha={date}"
        print(f"\n📅 Probando fecha: {date}")
        print(f"🔗 URL: {url}")
        
        try:
            response = requests.get(url)
            print(f"📊 Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Predicción: {data.get('prediction')}")
                print(f"🤖 Modelo: {data.get('model_type')}")
                print(f"🎯 Variable: {data.get('target_variable')}")
                
                # Mostrar cómo se interpretan los componentes de la fecha
                fecha_obj = datetime.strptime(date, "%Y-%m-%d")
                print(f"📋 Interpretación automática:")
                print(f"   - Día de semana: {fecha_obj.weekday()} ({fecha_obj.strftime('%A')})")
                print(f"   - Mes: {fecha_obj.month} ({fecha_obj.strftime('%B')})")
                print(f"   - Hora asumida: 23 (11 PM)")
            else:
                print(f"❌ Error: {response.text}")
                
        except requests.exceptions.ConnectionError:
            print("❌ No se pudo conectar al servidor")
            return
        except Exception as e:
            print(f"❌ Error: {e}")

def test_parametros_mode():
    """Prueba el MODO 2: Usando parámetros individuales"""
    print("\n\n🎯 MODO 2: Usando parámetros individuales")
    print("="*50)
    
    # Ejemplos con diferentes combinaciones de parámetros
    test_params = [
        {"dia_semana": 0, "mes": 7, "hora": 12},  # Lunes, Julio, mediodía
        {"dia_semana": 4, "mes": 12, "hora": 18}, # Viernes, Diciembre, 6 PM
        {"dia_semana": 6, "mes": 1},              # Domingo, Enero (hora default: 23)
        {"dia_semana": 2, "mes": 10, "hora": 9}   # Miércoles, Octubre, 9 AM
    ]
    
    for params in test_params:
        # Construir URL con parámetros
        param_str = "&".join([f"{k}={v}" for k, v in params.items()])
        url = f"{BASE_URL}/regression/predict/Interbank?{param_str}"
        
        print(f"\n📊 Probando parámetros: {params}")
        print(f"🔗 URL: {url}")
        
        # Traducir parámetros para mejor comprensión
        dias = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
        meses = ["", "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
                "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]
        
        dia_nombre = dias[params["dia_semana"]]
        mes_nombre = meses[params["mes"]]
        hora_valor = params.get("hora", 23)
        
        print(f"📋 Interpretación: {dia_nombre}, {mes_nombre}, {hora_valor}:00")
        
        try:
            response = requests.get(url)
            print(f"📊 Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Predicción: {data.get('prediction')}")
                print(f"🤖 Modelo: {data.get('model_type')}")
                print(f"🎯 Variable: {data.get('target_variable')}")
            else:
                print(f"❌ Error: {response.text}")
                
        except Exception as e:
            print(f"❌ Error: {e}")

def test_error_cases():
    """Prueba casos de error comunes"""
    print("\n\n⚠️  CASOS DE ERROR COMUNES")
    print("="*50)
    
    error_cases = [
        {
            "description": "Fecha con formato incorrecto",
            "url": f"{BASE_URL}/regression/predict/Interbank?fecha=2025/07/11"
        },
        {
            "description": "Día de semana fuera de rango",
            "url": f"{BASE_URL}/regression/predict/Interbank?dia_semana=8&mes=7"
        },
        {
            "description": "Mes fuera de rango",
            "url": f"{BASE_URL}/regression/predict/Interbank?dia_semana=1&mes=13"
        },
        {
            "description": "Hora fuera de rango",
            "url": f"{BASE_URL}/regression/predict/Interbank?dia_semana=1&mes=7&hora=25"
        },
        {
            "description": "Parámetros incompletos",
            "url": f"{BASE_URL}/regression/predict/Interbank?dia_semana=1"
        }
    ]
    
    for case in error_cases:
        print(f"\n❌ {case['description']}")
        print(f"🔗 URL: {case['url']}")
        
        try:
            response = requests.get(case["url"])
            print(f"📊 Status: {response.status_code}")
            if response.status_code != 200:
                data = response.json()
                print(f"💬 Mensaje: {data.get('detail', 'Error desconocido')}")
        except Exception as e:
            print(f"❌ Error: {e}")

def show_usage_summary():
    """Muestra un resumen de uso del endpoint"""
    print("\n\n📋 RESUMEN DE USO")
    print("="*60)
    print("🎯 Endpoint: GET /regression/predict/{username}")
    print()
    print("✅ MODO 1 - Solo fecha (RECOMENDADO):")
    print("   /regression/predict/Interbank?fecha=2025-07-11")
    print("   • Automáticamente calcula día_semana, mes")
    print("   • Asume hora=23 (11 PM)")
    print("   • Formato: YYYY-MM-DD")
    print()
    print("✅ MODO 2 - Parámetros individuales:")
    print("   /regression/predict/Interbank?dia_semana=4&mes=7&hora=15")
    print("   • dia_semana: 0-6 (0=Lunes, 6=Domingo)")
    print("   • mes: 1-12 (1=Enero, 12=Diciembre)")
    print("   • hora: 0-23 (opcional, default=23)")
    print()
    print("📤 RESPUESTA (siempre la misma estructura):")
    print("   {")
    print('     "prediction": 12500.0,')
    print('     "model_type": "RandomForestRegressor",')
    print('     "target_variable": "seguidores"')
    print("   }")
    print()
    print("⚠️  IMPORTANTE:")
    print("   • Use SOLO uno de los modos")
    print("   • Si usa 'fecha', los otros parámetros se ignoran")
    print("   • Validaciones automáticas de rangos")

def main():
    print("🚀 EJEMPLOS PRÁCTICOS: /regression/predict/{username}")
    print(f"🔗 Servidor: {BASE_URL}")
    print(f"👤 Usuario de prueba: Interbank")
    print(f"📅 Fecha actual: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        # Verificar conectividad
        response = requests.get(f"{BASE_URL}/")
        if response.status_code != 200:
            print("❌ Servidor no disponible")
            return
        
        # Ejecutar pruebas
        test_fecha_mode()
        test_parametros_mode()
        test_error_cases()
        show_usage_summary()
        
        print("\n" + "="*60)
        print("🎉 EJEMPLOS COMPLETADOS")
        print("📋 La documentación del endpoint ahora es más clara")
        print("✅ Los dos modos de uso están bien diferenciados")
        print("="*60)
        
    except requests.exceptions.ConnectionError:
        print("❌ Error: No se pudo conectar al servidor")
        print("   Asegúrate de que esté ejecutándose en http://localhost:8000")
    except Exception as e:
        print(f"❌ Error inesperado: {e}")

if __name__ == "__main__":
    main()
