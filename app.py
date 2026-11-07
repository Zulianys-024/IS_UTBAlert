from __future__ import annotations

import calendar
import io
import json
import time
from datetime import date, datetime
from urllib.parse import quote

import dash
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dash import Dash, Input, Output, State, callback, dash_table, dcc, html, no_update
from dash.exceptions import PreventUpdate

from utbapp.data_access import (
    create_followup_update,
    delete_followup,
    followup_history,
    followup_status,
    latest_by_student,
    load_data,
    period_label,
    read_followups,
    save_followup,
    update_followup,
)
from utbapp.i18n import (
    LANG_NAMES,
    final_label,
    fmt_int,
    fmt_pct,
    permanence_label,
    risk_label,
    signal_label,
    status_label,
    tr,
)

app = Dash(__name__, suppress_callback_exceptions=True, title="Alertas Tempranas · UTB", assets_folder="assets")
server = app.server
students, history, _ = load_data()

@server.route("/manus-routes.json")
def manus_routes():
    return server.response_class(
        response=json.dumps(
            {
                "routes": [
                    {"path": "/", "title": "Inicio"},
                    {"path": "/estudiantes", "title": "Estudiantes"},
                    {"path": "/alertas", "title": "Alertas"},
                    {"path": "/seguimientos", "title": "Seguimientos"},
                    {"path": "/reportes", "title": "Reportes"},
                    {"path": "/perfil", "title": "Mi perfil"},
                ]
            }
        ),
        mimetype="application/json",
    )

PALETTE = {"Alto": "#E3545B", "Medio": "#E8B000", "Bajo": "#009664"}
NAV = [
    ("nav.home", "/", "⌂"),
    ("nav.students", "/estudiantes", "ϙ"),
    ("nav.alerts", "/alertas", "◬"),
    ("nav.followups", "/seguimientos", "→"),
    ("nav.reports", "/reportes", "▥"),
]
DEFAULT_PREFS = {"lang": "es", "theme": "light"}
DEFAULT_PROFILE = {"name": "Camila", "email": "camila@utb.edu.co", "role": "admin", "description": ""}
FOLLOWUP_MAX_MONTHS = 6
DEMO_SESSION = {"user": "Camila", "role": "admin"}

ICON_PATHS = {
    "user": '<path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/>',
    "globe": '<circle cx="12" cy="12" r="9"/><path d="M3 12h18"/><path d="M12 3a15 15 0 0 1 0 18 15 15 0 0 1 0-18Z"/>',
    "sun": '<circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M2 12h2M20 12h2M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4"/>',
    "moon": '<path d="M21 12.8A9 9 0 1 1 11.2 3a7 7 0 0 0 9.8 9.8Z"/>',
    "logout": '<path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/><path d="M16 17l5-5-5-5"/><path d="M21 12H9"/>',
    "check": '<path d="M20 6L9 17l-5-5"/>',
    "chevron": '<path d="M6 9l6 6 6-6"/>',
    "pencil": '<path d="M12 20h9"/><path d="M16.5 3.5a2.1 2.1 0 0 1 3 3L7 19l-4 1 1-4Z"/>',
    "camera": '<path d="M23 19a2 2 0 0 1-2 2H3a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h4l2-3h6l2 3h4a2 2 0 0 1 2 2Z"/><circle cx="12" cy="13" r="4"/>',
    "shield": '<path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10Z"/><path d="M9 12l2 2 4-4"/>',
    "mail": '<rect x="2" y="4" width="20" height="16" rx="2"/><path d="m2 7 10 6 10-6"/>',
}


def icon(name, color="#5B6576", size=18, class_name=""):
    inner = ICON_PATHS[name]
    svg = (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 24 24" '
        f'fill="none" stroke="{color}" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round">{inner}</svg>'
    )
    return html.Img(
        src="data:image/svg+xml;utf8," + quote(svg),
        className=f"icon {class_name}".strip(),
        alt="",
    )


def initials(name):
    parts = [p for p in str(name or "").split() if p]
    if not parts:
        return "UT"
    if len(parts) == 1:
        return parts[0][:2].upper()
    return (parts[0][0] + parts[1][0]).upper()


def icon_box(text, tone="blue"):
    return html.Div(text, className=f"icon-box {tone}")


def risk_badge(lang, value):
    return html.Span(
        [html.Span(className="dot"), risk_label(lang, value)],
        className=f"badge {str(value).lower()}",
    )


def status_badge(lang, value):
    tone = {
        "Nueva": "red",
        "En seguimiento": "blue",
        "Cerrada": "green",
        "Sin acompañamiento": "muted",
    }.get(value, "muted")
    return html.Span(
        [html.Span(className="dot"), status_label(lang, value)],
        className=f"status {tone}",
    )


def demo_banner(lang, dismissed=False):
    if dismissed:
        return html.Div(id="demo-banner-container", style={"display": "none"})
    return html.Div(
        [
            html.Span("ⓘ", className="info-symbol"),
            html.B(tr(lang, "demo.title")),
            tr(lang, "demo.text"),
            html.Button(
                tr(lang, "demo.action"),
                id="dismiss-demo-btn",
                className="banner-action",
                style={
                    "border": "none",
                    "background": "none",
                    "cursor": "pointer",
                    "fontFamily": "inherit",
                    "color": "inherit",
                    "padding": "0",
                },
                n_clicks=0,
            ),
        ],
        id="demo-banner-container",
        className="demo-banner",
    )


def critical_alert_banner(high_count, lang):
    if not high_count:
        return html.Div(id="critical-alert-banner-container", style={"display": "none"})
    return html.Div(
        html.Div(
            [
                html.Div(
                    [
                        html.Div("⚠️", className="critical-alert-banner-icon"),
                        html.Div(
                            [
                                html.H4(tr(lang, "rf05.banner_title", count=high_count)),
                                html.P(tr(lang, "rf05.banner_desc", count=high_count)),
                            ],
                            className="critical-alert-banner-text",
                        ),
                    ],
                    className="critical-alert-banner-content",
                ),
                html.Div(
                    [
                        html.Span(tr(lang, "rf05.banner_btn")),
                    ],
                    className="critical-alert-banner-action",
                ),
            ],
            id="critical-alert-banner",
            className="critical-alert-banner",
            n_clicks=0,
        ),
        id="critical-alert-banner-container",
    )


def submenu_item(lang, item_id, label, active, icon_name):
    accent = "#153DDA" if active else "transparent"
    return html.Button(
        [
            html.Span(icon(icon_name, accent, 15), className="submenu-icon"),
            html.Span(label, className="submenu-label"),
            html.Span(icon("check", accent, 15), className="submenu-check") if active else html.Span(className="submenu-check"),
        ],
        id=item_id,
        className=f"submenu-item {'active' if active else ''}",
        n_clicks=0,
        type="button",
    )


def user_menu(lang, dark, profile):
    ink = "#A9B7CC" if dark else "#5B6576"
    accent = "#7FA6FF" if dark else "#153DDA"
    name = profile.get("name") or "Camila"
    role = tr(lang, "role.admin")
    theme_key = "menu.dark" if dark else "menu.light"
    return html.Div(
        [
            html.Button(
                [
                    html.Span(initials(name), className="avatar top-avatar"),
                    html.Span(
                        [html.B(name), html.Small(role)],
                        className="user-copy",
                    ),
                    html.Span(icon("chevron", ink, 16), className="chevron-icon"),
                ],
                id="user-menu-toggle",
                className="user-menu-btn",
                n_clicks=0,
                type="button",
                title=tr(lang, "menu.open"),
                **{"aria-label": tr(lang, "menu.open")},
            ),
            html.Div(
                [
                    dcc.Link(
                        [icon("user", ink, 18), html.Span(tr(lang, "menu.profile"))],
                        href="/perfil",
                        id="menu-profile",
                        className="menu-item",
                    ),
                    html.Div(
                        [
                            html.Div(
                                [
                                    icon("globe", ink, 18),
                                    html.Span(tr(lang, "menu.language")),
                                    html.Span(f": {LANG_NAMES[lang]}", className="menu-value"),
                                    html.Span(icon("chevron", ink, 14), className="menu-caret"),
                                ],
                                className="menu-item menu-trigger",
                            ),
                            html.Div(
                                [
                                    submenu_item(lang, "menu-lang-es", "Español", lang == "es", "globe"),
                                    submenu_item(lang, "menu-lang-en", "English", lang == "en", "globe"),
                                ],
                                className="submenu",
                            ),
                        ],
                        className="menu-group",
                    ),
                    html.Div(
                        [
                            html.Div(
                                [
                                    icon("moon" if dark else "sun", ink, 18),
                                    html.Span(tr(lang, "menu.theme")),
                                    html.Span(f": {tr(lang, theme_key)}", className="menu-value"),
                                    html.Span(icon("chevron", ink, 14), className="menu-caret"),
                                ],
                                className="menu-item menu-trigger",
                            ),
                            html.Div(
                                [
                                    submenu_item(lang, "menu-theme-light", tr(lang, "menu.light"), not dark, "sun"),
                                    submenu_item(lang, "menu-theme-dark", tr(lang, "menu.dark"), dark, "moon"),
                                ],
                                className="submenu",
                            ),
                        ],
                        className="menu-group",
                    ),
                    html.Div(className="menu-sep"),
                    html.Button(
                        [icon("logout", "#D84951", 18), html.Span(tr(lang, "menu.logout"))],
                        id="menu-logout",
                        className="menu-item menu-danger",
                        n_clicks=0,
                        type="button",
                    ),
                ],
                id="user-dropdown",
                className="user-dropdown",
            ),
        ],
        className="user-menu",
    )


def header(lang, dark, profile):
    return html.Header(
        [
            html.Div(
                [
                    html.Img(src="/assets/logo.png", alt="UTB", style={"height": "42px", "objectFit": "contain"}),
                    html.Div(className="brand-divider"),
                    html.Div("UTBAlert - Sistema de Alertas Tempranas", className="product-name"),
                ],
                className="brand",
            ),
            user_menu(lang, dark, profile),
        ],
        className="topbar",
    )


def sidebar(lang, path):
    items = []
    for key, href, glyph in NAV:
        active = path == href or (href != "/" and path.startswith(href))
        items.append(
            dcc.Link(
                [
                    html.Span(glyph, className="nav-icon"),
                    html.Span(tr(lang, key)),
                    html.Span(className="active-line"),
                ],
                href=href,
                className=f"nav-item {'active' if active else ''}",
            )
        )
    return html.Aside(
        [
            html.Div(tr(lang, "side.admin"), className="side-label"),
            html.Nav(items),
            html.Div(
                [
                    html.B(tr(lang, "side.system")),
                    html.Span(tr(lang, "side.period", period=period_label(max(history.periodo_academico)))),
                ],
                className="side-footer",
            ),
        ],
        className="sidebar",
    )


def shell(path, content, lang, dark, profile):
    return html.Div(
        [
            header(lang, dark, profile),
            html.Div([sidebar(lang, path), html.Main(content, className="main")], className="body"),
            html.Div(id="menu-backdrop", className="menu-backdrop"),
        ]
    )


def page_heading(lang, title, subtitle, action=None):
    copy = [
        html.Div(tr(lang, "eyebrow"), className="eyebrow"),
        html.H1(title),
    ]
    if subtitle:
        copy.append(html.P(subtitle))
    return html.Div(
        [
            html.Div(copy, className="heading-copy"),
            action,
        ],
        className="page-heading",
    )


def action_button(label, id=None, primary=False):
    class_name = f"button {'primary' if primary else ''}".strip()
    if id is None:
        return html.Button(label, className=class_name)
    return html.Button(label, id=id, className=class_name, n_clicks=0)


