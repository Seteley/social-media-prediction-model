#!/usr/bin/env python3
"""
Script para probar el sistema JWT usando solo bcrypt (sin passlib)
"""

import sys
import os
import duckdb
import bcrypt

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def hash_password(password: str) -> str:
    """Hash de contraseña usando bcrypt directamente"""
    password_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode('utf-8')

def verify_password(password: str, hashed: str) -> bool:
    """Verificar contraseña usando bcrypt directamente"""
    password_bytes = password.encode('utf-8')
    hashed_bytes = hashed.encode('utf-8')
    return bcrypt.checkpw(password_bytes, hashed_bytes)

def probar_sistema_jwt_simple():
    """Probar el sistema JWT usando funciones básicas"""
    
    print("🧪 PRUEBA SIMPLE DEL SISTEMA JWT (sin passlib)")
    print("=" * 55)
    
    # Credenciales de prueba
    username = "admin_interbank"
    password = "password123"
    
    print(f"🔐 Probando autenticación:")
    print(f"   Usuario: {username}")
    print(f"   Contraseña: {password}")
    
    try:
        # Conectar a la base de datos
        conn = duckdb.connect("data/base_de_datos/social_media.duckdb")
        
        # Buscar usuario
        result = conn.execute("""
            SELECT ua.username, ua.password_hash, ua.id_empresa, ua.rol, ua.activo, e.nombre
            FROM usuario_acceso ua
            JOIN empresa e ON ua.id_empresa = e.id_empresa
            WHERE ua.username = ?
        """, [username]).fetchone()
        
        if not result:
            print("❌ Usuario no encontrado")
            return False
        
        db_username, hash_stored, id_empresa, rol, activo, empresa_nombre = result
        
        print(f"\n📋 Usuario encontrado:")
        print(f"   Empresa: {empresa_nombre} (ID: {id_empresa})")
        print(f"   Rol: {rol}")
        print(f"   Activo: {'Sí' if activo else 'No'}")
        
        if not activo:
            print("❌ Usuario inactivo")
            return False
        
        # Verificar contraseña usando bcrypt directamente
        if verify_password(password, hash_stored):
            print("✅ ¡Contraseña correcta!")
            print("🎉 ¡Autenticación exitosa!")
            
            # Simular creación de token (sin JWT real por simplicidad)
            print(f"\n🎫 Token simulado para usuario:")
            print(f"   Subject: {username}")
            print(f"   Empresa autorizada: {id_empresa}")
            print(f"   Rol: {rol}")
            
            print("\n🎉 ¡Sistema de autenticación funcionando correctamente!")
            
            # Información para pruebas con API real
            print("\n🌐 PARA PROBAR CON LA API:")
            print("=" * 35)
            print("1. Iniciar API: uvicorn app.main:app --reload")
            print("2. Probar login:")
            print(f"""   curl -X POST "http://localhost:8000/auth/login" \\
        -H "Content-Type: application/json" \\
        -d '{{"username": "{username}", "password": "{password}"}}'""")
            
            return True
            
        else:
            print("❌ Contraseña incorrecta")
            print(f"   Hash almacenado: {hash_stored[:50]}...")
            
            # Verificar si el hash es válido
            try:
                # Intentar verificar con una contraseña de prueba
                test_result = verify_password("test", hash_stored)
                print("   El formato del hash parece válido")
            except Exception as e:
                print(f"   ⚠️ Formato de hash problemático: {e}")
            
            return False
            
    except Exception as e:
        print(f"❌ Error durante la prueba: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        try:
            conn.close()
        except:
            pass

def mostrar_info_usuarios():
    """Mostrar información de todos los usuarios"""
    print("\n👥 TODOS LOS USUARIOS DE PRUEBA:")
    print("=" * 40)
    
    try:
        conn = duckdb.connect("data/base_de_datos/social_media.duckdb")
        
        usuarios = conn.execute("""
            SELECT ua.username, ua.rol, ua.activo, e.nombre as empresa, ua.password_hash
            FROM usuario_acceso ua
            JOIN empresa e ON ua.id_empresa = e.id_empresa
            ORDER BY ua.rol, ua.username
        """).fetchall()
        
        if not usuarios:
            print("❌ No se encontraron usuarios en la base de datos")
            return
        
        for username, rol, activo, empresa, hash_password in usuarios:
            estado = "🟢 ACTIVO" if activo else "🔴 INACTIVO"
            
            # Verificar si el hash funciona
            try:
                hash_valido = verify_password("password123", hash_password)
                hash_status = "✅" if hash_valido else "❌"
            except:
                hash_status = "⚠️"
            
            print(f"   {hash_status} {username}")
            print(f"      Empresa: {empresa}")
            print(f"      Rol: {rol} | {estado}")
            print(f"      Hash válido: {'Sí' if hash_status == '✅' else 'No'}")
            print()
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error al obtener usuarios: {e}")

if __name__ == "__main__":
    exito = probar_sistema_jwt_simple()
    mostrar_info_usuarios()
    
    if exito:
        print("🚀 ¡El sistema está listo!")
        print("💡 Puedes iniciar la API y probar el login real.")
    else:
        print("⚠️ Hay problemas que necesitan ser resueltos.")
