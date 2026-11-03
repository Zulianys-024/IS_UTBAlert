-- ============================================================
-- ESQUEMA PARA CARGAR LOS DOS CSV SINTÉTICOS
-- BASE DE DATOS: ALERTAS_TEMPRANAS_BDD
-- ============================================================

-- ------------------------------------------------------------
-- 1. LIMPIEZA
-- ------------------------------------------------------------
DROP TABLE IF EXISTS VARIABLES_ACADEMICAS CASCADE;
DROP TABLE IF EXISTS ESTUDIANTE CASCADE;
DROP TABLE IF EXISTS PROGRAMA_ACADEMICO CASCADE;
DROP TABLE IF EXISTS PERIODO_ACADEMICO CASCADE;

-- ------------------------------------------------------------
-- 2. CATÁLOGOS
-- ------------------------------------------------------------
CREATE TABLE PROGRAMA_ACADEMICO (
    programa VARCHAR(150) PRIMARY KEY,
    creditos_plan SMALLINT NOT NULL
);

CREATE TABLE PERIODO_ACADEMICO (
    periodo_academico VARCHAR(6) PRIMARY KEY
);

-- ------------------------------------------------------------
-- 3. TABLA DE ESTUDIANTES
-- Esta tabla se llena con:
-- estudiantes_utb_sinteticos.csv
-- ------------------------------------------------------------
CREATE TABLE ESTUDIANTE (
    estudiante_id VARCHAR(15) PRIMARY KEY,
    programa VARCHAR(150) NOT NULL,
    periodo_ingreso VARCHAR(6) NOT NULL,
    nivel_actual SMALLINT NOT NULL,
    estado_permanencia VARCHAR(30) NOT NULL,
    semestres_cursados SMALLINT NOT NULL,
    promedio_acumulado_final DECIMAL(4,2),
    creditos_aprobados_totales INT NOT NULL,
    creditos_cursados_totales INT NOT NULL,
    creditos_reprobados_totales INT NOT NULL,
    avance_plan_final DECIMAL(5,2),
    estado_final VARCHAR(20) NOT NULL,

    CONSTRAINT Estudiante_Programa_FK
        FOREIGN KEY (programa)
        REFERENCES PROGRAMA_ACADEMICO(programa),

    CONSTRAINT Estudiante_Periodo_FK
        FOREIGN KEY (periodo_ingreso)
        REFERENCES PERIODO_ACADEMICO(periodo_academico),

    CONSTRAINT Estudiante_Permanencia_CK
        CHECK (estado_permanencia IN (
            'REGULAR',
            'CONDICIONADO',
            'PÉRDIDA_CARRERA'
        )),

    CONSTRAINT Estudiante_Resultado_CK
        CHECK (estado_final IN (
            'ACTIVO',
            'GRADUADO',
            'DESERTOR'
        ))
);

-- ------------------------------------------------------------
-- 4. HISTORIAL ACADÉMICO POR SEMESTRE
-- Esta tabla se llena con:
-- historial_academico_utb_sintetico.csv
-- ------------------------------------------------------------
CREATE TABLE VARIABLES_ACADEMICAS (
    estudiante_id VARCHAR(15) NOT NULL,
    programa VARCHAR(150) NOT NULL,
    periodo_academico VARCHAR(6) NOT NULL,
    nivel_actual SMALLINT NOT NULL,

    promedio_ponderado_semestre DECIMAL(4,2) NOT NULL,
    promedio_ponderado_acumulado DECIMAL(4,2) NOT NULL,

    asignaturas_inscritas SMALLINT NOT NULL,
    asignaturas_cursadas SMALLINT NOT NULL,
    asignaturas_aprobadas SMALLINT NOT NULL,
    asignaturas_reprobadas_periodo SMALLINT NOT NULL,
    asignaturas_reprobadas_acumuladas SMALLINT NOT NULL,
    asignaturas_canceladas SMALLINT NOT NULL,

    creditos_inscritos SMALLINT NOT NULL,
    creditos_cursados SMALLINT NOT NULL,
    creditos_aprobados SMALLINT NOT NULL,
    creditos_reprobados_acumulados INT NOT NULL,

    avance_plan DECIMAL(5,2) NOT NULL,
    retraso_academico SMALLINT NOT NULL,
    porcentaje_asistencia DECIMAL(5,2) NOT NULL,

    estado_academico VARCHAR(40) NOT NULL,
    deserto BOOLEAN NOT NULL,
    estado_final VARCHAR(20) NOT NULL,

    CONSTRAINT Historial_Estudiante_FK
        FOREIGN KEY (estudiante_id)
        REFERENCES ESTUDIANTE(estudiante_id),

    CONSTRAINT Historial_Periodo_FK
        FOREIGN KEY (periodo_academico)
        REFERENCES PERIODO_ACADEMICO(periodo_academico),

    CONSTRAINT Historial_Estudiante_Periodo_UK
        UNIQUE (estudiante_id, periodo_academico),

    CONSTRAINT Historial_Notas_CK
        CHECK (
            promedio_ponderado_semestre BETWEEN 0 AND 5
            AND promedio_ponderado_acumulado BETWEEN 0 AND 5
        )
);

-- ------------------------------------------------------------
-- 5. ÍNDICES
-- ------------------------------------------------------------
CREATE INDEX idx_estudiante_programa
ON ESTUDIANTE (programa);

CREATE INDEX idx_estudiante_estado
ON ESTUDIANTE (estado_final);

CREATE INDEX idx_historial_estudiante
ON VARIABLES_ACADEMICAS (estudiante_id);

CREATE INDEX idx_historial_periodo
ON VARIABLES_ACADEMICAS (periodo_academico);