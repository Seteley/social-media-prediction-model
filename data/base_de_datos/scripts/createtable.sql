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


-- Usando SEQUENCE para id_publicacion
CREATE SEQUENCE IF NOT EXISTS publicaciones_seq START 1;
CREATE TABLE IF NOT EXISTS publicaciones (
    id_publicacion INTEGER DEFAULT nextval('publicaciones_seq') PRIMARY KEY,
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


-- Usando SEQUENCE para id_metrica
CREATE SEQUENCE IF NOT EXISTS metrica_seq START 1;
CREATE TABLE IF NOT EXISTS metrica (
    id_metrica INTEGER DEFAULT nextval('metrica_seq') PRIMARY KEY,
    id_usuario INTEGER NOT NULL,
    hora TIMESTAMP NOT NULL,
    seguidores INTEGER,
    tweets INTEGER,
    siguiendo INTEGER,
    FOREIGN KEY (id_usuario) REFERENCES usuario(id_usuario)
);


-- Usando SEQUENCE para id_modelo (histórico)
CREATE SEQUENCE IF NOT EXISTS modelo_seq START 1;
CREATE TABLE IF NOT EXISTS modelo (
    id_modelo INTEGER DEFAULT nextval('modelo_seq') PRIMARY KEY,
    id_usuario INTEGER NOT NULL,
    tipo_modelo TEXT,
    parametros TEXT,
    fecha_entrenamiento DATE,
    archivo_modelo TEXT,
    evaluacion TEXT,
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
