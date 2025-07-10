import duckdb

# Ejecuta scripts SQL desde Python para evitar corrupción de la base de datos

def ejecutar_sql_script(path_db, path_sql):
    with open(path_sql, 'r', encoding='utf-8') as f:
        sql = f.read()
    con = duckdb.connect(path_db)
    con.execute(sql)
    con.close()
    print(f"Script ejecutado: {path_sql}")

if __name__ == "__main__":
    db_path = "data/base_de_datos/social_media.duckdb"
    scripts = [
        "data/base_de_datos/scripts/createtable.sql",
        "data/base_de_datos/scripts/insercioninsert.sql"
    ]
    for script in scripts:
        ejecutar_sql_script(db_path, script)
    print("Todos los scripts ejecutados correctamente.")
