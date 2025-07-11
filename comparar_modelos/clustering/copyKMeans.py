import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score

import matplotlib.pyplot as plt
import seaborn as sns

def run_kmeans_clustering(csv_path, n_clusters=5):
    # Cargar datos
    df = pd.read_csv(csv_path)
    # Filtrar para quedarnos solo con la última medición de cada tweet (por fecha_publicacion + contenido)
    df = df.sort_values('timestamp').drop_duplicates(subset=['fecha_publicacion', 'contenido'], keep='last').reset_index(drop=True)
    # Seleccionar solo columnas numéricas relevantes
    features = ['respuestas', 'retweets', 'likes', 'guardados', 'vistas']
    X = df[features].fillna(0)
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
    plt.title('Método del Codo')
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
    # Visualización
    from sklearn.decomposition import PCA
    pca = PCA(n_components=2)
    X_pca = pca.fit_transform(X_scaled)
    plt.figure(figsize=(7,5))
    sns.scatterplot(x=X_pca[:,0], y=X_pca[:,1], hue=labels, palette='Set2')
    plt.title(f'KMeans Clusters (k={n_clusters})')
    plt.show()
    # Promedios por cluster
    num_cols = df.select_dtypes(include='number').columns
    print('Promedios por cluster:')
    print(df.groupby('cluster_kmeans')[num_cols].mean())
    # Mostrar los primeros 5 datos de cada cluster
    print('\nPrimeros 5 datos de cada cluster:')
    for cluster in sorted(df['cluster_kmeans'].unique()):
        print(f'\nCluster {cluster}:')
        muestra = df[df['cluster_kmeans'] == cluster].head(5).copy()
        # Mostrar solo columnas clave y contenido
        if 'contenido' in muestra.columns:
            print(muestra[['fecha_publicacion', 'respuestas', 'retweets', 'likes', 'guardados', 'vistas', 'contenido']])
        else:
            print(muestra)
    return df

if __name__ == "__main__":
    # Cambia el path al archivo CSV limpio que quieras analizar
    csv_path = 'data/interbank_clean.csv'  # Ejemplo
    # csv_path = '../../data/elonmusk_clean.csv'  # Ejemplo
    run_kmeans_clustering(csv_path, 2)  # Cambia n_clusters si es necesario
