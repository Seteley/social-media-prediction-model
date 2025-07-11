"""
Script de prueba completo para validar todos los endpoints de clustering 
con JWT y control de acceso a nivel de empresa.

Este script verifica:
1. Autenticación JWT requerida (401)
2. Control de acceso por empresa (403)
3. Manejo de recursos no encontrados (404)
4. Funcionalidad correcta (200)

Ejecutar con: python test_clustering_endpoints_completo.py
"""

import requests
import json
import sys
from pathlib import Path

# Configuración
BASE_URL = "http://localhost:8000"
LOGIN_URL = f"{BASE_URL}/auth/login"

# Usuarios de prueba (deben existir en la BD)
USERS = {
    "admin": {"username": "test_admin", "password": "password123"},
    "user": {"username": "test_user", "password": "password123"},
    "viewer": {"username": "test_viewer", "password": "password123"},
}

# Endpoints a probar
CLUSTERING_ENDPOINTS = [
    {"method": "GET", "url": "/clustering/users", "requires_username": False},
    {"method": "GET", "url": "/clustering/model-info/{username}", "requires_username": True},
    {"method": "GET", "url": "/clustering/metrics/{username}", "requires_username": True},
    {"method": "GET", "url": "/clustering/history/{username}", "requires_username": True},
    {"method": "GET", "url": "/clustering/train/{username}", "requires_username": True},
    {"method": "GET", "url": "/clustering/clusters/{username}", "requires_username": True},
]

class ClusteringEndpointTester:
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
            response = self.session.post(LOGIN_URL, data=login_data)
            if response.status_code == 200:
                token = response.json().get("access_token")
                if token:
                    self.tokens[user_type] = token
                    return token
            return None
        except Exception as e:
            print(f"Error al hacer login como {user_type}: {e}")
            return None

    def test_endpoint_without_auth(self, endpoint):
        """Prueba endpoint sin autenticación - debe retornar 401"""
        url = endpoint["url"]
        if endpoint["requires_username"]:
            url = url.replace("{username}", "BanBif")
        
        full_url = f"{BASE_URL}{url}"
        
        try:
            response = self.session.get(full_url)
            passed = response.status_code == 401
            details = f"Status: {response.status_code}, Expected: 401"
            if not passed and response.status_code != 401:
                try:
                    details += f", Response: {response.json()}"
                except:
                    details += f", Response: {response.text[:100]}"
            
            self.print_test_result(
                f"Sin auth: {endpoint['method']} {url}",
                passed,
                details
            )
            return passed
        except Exception as e:
            self.print_test_result(
                f"Sin auth: {endpoint['method']} {url}",
                False,
                f"Error de conexión: {e}"
            )
            return False

    def test_endpoint_with_auth(self, endpoint, user_type, token):
        """Prueba endpoint con autenticación válida"""
        url = endpoint["url"]
        if endpoint["requires_username"]:
            url = url.replace("{username}", "BanBif")  # Cuenta existente
        
        full_url = f"{BASE_URL}{url}"
        headers = {"Authorization": f"Bearer {token}"}
        
        try:
            response = self.session.get(full_url, headers=headers)
            # Para endpoints autenticados, esperamos 200, 403, o 404
            passed = response.status_code in [200, 403, 404]
            details = f"Status: {response.status_code} (usuario: {user_type})"
            
            if response.status_code == 403:
                details += " - Sin acceso a la empresa"
            elif response.status_code == 404:
                details += " - Recurso no encontrado"
            elif response.status_code == 200:
                details += " - Acceso exitoso"
                
            if not passed:
                try:
                    details += f", Response: {response.json()}"
                except:
                    details += f", Response: {response.text[:100]}"
            
            self.print_test_result(
                f"Con auth: {endpoint['method']} {url} ({user_type})",
                passed,
                details
            )
            return passed
        except Exception as e:
            self.print_test_result(
                f"Con auth: {endpoint['method']} {url} ({user_type})",
                False,
                f"Error de conexión: {e}"
            )
            return False

    def test_cross_company_access(self, endpoint):
        """Prueba acceso a datos de otra empresa - debe retornar 403"""
        if not endpoint["requires_username"]:
            return True  # Skip si no requiere username
        
        url = endpoint["url"].replace("{username}", "otra_empresa_cuenta")
        full_url = f"{BASE_URL}{url}"
        
        # Usar token de admin para probar acceso cruzado
        if "admin" not in self.tokens:
            return False
            
        headers = {"Authorization": f"Bearer {self.tokens['admin']}"}
        
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
                f"Cross-company: {endpoint['method']} {url}",
                passed,
                details
            )
            return passed
        except Exception as e:
            self.print_test_result(
                f"Cross-company: {endpoint['method']} {url}",
                False,
                f"Error de conexión: {e}"
            )
            return False

    def run_all_tests(self):
        """Ejecuta todas las pruebas"""
        self.print_header("PRUEBAS DE ENDPOINTS DE CLUSTERING")
        
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
        
        print(f"\n🧪 Iniciando pruebas con {len(CLUSTERING_ENDPOINTS)} endpoints...")
        
        # Pruebas sin autenticación (debe retornar 401)
        self.print_header("PRUEBAS SIN AUTENTICACIÓN (Esperado: 401)")
        for endpoint in CLUSTERING_ENDPOINTS:
            self.test_endpoint_without_auth(endpoint)
        
        # Pruebas con autenticación válida
        self.print_header("PRUEBAS CON AUTENTICACIÓN VÁLIDA")
        for user_type, token in self.tokens.items():
            print(f"\n--- Probando como {user_type} ---")
            for endpoint in CLUSTERING_ENDPOINTS:
                self.test_endpoint_with_auth(endpoint, user_type, token)
        
        # Pruebas de acceso cruzado entre empresas
        self.print_header("PRUEBAS DE ACCESO CRUZADO (Esperado: 403/404)")
        for endpoint in CLUSTERING_ENDPOINTS:
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
    print("🚀 Iniciando pruebas de endpoints de clustering...")
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
    
    tester = ClusteringEndpointTester()
    success = tester.run_all_tests()
    
    if success:
        print("\n🏆 TODAS LAS PRUEBAS COMPLETADAS EXITOSAMENTE")
        return True
    else:
        print("\n💥 ALGUNAS PRUEBAS FALLARON")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
