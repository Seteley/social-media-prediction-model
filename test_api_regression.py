#!/usr/bin/env python3
"""
Script para probar los endpoints de regresión con parámetros de URL
"""

import requests
import json
from pathlib import Path

# Configuración
API_BASE = "http://localhost:8000"
TEST_USERNAME = "BanBif"  # Usuario con modelo entrenado

def test_api_endpoints():
    """Prueba los endpoints principales de la API."""
    
    print("🧪 Probando API de Regresión con parámetros de URL")
    print("=" * 60)
    
    # 1. Listar usuarios disponibles
    print("\n1️⃣ Listando usuarios con modelos disponibles...")
    try:
        response = requests.get(f"{API_BASE}/regression/users")
        if response.status_code == 200:
            users = response.json()
            print(f"✅ Usuarios disponibles: {users}")
        else:
            print(f"❌ Error: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ Error de conexión: {e}")
        return
    
    # 2. Obtener features requeridas
    print(f"\n2️⃣ Obteniendo features requeridas para {TEST_USERNAME}...")
    try:
        response = requests.get(f"{API_BASE}/regression/features/{TEST_USERNAME}")
        if response.status_code == 200:
            features_info = response.json()
            print(f"✅ Features requeridas: {features_info['required_features']}")
            print(f"🎯 Variable objetivo: {features_info['target_variable']}")
            print(f"🤖 Tipo de modelo: {features_info['model_type']}")
        else:
            print(f"❌ Error: {response.status_code} - {response.text}")
            return
    except Exception as e:
        print(f"❌ Error: {e}")
        return
    
    # 3. Hacer predicción con fecha (método recomendado)
    print(f"\n3️⃣ Haciendo predicción usando fecha...")
    
    from datetime import datetime, timedelta
    
    # Predicción para hoy
    fecha_hoy = datetime.now().strftime("%Y-%m-%d")
    prediction_url = f"{API_BASE}/regression/predict/{TEST_USERNAME}?fecha={fecha_hoy}"
    
    print(f"📡 URL: {prediction_url}")
    print(f"📅 Fecha: {fecha_hoy} (asume hora 23:00)")
    
    try:
        response = requests.get(prediction_url)
        if response.status_code == 200:
            prediction = response.json()
            print(f"✅ Predicción exitosa:")
            print(f"   🎯 Predicción: {prediction['prediction']:.2f} {prediction['target_variable']}")
            print(f"   🤖 Modelo: {prediction['model_type']}")
            print(f"   📊 Features usadas: {prediction['feature_names']}")
            print(f"   📅 Info de fecha:")
            fecha_info = prediction.get('fecha_info', {})
            print(f"      • Día: {fecha_info.get('dia_nombre', 'N/A')} (dia_semana={fecha_info.get('dia_semana_calculado', 'N/A')})")
            print(f"      • Mes: {fecha_info.get('mes_nombre', 'N/A')} (mes={fecha_info.get('mes_calculado', 'N/A')})")
            print(f"      • Hora asumida: {fecha_info.get('hora_asumida', 'N/A')}:00")
        else:
            print(f"❌ Error: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # 3b. Predicción para una fecha futura
    print(f"\n3️⃣b Predicción para fecha futura...")
    fecha_futura = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")
    future_url = f"{API_BASE}/regression/predict/{TEST_USERNAME}?fecha={fecha_futura}"
    
    print(f"📡 URL: {future_url}")
    print(f"📅 Fecha futura: {fecha_futura}")
    
    try:
        response = requests.get(future_url)
        if response.status_code == 200:
            prediction = response.json()
            print(f"✅ Predicción futura exitosa:")
            print(f"   🎯 Predicción: {prediction['prediction']:.2f} {prediction['target_variable']}")
            fecha_info = prediction.get('fecha_info', {})
            print(f"   � Para: {fecha_info.get('dia_nombre', 'N/A')}, {fecha_info.get('mes_nombre', 'N/A')}")
        else:
            print(f"❌ Error: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # 4. Obtener métricas del modelo
    print(f"\n4️⃣ Obteniendo métricas del modelo...")
    try:
        response = requests.get(f"{API_BASE}/regression/metrics/{TEST_USERNAME}")
        if response.status_code == 200:
            metrics = response.json()
            best_model = metrics.get('best_model', {})
            print(f"✅ Métricas del modelo:")
            print(f"   🏆 Mejor modelo: {best_model.get('model_name', 'N/A')}")
            print(f"   📊 R²: {best_model.get('r2_score', 0):.3f}")
            print(f"   📉 RMSE: {best_model.get('rmse', 0):.2f}")
            print(f"   📈 MAE: {best_model.get('mae', 0):.2f}")
        else:
            print(f"❌ Error: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print(f"\n🎉 Pruebas completadas!")

if __name__ == "__main__":
    # Verificar que el modelo existe
    model_path = Path(f"models/{TEST_USERNAME}/regresion.pkl")
    if not model_path.exists():
        print(f"❌ Modelo no encontrado: {model_path}")
        print(f"💡 Ejecuta primero: python -m scripts.run_individual --account {TEST_USERNAME}")
        exit(1)
    
    print(f"✅ Modelo encontrado: {model_path}")
    print("🚀 Asegúrate de que la API esté ejecutándose en: http://localhost:8000")
    print("💡 Ejecuta: python run_api.py")
    print()
    
    input("Presiona Enter para continuar con las pruebas...")
    test_api_endpoints()
