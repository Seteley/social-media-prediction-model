#!/usr/bin/env python3
"""
Script simple para probar que los endpoints de clustering estén funcionando
"""

import requests
import time
import sys

def test_api_connection():
    """Probar conexión básica con la API"""
    try:
        print("🔍 Probando conexión con la API...")
        response = requests.get("http://localhost:8000/docs", timeout=5)
        if response.status_code == 200:
            print("✅ API está respondiendo correctamente")
            return True
        else:
            print(f"❌ API respondió con código {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Error de conexión: {e}")
        return False

def test_clustering_endpoints():
    """Probar endpoints básicos de clustering"""
    endpoints = [
        "/clustering/users",
        "/clustering/model-info/BanBif",
        "/clustering/metrics/BanBif",
        "/clustering/history/BanBif",
        "/clustering/train/BanBif",
        "/clustering/clusters/BanBif"
    ]
    
    print("\n🧪 Probando endpoints de clustering (sin autenticación - debe dar 401)...")
    
    for endpoint in endpoints:
        try:
            response = requests.get(f"http://localhost:8000{endpoint}", timeout=10)
            if response.status_code == 401:
                print(f"✅ {endpoint} - Retorna 401 (correcto)")
            else:
                print(f"⚠️  {endpoint} - Retorna {response.status_code} (esperado 401)")
        except Exception as e:
            print(f"❌ {endpoint} - Error: {e}")

def main():
    print("🚀 Iniciando pruebas simples de clustering...")
    
    if not test_api_connection():
        print("\n💥 No se puede conectar con la API. Asegúrese de que esté ejecutándose.")
        print("Para iniciar la API, ejecute: uvicorn app.main:app --host 0.0.0.0 --port 8000")
        return False
    
    test_clustering_endpoints()
    print("\n✅ Pruebas básicas completadas")
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
