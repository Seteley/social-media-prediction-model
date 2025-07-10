import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score

import matplotlib.pyplot as plt
import seaborn as sns

def run_kmeans_clustering(username, n_clusters=5):
    # Construir el path del archivo CSV a partir del username
    csv_path = f'data/{username}_clean.csv'
    # Cargar datos
    df = pd.read_csv(csv_path)
    # Filtrar para quedarnos solo con la última medición de cada tweet (por fecha_publicacion + contenido)
    df = df.sort_values('timestamp').drop_duplicates(subset=['fecha_publicacion', 'contenido'], keep='last').reset_index(drop=True)
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
    # Usar solo engagement_rate para clustering
    X = df[['engagement_rate']].values
    # Escalar
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    # Método del Codo (Elbow Method) para elegir el número de clusters
    inercia = []
    K = range(1, 11)
    for k in K:
        kmeans = KMeans(n_clusters=k, random_state=42)
        kmeans.fit(X_scaled)
        inercia.append(kmeans.inertia_)
    plt.figure(figsize=(7,4))
    plt.plot(K, inercia, marker='o')
    plt.xlabel('Número de Clusters')
    plt.ylabel('Inercia')
    plt.title(f'Método del Codo (engagement_rate) para {username}')
    plt.show()
    # KMeans con el número de clusters elegido (por defecto n_clusters)
    kmeans = KMeans(n_clusters=n_clusters, random_state=42)
    labels = kmeans.fit_predict(X_scaled)
    df['cluster_kmeans'] = labels
    sil = silhouette_score(X_scaled, labels)
    print(f'Silhouette KMeans (k={n_clusters}): {sil:.3f}')
    # Davies-Bouldin Index
    from sklearn.metrics import davies_bouldin_score, calinski_harabasz_score
    db_index = davies_bouldin_score(X_scaled, labels)
    ch_index = calinski_harabasz_score(X_scaled, labels)
    print(f'Davies-Bouldin Index (k={n_clusters}): {db_index:.3f}')
    print(f'Calinski-Harabasz Index (k={n_clusters}): {ch_index:.3f}')
    # Visualización adaptada para 1D (engagement_rate)
    plt.figure(figsize=(8, 4))
    for cluster in sorted(df['cluster_kmeans'].unique()):
        plt.scatter(df[df['cluster_kmeans'] == cluster]['engagement_rate'],
                    np.zeros_like(df[df['cluster_kmeans'] == cluster]['engagement_rate']),
                    label=f'Cluster {cluster}')
    plt.xlabel('Engagement Rate')
    plt.yticks([])
    plt.title(f'KMeans Clusters (k={n_clusters}) por engagement_rate para {username}')
    plt.legend()
    plt.show()

    # Promedios por cluster (solo engagement_rate)
    print('Promedios de engagement_rate por cluster:')
    print(df.groupby('cluster_kmeans')['engagement_rate'].mean())

    # Mostrar los primeros 5 datos de cada cluster
    print('\nPrimeros 5 datos de cada cluster:')
    for cluster in sorted(df['cluster_kmeans'].unique()):
        print(f'\nCluster {cluster}:')
        muestra = df[df['cluster_kmeans'] == cluster].head(5).copy()
        if 'contenido' in muestra.columns:
            print(muestra[['fecha_publicacion', 'respuestas', 'retweets', 'likes', 'guardados', 'vistas', 'engagement_rate', 'contenido']])
        else:
            print(muestra)
    return df

if __name__ == "__main__":
    # Cambia el username por el que quieras analizar
    username = 'Interbank'  # Ejemplo
    run_kmeans_clustering(username, 3)  # Cambia n_clusters si es necesario