"""
Capa de Acceso y Gestión de Datos para UTBAlert.
Intenta consultar la base de datos PostgreSQL mediante DATABASE_URL.
Si no está disponible o falla, realiza fallback transparente al archivo local
data/processed/estudiantes_academicos.csv.
"""

import os
from pathlib import Path
import pandas as pd
import psycopg2
from dotenv import load_dotenv

from src.utils.courses import obtener_nombre_programa
from src.services.risk_engine import MotorDeRiesgo

load_dotenv()

PROJECT_ROOT = Path(__file__).resolve().parents[2]
CSV_PATH = PROJECT_ROOT / "data" / "processed" / "estudiantes_academicos.csv"

COLUMNAS_NORMALIZADAS = [
    "student_id",
    "course",
    "curricular_units_1st_sem_enrolled",
    "curricular_units_2nd_sem_enrolled",
    "curricular_units_1st_sem_grade",
    "curricular_units_2nd_sem_grade",
    "target",
    "attendance_percentage"
]


class DataService:
    _cached_df = None

    @classmethod
    def cargar_datos_crudos(cls, forzar_recarga: bool = False) -> pd.DataFrame:
        """Carga datos desde PostgreSQL o fallback a CSV local."""
        if cls._cached_df is not None and not forzar_recarga:
            return cls._cached_df.copy()

        db_url = os.getenv("DATABASE_URL")
        df = None

        if db_url:
            try:
                with psycopg2.connect(db_url) as conn:
                    query = f"SELECT {', '.join(COLUMNAS_NORMALIZADAS)} FROM estudiantes_academicos;"
                    df = pd.read_sql_query(query, conn)
            except Exception as e:
                print(f"[DataService] Advertencia: Conexión a PostgreSQL falló ({e}). Usando CSV local...")

        if df is None or df.empty:
            if not CSV_PATH.exists():
                raise FileNotFoundError(f"No se encontró el dataset en {CSV_PATH}")

            df = pd.read_csv(CSV_PATH)
            # Normalizar nombres de columnas del CSV
            nombres_csv_a_norm = {
                "Student ID": "student_id",
                "Course": "course",
                "Curricular units 1st sem (enrolled)": "curricular_units_1st_sem_enrolled",
                "Curricular units 2nd sem (enrolled)": "curricular_units_2nd_sem_enrolled",
                "Curricular units 1st sem (grade)": "curricular_units_1st_sem_grade",
                "Curricular units 2nd sem (grade)": "curricular_units_2nd_sem_grade",
                "Target": "target",
                "Attendance (%)": "attendance_percentage",
            }
            df = df.rename(columns=nombres_csv_a_norm)

        # Mapear nombres de carreras amigables
        df["programa_nombre"] = df["course"].apply(obtener_nombre_programa)

        # Procesar con el Motor de Riesgo (calcula PPA en escala 0-5 y nivel de riesgo)
        df_procesado = MotorDeRiesgo.procesar_dataframe(df)
        cls._cached_df = df_procesado
        return df_procesado.copy()

    @classmethod
    def obtener_estudiante_por_id(cls, student_id: str):
        df = cls.cargar_datos_crudos()
        resultado = df[df["student_id"] == str(student_id)]
        if resultado.empty:
            return None
        return resultado.iloc[0].to_dict()

    @classmethod
    def obtener_lista_programas(cls):
        df = cls.cargar_datos_crudos()
        return sorted(df["programa_nombre"].dropna().unique().tolist())
