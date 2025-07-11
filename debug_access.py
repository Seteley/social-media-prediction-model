#!/usr/bin/env python3
"""
Script para verificar los datos en la base de datos manualmente
"""

import duckdb

def check_access():
    conn = duckdb.connect('data/base_de_datos/social_media.duckdb')
    
    print("=== EMPRESAS ===")
    empresas = conn.execute("SELECT id_empresa, nombre FROM empresa ORDER BY id_empresa").fetchall()
    for emp in empresas:
        print(f"ID: {emp[0]} - {emp[1]}")
    
    print("\n=== USUARIOS (cuentas sociales) ===") 
    usuarios = conn.execute("SELECT id_usuario, id_empresa, cuenta, nombre FROM usuario ORDER BY id_empresa").fetchall()
    for user in usuarios:
        print(f"ID: {user[0]} - Empresa: {user[1]} - Cuenta: {user[2]} - Nombre: {user[3]}")
    
    print("\n=== USUARIOS_ACCESO (JWT users) ===")
    jwt_users = conn.execute("SELECT id_usuario_acceso, username, id_empresa, rol, activo FROM usuario_acceso ORDER BY id_empresa").fetchall()
    for user in jwt_users:
        print(f"ID: {user[0]} - User: {user[1]} - Empresa: {user[2]} - Rol: {user[3]} - Activo: {user[4]}")
    
    print("\n=== TESTS ESPECÍFICOS ===")
    
    # Test 1: admin_interbank acceso a Interbank (debería SER VERDADERO)
    query1 = """
    SELECT COUNT(*) 
    FROM usuario u
    WHERE u.id_empresa = 1 AND u.cuenta = 'Interbank'
    """
    result1 = conn.execute(query1).fetchone()
    print(f"admin_interbank acceso a Interbank: {result1[0] > 0} (resultado: {result1[0]})")
    
    # Test 2: admin_interbank acceso a BCPComunica (debería SER FALSO)
    query2 = """
    SELECT COUNT(*) 
    FROM usuario u
    WHERE u.id_empresa = 1 AND u.cuenta = 'BCPComunica'
    """
    result2 = conn.execute(query2).fetchone()
    print(f"admin_interbank acceso a BCPComunica: {result2[0] > 0} (resultado: {result2[0]})")
    
    # Test 3: ¿A qué cuentas tiene acceso empresa 1?
    query3 = """
    SELECT u.cuenta
    FROM usuario u
    WHERE u.id_empresa = 1
    """
    result3 = conn.execute(query3).fetchall()
    print(f"Empresa 1 (Interbank) tiene acceso a: {[r[0] for r in result3]}")
    
    # Test 4: ¿A qué empresa pertenece BCPComunica?
    query4 = """
    SELECT u.id_empresa, e.nombre
    FROM usuario u
    JOIN empresa e ON u.id_empresa = e.id_empresa  
    WHERE u.cuenta = 'BCPComunica'
    """
    result4 = conn.execute(query4).fetchall()
    print(f"BCPComunica pertenece a empresa: {result4[0] if result4 else 'No encontrada'}")
    
    conn.close()

if __name__ == "__main__":
    check_access()
