from unofficial_livecounts_api.twitter import TwitterAgent
from datetime import datetime
import csv
import os

def guardar_metricas_usuario(nombre_usuario):
    carpeta = "data"
    os.makedirs(carpeta, exist_ok=True)
    archivo_csv = os.path.join(carpeta, f"{nombre_usuario}_metricas.csv")

    if not os.path.exists(archivo_csv):
        with open(archivo_csv, mode='w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(["Hora", "Usuario", "Seguidores", "Tweets", "Following"])

    hora = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    metricas = TwitterAgent.fetch_user_metrics(query=nombre_usuario)
    seguidores = metricas.follower_count
    tweets = metricas.tweet_count
    following = metricas.following_count

    with open(archivo_csv, mode='a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow([hora, f"@{nombre_usuario}", seguidores, tweets, following])

    print(f"[{hora}] @{nombre_usuario} | Seguidores: {seguidores} | Tweets: {tweets} | Following: {following}")

if __name__ == "__main__":
    guardar_metricas_usuario("interbank")
