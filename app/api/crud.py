from fastapi import HTTPException
from typing import Any, Dict, List, Optional
import duckdb

DB_PATH = "data/base_de_datos/social_media.duckdb"

# --- CRUD Genérico ---
def get_all(table: str) -> List[Dict[str, Any]]:
    with duckdb.connect(DB_PATH) as con:
        rows = con.execute(f"SELECT * FROM {table}").fetchdf().to_dict(orient="records")
    return rows

def get_by_id(table: str, id_field: str, id_value: Any) -> Optional[Dict[str, Any]]:
    with duckdb.connect(DB_PATH) as con:
        row = con.execute(f"SELECT * FROM {table} WHERE {id_field} = ?", [id_value]).fetchdf()
        if row.empty:
            return None
        return row.iloc[0].to_dict()

def create_row(table: str, data: Dict[str, Any]) -> int:
    keys = ', '.join(data.keys())
    placeholders = ', '.join(['?'] * len(data))
    values = list(data.values())
    with duckdb.connect(DB_PATH) as con:
        con.execute(f"INSERT INTO {table} ({keys}) VALUES ({placeholders})", values)
        # DuckDB: get last inserted id (if autoincrement)
        last_id = con.execute("SELECT last_insert_rowid() as id").fetchone()[0]
    return last_id

def update_row(table: str, id_field: str, id_value: Any, data: Dict[str, Any]) -> int:
    set_clause = ', '.join([f"{k} = ?" for k in data.keys()])
    values = list(data.values()) + [id_value]
    with duckdb.connect(DB_PATH) as con:
        con.execute(f"UPDATE {table} SET {set_clause} WHERE {id_field} = ?", values)
        return con.execute(f"SELECT changes() as n").fetchone()[0]

def delete_row(table: str, id_field: str, id_value: Any) -> int:
    with duckdb.connect(DB_PATH) as con:
        con.execute(f"DELETE FROM {table} WHERE {id_field} = ?", [id_value])
        return con.execute(f"SELECT changes() as n").fetchone()[0]

# --- Lecturas específicas ---
def get_publicaciones_by_usuario(usuario: str) -> List[Dict[str, Any]]:
    with duckdb.connect(DB_PATH) as con:
        rows = con.execute('''
            SELECT p.* FROM publicaciones p
            JOIN usuario u ON p.id_usuario = u.id_usuario
            WHERE u.cuenta = ?
            ORDER BY p.fecha_publicacion DESC
        ''', [usuario]).fetchdf().to_dict(orient="records")
    return rows

def get_metricas_by_usuario(usuario: str) -> List[Dict[str, Any]]:
    with duckdb.connect(DB_PATH) as con:
        rows = con.execute('''
            SELECT m.* FROM metrica m
            JOIN usuario u ON m.id_usuario = u.id_usuario
            WHERE u.cuenta = ?
            ORDER BY m.hora DESC
        ''', [usuario]).fetchdf().to_dict(orient="records")
    return rows
