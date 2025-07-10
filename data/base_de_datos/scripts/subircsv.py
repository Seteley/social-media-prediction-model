import duckdb
import pandas as pd
import glob
import os

print("Conectando a la base de datos...")
con = duckdb.connect("data/base_de_datos/social_media.duckdb")
print("Conexión OK")

print("Cargando usuarios...")
usuarios = pd.read_sql("SELECT id_usuario, cuenta FROM usuario", con)
print("Usuarios cargados")
usuario_map = dict(zip(usuarios['cuenta'], usuarios['id_usuario']))
print("Mapeo de usuarios listo")

print("Subiendo publicaciones...")
for file in glob.glob("data/*_clean.csv"):
    print(f"Procesando archivo: {file}")
    username = os.path.basename(file).replace("_clean.csv", "")
    if username not in usuario_map:
        print(f"Usuario {username} no encontrado en la base de datos. Saltando archivo {file}.")
        continue
    try:
        df = pd.read_csv(file, encoding='utf-8')
        print(f"Leído correctamente: {file}")
    except Exception as e:
        print(f"Error leyendo {file}: {e}")
        continue
    df['id_usuario'] = usuario_map[username]
    # Seleccionar y reordenar columnas según la tabla publicaciones
    try:
        df = df[['id_usuario', 'fecha_publicacion', 'contenido', 'respuestas', 'retweets', 'likes', 'guardados', 'vistas']]
        print(df.head())
        print(df.columns)
        print(df.shape)
        batch_size = 500
        for start in range(0, len(df), batch_size):
            end = start + batch_size
            batch = df.iloc[start:end].values.tolist()
            con.executemany("INSERT INTO publicaciones (id_usuario, fecha_publicacion, contenido, respuestas, retweets, likes, guardados, vistas) VALUES (?, ?, ?, ?, ?, ?, ?, ?)", batch)
        print(f"Subido: {file}")
    except Exception as e:
        print(f"Error subiendo {file}: {e}")

print("Subiendo métricas...")
for file in glob.glob("data/*_metricas.csv"):
    print(f"Procesando archivo: {file}")
    username = os.path.basename(file).replace("_metricas.csv", "")
    if username not in usuario_map:
        print(f"Usuario {username} no encontrado en la base de datos. Saltando archivo {file}.")
        continue
    try:
        df = pd.read_csv(file, encoding='utf-8')
        print(f"Leído correctamente: {file}")
    except Exception as e:
        print(f"Error leyendo {file}: {e}")
        continue
    df['id_usuario'] = usuario_map[username]
    cols = ['id_usuario', 'hora', 'seguidores', 'tweets', 'siguiendo']
    try:
        df = df[cols]
        con.execute("INSERT INTO metrica (id_usuario, hora, seguidores, tweets, siguiendo) VALUES (?, ?, ?, ?, ?)", df.values.tolist())
        print(f"Subido: {file}")
    except Exception as e:
        print(f"Error subiendo {file}: {e}")

con.close()
print("Carga finalizada.")
