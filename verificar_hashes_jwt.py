#!/usr/bin/env python3
"""
VERIFICADOR Y GENERADOR DE HASHES JWT
=====================================

Script para verificar los hashes de contraseñas en la base de datos
y generar nuevos hashes correctos si es necesario.
"""

import bcrypt
import duckdb
from pathlib import Path

def generar_hash_correcto(password: str) -> str:
    """Genera un hash bcrypt correcto para la contraseña dada"""
    password_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hash_bytes = bcrypt.hashpw(password_bytes, salt)
    return hash_bytes.decode('utf-8')

def verificar_hash(password: str, hash_stored: str) -> bool:
    """Verifica si un hash corresponde a la contraseña"""
    try:
        password_bytes = password.encode('utf-8')
        hash_bytes = hash_stored.encode('utf-8')
        return bcrypt.checkpw(password_bytes, hash_bytes)
    except Exception as e:
        print(f"Error al verificar hash: {e}")
        return False

def generar_hashes_para_sql():
    """Genera hashes correctos y muestra el SQL actualizado"""
    password = "password123"
    
    print("🔐 GENERANDO HASHES BCRYPT CORRECTOS")
    print("=" * 50)
    print(f"Contraseña: {password}")
    print()
    
    # Generar un hash y verificar que funciona
    nuevo_hash = generar_hash_correcto(password)
    verificacion = verificar_hash(password, nuevo_hash)
    
    print(f"Nuevo hash generado: {nuevo_hash}")
    print(f"Verificación exitosa: {'✅' if verificacion else '❌'}")
    print()
    
    if verificacion:
        print("📝 SQL CORREGIDO CON HASH VÁLIDO:")
        print("=" * 50)
        print(f"""-- Inserciones para la tabla usuario_acceso (usuarios JWT para autenticación)
-- Contraseñas hasheadas con bcrypt (password: "password123")
INSERT INTO usuario_acceso (id_usuario_acceso, username, password_hash, id_empresa, rol, activo) VALUES
  (1, 'admin_interbank', '{nuevo_hash}', 1, 'admin', TRUE),
  (2, 'admin_banbif', '{nuevo_hash}', 2, 'admin', TRUE),
  (3, 'admin_nacion', '{nuevo_hash}', 3, 'admin', TRUE),
  (4, 'admin_bcrp', '{nuevo_hash}', 4, 'admin', TRUE),
  (5, 'admin_pichincha', '{nuevo_hash}', 5, 'admin', TRUE),
  (6, 'admin_bbva', '{nuevo_hash}', 6, 'admin', TRUE),
  (7, 'admin_bcp', '{nuevo_hash}', 7, 'admin', TRUE),
  (8, 'admin_scotiabank', '{nuevo_hash}', 8, 'admin', TRUE),
  (9, 'user_interbank', '{nuevo_hash}', 1, 'user', TRUE),
  (10, 'user_bcp', '{nuevo_hash}', 7, 'user', TRUE),
  (11, 'viewer_bbva', '{nuevo_hash}', 6, 'viewer', TRUE),
  (12, 'inactive_user', '{nuevo_hash}', 1, 'user', FALSE);""")
        
        return nuevo_hash
    else:
        print("❌ Error al generar hash válido")
        return None

def verificar_usuarios_en_db():
    """Verifica los usuarios en la base de datos"""
    db_path = "data/base_de_datos/social_media.duckdb"
    
    if not Path(db_path).exists():
        print(f"❌ Base de datos no encontrada: {db_path}")
        return False
    
    try:
        conn = duckdb.connect(db_path)
        
        # Verificar si existe la tabla
        try:
            usuarios = conn.execute("""
                SELECT id_usuario_acceso, username, password_hash, id_empresa, rol, activo 
                FROM usuario_acceso 
                ORDER BY id_usuario_acceso
            """).fetchall()
            
            if not usuarios:
                print("⚠️ No hay usuarios en la tabla usuario_acceso")
                return False
            
            print(f"\n👥 USUARIOS EN BASE DE DATOS ({len(usuarios)} encontrados):")
            print("=" * 60)
            
            password = "password123"
            for usuario in usuarios:
                id_acc, username, hash_stored, empresa, rol, activo = usuario
                verificacion = verificar_hash(password, hash_stored)
                estado = "✅" if verificacion else "❌"
                activo_text = "ACTIVO" if activo else "INACTIVO"
                
                print(f"{estado} {username} (ID:{id_acc}, Empresa:{empresa}, Rol:{rol}, {activo_text})")
                if not verificacion:
                    print(f"   Hash problemático: {hash_stored[:50]}...")
            
            # Contar verificaciones exitosas
            verificaciones_exitosas = sum(1 for usuario in usuarios 
                                        if verificar_hash(password, usuario[2]))
            
            print(f"\n📊 RESUMEN:")
            print(f"   Total usuarios: {len(usuarios)}")
            print(f"   Hashes válidos: {verificaciones_exitosas}")
            print(f"   Hashes inválidos: {len(usuarios) - verificaciones_exitosas}")
            
            return verificaciones_exitosas == len(usuarios)
            
        except Exception as e:
            print(f"❌ Error al consultar tabla usuario_acceso: {e}")
            print("💡 La tabla podría no existir o tener un esquema diferente")
            return False
        
    except Exception as e:
        print(f"❌ Error al conectar con la base de datos: {e}")
        return False
    finally:
        try:
            conn.close()
        except:
            pass

def main():
    """Función principal"""
    print("🔍 VERIFICADOR DE SISTEMA JWT")
    print("=" * 40)
    
    print("\n1️⃣ Verificando usuarios en base de datos...")
    usuarios_validos = verificar_usuarios_en_db()
    
    print("\n2️⃣ Generando hash correcto...")
    nuevo_hash = generar_hashes_para_sql()
    
    if not usuarios_validos and nuevo_hash:
        print("\n🔧 ACCIONES RECOMENDADAS:")
        print("=" * 30)
        print("1. Actualizar el archivo insercioninsert.sql con el nuevo hash")
        print("2. Recrear la base de datos ejecutando:")
        print("   - scripts/createtable.sql")
        print("   - scripts/insercioninsert.sql")
        print("3. O ejecutar: python configurar_jwt_smart.py")
    elif usuarios_validos:
        print("\n🎉 ¡Sistema JWT configurado correctamente!")
        print("💡 Puedes probar el login ahora")
    
    return usuarios_validos

if __name__ == "__main__":
    main()
