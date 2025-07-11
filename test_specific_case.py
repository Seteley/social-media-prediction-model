#!/usr/bin/env python3
"""
Test rápido para reproducir el problema específico
"""

import requests
import json

# El token que el usuario estaba usando (admin_interbank)
TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbl9pbnRlcmJhbmsiLCJlbXByZXNhX2lkIjoxLCJyb2wiOiJhZG1pbiIsImV4cCI6MTc1MjIzNTIyM30.Swt3_sMhntX-QX8TfUL6zCrOiRvSUNXYi1P6xpu2rho"

def test_specific_case():
    print("🧪 Probando el caso específico reportado...")
    print("Usuario: admin_interbank (empresa_id: 1)")
    print("Endpoint: /regression/predict/BCPComunica?fecha=2025-07-11")
    print("Resultado esperado: 403 Forbidden (acceso denegado)")
    print()
    
    url = "http://localhost:8000/regression/predict/BCPComunica?fecha=2025-07-11"
    headers = {"Authorization": f"Bearer {TOKEN}"}
    
    try:
        response = requests.get(url, headers=headers)
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 403:
            print("✅ CORRECTO: Acceso denegado como se esperaba")
            print(f"Mensaje: {response.json().get('detail', 'Sin detalle')}")
        elif response.status_code == 200:
            print("❌ ERROR: Acceso permitido cuando debería estar denegado")
            print(f"Respuesta: {response.json()}")
        else:
            print(f"⚠️  Código inesperado: {response.status_code}")
            print(f"Respuesta: {response.text}")
    
    except requests.exceptions.ConnectionError:
        print("❌ ERROR: No se puede conectar a la API")
        print("Asegúrate de que la API esté ejecutándose en localhost:8000")
    except Exception as e:
        print(f"❌ ERROR: {e}")

if __name__ == "__main__":
    test_specific_case()
