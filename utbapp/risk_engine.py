from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Any


DEFAULT_THRESHOLDS = {
    "promedio_acumulado_bajo": 3.20,
    "asistencia_baja": 70.0,
    "reprobadas_periodo_altas": 2,
    "retraso_academico_alto": 3,
    "avance_plan_minimo": 0.80,
    "canceladas_altas": 2,
}


@dataclass(frozen=True)
class RiskResult:
    level: str
    score: int
    criteria: list[str]
    main_signal: str

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


def evaluate_record(row: Any, thresholds: dict[str, float] | None = None) -> RiskResult:
    t = {**DEFAULT_THRESHOLDS, **(thresholds or {})}
    criteria: list[str] = []
    signals: list[tuple[str, str]] = []

    average = float(row.get("promedio_ponderado_acumulado", 0) or 0)
    attendance = float(row.get("porcentaje_asistencia", 0) or 0)
    failed = int(row.get("asignaturas_reprobadas_periodo", 0) or 0)
    delay = int(row.get("retraso_academico", 0) or 0)
    level = float(row.get("nivel_actual", 0) or 0)
    progress = float(row.get("avance_plan", 0) or 0)
    cancelled = int(row.get("asignaturas_canceladas", 0) or 0)
    expected_progress = level * 10.0

    if average < t["promedio_acumulado_bajo"]:
        criteria.append("C1")
        signals.append(("C1", f"Promedio acumulado {average:.2f} (< {t['promedio_acumulado_bajo']:.2f})"))
    if attendance < t["asistencia_baja"]:
        criteria.append("C2")
        signals.append(("C2", f"Asistencia {attendance:.0f} % (< {t['asistencia_baja']:.0f} %)"))
    if failed > t["reprobadas_periodo_altas"]:
        criteria.append("C3")
        signals.append(("C3", f"Reprobadas en el periodo {failed} (> {int(t['reprobadas_periodo_altas'])})"))
    if delay > t["retraso_academico_alto"]:
        criteria.append("C4")
        signals.append(("C4", f"Retraso académico {delay} (> {int(t['retraso_academico_alto'])})"))
    if progress < expected_progress * t["avance_plan_minimo"]:
        criteria.append("C5")
        signals.append(("C5", f"Avance del plan {progress:.1f} % (< {expected_progress * t['avance_plan_minimo']:.1f} %)"))
    if cancelled >= t["canceladas_altas"]:
        criteria.append("C6")
        signals.append(("C6", f"Asignaturas canceladas {cancelled} (≥ {int(t['canceladas_altas'])})"))

    high = len(criteria) >= 3 or ("C1" in criteria and "C2" in criteria)
    risk = "Alto" if high else "Medio" if criteria else "Bajo"
    return RiskResult(risk, len(criteria), criteria, signals[0][1] if signals else "Sin señales relevantes")


def add_risk_columns(history, thresholds=None):
    results = history.apply(lambda row: evaluate_record(row, thresholds), axis=1)
    history = history.copy()
    history["riesgo"] = [r.level for r in results]
    history["puntaje_riesgo"] = [r.score for r in results]
    history["criterios_cumplidos"] = [", ".join(r.criteria) for r in results]
    history["senal_principal"] = [r.main_signal for r in results]
    return history
