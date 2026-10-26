import pandas as pd
from pathlib import Path

project_root = Path(__file__).resolve().parents[1]
source_file = project_root / "data" / "raw" / "uci_dropout_raw.csv"
output_file = project_root / "data" / "processed" / "estudiantes_academicos.csv"

df = pd.read_csv(source_file)

output_file.parent.mkdir(parents=True, exist_ok=True)
df.to_csv(output_file, index=False)
print(f"Datos procesados guardados en {output_file}")
