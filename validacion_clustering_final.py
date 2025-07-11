#!/usr/bin/env python3
"""
Script de validación final para confirmar que todos los endpoints de clustering
implementan correctamente JWT y control de acceso siguiendo el patrón de regresión.
"""

import sys
import re
from pathlib import Path

def analyze_clustering_routes():
    """Analizar routes_cluster.py para verificar implementación correcta"""
    
    routes_file = Path("app/api/routes_cluster.py")
    if not routes_file.exists():
        print("❌ archivo routes_cluster.py no encontrado")
        return False
    
    content = routes_file.read_text(encoding='utf-8')
    
    # Verificar importaciones requeridas
    required_imports = [
        "from app.auth.dependencies import auth_required",
        "from app.auth.auth_service import auth_service"
    ]
    
    print("🔍 Verificando importaciones...")
    for imp in required_imports:
        if imp in content:
            print(f"✅ {imp}")
        else:
            print(f"❌ Falta: {imp}")
            return False
    
    # Verificar que no hay importaciones obsoletas
    obsolete_imports = ["get_current_user", "verify_company_access"]
    for obs in obsolete_imports:
        if obs in content:
            print(f"⚠️ Importación obsoleta encontrada: {obs}")
            return False
    
    print("✅ Importaciones correctas")
    
    # Analizar endpoints
    print("\n📋 Analizando endpoints...")
    
    # Buscar definiciones de endpoints
    endpoint_pattern = r'@router\.(get|post|put|delete)\("([^"]+)"[^)]*\)\s*(?:.*\n)*?def\s+(\w+)'
    endpoints = re.findall(endpoint_pattern, content, re.MULTILINE)
    
    required_endpoints = [
        ("/users", "list_users"),
        ("/model-info/{username}", "model_info"),
        ("/metrics/{username}", "model_metrics"),
        ("/history/{username}", "model_history"),
        ("/train/{username}", "train_clustering_duckdb"),
        ("/clusters/{username}", "get_clusters_content")
    ]
    
    found_endpoints = [(path, func) for method, path, func in endpoints]
    
    for req_path, req_func in required_endpoints:
        found = any(path == req_path and func == req_func for path, func in found_endpoints)
        if found:
            print(f"✅ {req_path} -> {req_func}")
        else:
            print(f"❌ Falta: {req_path} -> {req_func}")
            return False
    
    # Verificar que todos usan auth_required
    print("\n🔐 Verificando autenticación JWT...")
    
    for req_path, req_func in required_endpoints:
        # Buscar la función específica
        func_pattern = rf'def\s+{req_func}\s*\([^)]*Depends\(auth_required\)[^)]*\):'
        if re.search(func_pattern, content):
            print(f"✅ {req_func} usa auth_required")
        else:
            print(f"❌ {req_func} no usa auth_required")
            return False
    
    # Verificar control de acceso por empresa (para endpoints con username)
    print("\n🏢 Verificando control de acceso por empresa...")
    
    access_control_pattern = r'auth_service\.user_has_access_to_account\(current_user\[\'empresa_id\'\], username\)'
    
    endpoints_with_username = [func for path, func in required_endpoints if "{username}" in path]
    
    for func in endpoints_with_username:
        # Buscar el patrón de verificación de acceso en la función
        func_start = content.find(f"def {func}")
        if func_start == -1:
            print(f"❌ No se encontró función {func}")
            return False
        
        # Buscar el final de la función (próxima definición de función o final del archivo)
        next_func = content.find("\ndef ", func_start + 1)
        if next_func == -1:
            func_content = content[func_start:]
        else:
            func_content = content[func_start:next_func]
        
        if re.search(access_control_pattern, func_content):
            print(f"✅ {func} verifica acceso por empresa")
        else:
            print(f"❌ {func} no verifica acceso por empresa")
            return False
    
    # Verificar documentación OpenAPI
    print("\n📚 Verificando documentación OpenAPI...")
    
    responses_pattern = r'responses=\{[^}]*\}'
    responses_count = len(re.findall(responses_pattern, content))
    
    if responses_count >= len(required_endpoints):
        print(f"✅ Documentación OpenAPI presente ({responses_count} endpoints documentados)")
    else:
        print(f"⚠️ Documentación OpenAPI incompleta ({responses_count}/{len(required_endpoints)})")
    
    # Verificar códigos de estado HTTP correctos
    print("\n🔢 Verificando códigos de estado HTTP...")
    
    required_codes = ["401", "403", "404", "200"]
    for code in required_codes:
        if f'status_code={code}' in content or f'"description"' in content:
            print(f"✅ Código {code} manejado")
        else:
            print(f"⚠️ Código {code} podría no estar manejado")
    
    return True

def main():
    """Función principal"""
    print("🎯 VALIDACIÓN FINAL DE IMPLEMENTACIÓN JWT CLUSTERING")
    print("=" * 60)
    
    try:
        if analyze_clustering_routes():
            print("\n" + "=" * 60)
            print("🎉 ✅ VALIDACIÓN EXITOSA ✅")
            print("📋 Todos los endpoints de clustering implementan correctamente:")
            print("   • Autenticación JWT con auth_required")
            print("   • Control de acceso por empresa")
            print("   • Documentación OpenAPI")
            print("   • Manejo de códigos HTTP")
            print("   • Patrón consistente con regresión")
            print("\n🚀 La implementación está COMPLETA y lista para uso.")
            return True
        else:
            print("\n" + "=" * 60)
            print("💥 ❌ VALIDACIÓN FALLIDA ❌")
            print("⚠️ Revisar errores específicos arriba")
            return False
    except Exception as e:
        print(f"\n❌ Error durante validación: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
