import pandas as pd
from pathlib import Path

project_root = Path(__file__).resolve().parents[1]
source_file = project_root / "data" / "raw" / "uci_dropout_raw.csv"
output_file = project_root / "data" / "processed" / "estudiantes_academicos.csv"

df = pd.read_csv(source_file, sep=";")

# -----------------------------
# Seleccionar solo las variables que vas a usar
# -----------------------------
# Estas son las columnas que vas a utilizar en tu caso:
columns_to_keep = [
    "Course",
    "Curricular units 1st sem (enrolled)",
    "Curricular units 2nd sem (enrolled)",
    "Curricular units 1st sem (grade)",
    "Curricular units 2nd sem (grade)",
    "Target",
    # Si más adelante cambias de variables, solo ajustas esta lista.
    # Ejemplo:
    # "Age at enrollment",
    # "Gender",
    # "Admission grade",
]

# Si quieres conservar solo esas columnas:
df = df[columns_to_keep]

# Si quieres volver a todas las columnas, comenta la línea anterior.

output_file.parent.mkdir(parents=True, exist_ok=True)
df.to_csv(output_file, index=False)
print(f"Datos procesados guardados en {output_file}")
