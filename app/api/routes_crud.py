from fastapi import APIRouter, HTTPException
from app.api.crud import (
    get_all, get_by_id, create_row, update_row, delete_row,
    get_publicaciones_by_usuario, get_metricas_by_usuario
)
from typing import Any, Dict

router = APIRouter(prefix="/crud", tags=["CRUD"])

# --- Publicaciones de un usuario ---
@router.get("/publicaciones/{usuario}")
def publicaciones_usuario(usuario: str):
    rows = get_publicaciones_by_usuario(usuario)
    if not rows:
        raise HTTPException(status_code=404, detail="No se encontraron publicaciones para el usuario.")
    return rows

# --- Métricas de un usuario ---
@router.get("/metricas/{usuario}")
def metricas_usuario(usuario: str):
    rows = get_metricas_by_usuario(usuario)
    if not rows:
        raise HTTPException(status_code=404, detail="No se encontraron métricas para el usuario.")
    return rows

# --- CRUD genérico para cualquier tabla ---
@router.get("/{table}/all")
def crud_get_all(table: str):
    return get_all(table)

@router.get("/{table}/{id_field}/{id_value}")
def crud_get_by_id(table: str, id_field: str, id_value: Any):
    row = get_by_id(table, id_field, id_value)
    if not row:
        raise HTTPException(status_code=404, detail="No encontrado")
    return row

@router.post("/{table}/create")
def crud_create(table: str, data: Dict):
    last_id = create_row(table, data)
    return {"inserted_id": last_id}

@router.put("/{table}/update/{id_field}/{id_value}")
def crud_update(table: str, id_field: str, id_value: Any, data: Dict):
    n = update_row(table, id_field, id_value, data)
    return {"updated": n}

@router.delete("/{table}/delete/{id_field}/{id_value}")
def crud_delete(table: str, id_field: str, id_value: Any):
    n = delete_row(table, id_field, id_value)
    return {"deleted": n}
