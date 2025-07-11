from fastapi import APIRouter, HTTPException, Depends
from app.api.crud import (
    get_all, get_by_id, create_row, update_row, delete_row,
    get_publicaciones_by_usuario, get_metricas_by_usuario
)
from typing import Any, Dict
from app.auth.dependencies import auth_required
from app.auth.auth_service import auth_service

router = APIRouter(prefix="/crud", tags=["CRUD"])

# --- Publicaciones de un usuario ---
@router.get("/publicaciones/{usuario}",
    responses={
        200: {"description": "Publicaciones obtenidas exitosamente"},
        401: {"description": "Token inválido, expirado o no proporcionado"},
        403: {"description": "Sin acceso a la cuenta solicitada"},
        404: {"description": "No se encontraron publicaciones para el usuario"}
    }
)
def publicaciones_usuario(
    usuario: str,
    current_user: Dict[str, Any] = Depends(auth_required)
):
    """
    Obtiene todas las publicaciones de un usuario específico.
    
    **Requiere:** Token JWT válido y acceso a la cuenta
    
    **Parámetros:**
    - usuario: Nombre de la cuenta (debe pertenecer a tu empresa)
    
    **Códigos de respuesta:**
    - 200: Publicaciones obtenidas exitosamente
    - 401: Sin autenticación (token faltante, inválido o expirado)
    - 403: Sin acceso a la cuenta (empresa diferente)
    - 404: No se encontraron publicaciones para el usuario
    """
    # Verificar acceso a la cuenta
    if not auth_service.user_has_access_to_account(current_user['empresa_id'], usuario):
        raise HTTPException(
            status_code=403,
            detail=f"No tiene acceso a la cuenta @{usuario}"
        )
    
    rows = get_publicaciones_by_usuario(usuario)
    if not rows:
        raise HTTPException(
            status_code=404, 
            detail=f"No se encontraron publicaciones para @{usuario}."
        )
    return rows

# --- Métricas de un usuario ---
@router.get("/metricas/{usuario}",
    responses={
        200: {"description": "Métricas obtenidas exitosamente"},
        401: {"description": "Token inválido, expirado o no proporcionado"},
        403: {"description": "Sin acceso a la cuenta solicitada"},
        404: {"description": "No se encontraron métricas para el usuario"}
    }
)
def metricas_usuario(
    usuario: str,
    current_user: Dict[str, Any] = Depends(auth_required)
):
    """
    Obtiene todas las métricas de un usuario específico.
    
    **Requiere:** Token JWT válido y acceso a la cuenta
    
    **Parámetros:**
    - usuario: Nombre de la cuenta (debe pertenecer a tu empresa)
    
    **Códigos de respuesta:**
    - 200: Métricas obtenidas exitosamente
    - 401: Sin autenticación (token faltante, inválido o expirado)
    - 403: Sin acceso a la cuenta (empresa diferente)
    - 404: No se encontraron métricas para el usuario
    """
    # Verificar acceso a la cuenta
    if not auth_service.user_has_access_to_account(current_user['empresa_id'], usuario):
        raise HTTPException(
            status_code=403,
            detail=f"No tiene acceso a la cuenta @{usuario}"
        )
    
    rows = get_metricas_by_usuario(usuario)
    if not rows:
        raise HTTPException(
            status_code=404, 
            detail=f"No se encontraron métricas para @{usuario}."
        )
    return rows

# --- CRUD genérico para cualquier tabla (PROTEGIDO) ---
@router.get("/{table}/all",
    responses={
        200: {"description": "Datos obtenidos exitosamente"},
        401: {"description": "Token inválido, expirado o no proporcionado"},
        403: {"description": "Sin permisos para acceder"}
    }
)
def crud_get_all(
    table: str, 
    current_user: Dict[str, Any] = Depends(auth_required)
):
    """Obtiene todos los registros de una tabla (requiere JWT)"""
    return get_all(table)

@router.get("/{table}/{id_field}/{id_value}",
    responses={
        200: {"description": "Registro obtenido exitosamente"},
        401: {"description": "Token inválido, expirado o no proporcionado"},
        403: {"description": "Sin permisos para acceder"},
        404: {"description": "Registro no encontrado"}
    }
)
def crud_get_by_id(
    table: str, 
    id_field: str, 
    id_value: Any,
    current_user: Dict[str, Any] = Depends(auth_required)
):
    """Obtiene un registro por ID (requiere JWT)"""
    row = get_by_id(table, id_field, id_value)
    if not row:
        raise HTTPException(status_code=404, detail="No encontrado")
    return row

@router.post("/{table}/create",
    responses={
        200: {"description": "Registro creado exitosamente"},
        401: {"description": "Token inválido, expirado o no proporcionado"},
        403: {"description": "Sin permisos para crear"}
    }
)
def crud_create(
    table: str, 
    data: Dict,
    current_user: Dict[str, Any] = Depends(auth_required)
):
    """Crea un nuevo registro (requiere JWT)"""
    last_id = create_row(table, data)
    return {"inserted_id": last_id}

@router.put("/{table}/update/{id_field}/{id_value}",
    responses={
        200: {"description": "Registro actualizado exitosamente"},
        401: {"description": "Token inválido, expirado o no proporcionado"},
        403: {"description": "Sin permisos para actualizar"}
    }
)
def crud_update(
    table: str, 
    id_field: str, 
    id_value: Any, 
    data: Dict,
    current_user: Dict[str, Any] = Depends(auth_required)
):
    """Actualiza un registro (requiere JWT)"""
    n = update_row(table, id_field, id_value, data)
    return {"updated": n}

@router.delete("/{table}/delete/{id_field}/{id_value}",
    responses={
        200: {"description": "Registro eliminado exitosamente"},
        401: {"description": "Token inválido, expirado o no proporcionado"},
        403: {"description": "Sin permisos para eliminar"}
    }
)
def crud_delete(
    table: str, 
    id_field: str, 
    id_value: Any,
    current_user: Dict[str, Any] = Depends(auth_required)
):
    """Elimina un registro (requiere JWT)"""
    n = delete_row(table, id_field, id_value)
    return {"deleted": n}
