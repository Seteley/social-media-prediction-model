#!/usr/bin/env python3
# =============================================================================
# DEMO DEL SISTEMA JWT COMPLETO
# =============================================================================

"""
Demostración completa del sistema JWT implementado:
1. Login y obtención de token
2. Acceso a endpoints protegidos 
3. Control de acceso por empresa
4. Ejemplos de uso con diferentes usuarios
"""

import requests
import json
from datetime import datetime
import time

# Configuración
API_BASE = "http://localhost:8000"

def print_header(title, width=70):
    """Imprime encabezado con formato"""
    print("\n" + "=" * width)
    print(f" {title} ".center(width))
    print("=" * width)

def print_step(step, description):
    """Imprime paso con formato"""
    print(f"\n🔹 PASO {step}: {description}")
    print("-" * 60)

def pretty_print_json(data, title="Respuesta"):
    """Imprime JSON con formato bonito"""
    print(f"\n📄 {title}:")
    print(json.dumps(data, indent=2, ensure_ascii=False))

def test_login(username, password):
    """Prueba login y devuelve token"""
    print(f"🔐 Intentando login con: {username}")
    
    try:
        response = requests.post(
            f"{API_BASE}/auth/login",
            json={"username": username, "password": password}
        )
        
        if response.status_code == 200:
            token_data = response.json()
            print(f"✅ Login exitoso!")
            print(f"   👤 Usuario: {token_data['username']}")
            print(f"   🏢 Empresa ID: {token_data['empresa_id']}")
            print(f"   ⏰ Expira en: {token_data['expires_in']} segundos")
            return token_data['access_token']
        else:
            print(f"❌ Error en login: {response.status_code}")
            print(f"   Detalle: {response.text}")
            return None
            
    except requests.exceptions.ConnectionError:
        print("❌ Error: No se puede conectar a la API. ¿Está ejecutándose?")
        return None
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        return None

