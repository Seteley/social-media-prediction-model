import duckdb

# Crea una base llamada "social_media.duckdb" dentro de la carpeta data/
con = duckdb.connect("data/base_de_datos/social_media.duckdb")
print("Base de datos creada.")
con.close()
