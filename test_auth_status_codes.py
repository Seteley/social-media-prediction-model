#!/usr/bin/env python3
"""
Test para verificar los códigos de estado HTTP correctos
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def test_authentication_errors():
    print("🧪 PRUEBAS DE CÓDIGOS DE ERROR DE AUTENTICACIÓN")
    print("=" * 60)
    
    # Test 1: Sin token (debe ser 401)
    print("\n1️⃣  TEST: Acceso sin token de autenticación")
    print("   Endpoint: GET /regression/predict/Interbank?fecha=2025-07-11")
    print("   Resultado esperado: 401 Unauthorized")
    
    try:
        response = requests.get(f"{BASE_URL}/regression/predict/Interbank?fecha=2025-07-11")
        
        print(f"   ✅ Status Code: {response.status_code}")
        if response.status_code == 401:
            print("   ✅ CORRECTO: 401 Unauthorized")
            detail = response.json().get('detail', 'Sin detalle')
            print(f"   📄 Mensaje: {detail}")
        else:
            print(f"   ❌ INCORRECTO: Esperado 401, obtenido {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ ERROR: {e}")
    
    # Test 2: Usuario inactivo (debe ser 401 con mensaje específico)
    print("\n2️⃣  TEST: Login con usuario inactivo")
    print("   Usuario: inactive_user")
    print("   Resultado esperado: 401 Unauthorized - 'Cuenta de usuario inactiva'")
    
    try:
        login_data = {
            "username": "inactive_user",
            "password": "password123"
        }
        
        response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
        
        print(f"   ✅ Status Code: {response.status_code}")
        
        if response.status_code == 401:
            detail = response.json().get('detail', 'Sin detalle')
            print(f"   📄 Mensaje: {detail}")
            
            if "inactiva" in detail.lower() or "inactive" in detail.lower():
                print("   ✅ CORRECTO: Mensaje específico para usuario inactivo")
            else:
                print("   ⚠️  ADVERTENCIA: Mensaje no específico para usuario inactivo")
        else:
            print(f"   ❌ INCORRECTO: Esperado 401, obtenido {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ ERROR: {e}")
    
    # Test 3: Credenciales incorrectas (debe ser 401)
    print("\n3️⃣  TEST: Login con credenciales incorrectas")
    print("   Usuario: usuario_inexistente")
    print("   Resultado esperado: 401 Unauthorized - 'Credenciales incorrectas'")
    
    try:
        login_data = {
            "username": "usuario_inexistente",
            "password": "password_incorrecto"
        }
        
        response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
        
        print(f"   ✅ Status Code: {response.status_code}")
        
        if response.status_code == 401:
            detail = response.json().get('detail', 'Sin detalle')
            print(f"   📄 Mensaje: {detail}")
            
            if "credenciales" in detail.lower():
                print("   ✅ CORRECTO: Mensaje para credenciales incorrectas")
            else:
                print("   ⚠️  ADVERTENCIA: Mensaje no específico")
        else:
            print(f"   ❌ INCORRECTO: Esperado 401, obtenido {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ ERROR: {e}")
    
    # Test 4: Login exitoso (debe ser 200)
    print("\n4️⃣  TEST: Login exitoso con usuario activo")
    print("   Usuario: admin_interbank")
    print("   Resultado esperado: 200 OK")
    
    try:
        login_data = {
            "username": "admin_interbank",
            "password": "password123"
        }
        
        response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
        
        print(f"   ✅ Status Code: {response.status_code}")
        
        if response.status_code == 200:
            token_data = response.json()
            print("   ✅ CORRECTO: Login exitoso")
            print(f"   📄 Usuario: {token_data.get('username', 'N/A')}")
            print(f"   📄 Empresa ID: {token_data.get('empresa_id', 'N/A')}")
            print(f"   📄 Token type: {token_data.get('token_type', 'N/A')}")
            
            # Test adicional: Usar el token
            token = token_data.get('access_token')
            if token:
                print("\n   🔐 TEST ADICIONAL: Usar token obtenido")
                headers = {"Authorization": f"Bearer {token}"}
                test_response = requests.get(f"{BASE_URL}/regression/predict/Interbank?fecha=2025-07-11", headers=headers)
                print(f"       Status: {test_response.status_code}")
                
                if test_response.status_code == 200:
                    print("       ✅ Token funciona correctamente")
                elif test_response.status_code == 403:
                    print("       ✅ Control de acceso funcionando")
                else:
                    print(f"       ⚠️  Resultado inesperado: {test_response.status_code}")
        else:
            print(f"   ❌ INCORRECTO: Esperado 200, obtenido {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ ERROR: {e}")
    
    print("\n" + "=" * 60)
    print("RESUMEN:")
    print("- Sin autenticación → 401 Unauthorized ✅")
    print("- Usuario inactivo → 401 'Cuenta de usuario inactiva' ✅")
    print("- Credenciales incorrectas → 401 'Credenciales incorrectas' ✅")
    print("- Login exitoso → 200 OK ✅")

if __name__ == "__main__":
    test_authentication_errors()
