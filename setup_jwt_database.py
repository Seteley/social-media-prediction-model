#!/usr/bin/env python3
# =============================================================================
# SCRIPT DE INICIALIZACIÓN DE DATOS PARA JWT
# =============================================================================

"""
Script para crear datos de prueba en la base de datos para el sistema JWT
"""

import duckdb
from pathlib import Path
import sys
import os

# Agregar el directorio del proyecto al path
current_dir = Path(__file__).parent
project_dir = current_dir.parent
sys.path.append(str(project_dir))

from app.auth.jwt_config import get_password_hash

def init_database():
    """Inicializa la base de datos con datos de prueba"""
    
    db_path = "data/base_de_datos/social_media.duckdb"
    
    print("🔄 Inicializando base de datos para JWT...")
    
    # Verificar que el archivo de esquema existe
    schema_file = Path("data/base_de_datos/scripts/createtable.sql")
    if not schema_file.exists():
        print(f"❌ No se encontró el archivo de esquema: {schema_file}")
        return False
    
    try:
        # Conectar a la base de datos
        conn = duckdb.connect(db_path)
        
        # Ejecutar el script de creación de tablas
        print("📋 Ejecutando script de creación de tablas...")
        with open(schema_file, 'r', encoding='utf-8') as f:
            schema_sql = f.read()
        
        conn.execute(schema_sql)
        
        # Insertar datos de prueba
        print("📊 Insertando datos de prueba...")
        
        # 1. Crear empresas
        empresas = [
            (1, "Banco Interbank", "2025-01-01"),
            (2, "Banco BCP", "2025-01-01"),
            (3, "Banco BBVA", "2025-01-01"),
            (4, "Scotiabank", "2025-01-01"),
            (5, "Demo Company", "2025-01-01")
        ]
        
        for empresa in empresas:
            conn.execute("""
                INSERT OR REPLACE INTO empresa (id_empresa, nombre, fecha_registro)
                VALUES (?, ?, ?)
            """, empresa)
        
        # 2. Crear usuarios de cuentas de redes sociales
        usuarios = [
            (1, 1, "Interbank", "Banco Interbank Oficial", "2025-01-01"),
            (2, 2, "BCPComunica", "BCP Comunica", "2025-01-01"),
            (3, 3, "bbva_peru", "BBVA Perú", "2025-01-01"),
            (4, 4, "ScotiabankPE", "Scotiabank Perú", "2025-01-01"),
            (5, 1, "InterFinance", "Interbank Finanzas", "2025-01-01"),
            (6, 5, "TestAccount", "Cuenta de Pruebas", "2025-01-01")
        ]
        
        for usuario in usuarios:
            conn.execute("""
                INSERT OR REPLACE INTO usuario (id_usuario, id_empresa, cuenta, nombre, fecha_registro)
                VALUES (?, ?, ?, ?, ?)
            """, usuario)
        
        # 3. Crear usuarios de acceso (para login JWT)
        usuarios_acceso = [
            # Admin general
            (1, 1, "admin", get_password_hash("admin123"), "admin", True),
            
            # Usuarios por empresa
            (2, 1, "interbank_user", get_password_hash("inter123"), "user", True),
            (3, 2, "bcp_user", get_password_hash("bcp123"), "user", True),
            (4, 3, "bbva_user", get_password_hash("bbva123"), "user", True),
            (5, 4, "scotia_user", get_password_hash("scotia123"), "user", True),
            (6, 5, "demo_user", get_password_hash("demo123"), "user", True),
            
            # Usuarios adicionales
            (7, 1, "interbank_admin", get_password_hash("interadmin123"), "admin", True),
            (8, 2, "bcp_admin", get_password_hash("bcpadmin123"), "admin", True)
        ]
        
        for usuario_acceso in usuarios_acceso:
            conn.execute("""
                INSERT OR REPLACE INTO usuario_acceso 
                (id_usuario_acceso, id_empresa, username, password_hash, rol, activo)
                VALUES (?, ?, ?, ?, ?, ?)
            """, usuario_acceso)
        
        # 4. Insertar algunas métricas de ejemplo para Interbank
        metricas_interbank = [
            (1, 1, "2025-07-09 07:18:22", 304222, 66926, 71),
            (2, 1, "2025-07-09 08:27:42", 304221, 66926, 71),
            (3, 1, "2025-07-09 09:23:14", 304220, 66926, 71),
            (4, 1, "2025-07-10 07:20:15", 304237, 66934, 71),
            (5, 1, "2025-07-11 07:20:45", 304253, 66937, 70)
        ]
        
        for metrica in metricas_interbank:
            conn.execute("""
                INSERT OR REPLACE INTO metrica (id_metrica, id_usuario, hora, seguidores, tweets, siguiendo)
                VALUES (?, ?, ?, ?, ?, ?)
            """, metrica)
        
        conn.commit()
        conn.close()
        
        print("✅ Base de datos inicializada exitosamente!")
        print("\n📋 CREDENCIALES DE PRUEBA:")
        print("=" * 50)
        print("🔑 Admin general:")
        print("   username: admin")
        print("   password: admin123")
        print("   empresa: Banco Interbank")
        print()
        print("👤 Usuarios por empresa:")
        credenciales = [
            ("interbank_user", "inter123", "Banco Interbank"),
            ("bcp_user", "bcp123", "Banco BCP"),
            ("bbva_user", "bbva123", "Banco BBVA"),
            ("scotia_user", "scotia123", "Scotiabank"),
            ("demo_user", "demo123", "Demo Company")
        ]
        
        for username, password, empresa in credenciales:
            print(f"   username: {username}")
            print(f"   password: {password}")
            print(f"   empresa: {empresa}")
            print()
        
        return True
        
    except Exception as e:
        print(f"❌ Error inicializando base de datos: {e}")
        import traceback
        traceback.print_exc()
        return False

