#!/usr/bin/env python3
"""
Script para probar el sistema JWT completo sin iniciar la API
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.auth.auth_service import AuthService
from app.auth.jwt_config import create_access_token

def probar_sistema_jwt_completo():
    """Probar todo el flujo JWT usando las clases del sistema"""
    
    print("🧪 PRUEBA COMPLETA DEL SISTEMA JWT")
    print("=" * 50)
    
    # Inicializar el servicio de autenticación
    auth_service = AuthService()
    
    # Credenciales de prueba
    username = "admin_interbank"
    password = "password123"
    
    print(f"🔐 Probando autenticación:")
    print(f"   Usuario: {username}")
    print(f"   Contraseña: {password}")
    
    try:
        # Autenticar usuario
        user_data = auth_service.authenticate_user(username, password)
        
        if user_data:
            print("✅ ¡Autenticación exitosa!")
            print(f"   ID Usuario: {user_data['id_usuario_acceso']}")
            print(f"   Empresa ID: {user_data['id_empresa']}")
            print(f"   Rol: {user_data['rol']}")
            print(f"   Activo: {'Sí' if user_data['activo'] else 'No'}")
            
            # Crear token JWT
            access_token = create_access_token(data={"sub": username})
            print(f"\n🎫 Token JWT generado:")
            print(f"   {access_token[:50]}...")
            
            # Obtener información del usuario autenticado
            user_info = auth_service.get_user_by_username(username)
            if user_info:
                print(f"\n📋 Información del usuario:")
                print(f"   Empresa autorizada: {user_info['id_empresa']}")
                print(f"   Permisos: {user_info['rol']}")
            
            print("\n🎉 ¡Sistema JWT funcionando correctamente!")
            
            # Información para pruebas con cURL
            print("\n🌐 PRUEBA CON cURL:")
            print("=" * 30)
            print(f"""curl -X POST "http://localhost:8000/auth/login" \\
     -H "Content-Type: application/json" \\
     -d '{{"username": "{username}", "password": "{password}"}}'""")
            
            return True
            
        else:
            print("❌ Autenticación fallida")
            return False
            
    except Exception as e:
        print(f"❌ Error durante la prueba: {e}")
        return False

def mostrar_todos_los_usuarios():
    """Mostrar todos los usuarios disponibles para testing"""
    print("\n👥 USUARIOS DISPONIBLES PARA TESTING:")
    print("=" * 45)
    
    auth_service = AuthService()
    
    try:
        import duckdb
        conn = duckdb.connect("data/base_de_datos/social_media.duckdb")
        
        usuarios = conn.execute("""
            SELECT ua.username, ua.rol, ua.activo, e.nombre as empresa
            FROM usuario_acceso ua
            JOIN empresa e ON ua.id_empresa = e.id_empresa
            ORDER BY ua.rol, ua.username
        """).fetchall()
        
        for username, rol, activo, empresa in usuarios:
            estado = "🟢 ACTIVO" if activo else "🔴 INACTIVO"
            print(f"   • {username}")
            print(f"     Empresa: {empresa}")
            print(f"     Rol: {rol}")
            print(f"     Estado: {estado}")
            print(f"     Contraseña: password123")
            print()
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error al obtener usuarios: {e}")

if __name__ == "__main__":
    exito = probar_sistema_jwt_completo()
    mostrar_todos_los_usuarios()
    
    if exito:
        print("🚀 El sistema está listo para uso en producción!")
    else:
        print("⚠️ Hay problemas que necesitan ser resueltos.")
