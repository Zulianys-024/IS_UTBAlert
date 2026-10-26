#!/usr/bin/env python3
"""Descarga un dataset de Kaggle y lo guarda en data/raw/."""

import argparse
import os
import shutil
import sys
from pathlib import Path


def ensure_kagglehub():
    try:
        import kagglehub
    except ModuleNotFoundError as exc:
        raise SystemExit(
            "El paquete 'kagglehub' no está instalado. Ejecuta: python -m pip install -r requirements.txt"
        ) from exc
    return kagglehub


def validate_kaggle_credentials():
    username = os.getenv("KAGGLE_USERNAME")
    api_key = os.getenv("KAGGLE_KEY")

    if bool(username) != bool(api_key):
        raise SystemExit(
            "Si usas variables de entorno, configura ambas: "
            "KAGGLE_USERNAME y KAGGLE_KEY."
        )

    if username and api_key:
        return

    if os.getenv("KAGGLE_API_TOKEN"):
        return

    credentials_dir = Path(
        os.getenv("KAGGLE_CONFIG_DIR", Path.home() / ".kaggle")
    )
    credentials_file = credentials_dir / "kaggle.json"
    if not credentials_file.is_file():
        raise SystemExit(
            "No se encontraron credenciales de Kaggle. Configura KAGGLE_USERNAME y "
            "KAGGLE_KEY, KAGGLE_API_TOKEN, o coloca kaggle.json en "
            f"'{credentials_file}'."
        )


def parse_args():
    parser = argparse.ArgumentParser(
        description="Descarga un dataset de Kaggle y lo guarda localmente."
    )
    parser.add_argument(
        "--dataset",
        default="waleedejaz/predict-students-dropout-and-academic-success",
        help="Slug del dataset de Kaggle (ej. usuario/nombre-dataset)",
    )
    parser.add_argument(
        "--output-name",
        default="uci_dropout_raw.csv",
        help="Nombre del archivo CSV final dentro de data/raw/",
    )
    parser.add_argument(
        "--csv-file",
        help="Nombre del CSV dentro del dataset. Si no se indica, debe haber un único CSV.",
    )
    parser.add_argument(
        "--output-dir",
        default="data/raw",
        help="Carpeta de destino para el archivo descargado.",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    validate_kaggle_credentials()
    kagglehub = ensure_kagglehub()

    print("Descargando desde Kaggle...")
    descarga_path = kagglehub.dataset_download(args.dataset)

    destino_carpeta = Path(__file__).resolve().parents[1] / args.output_dir
    destino_carpeta.mkdir(parents=True, exist_ok=True)

    archivos_csv = sorted(Path(descarga_path).rglob("*.csv"))
    if not archivos_csv:
        raise SystemExit(f"No se encontró ningún archivo CSV en la descarga de '{args.dataset}'.")

    if args.csv_file:
        archivos_csv = [archivo for archivo in archivos_csv if archivo.name == args.csv_file]
        if not archivos_csv:
            raise SystemExit(
                f"No se encontró el CSV '{args.csv_file}' en la descarga de '{args.dataset}'."
            )
    elif len(archivos_csv) > 1:
        nombres = "\n".join(f"  - {archivo.name}" for archivo in archivos_csv)
        raise SystemExit(
            "El dataset contiene varios CSV. Selecciona uno con --csv-file:\n" + nombres
        )

    archivo_destino = destino_carpeta / args.output_name
    shutil.copy2(archivos_csv[0], archivo_destino)
    print(f"Archivo guardado con éxito en {archivo_destino}")


if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        raise
    except Exception as exc:  # pragma: no cover - ayuda a depurar errores de Kaggle
        print(f"Error al descargar el dataset: {exc}", file=sys.stderr)
        raise SystemExit(1)
