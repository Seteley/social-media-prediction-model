import duckdb
import os

# Definir la ruta donde se creará la base de datos
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
db_path = os.path.join(base_dir, 'social_media.duckdb')

try:
    # Crear la base de datos DuckDB (si no existe, se crea)
    conn = duckdb.connect(db_path)
    conn.close()
    print("OK")
except Exception as e:
    print(f"Error al crear la base de datos: {e}")
