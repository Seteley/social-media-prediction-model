#!/usr/bin/env python3
"""
Test simple para verificar que la corrección de control de acceso funciona
"""

import sys
sys.path.append('.')

from app.auth.auth_service import auth_service

def test_access_control():
    """Test simple del control de acceso"""
    
    print("=" * 50)
    print("TEST DE CONTROL DE ACCESO")
    print("=" * 50)
    
    # Test cases: usuario con empresa_id, account a probar, debería tener acceso?
    test_cases = [
        (1, "Interbank", True),      # Empresa 1 accede a Interbank
        (1, "BCPComunica", False),   # Empresa 1 NO debe acceder a BCP
        (2, "BCPComunica", True),    # Empresa 2 accede a BCP 
        (2, "Interbank", False),     # Empresa 2 NO debe acceder a Interbank
    ]
    
    for empresa_id, account, should_have_access in test_cases:
        try:
            has_access = auth_service.user_has_access_to_account(empresa_id, account)
            
            status = "✅ CORRECTO" if has_access == should_have_access else "❌ ERROR"
            access_text = "SÍ" if has_access else "NO"
            expected_text = "SÍ" if should_have_access else "NO"
            
            print(f"{status} - Empresa {empresa_id} acceso a {account}")
            print(f"  Resultado: {access_text}, Esperado: {expected_text}")
            
        except Exception as e:
            print(f"❌ ERROR - Empresa {empresa_id} acceso a {account}: {e}")
        
        print()

if __name__ == "__main__":
    test_access_control()
