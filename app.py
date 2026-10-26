"""
Aplicación Principal de Dash para UTBAlert.
Integra autenticación, enrutamiento en sesión, callbacks reactivos y gestión de estado.
"""

import os
import dash
from dash import html, dcc, Input, Output, State, callback_context
import dash_bootstrap_components as dbc
import pandas as pd

from src.services.auth_service import AuthService
from src.services.data_service import DataService
from src.services.storage_seguimiento import StorageSeguimiento
from src.views.login_view import crear_vista_login
from src.views.dashboard_view import crear_vista_dashboard
from src.components.charts import (
    crear_grafico_distribucion_riesgo,
    crear_grafico_riesgo_por_carrera,
    crear_grafico_ppa_vs_asistencia
)

# Inicializar aplicación Dash con estilos modernos
app = dash.Dash(
    __name__,
    title="UTBAlert - Alertas Tempranas UTB",
    external_stylesheets=[
        dbc.themes.FLATLY,
        "https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/bootstrap-icons.min.css"
    ],
    suppress_callback_exceptions=True
)

server = app.server

# Layout Raíz con almacenes de sesión
app.layout = html.Div(
    [
        dcc.Location(id="url", refresh=False),
        # Sesión del usuario autenticado
        dcc.Store(id="session-user-store", storage_type="session"),
        # Contenedor dinámico de vistas
        html.Div(id="page-content")
    ]
)


# ==========================================
# CALLBACK: Renderizado de Vistas (Login vs Dashboard)
# ==========================================
@app.callback(
    Output("page-content", "children"),
    Input("session-user-store", "data")
)
def renderizar_vista(usuario_data):
    if not usuario_data:
        return crear_vista_login()
    return crear_vista_dashboard(usuario_data)


# ==========================================
# CALLBACK: Autenticación / Logout (RF-01)
# ==========================================
@app.callback(
    [
        Output("session-user-store", "data"),
        Output("login-error-feedback", "children")
    ],
    [
        Input("btn-login-submit", "n_clicks"),
        Input("btn-logout", "n_clicks")
    ],
    [
        State("login-email", "value"),
        State("login-password", "value"),
        State("session-user-store", "data")
    ],
    prevent_initial_call=True
)
def manejar_autenticacion(n_login, n_logout, email, password, sesion_actual):
    ctx = callback_context
    if not ctx.triggered:
        return dash.no_update, dash.no_update

    trigger_id = ctx.triggered[0]["prop_id"].split(".")[0]

    # Cerrar Sesión
    if trigger_id == "btn-logout":
        if n_logout:
            return None, ""
        return dash.no_update, dash.no_update

    # Iniciar Sesión
    if trigger_id == "btn-login-submit":
        if not n_login:
            return dash.no_update, dash.no_update

        if not email or not password:
            return dash.no_update, dbc.Alert(
                "Por favor ingresa tu correo y contraseña institucional.",
                color="warning",
                className="py-2 small"
            )

        user = AuthService.validar_credenciales(email, password)
        if user:
            return user, ""
        else:
            return dash.no_update, dbc.Alert(
                "Credenciales incorrectas. Verifica tu correo o contraseña institucional.",
                color="danger",
                className="py-2 small"
            )

    return dash.no_update, dash.no_update


# ==========================================
# CALLBACK: Botón de Acceso Rápido "Ver Solo Riesgo Alto"
# ==========================================
@app.callback(
    Output("filtro-riesgo", "value"),
    Input("btn-filtrar-solo-altos", "n_clicks"),
    prevent_initial_call=True
)
def set_filtro_solo_altos(n_clicks):
    if n_clicks:
        return "Alto"
    return dash.no_update


