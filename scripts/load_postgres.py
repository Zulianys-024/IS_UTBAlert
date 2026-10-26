import os
import sys

import pandas as pd
import psycopg2
from psycopg2 import extras

def main():
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        print(
            "Falta configurar DATABASE_URL con la URL de conexión de PostgreSQL.",
            file=sys.stderr,
        )
        return 1

    ruta_csv = "data/processed/estudiantes_academicos.csv"
    df = pd.read_csv(ruta_csv)

    nombres_csv_a_postgres = {
        "Student ID": "student_id",
        "Course": "course",
        "Curricular units 1st sem (enrolled)": "curricular_units_1st_sem_enrolled",
        "Curricular units 2nd sem (enrolled)": "curricular_units_2nd_sem_enrolled",
        "Curricular units 1st sem (grade)": "curricular_units_1st_sem_grade",
        "Curricular units 2nd sem (grade)": "curricular_units_2nd_sem_grade",
        "Target": "target",
        "Attendance (%)": "attendance_percentage",
    }
    columnas_postgres = [
        "student_id",
        "course",
        "curricular_units_1st_sem_enrolled",
        "curricular_units_2nd_sem_enrolled",
        "curricular_units_1st_sem_grade",
        "curricular_units_2nd_sem_grade",
        "target",
        "attendance_percentage",
    ]
    # El CSV procesado usa etiquetas legibles; convertirlas al esquema de PostgreSQL.
    df = df.rename(columns=nombres_csv_a_postgres)
    faltantes = set(columnas_postgres) - set(df.columns)
    if faltantes:
        raise ValueError(f"Faltan columnas requeridas en el CSV: {', '.join(sorted(faltantes))}")

    query = (
        f"INSERT INTO estudiantes_academicos ({', '.join(columnas_postgres)}) "
        f"VALUES ({', '.join(['%s'] * len(columnas_postgres))})"
    )
    datos = list(df[columnas_postgres].itertuples(index=False, name=None))

    print("Subiendo datos a PostgreSQL...")
    with psycopg2.connect(database_url) as conn:
        with conn.cursor() as cursor:
            extras.execute_batch(cursor, query, datos)

    print(f"Carga completada: {len(datos)} filas insertadas.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
