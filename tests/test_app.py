import base64
import io

import pandas as pd
import pytest

import app as dashboard


def test_all_dashboard_pages_render():
    dashboard.app._setup_server()

    prefs = {"lang": "es", "theme": "light"}
    for path in ("/", "/estudiantes", "/variables", "/alertas", "/seguimientos", "/reportes", "/perfil", "/perfil/editar"):
        page = dashboard.render(path, {"user": "Camila"}, {}, prefs, {})
        assert page is not None


def test_pages_render_in_english_and_dark_theme():
    dashboard.app._setup_server()

    prefs = {"lang": "en", "theme": "dark"}
    for path in ("/", "/estudiantes", "/perfil", "/perfil/editar"):
        page = dashboard.render(path, {"user": "Camila"}, {}, prefs, {"name": "Camila"})
        assert page is not None


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
