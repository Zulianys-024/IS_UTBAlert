from __future__ import annotations

import io
import json
from urllib.parse import quote

import dash
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dash import Dash, Input, Output, State, callback, dash_table, dcc, html, no_update
from dash.exceptions import PreventUpdate

from utbapp.data_access import (
    followup_status,
    latest_by_student,
    load_data,
    period_label,
    read_followups,
    save_followup,
)
from utbapp.i18n import (
    LANG_NAMES,
    final_label,
    fmt_int,
    fmt_pct,
    risk_label,
    signal_label,
    status_label,
    tr,
)

app = Dash(__name__, suppress_callback_exceptions=True, title="Alertas Tempranas · UTB")
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
                    {"path": "/variables", "title": "Variables de riesgo"},
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
    ("nav.students", "/estudiantes", "♧"),
    ("nav.variables", "/variables", "☷"),
    ("nav.alerts", "/alertas", "♧"),
    ("nav.followups", "/seguimientos", "▣"),
    ("nav.reports", "/reportes", "▥"),
]
DEFAULT_PREFS = {"lang": "es", "theme": "light"}
DEFAULT_PROFILE = {"name": "Camila", "email": "camila@utb.edu.co", "role": "admin", "description": ""}
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


def demo_banner(lang):
    return html.Div(
        [
            html.Span("ⓘ", className="info-symbol"),
            html.B(tr(lang, "demo.title")),
            tr(lang, "demo.text"),
            html.Span(tr(lang, "demo.action"), className="banner-action"),
        ],
        className="demo-banner",
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
    return html.Div(
        [
            html.Div(
                [
                    html.Div(tr(lang, "eyebrow"), className="eyebrow"),
                    html.H1(title),
                    html.P(subtitle),
                ],
                className="heading-copy",
            ),
            action,
        ],
        className="page-heading",
    )


def action_button(label, id=None, primary=False):
    class_name = f"button {'primary' if primary else ''}".strip()
    if id is None:
        return html.Button(label, className=class_name)
    return html.Button(label, id=id, className=class_name, n_clicks=0)


def filter_bar(values, lang):
    values = values or {}

    def opts(items, all_key, labeler=None):
        lab = labeler or (lambda x: str(x))
        return [{"label": tr(lang, all_key), "value": "Todos"}] + [
            {"label": lab(x), "value": str(x)} for x in items
        ]

    return html.Div(
        [
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
        ],
        className="filter-bar",
    )


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
        tickpad=10,
    )
    fig.update_yaxes(gridcolor=theme["grid"], zeroline=False)
    return fig


# === PAGES ===


def home_page(values, lang, dark, profile):
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
        demo_banner(lang),
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
        html.Div(
            [
                icon_box("▧", "blue"),
                html.Div([html.B(tr(lang, "home.report")), html.P(tr(lang, "home.report_sub"))]),
                html.Span("→", className="arrow"),
            ],
            className="report-cta",
        ),
    ]


def students_page(values, lang, dark):
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
            tr(lang, "students.subtitle"),
            action_button(tr(lang, "export.directory"), "export-btn"),
        ),
        demo_banner(lang),
        filter_bar(values, lang),
        html.Div(
            [
                kpi(tr(lang, "students.analyzed"), fmt_int(len(df), lang), tr(lang, "students.by_filters"), "blue"),
                kpi(
                    tr(lang, "indicator.high"),
                    fmt_int((df.riesgo == "Alto").sum(), lang),
                    tr(lang, "pct.of_total", pct=fmt_pct((df.riesgo == "Alto").mean() * 100 if len(df) else 0, lang)),
                    "red",
                ),
                kpi(
                    tr(lang, "indicator.medium"),
                    fmt_int((df.riesgo == "Medio").sum(), lang),
                    tr(lang, "pct.of_total", pct=fmt_pct((df.riesgo == "Medio").mean() * 100 if len(df) else 0, lang)),
                    "amber",
                ),
                kpi(
                    tr(lang, "indicator.low"),
                    fmt_int((df.riesgo == "Bajo").sum(), lang),
                    tr(lang, "pct.of_total", pct=fmt_pct((df.riesgo == "Bajo").mean() * 100 if len(df) else 0, lang)),
                    "green",
                ),
            ],
            className="kpi-grid four",
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
                    row_selectable="single",
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
        ),
    ]


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


def alerts_page(values, lang, dark):
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
        demo_banner(lang),
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