def filter_bar(values, lang, compact=False):
    values = values or {}

    def opts(items, all_key, labeler=None):
        lab = labeler or (lambda x: str(x))
        return [{"label": tr(lang, all_key), "value": "Todos"}] + [
            {"label": lab(x), "value": str(x)} for x in items
        ]

    fields = [
        dcc.Dropdown(
            opts(options_from("programa"), "all.programs"),
            values.get("programa", "Todos"),
            id="global-programa",
            clearable=False,
            className="filter",
        ),
        dcc.Dropdown(
            period_options() + [{"label": tr(lang, "all.periods"), "value": "Todos"}],
            values.get("periodo", "Todos"),
            id="global-periodo",
            clearable=False,
            className="filter",
        ),
        dcc.Dropdown(
            opts(sorted(history.nivel_actual.unique()), "all.levels"),
            values.get("nivel", "Todos"),
            id="global-nivel",
            clearable=False,
            className="filter",
        ),
    ]

    if compact:
        # Vista de directorio: el riesgo alto es el único indicador visible.
        fields.append(
            dcc.Dropdown(
                [{"label": risk_label(lang, "Alto"), "value": "Alto"}],
                "Alto",
                id="global-riesgo",
                clearable=False,
                className="filter",
            )
        )
        # Anclas ocultas: los filtros retirados siguen existiendo para que el
        # callback update_filters no pierda sus Inputs.
        fields.append(
            html.Div(
                [
                    dcc.Dropdown(
                        opts(sorted(history.estado_academico.unique()), "all.states"),
                        "Todos",
                        id="global-academico",
                        clearable=False,
                    ),
                    dcc.Dropdown(
                        opts(sorted(students.estado_final.unique()), "all.final", lambda x: final_label(lang, x)),
                        "Todos",
                        id="global-final",
                        clearable=False,
                    ),
                ],
                className="filter-anchors",
            )
        )
    else:
        fields.extend(
            [
                dcc.Dropdown(
                    opts(sorted(history.estado_academico.unique()), "all.states"),
                    values.get("academico", "Todos"),
                    id="global-academico",
                    clearable=False,
                    className="filter",
                ),
                dcc.Dropdown(
                    opts(["Alto", "Medio", "Bajo"], "all.risks", lambda x: risk_label(lang, x)),
                    values.get("riesgo", "Todos"),
                    id="global-riesgo",
                    clearable=False,
                    className="filter",
                ),
                dcc.Dropdown(
                    opts(sorted(students.estado_final.unique()), "all.final", lambda x: final_label(lang, x)),
                    values.get("final", "Todos"),
                    id="global-final",
                    clearable=False,
                    className="filter",
                ),
            ]
        )

    return html.Div(fields, className="filter-bar")


def options_from(column):
    return sorted(students[column].dropna().unique())


def period_options():
    return [{"label": period_label(p), "value": p} for p in sorted(history.periodo_academico.unique())]


def kpi(label, value, sub, tone="blue", tag=None):
    return html.Div(
        [
            html.Div(
                [icon_box({"blue": "♧", "red": "△", "amber": "♢", "green": "✓"}.get(tone, "•"), tone), html.Span(tag or "", className="kpi-tag")],
                className="kpi-top",
            ),
            html.Div(value, className="kpi-value"),
            html.Div(label, className="kpi-label"),
            html.Div(sub, className="kpi-sub"),
        ],
        className="kpi-card",
    )


def filters_from(values):
    return {k: values.get(k) or "Todos" for k in ["programa", "periodo", "nivel", "academico", "riesgo", "final"]}


def apply_filters(values):
    values = filters_from(values or {})
    current = latest_by_student(history, None if values["periodo"] in ("Todos", "Todos los periodos") else values["periodo"])
    if values["programa"] != "Todos":
        current = current[current.programa == values["programa"]]
    if values["nivel"] != "Todos":
        current = current[current.nivel_actual.astype(str) == str(values["nivel"])]
    if values["academico"] != "Todos":
        current = current[current.estado_academico == values["academico"]]
    if values["riesgo"] != "Todos":
        current = current[current.riesgo == values["riesgo"]]
    if values["final"] != "Todos":
        current = current[current.estado_final == values["final"]]
    return current


def latest_view(values=None):
    return apply_filters(values or {})


def students_filters(values=None):
    """El directorio muestra siempre riesgo alto y no usa los filtros retirados."""
    return {**(values or {}), "riesgo": "Alto", "academico": "Todos", "final": "Todos"}


def table_styles(dark):
    if dark:
        header = {"backgroundColor": "#16233A", "color": "#8FA0B8", "fontWeight": "600", "fontSize": "11px", "border": "0", "textAlign": "left"}
        cell = {"border": "0", "borderBottom": "1px solid #1E2A3F", "padding": "13px 10px", "fontSize": "12px", "color": "#D6E0EF", "textAlign": "left", "backgroundColor": "#111C2E"}
    else:
        header = {"backgroundColor": "#F7F9FC", "color": "#748091", "fontWeight": "600", "fontSize": "11px", "border": "0", "textAlign": "left"}
        cell = {"border": "0", "borderBottom": "1px solid #E9EEF4", "padding": "13px 10px", "fontSize": "12px", "color": "#344054", "textAlign": "left"}
    return header, cell


def small_table(rows, columns, dark=False):
    header, cell = table_styles(dark)
    return dash_table.DataTable(
        data=rows,
        columns=[{"name": name, "id": key} for name, key in columns],
        page_size=8,
        style_as_list_view=True,
        style_table={"overflowX": "auto"},
        style_header=header,
        style_cell=cell,
    )


def chart_palette(dark):
    return {
        "paper": "#111C2E" if dark else "#ffffff",
        "plot": "#111C2E" if dark else "#ffffff",
        "font": "#9FB0C7" if dark else "#778292",
        "text": "#E6EDF8" if dark else "#17263C",
        "grid": "#22304A" if dark else "#E9EEF4",
    }


def distribution_figure(df, lang, dark):
    theme = chart_palette(dark)
    counts = df.riesgo.value_counts().reindex(["Alto", "Medio", "Bajo"], fill_value=0)
    fig = go.Figure(
        go.Pie(
            labels=counts.index,
            values=counts.values,
            hole=0.68,
            marker_colors=[PALETTE[x] for x in counts.index],
            textinfo="none",
            sort=False,
        )
    )
    fig.update_layout(
        showlegend=False,
        margin=dict(l=0, r=0, t=0, b=0),
        height=230,
        paper_bgcolor=theme["paper"],
        plot_bgcolor=theme["plot"],
        annotations=[
            dict(
                text=f"{fmt_int(len(df), lang)}<br><span style='font-size:11px'>{tr(lang, 'label.students')}</span>",
                x=0.5,
                y=0.5,
                showarrow=False,
                font=dict(size=25, color=theme["text"]),
            )
        ],
    )
    return fig


def trend_figure(lang, dark):
    theme = chart_palette(dark)
    counts = (
        history.assign(periodo=history.periodo_academico.map(period_label))
        .query("riesgo != 'Bajo'")
        .groupby("periodo")
        .size()
        .tail(6)
        .reset_index(name="alertas")
    )
    fig = px.area(counts, x="periodo", y="alertas", markers=False)
    fig.update_traces(
        line_color="#31B8CD",
        fillcolor="rgba(49,184,205,.28)" if dark else "rgba(216,240,245,.85)",
        hovertemplate="%{x}<br>%{y}<extra></extra>",
    )
    fig.update_layout(
        height=250,
        margin=dict(l=0, r=0, t=10, b=25),
        paper_bgcolor=theme["paper"],
        plot_bgcolor=theme["plot"],
        xaxis_title=None,
        yaxis_title=None,
        showlegend=False,
        font=dict(color=theme["font"], size=10),
    )
    fig.update_xaxes(
        gridcolor=theme["grid"],
        zeroline=False,
        type="category",
        tickangle=0,
        tickfont=dict(size=10),
        tickmode="array",
        tickvals=counts["periodo"].tolist(),
        ticktext=counts["periodo"].tolist(),
    )
    fig.update_yaxes(gridcolor=theme["grid"], zeroline=False)
    return fig


# === PAGES ===


def home_page(values, lang, dark, profile, dismissed_demo=False):
    df = latest_view(values)
    total = len(df) or 1
    counts = df.riesgo.value_counts()
    follows = read_followups()
    active = df[df.estado_final == "ACTIVO"]
    recent = (
        df[df.riesgo.isin(["Alto", "Medio"])]
        .sort_values(
            ["riesgo", "promedio_ponderado_acumulado"],
            key=lambda s: s.map({"Alto": 0, "Medio": 1}).fillna(2) if s.name == "riesgo" else s,
        )
        .head(6)
        .copy()
    )
    recent["periodo"] = recent.periodo_academico.map(period_label)
    recent["seguimiento"] = recent.estudiante_id.map(lambda x: followup_status(x, follows))
    rows = [
        {
            "prioridad": risk_label(lang, r.riesgo),
            "estudiante": r.estudiante_id,
            "motivo": signal_label(lang, r.senal_principal),
            "periodo": r.periodo,
            "estado": status_label(lang, r.seguimiento),
        }
        for _, r in recent.iterrows()
    ]
    new_alerts = sum(1 for r in rows if r["estado"] == status_label(lang, "Nueva"))
    return [
        page_heading(
            lang,
            tr(lang, "home.greeting", name=profile.get("name") or "Camila"),
            tr(lang, "home.subtitle"),
            action_button(tr(lang, "export.summary"), "export-btn"),
        ),
        critical_alert_banner(counts.get("Alto", 0), lang),
        demo_banner(lang, dismissed_demo),
        filter_bar(values, lang),
        html.Div(
            [
                kpi(
                    tr(lang, "students.analyzed"),
                    fmt_int(len(df), lang),
                    tr(
                        lang,
                        "home.counts",
                        active=fmt_int(len(active), lang),
                        graduated=fmt_int(len(df[df.estado_final == "GRADUADO"]), lang),
                        dropped=fmt_int(len(df[df.estado_final == "DESERTOR"]), lang),
                    ),
                    "blue",
                ),
                kpi(
                    tr(lang, "indicator.high"),
                    fmt_int(counts.get("Alto", 0), lang),
                    tr(lang, "pct.of_filtered", pct=fmt_pct(counts.get("Alto", 0) / total * 100, lang)),
                    "red",
                ),
                kpi(
                    tr(lang, "indicator.medium"),
                    fmt_int(counts.get("Medio", 0), lang),
                    tr(lang, "pct.of_filtered", pct=fmt_pct(counts.get("Medio", 0) / total * 100, lang)),
                    "amber",
                ),
                kpi(
                    tr(lang, "indicator.low"),
                    fmt_int(counts.get("Bajo", 0), lang),
                    tr(lang, "pct.of_filtered", pct=fmt_pct(counts.get("Bajo", 0) / total * 100, lang)),
                    "green",
                ),
                kpi(
                    tr(lang, "home.new_alerts"),
                    fmt_int(new_alerts, lang),
                    tr(lang, "label.last_period"),
                    "blue",
                    tr(lang, "label.last"),
                ),
            ],
            className="kpi-grid",
        ),
        html.Div(
            [
                html.Div(
                    [
                        html.Div(
                            [
                                html.H2(tr(lang, "home.distribution")),
                                html.P(tr(lang, "home.distribution_sub")),
                            ],
                            className="card-head",
                        ),
                        html.Div(
                            [
                                dcc.Graph(figure=distribution_figure(df, lang, dark), config={"displayModeBar": False}),
                                html.Div(
                                    [
                                        html.Div(
                                            [
                                                html.Span(className="legend-dot high"),
                                                risk_label(lang, "Alto"),
                                                html.Small(
                                                    f"{fmt_int(counts.get('Alto', 0), lang)} {tr(lang, 'label.students')} · {fmt_pct(counts.get('Alto', 0) / total * 100, lang)}"
                                                ),
                                            ]
                                        ),
                                        html.Div(
                                            [
                                                html.Span(className="legend-dot medium"),
                                                risk_label(lang, "Medio"),
                                                html.Small(
                                                    f"{fmt_int(counts.get('Medio', 0), lang)} {tr(lang, 'label.students')} · {fmt_pct(counts.get('Medio', 0) / total * 100, lang)}"
                                                ),
                                            ]
                                        ),
                                        html.Div(
                                            [
                                                html.Span(className="legend-dot low"),
                                                risk_label(lang, "Bajo"),
                                                html.Small(
                                                    f"{fmt_int(counts.get('Bajo', 0), lang)} {tr(lang, 'label.students')} · {fmt_pct(counts.get('Bajo', 0) / total * 100, lang)}"
                                                ),
                                            ]
                                        ),
                                    ],
                                    className="legend-list",
                                ),
                            ],
                            className="donut-content",
                        ),
                    ],
                    className="card chart-card",
                ),
                html.Div(
                    [
                        html.Div(
                            [html.H2(tr(lang, "home.trend")), html.P(tr(lang, "home.trend_sub"))],
                            className="card-head",
                        ),
                        dcc.Graph(figure=trend_figure(lang, dark), config={"displayModeBar": False}),
                        html.Div(
                            [
                                html.Span(tr(lang, "home.generated"), className="chart-foot"),
                                html.Span(tr(lang, "home.last6"), className="chart-foot right"),
                            ],
                            className="chart-footer",
                        ),
                    ],
                    className="card chart-card",
                ),
            ],
            className="two-col",
        ),
        html.Div(
            [
                html.Div(
                    [html.H2(tr(lang, "home.recent")), html.P(tr(lang, "home.recent_sub"))],
                    className="card-head",
                ),
                small_table(
                    rows,
                    [
                        (tr(lang, "col.priority"), "prioridad"),
                        (tr(lang, "col.student"), "estudiante"),
                        (tr(lang, "col.reason"), "motivo"),
                        (tr(lang, "col.period"), "periodo"),
                        (tr(lang, "col.status"), "estado"),
                    ],
                    dark,
                ),
            ],
            className="card table-card",
        ),
        variables_catalog_card(lang, dark),
    ]


