# 📊 Scripts del Proyecto TwitTrack

Esta carpeta contiene la modularización completa del notebook `modelos_twittrack.ipynb` en scripts Python separados y especializados.

## 🗂️ Estructura de Scripts

### 🔧 `config.py`
**Configuración inicial y librerías**
- Importaciones de todas las librerías necesarias
- Configuración global de pandas, matplotlib, warnings
- Configuración de modelos y parámetros del proyecto
- Variables de configuración centralizadas

### 📂 `data_loader.py`
**Carga y consolidación de datos**
- Búsqueda automática de archivos `*_clean.csv`
- Consolidación de múltiples usuarios en un DataFrame único
- Selección de scope de análisis (usuario específico o todos)
- Estadísticas y validación de datos cargados

### 🔧 `preprocessing.py`
**Preprocesamiento y Feature Engineering**
- Verificación de features disponibles
- Creación de features derivadas (longitud_tweet, engagement_rate, etc.)
- Manejo de valores faltantes
- Escalado estándar con StandardScaler
- Detección de outliers

### 🔵 `clustering.py`
**Análisis de Clustering**
- Implementación de K-Means y DBSCAN
- Evaluación con Silhouette Score
- Visualización con PCA en 2D
- Análisis comparativo automático
- Recomendación de algoritmo óptimo

### 📈 `regression_models.py`
**Modelos de Regresión**
- Implementación de 8 algoritmos de ML
- Evaluación con múltiples métricas (RMSE, MAE, R², EVS)
- Validación cruzada para robustez
- Sistema de recomendación automática
- Justificación detallada del modelo óptimo

### 🎨 `visualization.py`
**Visualización y Análisis Gráfico**
- Gráficos individuales por métrica
- Heatmap comparativo de rendimiento
- Radar chart de mejores modelos
- Dashboard resumen interactivo
- Análisis de correlaciones de features

### 🚀 `main_pipeline.py`
**Pipeline Principal**
- Orquestación completa del análisis
- Ejecución secuencial de todos los pasos
- Validación de cumplimiento de objetivos
- Generación de resumen ejecutivo
- Exportación de resultados

## 🎯 Uso de los Scripts

### Ejecución Individual
Cada script puede ejecutarse independientemente:

```python
# Ejemplo: Solo preprocesamiento
from data_loader import load_and_prepare_data
from preprocessing import preprocess_twitter_data

data, info = load_and_prepare_data(usuario_objetivo='interbank')
X_scaled, data_enhanced, features, preprocess_info = preprocess_twitter_data(data)
```

### Ejecución Completa
Para el análisis completo usar el pipeline principal:

```python
from main_pipeline import run_twitter_analysis

# Análisis completo
resultados = run_twitter_analysis(
    usuario_objetivo='interbank',  # o 'todos'
    target_variable='likes',       # o 'retweets', 'respuestas', etc.
    export_summary=True
)
```

### Configuración Personalizada
Modificar parámetros en `config.py`:

```python
# Cambiar configuración de clustering
MODELS_CONFIG['clustering']['kmeans']['n_clusters'] = 4
MODELS_CONFIG['clustering']['dbscan']['eps'] = 2.0

# Cambiar variable objetivo por defecto
PROJECT_CONFIG['default_target_variable'] = 'retweets'
```

## 📊 Outputs Esperados

### Resultados de Clustering
- Silhouette Scores de K-Means y DBSCAN
- Visualizaciones PCA en 2D
- Distribución de clusters
- Recomendación automática

### Resultados de Regresión
- Métricas de 8 modelos de ML
- Ranking por rendimiento
- Modelo recomendado con justificación
- Validación cruzada

### Visualizaciones
- Gráficos de barras por métrica
- Heatmap comparativo
- Radar chart de top modelos
- Dashboard resumen ejecutivo

### Archivos Exportados
- `analisis_twitter_resumen_YYYYMMDD_HHMMSS.txt`: Resumen completo
- Figuras en memoria para uso posterior

## 🔄 Flujo de Ejecución

1. **Configuración** (`config.py`) → Librerías y parámetros
2. **Carga** (`data_loader.py`) → Datos consolidados
3. **Preprocesamiento** (`preprocessing.py`) → Features escaladas
4. **Clustering** (`clustering.py`) → Segmentación de datos
5. **Regresión** (`regression_models.py`) → Predicción de engagement
6. **Visualización** (`visualization.py`) → Gráficos profesionales
7. **Pipeline** (`main_pipeline.py`) → Integración y resumen

## ⚙️ Configuración Avanzada

### Cambiar Usuario de Análisis
```python
# En main_pipeline.py línea 395
USUARIO = 'todos'  # Para analizar todos los usuarios
USUARIO = 'bbva_peru'  # Para usuario específico
```

### Cambiar Variable Objetivo
```python
# En main_pipeline.py línea 396
TARGET = 'retweets'  # Para predecir retweets
TARGET = 'vistas'    # Para predecir vistas
```

### Añadir Nuevos Modelos
```python
# En config.py, agregar a MODELS_CONFIG['regression']['models']
'Nuevo_Modelo': NuevoModelo(parametros=valores)
```

## 🎓 Cumplimiento Académico

Estos scripts cumplen con todos los requisitos del proyecto:

✅ **Implementación de 10+ modelos de ML** (2 clustering + 8 regresión)  
✅ **Comparación con métricas adecuadas** (Silhouette, RMSE, MAE, R²)  
✅ **Justificación del modelo más adecuado** (sistema automático)  
✅ **Uso de datos de webscraping** (archivos *_clean.csv)  
✅ **Análisis reproducible** (semillas aleatorias fijas)  
✅ **Documentación completa** (docstrings y comentarios)  

## 🚀 Próximos Pasos

1. **Ejecutar el pipeline completo** con `main_pipeline.py`
2. **Revisar los resultados** en la variable `resultados`
3. **Analizar las visualizaciones** generadas
4. **Transferir de vuelta a notebook** si es necesario
5. **Crear nuevas features** modificando `preprocessing.py`

## 📝 Notas Importantes

- Cada script es **autocontenido** y documentado
- Los parámetros están **centralizados** en `config.py`
- El sistema es **reproducible** (semillas fijas)
- Las visualizaciones son **profesionales** y publication-ready
- El código es **modular** y fácil de mantener

---

🎯 **Objetivo**: Scripts listos para producción que pueden ser ejecutados independientemente o como pipeline completo, manteniendo la funcionalidad completa del notebook original pero con mejor organización y mantenibilidad.
