# 📦 Scripts - Modelos de Regresión por Cuenta Individual

## 🎯 Descripción

Scripts especializados para modelos de regresión individuales por cuenta de Twitter/X. **Versión 3.0** enfocada en predicción del número de seguidores usando datos de la base DuckDB.

---

## 📁 Estructura Minimalista

```
scripts/
├── config.py              # ⚙️  Configuración de regresión y DB
├── data_loader.py          # 📊 Carga de datos desde DuckDB
├── preprocessing.py        # 🔧 Preprocesamiento para regresión
├── regression_models.py    # 🤖 Modelos de regresión ML
├── run_individual.py       # � Script principal por cuenta
├── __init__.py            # 📦 Configuración del paquete
└── README.md              # 📖 Esta documentación
```

### 🎯 **Enfoque Actual**:
- ✅ **Una cuenta a la vez**: Análisis individual especializado
- ✅ **Variable objetivo**: Número de seguidores (`seguidores`)
- ✅ **Fuente de datos**: Base de datos DuckDB
- ✅ **8 algoritmos ML**: Comparación automática
- ✅ **Guardado automático**: Modelos y reportes

---

## 🚀 Uso Rápido

### **Análisis de cuenta individual** (Recomendado)
```bash
# Listar cuentas disponibles
python scripts/run_individual.py --list-accounts

# Entrenar modelo para una cuenta específica
python scripts/run_individual.py --account BCPComunica

# Con opciones avanzadas
python scripts/run_individual.py --account bbva_peru --target seguidores --verbose
```

### **Uso programático**
```python
from scripts.data_loader import AccountDataLoader
from scripts.preprocessing import AccountPreprocessor
from scripts.regression_models import train_account_regression_model

# Cargar datos de una cuenta
loader = AccountDataLoader('BCPComunica')
data = loader.load_account_data()

# Preprocesar datos
preprocessor = AccountPreprocessor('BCPComunica')
processed_data = preprocessor.preprocess_account_data(data)

# Entrenar modelos
model, report = train_account_regression_model('BCPComunica', processed_data)
```

---

## 🔧 Módulos Principales

### 1. **`run_individual.py`** 🚀 **PRINCIPAL**
- **Función:** Script principal para análisis por cuenta
- **Características:**
  - ✅ CLI completa con argumentos
  - ✅ Validación de cuentas disponibles
  - ✅ Carga automática desde DuckDB
  - ✅ Entrenamiento de 8 modelos ML
  - ✅ Guardado automático de modelos y reportes
  - ✅ Salida detallada y manejo de errores

### 2. **`config.py`** ⚙️
- **Función:** Configuración para regresión y base de datos
- **Contiene:** `REGRESSION_MODELS`, `TARGET_VARIABLE`, `FEATURE_CONFIG`
- **Utilidades:** Conexión DB, validación, listado de cuentas

### 3. **`data_loader.py`** 📊
- **Clases:** `AccountDataLoader`, `MultiAccountLoader`
- **Función:** Carga de datos desde DuckDB con combinación de publicaciones y métricas

### 4. **`preprocessing.py`** 🔧
- **Clases:** `AccountPreprocessor`, `BatchPreprocessor`
- **Función:** Feature engineering, limpieza, escalado para regresión

### 5. **`regression_models.py`** 🤖
- **Clase:** `AccountRegressionModel`
- **Función:** 8 algoritmos ML con evaluación comparativa completa
- **Modelos:** Linear, Ridge, Lasso, Random Forest, Gradient Boosting, SVR, KNN, Decision Tree

---

## 📈 Mejoras en Versión 2.0

### **Nuevo Módulo Híbrido:**
- 🔄 Combina enfoque canónico + scripts del compañero
## ⚡ Características Clave

### **Enfoque Especializado:**
- 🎯 **Una cuenta por ejecución**: Análisis detallado e individual
- 🔢 **Variable objetivo fija**: Número de seguidores (`seguidores`)
- � **Fuente única**: Base de datos DuckDB
- 🤖 **8 algoritmos ML**: Comparación automática y selección del mejor
- � **Métricas completas**: R², RMSE, MAE, validación cruzada

### **Optimizaciones:**
- 🗑️ **Minimalista**: Solo 6 archivos esenciales
- 📦 **Arquitectura limpia**: Separación clara de responsabilidades  
- ⚡ **Enfoque específico**: Regresión de seguidores únicamente
- 🔗 **Importes relativos**: Funciona como paquete independiente

### **Automatización:**
- 🤖 **Entrenamiento automático**: 8 modelos simultáneos
- � **Guardado automático**: Mejor modelo y reportes JSON
- 📊 **Validación cruzada**: Métricas robustas por defecto
- 🎨 **CLI completa**: Interfaz de línea de comandos intuitiva

---

## 🧪 Testing Rápido

```bash
# Verificar base de datos y cuentas
cd social-media-prediction-model
python scripts/run_individual.py --list-accounts

# Test con una cuenta
python scripts/run_individual.py --account BCPComunica --verbose
```

### **Test programático:**
```python
# Verificar configuración
from scripts.config import verify_database, get_available_accounts
print("DB OK:", verify_database())
print("Cuentas:", get_available_accounts())

# Test rápido de carga
from scripts.data_loader import AccountDataLoader
loader = AccountDataLoader('BCPComunica')
data = loader.load_account_data()
print(f"Datos cargados: {len(data)} registros")
```

---

## 📋 Dependencias

### **Principales:**
- pandas
- numpy  
- scikit-learn
- joblib
- duckdb

### **Sistema:**
- Python 3.8+
- DuckDB database en `data/base_de_datos/`

---

## � Estructura de Salida

```
results/
├── models/              # Modelos entrenados (.pkl)
│   └── BCPComunica_linear_regression_20250711_143022.pkl
├── reports/             # Reportes JSON
│   └── BCPComunica_regression_report_20250711_143022.json
└── plots/              # Gráficos (futuro)
```

---

## 🎯 Estado del Proyecto

- **Versión:** 3.0.0
- **Estado:** ✅ **LISTA PARA PRODUCCIÓN**
- **Enfoque:** ✅ Regresión individual por cuenta
- **Fuente:** ✅ Base DuckDB
- **Target:** ✅ Número de seguidores

---

**Uso recomendado:** 
```bash
python scripts/run_individual.py --account <nombre_cuenta>
```

*Última actualización: Julio 2025*
