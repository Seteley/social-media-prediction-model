#!/bin/bash

# Script para probar el endpoint de predicción simplificado
# Usa cURL para hacer peticiones HTTP

echo "🚀 Probando endpoint de predicción simplificado..."
echo "=============================================="

# Test 1: Predicción usando parámetro fecha
echo ""
echo "🧪 Test 1: Predicción usando parámetro 'fecha'"
echo "URL: http://localhost:8000/regression/predict/BanBif?fecha=2025-07-11"
echo ""

curl -X GET "http://localhost:8000/regression/predict/BanBif?fecha=2025-07-11" \
     -H "accept: application/json" \
     -w "\nStatus Code: %{http_code}\n" \
     2>/dev/null | jq '.' 2>/dev/null || echo "Respuesta recibida (sin formatear JSON)"

echo ""
echo "=============================================="

# Test 2: Predicción usando parámetros individuales  
echo ""
echo "🧪 Test 2: Predicción usando parámetros individuales"
echo "URL: http://localhost:8000/regression/predict/BanBif?dia_semana=4&mes=7&hora=15"
echo ""

curl -X GET "http://localhost:8000/regression/predict/BanBif?dia_semana=4&mes=7&hora=15" \
     -H "accept: application/json" \
     -w "\nStatus Code: %{http_code}\n" \
     2>/dev/null | jq '.' 2>/dev/null || echo "Respuesta recibida (sin formatear JSON)"

echo ""
echo "=============================================="

# Test 3: Información del modelo
echo ""
echo "🧪 Test 3: Información del modelo"
echo "URL: http://localhost:8000/regression/model-info/BanBif"
echo ""

curl -X GET "http://localhost:8000/regression/model-info/BanBif" \
     -H "accept: application/json" \
     -w "\nStatus Code: %{http_code}\n" \
     2>/dev/null | jq '.' 2>/dev/null || echo "Respuesta recibida (sin formatear JSON)"

echo ""
echo "=============================================="
echo "✅ Pruebas completadas!"
echo ""
echo "📋 Verificaciones esperadas:"
echo "   ✓ La respuesta de predicción debe contener solo 3 campos:"
echo "     - prediction (número)"
echo "     - model_type (string)"  
echo "     - target_variable (string)"
echo "   ✓ NO debe contener campos como: input_features, timestamp, username, fecha_info"
echo "   ✓ Status code debe ser 200 para requests válidos"
