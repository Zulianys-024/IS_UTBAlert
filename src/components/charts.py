"""
Generador de Gráficos Analíticos Interactivos (Plotly) para UTBAlert.
Adaptado a la paleta institucional académica de la UTB (Fondo limpio, detalles en azul marino y rojo).
"""

import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

# Paleta de Riesgo Académica
COLOR_DISC = {
    "Alto": "#DC2626",    # Rojo institucional / Alerta crítica
    "Medio": "#D97706",   # Ámbar / Alerta preventiva
    "Bajo": "#059669"     # Verde / Desempeño satisfactorio
}

# Configuración de diseño limpia para el tema académico
THEME_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Plus Jakarta Sans, sans-serif", color="#1E293B"),
    margin=dict(l=25, r=25, t=65, b=25)
)


def crear_grafico_distribucion_riesgo(df: pd.DataFrame) -> go.Figure:
    """Gráfico tipo Donut de proporción de estudiantes por nivel de riesgo."""
    if df.empty:
        fig = go.Figure()
        fig.update_layout(**THEME_LAYOUT, title="Sin datos")
        return fig

    conteo = df["nivel_riesgo"].value_counts().reset_index()
    conteo.columns = ["Nivel", "Cantidad"]

    fig = px.pie(
        conteo,
        names="Nivel",
        values="Cantidad",
        color="Nivel",
        color_discrete_map=COLOR_DISC,
        hole=0.62
    )

    fig.update_traces(
        textinfo="percent+value",
        hovertemplate="<b>%{label}</b><br>Estudiantes: %{value:,}<br>Proporción: %{percent}<extra></extra>",
        marker=dict(line=dict(color="#FFFFFF", width=2))
    )

    # Título separado hacia arriba y leyenda posicionada abajo para evitar cualquier solapamiento
    fig.update_layout(
        **THEME_LAYOUT,
        title=dict(
            text="<b>Distribución Global por Nivel de Riesgo</b>",
            font=dict(size=14, color="#002B49"),
            x=0.02,
            y=0.98,
            xanchor="left",
            yanchor="top"
        ),
        legend=dict(
            orientation="h",
            yanchor="top",
            y=-0.05,        # Leyenda en la parte inferior para total claridad visual
            xanchor="center",
            x=0.5
        ),
        showlegend=True,
        annotations=[
            dict(
                text="Total<br><b>{:,}</b>".format(len(df)),
                x=0.5,
                y=0.5,
                font_size=17,
                showarrow=False,
                font_color="#002B49"
            )
        ]
    )
    return fig


def crear_grafico_riesgo_por_carrera(df: pd.DataFrame) -> go.Figure:
    """Gráfico de barras apiladas con el conteo de riesgo en cada carrera UTB."""
    if df.empty:
        fig = go.Figure()
        fig.update_layout(**THEME_LAYOUT, title="Sin datos")
        return fig

    agrupado = df.groupby(["programa_nombre", "nivel_riesgo"]).size().reset_index(name="Total")

    altos_por_carrera = df[df["nivel_riesgo"] == "Alto"]["programa_nombre"].value_counts()
    orden_carreras = altos_por_carrera.index.tolist()

    fig = px.bar(
        agrupado,
        x="programa_nombre",
        y="Total",
        color="nivel_riesgo",
        color_discrete_map=COLOR_DISC,
        category_orders={"programa_nombre": orden_carreras, "nivel_riesgo": ["Alto", "Medio", "Bajo"]},
        labels={"programa_nombre": "Carrera UTB", "Total": "N° de Estudiantes", "nivel_riesgo": "Riesgo"}
    )

    fig.update_layout(
        **THEME_LAYOUT,
        title=dict(
            text="<b>Casos de Riesgo por Programa Académico UTB</b>",
            font=dict(size=14, color="#002B49"),
            x=0.02,
            y=0.98,
            xanchor="left",
            yanchor="top"
        ),
        barmode="stack",
        xaxis=dict(tickangle=-35, showgrid=False, color="#475569"),
        yaxis=dict(showgrid=True, gridcolor="#E2E8F0", color="#475569")
    )
    return fig


def crear_grafico_ppa_vs_asistencia(df: pd.DataFrame) -> go.Figure:
    """Diagrama de dispersión PPA vs Asistencia con zonas de alerta."""
    if df.empty:
        fig = go.Figure()
        fig.update_layout(**THEME_LAYOUT, title="Sin datos")
        return fig

    df_sample = df.sample(min(len(df), 800), random_state=42)

    fig = px.scatter(
        df_sample,
        x="attendance_percentage",
        y="ppa",
        color="nivel_riesgo",
        color_discrete_map=COLOR_DISC,
        category_orders={"nivel_riesgo": ["Alto", "Medio", "Bajo"]},
        hover_data={"student_id": True, "programa_nombre": True, "ppa": ":.2f", "attendance_percentage": ":.1f%"},
        labels={"attendance_percentage": "Asistencia (%)", "ppa": "PPA (Escala UTB 0.0 - 5.0)", "nivel_riesgo": "Riesgo"}
    )

    fig.add_hline(
        y=3.20,
        line_dash="dot",
        line_color="#DC2626",
        annotation_text="Límite Prueba Académica (3.20)",
        annotation_position="bottom right",
        annotation_font_color="#DC2626"
    )

    fig.add_vline(
        x=70.0,
        line_dash="dot",
        line_color="#DC2626",
        annotation_text="Inasistencia Crítica (70%)",
        annotation_position="top left",
        annotation_font_color="#DC2626"
    )

    fig.update_layout(
        **THEME_LAYOUT,
        title=dict(
            text="<b>Relación PPA (0.0 - 5.0) vs. Asistencia (%)</b>",
            font=dict(size=14, color="#002B49"),
            x=0.02,
            y=0.98,
            xanchor="left",
            yanchor="top"
        ),
        xaxis=dict(showgrid=True, gridcolor="#E2E8F0", range=[0, 105], color="#475569"),
        yaxis=dict(showgrid=True, gridcolor="#E2E8F0", range=[0, 5.2], color="#475569")
    )
    return fig
