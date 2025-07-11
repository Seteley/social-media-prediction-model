#!/usr/bin/env python3
"""
Test para verificar que el control de acceso funciona correctamente en endpoints de regresión
"""

import requests
import json
from datetime import datetime

# Configuración
BASE_URL = "http://localhost:8000"
LOGIN_URL = f"{BASE_URL}/auth/login"

def login_user(username: str, password: str):
    """Login y obtención de token"""
    response = requests.post(LOGIN_URL, json={
        "username": username,
        "password": password
    })
    if response.status_code == 200:
        return response.json()["access_token"]
    else:
        print(f"❌ Error en login para {username}: {response.status_code} - {response.text}")
        return None

def test_endpoint_access(token: str, endpoint: str, username_test: str):
    """Prueba acceso a un endpoint específico"""
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(f"{BASE_URL}{endpoint}", headers=headers)
        return {
            "status_code": response.status_code,
            "allowed": response.status_code != 403,
            "response": response.json() if response.status_code != 500 else {"error": "server_error"}
        }
    except Exception as e:
        return {
            "status_code": 500,
            "allowed": False,
            "response": {"error": str(e)}
        }

def main():
    print("=" * 60)
    print("PRUEBA DE CONTROL DE ACCESO - ENDPOINTS DE REGRESIÓN")
    print("=" * 60)
    
    # Test usuarios
    test_users = [
        {"username": "interbank_user", "password": "password123", "empresa": "Interbank"},
        {"username": "bcp_admin", "password": "password123", "empresa": "BCPComunica"}
    ]
    
    # Test accounts/empresas
    test_accounts = ["Interbank", "BCPComunica", "ScotiabankPE"]
    
    # Endpoints a probar
    test_endpoints = [
        "/regression/predict/{account}?fecha=2025-01-15",
        "/regression/model-info/{account}",
        "/regression/features/{account}"
    ]
    
    results = []
    
    for user in test_users:
        print(f"\n🔑 Testing user: {user['username']} (Empresa: {user['empresa']})")
        
        # Login
        token = login_user(user['username'], user['password'])
        if not token:
            continue
        
        print(f"✅ Login exitoso para {user['username']}")
        
        for account in test_accounts:
            print(f"\n  🏢 Probando acceso a cuenta: {account}")
            
            for endpoint_template in test_endpoints:
                endpoint = endpoint_template.replace("{account}", account)
                
                print(f"    📍 Endpoint: {endpoint}")
                
                result = test_endpoint_access(token, endpoint, account)
                
                # Determinar si debería tener acceso
                should_have_access = (account == user['empresa']) or (user['username'] == 'bcp_admin' and 'admin' in user['username'])
                
                status_icon = "✅" if result['allowed'] == should_have_access else "❌"
                access_text = "PERMITIDO" if result['allowed'] else "DENEGADO"
                expected_text = "esperado" if result['allowed'] == should_have_access else "¡INCORRECTO!"
                
                print(f"      {status_icon} {access_text} ({expected_text}) - Status: {result['status_code']}")
                
                if result['status_code'] == 403:
                    print(f"        Mensaje: {result['response'].get('detail', 'Sin detalle')}")
                
                results.append({
                    "user": user['username'],
                    "user_empresa": user['empresa'],
                    "account_tested": account,
                    "endpoint": endpoint,
                    "should_have_access": should_have_access,
                    "actually_has_access": result['allowed'],
                    "correct": result['allowed'] == should_have_access,
                    "status_code": result['status_code'],
                    "response": result['response']
                })
    
    # Resumen de resultados
    print("\n" + "=" * 60)
    print("RESUMEN DE RESULTADOS")
    print("=" * 60)
    
    total_tests = len(results)
    correct_tests = sum(1 for r in results if r['correct'])
    incorrect_tests = total_tests - correct_tests
    
    print(f"Total de pruebas: {total_tests}")
    print(f"Pruebas correctas: {correct_tests}")
    print(f"Pruebas incorrectas: {incorrect_tests}")
    print(f"Porcentaje de éxito: {(correct_tests/total_tests)*100:.1f}%")
    
    if incorrect_tests > 0:
        print(f"\n❌ PROBLEMAS DETECTADOS ({incorrect_tests} casos):")
        for r in results:
            if not r['correct']:
                expected = "debería tener" if r['should_have_access'] else "NO debería tener"
                actual = "tiene" if r['actually_has_access'] else "NO tiene"
                print(f"  - {r['user']} {expected} acceso a {r['account_tested']} pero {actual} acceso")
                print(f"    Endpoint: {r['endpoint']}")
                print(f"    Status: {r['status_code']}")
    else:
        print(f"\n✅ TODOS LOS TESTS PASARON - Control de acceso funcionando correctamente")
    
    # Guardar resultados detallados
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"test_regression_access_results_{timestamp}.json"
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump({
            "timestamp": timestamp,
            "summary": {
                "total_tests": total_tests,
                "correct_tests": correct_tests,
                "incorrect_tests": incorrect_tests,
                "success_rate": (correct_tests/total_tests)*100
            },
            "results": results
        }, f, indent=2, ensure_ascii=False)
    
    print(f"\n📄 Resultados detallados guardados en: {filename}")

if __name__ == "__main__":
    main()
