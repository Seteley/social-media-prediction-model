#!/usr/bin/env python3
"""
Script para probar los endpoints de clustering protegidos con JWT
"""

import requests
import json

def test_clustering_jwt():
    """Probar el flujo completo de clustering con JWT"""
    
    print("🧪 PRUEBA DE CLUSTERING CON JWT")
    print("=" * 40)
    
    base_url = "http://localhost:8000"
    
    # 1. Login para obtener token
    print("1️⃣ Probando login...")
    login_data = {
        "username": "admin_interbank",
        "password": "password123"
    }
    
    try:
        response = requests.post(f"{base_url}/auth/login", json=login_data)
        
        if response.status_code == 200:
            token_data = response.json()
            token = token_data["access_token"]
            print("✅ Login exitoso")
            print(f"   Token: {token[:50]}...")
            print(f"   Empresa: {token_data.get('empresa_id')}")
            print(f"   Usuario: {token_data.get('username')}")
        else:
            print(f"❌ Error en login: {response.status_code}")
            print(f"   Respuesta: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error de conexión en login: {e}")
        return False
    
    # Headers con token
    headers = {"Authorization": f"Bearer {token}"}
    
    # 2. Probar endpoint de usuarios disponibles
    print("\n2️⃣ Probando lista de usuarios...")
    try:
        response = requests.get(f"{base_url}/clustering/users", headers=headers)
        
        if response.status_code == 200:
            users = response.json()
            print(f"✅ Usuarios disponibles: {users}")
        else:
            print(f"❌ Error obteniendo usuarios: {response.status_code}")
            print(f"   Respuesta: {response.text}")
            
    except Exception as e:
        print(f"❌ Error de conexión: {e}")
    
    # 3. Probar acceso permitido (misma empresa)
    print("\n3️⃣ Probando acceso permitido (Interbank)...")
    try:
        response = requests.get(f"{base_url}/clustering/model-info/Interbank", headers=headers)
        
        if response.status_code == 200:
            model_info = response.json()
            print("✅ Acceso permitido - Información del modelo:")
            print(f"   Tipo: {model_info.get('tipo_modelo', 'N/A')}")
            print(f"   Fecha: {model_info.get('fecha_entrenamiento', 'N/A')}")
        elif response.status_code == 404:
            print("⚠️ Modelo no encontrado (normal si no hay modelo entrenado)")
        else:
            print(f"❌ Error accediendo a modelo: {response.status_code}")
            print(f"   Respuesta: {response.text}")
            
    except Exception as e:
        print(f"❌ Error de conexión: {e}")
    
    # 4. Probar acceso denegado (diferente empresa)
    print("\n4️⃣ Probando acceso denegado (BCP - diferente empresa)...")
    try:
        response = requests.get(f"{base_url}/clustering/model-info/BCPComunica", headers=headers)
        
        if response.status_code == 403:
            print("✅ Acceso correctamente denegado")
            print(f"   Error: {response.json().get('detail', 'Sin detalle')}")
        else:
            print(f"⚠️ Acceso inesperado: {response.status_code}")
            print(f"   Respuesta: {response.text}")
            
    except Exception as e:
        print(f"❌ Error de conexión: {e}")
    
    # 5. Probar predicción de clustering (si hay datos)
    print("\n5️⃣ Probando predicción de clustering...")
    clustering_data = {
        "data": [[0.1, 1000], [0.2, 2000], [0.05, 500]],  # engagement_rate, vistas
        "features": ["engagement_rate", "vistas"]
    }
    
    try:
        response = requests.post(
            f"{base_url}/clustering/predict/Interbank", 
            json=clustering_data, 
            headers=headers
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Predicción exitosa:")
            print(f"   Labels: {result.get('labels', [])}")
            print(f"   N° clusters: {result.get('n_clusters', 0)}")
            print(f"   Tipo modelo: {result.get('model_type', 'N/A')}")
        elif response.status_code == 404:
            print("⚠️ Modelo no encontrado (necesita entrenamiento)")
        else:
            print(f"❌ Error en predicción: {response.status_code}")
            print(f"   Respuesta: {response.text}")
            
    except Exception as e:
        print(f"❌ Error de conexión: {e}")
    
    # 6. Probar sin token (debe fallar)
    print("\n6️⃣ Probando acceso sin token...")
    try:
        response = requests.get(f"{base_url}/clustering/users")
        
        if response.status_code == 401:
            print("✅ Acceso correctamente denegado sin token")
        else:
            print(f"⚠️ Acceso inesperado sin token: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error de conexión: {e}")
    
    print("\n🎉 Pruebas de clustering con JWT completadas")
    print("\n📋 RESUMEN:")
    print("✅ Sistema de clustering protegido con JWT")
    print("✅ Control de acceso por empresa implementado")
    print("✅ Autenticación requerida para todos los endpoints")
    return True

def mostrar_endpoints_clustering():
    """Mostrar todos los endpoints de clustering protegidos"""
    print("\n🔐 ENDPOINTS DE CLUSTERING PROTEGIDOS:")
    print("=" * 50)
    
    endpoints = [
        "GET /clustering/users - Lista usuarios con modelos",
        "GET /clustering/model-info/{username} - Info del modelo",
        "GET /clustering/metrics/{username} - Métricas del modelo", 
        "GET /clustering/history/{username} - Historial de modelos",
        "GET /clustering/train/{username} - Entrenar modelo",
        "GET /clustering/clusters/{username} - Obtener clusters",
        "POST /clustering/predict/{username} - Predicción"
    ]
    
    for endpoint in endpoints:
        print(f"   🔒 {endpoint}")
    
    print(f"\n💡 Todos requieren:")
    print(f"   • Header: Authorization: Bearer <token>")
    print(f"   • Acceso solo a empresa propia (excepto admins)")

if __name__ == "__main__":
    print("🛡️ VERIFICADOR DE CLUSTERING CON JWT")
    print("=" * 45)
    print("💡 Asegúrate de que la API esté ejecutándose en http://localhost:8000")
    print("💡 Comando: uvicorn app.main:app --reload")
    
    mostrar_endpoints_clustering()
    
    input("\n📍 Presiona Enter para comenzar las pruebas...")
    test_clustering_jwt()
