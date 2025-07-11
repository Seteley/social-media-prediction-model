#!/usr/bin/env python3
"""
Script para probar el login JWT
"""

import duckdb
import bcrypt

def probar_login():
    """Probar login con credenciales"""
    
    username = "admin_interbank"
    password = "password123"
    
    print(f"🔐 Probando login con:")
    print(f"   Usuario: {username}")
    print(f"   Contraseña: {password}")
    
    try:
        conn = duckdb.connect('data/base_de_datos/social_media.duckdb')
        
        # Buscar usuario
        result = conn.execute("""
            SELECT username, password_hash, id_empresa, rol, activo
            FROM usuario_acceso 
            WHERE username = ?
        """, [username]).fetchone()
        
        if not result:
            print("❌ Usuario no encontrado")
            return False
        
        db_username, hash_stored, id_empresa, rol, activo = result
        
        print(f"\n📋 Usuario encontrado:")
        print(f"   Empresa ID: {id_empresa}")
        print(f"   Rol: {rol}")
        print(f"   Activo: {'Sí' if activo else 'No'}")
        
        if not activo:
            print("❌ Usuario inactivo")
            return False
        
        # Verificar contraseña
        password_bytes = password.encode('utf-8')
        hash_bytes = hash_stored.encode('utf-8')
        
        if bcrypt.checkpw(password_bytes, hash_bytes):
            print("✅ ¡Contraseña correcta!")
            print("🎉 ¡Login exitoso!")
            
            # Mostrar información de la empresa
            empresa_result = conn.execute("""
                SELECT nombre FROM empresa WHERE id_empresa = ?
            """, [id_empresa]).fetchone()
            
            if empresa_result:
                print(f"🏢 Empresa: {empresa_result[0]}")
            
            return True
        else:
            print("❌ Contraseña incorrecta")
            print(f"   Hash almacenado: {hash_stored[:50]}...")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    finally:
        conn.close()

if __name__ == "__main__":
    print("🧪 PRUEBA DE LOGIN JWT")
    print("=" * 30)
    probar_login()
