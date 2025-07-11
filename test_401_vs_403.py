#!/usr/bin/env python3
"""
Test específico para verificar códigos de estado 401 vs 403
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def test_401_vs_403():
    print("🧪 PRUEBA ESPECÍFICA: CÓDIGOS 401 vs 403")
    print("=" * 60)
    
    print("\n1️⃣  TEST: Sin header Authorization (debe ser 401)")
    print("   Endpoint: GET /regression/predict/Interbank?fecha=2025-07-11")
    print("   Resultado esperado: 401 Unauthorized")
    
    try:
        # Test sin header Authorization
        response = requests.get(f"{BASE_URL}/regression/predict/Interbank?fecha=2025-07-11")
        
        print(f"   📊 Status Code: {response.status_code}")
        
        if response.status_code == 401:
            print("   ✅ CORRECTO: 401 Unauthorized")
        elif response.status_code == 403:
            print("   ❌ INCORRECTO: 403 Forbidden (debería ser 401)")
        else:
            print(f"   ❌ INESPERADO: {response.status_code}")
        
        try:
            detail = response.json().get('detail', 'Sin detalle')
            print(f"   📄 Mensaje: {detail}")
        except:
            print(f"   📄 Respuesta raw: {response.text}")
            
    except Exception as e:
        print(f"   ❌ ERROR: {e}")
    
    print("\n2️⃣  TEST: Header Authorization vacío (debe ser 401)")
    print("   Endpoint: GET /regression/predict/Interbank?fecha=2025-07-11")
    print("   Header: Authorization: Bearer")
    
    try:
        headers = {"Authorization": "Bearer"}
        response = requests.get(f"{BASE_URL}/regression/predict/Interbank?fecha=2025-07-11", headers=headers)
        
        print(f"   📊 Status Code: {response.status_code}")
        
        if response.status_code == 401:
            print("   ✅ CORRECTO: 401 Unauthorized")
        elif response.status_code == 403:
            print("   ❌ INCORRECTO: 403 Forbidden (debería ser 401)")
        else:
            print(f"   ❌ INESPERADO: {response.status_code}")
        
        try:
            detail = response.json().get('detail', 'Sin detalle')
            print(f"   📄 Mensaje: {detail}")
        except:
            print(f"   📄 Respuesta raw: {response.text}")
            
    except Exception as e:
        print(f"   ❌ ERROR: {e}")
    
    print("\n3️⃣  TEST: Token inválido (debe ser 401)")
    print("   Token: token_completamente_invalido")
    
    try:
        headers = {"Authorization": "Bearer token_completamente_invalido"}
        response = requests.get(f"{BASE_URL}/regression/predict/Interbank?fecha=2025-07-11", headers=headers)
        
        print(f"   📊 Status Code: {response.status_code}")
        
        if response.status_code == 401:
            print("   ✅ CORRECTO: 401 Unauthorized")
        elif response.status_code == 403:
            print("   ❌ INCORRECTO: 403 Forbidden (debería ser 401)")
        else:
            print(f"   ❌ INESPERADO: {response.status_code}")
        
        try:
            detail = response.json().get('detail', 'Sin detalle')
            print(f"   📄 Mensaje: {detail}")
        except:
            print(f"   📄 Respuesta raw: {response.text}")
            
    except Exception as e:
        print(f"   ❌ ERROR: {e}")
    
    print("\n4️⃣  TEST: Login para obtener token válido")
    
    try:
        login_data = {"username": "admin_interbank", "password": "password123"}
        login_response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
        
        if login_response.status_code == 200:
            token_data = login_response.json()
            token = token_data.get('access_token')
            print(f"   ✅ Login exitoso, token obtenido")
            
            if token:
                print("\n5️⃣  TEST: Token válido pero sin acceso (debe ser 403)")
                print("   Usuario: admin_interbank (empresa 1)")
                print("   Cuenta: BCPComunica (empresa 7)")
                
                headers = {"Authorization": f"Bearer {token}"}
                response = requests.get(f"{BASE_URL}/regression/predict/BCPComunica?fecha=2025-07-11", headers=headers)
                
                print(f"   📊 Status Code: {response.status_code}")
                
                if response.status_code == 403:
                    print("   ✅ CORRECTO: 403 Forbidden")
                elif response.status_code == 401:
                    print("   ❌ INCORRECTO: 401 Unauthorized (debería ser 403)")
                else:
                    print(f"   ❌ INESPERADO: {response.status_code}")
                
                try:
                    detail = response.json().get('detail', 'Sin detalle')
                    print(f"   📄 Mensaje: {detail}")
                except:
                    print(f"   📄 Respuesta raw: {response.text}")
                
                print("\n6️⃣  TEST: Token válido con acceso (debe ser 200)")
                print("   Usuario: admin_interbank (empresa 1)")
                print("   Cuenta: Interbank (empresa 1)")
                
                response = requests.get(f"{BASE_URL}/regression/predict/Interbank?fecha=2025-07-11", headers=headers)
                
                print(f"   📊 Status Code: {response.status_code}")
                
                if response.status_code == 200:
                    print("   ✅ CORRECTO: 200 OK")
                elif response.status_code == 404:
                    print("   ⚠️  404 Not Found (modelo no existe, pero autenticación funciona)")
                else:
                    print(f"   ❌ INESPERADO: {response.status_code}")
                
                try:
                    if response.status_code != 500:
                        detail = response.json()
                        print(f"   📄 Respuesta: {str(detail)[:100]}...")
                except:
                    print(f"   📄 Respuesta raw: {response.text[:100]}...")
        else:
            print(f"   ❌ Login falló: {login_response.status_code}")
            
    except Exception as e:
        print(f"   ❌ ERROR: {e}")
    
    print("\n" + "=" * 60)
    print("RESUMEN ESPERADO:")
    print("- Sin token → 401 Unauthorized ✅")
    print("- Token vacío → 401 Unauthorized ✅") 
    print("- Token inválido → 401 Unauthorized ✅")
    print("- Token válido sin acceso → 403 Forbidden ✅")
    print("- Token válido con acceso → 200 OK (o 404 si no hay modelo) ✅")

if __name__ == "__main__":
    test_401_vs_403()
