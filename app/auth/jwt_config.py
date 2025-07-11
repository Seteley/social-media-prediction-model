# =============================================================================
# CONFIGURACIÓN JWT Y AUTENTICACIÓN
# =============================================================================

"""
Configuración para autenticación JWT por empresa
"""

import os
from datetime import datetime, timedelta
from typing import Optional
import jwt
from passlib.context import CryptContext
from pydantic import BaseModel

# =============================================================================
# CONFIGURACIÓN JWT
# =============================================================================

# Clave secreta para JWT - EN PRODUCCIÓN USAR VARIABLE DE ENTORNO
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "tu-clave-secreta-super-segura-cambiar-en-produccion")
JWT_ALGORITHM = "HS256"
JWT_ACCESS_TOKEN_EXPIRE_MINUTES = 30  # Token expira en 30 minutos

# Contexto para hash de contraseñas
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# =============================================================================
# MODELOS PYDANTIC
# =============================================================================

class Token(BaseModel):
    access_token: str
    token_type: str
    expires_in: int
    empresa_id: int
    username: str

class TokenData(BaseModel):
    username: Optional[str] = None
    empresa_id: Optional[int] = None

class UserLogin(BaseModel):
    username: str
    password: str

class UserCreate(BaseModel):
    username: str
    password: str
    empresa_id: int
    rol: str = "user"

# =============================================================================
# UTILIDADES JWT
# =============================================================================

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifica que la contraseña sea correcta"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Genera hash de contraseña"""
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Crea token JWT"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    return encoded_jwt

def verify_token(token: str) -> Optional[TokenData]:
    """Verifica y decodifica token JWT"""
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        username: str = payload.get("sub")
        empresa_id: int = payload.get("empresa_id")
        
        if username is None or empresa_id is None:
            return None
            
        return TokenData(username=username, empresa_id=empresa_id)
    except jwt.PyJWTError:
        return None
