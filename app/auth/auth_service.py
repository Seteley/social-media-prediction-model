# =============================================================================
# SERVICIO DE AUTENTICACIÓN
# =============================================================================

"""
Servicio para manejar autenticación JWT con base de datos
"""

import duckdb
from typing import Optional, Dict, Any
from pathlib import Path
from app.auth.jwt_config import (
    verify_password, get_password_hash, create_access_token,
    verify_token, Token, TokenData, UserLogin, UserCreate,
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES
)
from datetime import timedelta

class AuthService:
    def __init__(self, db_path: str = "data/base_de_datos/social_media.duckdb"):
        self.db_path = db_path
    
    def get_connection(self):
        """Obtiene conexión a la base de datos"""
        return duckdb.connect(self.db_path)
    
    def authenticate_user(self, username: str, password: str) -> Optional[Dict[str, Any]]:
        """Autentica usuario y devuelve sus datos"""
        with self.get_connection() as conn:
            query = """
            SELECT ua.username, ua.password_hash, ua.id_empresa, ua.rol, ua.activo,
                   e.nombre as empresa_nombre
            FROM usuario_acceso ua
            JOIN empresa e ON ua.id_empresa = e.id_empresa
            WHERE ua.username = ? AND ua.activo = TRUE
            """
            
            result = conn.execute(query, [username]).fetchone()
            
            if not result:
                return None
            
            user_data = {
                'username': result[0],
                'password_hash': result[1],
                'empresa_id': result[2],
                'rol': result[3],
                'activo': result[4],
                'empresa_nombre': result[5]
            }
            
            # Verificar contraseña
            if not verify_password(password, user_data['password_hash']):
                return None
            
            return user_data
    
    def create_user(self, user_data: UserCreate) -> bool:
        """Crea nuevo usuario"""
        try:
            with self.get_connection() as conn:
                # Verificar que la empresa existe
                empresa_check = conn.execute(
                    "SELECT id_empresa FROM empresa WHERE id_empresa = ?", 
                    [user_data.empresa_id]
                ).fetchone()
                
                if not empresa_check:
                    raise ValueError(f"Empresa con ID {user_data.empresa_id} no existe")
                
                # Verificar que el username no existe
                user_check = conn.execute(
                    "SELECT username FROM usuario_acceso WHERE username = ?",
                    [user_data.username]
                ).fetchone()
                
                if user_check:
                    raise ValueError(f"Usuario {user_data.username} ya existe")
                
                # Crear usuario
                password_hash = get_password_hash(user_data.password)
                
                conn.execute("""
                    INSERT INTO usuario_acceso (id_empresa, username, password_hash, rol, activo)
                    VALUES (?, ?, ?, ?, TRUE)
                """, [user_data.empresa_id, user_data.username, password_hash, user_data.rol])
                
                return True
                
        except Exception as e:
            print(f"Error creando usuario: {e}")
            return False
    
    def login(self, login_data: UserLogin) -> Optional[Token]:
        """Realiza login y devuelve token JWT"""
        user = self.authenticate_user(login_data.username, login_data.password)
        
        if not user:
            return None
        
        # Crear token JWT
        access_token_expires = timedelta(minutes=JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user['username'], "empresa_id": user['empresa_id'], "rol": user['rol']},
            expires_delta=access_token_expires
        )
        
        return Token(
            access_token=access_token,
            token_type="bearer",
            expires_in=JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60,  # en segundos
            empresa_id=user['empresa_id'],
            username=user['username']
        )
    
    def get_current_user(self, token: str) -> Optional[Dict[str, Any]]:
        """Obtiene datos del usuario actual desde el token"""
        token_data = verify_token(token)
        
        if not token_data:
            return None
        
        with self.get_connection() as conn:
            query = """
            SELECT ua.username, ua.id_empresa, ua.rol, e.nombre as empresa_nombre
            FROM usuario_acceso ua
            JOIN empresa e ON ua.id_empresa = e.id_empresa
            WHERE ua.username = ? AND ua.activo = TRUE
            """
            
            result = conn.execute(query, [token_data.username]).fetchone()
            
            if not result:
                return None
            
            return {
                'username': result[0],
                'empresa_id': result[1],
                'rol': result[2],
                'empresa_nombre': result[3]
            }
    
    def get_empresa_users(self, empresa_id: int) -> list:
        """Obtiene todas las cuentas de usuario de una empresa"""
        with self.get_connection() as conn:
            query = """
            SELECT u.cuenta, u.nombre, u.fecha_registro
            FROM usuario u
            WHERE u.id_empresa = ?
            ORDER BY u.fecha_registro DESC
            """
            
            results = conn.execute(query, [empresa_id]).fetchall()
            
            return [
                {
                    'cuenta': row[0],
                    'nombre': row[1],
                    'fecha_registro': row[2].isoformat() if row[2] else None
                }
                for row in results
            ]
    
    def user_has_access_to_account(self, empresa_id: int, account_name: str) -> bool:
        """Verifica si una empresa tiene acceso a una cuenta específica"""
        with self.get_connection() as conn:
            query = """
            SELECT COUNT(*) 
            FROM usuario u
            WHERE u.id_empresa = ? AND u.cuenta = ?
            """
            
            result = conn.execute(query, [empresa_id, account_name]).fetchone()
            return result[0] > 0 if result else False

# Instancia global del servicio
auth_service = AuthService()
