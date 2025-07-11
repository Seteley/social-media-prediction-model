# RESOLUCIÓN DEL PROBLEMA DE CONTROL DE ACCESO

## 🚨 PROBLEMA IDENTIFICADO

El usuario reportó que, estando logueado como `admin_interbank` (empresa_id: 1), podía acceder a datos de `BCPComunica` (empresa_id: 7), lo que viola el control de acceso por empresa.

```bash
# Comando que NO debería funcionar pero estaba funcionando:
curl -H "Authorization: Bearer TOKEN_INTERBANK" \
   "http://localhost:8000/regression/predict/BCPComunica?fecha=2025-07-11"
```

## 🔍 ANÁLISIS DEL PROBLEMA

### Estructura de la Base de Datos:
- **Tabla `empresa`**: Define las empresas (Interbank=1, BCP=7, etc.)
- **Tabla `usuario`**: Cuentas sociales asociadas a empresas
- **Tabla `usuario_acceso`**: Usuarios JWT para autenticación

### Problema en el Código:
Los endpoints de regresión estaban usando `account_access_required` como dependencia, pero esta no funcionaba correctamente porque no podía acceder al parámetro `username` de la URL.

## ✅ SOLUCIÓN IMPLEMENTADA

### 1. Corrección en `/app/api/regression.py`

Se modificaron tres endpoints para usar verificación explícita:

```python
# ANTES (no funcionaba):
@router.get("/predict/{username}")
def predict_single_get(
    username: str, 
    fecha: str,
    current_user: Dict[str, Any] = Depends(account_access_required)  # ❌ No funcionaba
):

# DESPUÉS (funciona correctamente):
@router.get("/predict/{username}")
def predict_single_get(
    username: str, 
    fecha: str,
    current_user: Dict[str, Any] = Depends(auth_required)  # ✅ Solo autentica
):
    # Verificar acceso a la cuenta explícitamente
    if not auth_service.user_has_access_to_account(current_user['empresa_id'], username):
        raise HTTPException(
            status_code=403,
            detail=f"No tiene acceso a la cuenta @{username}"
        )
```

### 2. Endpoints Corregidos:
- `GET /regression/predict/{username}`
- `GET /regression/model-info/{username}`  
- `GET /regression/features/{username}`

### 3. Lógica de Verificación:
```python
def user_has_access_to_account(self, empresa_id: int, account_name: str) -> bool:
    """Verifica si una empresa tiene acceso a una cuenta específica"""
    with self.get_connection() as conn:
        query = """
        SELECT COUNT(*) 
        FROM usuario u
        WHERE u.id_empresa = ? AND u.cuenta = ?
        """
        result = conn.execute(query, [empresa_id, account_name]).fetchone()
        return result[0] > 0 if result else False
```

## 🧪 CASOS DE PRUEBA

### Casos Correctos (Debe Permitir):
```bash
# admin_interbank accede a Interbank ✅
curl -H "Authorization: Bearer TOKEN_INTERBANK" \
   "http://localhost:8000/regression/predict/Interbank?fecha=2025-07-11"

# admin_bcp accede a BCPComunica ✅  
curl -H "Authorization: Bearer TOKEN_BCP" \
   "http://localhost:8000/regression/predict/BCPComunica?fecha=2025-07-11"
```

### Casos Incorrectos (Debe Denegar - 403):
```bash
# admin_interbank NO puede acceder a BCPComunica ❌
curl -H "Authorization: Bearer TOKEN_INTERBANK" \
   "http://localhost:8000/regression/predict/BCPComunica?fecha=2025-07-11"
```

## 📋 SCRIPTS DE VERIFICACIÓN CREADOS

1. **`test_specific_case.py`**: Prueba el caso específico reportado
2. **`test_regression_access_control.py`**: Suite completa de pruebas de acceso
3. **`debug_access.py`**: Debug de datos en base de datos
4. **`start_api.py`**: Script para iniciar la API fácilmente

## 🔒 ESTRUCTURA DE CONTROL DE ACCESO

### Mapeo Empresa → Cuenta:
- **Empresa 1 (Interbank)** → Acceso a: `Interbank`
- **Empresa 2 (BanBif)** → Acceso a: `BanBif`
- **Empresa 3 (BancodelaNacion)** → Acceso a: `BancodelaNacion`
- **Empresa 4 (BCRP)** → Acceso a: `bcrpoficial`
- **Empresa 5 (BancoPichincha)** → Acceso a: `BancoPichincha`
- **Empresa 6 (BBVA)** → Acceso a: `bbva_peru`
- **Empresa 7 (BCP)** → Acceso a: `BCPComunica`
- **Empresa 8 (ScotiabankPE)** → Acceso a: `ScotiabankPE`

### Usuarios JWT de Prueba:
```
admin_interbank  → Empresa 1 → Solo acceso a Interbank
admin_bcp        → Empresa 7 → Solo acceso a BCPComunica
user_interbank   → Empresa 1 → Solo acceso a Interbank
user_bcp         → Empresa 7 → Solo acceso a BCPComunica
```

## 🚀 VERIFICACIÓN

Para verificar que la corrección funciona:

1. **Iniciar API**:
   ```bash
   python start_api.py
   ```

2. **Probar caso específico**:
   ```bash
   python test_specific_case.py
   ```

3. **Ejecutar suite completa**:
   ```bash
   python test_regression_access_control.py
   ```

## ✅ RESULTADO ESPERADO

Después de la corrección, el comando original del usuario debería devolver:

```json
{
  "detail": "No tiene acceso a la cuenta @BCPComunica"
}
```

Con status code: **403 Forbidden** ❌

En lugar de devolver datos de predicción ✅ (como ocurría antes del fix).