def test_protected_endpoint(token, endpoint, description):
    """Prueba un endpoint protegido"""
    print(f"🌐 Probando: {endpoint}")
    print(f"📝 Descripción: {description}")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(f"{API_BASE}{endpoint}", headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Éxito: {response.status_code}")
            pretty_print_json(data)
            return True
        else:
            print(f"❌ Error: {response.status_code}")
            try:
                error_data = response.json()
                pretty_print_json(error_data, "Error")
            except:
                print(f"   Detalle: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error en petición: {e}")
        return False

def test_prediction_with_auth(token, username, fecha):
    """Prueba predicción con autenticación"""
    print(f"🎯 Probando predicción para @{username} en fecha {fecha}")
    
    headers = {"Authorization": f"Bearer {token}"}
    params = {"fecha": fecha}
    
    try:
        response = requests.get(
            f"{API_BASE}/regression/predict/{username}",
            headers=headers,
            params=params
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Predicción exitosa!")
            print(f"   🎯 Predicción: {data['prediction']:,.0f} seguidores")
            print(f"   🤖 Modelo: {data['model_type']}")
            print(f"   📊 Variable: {data['target_variable']}")
            return True
        else:
            print(f"❌ Error: {response.status_code}")
            try:
                error_data = response.json()
                print(f"   Detalle: {error_data['detail']}")
            except:
                print(f"   Detalle: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error en predicción: {e}")
        return False

def test_unauthorized_access():
    """Prueba acceso sin token"""
    print("🚫 Probando acceso sin autenticación...")
    
    try:
        response = requests.get(f"{API_BASE}/auth/me")
        
        if response.status_code == 401:
            print("✅ Correcto: Acceso denegado sin token")
            return True
        else:
            print(f"❌ Inesperado: {response.status_code} (debería ser 401)")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_cross_company_access(token_empresa1, token_empresa2):
    """Prueba acceso entre empresas diferentes"""
    print("🏢 Probando acceso entre empresas...")
    
    # Usuario de empresa 1 trata de acceder a cuenta de empresa 2
    headers1 = {"Authorization": f"Bearer {token_empresa1}"}
    headers2 = {"Authorization": f"Bearer {token_empresa2}"}
    
    # Primero verificar qué cuentas tiene cada empresa
    print("\n📋 Verificando cuentas por empresa:")
    
    print("  👤 Usuario empresa 1:")
    response1 = requests.get(f"{API_BASE}/auth/my-accounts", headers=headers1)
    if response1.status_code == 200:
        accounts1 = response1.json()
        print(f"     Empresa: {accounts1['empresa_nombre']}")
        print(f"     Cuentas: {[acc['cuenta'] for acc in accounts1['accounts']]}")
    
    print("  👤 Usuario empresa 2:")
    response2 = requests.get(f"{API_BASE}/auth/my-accounts", headers=headers2)
    if response2.status_code == 200:
        accounts2 = response2.json()
        print(f"     Empresa: {accounts2['empresa_nombre']}")
        print(f"     Cuentas: {[acc['cuenta'] for acc in accounts2['accounts']]}")
    
    # Intentar acceso cruzado
    print("\n🚫 Intentando acceso cruzado:")
    print("  Usuario empresa 1 → cuenta de empresa 2")
    
    # Usar una cuenta que sabemos que existe (Interbank para empresa 1)
    response_cross = requests.get(
        f"{API_BASE}/regression/model-info/BCPComunica",  # BCP para empresa 2
        headers=headers1  # Token de empresa 1
    )
    
    if response_cross.status_code == 403:
        print("✅ Correcto: Acceso denegado entre empresas")
        return True
    else:
        print(f"❌ Inesperado: {response_cross.status_code} (debería ser 403)")
        return False

def main():
    """Función principal de demostración"""
    print_header("🔐 DEMO COMPLETA DEL SISTEMA JWT")
    print("🎯 Demostración de autenticación y control de acceso por empresa")
    print("🌐 Prueba todos los aspectos del sistema JWT implementado")
    
    # Paso 1: Probar acceso sin autenticación
    print_step(1, "Probar acceso sin autenticación")
    test_unauthorized_access()
    
    # Paso 2: Login de usuarios de diferentes empresas
    print_step(2, "Login de usuarios de diferentes empresas")
    
    # Login usuario Interbank
    token_interbank = test_login("interbank_user", "inter123")
    if not token_interbank:
        print("❌ No se pudo obtener token de Interbank. Saltando demos...")
        return
    
    # Login usuario BCP
    token_bcp = test_login("bcp_user", "bcp123")
    if not token_bcp:
        print("⚠️  No se pudo obtener token de BCP. Continuando con Interbank...")
    
    # Paso 3: Probar endpoints de información del usuario
    print_step(3, "Información del usuario autenticado")
    
    test_protected_endpoint(
        token_interbank, 
        "/auth/me", 
        "Información del usuario actual"
    )
    
    test_protected_endpoint(
        token_interbank,
        "/auth/my-accounts",
        "Cuentas disponibles para el usuario"
    )
    
    # Paso 4: Probar endpoints protegidos de regresión
    print_step(4, "Endpoints de regresión protegidos")
    
    # Información del modelo
    test_protected_endpoint(
        token_interbank,
        "/regression/model-info/Interbank",
        "Información del modelo de Interbank"
    )
    
    # Features requeridas
    test_protected_endpoint(
        token_interbank,
        "/regression/features/Interbank", 
        "Features requeridas para predicción"
    )
    
    # Paso 5: Probar predicciones con autenticación
    print_step(5, "Predicciones con autenticación")
    
    fechas_prueba = ["2025-07-11", "2025-12-25", "2025-01-01"]
    
    for fecha in fechas_prueba:
        test_prediction_with_auth(token_interbank, "Interbank", fecha)
        time.sleep(0.5)  # Pausa breve
    
    # Paso 6: Probar control de acceso entre empresas
    if token_bcp:
        print_step(6, "Control de acceso entre empresas")
        test_cross_company_access(token_interbank, token_bcp)
    
    # Paso 7: Probar acceso con token inválido
    print_step(7, "Acceso con token inválido")
    
    headers_invalid = {"Authorization": "Bearer token_falso_12345"}
    
    try:
        response = requests.get(f"{API_BASE}/auth/me", headers=headers_invalid)
        if response.status_code == 401:
            print("✅ Correcto: Token inválido rechazado")
        else:
            print(f"❌ Inesperado: {response.status_code}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Paso 8: Probar admin endpoints (si hay admin)
    print_step(8, "Endpoints de administrador")
    
    token_admin = test_login("admin", "admin123")
    if token_admin:
        print("🔑 Probando con usuario admin...")
        
        # Los admins pueden acceder a cualquier cuenta
        test_prediction_with_auth(token_admin, "Interbank", "2025-07-11")
        
        if token_bcp:
            test_prediction_with_auth(token_admin, "BCPComunica", "2025-07-11")
    
    # Resumen final
    print_header("🎉 DEMO COMPLETADA")
    
    print("✅ CARACTERÍSTICAS IMPLEMENTADAS:")
    print("   🔐 Autenticación JWT por usuario")
    print("   🏢 Control de acceso por empresa")
    print("   🚫 Protección de endpoints sensibles")
    print("   👥 Roles de usuario (user, admin)")
    print("   📊 Acceso controlado a cuentas de redes sociales")
    print("   🎯 Predicciones autenticadas")
    print("   ⏱️  Tokens con expiración")
    print("   🔒 Validación de permisos por empresa")
    
    print("\n📖 CÓMO USAR EL SISTEMA:")
    print("1. Hacer login: POST /auth/login")
    print("2. Usar token en header: Authorization: Bearer <token>")
    print("3. Acceder solo a cuentas de tu empresa")
    print("4. Admins tienen acceso a todas las cuentas")
    
    print("\n🔧 PRÓXIMOS PASOS:")
    print("• Cambiar JWT_SECRET_KEY en producción")
    print("• Configurar HTTPS para seguridad")
    print("• Implementar refresh tokens")
    print("• Añadir logging de accesos")
    print("• Implementar rate limiting")

if __name__ == "__main__":
    main()
