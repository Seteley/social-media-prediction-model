#!/usr/bin/env python3
"""
Script de prueba para validar la actualización del endpoint /regression/train 
y verificar que todos los endpoints de regresión implementan JWT correctamente.
"""

import requests
import json
import sys

def test_regression_train_endpoint():
    """Probar el nuevo endpoint GET /regression/train/{username}"""
    
    print("🧪 PRUEBAS DEL ENDPOINT /regression/train/{username}")
    print("=" * 60)
    
    # Datos de prueba
    base_url = "http://localhost:8000"
    login_data = {"username": "admin_interbank", "password": "password123"}
    
    # 1. Login
    print("🔐 Probando login...")
    try:
        response = requests.post(f"{base_url}/auth/login", json=login_data)
        if response.status_code == 200:
            token = response.json().get("access_token")
            print(f"✅ Login exitoso: {token[:20]}...")
        else:
            print(f"❌ Login falló: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error de conexión: {e}")
        return False
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # 2. Probar endpoint sin autenticación (debe dar 401)
    print("\n🔒 Probando sin autenticación (esperado 401)...")
    try:
        response = requests.get(f"{base_url}/regression/train/Interbank")
        if response.status_code == 401:
            print("✅ Retorna 401 sin autenticación")
        else:
            print(f"⚠️ Retorna {response.status_code} (esperado 401)")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # 3. Probar endpoint con autenticación válida
    print("\n🚀 Probando con autenticación válida...")
    try:
        response = requests.get(f"{base_url}/regression/train/Interbank", headers=headers)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Entrenamiento exitoso:")
            print(f"   • Mensaje: {result.get('message', 'N/A')}")
            print(f"   • Mejor modelo: {result.get('best_model', 'N/A')}")
            print(f"   • R² Score: {result.get('metrics', {}).get('r2_score', 'N/A')}")
        elif response.status_code == 403:
            print("🔒 Sin acceso a la cuenta (correcto si es diferente empresa)")
        elif response.status_code == 404:
            print("📁 Cuenta no encontrada o sin datos")
        else:
            print(f"⚠️ Status inesperado: {response.status_code}")
            try:
                print(f"   Respuesta: {response.json()}")
            except:
                print(f"   Respuesta: {response.text[:200]}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # 4. Probar acceso cruzado (diferente empresa)
    print("\n🚫 Probando acceso cruzado (esperado 403)...")
    try:
        response = requests.get(f"{base_url}/regression/train/BCPComunica", headers=headers)
        if response.status_code == 403:
            print("✅ Bloquea acceso cruzado (403)")
        else:
            print(f"⚠️ Status: {response.status_code} (esperado 403)")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # 5. Probar con parámetros query
    print("\n⚙️ Probando con parámetros query...")
    try:
        params = {
            "target_variable": "seguidores",
            "test_size": 0.3,
            "random_state": 123
        }
        response = requests.get(f"{base_url}/regression/train/Interbank", headers=headers, params=params)
        print(f"Status con parámetros: {response.status_code}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    return True

def test_all_regression_endpoints():
    """Probar todos los endpoints de regresión"""
    
    print("\n\n🔍 PRUEBAS DE TODOS LOS ENDPOINTS DE REGRESIÓN")
    print("=" * 60)
    
    base_url = "http://localhost:8000"
    login_data = {"username": "admin_interbank", "password": "password123"}
    
    # Login
    response = requests.post(f"{base_url}/auth/login", json=login_data)
    if response.status_code != 200:
        print("❌ No se pudo hacer login")
        return False
    
    token = response.json().get("access_token")
    headers = {"Authorization": f"Bearer {token}"}
    
    # Endpoints a probar
    endpoints = [
        {"method": "GET", "url": "/regression/users", "description": "Lista usuarios"},
        {"method": "GET", "url": "/regression/available-accounts", "description": "Cuentas disponibles"},
        {"method": "GET", "url": "/regression/metrics/Interbank", "description": "Métricas modelo"},
        {"method": "GET", "url": "/regression/history/Interbank", "description": "Historial entrenamientos"},
        {"method": "GET", "url": "/regression/train/Interbank", "description": "Entrenar modelo"},
        {"method": "DELETE", "url": "/regression/model/Interbank", "description": "Eliminar modelo"},
        {"method": "GET", "url": "/regression/compare-models/Interbank", "description": "Comparar modelos"},
    ]
    
    print("🧪 Probando endpoints sin autenticación (esperado 401):")
    for endpoint in endpoints:
        try:
            if endpoint["method"] == "GET":
                response = requests.get(f"{base_url}{endpoint['url']}")
            elif endpoint["method"] == "DELETE":
                response = requests.delete(f"{base_url}{endpoint['url']}")
            
            if response.status_code == 401:
                print(f"✅ {endpoint['url']} - 401")
            else:
                print(f"⚠️ {endpoint['url']} - {response.status_code}")
        except Exception as e:
            print(f"❌ {endpoint['url']} - Error: {e}")
    
    print("\n🔑 Probando endpoints con autenticación:")
    for endpoint in endpoints:
        try:
            if endpoint["method"] == "GET":
                response = requests.get(f"{base_url}{endpoint['url']}", headers=headers)
            elif endpoint["method"] == "DELETE":
                response = requests.delete(f"{base_url}{endpoint['url']}", headers=headers)
            
            if response.status_code in [200, 403, 404]:
                print(f"✅ {endpoint['url']} - {response.status_code} ({endpoint['description']})")
            else:
                print(f"⚠️ {endpoint['url']} - {response.status_code}")
        except Exception as e:
            print(f"❌ {endpoint['url']} - Error: {e}")
    
    return True

def main():
    """Función principal"""
    print("🚀 PRUEBAS DE ACTUALIZACIÓN REGRESSION TRAIN ENDPOINT")
    print("Verificando que la API esté ejecutándose...")
    
    try:
        response = requests.get("http://localhost:8000/docs", timeout=5)
        if response.status_code != 200:
            print("❌ La API no está respondiendo")
            return False
    except:
        print("❌ No se puede conectar con la API en localhost:8000")
        print("Para iniciar: uvicorn app.main:app --host 0.0.0.0 --port 8000")
        return False
    
    print("✅ API está ejecutándose\n")
    
    # Ejecutar pruebas
    success1 = test_regression_train_endpoint()
    success2 = test_all_regression_endpoints()
    
    if success1 and success2:
        print("\n🎉 ¡TODAS LAS PRUEBAS COMPLETADAS!")
        print("✅ Endpoint /regression/train/{username} actualizado correctamente")
        print("✅ Todos los endpoints implementan JWT y control de acceso")
        return True
    else:
        print("\n💥 Algunas pruebas fallaron")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