# ==========================================
# CALLBACK: Filtrado Dinámico de Datos, Tabla y Gráficos (RF-04, RF-06)
# ==========================================
@app.callback(
    [
        Output("tabla-estudiantes", "data"),
        Output("tabla-contador-registros", "children"),
        Output("grafico-distribucion", "figure"),
        Output("grafico-carreras", "figure"),
        Output("grafico-dispersion", "figure")
    ],
    [
        Input("filtro-carrera", "value"),
        Input("filtro-riesgo", "value"),
        Input("filtro-busqueda-id", "value")
    ],
    prevent_initial_call=True
)
def actualizar_dashboard(carrera, riesgo, busqueda_id):
    df = DataService.cargar_datos_crudos()
    total_original = len(df)

    # Filtrar por Carrera
    if carrera and carrera != "ALL":
        df = df[df["programa_nombre"] == carrera]

    # Filtrar por Nivel de Riesgo
    if riesgo and riesgo != "ALL":
        df = df[df["nivel_riesgo"] == riesgo]

    # Filtrar por Búsqueda de ID
    if busqueda_id:
        df = df[df["student_id"].str.contains(busqueda_id.strip(), case=False, na=False)]

    # Marcar si tiene notas de seguimiento
    notas_todas = StorageSeguimiento.obtener_todas_las_notas()
    df["tiene_seguimiento"] = df["student_id"].apply(
        lambda sid: f"📝 {len(notas_todas[sid])} notas" if sid in notas_todas and len(notas_todas[sid]) > 0 else "Sin notas"
    )

    # Ordenar priorizando Riesgo Alto y menor PPA
    orden_riesgo = {"Alto": 0, "Medio": 1, "Bajo": 2}
    df["peso_riesgo"] = df["nivel_riesgo"].map(orden_riesgo)
    df = df.sort_values(by=["peso_riesgo", "ppa"], ascending=[True, True])

    # Convertir a formato tabla
    cols_tabla = [
        "student_id",
        "programa_nombre",
        "ppa",
        "attendance_percentage",
        "nivel_riesgo",
        "motivo_riesgo",
        "tiene_seguimiento"
    ]
    data_tabla = df[cols_tabla].to_dict("records")
    contador_texto = f"Mostrando {len(df):,} de {total_original:,} casos"

    # Generar gráficos actualizados dinámicamente con los filtros aplicados
    fig_dist = crear_grafico_distribucion_riesgo(df)
    fig_carreras = crear_grafico_riesgo_por_carrera(df)
    fig_disp = crear_grafico_ppa_vs_asistencia(df)

    return data_tabla, contador_texto, fig_dist, fig_carreras, fig_disp


# ==========================================
# CALLBACK: Exportación a CSV (RF-08)
# ==========================================
@app.callback(
    Output("download-dataframe-csv", "data"),
    Input("btn-exportar-csv", "n_clicks"),
    [
        State("filtro-carrera", "value"),
        State("filtro-riesgo", "value"),
        State("filtro-busqueda-id", "value")
    ],
    prevent_initial_call=True
)
def exportar_csv(n_clicks, carrera, riesgo, busqueda_id):
    if not n_clicks:
        return dash.no_update

    df = DataService.cargar_datos_crudos()
    if carrera and carrera != "ALL":
        df = df[df["programa_nombre"] == carrera]
    if riesgo and riesgo != "ALL":
        df = df[df["nivel_riesgo"] == riesgo]
    if busqueda_id:
        df = df[df["student_id"].str.contains(busqueda_id.strip(), case=False, na=False)]

    cols_export = [
        "student_id", "programa_nombre", "ppa", "attendance_percentage",
        "nivel_riesgo", "motivo_riesgo", "target"
    ]
    df_export = df[cols_export].rename(columns={
        "student_id": "ID_Estudiante",
        "programa_nombre": "Programa_UTB",
        "ppa": "PPA_Escala_5",
        "attendance_percentage": "Asistencia_Pct",
        "nivel_riesgo": "Nivel_Riesgo",
        "motivo_riesgo": "Diagnostico",
        "target": "Estado_Original"
    })

    return dcc.send_data_frame(df_export.to_csv, "reporte_alertas_utb.csv", index=False)


