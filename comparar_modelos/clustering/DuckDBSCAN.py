import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import DBSCAN
from sklearn.metrics import silhouette_score, davies_bouldin_score, calinski_harabasz_score
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.decomposition import PCA

def run_dbscan_clustering(username, eps=0.5, min_samples=3):
    # Leer datos desde DuckDB en vez de CSV
    import duckdb
    db_path = 'data/base_de_datos/social_media.duckdb'
    query = f'''
        SELECT fecha_publicacion, contenido, respuestas, retweets, likes, guardados, vistas
        FROM (
            SELECT *,
                   ROW_NUMBER() OVER (PARTITION BY fecha_publicacion, contenido ORDER BY fecha_publicacion DESC) AS rn
            FROM publicaciones
            JOIN usuario ON publicaciones.id_usuario = usuario.id_usuario
            WHERE usuario.cuenta = '{username}'
        )
        WHERE rn = 1
    '''
    con = duckdb.connect(db_path)
    df = con.execute(query).fetchdf()
    con.close()
    # Ya deduplicado en SQL, solo resetear el índice
    df = df.reset_index(drop=True)
    # Calcular engagement_rate
    df[['respuestas', 'retweets', 'likes', 'guardados', 'vistas']] = df[['respuestas', 'retweets', 'likes', 'guardados', 'vistas']].fillna(0)
    df['engagement_rate'] = 0.0
    mask_vistas = df['vistas'] > 0
    df.loc[mask_vistas, 'engagement_rate'] = (
        df.loc[mask_vistas, 'respuestas'] +
        df.loc[mask_vistas, 'retweets'] +
        df.loc[mask_vistas, 'likes'] +
        df.loc[mask_vistas, 'guardados']
    ) / df.loc[mask_vistas, 'vistas']
    # Usar engagement_rate y vistas para clustering
    X = df[['engagement_rate', 'vistas']].values
    # Escalar
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    # Gráfico de k-distancia para ayudar a elegir eps
    from sklearn.neighbors import NearestNeighbors
    neighbors = NearestNeighbors(n_neighbors=min_samples)
    neighbors_fit = neighbors.fit(X_scaled)
    distances, indices = neighbors_fit.kneighbors(X_scaled)
    distances = np.sort(distances[:, min_samples-1])
    plt.figure(figsize=(7,4))
    plt.plot(distances)
    plt.ylabel(f'Distancia al {min_samples}º vecino más cercano')
    plt.xlabel('Puntos ordenados')
    plt.title(f'Gráfico de k-distancia para DBSCAN ({username})')
    plt.show()
    # DBSCAN
    dbscan = DBSCAN(eps=eps, min_samples=min_samples)
    labels = dbscan.fit_predict(X_scaled)
    df['cluster_dbscan'] = labels
    n_clusters = len(set(labels)) - (1 if -1 in labels else 0)
    n_noise = list(labels).count(-1)
    print(f'Número de clusters encontrados (sin ruido): {n_clusters}')
    print(f'Número de puntos de ruido: {n_noise}')
    # Métricas de evaluación (solo si hay más de 1 cluster y menos que total de muestras)
    if n_clusters > 1 and n_clusters < len(df):
        sil = silhouette_score(X_scaled, labels)
        db_index = davies_bouldin_score(X_scaled, labels)
        ch_index = calinski_harabasz_score(X_scaled, labels)
        print(f'Silhouette DBSCAN: {sil:.3f}')
        print(f'Davies-Bouldin Index: {db_index:.3f}')
        print(f'Calinski-Harabasz Index: {ch_index:.3f}')
    else:
        print('No es posible calcular métricas de cluster válidas (menos de 2 clusters).')
    # Visualización 2D (engagement_rate vs vistas)
    plt.figure(figsize=(8, 5))
    for cluster in sorted(set(labels)):
        if cluster == -1:
            plt.scatter(df[df['cluster_dbscan'] == cluster]['engagement_rate'],
                        df[df['cluster_dbscan'] == cluster]['vistas'],
                        label='Ruido', marker='x', color='gray')
        else:
            plt.scatter(df[df['cluster_dbscan'] == cluster]['engagement_rate'],
                        df[df['cluster_dbscan'] == cluster]['vistas'],
                        label=f'Cluster {cluster}')
    plt.xlabel('Engagement Rate')
    plt.ylabel('Vistas')
    plt.title(f'Clusters DBSCAN por engagement_rate y vistas para {username}')
    plt.legend()
    plt.show()

    # Promedios por cluster (excluyendo ruido)
    print('Promedios de engagement_rate y vistas por cluster (sin ruido):')
    print(df[df['cluster_dbscan'] != -1].groupby('cluster_dbscan')[['engagement_rate', 'vistas']].mean())

    # Mostrar los primeros 5 datos de cada cluster (excluyendo ruido)
    print('\nPrimeros 5 datos de cada cluster (sin ruido):')
    for cluster in sorted(set(labels)):
        if cluster == -1:
            continue
        print(f'\nCluster {cluster}:')
        muestra = df[df['cluster_dbscan'] == cluster].head(5).copy()
        if 'contenido' in muestra.columns:
            print(muestra[['fecha_publicacion', 'respuestas', 'retweets', 'likes', 'guardados', 'vistas', 'engagement_rate', 'contenido']])
        else:
            print(muestra)
    return df

if __name__ == "__main__":
    # Cambia el username por el que quieras analizar
    username = 'BanBif'  # Ejemplo
    run_dbscan_clustering(username, eps=1.1, min_samples=3)  # Ajusta eps y min_samples según sea necesario
    #run_dbscan_clustering(username, eps=0.2, min_samples=3)  # Ajusta eps y min_samples según sea necesario
