import base64
import io
import json

import pandas as pd
import pytest

import app as dashboard
from utbapp.data_access import followup_history, followup_status, read_followups, vigente_followup


def _collect_ids(component, found=None):
    """Recorre un árbol de componentes Dash y recoge los ``id`` encontrados."""
    found = [] if found is None else found
    if isinstance(component, (list, tuple)):
        for child in component:
            _collect_ids(child, found)
        return found
    if hasattr(component, "children"):
        _collect_ids(component.children, found)
    component_id = getattr(component, "id", None)
    if component_id is not None:
        found.append(component_id)
    return found


def _collect_text(component, found=None):
    """Recorre un árbol de componentes Dash y recoge el texto visible."""
    found = [] if found is None else found
    if isinstance(component, (list, tuple)):
        for child in component:
            _collect_text(child, found)
        return found
    if isinstance(component, str):
        found.append(component)
        return found
    if hasattr(component, "children"):
        _collect_text(component.children, found)
    return found


def _alerts_table(active_tab="all"):
    page = dashboard.alerts_page({}, "es", False, False, active_tab)
    card = page[3]
    return next(child for child in card.children if child.__class__.__name__ == "DataTable")



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


def test_alerts_table_student_first_and_tabs_filter():
    dashboard.app._setup_server()

    table = _alerts_table("all")
    assert [column["id"] for column in table.columns] == [
        "estudiante",
        "prioridad",
        "motivo",
        "periodo",
        "estado",
    ]

    for tab, expected in (
        ("new", "Nueva"),
        ("followup", "En seguimiento"),
        ("closed", "Cerrada"),
    ):
        filtered = _alerts_table(tab)
        assert all(row["estado"] == expected for row in filtered.data)


def test_followup_lifecycle_close_and_report_updates(monkeypatch, tmp_path):
    from utbapp import data_access

    path = tmp_path / "seguimientos.json"
    path.write_text(
        json.dumps(
            [
                {
                    "estudiante_id": "T00011387",
                    "periodo": "202601",
                    "responsable": "Camila",
                    "nota": "Nota inicial",
                    "proxima_accion": "Citar",
                    "fecha_proxima_accion": "2026-11-20",
                    "estado": "Nueva",
                    "report_updates": 0,
                    "created_at": "2026-11-01T10:00:00",
                }
            ],
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    monkeypatch.setattr(data_access, "FOLLOWUPS_PATH", path)

    assert followup_status("T00011387") == "Nueva"

    updated = data_access.create_followup_update(
        0, "202601", "Camila", "Segunda nota", "Esperar", "2026-11-25", "En seguimiento"
    )
    assert updated["report_updates"] == 1
    assert followup_status("T00011387") == "En seguimiento"

    closed = data_access.close_followup(1)
    assert closed["estado"] == "Cerrada"
    assert closed["closed_at"]
    assert followup_status("T00011387") == "Cerrada"

    with pytest.raises(ValueError):
        data_access.close_followup(1)


def test_closed_followup_detail_modal_fields():
    dashboard.app._setup_server()

    record = {
        "estudiante_id": "T00011387",
        "periodo": "202601",
        "responsable": "Camila",
        "nota": "Nota",
        "proxima_accion": "Citar",
        "fecha_proxima_accion": "2026-11-20",
        "estado": "Cerrada",
        "report_updates": 3,
        "created_at": "2026-11-01T10:00:00",
        "closed_at": "2026-11-07T15:30:00",
    }
    body = dashboard.closed_followup_detail_modal("es", record)
    ids = _collect_ids(body)

    assert "close-closed-followup-detail" in ids
    assert "edit-followup-detail" not in ids
    assert "update-followup-detail" not in ids
    text = " ".join(_collect_text(body))
    assert dashboard.tr("es", "followups.report_updates") in text
    assert dashboard.tr("es", "followups.closed_at") in text
    assert "3" in text
    assert "07/11/2026 15:30" in text


def test_closed_followup_hides_update_and_close_actions():
    dashboard.app._setup_server()

    record = {
        "estudiante_id": "T00011387",
        "periodo": "202601",
        "responsable": "Camila",
        "nota": "Nota",
        "proxima_accion": "Citar",
        "fecha_proxima_accion": "2026-11-20",
        "estado": "Cerrada",
        "report_updates": 1,
        "created_at": "2026-11-01T10:00:00",
        "closed_at": "2026-11-07T15:30:00",
    }
    ids = _collect_ids(dashboard.followups_table([record], "es", False))

    assert {"type": "followup-edit", "index": 0} in ids
    assert {"type": "followup-delete", "index": 0} in ids
    assert {"type": "followup-update", "index": 0} not in ids
    assert {"type": "followup-close", "index": 0} not in ids
