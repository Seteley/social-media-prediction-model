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
    # Seleccionar solo columnas numéricas relevantes
    features = ['respuestas', 'retweets', 'likes', 'guardados', 'vistas']
    X = df[features].fillna(0)
    # Escalar
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    # Índice de Silhouette para diferentes valores de k
    silhouettes = []
    K = range(2, 11)
    for k in K:
        kmeans = KMeans(n_clusters=k, random_state=42)
        labels = kmeans.fit_predict(X_scaled)
        score = silhouette_score(X_scaled, labels)
        silhouettes.append(score)
    plt.figure(figsize=(7,4))
    plt.plot(K, silhouettes, marker='o')
    plt.xlabel('Número de Clusters')
    plt.ylabel('Índice de Silhouette')
    plt.title('Silhouette Score vs Número de Clusters')
    plt.show()
    # KMeans con el número de clusters elegido (por defecto n_clusters)
    kmeans = KMeans(n_clusters=n_clusters, random_state=42)
    labels = kmeans.fit_predict(X_scaled)
    df['cluster_kmeans'] = labels
    sil = silhouette_score(X_scaled, labels)
    print(f'Silhouette KMeans (k={n_clusters}): {sil:.3f}')
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
    return df

if __name__ == "__main__":
    # Cambia el path al archivo CSV limpio que quieras analizar
    csv_path = 'data/interbank_clean.csv'  # Ejemplo
    # csv_path = '../../data/elonmusk_clean.csv'  # Ejemplo
    run_kmeans_clustering(csv_path)
