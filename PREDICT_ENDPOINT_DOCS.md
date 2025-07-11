# 📡 ENDPOINT: GET /regression/predict/{username}

## 🎯 Descripción
Realiza una predicción de regresión usando fecha o parámetros temporales individuales.

**URL:** `GET /regression/predict/{username}`

---

## 🔧 Modos de Uso

### ✅ MODO 1: Usando Fecha (RECOMENDADO)

**Formato:** `/regression/predict/{username}?fecha=YYYY-MM-DD`

**Ejemplo:**
```
http://localhost:8000/regression/predict/Interbank?fecha=2028-07-11
```

**Comportamiento:**
- ✅ Automáticamente extrae `dia_semana` y `mes` de la fecha
- ✅ Asume `hora=23` (11 PM) por defecto
- ✅ Valida formato de fecha
- ✅ Más simple y menos propenso a errores

**Parámetros:**
- `fecha` (string): Fecha en formato YYYY-MM-DD
  - Ejemplo: `2025-07-11`, `2028-10-11`

---

### ✅ MODO 2: Usando Parámetros Individuales

**Formato:** `/regression/predict/{username}?dia_semana=X&mes=Y&hora=Z`

**Ejemplo:**
```
http://localhost:8000/regression/predict/Interbank?dia_semana=2&mes=10&hora=15
```

**Parámetros:**
- `dia_semana` (int, requerido): Día de la semana
  - 0=Lunes, 1=Martes, 2=Miércoles, 3=Jueves, 4=Viernes, 5=Sábado, 6=Domingo
- `mes` (int, requerido): Mes del año
  - 1=Enero, 2=Febrero, ..., 12=Diciembre
- `hora` (int, opcional): Hora del día
  - Rango: 0-23, Default: 23

---

## 📤 Respuesta

**Siempre devuelve la misma estructura (simplificada):**

```json
{
  "prediction": 12500.0,
  "model_type": "RandomForestRegressor",
  "target_variable": "seguidores"
}
```

**Campos:**
- `prediction` (float): Valor predicho para la variable objetivo
- `model_type` (string): Tipo de modelo utilizado
- `target_variable` (string): Variable que se está prediciendo

---

## ⚠️ Reglas Importantes

1. **Use SOLO uno de los modos**: Si proporciona `fecha`, los otros parámetros se ignoran completamente
2. **MODO 1 es recomendado**: Más simple y menos propenso a errores
3. **Validaciones automáticas**: El sistema valida rangos y formatos automáticamente

---

## 🧪 Ejemplos Prácticos

### Usando Fecha
```bash
# Miércoles 11 de Octubre, 2028, hora 23
curl "http://localhost:8000/regression/predict/Interbank?fecha=2028-10-11"

# Viernes 11 de Julio, 2025, hora 23  
curl "http://localhost:8000/regression/predict/BanBif?fecha=2025-07-11"
```

### Usando Parámetros Individuales
```bash
# Miércoles, Octubre, 3 PM
curl "http://localhost:8000/regression/predict/Interbank?dia_semana=2&mes=10&hora=15"

# Viernes, Julio, hora por defecto (23)
curl "http://localhost:8000/regression/predict/BanBif?dia_semana=4&mes=7"
```

---

## ❌ Casos de Error

### Error 400: Formato de fecha inválido
```bash
curl "http://localhost:8000/regression/predict/Interbank?fecha=2025/07/11"
# Error: Formato debe ser YYYY-MM-DD
```

### Error 400: Parámetros fuera de rango
```bash
curl "http://localhost:8000/regression/predict/Interbank?dia_semana=8&mes=7"
# Error: dia_semana debe estar entre 0-6
```

### Error 400: Parámetros incompletos
```bash
curl "http://localhost:8000/regression/predict/Interbank?dia_semana=1"
# Error: Falta el parámetro 'mes'
```

### Error 404: Usuario no encontrado
```bash
curl "http://localhost:8000/regression/predict/UsuarioInexistente?fecha=2025-07-11"
# Error: Modelo no encontrado para el usuario
```

---

## 💡 Recomendaciones

1. **Use el MODO 1 (fecha)** siempre que sea posible
2. **Valide las fechas** antes de enviar la request
3. **Maneje los errores 400 y 404** apropiadamente en su aplicación
4. **Cache las respuestas** si hace múltiples predicciones con los mismos parámetros

---

## 🔍 Para Desarrolladores

**Modelos soportados:** BanBif, Interbank, BCPComunica, etc.
**Features utilizadas:** dia_semana, hora, mes (extraídas automáticamente de la fecha)
**Algoritmos:** RandomForest, DecisionTree, LinearRegression (según el mejor modelo entrenado)

**Script de prueba disponible:** `ejemplos_uso_predict.py`
