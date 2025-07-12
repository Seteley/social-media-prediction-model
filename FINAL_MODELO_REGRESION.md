# FINAL_MODELO_REGRESION: Documentación Completa de Modelos de Regresión

## 📊 Documentación Técnica de los 8 Modelos de Regresión - TwiTrack API

**Versión:** 3.0.0  
**Fecha:** Julio 2025  
**Sistema:** TwiTrack - Análisis Predictivo de Redes Sociales

---

## 📋 Índice

1. [Información General](#información-general)
2. [Configuración de Entrada](#configuración-de-entrada)
3. [Modelos de Regresión](#modelos-de-regresión)
4. [Métricas de Evaluación](#métricas-de-evaluación)
5. [Selección del Mejor Modelo](#selección-del-mejor-modelo)
6. [Salidas del Sistema](#salidas-del-sistema)
7. [Ejemplo de Uso](#ejemplo-de-uso)

---

## 🎯 Información General

### **Objetivo**
Predicción del número de seguidores en redes sociales utilizando métricas de engagement temporal para cuentas del sector financiero peruano.

### **Tipo de Problema**
Regresión supervisada multi-modelo con selección automática del mejor algoritmo.

### **Variable Objetivo**
- **Target:** `seguidores` (número de seguidores de la cuenta)

### **Features de Entrada**
- **dia_semana:** Día de la semana (0-6, donde 0=Lunes)
- **hora:** Hora del día (0-23)
- **mes:** Mes del año (1-12)

---

## ⚙️ Configuración de Entrada

### **Preparación de Datos**
```python
# División de datos
test_size: 0.2 (20% para prueba)
random_state: 42 (reproducibilidad)
cv_folds: 5 (validación cruzada)

# Preprocesamiento
fillna: 0 (valores faltantes)
scaling: No requerido (features numéricas simples)
```

### **Validación de Entrada**
- Verificación de variable objetivo en dataset
- Filtrado de features disponibles
- Manejo automático de valores faltantes
- Validación de dimensiones mínimas

---

## 🤖 Modelos de Regresión

### **1. Regresión Lineal Simple**
```python
Modelo: LinearRegression
Parámetros: {}
Descripción: Regresión Lineal Simple

Características:
- Modelo baseline más simple
- Relación lineal entre features y target
- Interpretabilidad máxima
- Sin regularización

Ventajas:
- Rápido entrenamiento e inferencia
- Fácil interpretación de coeficientes
- Estable y robusto

Desventajas:
- Asume relaciones lineales
- Sensible a outliers
- No maneja interacciones complejas
```

### **2. Regresión Ridge (L2)**
```python
Modelo: Ridge
Parámetros: {
    'alpha': 1.0,
    'random_state': 42
}
Descripción: Regresión Ridge (L2)

Características:
- Regularización L2 (penaliza coeficientes grandes)
- Reduce overfitting
- Mantiene todas las features

Ventajas:
- Mejor generalización que regresión lineal
- Maneja multicolinealidad
- Estable numéricamente

Desventajas:
- No elimina features irrelevantes
- Requiere tuning de alpha
- Menos interpretable que lineal simple
```

### **3. Regresión Lasso (L1)**
```python
Modelo: Lasso
Parámetros: {
    'alpha': 1.0,
    'random_state': 42
}
Descripción: Regresión Lasso (L1)

Características:
- Regularización L1 (puede eliminar features)
- Selección automática de features
- Solución sparse

Ventajas:
- Selección automática de features
- Reduce dimensionalidad
- Interpretable (coeficientes cero)

Desventajas:
- Puede eliminar features importantes
- Inestable con features correlacionadas
- Requiere tuning de alpha
```

### **4. Random Forest**
```python
Modelo: RandomForestRegressor
Parámetros: {
    'n_estimators': 100,
    'random_state': 42
}
Descripción: Random Forest

Características:
- Ensemble de árboles de decisión
- Bootstrap aggregating (bagging)
- Maneja interacciones no lineales

Ventajas:
- Excelente para relaciones no lineales
- Robusto a outliers
- No requiere scaling de features
- Proporciona importancia de features

Desventajas:
- Menos interpretable
- Puede hacer overfitting con pocos datos
- Mayor tiempo de entrenamiento
```

### **5. Gradient Boosting**
```python
Modelo: GradientBoostingRegressor
Parámetros: {
    'n_estimators': 100,
    'random_state': 42
}
Descripción: Gradient Boosting

Características:
- Ensemble secuencial de árboles débiles
- Optimización iterativa de errores
- Alta capacidad predictiva

Ventajas:
- Excelente performance predictiva
- Maneja interacciones complejas
- Robusto a outliers

Desventajas:
- Propenso a overfitting
- Lento entrenamiento
- Muchos hiperparámetros
- Menos interpretable
```

### **6. Support Vector Regression (SVR)**
```python
Modelo: SVR
Parámetros: {
    'kernel': 'rbf',
    'C': 1.0
}
Descripción: Support Vector Regression

Características:
- Mapeo a espacio de alta dimensión
- Kernel RBF para relaciones no lineales
- Tolerancia a errores con epsilon

Ventajas:
- Eficaz en alta dimensión
- Versátil (diferentes kernels)
- Robusto a outliers

Desventajas:
- Lento con datasets grandes
- Requiere scaling de features
- Difícil interpretación
- Sensible a hiperparámetros
```

### **7. K-Nearest Neighbors (KNN)**
```python
Modelo: KNeighborsRegressor
Parámetros: {
    'n_neighbors': 5
}
Descripción: K-Nearest Neighbors

Características:
- Aprendizaje basado en instancias
- No paramétrico
- Predicción por promedio de vecinos

Ventajas:
- Simple y intuitivo
- No asume distribución de datos
- Funciona bien con patrones locales

Desventajas:
- Sensible a curse of dimensionality
- Costoso computacionalmente en predicción
- Sensible a escala de features
- Requiere mucha memoria
```

### **8. Árbol de Decisión**
```python
Modelo: DecisionTreeRegressor
Parámetros: {
    'random_state': 42
}
Descripción: Árbol de Decisión

Características:
- Estructura jerárquica de decisiones
- Splits binarios por feature
- Máxima interpretabilidad

Ventajas:
- Extremadamente interpretable
- Maneja relaciones no lineales
- No requiere scaling
- Selección automática de features

Desventajas:
- Propenso a overfitting
- Inestable (alta varianza)
- Sesgado hacia features con más valores
- Puede crear reglas muy específicas
```

---

## 📈 Métricas de Evaluación

### **Métricas Calculadas por Modelo**

```python
Métricas Primarias:
- RMSE: Raíz del Error Cuadrático Medio
- MAE: Error Absoluto Medio  
- MedAE: Mediana del Error Absoluto
- R²: Coeficiente de Determinación
- EVS: Varianza Explicada
- CV_R²_mean: R² promedio en validación cruzada
- CV_R²_std: Desviación estándar de R² en CV
- MAPE: Error Porcentual Absoluto Medio
```

### **Interpretación de Métricas**

**RMSE (Root Mean Square Error)**
- Unidades: Mismas que variable objetivo (seguidores)
- Interpretación: Error promedio en predicciones
- Objetivo: Minimizar
- Sensible a outliers

**MAE (Mean Absolute Error)**
- Unidades: Mismas que variable objetivo
- Interpretación: Error absoluto promedio
- Objetivo: Minimizar
- Robusto a outliers

**R² (Coefficient of Determination)**
- Rango: [0, 1] (puede ser negativo si el modelo es muy malo)
- Interpretación: Porcentaje de varianza explicada
- Objetivo: Maximizar
- R² = 1 significa predicción perfecta

**MAPE (Mean Absolute Percentage Error)**
- Unidades: Porcentaje
- Interpretación: Error porcentual promedio
- Objetivo: Minimizar
- Útil para comparar entre diferentes escalas

---

## 🏆 Selección del Mejor Modelo

### **Metodología de Selección**

```python
Algoritmo de Score Compuesto:
1. Normalización min-max de todas las métricas
2. Asignación de pesos por métrica
3. Cálculo de score compuesto ponderado
4. Selección del modelo con mayor score

Métricas a Maximizar:
- R² (Coeficiente de determinación)
- EVS (Varianza explicada)  
- CV_R²_mean (R² en validación cruzada)

Métricas a Minimizar:
- RMSE (Error cuadrático medio)
- MAE (Error absoluto medio)
- MedAE (Mediana error absoluto)
- CV_R²_std (Variabilidad en CV)
- MAPE (Error porcentual)
```

### **Pesos por Defecto**
```python
Pesos Equitativos: {
    'RMSE': 1/8,
    'MAE': 1/8,
    'MedAE': 1/8,
    'R²': 1/8,
    'EVS': 1/8,
    'CV_R²_mean': 1/8,
    'CV_R²_std': 1/8,
    'MAPE': 1/8
}

Pesos Personalizables via API:
metric_weights = "{'R²':0.3,'RMSE':0.3,'MAE':0.2,'MAPE':0.2}"
```

---

## 📤 Salidas del Sistema

### **1. Respuesta de Entrenamiento**
```json
{
    "message": "Modelo de regresión entrenado exitosamente para @username",
    "best_model": "Random Forest",
    "metrics": {
        "score_compuesto": 0.847,
        "R²": 0.892,
        "RMSE": 1234.56,
        "MAE": 987.32,
        "MAPE": 5.67
    },
    "model_path": "models/username/regresion.pkl",
    "target_variable": "seguidores",
    "features_used": ["dia_semana", "hora", "mes"],
    "training_samples": 800,
    "test_samples": 200
}
```

### **2. Información del Modelo**
```json
{
    "username": "Interbank",
    "target_variable": "seguidores",
    "model_type": "RandomForestRegressor",
    "model_id": "random_forest",
    "timestamp": "2025-07-12T14:30:45.123456",
    "results_count": 8
}
```

### **3. Predicción Individual**
```json
{
    "prediction": 15420.5,
    "model_type": "RandomForestRegressor", 
    "target_variable": "seguidores"
}
```

### **4. Métricas Detalladas**
```json
{
    "account_name": "Interbank",
    "target_variable": "seguidores",
    "best_model": {
        "model_id": "random_forest",
        "model_name": "Random Forest",
        "score_compuesto": 0.847,
        "r2_score": 0.892,
        "rmse": 1234.56,
        "mae": 987.32
    },
    "all_results": [
        {
            "Modelo": "Random Forest",
            "R²": 0.892,
            "RMSE": 1234.56,
            "MAE": 987.32,
            "CV_R²_mean": 0.885
        }
    ],
    "feature_count": 3,
    "training_samples": 800,
    "test_samples": 200
}
```

---

## 🚀 Ejemplo de Uso

### **1. Entrenamiento con Pesos Personalizados**
```bash
# Entrenar con énfasis en R² y RMSE
GET /regression/train/Interbank?metric_weights={"R²":0.4,"RMSE":0.4,"MAE":0.2}

# Respuesta esperada
{
    "message": "Modelo entrenado exitosamente",
    "best_model": "Gradient Boosting",
    "metrics": {
        "score_compuesto": 0.923,
        "R²": 0.945,
        "RMSE": 856.23,
        "MAE": 634.12
    }
}
```

### **2. Predicción Individual**
```bash
# Predicción para un lunes a las 14:00 en julio
GET /regression/predict/Interbank?fecha=2025-07-14

# Respuesta esperada
{
    "prediction": 18567.3,
    "model_type": "GradientBoostingRegressor",
    "target_variable": "seguidores"
}
```

### **3. Consulta de Métricas**
```bash
# Obtener métricas detalladas del modelo
GET /regression/metrics/Interbank

# Respuesta: Métricas completas de todos los modelos evaluados
```

---

## 📊 Resumen de Performance Esperado

### **Ranking Típico de Modelos por Sector Financiero**

1. **Random Forest** - Mejor balance precisión/robustez
2. **Gradient Boosting** - Máxima precisión, riesgo overfitting  
3. **SVR** - Bueno con patrones complejos
4. **Ridge Regression** - Estable y confiable
5. **Decision Tree** - Interpretable pero inestable
6. **Linear Regression** - Baseline simple
7. **Lasso** - Bueno para selección de features
8. **KNN** - Dependiente de datos locales

### **Métricas Objetivo por Sector**
- **R² esperado:** 0.75 - 0.95
- **RMSE típico:** 500 - 2000 seguidores  
- **MAE típico:** 300 - 1500 seguidores
- **MAPE objetivo:** < 10%

---

## 🔧 Configuración Técnica

### **Requisitos del Sistema**
- Python 3.13+
- scikit-learn 1.3.2+
- pandas 2.1.4+
- numpy 1.26.2+

### **Archivos Generados**
- Modelo serializado: `models/{username}/regresion.pkl`
- Métricas: `metricas/{username}.json`
- Logs de entrenamiento: Sistema de logging integrado

### **Consideraciones de Producción**
- Validación de entrada robusta
- Manejo de errores comprehensivo
- Logging detallado de operaciones
- Respaldo automático de modelos
- Monitoreo de performance en tiempo real

---

**Este documento constituye la especificación técnica completa para los 8 modelos de regresión implementados en TwiTrack API v3.0.0**
