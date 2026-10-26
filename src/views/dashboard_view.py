"""
Vista Principal del Dashboard Analítico de Alertas Tempranas (RF-04, RF-05, RF-06, RF-08).
"""

from dash import html, dcc, dash_table
import dash_bootstrap_components as dbc
import pandas as pd

from src.components.navbar import crear_navbar, crear_banner_alerta_critica
from src.components.modal_seguimiento import crear_modal_seguimiento
from src.components.charts import (
    crear_grafico_distribucion_riesgo,
    crear_grafico_riesgo_por_carrera,
    crear_grafico_ppa_vs_asistencia
)
from src.services.data_service import DataService
from src.services.storage_seguimiento import StorageSeguimiento


def crear_vista_dashboard(usuario: dict):
    # Cargar datos procesados
    df = DataService.cargar_datos_crudos()
    total_estudiantes = len(df)
    total_alto = (df["nivel_riesgo"] == "Alto").sum()
    total_medio = (df["nivel_riesgo"] == "Medio").sum()
    total_bajo = (df["nivel_riesgo"] == "Bajo").sum()
    total_seguimientos = StorageSeguimiento.contar_seguimientos_totales()

    lista_programas = DataService.obtener_lista_programas()
    opciones_programas = [{"label": "Todos los Programas", "value": "ALL"}] + [
        {"label": prog, "value": prog} for prog in lista_programas
    ]

    # Preparar datos iniciales para la tabla ordenada por riesgo
    notas_todas = StorageSeguimiento.obtener_todas_las_notas()
    df_init = df.copy()
    df_init["tiene_seguimiento"] = df_init["student_id"].apply(
        lambda sid: f"📝 {len(notas_todas[sid])} notas" if sid in notas_todas and len(notas_todas[sid]) > 0 else "Sin notas"
    )
    orden_riesgo = {"Alto": 0, "Medio": 1, "Bajo": 2}
    df_init["peso_riesgo"] = df_init["nivel_riesgo"].map(orden_riesgo)
    df_init = df_init.sort_values(by=["peso_riesgo", "ppa"], ascending=[True, True])
    cols_tabla = [
        "student_id", "programa_nombre", "ppa", "attendance_percentage",
        "nivel_riesgo", "motivo_riesgo", "tiene_seguimiento"
    ]
    data_inicial = df_init[cols_tabla].to_dict("records")

    return html.Div(
        [
            # Barra de Navegación
            crear_navbar(usuario),

            # Contenedor Principal
            dbc.Container(
                [
                    # Alerta Roja Prominente de Casos Críticos (RF-05)
                    crear_banner_alerta_critica(total_alto, total_estudiantes),

                    # Fila de Tarjetas de Resumen (KPIs)
                    dbc.Row(
                        [
                            dbc.Col(
                                html.Div(
                                    [
                                        html.Span("Estudiantes Monitoreados", className="kpi-title"),
                                        html.Div(f"{total_estudiantes:,}", className="kpi-number", style={"color": "#002B49"}),
                                        html.Small("Base estructurada UTB", className="text-muted"),
                                    ],
                                    className="kpi-card kpi-total shadow-sm"
                                ),
                                xs=12, sm=6, lg=3,
                                className="mb-3"
                            ),
                            dbc.Col(
                                html.Div(
                                    [
                                        html.Span("🔴 Riesgo Alto (Prueba)", className="kpi-title text-danger"),
                                        html.Div(f"{total_alto:,}", className="kpi-number text-danger"),
                                        html.Small(f"{round((total_alto/total_estudiantes)*100, 1)}% del estudiantado (PPA ≤ 3.20)", className="text-danger opacity-75"),
                                    ],
                                    className="kpi-card kpi-high shadow-sm"
                                ),
                                xs=12, sm=6, lg=3,
                                className="mb-3"
                            ),
                            dbc.Col(
                                html.Div(
                                    [
                                        html.Span("🟡 Riesgo Medio", className="kpi-title text-warning"),
                                        html.Div(f"{total_medio:,}", className="kpi-number text-warning"),
                                        html.Small(f"{round((total_medio/total_estudiantes)*100, 1)}% en seguimiento preventivo", className="text-warning opacity-75"),
                                    ],
                                    className="kpi-card kpi-med shadow-sm"
                                ),
                                xs=12, sm=6, lg=3,
                                className="mb-3"
                            ),
                            dbc.Col(
                                html.Div(
                                    [
                                        html.Span("📝 Intervenciones de Bienestar", className="kpi-title text-info"),
                                        html.Div(id="kpi-total-intervenciones", children=f"{total_seguimientos:,}", className="kpi-number text-info"),
                                        html.Small("Bitácoras registradas en JSON", className="text-info opacity-75"),
                                    ],
                                    className="kpi-card shadow-sm",
                                    style={"borderLeft": "5px solid #06B6D4"}
                                ),
                                xs=12, sm=6, lg=3,
                                className="mb-3"
                            ),
                        ],
                        className="mb-3"
                    ),

                    # Barra de Filtros Dinámicos (RF-06)
                    html.Div(
                        [
                            dbc.Row(
                                [
                                    dbc.Col(
                                        [
                                            html.Label("Filtro por Programa Académico UTB", className="small text-muted fw-bold mb-1"),
                                            dcc.Dropdown(
                                                id="filtro-carrera",
                                                options=opciones_programas,
                                                value="ALL",
                                                clearable=False,
                                                className="dash-dropdown text-dark"
                                            )
                                        ],
                                        md=4,
                                        className="mb-2 mb-md-0"
                                    ),
                                    dbc.Col(
                                        [
                                            html.Label("Filtro por Nivel de Riesgo", className="small text-muted fw-bold mb-1"),
                                            dcc.Dropdown(
                                                id="filtro-riesgo",
                                                options=[
                                                    {"label": "Todos los Niveles", "value": "ALL"},
                                                    {"label": "🔴 Riesgo Alto (PPA ≤ 3.20 / Asist < 70%)", "value": "Alto"},
                                                    {"label": "🟡 Riesgo Medio (Preventivo)", "value": "Medio"},
                                                    {"label": "🟢 Riesgo Bajo (Satisfactorio)", "value": "Bajo"},
                                                ],
                                                value="ALL",
                                                clearable=False,
                                                className="dash-dropdown text-dark"
                                            )
                                        ],
                                        md=4,
                                        className="mb-2 mb-md-0"
                                    ),
                                    dbc.Col(
                                        [
                                            html.Label("Buscar por Código de Estudiante", className="small text-muted fw-bold mb-1"),
                                            dbc.Input(
                                                id="filtro-busqueda-id",
                                                placeholder="Ej: T00011111...",
                                                type="text",
                                                className="bg-white border-secondary-subtle"
                                            )
                                        ],
                                        md=2,
                                        className="mb-2 mb-md-0"
                                    ),
                                    dbc.Col(
                                        [
                                            html.Label("Exportar Reporte", className="small text-muted fw-bold mb-1 d-block"),
                                            dbc.Button(
                                                [html.I(className="bi bi-file-earmark-spreadsheet me-1"), "Exportar CSV"],
                                                id="btn-exportar-csv",
                                                className="w-100 fw-bold shadow-sm text-white",
                                                style={"backgroundColor": "#002B49", "borderColor": "#002B49"}
                                            ),
                                            dcc.Download(id="download-dataframe-csv")
                                        ],
                                        md=2
                                    )
                                ],
                                align="end"
                            )
                        ],
                        className="glass-card p-3 mb-4"
                    ),

                    # Fila de Gráficos Analíticos
                    dbc.Row(
                        [
                            dbc.Col(
                                html.Div(
                                    [dcc.Graph(id="grafico-distribucion", figure=crear_grafico_distribucion_riesgo(df))],
                                    className="glass-card p-3 h-100"
                                ),
                                lg=4,
                                className="mb-4"
                            ),
                            dbc.Col(
                                html.Div(
                                    [dcc.Graph(id="grafico-carreras", figure=crear_grafico_riesgo_por_carrera(df))],
                                    className="glass-card p-3 h-100"
                                ),
                                lg=8,
                                className="mb-4"
                            ),
                        ]
                    ),

                    # Gráfico de Dispersión PPA vs Asistencia
                    dbc.Row(
                        [
                            dbc.Col(
                                html.Div(
                                    [dcc.Graph(id="grafico-dispersion", figure=crear_grafico_ppa_vs_asistencia(df))],
                                    className="glass-card p-3"
                                ),
                                width=12,
                                className="mb-4"
                            )
                        ]
                    ),

                    # Tabla de Casos y Alertas
                    html.Div(
                        [
                            html.Div(
                                [
                                    html.Div(
                                        [
                                            html.H5("📋 Directorio de Seguimiento Estudiantil", className="fw-bold mb-0", style={"color": "#002B49"}),
                                            html.Small("Haz clic en cualquier fila para abrir la ficha del alumno y registrar notas de acompañamiento", className="text-secondary"),
                                        ]
                                    ),
                                    html.Span(
                                        id="tabla-contador-registros",
                                        children=f"Mostrando {len(df):,} de {total_estudiantes:,} casos",
                                        className="badge text-white fs-6",
                                        style={"backgroundColor": "#002B49"}
                                    )
                                ],
                                className="d-flex justify-content-between align-items-center mb-3 flex-wrap"
                            ),

                            # Tabla Interactiva Dash
                            dash_table.DataTable(
                                id="tabla-estudiantes",
                                data=data_inicial,
                                columns=[
                                    {"name": "ID Estudiante", "id": "student_id"},
                                    {"name": "Programa Académico (UTB)", "id": "programa_nombre"},
                                    {"name": "PPA (0.0 - 5.0)", "id": "ppa", "type": "numeric", "format": {"specifier": ".2f"}},
                                    {"name": "Asistencia (%)", "id": "attendance_percentage", "type": "numeric", "format": {"specifier": ".1f"}},
                                    {"name": "Nivel de Riesgo", "id": "nivel_riesgo"},
                                    {"name": "Diagnóstico / Motivo", "id": "motivo_riesgo"},
                                    {"name": "Notas Bienestar", "id": "tiene_seguimiento"}
                                ],
                                page_size=12,
                                page_current=0,
                                page_action="native",
                                sort_action="native",
                                row_selectable=False,
                                cell_selectable=True,
                                style_as_list_view=True,
                                style_cell={
                                    "textAlign": "left",
                                    "padding": "12px",
                                    "fontFamily": "Plus Jakarta Sans, sans-serif"
                                },
                                style_data_conditional=[
                                    # Resaltado en Rojo para Riesgo Alto (RF-05)
                                    {
                                        "if": {"filter_query": "{nivel_riesgo} = 'Alto'"},
                                        "backgroundColor": "rgba(239, 68, 68, 0.12)",
                                        "color": "#FCA5A5",
                                        "fontWeight": "600"
                                    },
                                    {
                                        "if": {"filter_query": "{nivel_riesgo} = 'Medio'"},
                                        "backgroundColor": "rgba(245, 158, 11, 0.08)",
                                        "color": "#FCD34D"
                                    },
                                    {
                                        "if": {"filter_query": "{nivel_riesgo} = 'Bajo'"},
                                        "backgroundColor": "rgba(16, 185, 129, 0.06)",
                                        "color": "#6EE7B7"
                                    },
                                    # PPA menor o igual a 3.20 en negrita roja
                                    {
                                        "if": {
                                            "column_id": "ppa",
                                            "filter_query": "{ppa} <= 3.20"
                                        },
                                        "color": "#EF4444",
                                        "fontWeight": "bold"
                                    }
                                ]
                            )
                        ],
                        className="glass-card p-4 mb-5"
                    ),

                    # Modal de Acompañamiento Psicológico
                    crear_modal_seguimiento(),

                    # Elementos dummy ocultos para consistencia de IDs en callbacks globales
                    html.Div(
                        [
                            dbc.Button(id="btn-login-submit", style={"display": "none"}),
                            dbc.Input(id="login-email", style={"display": "none"}),
                            dbc.Input(id="login-password", style={"display": "none"}),
                            html.Div(id="login-error-feedback", style={"display": "none"}),
                        ],
                        style={"display": "none"}
                    )
                ],
                fluid=True,
                className="px-4"
            )
        ]
    )
