#!/bin/bash
"""
Script para probar el flujo completo de JWT
"""

echo "🔐 PRUEBA COMPLETA DEL SISTEMA JWT"
echo "=================================="

echo ""
echo "1️⃣ Obteniendo token JWT..."
RESPONSE=$(curl -s -X POST "http://localhost:8000/auth/login" \
   -H "Content-Type: application/json" \
   -d '{"username": "admin_interbank", "password": "password123"}')

echo "Respuesta del login:"
echo "$RESPONSE" | python -m json.tool 2>/dev/null || echo "$RESPONSE"

# Extraer el token
TOKEN=$(echo "$RESPONSE" | python -c "import sys, json; data=json.load(sys.stdin); print(data['access_token'])" 2>/dev/null)

if [ -z "$TOKEN" ]; then
    echo "❌ Error: No se pudo obtener el token"
    exit 1
fi

echo ""
echo "✅ Token obtenido: ${TOKEN:0:50}..."

echo ""
echo "2️⃣ Probando acceso autorizado (misma empresa)..."
curl -s -H "Authorization: Bearer $TOKEN" \
   "http://localhost:8000/regression/predict/Interbank?fecha=2025-07-11" | \
   python -m json.tool 2>/dev/null || echo "Error en respuesta"

echo ""
echo "3️⃣ Probando acceso denegado (diferente empresa)..."
curl -s -H "Authorization: Bearer $TOKEN" \
   "http://localhost:8000/regression/predict/BCPComunica?fecha=2025-07-11" | \
   python -m json.tool 2>/dev/null || echo "Error en respuesta"

echo ""
echo "4️⃣ Probando sin autenticación..."
curl -s "http://localhost:8000/regression/predict/Interbank?fecha=2025-07-11" | \
   python -m json.tool 2>/dev/null || echo "Error en respuesta"

echo ""
echo "🎉 Pruebas completadas!"