# === DETALLE DEL ESTUDIANTE ===

STUDENT_PROFILE = students.set_index("estudiante_id")
LATEST_RECORD = latest_by_student(history).set_index("estudiante_id")


def clean_text(value):
    """Devuelve el texto del valor o ``None`` cuando no hay dato."""
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return None
    text = str(value).strip()
    return text if text and text.lower() not in ("nan", "none") else None


def fmt_detail(value, decimals=2, suffix=""):
    """Formatea un número del detalle y usa ``—`` cuando no hay dato."""
    number = pd.to_numeric(value, errors="coerce")
    if pd.isna(number):
        return "—"
    return f"{float(number):.{decimals}f}{suffix}"


def student_detail_data(student_id, lang):
    """Datos del estudiante seleccionado, desde la misma fuente que el directorio."""
    if student_id not in STUDENT_PROFILE.index or student_id not in LATEST_RECORD.index:
        return None
    info = STUDENT_PROFILE.loc[[student_id]].iloc[0]
    last = LATEST_RECORD.loc[[student_id]].iloc[0]
    entry_period = clean_text(info.get("periodo_ingreso"))
    last_period = clean_text(last.get("periodo_academico"))
    main_signal = clean_text(last.get("senal_principal"))
    return {
        "id": student_id,
        "programa": clean_text(last.get("programa")) or "—",
        "nivel": clean_text(last.get("nivel_actual")) or "—",
        "estado_final": clean_text(info.get("estado_final")),
        "estado_permanencia": clean_text(info.get("estado_permanencia")) or "—",
        "periodo_ingreso": period_label(entry_period) if entry_period else "—",
        "semestres": clean_text(info.get("semestres_cursados")) or "—",
        "promedio": fmt_detail(last.get("promedio_ponderado_acumulado")),
        "creditos": clean_text(info.get("creditos_aprobados_totales")) or "—",
        "avance": fmt_detail(last.get("avance_plan"), 1, "%"),
        "ultimo_periodo": period_label(last_period) if last_period else "—",
        "riesgo": clean_text(last.get("riesgo")) or "Bajo",
        "senal": signal_label(lang, main_signal) if main_signal else "—",
        "asistencia": fmt_detail(last.get("porcentaje_asistencia"), 1, "%"),
        "estado_academico": clean_text(last.get("estado_academico")) or "—",
    }


EMPTY_DETAIL = {
    "id": "",
    "programa": "—",
    "nivel": "—",
    "estado_final": None,
    "estado_permanencia": "—",
    "periodo_ingreso": "—",
    "semestres": "—",
    "promedio": "—",
    "creditos": "—",
    "avance": "—",
    "ultimo_periodo": "—",
    "riesgo": "Bajo",
    "senal": "—",
    "asistencia": "—",
    "estado_academico": "—",
}


def add_months(value: date, months: int) -> date:
    """Suma meses de calendario y conserva el día cuando existe."""
    month_index = value.month - 1 + months
    year = value.year + month_index // 12
    month = month_index % 12 + 1
    day = min(value.day, calendar.monthrange(year, month)[1])
    return date(year, month, day)


def followup_date_bounds() -> tuple[str, str]:
    """Rango permitido para la fecha de la próxima acción: hoy a +6 meses."""
    today = date.today()
    return today.isoformat(), add_months(today, FOLLOWUP_MAX_MONTHS).isoformat()


def toast(kind: str, message: str):
    """Salidas (clase, contenido) de la notificación temporal no bloqueante."""
    icon = "✓" if kind == "success" else "!"
    content = [
        html.Span(icon, className="toast-icon"),
        html.Span(message, className="toast-text"),
        html.Span(str(time.time_ns()), className="toast-token"),
    ]
    return f"toast toast-{kind}", content


def detail_item(label, value, tone=None):
    style = {"color": PALETTE[tone], "fontWeight": "600"} if tone in PALETTE else None
    return html.Div([html.Dt(label), html.Dd(value, style=style)])


def detail_column(title, items):
    return html.Section([html.H3(title), html.Dl(items)], className="student-detail-col")


def student_detail_modal(lang, data):
    state = permanence_label(lang, data["estado_final"]) if data["estado_final"] else "—"
    min_date, max_date = followup_date_bounds()
    return [
        html.Div(
            [
                html.H2(tr(lang, "detail.title"), id="student-detail-title"),
                html.Span(data["id"], className="student-detail-code"),
            ],
            className="student-detail-head",
        ),
        html.Div(
            [
                html.Span(tr(lang, "detail.avatar"), className="avatar student-detail-avatar", **{"aria-hidden": "true"}),
                html.Div(
                    [
                        html.B(data["programa"]),
                        html.Span(
                            tr(lang, "detail.level_state", level=data["nivel"], state=state),
                            className="student-detail-level",
                        ),
                        risk_badge(lang, data["riesgo"]),
                    ],
                    className="student-detail-identity-text",
                ),
            ],
            className="student-detail-identity",
        ),
        html.Div(
            [
                detail_column(
                    tr(lang, "detail.general"),
                    [
                        detail_item(tr(lang, "detail.program"), data["programa"]),
                        detail_item(tr(lang, "detail.entry_period"), data["periodo_ingreso"]),
                        detail_item(tr(lang, "detail.permanence"), data["estado_permanencia"]),
                        detail_item(tr(lang, "detail.semesters"), data["semestres"]),
                    ],
                ),
                detail_column(
                    tr(lang, "detail.performance"),
                    [
                        detail_item(tr(lang, "detail.average"), data["promedio"]),
                        detail_item(tr(lang, "detail.credits"), data["creditos"]),
                        detail_item(tr(lang, "detail.progress"), data["avance"]),
                        detail_item(tr(lang, "detail.last_period"), data["ultimo_periodo"]),
                    ],
                ),
                detail_column(
                    tr(lang, "detail.risk"),
                    [
                        detail_item(tr(lang, "detail.risk_level"), risk_label(lang, data["riesgo"]), data["riesgo"]),
                        detail_item(tr(lang, "detail.main_signal"), data["senal"]),
                        detail_item(tr(lang, "detail.attendance"), data["asistencia"]),
                        detail_item(tr(lang, "detail.academic_state"), data["estado_academico"]),
                    ],
                ),
            ],
            className="student-detail-grid",
        ),
        html.Div(
            [
                html.H3(tr(lang, "detail.followup")),
                html.P(tr(lang, "detail.followup_sub"), className="student-detail-sub"),
                dcc.Dropdown(
                    period_options(),
                    max(history.periodo_academico),
                    id="student-detail-period",
                    clearable=False,
                    className="filter",
                ),
                dcc.Textarea(id="student-detail-note", placeholder=tr(lang, "detail.note_ph"), className="textarea"),
                dcc.Input(id="student-detail-action", placeholder=tr(lang, "detail.action_ph"), className="search-input"),
                dcc.Input(
                    id="student-detail-date",
                    type="date",
                    min=min_date,
                    max=max_date,
                    placeholder=tr(lang, "detail.date_ph"),
                    className="search-input student-detail-date-input",
                ),
                html.Div(
                    [
                        html.Button(tr(lang, "detail.back"), id="close-student-detail", className="button", n_clicks=0, type="button"),
                        html.Button(
                            tr(lang, "action.save_followup"),
                            id="save-student-followup",
                            className="button primary",
                            n_clicks=0,
                            type="button",
                        ),
                    ],
                    className="modal-actions",
                ),
                html.Div(id="student-detail-message", className="form-message"),
            ],
            className="student-detail-followup",
        ),
    ]


def students_page(values, lang, dark, dismissed_demo=False):
    values = students_filters(values)
    df = latest_view(values).copy()
    follows = read_followups()
    df["periodo"] = df.periodo_academico.map(period_label)
    df["acompanamiento"] = df.estudiante_id.map(lambda x: status_label(lang, followup_status(x, follows)))
    df = df.sort_values(["puntaje_riesgo", "promedio_ponderado_acumulado"], ascending=[False, True])
    rows = df[
        ["estudiante_id", "programa", "nivel_actual", "riesgo", "senal_principal", "acompanamiento", "periodo"]
    ].rename(
        columns={
            "estudiante_id": "estudiante",
            "nivel_actual": "nivel",
            "riesgo": "indicador",
            "senal_principal": "señal_principal",
        }
    )
    rows["indicador"] = rows.indicador.map(lambda x: risk_label(lang, x))
    rows["señal_principal"] = rows["señal_principal"].map(lambda x: signal_label(lang, x))
    rows = rows.to_dict("records")
    header, cell = table_styles(dark)
    return [
        page_heading(
            lang,
            tr(lang, "students.title"),
            None,
            action_button(tr(lang, "export.directory"), "export-btn"),
        ),
        demo_banner(lang, dismissed_demo),
        html.Div(
            [
                filter_bar(values, lang, compact=True),
                html.Div(
                    [
                        icon_box("△", "red"),
                        html.Div(
                            [
                                html.Div(fmt_int(len(df), lang), className="kpi-value"),
                                html.Div(tr(lang, "indicator.high"), className="kpi-label"),
                            ],
                            className="compact-kpi-copy",
                        ),
                    ],
                    className="kpi-card compact-kpi",
                ),
            ],
            className="filter-row",
        ),
        html.Div(
            [
                html.Div(
                    [html.H2(tr(lang, "students.directory")), html.P(tr(lang, "students.directory_sub"))],
                    className="card-head",
                ),
                dcc.Input(id="student-search", placeholder=tr(lang, "students.search"), className="search-input"),
                dash_table.DataTable(
                    id="students-table",
                    data=rows,
                    columns=[
                        {"name": tr(lang, "col.student"), "id": "estudiante"},
                        {"name": tr(lang, "col.program"), "id": "programa"},
                        {"name": tr(lang, "col.level"), "id": "nivel"},
                        {"name": tr(lang, "col.indicator"), "id": "indicador"},
                        {"name": tr(lang, "col.signal"), "id": "señal_principal"},
                        {"name": tr(lang, "col.followup"), "id": "acompanamiento"},
                        {"name": tr(lang, "col.period"), "id": "periodo"},
                    ],
                    page_size=10,
                    style_as_list_view=True,
                    style_header=header,
                    style_cell=cell,
                    style_data_conditional=[
                        {
                            "if": {"column_id": "estudiante"},
                            "color": "#153DDA",
                            "textDecoration": "underline",
                            "cursor": "pointer",
                            "fontWeight": "500",
                        },
                        {"if": {"filter_query": f"{{indicador}} = '{risk_label(lang, 'Alto')}'", "column_id": "indicador"}, "color": PALETTE["Alto"], "fontWeight": "600"},
                        {"if": {"filter_query": f"{{indicador}} = '{risk_label(lang, 'Medio')}'", "column_id": "indicador"}, "color": PALETTE["Medio"], "fontWeight": "600"},
                    ],
                ),
            ],
            className="card table-card",
        ),
    ]


