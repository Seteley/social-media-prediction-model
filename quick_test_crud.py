#!/usr/bin/env python3
"""
Script de verificación rápida para endpoints CRUD
Prueba de forma simple si los endpoints están protegidos con JWT
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def quick_test_crud():
    print("🔒 VERIFICACIÓN RÁPIDA DE PROTECCIÓN JWT EN ENDPOINTS CRUD")
    print("=" * 60)
    
    # Endpoints a probar
    endpoints = [
        "/crud/publicaciones/BCPComunica",
        "/crud/metricas/BCPComunica"
    ]
    
    print("\n1️⃣ Probando acceso SIN TOKEN (debe devolver 401)")
    print("-" * 50)
    
    for endpoint in endpoints:
        try:
            response = requests.get(f"{BASE_URL}{endpoint}", timeout=5)
            if response.status_code == 401:
                print(f"✅ {endpoint}: 401 - Correctamente protegido")
            else:
                print(f"❌ {endpoint}: {response.status_code} - No protegido correctamente")
                try:
                    print(f"   Respuesta: {response.json()}")
                except:
                    print(f"   Respuesta: {response.text}")
        except requests.exceptions.ConnectionError:
            print(f"❌ {endpoint}: No se puede conectar al servidor")
        except Exception as e:
            print(f"❌ {endpoint}: Error - {e}")
    
    print("\n2️⃣ Probando con TOKEN INVÁLIDO (debe devolver 401)")
    print("-" * 50)
    
    invalid_token = "invalid_token_12345"
    headers = {"Authorization": f"Bearer {invalid_token}"}
    
    for endpoint in endpoints:
        try:
            response = requests.get(f"{BASE_URL}{endpoint}", headers=headers, timeout=5)
            if response.status_code == 401:
                print(f"✅ {endpoint}: 401 - Token inválido rechazado correctamente")
            else:
                print(f"❌ {endpoint}: {response.status_code} - Token inválido no rechazado")
                try:
                    print(f"   Respuesta: {response.json()}")
                except:
                    print(f"   Respuesta: {response.text}")
        except requests.exceptions.ConnectionError:
            print(f"❌ {endpoint}: No se puede conectar al servidor")
        except Exception as e:
            print(f"❌ {endpoint}: Error - {e}")
    
    print("\n3️⃣ RESUMEN")
    print("-" * 20)
    print("✅ Si todos los tests muestran 401, los endpoints están correctamente protegidos")
    print("❌ Si algún test no devuelve 401, hay un problema de seguridad")
    print("\n📝 Para pruebas completas con tokens válidos, usar: python test_crud_endpoints_jwt.py")

if __name__ == "__main__":
    quick_test_crud()
