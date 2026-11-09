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


def save_followup(student_id: str, period: str, responsible: str, note: str, next_action: str, next_date: str, status: str = "En seguimiento"):
    records = read_followups()
    if any(r.get("estudiante_id") == student_id for r in records):
        raise ValueError("El estudiante ya tiene un seguimiento; usa actualizar reporte")
    records.append({
        "estudiante_id": student_id,
        "periodo": period,
        "responsable": responsible,
        "nota": note,
        "proxima_accion": next_action,
        "fecha_proxima_accion": next_date,
        "estado": status,
        "report_updates": 0,
        "created_at": datetime.now().isoformat(timespec="seconds"),
    })
    _write_followups(records)
    return records[-1]


def create_followup_update(index: int, period: str, responsible: str, note: str, next_action: str, next_date: str, status: str = "En seguimiento") -> dict:
    """Agrega un nuevo registro para el estudiante, conservando el anterior."""
    records = read_followups()
    if index < 0 or index >= len(records):
        raise IndexError("Seguimiento no encontrado")
    previous = records[index]
    record = {
        "estudiante_id": previous["estudiante_id"],
        "periodo": period,
        "responsable": responsible,
        "nota": note,
        "proxima_accion": next_action,
        "fecha_proxima_accion": next_date,
        "estado": status,
        "report_updates": int(previous.get("report_updates") or 0) + 1,
        "created_at": datetime.now().isoformat(timespec="seconds"),
    }
    records.append(record)
    _write_followups(records)
    return record


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


def close_followup(index: int, reason: str = "") -> dict:
    """Cierra el seguimiento indicado y guarda la fecha, hora y motivo de cierre."""
    records = read_followups()
    if index < 0 or index >= len(records):
        raise IndexError("Seguimiento no encontrado")
    record = records[index]
    if record.get("estado") == "Cerrada":
        raise ValueError("El seguimiento ya está cerrado")
    record["estado"] = "Cerrada"
    record["closed_at"] = datetime.now().isoformat(timespec="seconds")
    reason = (reason or "").strip()
    if reason:
        record["close_reason"] = reason
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


def followup_history(student_id: str, records: list[dict] | None = None) -> list[dict]:
    """Historial completo de seguimientos de un estudiante.

    La fuente de datos (``data/seguimientos_demo.json``) es una lista plana
    donde cada estudiante puede tener varios registros, identificables por
    su ``created_at``. Esta función los agrupa y ordena del más antiguo
    (primera nota registrada) al más reciente.
    """
    records = records if records is not None else read_followups()
    return sorted(
        (r for r in records if r.get("estudiante_id") == student_id),
        key=lambda r: r.get("created_at") or "",
    )


def vigente_followup(student_id: str, records: list[dict] | None = None) -> dict | None:
    """Registro vigente de un estudiante: el más reciente de su historial.

    Es el que se muestra en la tabla de casos (la fila "actual"); los demás
    registros del historial permanecen como versiones anteriores.
    """
    history = followup_history(student_id, records)
    return history[-1] if history else None


def followup_status(student_id: str, records: list[dict] | None = None) -> str:
    records = records if records is not None else read_followups()
    matching = [r for r in records if r.get("estudiante_id") == student_id]
    if not matching:
        return "Sin acompañamiento"
    # El estado vigente es el del registro más reciente: así el cierre de un
    # seguimiento se refleja de inmediato en Alertas, Estudiantes y Seguimientos.
    latest = max(matching, key=lambda r: r.get("created_at") or "")
    status = latest.get("estado") or "En seguimiento"
    # "Nueva" era el estado inicial de un caso que ya tiene acompañamiento;
    # se normaliza a "En seguimiento" para que aparezca en esa bandeja.
    return "En seguimiento" if status == "Nueva" else status