def variables_catalog_card(lang, dark):
    idx = 0 if lang == "es" else 1
    rows = [
        {
            "variable": item["name"][idx],
            "categoria": item["cat"][idx],
            "criterio": item["criteria"][idx],
            "indicador": risk_label(lang, item["level"]),
            "estado": item["state"][idx],
        }
        for item in VARIABLES
    ]
    header, cell = table_styles(dark)
    return html.Div(
        [
            html.Div(
                [html.H2(tr(lang, "variables.catalog")), html.P(tr(lang, "variables.catalog_sub"))],
                className="card-head",
            ),
            dash_table.DataTable(
                data=rows,
                columns=[
                    {"name": tr(lang, "col.variable"), "id": "variable"},
                    {"name": tr(lang, "col.category"), "id": "categoria"},
                    {"name": tr(lang, "col.criteria"), "id": "criterio"},
                    {"name": tr(lang, "col.indicator"), "id": "indicador"},
                    {"name": tr(lang, "col.state"), "id": "estado"},
                ],
                style_as_list_view=True,
                style_header=header,
                style_cell=cell,
                style_data_conditional=[
                    {"if": {"filter_query": f"{{indicador}} = '{risk_label(lang, 'Alto')}'", "column_id": "indicador"}, "color": PALETTE["Alto"], "fontWeight": "600"},
                    {"if": {"filter_query": f"{{indicador}} = '{risk_label(lang, 'Medio')}'", "column_id": "indicador"}, "color": PALETTE["Medio"], "fontWeight": "600"},
                ],
            ),
        ],
        className="card table-card",
    )


VARIABLES = [
    {"name": ("Promedio acumulado", "Cumulative average"), "cat": ("Académica", "Academic"), "criteria": ("< 3,20", "< 3.20"), "level": "Alto", "state": ("Activo", "Active")},
    {"name": ("Asistencia", "Attendance"), "cat": ("Asistencia", "Attendance"), "criteria": ("< 70 %", "< 70 %"), "level": "Alto", "state": ("Activo", "Active")},
    {"name": ("Reprobadas en el periodo", "Failed courses this term"), "cat": ("Académica", "Academic"), "criteria": ("> 2", "> 2"), "level": "Alto", "state": ("Activo", "Active")},
    {"name": ("Retraso académico", "Academic delay"), "cat": ("Académica", "Academic"), "criteria": ("> 3", "> 3"), "level": "Alto", "state": ("Activo", "Active")},
    {"name": ("Avance del plan", "Plan progress"), "cat": ("Académica", "Academic"), "criteria": ("< 80 % del avance esperado", "< 80% of expected progress"), "level": "Medio", "state": ("Activo", "Active")},
    {"name": ("Asignaturas canceladas", "Cancelled courses"), "cat": ("Académica", "Academic"), "criteria": ("≥ 2 en el periodo", "≥ 2 in the term"), "level": "Medio", "state": ("Activo", "Active")},
    {"name": ("Descenso del promedio del semestre", "Semester average drop"), "cat": ("Académica", "Academic"), "criteria": ("≥ 0,5 frente al anterior", "≥ 0.5 vs. previous"), "level": "Medio", "state": ("Borrador", "Draft")},
]


def variables_page(lang, dark):
    idx = 0 if lang == "es" else 1
    rows = [
        {
            "variable": item["name"][idx],
            "categoria": item["cat"][idx],
            "criterio": item["criteria"][idx],
            "indicador": risk_label(lang, item["level"]),
            "estado": item["state"][idx],
        }
        for item in VARIABLES
    ]
    header, cell = table_styles(dark)
    return [
        page_heading(
            lang,
            tr(lang, "variables.title"),
            tr(lang, "variables.subtitle"),
            action_button(tr(lang, "action.new_variable")),
        ),
        demo_banner(lang),
        html.Div(
            [
                html.Div(
                    [html.H2(tr(lang, "variables.catalog")), html.P(tr(lang, "variables.catalog_sub"))],
                    className="card-head",
                ),
                dash_table.DataTable(
                    data=rows,
                    columns=[
                        {"name": tr(lang, "col.variable"), "id": "variable"},
                        {"name": tr(lang, "col.category"), "id": "categoria"},
                        {"name": tr(lang, "col.criteria"), "id": "criterio"},
                        {"name": tr(lang, "col.indicator"), "id": "indicador"},
                        {"name": tr(lang, "col.state"), "id": "estado"},
                    ],
                    style_as_list_view=True,
                    style_header=header,
                    style_cell=cell,
                ),
            ],
            className="card table-card",
        ),
        html.Div(
            [
                html.Div(
                    [html.H2(tr(lang, "variables.reading")), html.P(tr(lang, "variables.reading_sub"))],
                    className="card-head",
                ),
                html.Div(
                    [
                        html.P([risk_badge(lang, "Alto"), tr(lang, "variables.rule_high")]),
                        html.P([risk_badge(lang, "Medio"), tr(lang, "variables.rule_medium")]),
                        html.P([risk_badge(lang, "Bajo"), tr(lang, "variables.rule_low")]),
                    ],
                    className="reading-card",
                ),
            ],
            className="card notice-card",
        ),
        html.Div(tr(lang, "variables.disclaimer"), className="disclaimer"),
    ]


def alerts_summary_title(lang, count):
    if count == 1:
        return tr(lang, "alerts.new_count_one")
    return tr(lang, "alerts.new_count", count=fmt_int(count, lang))


def alerts_page(values, lang, dark, dismissed_demo=False):
    df = latest_view(values).copy()
    follows = read_followups()
    df["periodo"] = df.periodo_academico.map(period_label)
    df["estado"] = df.estudiante_id.map(lambda x: followup_status(x, follows))
    df = df[df.riesgo.isin(["Alto", "Medio"])].sort_values(
        ["puntaje_riesgo", "promedio_ponderado_acumulado"], ascending=[False, True]
    )
    rows = [
        {
            "prioridad": risk_label(lang, r.riesgo),
            "estudiante": r.estudiante_id,
            "motivo": signal_label(lang, r.senal_principal),
            "periodo": r.periodo,
            "estado": status_label(lang, r.estado),
        }
        for _, r in df.iterrows()
    ]
    return [
        page_heading(
            lang,
            tr(lang, "alerts.title"),
            tr(lang, "alerts.subtitle"),
            action_button(tr(lang, "export.alerts"), "export-btn"),
        ),
        demo_banner(lang, dismissed_demo),
        html.Div(
            [
                icon_box("♧", "blue"),
                html.Div(
                    [
                        html.H2(alerts_summary_title(lang, (df.estado == "Nueva").sum())),
                        html.P(tr(lang, "alerts.summary_sub")),
                    ]
                ),
                html.Div(
                    [html.B(tr(lang, "alerts.prioritize")), html.P(tr(lang, "alerts.prioritize_sub"))],
                    className="alert-explain",
                ),
            ],
            className="alert-summary",
        ),
        html.Div(
            [
                html.Div(
                    [html.H2(tr(lang, "alerts.inbox")), html.P(tr(lang, "alerts.inbox_sub"))],
                    className="card-head",
                ),
                html.Div(
                    [
                        html.Span(tr(lang, "alerts.tab_all"), className="tab active"),
                        html.Span(tr(lang, "alerts.tab_new"), className="tab"),
                        html.Span(tr(lang, "alerts.tab_followup"), className="tab"),
                        html.Span(tr(lang, "alerts.tab_closed"), className="tab"),
                    ],
                    className="tabs",
                ),
                small_table(
                    rows,
                    [
                        (tr(lang, "col.priority"), "prioridad"),
                        (tr(lang, "col.student"), "estudiante"),
                        (tr(lang, "col.reason"), "motivo"),
                        (tr(lang, "col.period"), "periodo"),
                        (tr(lang, "col.status"), "estado"),
                    ],
                    dark,
                ),
            ],
            className="card table-card",
        ),
        html.P(tr(lang, "alerts.disclaimer"), className="disclaimer"),
    ]


# === PAGES 2 ===


def _parse_followup_datetime(value):
    """Convierte los formatos de fecha usados por la demo en ``datetime``."""
    if value in (None, ""):
        return None
    text = str(value).strip()
    try:
        return datetime.fromisoformat(text.replace("Z", "+00:00")).replace(tzinfo=None)
    except ValueError:
        pass
    for fmt in ("%Y/%m/%d %H:%M:%S", "%Y/%m/%d", "%d/%m/%Y %H:%M", "%d/%m/%Y"):
        try:
            return datetime.strptime(text, fmt)
        except ValueError:
            continue
    return None


def format_followup_datetime(value):
    """Fecha legible DD/MM/AAAA HH:mm (compatible con registros antiguos)."""
    parsed = _parse_followup_datetime(value)
    if parsed is None:
        return str(value) if value else "—"
    return parsed.strftime("%d/%m/%Y %H:%M")


def format_followup_date(value):
    parsed = _parse_followup_datetime(value)
    if parsed is None:
        return str(value) if value else "—"
    return parsed.strftime("%d/%m/%Y")


def _to_iso_date(value):
    parsed = _parse_followup_datetime(value)
    return parsed.date().isoformat() if parsed else None


def followup_timestamp(record):
    """``updated_at`` cuando existe; de lo contrario la creación original."""
    return record.get("updated_at") or record.get("created_at")


def latest_followup_rows(records):
    """Devuelve (índice original, registro) del reporte vigente por estudiante."""
    latest = {}
    for index, record in enumerate(records):
        student_id = record.get("estudiante_id")
        current = latest.get(student_id)
        timestamp = record.get("created_at") or ""
        if current is None or timestamp >= (current[1].get("created_at") or ""):
            latest[student_id] = (index, record)
    return sorted(latest.values(), key=lambda item: item[1].get("estudiante_id") or "")


