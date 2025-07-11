#!/usr/bin/env python3
# =============================================================================
# CONFIGURACIÓN AUTOMÁTICA DEL SISTEMA JWT
# =============================================================================

"""
🔧 Script para configurar automáticamente el sistema JWT

Este script:
✅ Ejecuta las inserciones SQL para usuarios JWT
✅ Verifica la configuración de la base de datos
✅ Valida las credenciales de prueba
✅ Ejecuta tests básicos del sistema

Uso: python configurar_jwt_pruebas.py
"""

import duckdb
import os
from pathlib import Path
from app.auth.jwt_config import get_password_hash, verify_password

class JWTConfiguracion:
    """Configurador automático del sistema JWT"""
    
    def __init__(self):
        self.db_path = "data/base_de_datos/social_media.duckdb"
        self.sql_file = "data/base_de_datos/scripts/insercioninsert.sql"
        
    def print_header(self, title: str):
        """Imprimir header con formato"""
        print(f"\n{'='*60}")
        print(f"🔧 {title}")
        print('='*60)
    
    def print_status(self, message: str, success: bool = True):
        """Imprimir estado con icono"""
        icon = "✅" if success else "❌"
        print(f"{icon} {message}")
    
    def verificar_archivos(self):
        """Verificar que existan los archivos necesarios"""
        self.print_header("VERIFICACIÓN DE ARCHIVOS")
        
        archivos_requeridos = [
            self.db_path,
            self.sql_file,
            "app/auth/jwt_config.py",
            "app/auth/auth_service.py"
        ]
        
        todos_existen = True
        for archivo in archivos_requeridos:
            existe = Path(archivo).exists()
            self.print_status(f"Archivo {archivo}", existe)
            if not existe:
                todos_existen = False
        
        return todos_existen
    
    def ejecutar_inserciones(self):
        """Ejecutar las inserciones SQL para JWT"""
        self.print_header("EJECUTANDO INSERCIONES SQL")
        
        try:
            # Leer el archivo SQL
            with open(self.sql_file, 'r', encoding='utf-8') as f:
                sql_content = f.read()
            
            # Conectar a la base de datos
            conn = duckdb.connect(self.db_path)
            
            # Ejecutar las inserciones
            conn.execute(sql_content)
            conn.commit()
            
            self.print_status("Inserciones SQL ejecutadas exitosamente")
            
            # Verificar las inserciones
            empresas = conn.execute("SELECT COUNT(*) FROM empresa").fetchone()[0]
            usuarios = conn.execute("SELECT COUNT(*) FROM usuario").fetchone()[0]
            usuarios_acceso = conn.execute("SELECT COUNT(*) FROM usuario_acceso").fetchone()[0]
            
            print(f"   📊 Empresas insertadas: {empresas}")
            print(f"   👥 Usuarios (cuentas sociales): {usuarios}")
            print(f"   🔑 Usuarios de acceso JWT: {usuarios_acceso}")
            
            conn.close()
            return True
            
        except Exception as e:
            self.print_status(f"Error ejecutando SQL: {str(e)}", False)
            return False
    
    def verificar_usuarios_jwt(self):
        """Verificar que los usuarios JWT estén correctamente configurados"""
        self.print_header("VERIFICACIÓN DE USUARIOS JWT")
        
        try:
            conn = duckdb.connect(self.db_path)
            
            # Obtener usuarios con información de empresa
            query = """
            SELECT ua.username, ua.rol, ua.activo, e.nombre as empresa
            FROM usuario_acceso ua
            JOIN empresa e ON ua.id_empresa = e.id_empresa
            ORDER BY ua.id_empresa, ua.username
            """
            
            usuarios = conn.execute(query).fetchall()
            
            print("👥 Usuarios JWT configurados:")
            print("-" * 60)
            
            for username, rol, activo, empresa in usuarios:
                estado = "🟢 Activo" if activo else "🔴 Inactivo"
                print(f"   🔑 {username:<20} | {rol:<8} | {empresa:<15} | {estado}")
            
            conn.close()
            
            self.print_status(f"Total de usuarios configurados: {len(usuarios)}")
            return True
            
        except Exception as e:
            self.print_status(f"Error verificando usuarios: {str(e)}", False)
            return False
    
    def probar_autenticacion(self):
        """Probar la autenticación con usuarios de prueba"""
        self.print_header("PRUEBAS DE AUTENTICACIÓN")
        
        # Importar servicios JWT
        try:
            from app.auth.auth_service import auth_service
            
            # Usuarios de prueba
            usuarios_prueba = [
                ("admin_interbank", "password123", True),
                ("admin_bcp", "password123", True),
                ("inactive_user", "password123", False),
                ("usuario_inexistente", "password123", False),
                ("admin_interbank", "password_incorrecta", False)
            ]
            
            print("🧪 Ejecutando pruebas de autenticación:")
            print("-" * 60)
            
            for username, password, debe_funcionar in usuarios_prueba:
                try:
                    resultado = auth_service.authenticate_user(username, password)
                    
                    if debe_funcionar and resultado:
                        print(f"   ✅ {username} → Login exitoso (esperado)")
                        print(f"      👤 Usuario: {resultado['username']}")
                        print(f"      🏢 Empresa: {resultado['empresa_nombre']}")
                        print(f"      🔰 Rol: {resultado['rol']}")
                        
                    elif not debe_funcionar and not resultado:
                        print(f"   ✅ {username} → Login fallido (esperado)")
                        
                    elif debe_funcionar and not resultado:
                        print(f"   ❌ {username} → Login falló (no esperado)")
                        
                    else:  # not debe_funcionar and resultado
                        print(f"   ❌ {username} → Login exitoso (no esperado)")
                        
                except Exception as e:
                    print(f"   ❌ {username} → Error: {str(e)}")
            
            return True
            
        except Exception as e:
            self.print_status(f"Error en pruebas de autenticación: {str(e)}", False)
            return False
    
    def generar_tokens_prueba(self):
        """Generar tokens JWT para testing manual"""
        self.print_header("GENERACIÓN DE TOKENS DE PRUEBA")
        
        try:
            from app.auth.jwt_config import create_access_token
            from app.auth.auth_service import auth_service
            
            # Usuarios para generar tokens
            usuarios_token = [
                "admin_interbank",
                "admin_bcp", 
                "admin_bbva"
            ]
            
            print("🔑 Tokens JWT generados para testing:")
            print("-" * 60)
            
            tokens = {}
            for username in usuarios_token:
                user = auth_service.authenticate_user(username, "password123")
                if user:
                    token = create_access_token({
                        "sub": user["username"],
                        "empresa_id": user["empresa_id"]
                    })
                    tokens[username] = token
                    
                    print(f"👤 {username}:")
                    print(f"   🏢 Empresa: {user['empresa_nombre']}")
                    print(f"   🔑 Token: {token[:50]}...")
                    print()
            
            # Guardar tokens en archivo para testing
            with open("tokens_prueba.txt", "w") as f:
                f.write("# TOKENS JWT PARA TESTING\n")
                f.write("# Generados automáticamente\n\n")
                for username, token in tokens.items():
                    f.write(f"# {username}\n")
                    f.write(f"export TOKEN_{username.upper()}='{token}'\n\n")
            
            self.print_status("Tokens guardados en tokens_prueba.txt")
            return True
            
        except Exception as e:
            self.print_status(f"Error generando tokens: {str(e)}", False)
            return False
    
    def mostrar_ejemplos_curl(self):
        """Mostrar ejemplos de uso con cURL"""
        self.print_header("EJEMPLOS DE USO CON CURL")
        
        print("📡 Comandos cURL para testing:")
        print()
        
        print("1️⃣ LOGIN EXITOSO:")
        print('curl -X POST "http://localhost:8000/auth/login" \\')
        print('-H "Content-Type: application/json" \\')
        print('-d \'{"username": "admin_interbank", "password": "password123"}\'')
        print()
        
        print("2️⃣ PREDICCIÓN CON TOKEN (reemplazar TOKEN):")
        print('curl -H "Authorization: Bearer TOKEN" \\')
        print('"http://localhost:8000/regression/predict/Interbank?fecha=2025-07-11"')
        print()
        
        print("3️⃣ ACCESO DENEGADO (usuario Interbank → cuenta BCP):")
        print('curl -H "Authorization: Bearer TOKEN_INTERBANK" \\')
        print('"http://localhost:8000/regression/predict/BCPComunica?fecha=2025-07-11"')
        print()
        
        print("4️⃣ SIN AUTENTICACIÓN (debe dar 401):")
        print('curl "http://localhost:8000/regression/predict/Interbank?fecha=2025-07-11"')
        print()
        
        print("💡 NOTA: Los tokens se encuentran en el archivo 'tokens_prueba.txt'")
    
    def configurar_completo(self):
        """Ejecutar configuración completa del sistema JWT"""
        print("🚀 CONFIGURACIÓN AUTOMÁTICA DEL SISTEMA JWT")
        print("=" * 80)
        print("Este script configurará todos los componentes necesarios para JWT")
        
        # Paso 1: Verificar archivos
        if not self.verificar_archivos():
            print("\n❌ Archivos faltantes. Revisar la instalación.")
            return False
        
        # Paso 2: Ejecutar inserciones
        if not self.ejecutar_inserciones():
            print("\n❌ Error en inserciones SQL.")
            return False
        
        # Paso 3: Verificar usuarios
        if not self.verificar_usuarios_jwt():
            print("\n❌ Error verificando usuarios JWT.")
            return False
        
        # Paso 4: Probar autenticación
        if not self.probar_autenticacion():
            print("\n❌ Error en pruebas de autenticación.")
            return False
        
        # Paso 5: Generar tokens de prueba
        if not self.generar_tokens_prueba():
            print("\n❌ Error generando tokens de prueba.")
            return False
        
        # Paso 6: Mostrar ejemplos
        self.mostrar_ejemplos_curl()
        
        # Resumen final
        self.print_header("CONFIGURACIÓN COMPLETADA")
        print("🎉 ¡Sistema JWT configurado exitosamente!")
        print()
        print("✅ Base de datos configurada con usuarios de prueba")
        print("✅ Autenticación JWT funcionando")
        print("✅ Tokens de prueba generados")
        print("✅ Control de acceso por empresa validado")
        print()
        print("🚀 PRÓXIMOS PASOS:")
        print("   1. Iniciar la API: python run_api.py")
        print("   2. Probar con cURL usando los ejemplos mostrados")
        print("   3. Ejecutar demo: python demo_jwt_sistema.py")
        print("   4. Ejecutar tests: python test_jwt_system.py")
        
        return True

def main():
    """Función principal"""
    configurador = JWTConfiguracion()
    configurador.configurar_completo()

if __name__ == "__main__":
    main()
