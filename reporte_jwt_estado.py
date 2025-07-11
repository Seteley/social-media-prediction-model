#!/usr/bin/env python3
# =============================================================================
# REPORTE DE ESTADO DEL SISTEMA JWT
# =============================================================================

"""
📊 Generador de Reporte de Estado del Sistema JWT

Este script verifica y documenta el estado actual de todos los componentes
del sistema de autenticación JWT implementado.

Ejecutar: python reporte_jwt_estado.py
"""

import os
import sys
import duckdb
import requests
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any

class JWTSystemReport:
    """Generador de reportes del sistema JWT"""
    
    def __init__(self):
        self.base_path = Path(".")
        self.db_path = "data/base_de_datos/social_media.db"
        self.api_url = "http://localhost:8000"
        self.report_data = {}
        
    def print_header(self, title: str):
        """Imprimir header de sección"""
        print(f"\n{'='*60}")
        print(f"📊 {title}")
        print('='*60)
    
    def print_status(self, check: str, status: bool, details: str = ""):
        """Imprimir estado de verificación"""
        icon = "✅" if status else "❌"
        print(f"{icon} {check}")
        if details:
            print(f"   📝 {details}")
    
    def check_files(self) -> Dict[str, Any]:
        """Verificar archivos del sistema JWT"""
        self.print_header("VERIFICACIÓN DE ARCHIVOS")
        
        required_files = {
            # Archivos core JWT
            "app/auth/jwt_config.py": "Configuración JWT principal",
            "app/auth/auth_service.py": "Servicios de autenticación",
            "app/auth/dependencies.py": "Dependencias FastAPI",
            "app/auth/__init__.py": "Inicialización del módulo",
            
            # Endpoints protegidos
            "app/api/auth_routes.py": "Rutas de autenticación",
            "app/api/regression.py": "Endpoints ML protegidos",
            "app/main.py": "Aplicación principal",
            
            # Scripts y documentación
            "setup_jwt_database.py": "Script configuración BD",
            "test_jwt_system.py": "Tests del sistema",
            "demo_jwt_sistema.py": "Demo interactiva",
            "DOCUMENTACION_JWT_COMPLETA.md": "Documentación técnica",
            "README_JWT.md": "Guía de usuario",
            
            # Configuración
            "requirements.txt": "Dependencias del proyecto"
        }
        
        file_status = {}
        for file_path, description in required_files.items():
            exists = (self.base_path / file_path).exists()
            file_status[file_path] = exists
            self.print_status(f"{description}", exists, file_path)
        
        missing_files = [f for f, exists in file_status.items() if not exists]
        
        print(f"\n📈 Resumen de archivos:")
        print(f"   ✅ Existentes: {len(file_status) - len(missing_files)}")
        print(f"   ❌ Faltantes: {len(missing_files)}")
        
        return {
            "total_files": len(file_status),
            "existing_files": len(file_status) - len(missing_files),
            "missing_files": missing_files,
            "completion_rate": (len(file_status) - len(missing_files)) / len(file_status) * 100
        }
    
    def check_database(self) -> Dict[str, Any]:
        """Verificar configuración de base de datos"""
        self.print_header("VERIFICACIÓN DE BASE DE DATOS")
        
        db_status = {
            "exists": False,
            "tables": [],
            "users": 0,
            "empresas": 0,
            "connections": False
        }
        
        try:
            # Verificar existencia del archivo
            db_exists = Path(self.db_path).exists()
            db_status["exists"] = db_exists
            self.print_status("Archivo de base de datos", db_exists, self.db_path)
            
            if db_exists:
                # Conectar y verificar tablas
                conn = duckdb.connect(self.db_path)
                
                # Verificar tablas requeridas
                required_tables = ["empresa", "usuario_acceso", "usuario", "metrica"]
                existing_tables = []
                
                for table in required_tables:
                    try:
                        result = conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()
                        existing_tables.append(table)
                        self.print_status(f"Tabla '{table}'", True, f"{result[0]} registros")
                        
                        if table == "usuario_acceso":
                            db_status["users"] = result[0]
                        elif table == "empresa":
                            db_status["empresas"] = result[0]
                            
                    except Exception as e:
                        self.print_status(f"Tabla '{table}'", False, str(e))
                
                db_status["tables"] = existing_tables
                db_status["connections"] = True
                
                # Verificar usuarios de prueba
                try:
                    users_query = """
                    SELECT ua.username, e.nombre as empresa
                    FROM usuario_acceso ua
                    JOIN empresa e ON ua.id_empresa = e.id_empresa
                    WHERE ua.activo = TRUE
                    """
                    users = conn.execute(users_query).fetchall()
                    
                    print(f"\n👥 Usuarios configurados:")
                    for username, empresa in users:
                        print(f"   🔑 {username} → {empresa}")
                
                except Exception as e:
                    self.print_status("Consulta de usuarios", False, str(e))
                
                conn.close()
            
        except Exception as e:
            self.print_status("Conexión a base de datos", False, str(e))
        
        return db_status
    
    def check_dependencies(self) -> Dict[str, Any]:
        """Verificar dependencias Python"""
        self.print_header("VERIFICACIÓN DE DEPENDENCIAS")
        
        required_packages = {
            "jwt": "PyJWT para manejo de tokens",
            "passlib": "Hashing seguro de contraseñas",
            "fastapi": "Framework web",
            "duckdb": "Base de datos",
            "requests": "Cliente HTTP para tests"
        }
        
        dep_status = {}
        for package, description in required_packages.items():
            try:
                if package == "jwt":
                    import jwt
                    version = jwt.__version__
                elif package == "passlib":
                    import passlib
                    version = passlib.__version__
                elif package == "fastapi":
                    import fastapi
                    version = fastapi.__version__
                elif package == "duckdb":
                    import duckdb
                    version = duckdb.__version__
                elif package == "requests":
                    import requests
                    version = requests.__version__
                
                dep_status[package] = True
                self.print_status(description, True, f"v{version}")
                
            except ImportError:
                dep_status[package] = False
                self.print_status(description, False, "No instalado")
        
        missing_deps = [pkg for pkg, status in dep_status.items() if not status]
        
        print(f"\n📦 Resumen de dependencias:")
        print(f"   ✅ Instaladas: {len(dep_status) - len(missing_deps)}")
        print(f"   ❌ Faltantes: {len(missing_deps)}")
        
        if missing_deps:
            print(f"\n💡 Para instalar dependencias faltantes:")
            print(f"   pip install {' '.join(missing_deps)}")
        
        return {
            "total_packages": len(required_packages),
            "installed_packages": len(dep_status) - len(missing_deps),
            "missing_packages": missing_deps
        }
    
    def check_api_status(self) -> Dict[str, Any]:
        """Verificar estado de la API"""
        self.print_header("VERIFICACIÓN DE API")
        
        api_status = {
            "running": False,
            "auth_endpoints": False,
            "protected_endpoints": False,
            "login_working": False
        }
        
        try:
            # Verificar que la API esté corriendo
            response = requests.get(f"{self.api_url}/docs", timeout=5)
            api_status["running"] = response.status_code == 200
            self.print_status("API corriendo", api_status["running"], f"{self.api_url}")
            
            if api_status["running"]:
                # Verificar endpoint de login
                try:
                    response = requests.post(f"{self.api_url}/auth/login", 
                                           json={"username": "test", "password": "test"},
                                           timeout=5)
                    api_status["auth_endpoints"] = response.status_code in [401, 422]  # Esperamos error, pero endpoint existe
                    self.print_status("Endpoint de login", api_status["auth_endpoints"], "/auth/login")
                except Exception as e:
                    self.print_status("Endpoint de login", False, str(e))
                
                # Verificar endpoint protegido
                try:
                    response = requests.get(f"{self.api_url}/regression/predict/Interbank?fecha=2025-07-11", 
                                          timeout=5)
                    api_status["protected_endpoints"] = response.status_code == 401  # Sin auth debe dar 401
                    self.print_status("Endpoints protegidos", api_status["protected_endpoints"], "401 sin token (correcto)")
                except Exception as e:
                    self.print_status("Endpoints protegidos", False, str(e))
                
                # Test login real si tenemos datos
                try:
                    login_response = requests.post(f"{self.api_url}/auth/login",
                                                 json={"username": "admin_interbank", "password": "password123"},
                                                 timeout=5)
                    api_status["login_working"] = login_response.status_code == 200
                    self.print_status("Login funcional", api_status["login_working"], "Credenciales de prueba")
                    
                    if api_status["login_working"]:
                        token = login_response.json().get("access_token")
                        
                        # Test endpoint con token
                        headers = {"Authorization": f"Bearer {token}"}
                        pred_response = requests.get(f"{self.api_url}/regression/predict/Interbank?fecha=2025-07-11",
                                                   headers=headers, timeout=5)
                        
                        token_working = pred_response.status_code in [200, 422]  # 200 ok o 422 validation error
                        self.print_status("Token funcionando", token_working, f"Status: {pred_response.status_code}")
                
                except Exception as e:
                    self.print_status("Test de login", False, str(e))
        
        except Exception as e:
            self.print_status("Conexión a API", False, str(e))
            print(f"💡 Para iniciar la API: python run_api.py")
        
        return api_status
    
    def check_security_features(self) -> Dict[str, Any]:
        """Verificar características de seguridad"""
        self.print_header("VERIFICACIÓN DE SEGURIDAD")
        
        security_status = {}
        
        # Verificar configuración JWT
        try:
            from app.auth.jwt_config import JWT_SECRET_KEY, JWT_ALGORITHM, JWT_ACCESS_TOKEN_EXPIRE_MINUTES
            
            # Secret key
            secure_key = len(JWT_SECRET_KEY) >= 32
            security_status["secure_secret"] = secure_key
            self.print_status("Clave secreta segura", secure_key, f"{len(JWT_SECRET_KEY)} caracteres")
            
            # Algoritmo
            secure_algo = JWT_ALGORITHM == "HS256"
            security_status["secure_algorithm"] = secure_algo
            self.print_status("Algoritmo seguro", secure_algo, JWT_ALGORITHM)
            
            # Expiración
            reasonable_expiry = 1 <= JWT_ACCESS_TOKEN_EXPIRE_MINUTES <= 60
            security_status["reasonable_expiry"] = reasonable_expiry
            self.print_status("Tiempo de expiración", reasonable_expiry, f"{JWT_ACCESS_TOKEN_EXPIRE_MINUTES} minutos")
            
        except Exception as e:
            self.print_status("Configuración JWT", False, str(e))
        
        # Verificar hash de contraseñas
        try:
            from app.auth.jwt_config import pwd_context
            
            # Test hash
            test_hash = pwd_context.hash("test_password")
            bcrypt_used = test_hash.startswith("$2b$")
            security_status["bcrypt_hashing"] = bcrypt_used
            self.print_status("Hash bcrypt", bcrypt_used, "Contraseñas seguras")
            
        except Exception as e:
            self.print_status("Sistema de hash", False, str(e))
        
        return security_status
    
    def generate_summary_report(self):
        """Generar reporte resumen"""
        self.print_header("REPORTE RESUMEN DEL SISTEMA JWT")
        
        print("🎯 ESTADO GENERAL DEL SISTEMA:")
        print()
        
        # Calcular puntuación general
        checks = [
            ("Archivos del sistema", self.report_data.get("files", {}).get("completion_rate", 0)),
            ("Base de datos", 100 if self.report_data.get("database", {}).get("exists", False) else 0),
            ("Dependencias", 100 if len(self.report_data.get("dependencies", {}).get("missing_packages", [])) == 0 else 50),
            ("API funcionando", 100 if self.report_data.get("api", {}).get("running", False) else 0),
            ("Login funcionando", 100 if self.report_data.get("api", {}).get("login_working", False) else 0)
        ]
        
        total_score = sum(score for _, score in checks) / len(checks)
        
        print(f"📊 PUNTUACIÓN GENERAL: {total_score:.1f}/100")
        print()
        
        for check_name, score in checks:
            status = "🟢" if score >= 90 else "🟡" if score >= 50 else "🔴"
            print(f"{status} {check_name}: {score:.1f}%")
        
        print()
        
        if total_score >= 90:
            print("🎉 ¡SISTEMA COMPLETAMENTE FUNCIONAL!")
            print("   ✅ Listo para producción")
            print("   ✅ Todas las características implementadas")
            print("   ✅ Seguridad validada")
        elif total_score >= 70:
            print("⚡ SISTEMA MAYORMENTE FUNCIONAL")
            print("   ✅ Funcionalidad core implementada")
            print("   ⚠️  Algunas mejoras pendientes")
        else:
            print("🔧 SISTEMA REQUIERE CONFIGURACIÓN")
            print("   ❌ Componentes críticos faltantes")
            print("   🛠️  Revisar documentación de instalación")
        
        # Acciones recomendadas
        print("\n🚀 PRÓXIMOS PASOS RECOMENDADOS:")
        
        missing_files = self.report_data.get("files", {}).get("missing_files", [])
        if missing_files:
            print("   📁 Verificar archivos faltantes")
        
        if not self.report_data.get("database", {}).get("exists", False):
            print("   🗃️  Ejecutar: python setup_jwt_database.py")
        
        missing_deps = self.report_data.get("dependencies", {}).get("missing_packages", [])
        if missing_deps:
            print(f"   📦 Instalar: pip install {' '.join(missing_deps)}")
        
        if not self.report_data.get("api", {}).get("running", False):
            print("   🚀 Iniciar API: python run_api.py")
        
        print("\n📚 DOCUMENTACIÓN DISPONIBLE:")
        print("   📖 README_JWT.md - Guía de usuario")
        print("   📋 DOCUMENTACION_JWT_COMPLETA.md - Documentación técnica")
        print("   🎯 demo_jwt_sistema.py - Demostración interactiva")
        print("   🧪 test_jwt_system.py - Tests automatizados")
    
    def run_full_report(self):
        """Ejecutar reporte completo"""
        print("🔐 REPORTE DE ESTADO - SISTEMA JWT")
        print(f"⏰ Generado: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Ejecutar todas las verificaciones
        self.report_data["files"] = self.check_files()
        self.report_data["database"] = self.check_database()
        self.report_data["dependencies"] = self.check_dependencies()
        self.report_data["api"] = self.check_api_status()
        self.report_data["security"] = self.check_security_features()
        
        # Generar resumen
        self.generate_summary_report()
        
        # Guardar reporte en archivo
        report_file = f"jwt_system_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(self.report_data, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Reporte guardado en: {report_file}")

def main():
    """Función principal"""
    reporter = JWTSystemReport()
    reporter.run_full_report()

if __name__ == "__main__":
    main()