def followups_table(records, lang, dark):
    """Tabla de casos con ID clicable y acciones de editar/eliminar."""
    header, cell = table_styles(dark)
    header_style = {**header, "padding": "10px 6px"}
    cell_style = {**cell, "padding": "10px 6px", "fontSize": "11.5px"}
    actions_style = {**cell_style}

    head = html.Thead(
        html.Tr(
            [
                html.Th(tr(lang, "col.student"), style=header_style),
                html.Th(tr(lang, "col.responsible"), style=header_style),
                html.Th(tr(lang, "col.next_action"), style=header_style),
                html.Th(tr(lang, "col.period"), style=header_style),
                html.Th(tr(lang, "followups.datetime"), style=header_style),
                html.Th(tr(lang, "col.status"), style=header_style),
                html.Th(tr(lang, "followups.actions"), style=header_style),
            ]
        )
    )

    body_rows = []
    for index, record in latest_followup_rows(records):
        edited = bool(record.get("updated_at"))
        timestamp_children = [html.Span(format_followup_datetime(followup_timestamp(record)))]
        if edited:
            timestamp_children.append(html.Span(tr(lang, "followups.edited"), className="followup-edited"))
        if sum(r.get("estudiante_id") == record.get("estudiante_id") for r in records) > 1:
            timestamp_children.append(html.Span(tr(lang, "followups.updated_tag"), className="followup-updated"))
        period = record.get("periodo")
        body_rows.append(
            html.Tr(
                [
                    html.Td(
                        html.Button(
                            record.get("estudiante_id") or "—",
                            id={"type": "followup-open", "index": index},
                            className="followup-link",
                            n_clicks=0,
                            type="button",
                        ),
                        style=cell_style,
                    ),
                    html.Td(record.get("responsable") or "—", style=cell_style),
                    html.Td(record.get("proxima_accion") or "—", style=cell_style),
                    html.Td(
                        period_label(period) if period else "—",
                        style={**cell_style, "whiteSpace": "nowrap"},
                    ),
                    html.Td(html.Div(timestamp_children, className="followup-date-cell"), style=cell_style),
                    html.Td(status_badge(lang, record.get("estado")), style=cell_style),
                    html.Td(
                        html.Div(
                            [
                                html.Button(
                                    tr(lang, "followups.edit"),
                                    id={"type": "followup-edit", "index": index},
                                    className="button followup-action-button",
                                    n_clicks=0,
                                    type="button",
                                ),
                                html.Button(
                                    tr(lang, "followups.delete"),
                                    id={"type": "followup-delete", "index": index},
                                    className="button followup-action-button followup-delete-button",
                                    n_clicks=0,
                                    type="button",
                                ),
                                html.Button(
                                    tr(lang, "followups.update_report"),
                                    id={"type": "followup-update", "index": index},
                                    className="button followup-action-button",
                                    n_clicks=0,
                                    type="button",
                                ),
                            ],
                            className="followup-actions",
                        ),
                        style=actions_style,
                    ),
                ]
            )
        )

    return html.Div(
        html.Table([head, html.Tbody(body_rows)], className="followup-table"),
        className="followup-table-wrap",
    )


def followup_detail_modal(lang, record):
    """Detalle de solo lectura de un seguimiento (sin formulario)."""
    record = record or {}
    items = [
        detail_item(tr(lang, "col.period"), period_label(record["periodo"]) if record.get("periodo") else "—"),
        detail_item(tr(lang, "col.responsible"), record.get("responsable") or "—"),
        detail_item(tr(lang, "followups.note"), record.get("nota") or "—"),
        detail_item(tr(lang, "col.next_action"), record.get("proxima_accion") or "—"),
        detail_item(tr(lang, "followups.next_date"), format_followup_date(record.get("fecha_proxima_accion"))),
        detail_item(tr(lang, "followups.created_at"), format_followup_datetime(record.get("created_at"))),
    ]
    if record.get("updated_at"):
        items.append(
            detail_item(tr(lang, "followups.updated_at"), format_followup_datetime(record.get("updated_at")))
        )
    return [
        html.Div(
            html.Button(
                tr(lang, "followups.export_history"),
                id="export-followup-history",
                className="button",
                n_clicks=0,
                type="button",
            ),
            className="followup-export-bar",
        ),
        html.Div(
            [
                html.H2(tr(lang, "followups.detail_title")),
                html.Span(record.get("estudiante_id") or "", className="student-detail-code"),
            ],
            className="student-detail-head",
        ),
        html.Dl(items, className="followup-detail-list"),
        html.Div(
            [
                html.Button(
                    tr(lang, "followups.close"),
                    id="close-followup-detail",
                    className="button",
                    n_clicks=0,
                    type="button",
                ),
                html.Button(
                    tr(lang, "followups.edit"),
                    id="edit-followup-detail",
                    className="button primary",
                    n_clicks=0,
                    type="button",
                ),
                html.Button(
                    tr(lang, "followups.update_report"),
                    id="update-followup-detail",
                    className="button primary",
                    n_clicks=0,
                    type="button",
                ),
            ],
            className="modal-actions",
        ),
    ]


def followup_edit_modal(lang, record, is_update=False):
    """Formulario único de edición, reutilizado por tabla y detalle."""
    record = record or {}
    min_date, max_date = followup_date_bounds()
    return [
        html.Div(
            [
                html.H2(tr(lang, "followups.update_title") if is_update else tr(lang, "followups.edit_title")),
                html.Span(record.get("estudiante_id") or "", className="student-detail-code"),
            ],
            className="student-detail-head",
        ),
        html.P(tr(lang, "followups.update_sub") if is_update else tr(lang, "followups.edit_sub"), className="student-detail-sub"),
        dcc.Dropdown(
            period_options(),
            (None if is_update else record.get("periodo")) or max(history.periodo_academico),
            id="edit-followup-period",
            clearable=False,
            className="filter",
        ),
        dcc.Textarea(
            id="edit-followup-note",
            value="" if is_update else (record.get("nota") or ""),
            placeholder=tr(lang, "followups.note_ph"),
            className="textarea",
        ),
        dcc.Input(
            id="edit-followup-action",
            value="" if is_update else (record.get("proxima_accion") or ""),
            placeholder=tr(lang, "followups.action_ph"),
            className="search-input",
        ),
        dcc.Input(
            id="edit-followup-date",
            type="date",
            value=None if is_update else _to_iso_date(record.get("fecha_proxima_accion")),
            min=min_date,
            max=max_date,
            className="search-input",
        ),
    ]


def followup_delete_modal(lang, record):
    """Confirmación explícita antes de eliminar un seguimiento."""
    student_id = (record or {}).get("estudiante_id") or "—"
    return [
        html.H2(tr(lang, "followups.delete_title")),
        html.P(tr(lang, "followups.delete_text")),
        html.P(
            [
                tr(lang, "followups.delete_target"),
                html.B(student_id, id="followup-delete-target"),
            ],
            className="followup-delete-target",
        ),
        html.P(tr(lang, "followups.delete_warning"), className="followup-delete-warning"),
    ]


def followups_page(lang, dark, profile, dismissed_demo=False):
    records = read_followups()
    if not records:
        return [
            page_heading(
                lang,
                tr(lang, "followups.title"),
                tr(lang, "followups.subtitle"),
            ),
            demo_banner(lang, dismissed_demo),
            html.Div(
                [
                    html.Div("▣", className="empty-icon"),
                    html.H2(tr(lang, "followups.empty_title")),
                    html.P(tr(lang, "followups.empty_text")),
                ],
                className="empty-state",
            ),
        ]
    return [
        page_heading(
            lang,
            tr(lang, "followups.title"),
            tr(lang, "followups.subtitle_full"),
        ),
        demo_banner(lang, dismissed_demo),
        html.Div(
            [
                html.Div(
                    [html.H2(tr(lang, "followups.cases")), html.P(tr(lang, "followups.cases_sub"))],
                    className="card-head",
                ),
                followups_table(records, lang, dark),
            ],
            className="card table-card",
        ),
    ]


def reports_page(values, lang, dark, dismissed_demo=False):
    theme = chart_palette(dark)
    df = latest_view(values).copy()
    status = df.estado_final.value_counts().reindex(["ACTIVO", "GRADUADO", "DESERTOR"], fill_value=0).reset_index()
    status.columns = ["estado_final", "cantidad"]
    status["etiqueta"] = status.estado_final.map(lambda x: final_label(lang, x))
    donut = px.pie(
        status,
        names="etiqueta",
        values="cantidad",
        hole=0.62,
        color="etiqueta",
        color_discrete_map={
            final_label(lang, "ACTIVO"): "#153DDA",
            final_label(lang, "GRADUADO"): "#009664",
            final_label(lang, "DESERTOR"): "#E3545B",
        },
    )
    donut.update_layout(
        height=220,
        margin=dict(l=0, r=0, t=0, b=0),
        showlegend=True,
        paper_bgcolor=theme["paper"],
        font=dict(size=10, color=theme["font"]),
    )
    averages = history.groupby("periodo_academico", as_index=False).promedio_ponderado_acumulado.mean().tail(6)
    averages["periodo"] = averages.periodo_academico.map(period_label)
    line = px.line(averages, x="periodo", y="promedio_ponderado_acumulado", markers=True)
    line.update_traces(line_color="#31B8CD")
    line.update_layout(
        height=220,
        margin=dict(l=0, r=0, t=0, b=0),
        paper_bgcolor=theme["paper"],
        plot_bgcolor=theme["plot"],
        yaxis_title=None,
        xaxis_title=None,
        font=dict(color=theme["font"]),
    )
    line.update_xaxes(gridcolor=theme["grid"], zeroline=False)
    line.update_yaxes(gridcolor=theme["grid"], zeroline=False)
    return [
        page_heading(
            lang,
            tr(lang, "reports.title"),
            tr(lang, "reports.subtitle"),
            action_button(tr(lang, "export.summary"), "export-btn"),
        ),
        demo_banner(lang, dismissed_demo),
        html.Div(
            [
                html.H2(tr(lang, "reports.prepare")),
                html.P(tr(lang, "reports.prepare_sub")),
                html.Div(
                    [
                        dcc.Dropdown(period_options(), max(history.periodo_academico), id="report-period", clearable=False, className="filter"),
                        dcc.Dropdown(
                            [{"label": tr(lang, "all.programs"), "value": "Todos"}]
                            + [{"label": x, "value": x} for x in options_from("programa")],
                            "Todos",
                            id="report-program",
                            clearable=False,
                            className="filter",
                        ),
                        dcc.Dropdown(
                            [{"label": "CSV", "value": "csv"}, {"label": "XLSX", "value": "xlsx"}],
                            "csv",
                            id="report-format",
                            clearable=False,
                            className="filter",
                        ),
                        action_button(tr(lang, "action.generate"), "generate-report", True),
                    ],
                    className="report-controls",
                ),
            ],
            className="card report-builder",
        ),
        html.H2(tr(lang, "reports.summary"), className="section-title"),
        html.Div(
            [
                kpi(tr(lang, "students.analyzed"), fmt_int(len(df), lang), tr(lang, "reports.by_filters"), "blue"),
                kpi(tr(lang, "indicator.high"), fmt_int((df.riesgo == "Alto").sum(), lang), tr(lang, "indicator.high_short"), "red"),
                kpi(tr(lang, "indicator.medium"), fmt_int((df.riesgo == "Medio").sum(), lang), tr(lang, "indicator.medium_short"), "amber"),
                kpi(tr(lang, "indicator.low"), fmt_int((df.riesgo == "Bajo").sum(), lang), tr(lang, "indicator.low_short"), "green"),
            ],
            className="kpi-grid four",
        ),
        html.Div(
            [
                html.Div(
                    [html.H2(tr(lang, "reports.analysis")), html.P(tr(lang, "reports.analysis_sub"))],
                    className="card-head",
                ),
                html.Div(
                    [
                        html.Div(
                            [html.H3(tr(lang, "reports.final_status")), dcc.Graph(figure=donut, config={"displayModeBar": False})],
                            className="report-chart",
                        ),
                        html.Div(
                            [html.H3(tr(lang, "reports.average")), dcc.Graph(figure=line, config={"displayModeBar": False})],
                            className="report-chart",
                        ),
                    ],
                    className="report-chart-grid",
                ),
                html.P(tr(lang, "reports.note"), className="chart-note"),
            ],
            className="card report-analysis",
        ),
    ]


