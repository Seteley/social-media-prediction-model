# API de Regresión - Social Media Analytics

## 📋 Descripción

API RESTful para entrenar y usar modelos de regresión para predicción del número de seguidores y otras métricas de redes sociales.

## 🚀 Uso

### Iniciar el servidor
```bash
python run_api.py
```

La API estará disponible en: `http://localhost:8000`

### Documentación interactiva
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

## 📊 Endpoints de Regresión

### 🔍 Gestión de Modelos (`/regression`)

#### `GET /regression/users`
Lista usuarios con modelos de regresión disponibles.

**Respuesta:**
```json
["BanBif", "Interbank", "BCPComunica"]
```

#### `GET /regression/available-accounts`
Lista todas las cuentas disponibles en la base de datos.

**Respuesta:**
```json
{
  "accounts": ["BanBif", "Interbank", "BCPComunica", "..."],
  "total": 8
}
```

#### `GET /regression/metrics/{username}`
Obtiene métricas detalladas del modelo de un usuario.

**Ejemplo:** `GET /regression/metrics/BanBif`

**Respuesta:**
```json
{
  "account_name": "BanBif",
  "target_variable": "seguidores",
  "best_model": {
    "model_name": "Random Forest",
    "r2_score": 0.886,
    "rmse": 2.21,
    "mae": 1.44
  },
  "features_used": ["engagement_rate", "total_tweets", "actividad_publicacion"],
  "training_samples": 13,
  "test_samples": 4
}
```

#### `GET /regression/train/{username}?target_variable=seguidores&test_size=0.2`
Entrena modelo de regresión para un usuario usando parámetros de URL.

**Parámetros de URL:**
- `target_variable` (opcional): Variable objetivo (default: "seguidores")
- `test_size` (opcional): Proporción de datos para test (default: 0.2)
- `random_state` (opcional): Semilla aleatoria (default: 42)

**Ejemplo:** `GET /regression/train/BanBif?target_variable=seguidores&test_size=0.2`

**Respuesta:**
```json
{
  "message": "Regression model trained successfully for BanBif",
  "best_model": "Random Forest",
  "metrics": {
    "r2_score": 0.886,
    "rmse": 2.21,
    "mae": 1.44
  },
  "model_path": "models/BanBif/regresion.pkl",
  "features_used": ["engagement_rate", "total_tweets"],
  "training_samples": 13,
  "test_samples": 4
}
```

#### `GET /regression/compare-models/{username}`
Compara todos los modelos entrenados para un usuario.

**Respuesta:**
```json
{
  "account_name": "BanBif",
  "target_variable": "seguidores",
  "total_models": 8,
  "best_model": { "model_name": "Random Forest", "r2_score": 0.886 },
  "model_comparison": [
    { "Modelo": "Random Forest", "R²": 0.886, "RMSE": 2.21 },
    { "Modelo": "Gradient Boosting", "R²": 0.753, "RMSE": 3.24 }
  ]
}
```

#### `DELETE /regression/model/{username}`
Elimina modelo y métricas de un usuario.

### 🎯 Predicciones (`/regression`)

#### `GET /regression/predict/{username}?fecha=YYYY-MM-DD`
Realiza predicción usando fecha (método recomendado y más simple).

**Parámetro principal:**
- `fecha`: Fecha en formato YYYY-MM-DD (ej: 2025-07-11)
  - Se asume automáticamente hora 23:00 (fin del día)
  - Se extrae automáticamente: día de la semana y mes

**Parámetros alternativos (solo si no se usa fecha):**
- `dia_semana`: Día de la semana (0=Lunes, 6=Domingo)
- `hora`: Hora del día (0-23, default: 23)
- `mes`: Mes del año (1-12)

**Ejemplo recomendado:** `GET /regression/predict/BanBif?fecha=2025-07-11`

**Ejemplo alternativo:** `GET /regression/predict/BanBif?dia_semana=4&hora=23&mes=7`

**Respuesta:**
```json
{
  "prediction": 4363.2,
  "model_type": "RandomForestRegressor",
  "target_variable": "seguidores",
  "input_features": {
    "engagement_rate": 0.05,
    "total_tweets": 1000,
    "actividad_publicacion": 5
  },
  "timestamp": "2025-07-11T15:30:45",
  "username": "BanBif"
}
```

#### `GET /regression/features/{username}`
Obtiene las features requeridas para hacer predicciones.

**Respuesta:**
```json
{
  "username": "BanBif",
  "required_features": ["engagement_rate", "total_tweets", "actividad_publicacion"],
  "target_variable": "seguidores",
  "model_type": "RandomForestRegressor",
  "example_url": "/regression/predict/BanBif?engagement_rate=0.0&total_tweets=0.0&actividad_publicacion=0.0..."
}
```

#### `POST /regression/predict-batch`
Realiza predicciones múltiples (mantiene compatibilidad).

**Body:**
```json
{
  "username": "BanBif",
  "input_data": {
    "engagement_rate": 0.05,
    "total_tweets": 1000,
    "actividad_publicacion": 5
  }
}
```

**Respuesta:**
```json
{
  "prediction": 4363.2,
  "model_type": "RandomForestRegressor",
  "target_variable": "seguidores",
  "input_features": {
    "engagement_rate": 0.05,
    "total_tweets": 1000,
    "actividad_publicacion": 5
  },
  "timestamp": "2025-07-11T15:30:45"
}
```

#### `GET /regression/model-info/{username}`
Obtiene información del modelo guardado.

## 🔧 Estructura de Archivos

```
models/
├── BanBif/
│   └── regresion.pkl     # Modelo entrenado
└── Interbank/
    └── regresion.pkl

metricas/
├── BanBif.json          # Métricas y reportes
└── Interbank.json
```

## 📈 Variables Soportadas

- **seguidores** (por defecto): Número de seguidores
- **total_tweets**: Número total de tweets
- **siguiendo**: Cuentas seguidas
- **publicaciones_dia**: Frecuencia de publicaciones
- Cualquier variable numérica de la tabla `metrica`

## 🧪 Ejemplo de Uso con cURL

```bash
# Listar usuarios disponibles
curl -X GET "http://localhost:8000/regression/users"

# Entrenar modelo para BanBif
curl -X GET "http://localhost:8000/regression/train/BanBif?target_variable=seguidores"

# Obtener features requeridas
curl -X GET "http://localhost:8000/regression/features/BanBif"

# Obtener métricas
curl -X GET "http://localhost:8000/regression/metrics/BanBif"

# 🎯 PREDICCIÓN USANDO FECHA (RECOMENDADO)
# Predicción para hoy (2025-07-11)
curl -X GET "http://localhost:8000/regression/predict/BanBif?fecha=2025-07-11"

# Predicción para una fecha específica
curl -X GET "http://localhost:8000/regression/predict/BanBif?fecha=2025-12-25"

# Predicción para mañana
curl -X GET "http://localhost:8000/regression/predict/BanBif?fecha=2025-07-12"

# MÉTODO ALTERNATIVO: Parámetros individuales
curl -X GET "http://localhost:8000/regression/predict/BanBif?dia_semana=4&hora=23&mes=7"
```

## 🔍 Troubleshooting

### Error 404: Model not found
- Asegúrate de que el modelo esté entrenado: `POST /regression/train/{username}`
- Verifica que el archivo `models/{username}/regresion.pkl` existe

### Error 400: Missing features
- Verifica que todas las features requeridas estén en el input
- Consulta `GET /regression/model-info/{username}` para ver features necesarias

### Error 500: Training error
- Verifica que la cuenta existe: `GET /regression/available-accounts`
- Revisa que haya suficientes datos en la base de datos
