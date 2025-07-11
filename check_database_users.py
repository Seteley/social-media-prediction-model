#!/usr/bin/env python3
"""
Script para verificar usuarios y empresas en la base de datos
"""

import duckdb
from pathlib import Path

def check_database():
    """Verifica el contenido de la base de datos"""
    db_path = Path("data/base_de_datos/social_media.duckdb")
    
    if not db_path.exists():
        print(f"❌ Base de datos no encontrada en: {db_path}")
        return
    
    print("🔍 Conectando a la base de datos...")
    
    try:
        conn = duckdb.connect(str(db_path))
        
        print("\n" + "=" * 60)
        print("EMPRESAS REGISTRADAS")
        print("=" * 60)
        
        # Listar empresas
        empresas = conn.execute("SELECT id, nombre FROM empresa ORDER BY id").fetchall()
        for emp in empresas:
            print(f"ID: {emp[0]}, Nombre: {emp[1]}")
        
        print("\n" + "=" * 60)
        print("USUARIOS REGISTRADOS")
        print("=" * 60)
        
        # Listar usuarios con sus empresas
        usuarios = conn.execute("""
            SELECT u.id, u.username, u.rol, u.activo, u.id_empresa, e.nombre as empresa_nombre
            FROM usuario u
            LEFT JOIN empresa e ON u.id_empresa = e.id
            ORDER BY u.id_empresa, u.username
        """).fetchall()
        
        for user in usuarios:
            activo_text = "✅ Activo" if user[3] else "❌ Inactivo"
            print(f"ID: {user[0]}, Usuario: {user[1]}, Rol: {user[2]}, {activo_text}")
            print(f"    Empresa: {user[5]} (ID: {user[4]})")
            print()
        
        print("\n" + "=" * 60)
        print("CUENTAS/MODELOS DISPONIBLES")
        print("=" * 60)
        
        # Verificar qué cuentas están disponibles en la tabla usuario (para modelos)
        cuentas = conn.execute("""
            SELECT DISTINCT cuenta, id_empresa, e.nombre as empresa_nombre
            FROM usuario u
            LEFT JOIN empresa e ON u.id_empresa = e.id
            WHERE cuenta IS NOT NULL
            ORDER BY id_empresa, cuenta
        """).fetchall()
        
        for cuenta in cuentas:
            print(f"Cuenta: {cuenta[0]}, Empresa: {cuenta[2]} (ID: {cuenta[1]})")
        
        print("\n" + "=" * 60)
        print("RESUMEN DE ACCESOS")
        print("=" * 60)
        
        # Para cada usuario, mostrar a qué cuentas tiene acceso
        for user in usuarios:
            if user[3]:  # Solo usuarios activos
                print(f"\n👤 Usuario: {user[1]} (Empresa: {user[5]})")
                
                # Buscar cuentas de la misma empresa
                cuentas_acceso = conn.execute("""
                    SELECT DISTINCT cuenta
                    FROM usuario
                    WHERE id_empresa = ? AND cuenta IS NOT NULL
                    ORDER BY cuenta
                """, [user[4]]).fetchall()
                
                if cuentas_acceso:
                    print("   Acceso a cuentas:")
                    for cuenta in cuentas_acceso:
                        print(f"     - {cuenta[0]}")
                else:
                    print("   ⚠️  Sin acceso a ninguna cuenta")
        
        conn.close()
    
    except Exception as e:
        print(f"❌ Error al acceder a la base de datos: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_database()
