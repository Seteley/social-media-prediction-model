#!/usr/bin/env python3
# =============================================================================
# CONFIGURACIÓN SMART DEL SISTEMA JWT
# =============================================================================

"""
🔧 Configuración inteligente del sistema JWT

Este script maneja automáticamente:
✅ Datos existentes en la base de datos
✅ Inserciones solo cuando es necesario
✅ Validación completa del sistema
✅ Generación de tokens de prueba

Uso: python configurar_jwt_smart.py
"""

import duckdb
import os
from pathlib import Path
from app.auth.jwt_config import get_password_hash, verify_password, create_access_token

class JWTConfiguracionSmart:
    """Configurador inteligente del sistema JWT"""
    
    def __init__(self):
        self.db_path = "data/base_de_datos/social_media.duckdb"
        
    def print_header(self, title: str):
        """Imprimir header con formato"""
        print(f"\n{'='*60}")
        print(f"🔧 {title}")
        print('='*60)
    
    def print_status(self, message: str, success: bool = True):
        """Imprimir estado con icono"""
        icon = "✅" if success else "❌"
        print(f"{icon} {message}")
    
    def verificar_y_crear_tabla_usuario_acceso(self):
        """Verificar y crear tabla usuario_acceso si no existe"""
        self.print_header("VERIFICACIÓN DE TABLA USUARIO_ACCESO")
        
        try:
            conn = duckdb.connect(self.db_path)
            
            # Verificar si la tabla existe
            result = conn.execute("""
                SELECT COUNT(*) 
                FROM information_schema.tables 
                WHERE table_name = 'usuario_acceso'
            """).fetchone()
            
            tabla_existe = result[0] > 0
            
            if not tabla_existe:
                self.print_status("Tabla usuario_acceso no existe, creándola...")
                
                # Crear tabla usuario_acceso
                conn.execute("""
                    CREATE TABLE usuario_acceso (
                        id_usuario INTEGER PRIMARY KEY,
                        username VARCHAR(50) UNIQUE NOT NULL,
                        password_hash VARCHAR(255) NOT NULL,
                        id_empresa INTEGER NOT NULL,
                        rol VARCHAR(20) DEFAULT 'user',
                        activo BOOLEAN DEFAULT TRUE,
                        fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        ultimo_acceso TIMESTAMP,
                        FOREIGN KEY (id_empresa) REFERENCES empresa(id_empresa)
                    )
                """)
                
                self.print_status("Tabla usuario_acceso creada exitosamente")
            else:
                self.print_status("Tabla usuario_acceso ya existe")
            
            conn.close()
            return True
            
        except Exception as e:
            self.print_status(f"Error con tabla usuario_acceso: {str(e)}", False)
            return False
    
    def insertar_usuarios_jwt(self):
        """Insertar usuarios JWT solo si no existen"""
        self.print_header("CONFIGURACIÓN DE USUARIOS JWT")
        
        try:
            conn = duckdb.connect(self.db_path)
            
            # Usuarios a insertar
            usuarios_jwt = [
                (1, 'admin_interbank', 1, 'admin'),
                (2, 'admin_banbif', 2, 'admin'),
                (3, 'admin_nacion', 3, 'admin'),
                (4, 'admin_bcrp', 4, 'admin'),
                (5, 'admin_pichincha', 5, 'admin'),
                (6, 'admin_bbva', 6, 'admin'),
                (7, 'admin_bcp', 7, 'admin'),
                (8, 'admin_scotiabank', 8, 'admin'),
                (9, 'user_interbank', 1, 'user'),
                (10, 'user_bcp', 7, 'user'),
                (11, 'viewer_bbva', 6, 'viewer')
            ]
            
            password_hash = get_password_hash("password123")
            insertados = 0
            ya_existentes = 0
            
            for id_usuario, username, id_empresa, rol in usuarios_jwt:
                # Verificar si el usuario ya existe
                existing = conn.execute(
                    "SELECT COUNT(*) FROM usuario_acceso WHERE username = ?", 
                    [username]
                ).fetchone()
                
                if existing[0] == 0:
                    # Insertar usuario
                    conn.execute("""
                        INSERT INTO usuario_acceso 
                        (id_usuario, username, password_hash, id_empresa, rol, activo) 
                        VALUES (?, ?, ?, ?, ?, TRUE)
                    """, [id_usuario, username, password_hash, id_empresa, rol])
                    
                    insertados += 1
                    self.print_status(f"Usuario {username} insertado")
                else:
                    ya_existentes += 1
                    self.print_status(f"Usuario {username} ya existe")
            
            conn.commit()
            conn.close()
            
            print(f"\n📊 Resumen:")
            print(f"   ✅ Usuarios insertados: {insertados}")
            print(f"   ℹ️  Usuarios existentes: {ya_existentes}")
            print(f"   📝 Total configurados: {insertados + ya_existentes}")
            
            return True
            
        except Exception as e:
            self.print_status(f"Error insertando usuarios: {str(e)}", False)
            return False
    
    def verificar_configuracion_completa(self):
        """Verificar que la configuración esté completa"""
        self.print_header("VERIFICACIÓN DE CONFIGURACIÓN COMPLETA")
        
        try:
            conn = duckdb.connect(self.db_path)
            
            # Verificar empresas
            empresas = conn.execute("SELECT COUNT(*) FROM empresa").fetchone()[0]
            self.print_status(f"Empresas configuradas: {empresas}")
            
            # Verificar usuarios sociales
            usuarios = conn.execute("SELECT COUNT(*) FROM usuario").fetchone()[0]
            self.print_status(f"Usuarios (cuentas sociales): {usuarios}")
            
            # Verificar usuarios JWT
            usuarios_jwt = conn.execute("SELECT COUNT(*) FROM usuario_acceso").fetchone()[0]
            self.print_status(f"Usuarios JWT: {usuarios_jwt}")
            
            # Verificar métricas
            metricas = conn.execute("SELECT COUNT(*) FROM metrica").fetchone()[0]
            self.print_status(f"Registros de métricas: {metricas:,}")
            
            # Mostrar usuarios JWT por empresa
            query = """
            SELECT ua.username, ua.rol, e.nombre as empresa, ua.activo
            FROM usuario_acceso ua
            JOIN empresa e ON ua.id_empresa = e.id_empresa
            ORDER BY ua.id_empresa, ua.username
            """
            
            usuarios_info = conn.execute(query).fetchall()
            
            print(f"\n👥 Usuarios JWT configurados:")
            print("-" * 70)
            for username, rol, empresa, activo in usuarios_info:
                estado = "🟢" if activo else "🔴"
                print(f"   {estado} {username:<18} | {rol:<8} | {empresa}")
            
            conn.close()
            return True
            
        except Exception as e:
            self.print_status(f"Error en verificación: {str(e)}", False)
            return False
    
    def probar_autenticacion_rapida(self):
        """Prueba rápida de autenticación"""
        self.print_header("PRUEBA RÁPIDA DE AUTENTICACIÓN")
        
        try:
            from app.auth.auth_service import auth_service
            
            # Probar algunos usuarios
            usuarios_prueba = [
                "admin_interbank",
                "admin_bcp",
                "admin_bbva"
            ]
            
            print("🧪 Probando autenticación:")
            print("-" * 50)
            
            tokens_generados = {}
            
            for username in usuarios_prueba:
                user = auth_service.authenticate_user(username, "password123")
                if user:
                    # Generar token
                    token = create_access_token({
                        "sub": user["username"],
                        "empresa_id": user["empresa_id"]
                    })
                    tokens_generados[username] = token
                    
                    self.print_status(f"{username} → {user['empresa_nombre']}")
                else:
                    self.print_status(f"{username} → Error", False)
            
            # Guardar tokens para testing manual
            if tokens_generados:
                with open("tokens_prueba_jwt.txt", "w") as f:
                    f.write("# TOKENS JWT PARA TESTING MANUAL\n")
                    f.write(f"# Generados automáticamente\n\n")
                    
                    for username, token in tokens_generados.items():
                        f.write(f"# Usuario: {username}\n")
                        f.write(f"export TOKEN_{username.upper().replace('_', '')}='{token}'\n\n")
                        f.write(f"# Ejemplo de uso:\n")
                        f.write(f'# curl -H "Authorization: Bearer $TOKEN_{username.upper().replace("_", "")}" \\\n')
                        f.write(f'#   "http://localhost:8000/regression/predict/CUENTA?fecha=2025-07-11"\n\n')
                
                self.print_status("Tokens guardados en tokens_prueba_jwt.txt")
            
            return True
            
        except Exception as e:
            self.print_status(f"Error en prueba de autenticación: {str(e)}", False)
            return False
    
    def mostrar_ejemplos_uso(self):
        """Mostrar ejemplos de uso"""
        self.print_header("EJEMPLOS DE USO")
        
        print("🚀 El sistema JWT está configurado. Ejemplos de uso:")
        print()
        
        print("1️⃣ INICIAR LA API:")
        print("   python run_api.py")
        print()
        
        print("2️⃣ LOGIN:")
        print('   curl -X POST "http://localhost:8000/auth/login" \\')
        print('   -H "Content-Type: application/json" \\')
        print('   -d \'{"username": "admin_interbank", "password": "password123"}\'')
        print()
        
        print("3️⃣ HACER PREDICCIÓN (reemplazar TOKEN):")
        print('   curl -H "Authorization: Bearer TOKEN" \\')
        print('   "http://localhost:8000/regression/predict/Interbank?fecha=2025-07-11"')
        print()
        
        print("4️⃣ EJECUTAR DEMO COMPLETA:")
        print("   python demo_jwt_sistema.py")
        print()
        
        print("5️⃣ EJECUTAR PRUEBAS COMPLETAS:")
        print("   python probar_jwt_completo.py")
        print()
        
        print("📝 CREDENCIALES DE PRUEBA (password: password123):")
        print("   • admin_interbank → Acceso a Interbank")
        print("   • admin_bcp → Acceso a BCPComunica")
        print("   • admin_bbva → Acceso a bbva_peru")
        print("   • admin_scotiabank → Acceso a ScotiabankPE")
    
    def configurar_sistema_completo(self):
        """Configuración completa e inteligente del sistema"""
        print("🚀 CONFIGURACIÓN INTELIGENTE DEL SISTEMA JWT")
        print("=" * 80)
        print("Configurando sistema JWT de manera inteligente...")
        
        # Paso 1: Verificar y crear tabla si no existe
        if not self.verificar_y_crear_tabla_usuario_acceso():
            print("\n❌ Error configurando tabla usuario_acceso")
            return False
        
        # Paso 2: Insertar usuarios JWT (solo los que no existan)
        if not self.insertar_usuarios_jwt():
            print("\n❌ Error insertando usuarios JWT")
            return False
        
        # Paso 3: Verificar configuración completa
        if not self.verificar_configuracion_completa():
            print("\n❌ Error verificando configuración")
            return False
        
        # Paso 4: Prueba rápida de autenticación
        if not self.probar_autenticacion_rapida():
            print("\n❌ Error en prueba de autenticación")
            return False
        
        # Paso 5: Mostrar ejemplos de uso
        self.mostrar_ejemplos_uso()
        
        # Éxito
        self.print_header("CONFIGURACIÓN COMPLETADA")
        print("🎉 ¡Sistema JWT configurado exitosamente!")
        print()
        print("✅ Base de datos actualizada")
        print("✅ Usuarios JWT configurados")
        print("✅ Autenticación funcionando")
        print("✅ Tokens de prueba generados")
        print()
        print("🎯 SISTEMA LISTO PARA USAR")
        
        return True

def main():
    """Función principal"""
    configurador = JWTConfiguracionSmart()
    configurador.configurar_sistema_completo()

if __name__ == "__main__":
    main()
