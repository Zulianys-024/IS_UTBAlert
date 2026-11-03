import os
import sys
from contextlib import closing
from pathlib import Path

import pandas as pd
import psycopg2
from psycopg2 import extras


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data" / "processed"

PROGRAMAS = {
    "Ingeniería Industrial": 169,
    "Ingeniería Civil": 170,
    "Ingeniería Electrónica": 170,
    "Ingeniería Mecatrónica": 172,
    "Ingeniería de Sistemas y Computación": 162,
    "Ingeniería Biomédica": 169,
    "Arquitectura": 170,
    "Ingeniería Ambiental": 171,
    "Ingeniería Química": 175,
    "Ingeniería Naval": 168,
    "Ingeniería Mecánica": 172,
}

ESTUDIANTE_COLUMNS = [
    "estudiante_id",
    "programa",
    "periodo_ingreso",
    "nivel_actual",
    "estado_permanencia",
    "semestres_cursados",
    "promedio_acumulado_final",
    "creditos_aprobados_totales",
    "creditos_cursados_totales",
    "creditos_reprobados_totales",
    "avance_plan_final",
    "estado_final",
]

HISTORIAL_COLUMNS = [
    "estudiante_id",
    "programa",
    "periodo_academico",
    "nivel_actual",
    "promedio_ponderado_semestre",
    "promedio_ponderado_acumulado",
    "asignaturas_inscritas",
    "asignaturas_cursadas",
    "asignaturas_aprobadas",
    "asignaturas_reprobadas_periodo",
    "asignaturas_reprobadas_acumuladas",
    "asignaturas_canceladas",
    "creditos_inscritos",
    "creditos_cursados",
    "creditos_aprobados",
    "creditos_reprobados_acumulados",
    "avance_plan",
    "retraso_academico",
    "porcentaje_asistencia",
    "estado_academico",
    "deserto",
    "estado_final",
]


def read_csv(path, required_columns):
    if not path.is_file():
        raise FileNotFoundError(f"No se encontró el archivo requerido: {path}")

    dataframe = pd.read_csv(path)
    missing = set(required_columns) - set(dataframe.columns)
    if missing:
        raise ValueError(
            f"En {path.name} faltan columnas requeridas: {', '.join(sorted(missing))}"
        )
    if dataframe.empty:
        raise ValueError(f"El archivo {path.name} no contiene registros.")

    null_columns = [
        column for column in required_columns if dataframe[column].isna().any()
    ]
    if null_columns:
        raise ValueError(
            f"Hay valores vacíos en {path.name}: {', '.join(null_columns)}"
        )
    return dataframe[required_columns].copy()


def normalize_periods(dataframe, column, source_name):
    periods = dataframe[column].astype("string").str.strip()
    invalid = periods.isna() | ~periods.str.fullmatch(r"\d{6}")
    if invalid.any():
        rows = (invalid[invalid].index + 2).tolist()[:5]
        raise ValueError(
            f"{source_name}: {column} debe tener formato AAAAPP de seis dígitos. "
            f"Revisa las filas CSV: {rows}"
        )
    dataframe[column] = periods.astype(str)


def normalize_and_validate(estudiantes, historial):
    normalize_periods(estudiantes, "periodo_ingreso", "estudiantes_utb_sinteticos.csv")
    normalize_periods(
        historial, "periodo_academico", "historial_academico_utb_sintetico.csv"
    )

    if estudiantes["estudiante_id"].duplicated().any():
        raise ValueError("El CSV de estudiantes contiene estudiante_id duplicados.")
    if historial.duplicated(["estudiante_id", "periodo_academico"]).any():
        raise ValueError(
            "El CSV de historial contiene más de un registro para un estudiante y periodo."
        )

    programas_usados = set(estudiantes["programa"]) | set(historial["programa"])
    programas_desconocidos = programas_usados - set(PROGRAMAS)
    if programas_desconocidos:
        raise ValueError(
            "Hay programas sin créditos de plan definidos en el cargador: "
            + ", ".join(sorted(programas_desconocidos))
        )

    estudiantes_por_id = estudiantes.set_index("estudiante_id")["programa"]
    historial_ids = set(historial["estudiante_id"])
    ids_sin_estudiante = historial_ids - set(estudiantes_por_id.index)
    if ids_sin_estudiante:
        ejemplos = ", ".join(sorted(ids_sin_estudiante)[:5])
        raise ValueError(
            "Hay filas del historial sin estudiante correspondiente: " + ejemplos
        )

    programas_esperados = historial["estudiante_id"].map(estudiantes_por_id)
    discrepancias = historial["programa"] != programas_esperados
    if discrepancias.any():
        raise ValueError(
            "El programa de algunos registros del historial no coincide con el del estudiante."
        )


