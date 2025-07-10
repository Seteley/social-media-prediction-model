import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import DBSCAN
from sklearn.metrics import silhouette_score, davies_bouldin_score, calinski_harabasz_score
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.decomposition import PCA

def run_dbscan_clustering(username, eps=0.5, min_samples=5):
    # Construir el path del archivo CSV a partir del username
    csv_path = f'data/{username}_clean.csv'
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
    # Visualización
    pca = PCA(n_components=2)
    X_pca = pca.fit_transform(X_scaled)
    plt.figure(figsize=(7,5))
    sns.scatterplot(x=X_pca[:,0], y=X_pca[:,1], hue=labels, palette='Set2', legend='full')
    plt.title(f'DBSCAN Clusters para {username}')
    plt.show()
    # Promedios por cluster (excluyendo ruido)
    num_cols = df.select_dtypes(include='number').columns
    print('Promedios por cluster (sin ruido):')
    print(df[df['cluster_dbscan'] != -1].groupby('cluster_dbscan')[num_cols].mean())
    # Mostrar los primeros 5 datos de cada cluster (excluyendo ruido)
    print('\nPrimeros 5 datos de cada cluster (sin ruido):')
    for cluster in sorted(set(labels)):
        if cluster == -1:
            continue
        print(f'\nCluster {cluster}:')
        muestra = df[df['cluster_dbscan'] == cluster].head(5).copy()
        if 'contenido' in muestra.columns:
            print(muestra[['fecha_publicacion', 'respuestas', 'retweets', 'likes', 'guardados', 'vistas', 'contenido']])
        else:
            print(muestra)
    return df

if __name__ == "__main__":
    # Cambia el username por el que quieras analizar
    username = 'Interbank'  # Ejemplo
    run_dbscan_clustering(username, eps=1.58, min_samples=4)  # Ajusta eps y min_samples según sea necesario
