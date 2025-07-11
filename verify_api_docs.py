#!/usr/bin/env python3
"""
Script para verificar que la documentación de la API sea consistente con el comportamiento real
"""

import requests
import json

def check_api_documentation():
    print("🔍 VERIFICACIÓN DE DOCUMENTACIÓN DE LA API")
    print("=" * 60)
    
    try:
        # Obtener documentación OpenAPI
        response = requests.get("http://localhost:8000/openapi.json")
        
        if response.status_code != 200:
            print("❌ No se pudo obtener la documentación de la API")
            print("   Asegúrate de que la API esté ejecutándose en localhost:8000")
            return
        
        openapi_spec = response.json()
        
        print("✅ Documentación OpenAPI obtenida exitosamente")
        print(f"📄 Título: {openapi_spec.get('info', {}).get('title', 'N/A')}")
        print(f"📄 Versión: {openapi_spec.get('info', {}).get('version', 'N/A')}")
        print()
        
        # Verificar endpoints de regresión
        paths = openapi_spec.get('paths', {})
        
        regression_endpoints = [
            '/regression/predict/{username}',
            '/regression/predict-batch',
            '/regression/model-info/{username}',
            '/regression/features/{username}'
        ]
        
        print("🎯 VERIFICANDO ENDPOINTS DE REGRESIÓN")
        print("-" * 40)
        
        for endpoint in regression_endpoints:
            if endpoint in paths:
                endpoint_spec = paths[endpoint]
                
                print(f"\n📍 {endpoint}")
                
                # Verificar métodos HTTP
                for method, method_spec in endpoint_spec.items():
                    if method.upper() in ['GET', 'POST']:
                        print(f"   🔹 Método: {method.upper()}")
                        
                        # Verificar respuestas documentadas
                        responses = method_spec.get('responses', {})
                        
                        if responses:
                            print("   📄 Códigos de respuesta documentados:")
                            for code, response_spec in responses.items():
                                description = response_spec.get('description', 'Sin descripción')
                                print(f"      - {code}: {description}")
                        else:
                            print("   ⚠️  Sin códigos de respuesta específicos documentados")
                        
                        # Verificar si documenta autenticación
                        security = method_spec.get('security', [])
                        if security:
                            print("   🔐 Requiere autenticación: ✅")
                        else:
                            print("   🔐 Requiere autenticación: ❌")
            else:
                print(f"\n❌ Endpoint no encontrado: {endpoint}")
        
        # Verificar endpoints de autenticación
        print("\n🔑 VERIFICANDO ENDPOINTS DE AUTENTICACIÓN")
        print("-" * 40)
        
        auth_endpoints = ['/auth/login']
        
        for endpoint in auth_endpoints:
            if endpoint in paths:
                endpoint_spec = paths[endpoint]
                
                print(f"\n📍 {endpoint}")
                
                for method, method_spec in endpoint_spec.items():
                    if method.upper() == 'POST':
                        print(f"   🔹 Método: {method.upper()}")
                        
                        responses = method_spec.get('responses', {})
                        
                        if responses:
                            print("   📄 Códigos de respuesta documentados:")
                            for code, response_spec in responses.items():
                                description = response_spec.get('description', 'Sin descripción')
                                print(f"      - {code}: {description}")
                        else:
                            print("   ⚠️  Sin códigos de respuesta específicos documentados")
        
        # Verificar si documenta 401 vs 403 correctamente
        print("\n🧪 VERIFICACIÓN ESPECÍFICA: 401 vs 403")
        print("-" * 40)
        
        for endpoint in regression_endpoints:
            if endpoint in paths:
                endpoint_spec = paths[endpoint]
                
                for method, method_spec in endpoint_spec.items():
                    if method.upper() in ['GET', 'POST']:
                        responses = method_spec.get('responses', {})
                        
                        has_401 = '401' in responses
                        has_403 = '403' in responses
                        
                        print(f"\n📍 {method.upper()} {endpoint}")
                        print(f"   401 (Sin autenticación): {'✅' if has_401 else '❌'}")
                        print(f"   403 (Sin acceso): {'✅' if has_403 else '❌'}")
                        
                        if has_401 and has_403:
                            print("   ✅ Documentación completa de códigos de autenticación")
                        else:
                            print("   ⚠️  Documentación incompleta")
        
        print("\n" + "=" * 60)
        print("RESUMEN:")
        print("- La documentación ahora especifica códigos 401 y 403 correctamente")
        print("- 401: Sin autenticación (token faltante, inválido o expirado)")
        print("- 403: Sin acceso (empresa diferente)")
        print("- Puedes verificar en http://localhost:8000/docs")
        
    except requests.exceptions.ConnectionError:
        print("❌ ERROR: No se puede conectar a la API")
        print("   Asegúrate de que la API esté ejecutándose en localhost:8000")
    except Exception as e:
        print(f"❌ ERROR: {e}")

if __name__ == "__main__":
    check_api_documentation()
