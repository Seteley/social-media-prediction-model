#!/bin/bash

echo "🧪 VERIFICACIÓN RÁPIDA: Endpoint solo acepta fechas"
echo "================================================="

# Test 1: Fecha válida (debería funcionar)
echo ""
echo "✅ Test 1: Fecha válida"
echo "URL: http://localhost:8000/regression/predict/Interbank?fecha=2025-07-11"
curl -s "http://localhost:8000/regression/predict/Interbank?fecha=2025-07-11" | jq '.' 2>/dev/null || echo "Sin formato JSON o servidor no disponible"

# Test 2: Parámetros individuales (debería fallar)
echo ""
echo "❌ Test 2: Parámetros individuales (deberían fallar)"
echo "URL: http://localhost:8000/regression/predict/Interbank?dia_semana=2&mes=10"
curl -s "http://localhost:8000/regression/predict/Interbank?dia_semana=2&mes=10" | jq '.' 2>/dev/null || echo "Sin formato JSON o servidor no disponible"

# Test 3: Sin parámetros (debería fallar)
echo ""
echo "❌ Test 3: Sin parámetros (debería fallar)"
echo "URL: http://localhost:8000/regression/predict/Interbank"
curl -s "http://localhost:8000/regression/predict/Interbank" | jq '.' 2>/dev/null || echo "Sin formato JSON o servidor no disponible"

echo ""
echo "================================================="
echo "✅ Resultados esperados:"
echo "   - Test 1: Respuesta con prediction, model_type, target_variable"
echo "   - Test 2: Error (parámetros no reconocidos)"
echo "   - Test 3: Error (fecha requerida)"
