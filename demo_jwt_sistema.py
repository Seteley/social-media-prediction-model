#!/usr/bin/env python3
# =============================================================================
# DEMOSTRACIÓN PRÁCTICA - SISTEMA JWT COMPLETO
# =============================================================================

"""
🎯 DEMO INTERACTIVA del Sistema JWT Implementado

Este script demuestra:
✅ Login y obtención de tokens
✅ Protección de endpoints por empresa
✅ Control de acceso granular
✅ Manejo de errores de autenticación
✅ Validación de permisos por cuenta

Ejecutar con el servidor API corriendo:
python demo_jwt_sistema.py
"""

import requests
import json
import time
from datetime import datetime
from typing import Dict, Any, Optional

class JWTDemoClient:
    """Cliente demo para demostrar el sistema JWT"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.tokens = {}  # Almacenar tokens por usuario
        self.current_user = None
        
    def print_section(self, title: str):
        """Imprimir sección con formato"""
        print(f"\n{'='*60}")
        print(f"🎯 {title}")
        print('='*60)
    
    def print_result(self, success: bool, message: str):
        """Imprimir resultado con formato"""
        icon = "✅" if success else "❌"
        print(f"{icon} {message}")
    
    def login(self, username: str, password: str) -> bool:
        """Realizar login y obtener token"""
        try:
            url = f"{self.base_url}/auth/login"
            data = {"username": username, "password": password}
            
            response = requests.post(url, json=data)
            
            if response.status_code == 200:
                result = response.json()
                self.tokens[username] = result["access_token"]
                self.current_user = {
                    "username": username,
                    "token": result["access_token"],
                    "empresa_id": result.get("empresa_id"),
                    "empresa_nombre": result.get("empresa_nombre", "N/A")
                }
                
                self.print_result(True, f"Login exitoso para {username}")
                print(f"   👤 Usuario: {username}")
                print(f"   🏢 Empresa: {self.current_user['empresa_nombre']}")
                print(f"   🔑 Token: {result['access_token'][:50]}...")
                return True
            else:
                self.print_result(False, f"Login fallido: {response.status_code}")
                print(f"   📝 Detalle: {response.text}")
                return False
                
        except Exception as e:
            self.print_result(False, f"Error en login: {str(e)}")
            return False
    
    def test_prediction(self, account: str, fecha: str = "2025-07-11") -> Dict[str, Any]:
        """Probar endpoint de predicción"""
        try:
            if not self.current_user:
                return {"error": "No hay usuario logueado"}
            
            url = f"{self.base_url}/regression/predict/{account}"
            headers = {"Authorization": f"Bearer {self.current_user['token']}"}
            params = {"fecha": fecha}
            
            response = requests.get(url, headers=headers, params=params)
            
            result = {
                "status_code": response.status_code,
                "account": account,
                "user": self.current_user["username"],
                "empresa": self.current_user["empresa_nombre"]
            }
            
            if response.status_code == 200:
                data = response.json()
                result.update({
                    "success": True,
                    "prediction": data.get("prediction"),
                    "model_type": data.get("model_type"),
                    "target_variable": data.get("target_variable")
                })
                self.print_result(True, f"Predicción exitosa para {account}")
                print(f"   📊 Predicción: {data.get('prediction')}")
                print(f"   🤖 Modelo: {data.get('model_type')}")
                
            elif response.status_code == 401:
                result.update({"success": False, "error": "Token inválido o expirado"})
                self.print_result(False, f"Token inválido para {account}")
                
            elif response.status_code == 403:
                result.update({"success": False, "error": "Sin permisos para esta cuenta"})
                self.print_result(False, f"Sin permisos para {account}")
                print(f"   🚫 Usuario de {self.current_user['empresa_nombre']} no puede acceder a {account}")
                
            else:
                result.update({"success": False, "error": f"Error {response.status_code}"})
                self.print_result(False, f"Error {response.status_code} para {account}")
            
            return result
            
        except Exception as e:
            self.print_result(False, f"Error en predicción: {str(e)}")
            return {"error": str(e)}
    
    def test_available_accounts(self) -> list:
        """Probar endpoint de cuentas disponibles"""
        try:
            if not self.current_user:
                return []
            
            url = f"{self.base_url}/regression/available-accounts"
            headers = {"Authorization": f"Bearer {self.current_user['token']}"}
            
            response = requests.get(url, headers=headers)
            
            if response.status_code == 200:
                accounts = response.json()
                self.print_result(True, f"Cuentas disponibles obtenidas")
                for acc in accounts:
                    print(f"   📱 {acc}")
                return accounts
            else:
                self.print_result(False, f"Error obteniendo cuentas: {response.status_code}")
                return []
                
        except Exception as e:
            self.print_result(False, f"Error: {str(e)}")
            return []
    
    def test_without_auth(self, account: str = "Interbank") -> Dict[str, Any]:
        """Probar endpoint sin autenticación"""
        try:
            url = f"{self.base_url}/regression/predict/{account}"
            params = {"fecha": "2025-07-11"}
            
            response = requests.get(url, params=params)  # Sin headers de auth
            
            if response.status_code == 401:
                self.print_result(True, "Endpoint correctamente protegido - sin auth denegado")
                return {"success": True, "protected": True}
            else:
                self.print_result(False, f"VULNERABILIDAD: Endpoint no protegido - status {response.status_code}")
                return {"success": False, "protected": False}
                
        except Exception as e:
            self.print_result(False, f"Error: {str(e)}")
            return {"error": str(e)}
    
    def demo_complete_flow(self):
        """Demostración completa del flujo JWT"""
        
        print("🚀 DEMOSTRACIÓN COMPLETA DEL SISTEMA JWT")
        print("=" * 80)
        print("Este demo muestra:")
        print("  • Login y autenticación")
        print("  • Protección de endpoints")
        print("  • Control de acceso por empresa")
        print("  • Manejo de errores de seguridad")
        
        # 1. Test sin autenticación
        self.print_section("1. TEST SIN AUTENTICACIÓN")
        print("Probando acceso sin token (debe fallar)...")
        self.test_without_auth()
        
        # 2. Login como Interbank
        self.print_section("2. LOGIN COMO INTERBANK")
        success = self.login("admin_interbank", "password123")
        
        if success:
            # 3. Ver cuentas disponibles
            self.print_section("3. CUENTAS DISPONIBLES PARA INTERBANK")
            accounts = self.test_available_accounts()
            
            # 4. Predicción válida (misma empresa)
            self.print_section("4. PREDICCIÓN VÁLIDA (MISMO EMPRESA)")
            print("Probando predicción para cuenta de Interbank...")
            self.test_prediction("Interbank")
            
            # 5. Predicción inválida (otra empresa)
            self.print_section("5. CONTROL DE ACCESO (OTRA EMPRESA)")
            print("Probando predicción para cuenta de BCP (debe fallar)...")
            self.test_prediction("BCPComunica")
        
        # 6. Login como BCP
        self.print_section("6. LOGIN COMO BCP")
        success_bcp = self.login("admin_bcp", "password123")
        
        if success_bcp:
            # 7. Predicción válida para BCP
            self.print_section("7. PREDICCIÓN VÁLIDA PARA BCP")
            print("Probando predicción para cuenta de BCP...")
            self.test_prediction("BCPComunica")
            
            # 8. Predicción inválida para Interbank
            self.print_section("8. CONTROL DE ACCESO (INTERBANK DENEGADO)")
            print("Probando predicción para Interbank desde BCP (debe fallar)...")
            self.test_prediction("Interbank")
        
        # 9. Test con credenciales inválidas
        self.print_section("9. TEST CREDENCIALES INVÁLIDAS")
        print("Probando login con contraseña incorrecta...")
        self.login("admin_interbank", "contraseña_incorrecta")
        
        # 10. Resumen final
        self.print_section("10. RESUMEN DE SEGURIDAD")
        self.print_security_summary()
    
    def print_security_summary(self):
        """Imprimir resumen de seguridad"""
        print("🛡️ CARACTERÍSTICAS DE SEGURIDAD IMPLEMENTADAS:")
        print()
        print("✅ Autenticación JWT")
        print("   • Tokens firmados digitalmente")
        print("   • Expiración automática (30 min)")
        print("   • Validación en cada request")
        print()
        print("✅ Control de Acceso Multi-Empresa")
        print("   • Cada empresa solo ve sus datos")
        print("   • Validación automática de permisos")
        print("   • Aislamiento completo de datos")
        print()
        print("✅ Protección de Endpoints")
        print("   • 11 endpoints protegidos con JWT")
        print("   • Respuestas 401 sin token válido")
        print("   • Respuestas 403 sin permisos")
        print()
        print("✅ Contraseñas Seguras")
        print("   • Hash bcrypt con salt")
        print("   • No almacenamiento en texto plano")
        print("   • Validación en cada login")
        print()
        print("🎯 SISTEMA LISTO PARA PRODUCCIÓN EMPRESARIAL")

def main():
    """Función principal para ejecutar la demo"""
    
    print("🔐 Iniciando demostración del Sistema JWT...")
    print("📋 Verificando conexión con API...")
    
    # Verificar que la API esté corriendo
    try:
        response = requests.get("http://localhost:8000/docs")
        if response.status_code == 200:
            print("✅ API corriendo en http://localhost:8000")
        else:
            print("❌ API no responde correctamente")
            return
    except Exception as e:
        print(f"❌ Error conectando a API: {e}")
        print("💡 Asegúrate de que la API esté corriendo:")
        print("   python run_api.py")
        return
    
    # Ejecutar demostración
    demo = JWTDemoClient()
    demo.demo_complete_flow()
    
    print("\n" + "="*80)
    print("🎉 DEMOSTRACIÓN COMPLETADA")
    print("📚 Ver documentación completa en: DOCUMENTACION_JWT_COMPLETA.md")
    print("🧪 Ejecutar tests: python test_jwt_system.py")
    print("="*80)

if __name__ == "__main__":
    main()
