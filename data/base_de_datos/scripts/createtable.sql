-- Eliminar en orden para evitar conflictos de claves foráneas
DROP TABLE IF EXISTS publicaciones;
DROP TABLE IF EXISTS metrica;
DROP TABLE IF EXISTS modelo;
DROP TABLE IF EXISTS usuario_acceso;
DROP TABLE IF EXISTS usuario;
DROP TABLE IF EXISTS empresa;

-- (Re)crear todo desde cero

-- Tabla de empresas (clientes)
CREATE TABLE IF NOT EXISTS empresa (
    id_empresa INTEGER PRIMARY KEY,
    nombre TEXT NOT NULL,
    fecha_registro DATE DEFAULT current_date
);

-- Tabla de usuarios
CREATE TABLE IF NOT EXISTS usuario (
    id_usuario INTEGER PRIMARY KEY,
    id_empresa INTEGER NOT NULL,
    cuenta TEXT NOT NULL UNIQUE,
    nombre TEXT,
    fecha_registro DATE DEFAULT current_date,
    FOREIGN KEY (id_empresa) REFERENCES empresa(id_empresa)
);

-- Publicaciones
CREATE TABLE IF NOT EXISTS publicaciones (
    id_publicacion SERIAL PRIMARY KEY
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
-- Solo se guarda el mejor modelo por usuario
CREATE TABLE IF NOT EXISTS modelo (
    id_usuario INTEGER PRIMARY KEY, -- Solo un modelo por usuario
    tipo_modelo TEXT,
    parametros TEXT,
    fecha_entrenamiento DATE,
    archivo_modelo TEXT,
    FOREIGN KEY (id_usuario) REFERENCES usuario(id_usuario)
);

-- Usuarios de acceso (personas que usan la API)
CREATE TABLE IF NOT EXISTS usuario_acceso (
    id_usuario_acceso INTEGER PRIMARY KEY,
    id_empresa INTEGER NOT NULL,
    username TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    rol TEXT,
    activo BOOLEAN DEFAULT TRUE,
    FOREIGN KEY (id_empresa) REFERENCES empresa(id_empresa)
);
