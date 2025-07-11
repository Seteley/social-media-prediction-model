# Social Media Regression Models 🚀

> **Modelo de regresión para predicción del número de seguidores por cuenta individual**

## 📊 Descripción

Sistema modular para análisis de regresión individualizado de cuentas de Twitter/X, enfocado en predecir el **número de seguidores** utilizando datos de métricas temporales almacenados en DuckDB. El proyecto se centra en generar modelos de regresión específicos para cada cuenta, utilizando principalmente datos de la tabla `metrica` junto con estadísticas agregadas de publicaciones.

## 🎯 Características Principales

- **Predicción de Seguidores**: Enfoque específico en predecir el crecimiento de seguidores
- **Datos de Métricas Temporales**: Análisis basado en series temporales de métricas de cuenta
- **Features de Tendencia**: Incluye diferencias temporales, promedios móviles y ratios
- **Análisis Individual**: Modelo de regresión específico para cada cuenta
- **Base de Datos DuckDB**: Carga de datos directamente desde la base de datos
- **Múltiples Algoritmos**: 8 modelos de regresión diferentes
- **Preprocesamiento Automático**: Feature engineering y selección automática
- **Reportes Detallados**: Exportación de resultados y modelos entrenados
- **CLI Intuitiva**: Interfaz de línea de comandos fácil de usar

## 🗂️ Estructura del Proyecto

```
social-media-prediction-model/
├── scripts/                    # Módulos principales
│   ├── config.py              # Configuración y conexión DB
│   ├── data_loader.py         # Carga de datos desde DuckDB
│   ├── preprocessing.py       # Preprocesamiento y feature engineering
│   ├── regression_models.py   # Modelos de regresión
│   └── run_individual.py      # CLI para análisis individual
├── data/                       # Datos y base de datos
│   └── base_de_datos/         # DuckDB database
├── results/                    # Resultados del análisis
│   ├── models/                # Modelos entrenados (.pkl)
│   ├── reports/               # Reportes JSON
│   └── plots/                 # Visualizaciones (futuro)
└── requirements.txt           # Dependencias
```

## ⚙️ Instalación

1. **Clonar el repositorio**:
```bash
git clone <repository-url>
cd social-media-prediction-model
```

2. **Instalar dependencias**:
```bash
pip install -r requirements.txt
```

3. **Verificar la base de datos**:
```bash
python -m scripts.config
```

## 🚀 Uso

### Ver cuentas disponibles
```bash
python -m scripts.run_individual --list-accounts
```

### Ejecutar análisis para una cuenta específica
```bash
python -m scripts.run_individual --account BCPComunica
```

### Opciones adicionales
```bash
# Cambiar variable objetivo (seguidores por defecto, otras opciones disponibles)
python -m scripts.run_individual --account BCPComunica --target total_tweets

# Especificar directorio de salida
python -m scripts.run_individual --account BCPComunica --output-dir ./custom_results

# Modo verbose para más detalles
python -m scripts.run_individual --account BCPComunica --verbose
```

## 📊 Modelos Disponibles

1. **Regresión Lineal Simple** - Modelo base linear
2. **Regresión Ridge (L2)** - Regularización L2
3. **Regresión Lasso (L1)** - Regularización L1
4. **Random Forest** - Ensamble de árboles
5. **Gradient Boosting** - Boosting gradient
6. **Support Vector Regression** - SVM para regresión
7. **K-Nearest Neighbors** - KNN adaptado para regresión
8. **Árbol de Decisión** - Árbol individual

## 📈 Features Utilizadas

### 🎯 Variable Objetivo
- **seguidores**: Número de seguidores de la cuenta (principal métrica a predecir)

### 📊 Features de Métricas Principales
- **total_tweets**: Número total de tweets de la cuenta
- **siguiendo**: Número de cuentas que sigue
- **publicaciones_dia**: Número de publicaciones por día

### ⏰ Features Temporales
- **dia_semana**: Día de la semana (0-6)
- **hora**: Hora del día (0-23)  
- **mes**: Mes del año (1-12)
- **dia_año**: Día del año (1-365)
- **posicion_temporal**: Posición temporal normalizada

### 📈 Features de Tendencia y Crecimiento
- **seguidores_diff**: Diferencia en seguidores respecto al período anterior
- **tweets_diff**: Diferencia en tweets totales
- **siguiendo_diff**: Diferencia en número de cuentas seguidas
- **seguidores_ma7**: Promedio móvil de seguidores (7 períodos)
- **seguidores_std7**: Desviación estándar de seguidores (7 períodos)

### 🔢 Features de Ratios
- **ratio_seguidores_siguiendo**: Proporción seguidores/siguiendo
- **ratio_seguidores_tweets**: Proporción seguidores/tweets totales

