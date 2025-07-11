# =============================================================================
# ENDPOINTS DE AUTENTICACIÓN
# =============================================================================

"""
Endpoints para login, registro y gestión de usuarios
"""

from fastapi import APIRouter, HTTPException, Depends, status
from app.auth.jwt_config import Token, UserLogin, UserCreate
from app.auth.auth_service import auth_service
from app.auth.dependencies import auth_required, admin_required
from typing import Dict, Any, List

router = APIRouter(prefix="/auth", tags=["Autenticación"])

@router.post("/login", response_model=Token)
def login(login_data: UserLogin):
    """
    Iniciar sesión y obtener token JWT
    
    **Parámetros:**
    - username: Nombre de usuario
    - password: Contraseña
    
    **Respuesta:**
    - access_token: Token JWT para usar en endpoints protegidos
    - token_type: Tipo de token (bearer)
    - expires_in: Tiempo de expiración en segundos
    - empresa_id: ID de la empresa del usuario
    - username: Nombre de usuario
    """
    token = auth_service.login(login_data)
    
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales incorrectas"
        )
    
    return token

@router.post("/register", dependencies=[Depends(admin_required)])
def register(user_data: UserCreate):
    """
    Registrar nuevo usuario (solo admins)
    
    **Requiere:** Token de admin
    
    **Parámetros:**
    - username: Nombre de usuario único
    - password: Contraseña
    - empresa_id: ID de la empresa
    - rol: Rol del usuario (user, admin)
    """
    success = auth_service.create_user(user_data)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Error al crear usuario. Verifique que el username no exista y la empresa sea válida."
        )
    
    return {"message": f"Usuario {user_data.username} creado exitosamente"}

@router.get("/me")
def get_current_user_info(current_user: Dict[str, Any] = Depends(auth_required)):
    """
    Obtener información del usuario actual
    
    **Requiere:** Token válido
    
    **Respuesta:**
    - username: Nombre de usuario
    - empresa_id: ID de la empresa
    - empresa_nombre: Nombre de la empresa
    - rol: Rol del usuario
    """
    return {
        "username": current_user["username"],
        "empresa_id": current_user["empresa_id"],
        "empresa_nombre": current_user["empresa_nombre"],
        "rol": current_user["rol"]
    }

@router.get("/my-accounts")
def get_my_accounts(current_user: Dict[str, Any] = Depends(auth_required)):
    """
    Obtener cuentas de redes sociales disponibles para el usuario
    
    **Requiere:** Token válido
    
    **Respuesta:**
    Lista de cuentas de redes sociales de la empresa del usuario
    """
    empresa_id = current_user.get('empresa_id')
    accounts = auth_service.get_empresa_users(empresa_id)
    
    return {
        "empresa_id": empresa_id,
        "empresa_nombre": current_user.get('empresa_nombre'),
        "total_accounts": len(accounts),
        "accounts": accounts
    }

@router.get("/test-protected")
def test_protected_endpoint(current_user: Dict[str, Any] = Depends(auth_required)):
    """
    Endpoint de prueba para verificar autenticación
    
    **Requiere:** Token válido
    """
    return {
        "message": "¡Acceso autorizado!",
        "user": current_user["username"],
        "empresa": current_user["empresa_nombre"]
    }