# ==========================================
# CALLBACK: Apertura de Modal de Seguimiento Psicológico (RF-07)
# ==========================================
@app.callback(
    [
        Output("modal-seguimiento", "is_open"),
        Output("modal-student-id-store", "data"),
        Output("modal-student-info-header", "children"),
        Output("modal-historial-notas", "children"),
        Output("feedback-guardar-nota", "children")
    ],
    [
        Input("tabla-estudiantes", "active_cell"),
        Input("btn-cerrar-modal", "n_clicks"),
        Input("btn-guardar-nota", "n_clicks")
    ],
    [
        State("tabla-estudiantes", "data"),
        State("modal-student-id-store", "data"),
        State("input-nota-profesional", "value"),
        State("input-nota-motivo", "value"),
        State("input-nota-observaciones", "value"),
        State("input-nota-compromisos", "value")
    ],
    prevent_initial_call=True
)
def gestionar_modal_seguimiento(
    active_cell,
    n_cerrar,
    n_guardar,
    data_tabla,
    student_id_actual,
    profesional,
    motivo,
    observaciones,
    compromisos
):
    ctx = callback_context
    if not ctx.triggered:
        return dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update

    trigger = ctx.triggered[0]["prop_id"].split(".")[0]

    # Cerrar modal
    if trigger == "btn-cerrar-modal":
        return False, None, html.Div(), html.Div(), ""

    # Guardar nueva nota (RF-07)
    if trigger == "btn-guardar-nota":
        if not student_id_actual:
            return dash.no_update, dash.no_update, dash.no_update, dash.no_update, dbc.Alert("Error: No hay estudiante activo.", color="danger")
        if not observaciones or not observaciones.strip():
            return dash.no_update, dash.no_update, dash.no_update, dash.no_update, dbc.Alert("Por favor escribe una observación antes de guardar.", color="warning")

        StorageSeguimiento.guardar_nota(
            student_id=student_id_actual,
            profesional=profesional,
            motivo=motivo,
            observaciones=observaciones.strip(),
            compromisos=compromisos.strip() if compromisos else ""
        )

        historial_actualizado = _renderizar_historial_notas(student_id_actual)
        feedback = dbc.Alert("✅ Nota de intervención guardada con éxito en JSON local.", color="success", duration=3000)
        return True, student_id_actual, dash.no_update, historial_actualizado, feedback

    # Abrir modal desde clic en la tabla
    if trigger == "tabla-estudiantes" and active_cell:
        row_index = active_cell["row"]
        if row_index < len(data_tabla):
            estudiante = data_tabla[row_index]
            sid = estudiante["student_id"]

            info_header = dbc.Card(
                dbc.CardBody(
                    [
                        dbc.Row(
                            [
                                dbc.Col(
                                    [
                                        html.H5(f"Estudiante: {sid}", className="fw-bold mb-1", style={"color": "#002B49"}),
                                        html.P(f"Carrera: {estudiante['programa_nombre']}", className="text-secondary small mb-0"),
                                    ],
                                    md=6
                                ),
                                dbc.Col(
                                    [
                                        html.Div(
                                            [
                                                html.Span(f"PPA: {estudiante['ppa']:.2f}", className="badge bg-danger me-2 fs-6" if estudiante['ppa'] <= 3.20 else "badge bg-warning me-2 fs-6"),
                                                html.Span(f"Asistencia: {estudiante['attendance_percentage']:.1f}%", className="badge bg-secondary me-2 fs-6"),
                                                html.Span(f"Riesgo {estudiante['nivel_riesgo']}", className="badge bg-danger text-white fs-6" if estudiante['nivel_riesgo'] == 'Alto' else "badge bg-warning text-dark fs-6"),
                                            ]
                                        ),
                                        html.Small(f"Motivo: {estudiante['motivo_riesgo']}", className="text-danger fw-semibold d-block mt-1")
                                    ],
                                    md=6,
                                    className="text-md-end mt-2 mt-md-0"
                                )
                            ]
                        )
                    ]
                ),
                className="bg-light border-secondary-subtle mb-3"
            )

            historial_notas = _renderizar_historial_notas(sid)
            return True, sid, info_header, historial_notas, ""

    return dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update


def _renderizar_historial_notas(student_id: str):
    notas = StorageSeguimiento.obtener_notas_estudiante(student_id)
    if not notas:
        return html.P("No hay registros previos de seguimiento para este alumno.", className="text-muted small fst-italic p-2")

    items = []
    for nota in notas:
        items.append(
            dbc.Card(
                dbc.CardBody(
                    [
                        html.Div(
                            [
                                html.Span(f"📌 {nota.get('motivo', 'Intervención')}", className="fw-bold small", style={"color": "#002B49"}),
                                html.Small(f"{nota.get('fecha', '')} | {nota.get('profesional', '')}", className="text-muted"),
                            ],
                            className="d-flex justify-content-between mb-1"
                        ),
                        html.P(nota.get("observaciones", ""), className="text-dark small mb-2"),
                        html.Div(
                            [
                                html.Span("🤝 Compromisos: ", className="fw-bold small", style={"color": "#0B4F80"}),
                                html.Span(nota.get("compromisos", "Ninguno"), className="small text-muted")
                            ]
                        ) if nota.get("compromisos") else html.Div()
                    ],
                    className="p-2"
                ),
                className="bg-light border-secondary-subtle mb-2"
            )
        )
    return html.Div(items)


if __name__ == "__main__":
    puerto = int(os.environ.get("PORT", 8050))
    print(f"🚀 UTBAlert Dashboard ejecutándose en http://127.0.0.1:{puerto}")
    app.run(debug=True, port=puerto)
