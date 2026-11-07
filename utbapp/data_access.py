from __future__ import annotations

import json
import os
from datetime import datetime
from pathlib import Path

import pandas as pd

from .risk_engine import add_risk_columns

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data" / "processed"
FOLLOWUPS_PATH = ROOT / "data" / "seguimientos_demo.json"


def normalize_period(value) -> str:
    text = str(value).split(".")[0]
    return text if len(text) == 6 else text.zfill(6)


def period_label(value) -> str:
    value = normalize_period(value)
    return f"{value[:4]}-{value[4:]}" if len(value) == 6 else value


def load_data() -> tuple[pd.DataFrame, pd.DataFrame, bool]:
    students = pd.read_csv(DATA_DIR / "estudiantes_utb_sinteticos.csv", dtype={"estudiante_id": str, "periodo_ingreso": str})
    history = pd.read_csv(DATA_DIR / "historial_academico_utb_sintetico.csv", dtype={"estudiante_id": str, "periodo_academico": str})
    students["periodo_ingreso"] = students["periodo_ingreso"].map(normalize_period)
    history["periodo_academico"] = history["periodo_academico"].map(normalize_period)
    thresholds = None
    history = add_risk_columns(history, thresholds)
    return students, history, False


def latest_by_student(history: pd.DataFrame, period: str | None = None) -> pd.DataFrame:
    current = history if not period or period == "Todos los periodos" else history[history.periodo_academico == period]
    return current.sort_values(["estudiante_id", "periodo_academico"]).groupby("estudiante_id", as_index=False).tail(1)


def read_followups() -> list[dict]:
    if not FOLLOWUPS_PATH.exists():
        return []
    try:
        return json.loads(FOLLOWUPS_PATH.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return []


def _write_followups(records: list[dict]) -> None:
    FOLLOWUPS_PATH.parent.mkdir(parents=True, exist_ok=True)
    FOLLOWUPS_PATH.write_text(json.dumps(records, ensure_ascii=False, indent=2), encoding="utf-8")


def save_followup(student_id: str, period: str, responsible: str, note: str, next_action: str, next_date: str, status: str = "Nueva"):
    records = read_followups()
    records.append({
        "estudiante_id": student_id,
        "periodo": period,
        "responsable": responsible,
        "nota": note,
        "proxima_accion": next_action,
        "fecha_proxima_accion": next_date,
        "estado": status,
        "created_at": datetime.now().isoformat(timespec="seconds"),
    })
    _write_followups(records)
    return records[-1]


def update_followup(
    index: int,
    period: str,
    note: str,
    next_action: str,
    next_date: str,
) -> dict:
    """Actualiza un seguimiento existente conservando su fecha de creación.

    ``created_at`` nunca se sobrescribe; cada edición agrega/actualiza
    ``updated_at`` con el momento exacto del guardado.
    """
    records = read_followups()
    if index < 0 or index >= len(records):
        raise IndexError("Seguimiento no encontrado")
    record = records[index]
    record["periodo"] = period
    record["nota"] = note
    record["proxima_accion"] = next_action
    record["fecha_proxima_accion"] = next_date
    record["updated_at"] = datetime.now().isoformat(timespec="seconds")
    _write_followups(records)
    return record


def delete_followup(index: int) -> dict:
    """Elimina el seguimiento indicado de la fuente de datos local."""
    records = read_followups()
    if index < 0 or index >= len(records):
        raise IndexError("Seguimiento no encontrado")
    removed = records.pop(index)
    _write_followups(records)
    return removed


def followup_status(student_id: str, records: list[dict] | None = None) -> str:
    records = records if records is not None else read_followups()
    matching = [r for r in records if r.get("estudiante_id") == student_id]
    if not matching:
        return "Sin acompañamiento"
    if any(r.get("estado") == "En seguimiento" for r in matching):
        return "En seguimiento"
    if any(r.get("estado") == "Nueva" for r in matching):
        return "Nueva"
    return "Cerrada"
