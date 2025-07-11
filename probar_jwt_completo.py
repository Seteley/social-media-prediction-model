#!/usr/bin/env python3
# =============================================================================
# PRUEBAS COMPLETAS DEL SISTEMA JWT
# =============================================================================

"""
🧪 Suite completa de pruebas para el sistema JWT

Este script valida:
✅ Autenticación con todas las empresas
✅ Control de acceso por empresa
✅ Protección de endpoints
✅ Manejo de errores
✅ Performance básico

Ejecutar: python probar_jwt_completo.py
"""

import requests
import time
import json
from typing import Dict, List, Tuple

class PruebasJWTCompletas:
    """Suite completa de pruebas JWT"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.tokens = {}
        self.resultados = {
            "login": [],
            "acceso_permitido": [],
            "acceso_denegado": [],
            "endpoints_protegidos": [],
            "performance": []
        }
    
    def print_header(self, title: str):
        """Imprimir header de sección"""
        print(f"\n{'='*70}")
        print(f"🧪 {title}")
        print('='*70)
    
    def print_test(self, test: str, resultado: bool, detalle: str = ""):
        """Imprimir resultado de test"""
        icon = "✅" if resultado else "❌"
        print(f"{icon} {test}")
        if detalle:
            print(f"   📝 {detalle}")
    
    def verificar_api_disponible(self) -> bool:
        """Verificar que la API esté corriendo"""
        try:
            response = requests.get(f"{self.base_url}/docs", timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def test_login_todas_empresas(self):
        """Probar login con todas las empresas"""
        self.print_header("PRUEBAS DE LOGIN POR EMPRESA")
        
        # Usuarios de prueba por empresa
        usuarios_empresas = [
            ("admin_interbank", "Interbank"),
            ("admin_banbif", "BanBif"),
            ("admin_nacion", "BancodelaNacion"),
            ("admin_bcrp", "BCRP"),
            ("admin_pichincha", "BancoPichincha"),
            ("admin_bbva", "BBVA"),
            ("admin_bcp", "BCP"),
            ("admin_scotiabank", "ScotiabankPE")
        ]
        
        print("🔐 Probando login para todas las empresas:")
        print("-" * 70)
        
        for username, empresa_esperada in usuarios_empresas:
            try:
                # Intentar login
                login_data = {"username": username, "password": "password123"}
                response = requests.post(f"{self.base_url}/auth/login", json=login_data, timeout=5)
                
                if response.status_code == 200:
                    data = response.json()
                    token = data.get("access_token")
                    empresa_obtenida = data.get("empresa_nombre", "N/A")
                    
                    # Guardar token para pruebas posteriores
                    self.tokens[username] = token
                    
                    # Validar empresa
                    empresa_correcta = empresa_esperada.lower() in empresa_obtenida.lower()
                    
                    self.print_test(f"Login {username}", True, 
                                  f"Empresa: {empresa_obtenida}")
                    
                    self.resultados["login"].append({
                        "username": username,
                        "success": True,
                        "empresa": empresa_obtenida,
                        "token_length": len(token) if token else 0
                    })
                    
                else:
                    self.print_test(f"Login {username}", False, 
                                  f"Status: {response.status_code}")
                    
                    self.resultados["login"].append({
                        "username": username,
                        "success": False,
                        "error": f"HTTP {response.status_code}"
                    })
            
            except Exception as e:
                self.print_test(f"Login {username}", False, f"Error: {str(e)}")
                self.resultados["login"].append({
                    "username": username,
                    "success": False,
                    "error": str(e)
                })
        
        exitosos = len([r for r in self.resultados["login"] if r.get("success", False)])
        print(f"\n📊 Resumen: {exitosos}/{len(usuarios_empresas)} logins exitosos")
    
    def test_acceso_por_empresa(self):
        """Probar control de acceso por empresa"""
        self.print_header("CONTROL DE ACCESO POR EMPRESA")
        
        # Mapeo de usuarios a sus cuentas permitidas
        acceso_permitido = [
            ("admin_interbank", "Interbank"),
            ("admin_bcp", "BCPComunica"),
            ("admin_bbva", "bbva_peru"),
            ("admin_scotiabank", "ScotiabankPE")
        ]
        
        # Acceso que debe ser denegado (cross-empresa)
        acceso_denegado = [
            ("admin_interbank", "BCPComunica"),  # Interbank → BCP
            ("admin_bcp", "Interbank"),          # BCP → Interbank
            ("admin_bbva", "ScotiabankPE"),      # BBVA → Scotiabank
            ("admin_scotiabank", "bbva_peru")    # Scotiabank → BBVA
        ]
        
        print("✅ Probando acceso PERMITIDO (misma empresa):")
        print("-" * 70)
        
        for username, cuenta in acceso_permitido:
            if username in self.tokens:
                try:
                    headers = {"Authorization": f"Bearer {self.tokens[username]}"}
                    response = requests.get(
                        f"{self.base_url}/regression/predict/{cuenta}?fecha=2025-07-11",
                        headers=headers, timeout=5
                    )
                    
                    permitido = response.status_code in [200, 422]  # 200 OK o 422 validation error
                    self.print_test(f"{username} → {cuenta}", permitido,
                                  f"Status: {response.status_code}")
                    
                    self.resultados["acceso_permitido"].append({
                        "username": username,
                        "cuenta": cuenta,
                        "permitido": permitido,
                        "status_code": response.status_code
                    })
                
                except Exception as e:
                    self.print_test(f"{username} → {cuenta}", False, f"Error: {str(e)}")
        
        print("\n🚫 Probando acceso DENEGADO (diferente empresa):")
        print("-" * 70)
        
        for username, cuenta in acceso_denegado:
            if username in self.tokens:
                try:
                    headers = {"Authorization": f"Bearer {self.tokens[username]}"}
                    response = requests.get(
                        f"{self.base_url}/regression/predict/{cuenta}?fecha=2025-07-11",
                        headers=headers, timeout=5
                    )
                    
                    denegado = response.status_code == 403  # Debe ser 403 Forbidden
                    self.print_test(f"{username} → {cuenta}", denegado,
                                  f"Status: {response.status_code} (esperado: 403)")
                    
                    self.resultados["acceso_denegado"].append({
                        "username": username,
                        "cuenta": cuenta,
                        "denegado": denegado,
                        "status_code": response.status_code
                    })
                
                except Exception as e:
                    self.print_test(f"{username} → {cuenta}", False, f"Error: {str(e)}")
    
    def test_endpoints_protegidos(self):
        """Probar que todos los endpoints estén protegidos"""
        self.print_header("PROTECCIÓN DE ENDPOINTS")
        
        # Lista de endpoints que deben estar protegidos
        endpoints_protegidos = [
            ("GET", "/regression/predict/Interbank?fecha=2025-07-11"),
            ("GET", "/regression/model-info/Interbank"),
            ("GET", "/regression/metrics/Interbank"),
            ("GET", "/regression/available-accounts"),
            ("GET", "/regression/users"),
            ("GET", "/regression/features/Interbank")
        ]
        
        print("🛡️ Verificando protección de endpoints (sin token):")
        print("-" * 70)
        
        for method, endpoint in endpoints_protegidos:
            try:
                if method == "GET":
                    response = requests.get(f"{self.base_url}{endpoint}", timeout=5)
                elif method == "POST":
                    response = requests.post(f"{self.base_url}{endpoint}", json={}, timeout=5)
                
                protegido = response.status_code == 401  # Debe ser 401 Unauthorized
                self.print_test(f"{method} {endpoint}", protegido,
                              f"Status: {response.status_code} (esperado: 401)")
                
                self.resultados["endpoints_protegidos"].append({
                    "method": method,
                    "endpoint": endpoint,
                    "protegido": protegido,
                    "status_code": response.status_code
                })
            
            except Exception as e:
                self.print_test(f"{method} {endpoint}", False, f"Error: {str(e)}")
    
    def test_tokens_invalidos(self):
        """Probar manejo de tokens inválidos"""
        self.print_header("MANEJO DE TOKENS INVÁLIDOS")
        
        tokens_invalidos = [
            ("Token vacío", ""),
            ("Token inválido", "invalid.token.here"),
            ("Token malformado", "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.invalid"),
            ("Sin Bearer", "just-a-token-without-bearer")
        ]
        
        print("🔍 Probando tokens inválidos:")
        print("-" * 70)
        
        for descripcion, token_invalido in tokens_invalidos:
            try:
                headers = {"Authorization": f"Bearer {token_invalido}"}
                response = requests.get(
                    f"{self.base_url}/regression/predict/Interbank?fecha=2025-07-11",
                    headers=headers, timeout=5
                )
                
                rechazado = response.status_code == 401
                self.print_test(descripcion, rechazado,
                              f"Status: {response.status_code} (esperado: 401)")
            
            except Exception as e:
                self.print_test(descripcion, False, f"Error: {str(e)}")
    
    def test_credenciales_incorrectas(self):
        """Probar login con credenciales incorrectas"""
        self.print_header("CREDENCIALES INCORRECTAS")
        
        credenciales_incorrectas = [
            ("admin_interbank", "password_incorrecto"),
            ("usuario_inexistente", "password123"),
            ("admin_interbank", ""),
            ("", "password123")
        ]
        
        print("🔐 Probando credenciales incorrectas:")
        print("-" * 70)
        
        for username, password in credenciales_incorrectas:
            try:
                login_data = {"username": username, "password": password}
                response = requests.post(f"{self.base_url}/auth/login", json=login_data, timeout=5)
                
                rechazado = response.status_code == 401
                self.print_test(f"Login: {username}/{password[:3]}...", rechazado,
                              f"Status: {response.status_code} (esperado: 401)")
            
            except Exception as e:
                self.print_test(f"Login: {username}", False, f"Error: {str(e)}")
    
    def test_performance_basico(self):
        """Pruebas básicas de performance"""
        self.print_header("PRUEBAS DE PERFORMANCE")
        
        if "admin_interbank" not in self.tokens:
            print("❌ No hay token disponible para pruebas de performance")
            return
        
        print("⚡ Midiendo tiempos de respuesta:")
        print("-" * 70)
        
        headers = {"Authorization": f"Bearer {self.tokens['admin_interbank']}"}
        
        # Test de múltiples requests
        tiempos = []
        for i in range(5):
            start_time = time.time()
            try:
                response = requests.get(
                    f"{self.base_url}/regression/predict/Interbank?fecha=2025-07-11",
                    headers=headers, timeout=5
                )
                end_time = time.time()
                tiempo = end_time - start_time
                tiempos.append(tiempo)
                
                print(f"   Request {i+1}: {tiempo:.3f}s (Status: {response.status_code})")
            
            except Exception as e:
                print(f"   Request {i+1}: Error - {str(e)}")
        
        if tiempos:
            tiempo_promedio = sum(tiempos) / len(tiempos)
            tiempo_max = max(tiempos)
            tiempo_min = min(tiempos)
            
            print(f"\n📊 Estadísticas de performance:")
            print(f"   • Tiempo promedio: {tiempo_promedio:.3f}s")
            print(f"   • Tiempo mínimo: {tiempo_min:.3f}s")
            print(f"   • Tiempo máximo: {tiempo_max:.3f}s")
            
            # Evaluar performance
            performance_ok = tiempo_promedio < 1.0  # Menos de 1 segundo
            self.print_test("Performance aceptable", performance_ok,
                          f"Promedio: {tiempo_promedio:.3f}s")
            
            self.resultados["performance"] = {
                "promedio": tiempo_promedio,
                "minimo": tiempo_min,
                "maximo": tiempo_max,
                "aceptable": performance_ok
            }
    
    def generar_reporte_final(self):
        """Generar reporte final de todas las pruebas"""
        self.print_header("REPORTE FINAL DE PRUEBAS")
        
        # Calcular estadísticas
        total_logins = len(self.resultados["login"])
        logins_exitosos = len([r for r in self.resultados["login"] if r.get("success", False)])
        
        total_acceso_permitido = len(self.resultados["acceso_permitido"])
        accesos_exitosos = len([r for r in self.resultados["acceso_permitido"] if r.get("permitido", False)])
        
        total_acceso_denegado = len(self.resultados["acceso_denegado"])
        denegaciones_correctas = len([r for r in self.resultados["acceso_denegado"] if r.get("denegado", False)])
        
        total_endpoints = len(self.resultados["endpoints_protegidos"])
        endpoints_protegidos = len([r for r in self.resultados["endpoints_protegidos"] if r.get("protegido", False)])
        
        print("📊 RESUMEN DE RESULTADOS:")
        print("-" * 70)
        print(f"🔐 Login por empresa:        {logins_exitosos}/{total_logins} exitosos")
        print(f"✅ Acceso permitido:         {accesos_exitosos}/{total_acceso_permitido} correctos")
        print(f"🚫 Acceso denegado:          {denegaciones_correctas}/{total_acceso_denegado} correctos")
        print(f"🛡️ Endpoints protegidos:     {endpoints_protegidos}/{total_endpoints} protegidos")
        
        if self.resultados["performance"]:
            perf = self.resultados["performance"]
            print(f"⚡ Performance:              {perf['promedio']:.3f}s promedio")
        
        # Calcular puntuación general
        puntuaciones = []
        if total_logins > 0:
            puntuaciones.append(logins_exitosos / total_logins)
        if total_acceso_permitido > 0:
            puntuaciones.append(accesos_exitosos / total_acceso_permitido)
        if total_acceso_denegado > 0:
            puntuaciones.append(denegaciones_correctas / total_acceso_denegado)
        if total_endpoints > 0:
            puntuaciones.append(endpoints_protegidos / total_endpoints)
        
        if puntuaciones:
            puntuacion_general = sum(puntuaciones) / len(puntuaciones) * 100
            
            print(f"\n🎯 PUNTUACIÓN GENERAL: {puntuacion_general:.1f}/100")
            
            if puntuacion_general >= 95:
                print("🎉 ¡EXCELENTE! Sistema JWT funcionando perfectamente")
            elif puntuacion_general >= 80:
                print("✅ BUENO: Sistema JWT funcionando correctamente")
            elif puntuacion_general >= 60:
                print("⚠️ REGULAR: Sistema JWT con algunas fallas")
            else:
                print("❌ CRÍTICO: Sistema JWT requiere revisión")
        
        # Guardar reporte en archivo
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        reporte_file = f"reporte_pruebas_jwt_{timestamp}.json"
        
        with open(reporte_file, 'w', encoding='utf-8') as f:
            json.dump(self.resultados, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Reporte detallado guardado en: {reporte_file}")
    
    def ejecutar_todas_las_pruebas(self):
        """Ejecutar suite completa de pruebas"""
        print("🧪 SUITE COMPLETA DE PRUEBAS JWT")
        print("=" * 80)
        print("Validando sistema de autenticación JWT...")
        
        # Verificar que la API esté disponible
        if not self.verificar_api_disponible():
            print("❌ API no disponible en http://localhost:8000")
            print("💡 Iniciar con: python run_api.py")
            return False
        
        print("✅ API disponible, comenzando pruebas...")
        
        # Ejecutar todas las pruebas
        self.test_login_todas_empresas()
        self.test_acceso_por_empresa()
        self.test_endpoints_protegidos()
        self.test_tokens_invalidos()
        self.test_credenciales_incorrectas()
        self.test_performance_basico()
        
        # Generar reporte final
        self.generar_reporte_final()
        
        return True

def main():
    """Función principal"""
    pruebas = PruebasJWTCompletas()
    pruebas.ejecutar_todas_las_pruebas()

if __name__ == "__main__":
    main()
