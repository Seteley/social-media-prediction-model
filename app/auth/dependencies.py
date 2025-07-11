# =============================================================================
# MIDDLEWARES Y DEPENDENCIAS DE AUTENTICACIÓN
# =============================================================================

"""
Middlewares y dependencias para proteger endpoints con JWT
"""

from fastapi import HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Dict, Any
from app.auth.auth_service import auth_service

# Esquema de seguridad Bearer Token
security = HTTPBearer()

class AuthRequired:
    """Dependencia para requerir autenticación"""
    
    def __call__(self, credentials: HTTPAuthorizationCredentials = Depends(security)) -> Dict[str, Any]:
        """Verifica token y devuelve datos del usuario"""
        token = credentials.credentials
        
        user = auth_service.get_current_user(token)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token inválido o expirado",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        return user

class AdminRequired:
    """Dependencia para requerir rol de admin"""
    
    def __call__(self, current_user: Dict[str, Any] = Depends(AuthRequired())) -> Dict[str, Any]:
        """Verifica que el usuario sea admin"""
        if current_user.get('rol') != 'admin':
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Se requieren permisos de administrador"
            )
        
        return current_user

class AccountAccessRequired:
    """Dependencia para verificar acceso a una cuenta específica"""
    
    def __init__(self, account_param: str = "username"):
        self.account_param = account_param
    
    def __call__(self, username: str, current_user: Dict[str, Any] = Depends(AuthRequired())) -> Dict[str, Any]:
        """Verifica que el usuario tenga acceso a la cuenta"""
        
        # Los admins tienen acceso a todo
        if current_user.get('rol') == 'admin':
            return current_user
        
        # Verificar si la empresa tiene acceso a esta cuenta
        empresa_id = current_user.get('empresa_id')
        
        if not auth_service.user_has_access_to_account(empresa_id, username):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"No tiene acceso a la cuenta @{username}"
            )
        
        return current_user

# Instancias de las dependencias
auth_required = AuthRequired()
admin_required = AdminRequired()
account_access_required = AccountAccessRequired()

def get_user_accounts(current_user: Dict[str, Any] = Depends(auth_required)) -> list:
    """Obtiene las cuentas disponibles para el usuario actual"""
    empresa_id = current_user.get('empresa_id')
    return auth_service.get_empresa_users(empresa_id)
