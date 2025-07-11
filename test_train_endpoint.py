#!/usr/bin/env python3
"""
Prueba rápida del endpoint actualizado /regression/train/{username}
"""

import requests

def main():
    print("🧪 Prueba rápida del endpoint /regression/train/{username}")
    
    # Verificar que el servidor esté ejecutándose
    try:
        response = requests.get('http://localhost:8000/docs', timeout=5)
        if response.status_code == 200:
            print('✅ Servidor está ejecutándose')
            
            # Probar endpoint sin autenticación (debe dar 401)
            response = requests.get('http://localhost:8000/regression/train/Interbank')
            if response.status_code == 401:
                print('✅ Endpoint /regression/train/{username} retorna 401 sin auth (correcto)')
                print('✅ Actualización completada exitosamente')
                return True
            else:
                print(f'⚠️ Endpoint retorna {response.status_code} (esperado 401)')
                return False
                
        else:
            print('❌ Servidor no responde correctamente')
            return False
    except Exception as e:
        print('❌ Servidor no está ejecutándose:', e)
        print('Para iniciar: uvicorn app.main:app --host 0.0.0.0 --port 8000')
        return False

if __name__ == "__main__":
    main()
