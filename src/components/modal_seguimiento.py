"""
Componente del Modal de Detalle Estudiantil y Registro de Notas de Seguimiento Psicológico (RF-07).
"""

from dash import html, dcc
import dash_bootstrap_components as dbc
from typing import Dict, Any, List


def crear_modal_seguimiento():
    return dbc.Modal(
        [
            dbc.ModalHeader(
                dbc.ModalTitle(
                    html.Div(
                        [
                            html.I(className="bi bi-person-lines-fill me-2", style={"color": "#E30613"}),
                            html.Span("Ficha de Acompañamiento y Seguimiento", className="fw-bold text-white"),
                        ],
                        className="d-flex align-items-center"
                    )
                ),
                close_button=True,
                style={"backgroundColor": "#002B49"}
            ),
            dbc.ModalBody(
                [
                    # Almacén de ID del estudiante abierto
                    dcc.Store(id="modal-student-id-store"),

                    # Encabezado con datos del estudiante
                    html.Div(id="modal-student-info-header", className="mb-3"),

                    # Formulario para agregar nueva nota
                    html.Div(
                        [
                            html.H6("📝 Registrar Nueva Intervención / Nota de Bienestar", className="fw-bold mb-2", style={"color": "#002B49"}),
                            dbc.Row(
                                [
                                    dbc.Col(
                                        [
                                            dbc.Label("Profesional a Cargo", className="small text-muted fw-semibold"),
                                            dbc.Input(id="input-nota-profesional", placeholder="Nombre del profesional", value="Personal de Bienestar UTB"),
                                        ],
                                        md=6,
                                        className="mb-2"
                                    ),
                                    dbc.Col(
                                        [
                                            dbc.Label("Motivo de Intervención", className="small text-muted fw-semibold"),
                                            dbc.Select(
                                                id="input-nota-motivo",
                                                options=[
                                                    {"label": "Prueba Académica (PPA ≤ 3.20)", "value": "Prueba Académica"},
                                                    {"label": "Inasistencia Crítica (< 70%)", "value": "Inasistencia Crítica"},
                                                    {"label": "Apoyo Psicológico / Emocional", "value": "Apoyo Psicológico"},
                                                    {"label": "Seguimiento de Tutorías", "value": "Seguimiento de Tutorías"},
                                                    {"label": "Otro factor de bienestar", "value": "Otro"},
                                                ],
                                                value="Prueba Académica"
                                            ),
                                        ],
                                        md=6,
                                        className="mb-2"
                                    ),
                                ]
                            ),
                            dbc.Label("Observaciones Clínicas / Académicas", className="small text-muted fw-semibold"),
                            dbc.Textarea(
                                id="input-nota-observaciones",
                                placeholder="Describe el estado del estudiante, causas reportadas y diagnóstico de bienestar...",
                                rows=3,
                                className="mb-2"
                            ),
                            dbc.Label("Compromisos y Plan de Acción", className="small text-muted fw-semibold"),
                            dbc.Input(
                                id="input-nota-compromisos",
                                placeholder="Ej: Remisión a tutorías de cálculo, cita con psicología en 15 días...",
                                className="mb-3"
                            ),
                            dbc.Button(
                                [html.I(className="bi bi-save me-1"), "Guardar Nota de Seguimiento"],
                                id="btn-guardar-nota",
                                className="w-100 fw-bold shadow-sm text-white",
                                style={"backgroundColor": "#002B49", "borderColor": "#002B49"}
                            ),
                            html.Div(id="feedback-guardar-nota", className="mt-2 text-center small")
                        ],
                        className="p-3 mb-3 rounded bg-light border border-secondary-subtle"
                    ),

                    # Historial previo de notas
                    html.H6("📜 Historial de Intervenciones Registradas", className="fw-bold mb-2", style={"color": "#002B49"}),
                    html.Div(id="modal-historial-notas", style={"maxHeight": "250px", "overflowY": "auto"})
                ]
            ),
            dbc.ModalFooter(
                dbc.Button("Cerrar", id="btn-cerrar-modal", color="secondary", outline=True, className="ms-auto")
            )
        ],
        id="modal-seguimiento",
        size="lg",
        is_open=False,
        backdrop="static",
        scrollable=True
    )
