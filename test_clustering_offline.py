#!/usr/bin/env python3
"""
Script para probar el comportamiento offline de los endpoints de clustering
sin necesidad de ejecutar el servidor
"""

import sys
from pathlib import Path
import importlib.util

def test_routes_import():
    """Probar que se pueden importar las rutas sin errores"""
    try:
        print("🔍 Probando importación de routes_cluster.py...")
        from app.api.routes_cluster import router
        print("✅ routes_cluster.py importado exitosamente")
        
        # Verificar que el router tiene las rutas esperadas
        routes = []
        for route in router.routes:
            if hasattr(route, 'path'):
                routes.append({
                    'path': route.path,
                    'methods': list(route.methods) if hasattr(route, 'methods') else []
                })
        
        print(f"📋 Se encontraron {len(routes)} rutas:")
        for route in routes:
            print(f"   • {route['methods']} {route['path']}")
        
        return True
    except Exception as e:
        print(f"❌ Error al importar routes_cluster.py: {e}")
        return False

def test_auth_integration():
    """Probar que la integración con el sistema de autenticación funciona"""
    try:
        print("\n🔐 Probando integración con sistema de autenticación...")
        from app.auth.dependencies import auth_required
        from app.auth.auth_service import auth_service
        print("✅ Dependencias de autenticación importadas exitosamente")
        return True
    except Exception as e:
        print(f"❌ Error en integración de autenticación: {e}")
        return False

def test_main_app():
    """Probar que la aplicación principal se puede importar"""
    try:
        print("\n🚀 Probando importación de la aplicación principal...")
        from app.main import app
        print("✅ Aplicación principal importada exitosamente")
        
        # Verificar que los endpoints de clustering están registrados
        clustering_routes = []
        for route in app.routes:
            if hasattr(route, 'path') and '/clustering' in route.path:
                clustering_routes.append({
                    'path': route.path,
                    'methods': list(route.methods) if hasattr(route, 'methods') else []
                })
        
        print(f"📋 Endpoints de clustering registrados: {len(clustering_routes)}")
        for route in clustering_routes:
            print(f"   • {route['methods']} {route['path']}")
        
        return True
    except Exception as e:
        print(f"❌ Error al importar aplicación principal: {e}")
        return False

def verify_endpoint_security():
    """Verificar que todos los endpoints tienen seguridad JWT"""
    try:
        print("\n🔒 Verificando que todos los endpoints requieren autenticación...")
        from app.api.routes_cluster import router
        
        endpoints_checked = 0
        secure_endpoints = 0
        
        for route in router.routes:
            if hasattr(route, 'endpoint'):
                endpoints_checked += 1
                # Verificar dependencias del endpoint
                dependencies = getattr(route, 'dependencies', [])
                dependency_names = []
                
                if hasattr(route.endpoint, '__annotations__'):
                    for param_name, param_type in route.endpoint.__annotations__.items():
                        if param_name != 'return':
                            dependency_names.append(str(param_type))
                
                # Buscar auth_required en las dependencias
                has_auth = any('auth_required' in dep for dep in dependency_names)
                
                if has_auth:
                    secure_endpoints += 1
                    print(f"   ✅ {route.path} - Protegido con JWT")
                else:
                    print(f"   ⚠️  {route.path} - Sin protección JWT detectada")
        
        print(f"\n📊 Resumen de seguridad:")
        print(f"   • Endpoints verificados: {endpoints_checked}")
        print(f"   • Endpoints protegidos: {secure_endpoints}")
        
        return secure_endpoints == endpoints_checked
    except Exception as e:
        print(f"❌ Error al verificar seguridad: {e}")
        return False

def main():
    """Función principal"""
    print("🧪 PRUEBAS OFFLINE DE ENDPOINTS DE CLUSTERING")
    print("=" * 60)
    
    tests = [
        ("Importación de rutas", test_routes_import),
        ("Integración de autenticación", test_auth_integration),
        ("Aplicación principal", test_main_app),
        ("Seguridad de endpoints", verify_endpoint_security)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n🔬 Ejecutando: {test_name}")
        if test_func():
            passed += 1
            print(f"✅ {test_name} - PASÓ")
        else:
            print(f"❌ {test_name} - FALLÓ")
    
    print(f"\n{'='*60}")
    print(f"📊 RESUMEN: {passed}/{total} pruebas pasaron")
    
    if passed == total:
        print("🎉 ¡Todas las pruebas offline pasaron exitosamente!")
        print("\n📝 SIGUIENTE PASO:")
        print("   Para pruebas completas, inicie el servidor con:")
        print("   uvicorn app.main:app --host 0.0.0.0 --port 8000")
        print("   Y luego ejecute: python test_clustering_endpoints_completo.py")
        return True
    else:
        print(f"💥 {total - passed} pruebas fallaron. Revisar errores arriba.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
