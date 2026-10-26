import pandas as pd
from pathlib import Path

project_root = Path(__file__).resolve().parents[1]
source_file = project_root / "data" / "raw" / "uci_dropout_raw.csv"
output_file = project_root / "data" / "processed" / "estudiantes_academicos.csv"

df = pd.read_csv(source_file, sep=";")

# -----------------------------
# Seleccionar solo las variables que vas a usar
# -----------------------------
# Cambia estas columnas por las que realmente te interesen.
# IMPORTANTE: los nombres deben coincidir exactamente con los encabezados del CSV.
#columns_to_keep = [
    #"Age at enrollment",     # ejemplo: edad al matricularse
    #"Gender",                # ejemplo: género
    #"Admission grade",       # ejemplo: nota de admisión
    #"Scholarship holder",    # ejemplo: beca
    #"Target",                # etiqueta / resultado objetivo
    # "Marital status",
    # "Application mode",
    # "Course",
    # "Previous qualification",
    # agrega aquí las variables que quieras usar
#]

# Si quieres conservar solo esas columnas:
#df = df[columns_to_keep]

# Si no quieres usar la variable "Target" como característica, la puedes quitar
# de la lista anterior y dejarla solo si la necesitas como etiqueta.

output_file.parent.mkdir(parents=True, exist_ok=True)
df.to_csv(output_file, index=False)
print(f"Datos procesados guardados en {output_file}")
