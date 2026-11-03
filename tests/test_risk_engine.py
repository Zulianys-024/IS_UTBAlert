import pandas as pd

from utbapp.risk_engine import evaluate_record


def test_high_when_average_and_attendance_are_low():
    row = pd.Series({
        "promedio_ponderado_acumulado": 2.9,
        "porcentaje_asistencia": 60,
        "asignaturas_reprobadas_periodo": 0,
        "retraso_academico": 0,
        "nivel_actual": 3,
        "avance_plan": 24,
        "asignaturas_canceladas": 0,
    })
    result = evaluate_record(row)
    assert result.level == "Alto"
    assert result.criteria == ["C1", "C2"]


def test_low_when_no_criteria_are_met():
    row = pd.Series({
        "promedio_ponderado_acumulado": 4.2,
        "porcentaje_asistencia": 95,
        "asignaturas_reprobadas_periodo": 0,
        "retraso_academico": 0,
        "nivel_actual": 3,
        "avance_plan": 30,
        "asignaturas_canceladas": 0,
    })
    assert evaluate_record(row).level == "Bajo"
