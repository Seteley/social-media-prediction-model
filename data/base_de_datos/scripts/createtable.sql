-- Tabla de usuarios
CREATE TABLE IF NOT EXISTS usuario (
    id_usuario INTEGER PRIMARY KEY,
    cuenta TEXT NOT NULL UNIQUE,
    nombre TEXT,
    fecha_registro DATE DEFAULT current_date
);

-- Publicaciones
CREATE TABLE IF NOT EXISTS publicaciones (
    id_publicacion INTEGER PRIMARY KEY,
    id_usuario INTEGER NOT NULL,
    fecha_publicacion TIMESTAMP NOT NULL,
    contenido TEXT,
    respuestas INTEGER,
    retweets INTEGER,
    likes INTEGER,
    guardados INTEGER,
    vistas INTEGER,
    FOREIGN KEY (id_usuario) REFERENCES usuario(id_usuario)
);

-- Métricas por hora
CREATE TABLE IF NOT EXISTS metrica (
    id_metrica INTEGER PRIMARY KEY,
    id_usuario INTEGER NOT NULL,
    hora TIMESTAMP NOT NULL,
    seguidores INTEGER,
    tweets INTEGER,
    siguiendo INTEGER,
    FOREIGN KEY (id_usuario) REFERENCES usuario(id_usuario)
);

-- Modelos entrenados
CREATE TABLE IF NOT EXISTS modelo (
    id_modelo INTEGER PRIMARY KEY,
    id_usuario INTEGER NOT NULL,
    tipo_modelo TEXT,
    parametros TEXT,
    fecha_entrenamiento DATE,
    archivo_modelo TEXT,
    FOREIGN KEY (id_usuario) REFERENCES usuario(id_usuario)
);