def verify_database():
    """Verifica que los datos se crearon correctamente"""
    print("\n🔍 Verificando datos creados...")
    
    db_path = "data/base_de_datos/social_media.duckdb"
    
    try:
        conn = duckdb.connect(db_path)
        
        # Verificar empresas
        empresas = conn.execute("SELECT COUNT(*) FROM empresa").fetchone()[0]
        print(f"   Empresas creadas: {empresas}")
        
        # Verificar usuarios de redes sociales
        usuarios = conn.execute("SELECT COUNT(*) FROM usuario").fetchone()[0]
        print(f"   Cuentas de redes sociales: {usuarios}")
        
        # Verificar usuarios de acceso
        usuarios_acceso = conn.execute("SELECT COUNT(*) FROM usuario_acceso").fetchone()[0]
        print(f"   Usuarios de acceso: {usuarios_acceso}")
        
        # Verificar métricas
        metricas = conn.execute("SELECT COUNT(*) FROM metrica").fetchone()[0]
        print(f"   Métricas de ejemplo: {metricas}")
        
        # Mostrar detalle de usuarios por empresa
        print(f"\n📊 Detalle por empresa:")
        query = """
        SELECT e.nombre, ua.username, ua.rol, 
               COUNT(u.id_usuario) as cuentas_redes_sociales
        FROM empresa e
        LEFT JOIN usuario_acceso ua ON e.id_empresa = ua.id_empresa
        LEFT JOIN usuario u ON e.id_empresa = u.id_empresa
        GROUP BY e.nombre, ua.username, ua.rol
        ORDER BY e.nombre, ua.rol DESC
        """
        
        results = conn.execute(query).fetchall()
        current_empresa = None
        
        for row in results:
            empresa, username, rol, cuentas = row
            if empresa != current_empresa:
                print(f"\n   🏢 {empresa}:")
                current_empresa = empresa
            print(f"      👤 {username} ({rol}) - {cuentas} cuentas")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Error verificando base de datos: {e}")
        return False

def main():
    """Función principal"""
    print("🔐 INICIALIZACIÓN DE SISTEMA JWT")
    print("=" * 50)
    
    # Crear directorio de base de datos si no existe
    db_dir = Path("data/base_de_datos")
    db_dir.mkdir(parents=True, exist_ok=True)
    
    if init_database():
        verify_database()
        
        print("\n🎉 SISTEMA JWT LISTO!")
        print("=" * 50)
        print("🚀 Ahora puedes:")
        print("   1. Iniciar la API: python run_api.py")
        print("   2. Hacer login: POST /auth/login")
        print("   3. Usar endpoints protegidos con el token JWT")
        print()
        print("📖 Ejemplo de login:")
        print('   curl -X POST "http://localhost:8000/auth/login" \\')
        print('        -H "Content-Type: application/json" \\')
        print('        -d \'{"username": "interbank_user", "password": "inter123"}\'')
        
    else:
        print("\n❌ Error en la inicialización")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
