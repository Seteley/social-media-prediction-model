# 📡 EJEMPLOS cURL: Todos los Endpoints de Regresión

## 🎯 Endpoints de Predicción

### 1. Predicción Individual con Fecha
```bash
curl -X GET "http://localhost:8000/regression/predict/BanBif?fecha=2025-07-11" \
     -H "accept: application/json"
```

### 2. Predicción Individual con Parámetros
```bash
curl -X GET "http://localhost:8000/regression/predict/BanBif?dia_semana=4&mes=7&hora=15" \
     -H "accept: application/json"
```

### 3. Predicción Batch (POST)
```bash
curl -X POST "http://localhost:8000/regression/predict-batch" \
     -H "accept: application/json" \
     -H "Content-Type: application/json" \
     -d '{
       "username": "BanBif",
       "data": [
         {"dia_semana": 0, "hora": 12, "mes": 7},
         {"dia_semana": 1, "hora": 18, "mes": 8},
         {"dia_semana": 2, "hora": 9, "mes": 9}
       ]
     }'
```

## 📊 Endpoints de Información

### 4. Información del Modelo
```bash
curl -X GET "http://localhost:8000/regression/model-info/BanBif" \
     -H "accept: application/json"
```

### 5. Features Requeridas
```bash
curl -X GET "http://localhost:8000/regression/features/BanBif" \
     -H "accept: application/json"
```

## 🛠️ Endpoints de Gestión

### 6. Lista de Usuarios con Modelos
```bash
curl -X GET "http://localhost:8000/regression/users" \
     -H "accept: application/json"
```

### 7. Cuentas Disponibles en Base de Datos
```bash
curl -X GET "http://localhost:8000/regression/available-accounts" \
     -H "accept: application/json"
```

### 8. Métricas del Modelo
```bash
curl -X GET "http://localhost:8000/regression/metrics/BanBif" \
     -H "accept: application/json"
```

### 9. Historial de Entrenamientos
```bash
curl -X GET "http://localhost:8000/regression/history/BanBif" \
     -H "accept: application/json"
```

### 10. Comparar Modelos
```bash
curl -X GET "http://localhost:8000/regression/compare-models/BanBif" \
     -H "accept: application/json"
```

## 🚀 Endpoint de Entrenamiento

### 11. Entrenar Modelo (POST) - ¡MEJORADO!
```bash
curl -X POST "http://localhost:8000/regression/train" \
     -H "accept: application/json" \
     -H "Content-Type: application/json" \
     -d '{
       "username": "BanBif",
       "target_variable": "seguidores",
       "test_size": 0.2,
       "random_state": 42
     }'
```

## 🗑️ Endpoint de Eliminación

### 12. Eliminar Modelo
```bash
curl -X DELETE "http://localhost:8000/regression/model/BanBif" \
     -H "accept: application/json"
```

## 🔍 Ejemplos de Respuestas

### Predicción Individual (Simplificada)
```json
{
  "prediction": 12500.0,
  "model_type": "RandomForestRegressor",
  "target_variable": "seguidores"
}
```

### Predicción Batch
```json
{
  "predictions": [12500.0, 13200.0, 11800.0],
  "model_type": "RandomForestRegressor",
  "target_variable": "seguidores"
}
```

### Información del Modelo
```json
{
  "username": "BanBif",
  "target_variable": "seguidores",
  "model_type": "RandomForestRegressor",
  "feature_names": ["dia_semana", "hora", "mes"],
  "model_id": "BanBif_regresion_2025",
  "timestamp": "2025-07-11T10:30:00",
  "results_count": 5
}
```

### Entrenamiento Exitoso
```json
{
  "message": "Regression model trained successfully for BanBif",
  "best_model": "RandomForestRegressor",
  "metrics": {
    "r2_score": 0.85,
    "rmse": 2500.0,
    "mae": 1800.0,
    "cv_r2": 0.82
  },
  "model_path": "models/BanBif/regresion.pkl",
  "target_variable": "seguidores",
  "features_used": ["dia_semana", "hora", "mes"],
  "training_samples": 800,
  "test_samples": 200
}
```

## ⚠️ Ejemplos de Errores

### Usuario No Encontrado (404)
```bash
curl -X GET "http://localhost:8000/regression/predict/UsuarioInexistente?fecha=2025-07-11"
```

### Parámetros Inválidos (400)
```bash
curl -X GET "http://localhost:8000/regression/predict/BanBif?dia_semana=8&mes=13"
```

### Fecha Inválida (400)
```bash
curl -X GET "http://localhost:8000/regression/predict/BanBif?fecha=2025-13-45"
```

## 💡 Notas Importantes

1. **Predicción Simplificada**: Solo devuelve 3 campos esenciales
2. **Entrenamiento mejorado**: Ahora es POST (buenas prácticas REST)
3. **Validaciones añadidas**: Rangos de parámetros validados
4. **Compatibilidad**: Soporta fecha o parámetros individuales
5. **Manejo de errores**: Mensajes claros y códigos HTTP apropiados

## 🧪 Ejecutar Pruebas Automatizadas

```bash
# Prueba rápida con Python
python test_all_regression_endpoints.py

# Prueba rápida con script bash
bash test_curl.sh
```
