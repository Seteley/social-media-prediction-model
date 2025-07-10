import duckdb
con = duckdb.connect("data/base_de_datos/social_media.duckdb")
print("OK")
con.close()