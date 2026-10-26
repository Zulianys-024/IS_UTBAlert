import pandas as pd
import psycopg2
from psycopg2 import extras

# 1. Leer el CSV que modificaste por fuera y guardaste en processed
ruta_csv = "data/processed/estudiantes_academicos.csv"
df = pd.read_csv(ruta_csv)

# 2. Conectar a tu base de datos de PostgreSQL
# ( REEMPLAZA ESTOS DATOS CON LOS TUYOS )
conn = psycopg2.connect(
    host="localhost",
    database="proyecto_desercion",
    user="postgres",
    password="12345"
)
cursor = conn.cursor()

# 3. Mapear las columnas del CSV a los nombres exactos de Postgres
# Esto asegura que se inserten en el orden correcto, sin importar cómo se llamen en tu Excel
columnas_postgres = [
    "student_id", 
    "course", 
    "curricular_units_1st_sem_enrolled", 
    "curricular_units_2nd_sem_enrolled", 
    "curricular_units_1st_sem_grade", 
    "curricular_units_2nd_sem_grade", 
    "target", 
    "attendance_percentage"
]

columnas_query = ", ".join(columnas_postgres)
valores_query = ",".join(["%s"] * len(columnas_postgres))
query = f"INSERT INTO estudiantes_academicos ({columnas_query}) VALUES ({valores_query})"

# 4. Insertar los datos en bloque de forma masiva
print("Subiendo datos a PostgreSQL...")
datos_a_insertar = [tuple(x) for x in df.to_numpy()]
extras.execute_batch(cursor, query, datos_a_insertar)

# 5. Confirmar cambios y cerrar la conexión
conn.commit()
cursor.close()
conn.close()

print("¡Éxito! Tu base de datos en PostgreSQL ya tiene guardado el nuevo dataset modificado.")