def profile_page(lang, dark, profile):
    name = profile.get("name") or "Camila"
    description = profile.get("description") or ""

    def detail(label, value):
        return html.Div(
            [
                html.Div(label, className="profile-detail-label"),
                html.Div(value or "—", className="profile-detail-value"),
            ]
        )

    return [
        page_heading(lang, tr(lang, "profile.title"), tr(lang, "profile.subtitle")),
        html.Div(
            [
                html.Div(
                    [html.H2(tr(lang, "profile.info")), html.P(tr(lang, "profile.info_sub"))],
                    className="card-head",
                ),
                html.Div(
                    [
                        html.Div(initials(name), className="profile-avatar"),
                        html.Div(
                            [
                                html.Div(name, className="profile-name"),
                                html.Div(tr(lang, "role.admin"), className="profile-role"),
                                html.Div(profile.get("email") or "", className="profile-email"),
                            ],
                            className="profile-identity",
                        ),
                        dcc.Link(
                            [icon("pencil", "#ffffff", 16), html.Span(tr(lang, "profile.edit"))],
                            href="/perfil/editar",
                            className="button primary profile-edit-btn",
                        ),
                    ],
                    className="profile-card-row",
                ),
                html.Div(
                    [
                        detail(tr(lang, "profile.name"), name),
                        detail(tr(lang, "profile.email"), profile.get("email")),
                        detail(tr(lang, "profile.role"), tr(lang, "role.admin")),
                        detail(tr(lang, "profile.description"), description),
                    ],
                    className="profile-details",
                ),
            ],
            className="card profile-card",
        ),
    ]


def profile_edit_page(lang, dark, profile):
    name = profile.get("name") or "Camila"
    ink = "#A9B7CC" if dark else "#5B6576"
    accent = "#7FA6FF" if dark else "#153DDA"
    return [
        html.Div(
            [
                dcc.Link(tr(lang, "profile.title"), href="/perfil", className="breadcrumb-link"),
                html.Span("/", className="breadcrumb-sep"),
                html.Span(tr(lang, "profile.edit_title"), className="breadcrumb-current"),
            ],
            className="breadcrumb",
        ),
        html.Div(
            [html.H1(tr(lang, "profile.edit_title")), html.P(tr(lang, "profile.edit_sub"))],
            className="heading-copy edit-heading",
        ),
        html.Div(
            [
                html.Div(
                    [
                        html.Div(
                            [
                                html.Div(initials(name), className="profile-avatar large"),
                                html.Span(
                                    [icon("camera", accent, 15), html.Span(tr(lang, "profile.change_photo"))],
                                    className="profile-photo-link",
                                ),
                            ],
                            className="profile-edit-aside",
                        ),
                        html.Div(
                            [
                                html.Div(
                                    [icon("chevron", ink, 16), html.H2(tr(lang, "profile.general"))],
                                    className="profile-section-title",
                                ),
                                html.Label(tr(lang, "profile.name"), htmlFor="profile-name", className="login-label"),
                                dcc.Input(id="profile-name", value=name, className="login-input profile-input"),
                                html.Label(tr(lang, "profile.email"), htmlFor="profile-email", className="login-label"),
                                dcc.Input(id="profile-email", value=profile.get("email") or "", className="login-input profile-input"),
                                html.Label(tr(lang, "profile.role"), htmlFor="profile-role", className="login-label"),
                                dcc.Input(
                                    id="profile-role",
                                    value=tr(lang, "role.admin"),
                                    disabled=True,
                                    className="login-input profile-input profile-input-disabled",
                                ),
                                html.Label(tr(lang, "profile.description"), htmlFor="profile-description", className="login-label"),
                                dcc.Textarea(
                                    id="profile-description",
                                    value=profile.get("description") or "",
                                    className="textarea profile-textarea",
                                ),
                                html.Div(id="profile-message", className="form-message"),
                            ],
                            className="profile-edit-main",
                        ),
                    ],
                    className="profile-edit-body",
                ),
                html.Div(
                    [
                        dcc.Link(tr(lang, "action.cancel"), href="/perfil", className="button"),
                        html.Button(tr(lang, "profile.save"), id="profile-save", className="button primary", n_clicks=0),
                    ],
                    className="profile-edit-actions",
                ),
            ],
            className="card profile-edit-card",
        ),
    ]


# === LOGIN ===


def eye_icon(open_eye=True, color="#98A2B3"):
    if open_eye:
        inner = '<path d="M2.2 12S5.8 5.8 12 5.8 21.8 12 21.8 12 18.2 18.2 12 18.2 2.2 12 2.2 12Z"/><circle cx="12" cy="12" r="3.1"/>'
    else:
        inner = '<path d="M3 3l18 18"/><path d="M10.4 6.1A10.6 10.6 0 0 1 12 6c6.2 0 9.8 6 9.8 6a17.9 17.9 0 0 1-3.3 3.9M6.6 7.9A18.4 18.4 0 0 0 2.2 12s3.6 6 9.8 6a9.9 9.9 0 0 0 3.4-.6"/>'
    svg = (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" '
        f'fill="none" stroke="{color}" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round">{inner}</svg>'
    )
    return html.Img(src="data:image/svg+xml;utf8," + quote(svg), className="login-eye-svg", alt="")


def login_page(lang):
    return html.Div(
        [
            html.Section(
                [
                    html.Div(
                        [
                            html.Img(src="/assets/logo2.png", alt="UTB", style={"height": "40px", "objectFit": "contain"}),
                            html.Div(className="login-logo-divider"),
                            html.Div(tr(lang, "login.product"), className="login-logo-product"),
                        ],
                        className="login-logo",
                    ),
                    html.Div(
                        [
                            html.Div(tr(lang, "login.hero_eyebrow"), className="login-hero-eyebrow"),
                            html.H2(
                                [tr(lang, "login.hero_title_1"), html.Br(), tr(lang, "login.hero_title_2")],
                                className="login-hero-title",
                            ),
                            html.P(tr(lang, "login.hero_text"), className="login-hero-text"),
                        ],
                        className="login-hero",
                    ),
                    html.Div(
                        [
                            html.Span(tr(lang, "login.footer_left")),
                            html.Span(tr(lang, "login.footer_right")),
                        ],
                        className="login-hero-footer",
                    ),
                ],
                className="login-visual",
            ),
            html.Section(
                [
                    html.Div(
                        [
                            html.Div(tr(lang, "login.portal"), className="login-eyebrow"),
                            html.H1(tr(lang, "login.title"), className="login-title"),
                            html.P(tr(lang, "login.subtitle"), className="login-subtitle"),
                            html.Div(
                                [
                                    html.Label(tr(lang, "login.user"), htmlFor="login-user", className="login-label"),
                                    dcc.Input(
                                        id="login-user",
                                        type="text",
                                        value="bienestar@utb.edu.co",
                                        placeholder="usuario@utb.edu.co",
                                        className="login-input login-user-input",
                                        autoComplete="username",
                                    ),
                                    html.Label(tr(lang, "login.password"), htmlFor="login-pass", className="login-label"),
                                    html.Div(
                                        [
                                            dcc.Input(
                                                id="login-pass",
                                                type="password",
                                                value="demo",
                                                placeholder="••••••••",
                                                className="login-input",
                                                autoComplete="current-password",
                                            ),
                                            html.Button(
                                                eye_icon(),
                                                id="login-toggle-pass",
                                                className="login-eye",
                                                type="button",
                                                title=tr(lang, "login.show_password"),
                                                n_clicks=0,
                                                **{"aria-label": tr(lang, "login.show_password")},
                                            ),
                                        ],
                                        className="login-pass-wrap",
                                    ),
                                    html.Div(
                                        [
                                            dcc.Checklist(
                                                options=[{"label": tr(lang, "login.remember"), "value": "recordar"}],
                                                value=["recordar"],
                                                id="login-remember",
                                                className="login-remember",
                                            ),
                                            html.A(
                                                tr(lang, "login.forgot"),
                                                href="mailto:soporte@utb.edu.co?subject=Restablecer%20contrase%C3%B1a",
                                                className="login-link",
                                            ),
                                        ],
                                        className="login-options",
                                    ),
                                    html.Button(
                                        tr(lang, "login.submit"),
                                        id="login-button",
                                        className="login-submit",
                                        type="button",
                                        n_clicks=0,
                                    ),
                                    html.Div(
                                        [
                                            html.Span("i", className="login-note-icon"),
                                            html.Span(tr(lang, "login.demo_note")),
                                        ],
                                        className="login-note",
                                    ),
                                    html.Div(id="login-error", className="login-error"),
                                    html.Div(
                                        [
                                            tr(lang, "login.help"),
                                            html.A("soporte@utb.edu.co", href="mailto:soporte@utb.edu.co"),
                                            " · ",
                                            html.A("+57 605 693 1919", href="tel:+576056931919"),
                                        ],
                                        className="login-help",
                                    ),
                                    html.Button(
                                        [tr(lang, "login.demo_link"), html.Span("→", className="login-demo-arrow")],
                                        id="login-demo",
                                        className="login-demo",
                                        type="button",
                                        n_clicks=0,
                                    ),
                                ],
                                className="login-form",
                            ),
                            html.Div(
                                [
                                    html.Span(tr(lang, "login.copyright")),
                                    html.A(tr(lang, "login.legal"), href="#", className="login-footer-link"),
                                ],
                                className="login-footer",
                            ),
                        ],
                        className="login-form-wrap",
                    ),
                ],
                className="login-panel",
            ),
            menu_anchors(),
        ],
        className="login-page",
    )


def menu_anchors():
    """Anclas ocultas para que los callbacks del menú existan también en el login."""
    return html.Div(
        [
            html.Button(id="user-menu-toggle", n_clicks=0),
            html.Div(id="user-dropdown"),
            html.Div(id="menu-backdrop", n_clicks=0),
            html.Button(id="menu-profile", n_clicks=0),
            html.Button(id="menu-lang-es", n_clicks=0),
            html.Button(id="menu-lang-en", n_clicks=0),
            html.Button(id="menu-theme-light", n_clicks=0),
            html.Button(id="menu-theme-dark", n_clicks=0),
            html.Button(id="menu-logout", n_clicks=0),
        ],
        className="menu-anchors",
    )


def modal(content, modal_id):
    return html.Div([html.Div(content, className="modal-card")], id=modal_id, className="modal hidden")


app.layout = html.Div(
    [
        dcc.Location(id="url", refresh=False),
        dcc.Store(id="auth", storage_type="session"),
        dcc.Store(id="prefs", storage_type="local", data=DEFAULT_PREFS),
        dcc.Store(id="profile", storage_type="local", data=DEFAULT_PROFILE),
        dcc.Store(id="menu-open", data=False),
        dcc.Store(id="filters", data={}),
        dcc.Store(id="report-format-store", data="csv"),
        dcc.Store(id="selected-student"),
        dcc.Store(id="selected-followup"),
        dcc.Store(id="edit-followup"),
        dcc.Store(id="delete-followup"),
        dcc.Store(id="followups-version", data=0),
        dcc.Store(id="demo-dismissed", data=False, storage_type="session"),
        html.Div(id="root", children=login_page("es")),
        html.Div(
            html.Div(
                student_detail_modal("es", EMPTY_DETAIL),
                id="student-detail-body",
                className="modal-card student-detail-card",
                tabIndex="-1",
            ),
            id="student-detail-modal",
            className="modal hidden",
            role="dialog",
            **{"aria-modal": "true", "aria-labelledby": "student-detail-title"},
        ),
        # Detalle de solo lectura del seguimiento (se abre al pulsar el ID).
        html.Div(
            html.Div(
                followup_detail_modal("es", {}),
                id="followup-detail-body",
                className="modal-card followup-detail-card",
                tabIndex="-1",
            ),
            id="followup-detail-modal",
            className="modal hidden",
            role="dialog",
            **{"aria-modal": "true"},
        ),
        # Formulario de edición compartido por la tabla y el detalle.
        html.Div(
            html.Div(
                [
                    html.Div(id="followup-edit-body"),
                    html.Div(
                        [
                            html.Button(
                                tr("es", "action.cancel"),
                                id="close-followup-edit",
                                className="button",
                                n_clicks=0,
                                type="button",
                            ),
                            html.Button(
                                tr("es", "followups.save_changes"),
                                id="save-followup-edit",
                                className="button primary",
                                n_clicks=0,
                                type="button",
                            ),
                        ],
                        className="modal-actions",
                    ),
                ],
                className="modal-card followup-edit-card",
            ),
            id="followup-edit-modal",
            className="modal hidden",
            role="dialog",
            **{"aria-modal": "true"},
        ),
        # Confirmación de eliminación (nunca borra sin confirmar).
        html.Div(
            html.Div(
                [
                    html.Div(id="followup-delete-body"),
                    html.Div(
                        [
                            html.Button(
                                tr("es", "action.cancel"),
                                id="cancel-followup-delete",
                                className="button",
                                n_clicks=0,
                                type="button",
                            ),
                            html.Button(
                                tr("es", "followups.delete_confirm"),
                                id="confirm-followup-delete",
                                className="button primary followup-delete-confirm",
                                n_clicks=0,
                                type="button",
                            ),
                        ],
                        className="modal-actions",
                    ),
                ],
                className="modal-card followup-delete-card",
            ),
            id="followup-delete-modal",
            className="modal hidden",
            role="dialog",
            **{"aria-modal": "true"},
        ),
        html.Div(
            id="toast",
            className="toast",
            role="status",
            **{"aria-live": "polite"},
        ),
        dcc.Download(id="download"),
        dcc.Download(id="followup-history-download"),
    ],
    id="app",
    className="app theme-light",
)