def followups_page(lang, dark, profile):
    records = read_followups()
    followup_form = html.Div(
        [
            html.Div(
                [
                    html.H2(tr(lang, "followups.form_title")),
                    html.P(tr(lang, "followups.form_sub")),
                    dcc.Input(id="followup-student", placeholder=tr(lang, "followups.student_ph"), className="search-input"),
                    dcc.Dropdown(period_options(), max(history.periodo_academico), id="followup-period", clearable=False, className="filter"),
                    dcc.Textarea(id="followup-note", placeholder=tr(lang, "followups.note_ph"), className="textarea"),
                    dcc.Input(id="followup-action", placeholder=tr(lang, "followups.action_ph"), className="search-input"),
                    dcc.Input(id="followup-date", type="date", className="search-input"),
                    html.Div(
                        [
                            html.Button(tr(lang, "action.cancel"), id="close-followup", className="button", n_clicks=0),
                            html.Button(tr(lang, "action.save_followup"), id="save-followup", className="button primary", n_clicks=0),
                        ],
                        className="modal-actions",
                    ),
                    html.Div(id="followup-message", className="form-message"),
                ],
                className="modal-card",
            )
        ],
        id="followup-modal",
        className="modal hidden",
    )
    if not records:
        return [
            page_heading(
                lang,
                tr(lang, "followups.title"),
                tr(lang, "followups.subtitle"),
                action_button(tr(lang, "action.register_followup"), "open-followup"),
            ),
            demo_banner(lang),
            html.Div(
                [
                    html.Div("▣", className="empty-icon"),
                    html.H2(tr(lang, "followups.empty_title")),
                    html.P(tr(lang, "followups.empty_text")),
                ],
                className="empty-state",
            ),
            followup_form,
        ]
    rows = [
        {
            "estudiante": r["estudiante_id"],
            "responsable": r["responsable"],
            "proxima_accion": r["proxima_accion"],
            "periodo": period_label(r["periodo"]),
            "estado": status_label(lang, r["estado"]),
        }
        for r in records
    ]
    return [
        page_heading(
            lang,
            tr(lang, "followups.title"),
            tr(lang, "followups.subtitle_full"),
            action_button(tr(lang, "action.register_followup"), "open-followup"),
        ),
        demo_banner(lang),
        html.Div(
            [
                html.Div(
                    [html.H2(tr(lang, "followups.cases")), html.P(tr(lang, "followups.cases_sub"))],
                    className="card-head",
                ),
                small_table(
                    rows,
                    [
                        (tr(lang, "col.student"), "estudiante"),
                        (tr(lang, "col.responsible"), "responsable"),
                        (tr(lang, "col.next_action"), "proxima_accion"),
                        (tr(lang, "col.period"), "periodo"),
                        (tr(lang, "col.status"), "estado"),
                    ],
                    dark,
                ),
            ],
            className="card table-card",
        ),
        followup_form,
    ]


def reports_page(values, lang, dark):
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
        demo_banner(lang),
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
        html.Div(id="root", children=login_page("es")),
        dcc.Download(id="download"),
    ],
    id="app",
    className="app theme-light",
)


@callback(Output("app", "className"), Input("prefs", "data"))
def apply_theme(prefs):
    theme = (prefs or DEFAULT_PREFS).get("theme", "light")
    return f"app theme-{theme}"


@callback(
    Output("root", "children"),
    Input("url", "pathname"),
    Input("auth", "data"),
    Input("filters", "data"),
    Input("prefs", "data"),
    Input("profile", "data"),
)
def render(path, auth, values, prefs, profile):
    prefs = {**DEFAULT_PREFS, **(prefs or {})}
    lang = prefs["lang"]
    dark = prefs["theme"] == "dark"
    profile = {**DEFAULT_PROFILE, **(profile or {})}
    if not auth:
        return login_page(lang)
    path = path or "/"
    if path == "/estudiantes":
        content = students_page(values, lang, dark)
    elif path == "/variables":
        content = variables_page(lang, dark)
    elif path == "/alertas":
        content = alerts_page(values, lang, dark)
    elif path == "/seguimientos":
        content = followups_page(lang, dark, profile)
    elif path == "/reportes":
        content = reports_page(values, lang, dark)
    elif path == "/perfil":
        content = profile_page(lang, dark, profile)
    elif path == "/perfil/editar":
        content = profile_edit_page(lang, dark, profile)
    else:
        content = home_page(values, lang, dark, profile)
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
    prevent_initial_call=True,
)
def update_filters(programa, periodo, nivel, academico, riesgo, final, current):
    new = {"programa": programa, "periodo": periodo, "nivel": nivel, "academico": academico, "riesgo": riesgo, "final": final}
    if (current or {}) == new:
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
    df = latest_view(values).copy()
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
    df = latest_view(values).copy()
    if (path or "").startswith("/alertas"):
        df = df[df.riesgo.isin(["Alto", "Medio"])]
    return export_frame(df, fmt or "csv")


@callback(
    Output("report-format-store", "data"),
    Input("report-format", "value"),
    prevent_initial_call=True,
)
def store_report_format(value):
    return value or "csv"


@callback(
    Output("followup-modal", "className"),
    Input("open-followup", "n_clicks"),
    Input("close-followup", "n_clicks"),
    Input("save-followup", "n_clicks"),
    prevent_initial_call=True,
)
def toggle_followup_modal(open_clicks, close_clicks, save_clicks):
    if dash.ctx.triggered_id == "open-followup":
        if not open_clicks:
            raise PreventUpdate
        return "modal"
    return "modal hidden"


@callback(
    Output("followup-message", "children"),
    Input("save-followup", "n_clicks"),
    State("followup-student", "value"),
    State("followup-period", "value"),
    State("followup-note", "value"),
    State("followup-action", "value"),
    State("followup-date", "value"),
    State("profile", "data"),
    State("prefs", "data"),
    prevent_initial_call=True,
)
def create_followup(_, student_id, period, note, action, next_date, profile, prefs):
    if not _:
        raise PreventUpdate
    lang = (prefs or DEFAULT_PREFS).get("lang", "es")
    if not all([student_id, period, note, action, next_date]):
        return tr(lang, "followups.msg_missing")
    if student_id not in set(students.estudiante_id):
        return tr(lang, "followups.msg_invalid")
    responsible = (profile or DEFAULT_PROFILE).get("name") or "Camila"
    save_followup(student_id, period, responsible, note, action, next_date, "Nueva")
    return tr(lang, "followups.msg_saved")


if __name__ == "__main__":
    app.run(debug=False, host="127.0.0.1", port=8050)