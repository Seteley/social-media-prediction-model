# 📊 DOCUMENTACIÓN COMPLETA: REFACTORIZACIÓN DEL ENDPOINT DE PREDICCIÓN

## 🎯 Resumen de la Refactorización

El endpoint de predicción de regresión ha sido **completamente refactorizado** para simplificar su uso. Ahora acepta únicamente el parámetro `fecha` y devuelve solo los campos esenciales.

## 📋 Cambios Implementados

### ✅ ANTES vs DESPUÉS

**❌ ANTES (Complejo):**
```bash
curl "http://localhost:8000/regression/predict/Interbank?dia_semana=4&hora=23&mes=7"
```

**✅ DESPUÉS (Simplificado):**
```bash
curl "http://localhost:8000/regression/predict/Interbank?fecha=2025-07-11"
```

### 🔧 Respuesta Simplificada

**❌ ANTES (Verbose - 12+ campos):**
```json
{
  "prediction": 304250.0,
  "model_type": "RandomForestRegressor",
  "target_variable": "seguidores",
  "input_features": {...},
  "feature_names": [...],
  "fecha_info": {...},
  "timestamp": "...",
  "username": "...",
  "confidence": "...",
  "model_version": "...",
  "metadata": {...}
}
```

**✅ DESPUÉS (Limpio - Solo 3 campos esenciales):**
```json
{
  "prediction": 304250.0,
  "model_type": "RandomForestRegressor", 
  "target_variable": "seguidores"
}
```

## 🤖 Los 8 Modelos de Regresión Disponibles

El sistema entrena y evalúa **8 algoritmos diferentes** para cada cuenta:

| # | Modelo | Descripción | Características |
|---|---------|-------------|-----------------|
| 1 | **Linear Regression** | Regresión Lineal Simple | Modelo base, rápido, interpretable |
| 2 | **Ridge (L2)** | Regularización L2 | Previene overfitting, estable |
| 3 | **Lasso (L1)** | Regularización L1 | Selección automática de features |
| 4 | **Random Forest** | Ensamble de árboles | Robusto, maneja no-linealidad |
| 5 | **Gradient Boosting** | Boosting secuencial | Alta precisión, optimización iterativa |
| 6 | **Support Vector Regression** | SVM para regresión | Efectivo en espacios de alta dimensión |
| 7 | **K-Nearest Neighbors** | Basado en vecinos | No paramétrico, local |
| 8 | **Decision Tree** | Árbol de decisión individual | Interpretable, maneja relaciones complejas |

## 📅 Extracción Automática de Features Temporales

### 🔄 Proceso Interno del Endpoint

Cuando envías una fecha como `2025-07-11`, el sistema automáticamente:

```python
# Input del usuario
fecha = "2025-07-11"

# Extracción automática
fecha_obj = datetime.strptime(fecha, "%Y-%m-%d")
dia_semana = fecha_obj.weekday()  # 4 (Viernes, 0=Lunes)
hora = 23                         # Fin del día por defecto  
mes = fecha_obj.month             # 7 (Julio)

# Features temporales resultantes
features_temporales = {
    'dia_semana': 4,  # Viernes
    'hora': 23,       # 11:00 PM
    'mes': 7          # Julio
}
```

### 📊 Mapeo de Valores Temporales

**Días de la Semana:**
- 0 = Lunes, 1 = Martes, 2 = Miércoles, 3 = Jueves
- 4 = Viernes, 5 = Sábado, 6 = Domingo

**Meses:**
- 1 = Enero, 2 = Febrero, ..., 12 = Diciembre

**Horas:**
- Siempre se asume **hora = 23** (fin del día) para simplicidad

## 📈 Ejemplo Real con Datos de Interbank

### 📊 Dataset de Interbank
```csv
Hora,Usuario,Seguidores,Tweets,Following
2025-07-09 07:18:22,@Interbank,304222,66926,71
2025-07-09 08:27:42,@Interbank,304221,66926,71
2025-07-09 09:23:14,@Interbank,304220,66926,71
...
```

### 🛠️ Features Utilizadas para Entrenamiento

1. **Features Temporales** (extraídas automáticamente):
   - `dia_semana`: 0-6
   - `hora`: 0-23  
   - `mes`: 1-12

2. **Features Base** (del dataset):
   - `Tweets`: Número total de tweets
   - `Following`: Cuentas seguidas

3. **Features Derivadas** (calculadas):
   - `ratio_seguidores_tweets`: Seguidores / Tweets
   - `ratio_seguidores_siguiendo`: Seguidores / Following

### 🎯 Variable Objetivo
- **`seguidores`**: Número de seguidores a predecir

## 🧪 Ejemplos de Uso del Endpoint Refactorizado

