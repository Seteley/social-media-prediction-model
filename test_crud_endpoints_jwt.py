#!/usr/bin/env python3
"""
Script de prueba para validar la protección JWT de los endpoints CRUD:
- /crud/publicaciones/{usuario}
- /crud/metricas/{usuario}

Este script verifica:
1. Autenticación JWT requerida (401)
2. Control de acceso por empresa (403)
3. Funcionalidad correcta (200/404)
"""

import requests
import json
import sys

# Configuración
BASE_URL = "http://localhost:8000"
LOGIN_URL = f"{BASE_URL}/auth/login"

# Usuarios de prueba
USERS = {
    "admin_interbank": {"username": "admin_interbank", "password": "password123"},
    "admin_bcp": {"username": "admin_bcp", "password": "password123"},
    "admin_bbva": {"username": "admin_bbva", "password": "password123"},
}

# Endpoints a probar
CRUD_ENDPOINTS = [
    {"url": "/crud/publicaciones/{usuario}", "description": "Publicaciones usuario"},
    {"url": "/crud/metricas/{usuario}", "description": "Métricas usuario"},
]

class CRUDEndpointTester:
    def __init__(self):
        self.session = requests.Session()
        self.tokens = {}
        self.results = {
            "total_tests": 0,
            "passed": 0,
            "failed": 0,
            "details": []
        }

    def print_header(self, title):
        print(f"\n{'='*60}")
        print(f"{title:^60}")
        print(f"{'='*60}")

    def print_test_result(self, test_name, passed, details=""):
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} {test_name}")
        if details:
            print(f"    {details}")
        
        self.results["total_tests"] += 1
        if passed:
            self.results["passed"] += 1
        else:
            self.results["failed"] += 1
        
        self.results["details"].append({
            "test": test_name,
            "passed": passed,
            "details": details
        })

    def login_user(self, user_type):
        """Intenta hacer login y obtener token JWT"""
        if user_type not in USERS:
            return None
        
        user_data = USERS[user_type]
        login_data = {
            "username": user_data["username"],
            "password": user_data["password"]
        }
        
        try:
            response = self.session.post(LOGIN_URL, json=login_data)
            if response.status_code == 200:
                token = response.json().get("access_token")
                if token:
                    self.tokens[user_type] = token
                    return token
            return None
        except Exception as e:
            print(f"Error al hacer login como {user_type}: {e}")
            return None

    def test_endpoint_without_auth(self, endpoint, test_usuario):
        """Prueba endpoint sin autenticación - debe retornar 401"""
        url = endpoint["url"].replace("{usuario}", test_usuario)
        full_url = f"{BASE_URL}{url}"
        
        try:
            response = self.session.get(full_url)
            passed = response.status_code == 401
            details = f"Status: {response.status_code}, Expected: 401"
            if not passed:
                try:
                    details += f", Response: {response.json()}"
                except:
                    details += f", Response: {response.text[:100]}"
            
            self.print_test_result(
                f"Sin auth: {url}",
                passed,
                details
            )
            return passed
        except Exception as e:
            self.print_test_result(
                f"Sin auth: {url}",
                False,
                f"Error de conexión: {e}"
            )
            return False

    def test_endpoint_with_auth(self, endpoint, user_type, token, test_usuario):
        """Prueba endpoint con autenticación válida"""
        url = endpoint["url"].replace("{usuario}", test_usuario)
        full_url = f"{BASE_URL}{url}"
        headers = {"Authorization": f"Bearer {token}"}
        
        try:
            response = self.session.get(full_url, headers=headers)
            # Para endpoints autenticados, esperamos 200, 403, o 404
            passed = response.status_code in [200, 403, 404]
            details = f"Status: {response.status_code} (usuario: {user_type}, cuenta: {test_usuario})"
            
            if response.status_code == 403:
                details += " - Sin acceso a la empresa"
            elif response.status_code == 404:
                details += " - Datos no encontrados"
            elif response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    details += f" - {len(data)} registros encontrados"
                else:
                    details += " - Datos obtenidos"
                
            if not passed:
                try:
                    details += f", Response: {response.json()}"
                except:
                    details += f", Response: {response.text[:100]}"
            
            self.print_test_result(
                f"Con auth: {url} ({user_type})",
                passed,
                details
            )
            return passed
        except Exception as e:
            self.print_test_result(
                f"Con auth: {url} ({user_type})",
                False,
                f"Error de conexión: {e}"
            )
            return False

    def test_cross_company_access(self, endpoint):
        """Prueba acceso a datos de otra empresa - debe retornar 403"""
        # Usar token de admin_interbank para acceder a datos de BCP
        if "admin_interbank" not in self.tokens:
            return False
            
        url = endpoint["url"].replace("{usuario}", "BCPComunica")  # Cuenta de otra empresa
        full_url = f"{BASE_URL}{url}"
        headers = {"Authorization": f"Bearer {self.tokens['admin_interbank']}"}
        
        try:
            response = self.session.get(full_url, headers=headers)
            # Esperamos 403 (sin acceso) o 404 (no existe)
            passed = response.status_code in [403, 404]
            details = f"Status: {response.status_code}, Expected: 403 or 404"
            
            if not passed:
                try:
                    details += f", Response: {response.json()}"
                except:
                    details += f", Response: {response.text[:100]}"
            
            self.print_test_result(
                f"Cross-company: {url}",
                passed,
                details
            )
            return passed
        except Exception as e:
            self.print_test_result(
                f"Cross-company: {url}",
                False,
                f"Error de conexión: {e}"
            )
            return False

    def run_all_tests(self):
        """Ejecuta todas las pruebas"""
        self.print_header("PRUEBAS DE ENDPOINTS CRUD PROTEGIDOS")
        
        print("\n🔐 Haciendo login con usuarios de prueba...")
        for user_type in USERS.keys():
            token = self.login_user(user_type)
            if token:
                print(f"✅ Login exitoso: {user_type}")
            else:
                print(f"❌ Login fallido: {user_type}")
        
        if not self.tokens:
            print("\n❌ No se pudo obtener ningún token. Verifique que los usuarios existan en la BD.")
            return
        
        print(f"\n🧪 Iniciando pruebas con {len(CRUD_ENDPOINTS)} endpoints...")
        
        # Cuentas de prueba para diferentes escenarios
        test_accounts = ["Interbank", "BCPComunica", "bbva_peru"]
        
        # Pruebas sin autenticación (debe retornar 401)
        self.print_header("PRUEBAS SIN AUTENTICACIÓN (Esperado: 401)")
        for endpoint in CRUD_ENDPOINTS:
            for account in test_accounts[:1]:  # Solo probamos con una cuenta
                self.test_endpoint_without_auth(endpoint, account)
        
        # Pruebas con autenticación válida
        self.print_header("PRUEBAS CON AUTENTICACIÓN VÁLIDA")
        for user_type, token in self.tokens.items():
            print(f"\n--- Probando como {user_type} ---")
            for endpoint in CRUD_ENDPOINTS:
                for account in test_accounts:
                    self.test_endpoint_with_auth(endpoint, user_type, token, account)
        
        # Pruebas de acceso cruzado entre empresas
        self.print_header("PRUEBAS DE ACCESO CRUZADO (Esperado: 403/404)")
        for endpoint in CRUD_ENDPOINTS:
            self.test_cross_company_access(endpoint)
        
        # Resumen
        self.print_header("RESUMEN DE RESULTADOS")
        print(f"📊 Total de pruebas: {self.results['total_tests']}")
        print(f"✅ Pruebas exitosas: {self.results['passed']}")
        print(f"❌ Pruebas fallidas: {self.results['failed']}")
        
        success_rate = (self.results['passed'] / self.results['total_tests']) * 100 if self.results['total_tests'] > 0 else 0
        print(f"📈 Tasa de éxito: {success_rate:.1f}%")
        
        if self.results['failed'] > 0:
            print(f"\n⚠️  Hay {self.results['failed']} pruebas fallidas. Revisar detalles arriba.")
            return False
        else:
            print(f"\n🎉 ¡Todas las pruebas pasaron exitosamente!")
            return True

def main():
    """Función principal"""
    print("🚀 Iniciando pruebas de endpoints CRUD protegidos...")
    print("📋 Verificando que la API esté ejecutándose...")
    
    try:
        response = requests.get(f"{BASE_URL}/docs", timeout=5)
        if response.status_code != 200:
            print("❌ La API no está respondiendo. Asegúrese de que esté ejecutándose en localhost:8000")
            return False
    except requests.exceptions.RequestException:
        print("❌ No se puede conectar con la API. Asegúrese de que esté ejecutándose en localhost:8000")
        return False
    
    print("✅ API está respondiendo. Iniciando pruebas...")
    
    tester = CRUDEndpointTester()
    success = tester.run_all_tests()
    
    if success:
        print("\n🏆 TODAS LAS PRUEBAS COMPLETADAS EXITOSAMENTE")
        print("✅ Endpoints CRUD protegidos correctamente con JWT")
        return True
    else:
        print("\n💥 ALGUNAS PRUEBAS FALLARON")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
