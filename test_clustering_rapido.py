#!/usr/bin/env python3
"""
Prueba rápida de endpoints de clustering con JWT
"""

import requests
import json

def main():
    print("🔐 Probando login...")
    login_data = {'username': 'test_admin', 'password': 'password123'}
    response = requests.post('http://localhost:8000/auth/login', data=login_data)
    print(f"Login status: {response.status_code}")

    if response.status_code == 200:
        token = response.json().get('access_token')
        print(f"✅ Token obtenido: {token[:20]}...")
        
        print("\n🧪 Probando endpoints con autenticación...")
        headers = {'Authorization': f'Bearer {token}'}
        
        endpoints = [
            '/clustering/users',
            '/clustering/model-info/BanBif',
            '/clustering/metrics/BanBif',
            '/clustering/history/BanBif'
        ]
        
        for endpoint in endpoints:
            test_response = requests.get(f'http://localhost:8000{endpoint}', headers=headers)
            if test_response.status_code == 200:
                print(f"✅ {endpoint} - Status: {test_response.status_code}")
            elif test_response.status_code == 403:
                print(f"🔒 {endpoint} - Status: {test_response.status_code} (Sin acceso a empresa)")
            elif test_response.status_code == 404:
                print(f"📁 {endpoint} - Status: {test_response.status_code} (Recurso no encontrado)")
            else:
                print(f"⚠️ {endpoint} - Status: {test_response.status_code}")
    else:
        print("❌ Login falló")
        try:
            print(f"Respuesta: {response.json()}")
        except:
            print(f"Respuesta texto: {response.text}")

if __name__ == "__main__":
    main()
