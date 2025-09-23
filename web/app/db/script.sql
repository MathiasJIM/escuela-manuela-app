-- Habilitar extensión para UUIDs
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- Tabla: anio_lectivo
CREATE TABLE anio_lectivo (
    id_anio UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    nombre VARCHAR(9) UNIQUE NOT NULL, 
    fecha_inicio DATE NOT NULL,
    fecha_fin DATE NOT NULL,
    activo BOOLEAN NOT NULL DEFAULT FALSE
);

-- Tabla: usuario
CREATE TABLE usuario (
    id_usuario UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    nombre VARCHAR(100) NOT NULL,
    correo VARCHAR(100) UNIQUE NOT NULL,
    rol VARCHAR(20) NOT NULL CHECK (rol IN ('direccion', 'profesor', 'padre')),
    contrasena_hash TEXT NOT NULL,
    activo BOOLEAN NOT NULL DEFAULT FALSE,
    foto TEXT
);

-- Tabla: profesor
CREATE TABLE profesor (
    id_profesor UUID PRIMARY KEY REFERENCES usuario(id_usuario) ON DELETE CASCADE
);

-- Tabla: comite
CREATE TABLE comite (
    id_comite UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    nombre VARCHAR(100) NOT NULL
);

-- Tabla: docente_comite
CREATE TABLE docente_comite (
    id_profesor UUID REFERENCES profesor(id_profesor) ON DELETE CASCADE,
    id_comite UUID REFERENCES comite(id_comite) ON DELETE CASCADE,
    PRIMARY KEY (id_profesor, id_comite)
);

-- Tabla: materia
CREATE TABLE materia (
    id_materia UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    nombre VARCHAR(100) NOT NULL
);

-- Tabla intermedia: profesor_materia
CREATE TABLE profesor_materia (
    id_profesor UUID REFERENCES profesor(id_profesor) ON DELETE CASCADE,
    id_materia UUID REFERENCES materia(id_materia) ON DELETE CASCADE,
    id_anio UUID REFERENCES anio_lectivo(id_anio),
    PRIMARY KEY (id_profesor, id_materia, id_anio)
);

-- Tabla: seccion
CREATE TABLE seccion (
    id_seccion UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    nombre VARCHAR(20) NOT NULL,
    grado VARCHAR(20) NOT NULL,
    id_profesor_guia UUID REFERENCES usuario(id_usuario),
    id_anio UUID REFERENCES anio_lectivo(id_anio) ON DELETE CASCADE
);

-- Tabla intermedia: profesor_seccion
CREATE TABLE profesor_seccion (
    id_profesor UUID REFERENCES profesor(id_profesor) ON DELETE CASCADE,
    id_seccion UUID REFERENCES seccion(id_seccion) ON DELETE CASCADE,
    PRIMARY KEY (id_profesor, id_seccion)
);

CREATE TABLE estudiante (
    id_estudiante UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    cedula VARCHAR(20) NOT NULL UNIQUE,
    nombre VARCHAR(50) NOT NULL,
    primer_apellido VARCHAR(50) NOT NULL,
    segundo_apellido VARCHAR(50) NOT NULL,
    id_padre UUID REFERENCES usuario(id_usuario) ON DELETE SET NULL,
    id_seccion UUID REFERENCES seccion(id_seccion) ON DELETE SET NULL
);


-- Tabla: matricula
CREATE TABLE matricula (
    id_matricula UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    id_estudiante UUID REFERENCES estudiante(id_estudiante) ON DELETE CASCADE,
    id_seccion UUID REFERENCES seccion(id_seccion) ON DELETE CASCADE,
    id_anio UUID REFERENCES anio_lectivo(id_anio),
    fecha_matricula DATE DEFAULT CURRENT_DATE,
    UNIQUE (id_estudiante, id_anio)
);

-- Tabla: cita
CREATE TABLE cita (
    id_cita UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    id_padre UUID REFERENCES usuario(id_usuario) ON DELETE CASCADE,
    id_profesor UUID REFERENCES profesor(id_profesor) ON DELETE CASCADE,
    fecha_hora TIMESTAMP NOT NULL,
    estado VARCHAR(20) CHECK (estado IN ('pendiente', 'aceptada', 'rechazada'))
);

-- Tabla: aviso
CREATE TABLE aviso (
    id_aviso UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    titulo VARCHAR(100) NOT NULL,
    contenido TEXT NOT NULL,
    fecha_envio TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    destinatario VARCHAR(20) CHECK (destinatario IN ('todos', 'profesores', 'padres'))
);

-- Tabla: evento
CREATE TABLE evento (
    id_evento UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    titulo VARCHAR(100) NOT NULL,
    descripcion TEXT NOT NULL,
    fecha_hora TIMESTAMP NOT NULL,
    destinatario VARCHAR(20) CHECK (destinatario IN ('todos', 'para mi'))
);