### 💬 Features de Engagement Agregadas
- **avg_likes_dia**: Promedio de likes por día
- **avg_retweets_dia**: Promedio de retweets por día
- **avg_respuestas_dia**: Promedio de respuestas por día
- **avg_vistas_dia**: Promedio de vistas por día
- **total_engagement_dia**: Total de engagement por día
- **engagement_rate_promedio**: Tasa de engagement promedio
- **engagement_ma7**: Promedio móvil de engagement (7 períodos)

## 💾 Resultados

Cada análisis genera:

- **Modelo entrenado** (`.pkl`): Guardado en `results/models/`
- **Reporte JSON**: Métricas detalladas en `results/reports/`
- **Comparación de modelos**: R², RMSE, MAE, CV scores

## 🔧 Estructura de Datos

El sistema carga datos combinando las tablas de la base de datos DuckDB:

### 📊 Fuente Principal: Tabla `metrica`
- **Registros temporales** de métricas de cuenta
- **seguidores**: Variable objetivo principal
- **tweets**: Número total de tweets
- **siguiendo**: Cuentas seguidas
- **hora**: Timestamp de la métrica

### 📝 Datos Agregados: Tabla `publicaciones`
- **Estadísticas diarias** agregadas por fecha
- **Promedios de engagement** (likes, retweets, respuestas, vistas)
- **Conteo de publicaciones** por día
- **Total de engagement** por día

### 👤 Información de Cuenta: Tabla `usuario`
- **Identificación** de la cuenta
- **Metadatos** de usuario

### 💡 Enfoque de Modeling
- **Predicción temporal**: Los datos se ordenan cronológicamente
- **Features de tendencia**: Se calculan diferencias y promedios móviles
- **Ventana temporal**: Análisis de los últimos 7 registros para suavizado
- **Outliers**: Filtrado opcional de valores extremos usando IQR

## 📋 Cuentas Disponibles

- BCPComunica
- BanBif  
- BancoPichincha
- BancodelaNacion
- Interbank
- ScotiabankPE
- bbva_peru
- bcrpoficial

## 📖 Ejemplo de Uso

```bash
# 1. Ver cuentas disponibles
python -m scripts.run_individual --list-accounts

# 2. Ejecutar análisis para BanBif
python -m scripts.run_individual --account BanBif

# 3. Revisar resultados
ls results/models/BanBif_*
ls results/reports/BanBif_*
```

## 🧪 Testing

```bash
# Test carga de datos
python -m scripts.data_loader

# Test preprocesamiento
python -c "from scripts.preprocessing import AccountPreprocessor; print('✅ Preprocessing OK')"

# Test modelos
python -c "from scripts.regression_models import AccountRegression; print('✅ Models OK')"
```

## 📊 Métricas de Evaluación

- **R² (Coeficiente de determinación)**: Varianza explicada por el modelo
- **RMSE (Root Mean Square Error)**: Error cuadrático medio
- **MAE (Mean Absolute Error)**: Error absoluto medio
- **CV R² Score**: R² promedio en validación cruzada

## 🎯 Variables Objetivo Soportadas

- `seguidores` (por defecto) - **Predicción de crecimiento de seguidores**
- `total_tweets` - Predicción de actividad de tweets
- `siguiendo` - Predicción de cuentas seguidas
- `publicaciones_dia` - Predicción de frecuencia de publicaciones
- Cualquier columna numérica de la tabla metrica

## 🔄 Flujo de Trabajo

1. **Carga de datos**: Extracción desde DuckDB con consulta SQL que combina metrica y publicaciones
2. **Agregación temporal**: Estadísticas de publicaciones agrupadas por día  
3. **Feature engineering**: Generación de features de tendencia, ratios y promedios móviles
4. **Preprocesamiento**: Limpieza, filtrado de outliers y escalado
5. **División de datos**: Train/test split (80/20)
6. **Entrenamiento**: 8 modelos diferentes con validación cruzada
7. **Evaluación**: Métricas de rendimiento y selección del mejor modelo
8. **Exportación**: Guardado de modelo y reporte detallado

## 👥 Contribución

1. Fork el proyecto
2. Crear rama de feature (`git checkout -b feature/nueva-funcionalidad`)
3. Commit cambios (`git commit -am 'Agregar nueva funcionalidad'`)
4. Push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Crear Pull Request

## 📄 Licencia

Este proyecto está bajo la Licencia MIT - ver el archivo [LICENSE](LICENSE) para detalles.

---

**Versión**: 3.0.0  
**Última actualización**: Julio 2025  
**Desarrollado para**: Análisis de datos - UNI