@callback(
    Output("app", "className"),
    Input("prefs", "data"),
    Input("auth", "data"),
)
def apply_theme(prefs, auth):
    if not auth:
        return "app theme-light"
    theme = (prefs or DEFAULT_PREFS).get("theme", "light")
    return f"app theme-{theme}"


@callback(
    Output("root", "children"),
    Input("url", "pathname"),
    Input("auth", "data"),
    Input("filters", "data"),
    Input("prefs", "data"),
    Input("profile", "data"),
    Input("demo-dismissed", "data"),
    Input("followups-version", "data"),
)
def render(path, auth, values, prefs, profile, demo_dismissed, followups_version):
    prefs = {**DEFAULT_PREFS, **(prefs or {})}
    lang = prefs["lang"]
    dark = prefs["theme"] == "dark"
    profile = {**DEFAULT_PROFILE, **(profile or {})}
    if not auth:
        return login_page(lang)
    path = path or "/"
    dismissed_demo = bool(demo_dismissed)
    if path == "/estudiantes":
        content = students_page(values, lang, dark, dismissed_demo)
    elif path == "/alertas":
        content = alerts_page(values, lang, dark, dismissed_demo)
    elif path == "/seguimientos":
        content = followups_page(lang, dark, profile, dismissed_demo)
    elif path == "/reportes":
        content = reports_page(values, lang, dark, dismissed_demo)
    elif path == "/perfil":
        content = profile_page(lang, dark, profile)
    elif path == "/perfil/editar":
        content = profile_edit_page(lang, dark, profile)
    else:
        content = home_page(values, lang, dark, profile, dismissed_demo)
    return shell(path, content, lang, dark, profile)


@callback(
    Output("auth", "data"),
    Output("login-error", "children"),
    Input("login-button", "n_clicks"),
    Input("login-demo", "n_clicks"),
    Input("login-user", "n_submit"),
    Input("login-pass", "n_submit"),
    State("login-user", "value"),
    State("login-pass", "value"),
    State("prefs", "data"),
    prevent_initial_call=True,
)
def do_login(_, demo_clicks, user_submit, pass_submit, user, password, prefs):
    if not any([demo_clicks, user_submit, pass_submit, _]):
        raise PreventUpdate
    lang = (prefs or DEFAULT_PREFS).get("lang", "es")
    if dash.ctx.triggered_id == "login-demo":
        return DEMO_SESSION, ""
    if not (user or "").strip() or not (password or "").strip():
        return no_update, tr(lang, "login.error")
    return DEMO_SESSION, ""


@callback(
    Output("login-pass", "type"),
    Output("login-toggle-pass", "className"),
    Output("login-toggle-pass", "children"),
    Input("login-toggle-pass", "n_clicks"),
    prevent_initial_call=True,
)
def toggle_password_visibility(clicks):
    if not clicks:
        raise PreventUpdate
    visible = clicks % 2 == 1
    return (
        "text" if visible else "password",
        "login-eye visible" if visible else "login-eye",
        eye_icon(not visible, "#153DDA" if visible else "#98A2B3"),
    )


@callback(
    Output("prefs", "data"),
    Input("menu-lang-es", "n_clicks"),
    Input("menu-lang-en", "n_clicks"),
    Input("menu-theme-light", "n_clicks"),
    Input("menu-theme-dark", "n_clicks"),
    State("prefs", "data"),
    prevent_initial_call=True,
)
def update_prefs(_, __, ___, ____, prefs):
    if not any([_, __, ___, ____]):
        raise PreventUpdate
    prefs = {**DEFAULT_PREFS, **(prefs or {})}
    triggered = dash.ctx.triggered_id
    if triggered == "menu-lang-es":
        prefs["lang"] = "es"
    elif triggered == "menu-lang-en":
        prefs["lang"] = "en"
    elif triggered == "menu-theme-light":
        prefs["theme"] = "light"
    elif triggered == "menu-theme-dark":
        prefs["theme"] = "dark"
    return prefs


@callback(
    Output("menu-open", "data"),
    Input("user-menu-toggle", "n_clicks"),
    Input("menu-backdrop", "n_clicks"),
    Input("menu-profile", "n_clicks"),
    Input("menu-lang-es", "n_clicks"),
    Input("menu-lang-en", "n_clicks"),
    Input("menu-theme-light", "n_clicks"),
    Input("menu-theme-dark", "n_clicks"),
    Input("url", "pathname"),
    State("menu-open", "data"),
    prevent_initial_call=True,
)
def toggle_user_menu(toggle, backdrop, profile_click, lang_es, lang_en, theme_light, theme_dark, path, is_open):
    if dash.ctx.triggered_id == "user-menu-toggle":
        if not toggle:
            raise PreventUpdate
        return not is_open
    return False


@callback(
    Output("user-dropdown", "className"),
    Output("menu-backdrop", "className"),
    Input("menu-open", "data"),
)
def render_menu(is_open):
    return (
        "user-dropdown open" if is_open else "user-dropdown",
        "menu-backdrop open" if is_open else "menu-backdrop",
    )


@callback(
    Output("auth", "data", allow_duplicate=True),
    Output("url", "pathname", allow_duplicate=True),
    Input("menu-logout", "n_clicks"),
    prevent_initial_call=True,
)
def logout(_):
    if not _:
        raise PreventUpdate
    return None, "/"


@callback(
    Output("profile", "data"),
    Output("url", "pathname", allow_duplicate=True),
    Output("profile-message", "children"),
    Input("profile-save", "n_clicks"),
    State("profile-name", "value"),
    State("profile-email", "value"),
    State("profile-description", "value"),
    State("profile", "data"),
    State("prefs", "data"),
    prevent_initial_call=True,
)
def save_profile(_, name, email, description, profile, prefs):
    if not _:
        raise PreventUpdate
    lang = (prefs or DEFAULT_PREFS).get("lang", "es")
    if not (name or "").strip() or not (email or "").strip():
        return no_update, no_update, tr(lang, "profile.required")
    updated = {
        **DEFAULT_PROFILE,
        **(profile or {}),
        "name": name.strip(),
        "email": email.strip(),
        "description": (description or "").strip(),
    }
    return updated, "/perfil", ""


@callback(
    Output("filters", "data"),
    Input("global-programa", "value"),
    Input("global-periodo", "value"),
    Input("global-nivel", "value"),
    Input("global-academico", "value"),
    Input("global-riesgo", "value"),
    Input("global-final", "value"),
    State("filters", "data"),
    State("url", "pathname"),
    prevent_initial_call=True,
)
def update_filters(programa, periodo, nivel, academico, riesgo, final, current, path):
    current = current or {}
    new = {"programa": programa, "periodo": periodo, "nivel": nivel, "academico": academico, "riesgo": riesgo, "final": final}
    if (path or "").startswith("/estudiantes"):
        # En el directorio el riesgo es fijo (alto) y los filtros de estado no
        # existen: se conservan los valores globales para no contaminar Inicio.
        for key in ("riesgo", "academico", "final"):
            new[key] = current.get(key, "Todos")
    if current == new:
        raise PreventUpdate
    return new


@callback(
    Output("students-table", "data"),
    Input("student-search", "value"),
    State("filters", "data"),
    State("prefs", "data"),
    prevent_initial_call=True,
)
def search_students(term, values, prefs):
    if term is None:
        raise PreventUpdate
    lang = (prefs or DEFAULT_PREFS).get("lang", "es")
    df = latest_view(students_filters(values)).copy()
    if term:
        df = df[df.estudiante_id.str.contains(term.strip(), case=False, na=False)]
    follows = read_followups()
    df["acompanamiento"] = df.estudiante_id.map(lambda x: status_label(lang, followup_status(x, follows)))
    df["riesgo"] = df.riesgo.map(lambda x: risk_label(lang, x))
    df["senal_principal"] = df.senal_principal.map(lambda x: signal_label(lang, x))
    df["periodo_academico"] = df.periodo_academico.map(period_label)
    return (
        df[["estudiante_id", "programa", "nivel_actual", "riesgo", "senal_principal", "acompanamiento", "periodo_academico"]]
        .rename(
            columns={
                "estudiante_id": "estudiante",
                "nivel_actual": "nivel",
                "riesgo": "indicador",
                "senal_principal": "señal_principal",
                "periodo_academico": "periodo",
            }
        )
        .to_dict("records")
    )


@callback(
    Output("student-detail-modal", "className"),
    Output("student-detail-body", "children"),
    Output("selected-student", "data"),
    Output("students-table", "active_cell"),
    Output("toast", "className"),
    Output("toast", "children"),
    Input("students-table", "active_cell"),
    Input("close-student-detail", "n_clicks"),
    Input("save-student-followup", "n_clicks"),
    State("selected-student", "data"),
    State("students-table", "data"),
    State("student-detail-period", "value"),
    State("student-detail-note", "value"),
    State("student-detail-action", "value"),
    State("student-detail-date", "value"),
    State("profile", "data"),
    State("prefs", "data"),
    prevent_initial_call=True,
)
def toggle_student_detail(
    active_cell,
    close_clicks,
    save_clicks,
    student_id,
    table_data,
    period,
    note,
    action,
    next_date,
    profile,
    prefs,
):
    lang = (prefs or DEFAULT_PREFS).get("lang", "es")
    trigger = dash.ctx.triggered_id
    empty_body = student_detail_modal(lang, EMPTY_DETAIL)

    # Cancelar o Escape: cierra y deja el formulario limpio.
    if trigger == "close-student-detail":
        return "modal hidden", empty_body, no_update, None, no_update, no_update

    # Guardar seguimiento: sólo cierra si el guardado es correcto.
    if trigger == "save-student-followup":
        if not save_clicks:
            raise PreventUpdate
        if not student_id or not all([period, note, action, next_date]):
            return (no_update, no_update, no_update, no_update, *toast("error", tr(lang, "followups.msg_missing")))
        if student_id not in set(students.estudiante_id):
            return (no_update, no_update, no_update, no_update, *toast("error", tr(lang, "followups.msg_invalid")))
        if any(r.get("estudiante_id") == student_id for r in read_followups()):
            return (no_update, no_update, no_update, no_update, *toast("error", tr(lang, "followups.msg_exists")))
        try:
            next_date_value = date.fromisoformat(str(next_date)[:10])
        except (TypeError, ValueError):
            next_date_value = None
        today = date.today()
        if next_date_value is None or next_date_value < today or next_date_value > add_months(today, FOLLOWUP_MAX_MONTHS):
            return (no_update, no_update, no_update, no_update, *toast("error", tr(lang, "detail.msg_date_range")))
        responsible = (profile or DEFAULT_PROFILE).get("name") or "Camila"
        try:
            save_followup(student_id, period, responsible, note, action, next_date, "Nueva")
        except Exception:
            return (no_update, no_update, no_update, no_update, *toast("error", tr(lang, "followups.msg_error")))
        # Éxito: cierra, limpia el formulario y avisa con un toast temporal.
        return (
            "modal hidden",
            empty_body,
            no_update,
            None,
            *toast("success", tr(lang, "followups.msg_saved")),
        )

    if not active_cell or active_cell.get("column_id") != "estudiante":
        raise PreventUpdate
    rows = table_data or []
    index = active_cell.get("row")
    if index is None or index < 0 or index >= len(rows):
        raise PreventUpdate
    student_id = rows[index].get("estudiante")
    data = student_detail_data(student_id, lang)
    if not data:
        raise PreventUpdate
    return "modal", student_detail_modal(lang, data), student_id, no_update, no_update, no_update