CREATE TABLE notificacion (
    id_notificacion UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    id_usuario UUID REFERENCES usuario(id_usuario) ON DELETE CASCADE,
    titulo VARCHAR(100) NOT NULL,
    mensaje TEXT NOT NULL,
    fecha TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    tipo VARCHAR(20) CHECK (tipo IN ('sistema', 'cita', 'material', 'calendario', 'mensaje', 'alerta', 'aviso')),
    leida BOOLEAN NOT NULL DEFAULT FALSE,
    accionable BOOLEAN DEFAULT FALSE,
    accion VARCHAR(50),
    accion_texto VARCHAR(50),
    accion_icono VARCHAR(30),
    referencia_id UUID,
    referencia_tipo VARCHAR(30)
);

-- Tabla: asistencia
CREATE TABLE asistencia (
    id_asistencia UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    id_estudiante UUID REFERENCES estudiante(id_estudiante) ON DELETE CASCADE,
    id_materia UUID REFERENCES materia(id_materia),
    id_anio UUID REFERENCES anio_lectivo(id_anio),
    fecha DATE NOT NULL,
    estado VARCHAR(20) CHECK (estado IN ('presente', 'ausente', 'justificada', 'injustificada')),
    comentario TEXT,
    UNIQUE (id_estudiante, id_materia, fecha)
);

-- Tabla: bloque_horario
CREATE TABLE bloque_horario (
    id_bloque UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    nombre VARCHAR(20),
    hora_inicio TIME,
    hora_fin TIME
);

-- Tabla: horario
CREATE TABLE horario (
    id_horario UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    id_seccion UUID REFERENCES seccion(id_seccion) ON DELETE CASCADE,
    id_materia UUID REFERENCES materia(id_materia) ON DELETE CASCADE,
    id_profesor UUID REFERENCES profesor(id_profesor) ON DELETE CASCADE,
    id_anio UUID REFERENCES anio_lectivo(id_anio),
    dia VARCHAR(10) CHECK (dia IN ('lunes','martes','miércoles','jueves','viernes')),
    id_bloque UUID REFERENCES bloque_horario(id_bloque),
    UNIQUE (id_seccion, id_anio, dia, id_bloque)
);

-- Tabla: junta_patronato
CREATE TABLE junta_patronato (
    id_miembro UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    nombre VARCHAR(100) NOT NULL,
    puesto VARCHAR(100) NOT NULL,
    foto TEXT,
    tipo VARCHAR(20) NOT NULL CHECK (tipo IN ('junta', 'patronato'))
);

-- Tabla: informe_junta_patronato
CREATE TABLE informe_junta_patronato (
    id_informe UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    id_miembro UUID REFERENCES junta_patronato(id_miembro) ON DELETE CASCADE,
    titulo VARCHAR(100) NOT NULL,
    archivo TEXT NOT NULL,
    fecha_subida TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabla: cuenta_donacion
CREATE TABLE cuenta_donacion (
    id_cuenta UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    descripcion TEXT,
    numero_cuenta VARCHAR(30),
    sinpe VARCHAR(30),
    activa BOOLEAN DEFAULT TRUE
);

-- Tabla: nota
CREATE TABLE nota (
    id_nota UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    id_estudiante UUID REFERENCES estudiante(id_estudiante) ON DELETE CASCADE,
    id_materia UUID REFERENCES materia(id_materia),
    id_anio UUID REFERENCES anio_lectivo(id_anio),
    tipo VARCHAR(30) CHECK (tipo IN ('tarea', 'prueba', 'trabajo cotidiano')),
    descripcion TEXT,
    calificacion DECIMAL(5,2) CHECK (calificacion >= 0 AND calificacion <= 100),
    fecha DATE NOT NULL
);

-- Tabla: documento
CREATE TABLE documento (
    id_documento UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    titulo VARCHAR(100) NOT NULL,
    descripcion TEXT,
    tipo VARCHAR(30) CHECK (tipo IN ('planeamiento', 'circular', 'material', 'informe', 'otro')) NOT NULL,
    archivo TEXT NOT NULL,
    fecha_subida TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    subido_por UUID REFERENCES usuario(id_usuario) ON DELETE SET NULL,
    destinatario VARCHAR(20) CHECK (destinatario IN ('direccion', 'profesores', 'padres', 'todos')) DEFAULT 'todos'
);

CREATE TABLE noticia (
    id_noticia UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    titulo VARCHAR(100) NOT NULL,
    contenido TEXT NOT NULL,
    fecha_publicacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    publicada_por UUID REFERENCES usuario(id_usuario) ON DELETE SET NULL
);