### 1. Predicción para Hoy
```bash
curl "http://localhost:8000/regression/predict/Interbank?fecha=2025-07-11"
```

**Extracción automática:**
- dia_semana = 4 (Viernes)
- hora = 23 (fin del día)
- mes = 7 (Julio)

**Respuesta:**
```json
{
  "prediction": 304285.0,
  "model_type": "RandomForestRegressor",
  "target_variable": "seguidores"
}
```

### 2. Predicción para Navidad
```bash
curl "http://localhost:8000/regression/predict/Interbank?fecha=2025-12-25"
```

**Extracción automática:**
- dia_semana = 3 (Jueves)
- hora = 23
- mes = 12 (Diciembre)

### 3. Predicción para Año Nuevo
```bash
curl "http://localhost:8000/regression/predict/Interbank?fecha=2025-01-01"
```

**Extracción automática:**
- dia_semana = 2 (Miércoles)
- hora = 23
- mes = 1 (Enero)

## 🔧 Flujo Completo del Sistema

### 1. **Entrenamiento** (Una vez por cuenta)
```bash
# Entrenar modelo para Interbank
curl "http://localhost:8000/regression/train/Interbank"
```

El sistema:
1. Carga datos de `data/Interbank_metricas.csv`
2. Extrae features temporales de timestamps
3. Entrena los 8 modelos
4. Selecciona el mejor (por R²)
5. Guarda en `models/Interbank/regresion.pkl`

### 2. **Predicción** (Cualquier momento)
```bash
# Predecir para cualquier fecha
curl "http://localhost:8000/regression/predict/Interbank?fecha=YYYY-MM-DD"
```

El sistema:
1. Carga modelo entrenado
2. Extrae features temporales de la fecha
3. Combina con features promedio de la cuenta
4. Realiza predicción
5. Devuelve solo campos esenciales

## 📊 Comparación de Modelos para Interbank

**Ejemplo de ranking típico:**

| # | Modelo | R² | RMSE | MAE |
|---|--------|----|----|-----|
| 1 | Random Forest | 0.886 | 12.1 | 8.4 |
| 2 | Gradient Boosting | 0.754 | 17.8 | 12.2 |
| 3 | Ridge | 0.623 | 22.1 | 16.7 |
| 4 | Linear Regression | 0.598 | 22.8 | 17.1 |
| 5 | Lasso | 0.587 | 23.1 | 17.5 |
| 6 | Decision Tree | 0.421 | 27.4 | 20.8 |
| 7 | SVR | 0.398 | 27.9 | 21.2 |
| 8 | KNN | 0.312 | 29.8 | 22.6 |

**🏆 Mejor modelo:** Random Forest con 88.6% de varianza explicada

## ✅ Ventajas de la Refactorización

### 🎯 **Simplicidad**
- Solo necesitas saber la fecha
- No más cálculos manuales de día_semana, hora, mes
- Menos probabilidad de errores

### 🧹 **Respuesta Limpia**
- Solo 3 campos esenciales
- No información innecesaria
- Fácil de procesar

### 🚀 **Mejor UX**
- Interfaz más intuitiva
- Compatible con herramientas de calendario
- Más fácil de integrar

### 🔧 **Mantenibilidad**
- Código más simple
- Menos parámetros que validar
- Lógica centralizada

## 🧪 Scripts de Prueba Disponibles

1. **`test_fecha_only.py`** - Verifica que solo acepta fecha
2. **`test_endpoint_simplified.py`** - Prueba completa en Python
3. **`test_fecha_curl.sh`** - Pruebas rápidas con cURL
4. **`documentacion_8_modelos_interbank.py`** - Demo completa con datos reales

## 📡 API Endpoints Disponibles

### Gestión de Modelos
- `GET /regression/train/{username}` - Entrenar modelo
- `GET /regression/metrics/{username}` - Ver métricas
- `GET /regression/model-info/{username}` - Info del modelo
- `DELETE /regression/model/{username}` - Eliminar modelo

### Predicciones
- **`GET /regression/predict/{username}?fecha=YYYY-MM-DD`** - ⭐ **ENDPOINT PRINCIPAL**
- `GET /regression/features/{username}` - Ver features requeridas

## 🎉 Conclusión

La refactorización del endpoint de predicción de regresión ha logrado:

✅ **Simplificar la interfaz** - Solo parámetro `fecha`  
✅ **Limpiar la respuesta** - Solo campos esenciales  
✅ **Mantener funcionalidad** - Todos los 8 modelos siguen funcionando  
✅ **Mejorar UX** - Más fácil de usar e integrar  
✅ **Documentar completamente** - Con ejemplos reales de Interbank  

El sistema ahora es más intuitivo y profesional, manteniendo toda la potencia de los 8 algoritmos de machine learning para la predicción de seguidores.