def export_frame(df, fmt):
    if fmt == "xlsx":
        buf = io.BytesIO()
        df.to_excel(buf, index=False, engine="openpyxl")
        return dcc.send_bytes(buf.getvalue(), "alertas_tempranas.xlsx")
    return dcc.send_data_frame(df.to_csv, "alertas_tempranas.csv", index=False, encoding="utf-8-sig")


@callback(
    Output("download", "data"),
    Input("export-btn", "n_clicks"),
    State("url", "pathname"),
    State("filters", "data"),
    State("report-format-store", "data"),
    prevent_initial_call=True,
)
def export_any(clicks, path, values, fmt):
    if not clicks:
        raise PreventUpdate
    if (path or "").startswith("/estudiantes"):
        df = latest_view(students_filters(values)).copy()
    else:
        df = latest_view(values).copy()
        if (path or "").startswith("/alertas"):
            df = df[df.riesgo.isin(["Alto", "Medio"])]
    return export_frame(df, fmt or "csv")


@callback(
    Output("followup-history-download", "data"),
    Input("export-followup-history", "n_clicks"),
    State("selected-followup", "data"),
    State("prefs", "data"),
    prevent_initial_call=True,
)
def export_followup_history(clicks, selected_index, prefs):
    if not clicks or selected_index is None:
        raise PreventUpdate
    records = read_followups()
    if selected_index < 0 or selected_index >= len(records):
        raise PreventUpdate
    student_id = records[selected_index].get("estudiante_id")
    history_records = followup_history(student_id, records)
    lang = (prefs or DEFAULT_PREFS).get("lang", "es")
    labels = [
        tr(lang, "col.period"),
        tr(lang, "followups.note"),
        tr(lang, "col.next_action"),
        tr(lang, "followups.next_date"),
        tr(lang, "followups.created_at"),
        tr(lang, "followups.updated_at"),
    ]
    frame = pd.DataFrame([
        [
            r.get("periodo"), r.get("nota"), r.get("proxima_accion"),
            r.get("fecha_proxima_accion"), r.get("created_at"), r.get("updated_at"),
        ]
        for r in history_records
    ], columns=labels)
    buffer = io.BytesIO()
    frame.to_excel(buffer, index=False, engine="openpyxl")
    filename_date = date.today().isoformat()
    return dcc.send_bytes(buffer.getvalue(), f"seguimiento_{student_id}_{filename_date}.xlsx")


@callback(
    Output("report-format-store", "data"),
    Input("report-format", "value"),
    prevent_initial_call=True,
)
def store_report_format(value):
    return value or "csv"


@callback(
    Output("followup-detail-modal", "className"),
    Output("followup-detail-body", "children"),
    Output("selected-followup", "data"),
    Input({"type": "followup-open", "index": dash.ALL}, "n_clicks"),
    Input("close-followup-detail", "n_clicks"),
    State("prefs", "data"),
    prevent_initial_call=True,
)
def toggle_followup_detail(open_clicks, close_clicks, prefs):
    lang = (prefs or DEFAULT_PREFS).get("lang", "es")
    trigger = dash.ctx.triggered_id
    if trigger == "close-followup-detail":
        if not close_clicks:
            raise PreventUpdate
        # Se conserva el cuerpo (oculto) para que los botones Cerrar/Editar
        # sigan existiendo como Inputs del callback y no se rompa el layout.
        return "modal hidden", no_update, None
    if isinstance(trigger, dict) and trigger.get("type") == "followup-open":
        index = trigger.get("index")
        if not dash.ctx.triggered or not dash.ctx.triggered[0].get("value"):
            raise PreventUpdate
        records = read_followups()
        if index is None or index < 0 or index >= len(records):
            raise PreventUpdate
        return "modal", followup_detail_modal(lang, records[index]), index
    raise PreventUpdate


@callback(
    Output("followup-edit-modal", "className"),
    Output("followup-edit-body", "children"),
    Output("edit-followup", "data"),
    Input({"type": "followup-edit", "index": dash.ALL}, "n_clicks"),
    Input({"type": "followup-update", "index": dash.ALL}, "n_clicks"),
    Input("edit-followup-detail", "n_clicks"),
    Input("update-followup-detail", "n_clicks"),
    Input("close-followup-edit", "n_clicks"),
    State("selected-followup", "data"),
    State("prefs", "data"),
    prevent_initial_call=True,
)
def open_followup_edit(table_clicks, update_clicks, detail_clicks, update_detail_clicks, close_clicks, selected_index, prefs):
    lang = (prefs or DEFAULT_PREFS).get("lang", "es")
    trigger = dash.ctx.triggered_id
    if trigger == "close-followup-edit":
        return "modal hidden", no_update, None
    is_update = False
    if trigger == "update-followup-detail":
        if not update_detail_clicks:
            raise PreventUpdate
        index = selected_index
        source = "detail"
        is_update = True
    elif trigger == "edit-followup-detail":
        if not detail_clicks:
            raise PreventUpdate
        index = selected_index
        source = "detail"
    elif isinstance(trigger, dict) and trigger.get("type") in ("followup-edit", "followup-update"):
        index = trigger.get("index")
        if not dash.ctx.triggered or not dash.ctx.triggered[0].get("value"):
            raise PreventUpdate
        source = "table"
        is_update = trigger.get("type") == "followup-update"
    else:
        raise PreventUpdate
    records = read_followups()
    if index is None or index < 0 or index >= len(records):
        raise PreventUpdate
    return "modal", followup_edit_modal(lang, records[index], is_update), {"index": index, "source": source, "is_update": is_update}


@callback(
    Output("followup-edit-modal", "className", allow_duplicate=True),
    Output("followup-detail-body", "children", allow_duplicate=True),
    Output("followups-version", "data", allow_duplicate=True),
    Output("selected-followup", "data", allow_duplicate=True),
    Output("toast", "className", allow_duplicate=True),
    Output("toast", "children", allow_duplicate=True),
    Input("save-followup-edit", "n_clicks"),
    State("edit-followup-period", "value"),
    State("edit-followup-note", "value"),
    State("edit-followup-action", "value"),
    State("edit-followup-date", "value"),
    State("edit-followup", "data"),
    State("prefs", "data"),
    State("followups-version", "data"),
    prevent_initial_call=True,
)
def save_followup_edit(_, period, note, action, next_date, edit_state, prefs, version):
    if not _:
        raise PreventUpdate
    lang = (prefs or DEFAULT_PREFS).get("lang", "es")
    edit_state = edit_state or {}
    index = edit_state.get("index")
    if index is None:
        return no_update, no_update, no_update, no_update, *toast("error", tr(lang, "followups.msg_update_error"))
    if not all([period, note, action, next_date]):
        return no_update, no_update, no_update, no_update, *toast("error", tr(lang, "followups.msg_missing"))
    try:
        next_date_value = date.fromisoformat(str(next_date)[:10])
    except (TypeError, ValueError):
        next_date_value = None
    today = date.today()
    if next_date_value is None or next_date_value < today or next_date_value > add_months(today, FOLLOWUP_MAX_MONTHS):
        return no_update, no_update, no_update, no_update, *toast("error", tr(lang, "detail.msg_date_range"))
    try:
        if edit_state.get("is_update"):
            previous = read_followups()[index]
            updated = create_followup_update(
                index, period, previous.get("responsable") or (prefs or DEFAULT_PROFILE).get("name") or "Camila",
                note, action, next_date, previous.get("estado") or "Nueva",
            )
        else:
            updated = update_followup(index, period, note, action, next_date)
    except Exception:
        return no_update, no_update, no_update, no_update, *toast("error", tr(lang, "followups.msg_update_error"))
    # Si la edición se abrió desde el detalle, se vuelve al detalle ya
    # actualizado. Si se abrió desde la tabla, todo se cierra y la tabla
    # se refresca mediante followups-version.
    detail_body = followup_detail_modal(lang, updated) if edit_state.get("source") == "detail" else no_update
    return (
        "modal hidden",
        detail_body,
        (version or 0) + 1,
        len(read_followups()) - 1 if edit_state.get("is_update") and edit_state.get("source") == "detail" else no_update,
        *toast("success", tr(lang, "followups.msg_updated")),
    )


@callback(
    Output("followup-delete-modal", "className"),
    Output("followup-delete-body", "children"),
    Output("delete-followup", "data"),
    Output("followups-version", "data", allow_duplicate=True),
    Output("toast", "className", allow_duplicate=True),
    Output("toast", "children", allow_duplicate=True),
    Input({"type": "followup-delete", "index": dash.ALL}, "n_clicks"),
    Input("cancel-followup-delete", "n_clicks"),
    Input("confirm-followup-delete", "n_clicks"),
    State("delete-followup", "data"),
    State("prefs", "data"),
    State("followups-version", "data"),
    prevent_initial_call=True,
)
def manage_followup_delete(table_clicks, cancel_clicks, confirm_clicks, delete_index, prefs, version):
    lang = (prefs or DEFAULT_PREFS).get("lang", "es")
    trigger = dash.ctx.triggered_id
    if trigger == "cancel-followup-delete":
        return "modal hidden", no_update, None, no_update, no_update, no_update
    if isinstance(trigger, dict) and trigger.get("type") == "followup-delete":
        index = trigger.get("index")
        if not dash.ctx.triggered or not dash.ctx.triggered[0].get("value"):
            raise PreventUpdate
        records = read_followups()
        if index is None or index < 0 or index >= len(records):
            raise PreventUpdate
        return "modal", followup_delete_modal(lang, records[index]), index, no_update, no_update, no_update
    if trigger == "confirm-followup-delete":
        if not confirm_clicks or delete_index is None:
            raise PreventUpdate
        try:
            delete_followup(delete_index)
        except Exception:
            return no_update, no_update, no_update, no_update, *toast("error", tr(lang, "followups.msg_delete_error"))
        return (
            "modal hidden",
            no_update,
            None,
            (version or 0) + 1,
            *toast("success", tr(lang, "followups.msg_deleted")),
        )
    raise PreventUpdate


if __name__ == "__main__":
    app.run(debug=False, host="127.0.0.1", port=8050)

@callback(
    Output("url", "pathname", allow_duplicate=True),
    Output("filters", "data", allow_duplicate=True),
    Input("critical-alert-banner", "n_clicks"),
    State("filters", "data"),
    prevent_initial_call=True,
)
def on_critical_alert_click(clicks, current_filters):
    if not clicks:
        raise PreventUpdate
    # El directorio ya muestra solo riesgo alto: no se contamina el filtro global.
    return "/estudiantes", no_update


@callback(
    Output("demo-dismissed", "data"),
    Input("dismiss-demo-btn", "n_clicks"),
    prevent_initial_call=True,
)
def dismiss_demo_banner(clicks):
    if not clicks:
        raise PreventUpdate
    return True
