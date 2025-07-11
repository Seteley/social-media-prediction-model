#!/usr/bin/env python3
"""
Script simple para actualizar los hashes JWT en la base de datos
"""

import duckdb
import bcrypt

def actualizar_hashes_jwt():
    """Actualizar todos los hashes JWT con el hash correcto"""
    
    # Hash correcto para "password123"
    hash_correcto = "$2b$12$1jXfeJ71UhUbNT8ZijnxoOkSB.8erlTb4z0UbbK0R7bDT/bH.oKTW"
    
    db_path = "data/base_de_datos/social_media.duckdb"
    
    try:
        print("🔄 Conectando a la base de datos...")
        conn = duckdb.connect(db_path)
        
        # Actualizar todos los hashes
        print("🔧 Actualizando hashes de contraseñas...")
        conn.execute("""
            UPDATE usuario_acceso 
            SET password_hash = ?
        """, [hash_correcto])
        
        # Verificar la actualización
        result = conn.execute("SELECT COUNT(*) FROM usuario_acceso").fetchone()
        total_usuarios = result[0] if result else 0
        
        print(f"✅ {total_usuarios} usuarios actualizados con hash correcto")
        
        # Verificar algunos usuarios específicos
        usuarios_test = conn.execute("""
            SELECT username, rol, activo 
            FROM usuario_acceso 
            WHERE username IN ('admin_interbank', 'admin_bcp', 'user_interbank')
            ORDER BY username
        """).fetchall()
        
        print("\n📋 Usuarios de prueba disponibles:")
        for username, rol, activo in usuarios_test:
            estado = "ACTIVO" if activo else "INACTIVO"
            print(f"   • {username} (rol: {rol}, {estado})")
        
        conn.close()
        
        print("\n🎉 ¡Actualización completada!")
        print("💡 Ahora puedes probar el login con:")
        print("   Usuario: admin_interbank")
        print("   Contraseña: password123")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    print("🛠️ ACTUALIZADOR DE HASHES JWT")
    print("=" * 40)
    actualizar_hashes_jwt()
