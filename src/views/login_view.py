"""
Vista de Autenticación de Usuarios.
Diseñada con la identidad visual institucional de la Universidad Tecnológica de Bolívar.
"""

from dash import html
import dash_bootstrap_components as dbc


def crear_vista_login():
    return dbc.Container(
        [
            dbc.Row(
                [
                    dbc.Col(
                        [
                            html.Div(
                                [
                                    # Logo oficial UTB y Título
                                    html.Div(
                                        [
                                            html.Img(
                                                src="/assets/logo_utb.png",
                                                className="login-header-logo mb-3",
                                                style={"maxHeight": "80px", "maxWidth": "220px"},
                                                alt="Universidad Tecnológica de Bolívar"
                                            ),
                                            html.H3(
                                                [
                                                    html.Span("UTB", style={"color": "#E30613", "fontWeight": "800"}),
                                                    html.Span("Alert", style={"color": "#002B49", "fontWeight": "800"}),
                                                ],
                                                className="mb-1"
                                            ),
                                            html.P("Sistema Analítico de Alertas Tempranas", className="text-secondary small fw-medium mb-3"),
                                        ],
                                        className="text-center"
                                    ),

                                    # Tarjeta de Formulario Estilo Académico
                                    html.Div(
                                        [
                                            html.H5("Acceso Institucional", className="fw-bold mb-2 text-center", style={"color": "#002B49"}),
                                            html.P("Ingreso exclusivo para el personal de Bienestar Universitario y Administradores.", className="text-muted small mb-4 text-center"),

                                            dbc.Label("Correo Institucional", className="small text-secondary fw-semibold"),
                                            dbc.InputGroup(
                                                [
                                                    dbc.InputGroupText("✉️", className="bg-light border-end-0 text-muted"),
                                                    dbc.Input(
                                                        id="login-email",
                                                        type="email",
                                                        placeholder="usuario@utb.edu.co",
                                                        className="border-start-0"
                                                    ),
                                                ],
                                                className="mb-3"
                                            ),

                                            dbc.Label("Contraseña", className="small text-secondary fw-semibold"),
                                            dbc.InputGroup(
                                                [
                                                    dbc.InputGroupText("🔒", className="bg-light border-end-0 text-muted"),
                                                    dbc.Input(
                                                        id="login-password",
                                                        type="password",
                                                        placeholder="••••••••••••",
                                                        className="border-start-0"
                                                    ),
                                                ],
                                                className="mb-3"
                                            ),

                                            dbc.Button(
                                                "Iniciar Sesión",
                                                id="btn-login-submit",
                                                className="w-100 fw-bold py-2 mt-2 shadow-sm text-white",
                                                style={"backgroundColor": "#002B49", "borderColor": "#002B49"}
                                            ),

                                            html.Div(id="login-error-feedback", className="mt-3 text-center"),
                                        ],
                                        className="login-card p-4 p-md-5"
                                    ),

                                    html.Div(
                                        "Universidad Tecnológica de Bolívar • Dirección de Bienestar Universitario",
                                        className="text-center text-muted small mt-4"
                                    ),

                                    # Elemento oculto para satisfacer los inputs de callback globales cuando está en login
                                    html.Div(
                                        dbc.Button(id="btn-logout", style={"display": "none"}),
                                        style={"display": "none"}
                                    )
                                ],
                                className="mx-auto",
                                style={"maxWidth": "440px"}
                            )
                        ],
                        width=12
                    )
                ],
                className="min-vh-100 d-flex align-items-center justify-content-center py-5"
            )
        ],
        fluid=True
    )
