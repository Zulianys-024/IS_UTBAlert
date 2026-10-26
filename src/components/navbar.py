"""
Componentes de Cabecera (Navbar) y Banner de Alerta Crítica.
Diseñado con los colores institucionales y logo oficial de la UTB.
"""

from dash import html
import dash_bootstrap_components as dbc


def crear_navbar(usuario: dict):
    nombre_user = usuario.get("nombre", "Personal de Bienestar") if usuario else "Personal de Bienestar"
    rol_user = usuario.get("rol", "Bienestar Universitario") if usuario else "Bienestar Universitario"

    return dbc.Navbar(
        dbc.Container(
            [
                # Brand con logo oficial UTB
                html.A(
                    dbc.Row(
                        [
                            dbc.Col(
                                html.Img(
                                    src="/assets/logo_utb.png",
                                    height="45px",
                                    className="me-2 nav-logo-img",
                                    alt="Logo UTB"
                                ),
                                width="auto"
                            ),
                            dbc.Col(
                                [
                                    html.Div(
                                        [
                                            html.Span("UTB", className="fw-bolder fs-4", style={"color": "#E30613"}),
                                            html.Span("Alert", className="fw-bolder fs-4 text-white"),
                                        ]
                                    ),
                                    html.Small("Sistema de Alertas Tempranas - Vicerrectoría de Bienestar", className="text-light opacity-75 d-none d-md-block", style={"fontSize": "0.72rem"}),
                                ],
                                width="auto"
                            ),
                        ],
                        align="center",
                        className="g-2",
                    ),
                    href="#",
                    style={"textDecoration": "none"},
                ),

                # Right User Info & Actions
                html.Div(
                    [
                        html.Div(
                            [
                                html.Span(nombre_user, className="fw-bold d-block text-white text-end", style={"fontSize": "0.85rem"}),
                                html.Span(rol_user, className="badge text-uppercase", style={"fontSize": "0.68rem", "backgroundColor": "#E30613"}),
                            ],
                            className="me-3 d-none d-sm-block text-end"
                        ),
                        dbc.Button(
                            [html.I(className="bi bi-box-arrow-right me-1"), "Cerrar Sesión"],
                            id="btn-logout",
                            color="light",
                            size="sm",
                            outline=True,
                            className="text-white border-white-50"
                        )
                    ],
                    className="d-flex align-items-center"
                )
            ],
            fluid=True,
            className="px-4"
        ),
        color="#002B49",  # Azul marino oficial UTB
        dark=True,
        className="py-2 mb-4 sticky-top shadow-sm border-bottom border-light border-opacity-10"
    )


def crear_banner_alerta_critica(total_alto: int, total_estudiantes: int):
    """Banner visual para alertas de riesgo alto prioritarias."""
    porcentaje_alto = round((total_alto / total_estudiantes * 100), 1) if total_estudiantes > 0 else 0

    return html.Div(
        [
            dbc.Row(
                [
                    dbc.Col(
                        [
                            html.Div(
                                [
                                    html.Span("⚠️", style={"fontSize": "2.2rem"}, className="me-3"),
                                    html.Div(
                                        [
                                            html.H5("ALERTA PRIORITARIA: Casos Críticos en Prueba Académica o Inasistencia", className="text-danger fw-bolder mb-1"),
                                            html.P(
                                                f"Se detectaron {total_alto:,} estudiantes ({porcentaje_alto}%) clasificados en RIESGO ALTO. "
                                                "Su PPA acumulado se encuentra igual o por debajo del umbral de prueba (≤ 3.20) o su porcentaje de asistencia es inferior al 70%. "
                                                "Requieren intervención inmediata del área de Bienestar Universitario.",
                                                className="mb-0 text-dark small"
                                            ),
                                        ]
                                    ),
                                ],
                                className="d-flex align-items-center"
                            )
                        ],
                        md=9
                    ),
                    dbc.Col(
                        [
                            dbc.Button(
                                [html.I(className="bi bi-funnel-fill me-1"), "Ver Solo Riesgo Alto"],
                                id="btn-filtrar-solo-altos",
                                color="danger",
                                className="fw-bold w-100 shadow-sm"
                            )
                        ],
                        md=3,
                        className="d-flex align-items-center justify-content-md-end mt-2 mt-md-0"
                    )
                ],
                align="center"
            )
        ],
        className="critical-alert-banner mb-4"
    )