def python_records(dataframe, columns):
    # psycopg2 espera tipos nativos de Python, no escalares de NumPy/Pandas.
    records = []
    for row in dataframe[columns].itertuples(index=False, name=None):
        records.append(
            tuple(value.item() if hasattr(value, "item") else value for value in row)
        )
    return records


def upsert_statement(table, columns, conflict_columns):
    column_sql = ", ".join(columns)
    values_sql = ", ".join(["%s"] * len(columns))
    updates = [column for column in columns if column not in conflict_columns]
    update_sql = ", ".join(f"{column} = EXCLUDED.{column}" for column in updates)
    conflict_sql = ", ".join(conflict_columns)
    return (
        f"INSERT INTO {table} ({column_sql}) VALUES ({values_sql}) "
        f"ON CONFLICT ({conflict_sql}) DO UPDATE SET {update_sql}"
    )


def main():
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        print(
            "Falta configurar DATABASE_URL con la URL de conexión de PostgreSQL.",
            file=sys.stderr,
        )
        return 1

    estudiantes = read_csv(
        DATA_DIR / "estudiantes_utb_sinteticos.csv", ESTUDIANTE_COLUMNS
    )
    historial = read_csv(
        DATA_DIR / "historial_academico_utb_sintetico.csv", HISTORIAL_COLUMNS
    )
    normalize_and_validate(estudiantes, historial)

    periodos = sorted(
        set(estudiantes["periodo_ingreso"]) | set(historial["periodo_academico"])
    )
    programas = sorted(
        set(estudiantes["programa"]) | set(historial["programa"])
    )

    try:
        # Una transacción única evita dejar cargados solo algunos archivos/tablas.
        with closing(psycopg2.connect(database_url)) as conn:
            with conn:
                with conn.cursor() as cursor:
                    extras.execute_values(
                        cursor,
                        "INSERT INTO programa_academico (programa, creditos_plan) "
                        "VALUES %s ON CONFLICT (programa) DO UPDATE "
                        "SET creditos_plan = EXCLUDED.creditos_plan",
                        [(programa, PROGRAMAS[programa]) for programa in programas],
                    )
                    extras.execute_values(
                        cursor,
                        "INSERT INTO periodo_academico (periodo_academico) VALUES %s "
                        "ON CONFLICT (periodo_academico) DO NOTHING",
                        [(periodo,) for periodo in periodos],
                    )
                    extras.execute_batch(
                        cursor,
                        upsert_statement(
                            "estudiante", ESTUDIANTE_COLUMNS, ["estudiante_id"]
                        ),
                        python_records(estudiantes, ESTUDIANTE_COLUMNS),
                    )
                    extras.execute_batch(
                        cursor,
                        upsert_statement(
                            "variables_academicas",
                            HISTORIAL_COLUMNS,
                            ["estudiante_id", "periodo_academico"],
                        ),
                        python_records(historial, HISTORIAL_COLUMNS),
                    )
    except psycopg2.Error as exc:
        print(
            "No se pudo cargar la base. Confirma que ejecutaste el esquema actualizado "
            f"en Supabase y que DATABASE_URL es correcta. Detalle: {exc}",
            file=sys.stderr,
        )
        return 1

    print(
        "Carga completada: "
        f"{len(programas)} programas, {len(periodos)} periodos, "
        f"{len(estudiantes)} estudiantes y {len(historial)} registros de historial."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
