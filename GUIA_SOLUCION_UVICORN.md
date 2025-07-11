# GUÍA DE SOLUCIÓN: PROBLEMA CON UVICORN/API

## 🚨 PROBLEMA
- `uvicorn app.main:app --reload` no inicia correctamente
- localhost:8000 no responde
- Error de KeyboardInterrupt al presionar Ctrl+C (normal)

## 🔍 DIAGNÓSTICO PASO A PASO

### **Paso 1: Verificar app básica**
```bash
cd "tu_directorio_del_proyecto"
python minimal_app.py
```
- Si funciona → El problema está en los routers
- Si no funciona → Problema con FastAPI/uvicorn

### **Paso 2: Diagnóstico gradual de routers**
```bash
python debug_routers.py
```
Este script probará cada router individualmente y mostrará cuál causa el problema.

### **Paso 3: Test de imports**
```bash
python test_imports.py
```
Verificará si todos los módulos se pueden importar correctamente.

### **Paso 4: Diagnóstico completo**
```bash
python diagnose_imports.py
```
Verificará archivos, dependencias y estructura del proyecto.

## 🔧 SOLUCIONES COMUNES

### **Solución 1: Problema con dependencias**
```bash
# Verificar que todas las dependencias estén instaladas
pip install -r requirements.txt

# Verificar que estés en el entorno virtual correcto
pip list | grep fastapi
pip list | grep uvicorn
```

### **Solución 2: Problema con imports circulares**
Si `debug_routers.py` muestra errores específicos en algunos routers:

1. **Error en auth_routes:**
   ```bash
   # Verificar dependencies.py
   python -c "from app.auth.dependencies import auth_required; print('OK')"
   ```

2. **Error en regression:**
   ```bash
   # Verificar regression.py
   python -c "from app.api.regression import router; print('OK')"
   ```

### **Solución 3: Usar app simplificada temporalmente**
Si el problema persiste, usar temporalmente una versión sin problemas:

```python
# Crea temp_main.py
from fastapi import FastAPI

app = FastAPI(title="Social Media API - Temp")

@app.get("/")
def root():
    return {"message": "API temporal funcionando"}

# Solo agregar auth_routes si funciona
try:
    from app.api import auth_routes
    app.include_router(auth_routes.router, tags=["Auth"])
except:
    pass

# Luego ejecutar:
# uvicorn temp_main:app --reload
```

### **Solución 4: Iniciar sin reload**
```bash
# Probar sin --reload
uvicorn app.main:app --host 127.0.0.1 --port 8000

# O usar el script directo
python start_server.py
```

### **Solución 5: Verificar puerto**
```bash
# Verificar si el puerto 8000 está ocupado
netstat -ano | findstr :8000

# Si está ocupado, usar otro puerto
uvicorn app.main:app --port 8001
```

## 🎯 COMANDOS DE VERIFICACIÓN

### **Verificar que la API funciona:**
```bash
# En otra terminal (después de iniciar la API)
curl http://localhost:8000/
curl http://localhost:8000/docs
```

### **Test de autenticación:**
```bash
# Login
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username": "admin_interbank", "password": "password123"}'

# Test sin token (debe ser 401)
curl "http://localhost:8000/regression/predict/Interbank?fecha=2025-07-11"
```

## 📋 SECUENCIA RECOMENDADA

1. **Ejecutar:** `python minimal_app.py`
   - Si funciona → Continuar al paso 2
   - Si no funciona → Verificar FastAPI/uvicorn

2. **Ejecutar:** `python debug_routers.py`
   - Identificar qué router causa problemas
   - Corregir imports específicos

3. **Ejecutar:** `python start_server.py`
   - Intento de inicio con diagnóstico

4. **Última opción:** `uvicorn app.main:app --host 127.0.0.1 --port 8000`
   - Comando directo sin reload

## ✅ VERIFICAR SOLUCIÓN

Una vez que la API esté funcionando:

```bash
# Verificar endpoint base
curl http://localhost:8000/

# Verificar documentación
# Abrir en navegador: http://localhost:8000/docs

# Test de autenticación completo
python test_401_vs_403.py
```

## 🚀 RESULTADO ESPERADO

```json
// GET http://localhost:8000/
{
  "message": "Social Media Analytics API funcionando con autenticación JWT",
  "version": "3.0.0",
  "authentication": "JWT Bearer Token requerido para endpoints protegidos"
}
```

## 📞 SI PERSISTE EL PROBLEMA

1. Ejecutar cada script de diagnóstico
2. Copiar los mensajes de error exactos
3. Verificar que el entorno virtual esté activo
4. Asegurar que todas las dependencias estén instaladas

El error de `KeyboardInterrupt` que ves es **normal** cuando presionas Ctrl+C. El problema real es por qué la API no inicia correctamente.
