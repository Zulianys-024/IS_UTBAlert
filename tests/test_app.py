import base64
import io

import pandas as pd
import pytest

import app as dashboard
from utbapp.data_access import followup_history, read_followups, vigente_followup


def test_all_dashboard_pages_render():
    dashboard.app._setup_server()

    prefs = {"lang": "es", "theme": "light"}
    for path in ("/", "/estudiantes", "/variables", "/alertas", "/seguimientos", "/reportes", "/perfil", "/perfil/editar"):
        page = dashboard.render(path, {"user": "Camila"}, {}, prefs, {}, False, 0)
        assert page is not None


def test_pages_render_in_english_and_dark_theme():
    dashboard.app._setup_server()

    prefs = {"lang": "en", "theme": "dark"}
    for path in ("/", "/estudiantes", "/perfil", "/perfil/editar"):
        page = dashboard.render(path, {"user": "Camila"}, {}, prefs, {"name": "Camila"}, False, 0)
        assert page is not None


def test_students_directory_defaults_to_active_high_risk():
    dashboard.app._setup_server()

    full = dashboard.latest_view({})
    directory = dashboard.latest_view(dashboard.dir_filters({}))

    assert not directory.empty
    assert set(directory["riesgo"].unique()) == {"Alto"}
    assert set(directory["estado_final"].unique()) == {"ACTIVO"}
    assert len(directory) < len(full)
    assert len(directory) == dashboard.active_high_risk_count()


@pytest.mark.parametrize("report_format", ["csv", "xlsx"])
def test_report_export_uses_filter_state(report_format):
    dashboard.app._setup_server()
    output, callback = next(
        (output, callback)
        for output, callback in dashboard.app.callback_map.items()
        if output == "download.data"
    )
    payload = {
        "output": output,
        "outputs": {"id": "download", "property": "data"},
        "inputs": [
            {
                "id": item["id"],
                "property": item["property"],
                "value": 1 if item["id"] == "export-btn" else 0,
            }
            for item in callback["inputs"]
        ],
        "state": [
            {
                "id": item["id"],
                "property": item["property"],
                "value": {
                    "filters": {"riesgo": "Alto"},
                    "url": "/reportes",
                    "report-format-store": report_format,
                }.get(item["id"]),
            }
            for item in callback["state"]
        ],
        "changedPropIds": ["export-btn.n_clicks"],
    }

    response = dashboard.server.test_client().post(
        "/_dash-update-component", json=payload
    )

    assert response.status_code == 200
    download = response.json["response"]["download"]["data"]
    assert download["filename"] == f"alertas_tempranas.{report_format}"
    content = base64.b64decode(download["content"]) if download.get("base64") else download["content"]
    exported = (
        pd.read_excel(io.BytesIO(content))
        if report_format == "xlsx"
        else pd.read_csv(io.StringIO(content))
    )
    assert not exported.empty
    assert set(exported["riesgo"]) == {"Alto"}


def test_followup_history_and_vigente_helpers():
    dashboard.app._setup_server()

    records = read_followups()
    assert records
    student_id = records[0]["estudiante_id"]

    history = followup_history(student_id, records)
    assert history
    assert {r["estudiante_id"] for r in history} == {student_id}
    created = [r.get("created_at") or "" for r in history]
    assert created == sorted(created)  # del más antiguo al más reciente

    vigente = vigente_followup(student_id, records)
    assert vigente == history[-1]

    assert followup_history("inexistente", records) == []
    assert vigente_followup("inexistente", records) is None


def test_followup_history_export_xlsx():
    dashboard.app._setup_server()

    records = read_followups()
    assert records
    selected = records[0]
    history = followup_history(selected["estudiante_id"], records)

    download = dashboard.export_followup_history(1, 0, dashboard.DEFAULT_PREFS)
    assert download["filename"].startswith(f"seguimiento_{selected['estudiante_id']}_")
    content = base64.b64decode(download["content"])
    exported = pd.read_excel(io.BytesIO(content))
    assert len(exported) == len(history)

    expected_columns = [
        dashboard.tr("es", key)
        for key in ("col.period", "followups.note", "col.next_action", "followups.next_date", "followups.created_at", "followups.updated_at")
    ]
    assert list(exported.columns) == expected_columns
