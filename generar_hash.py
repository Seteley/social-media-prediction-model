#!/usr/bin/env python3
"""
Generador rápido de hash bcrypt correcto
"""

import bcrypt

def generar_hash_correcto():
    password = "password123"
    password_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hash_bytes = bcrypt.hashpw(password_bytes, salt)
    hash_str = hash_bytes.decode('utf-8')
    
    # Verificar que el hash funciona
    verificacion = bcrypt.checkpw(password_bytes, hash_bytes)
    
    print(f"Contraseña: {password}")
    print(f"Hash generado: {hash_str}")
    print(f"Verificación: {'✅ CORRECTO' if verificacion else '❌ ERROR'}")
    
    return hash_str

if __name__ == "__main__":
    generar_hash_correcto()
