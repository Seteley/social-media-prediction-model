#!/usr/bin/env python3
"""
VALIDADOR RÁPIDO DEL SISTEMA JWT
===============================

Script para validar que el sistema JWT está correctamente configurado
y que los datos de prueba están disponibles en la base de datos.

Uso: python validar_jwt_setup.py
"""

import os
import sys
import duckdb
from pathlib import Path

def validar_estructura_archivos():
    """Valida que todos los archivos necesarios existan"""
    print("🔍 Validando estructura de archivos...")
    
    archivos_requeridos = [
        "app/auth/jwt_config.py",
        "app/auth/auth_service.py", 
        "app/auth/dependencies.py",
        "app/api/auth_routes.py",
        "configurar_jwt_smart.py",
        "demo_jwt_sistema.py",
        "probar_jwt_completo.py",
        "README_JWT.md",
        "DOCUMENTACION_JWT_COMPLETA.md",
        "data/base_de_datos/scripts/insercioninsert.sql",
        "data/base_de_datos/social_media.duckdb"
    ]
    
    archivos_faltantes = []
    for archivo in archivos_requeridos:
        if not Path(archivo).exists():
            archivos_faltantes.append(archivo)
    
    if archivos_faltantes:
        print("❌ Archivos faltantes:")
        for archivo in archivos_faltantes:
            print(f"   - {archivo}")
        return False
    else:
        print(f"✅ Todos los {len(archivos_requeridos)} archivos principales encontrados")
        return True

def validar_base_datos():
    """Valida que la base de datos tenga los usuarios JWT"""
    print("\n🗄️ Validando base de datos...")
    
    db_path = "data/base_de_datos/social_media.duckdb"
    if not Path(db_path).exists():
        print(f"❌ Base de datos no encontrada: {db_path}")
        return False
    
    try:
        conn = duckdb.connect(db_path)
        
        # Verificar tabla usuario_acceso
        result = conn.execute("SELECT COUNT(*) as total FROM usuario_acceso").fetchone()
        total_usuarios = result[0] if result else 0
        
        if total_usuarios == 0:
            print("❌ No hay usuarios JWT en la base de datos")
            return False
        
        # Verificar usuarios por rol
        roles = conn.execute("""
            SELECT rol, COUNT(*) as cantidad 
            FROM usuario_acceso 
            GROUP BY rol 
            ORDER BY rol
        """).fetchall()
        
        print(f"✅ Base de datos encontrada con {total_usuarios} usuarios JWT:")
        for rol, cantidad in roles:
            print(f"   - {rol}: {cantidad} usuarios")
        
        # Verificar usuarios activos vs inactivos
        activos = conn.execute("SELECT COUNT(*) FROM usuario_acceso WHERE activo = TRUE").fetchone()[0]
        inactivos = conn.execute("SELECT COUNT(*) FROM usuario_acceso WHERE activo = FALSE").fetchone()[0]
        
        print(f"   - Activos: {activos}")
        print(f"   - Inactivos: {inactivos}")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Error al validar base de datos: {e}")
        return False

def validar_configuracion():
    """Valida que las dependencias estén instaladas"""
    print("\n📦 Validando dependencias...")
    
    try:
        import jwt
        import passlib
        import bcrypt
        print("✅ Dependencias JWT instaladas correctamente")
        return True
    except ImportError as e:
        print(f"❌ Dependencia faltante: {e}")
        print("💡 Ejecuta: pip install -r requirements.txt")
        return False

def mostrar_resumen():
    """Muestra un resumen del sistema JWT"""
    print("\n" + "="*60)
    print("📋 RESUMEN DEL SISTEMA JWT")
    print("="*60)
    print()
    print("🔐 USUARIOS DE PRUEBA DISPONIBLES:")
    print("   • admin_interbank / password123 (Empresa: Interbank)")
    print("   • admin_bcp / password123 (Empresa: BCP)")
    print("   • admin_bbva / password123 (Empresa: BBVA)")
    print("   • user_interbank / password123 (Usuario regular)")
    print("   • viewer_bbva / password123 (Solo lectura)")
    print("   • inactive_user / password123 (Cuenta desactivada)")
    print()
    print("🚀 SCRIPTS DISPONIBLES:")
    print("   • python configurar_jwt_smart.py   → Configurar usuarios")
    print("   • python demo_jwt_sistema.py       → Demo interactivo")
    print("   • python probar_jwt_completo.py    → Tests completos")
    print()
    print("📚 DOCUMENTACIÓN:")
    print("   • README_JWT.md                    → Guía rápida")
    print("   • DOCUMENTACION_JWT_COMPLETA.md    → Documentación técnica")
    print()
    print("🌐 INICIO DE API:")
    print("   • uvicorn app.main:app --reload    → Iniciar servidor")
    print("   • http://localhost:8000/docs       → Swagger UI")
    print("   • http://localhost:8000/auth/login → Endpoint de login")

def main():
    """Función principal de validación"""
    print("🛡️ VALIDADOR DEL SISTEMA JWT - Social Media Prediction Model")
    print("=" * 65)
    
    validaciones = [
        validar_estructura_archivos(),
        validar_base_datos(),
        validar_configuracion()
    ]
    
    if all(validaciones):
        print("\n🎉 ¡SISTEMA JWT COMPLETAMENTE CONFIGURADO!")
        mostrar_resumen()
        return True
    else:
        print("\n⚠️ Hay problemas con la configuración del sistema JWT")
        print("💡 Revisa los errores anteriores y ejecuta los scripts de configuración necesarios")
        return False

if __name__ == "__main__":
    exito = main()
    sys.exit(0 if exito else 1)
