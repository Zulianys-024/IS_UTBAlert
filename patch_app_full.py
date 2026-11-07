with open('app.py', 'r', encoding='utf-8') as f:
    text = f.read()

# 1. Update NAV to remove variables
old_nav = '''NAV = [
    ("nav.home", "/", "⌂"),
    ("nav.students", "/estudiantes", "ϙ"),
    ("nav.variables", "/variables", "☷"),
    ("nav.alerts", "/alertas", "◬"),
    ("nav.followups", "/seguimientos", "→"),
    ("nav.reports", "/reportes", "▥"),
]'''

new_nav = '''NAV = [
    ("nav.home", "/", "⌂"),
    ("nav.students", "/estudiantes", "ϙ"),
    ("nav.alerts", "/alertas", "◬"),
    ("nav.followups", "/seguimientos", "→"),
    ("nav.reports", "/reportes", "▥"),
]'''

assert old_nav in text, "old_nav not found"
text = text.replace(old_nav, new_nav, 1)

# 2. Update manus_routes
old_routes = '''                "routes": [
                    {"path": "/", "title": "Inicio"},
                    {"path": "/estudiantes", "title": "Estudiantes"},
                    {"path": "/variables", "title": "Variables de riesgo"},
                    {"path": "/alertas", "title": "Alertas"},
                    {"path": "/seguimientos", "title": "Seguimientos"},
                    {"path": "/reportes", "title": "Reportes"},
                    {"path": "/perfil", "title": "Mi perfil"},
                ]'''

new_routes = '''                "routes": [
                    {"path": "/", "title": "Inicio"},
                    {"path": "/estudiantes", "title": "Estudiantes"},
                    {"path": "/alertas", "title": "Alertas"},
                    {"path": "/seguimientos", "title": "Seguimientos"},
                    {"path": "/reportes", "title": "Reportes"},
                    {"path": "/perfil", "title": "Mi perfil"},
                ]'''

assert old_routes in text, "old_routes not found"
text = text.replace(old_routes, new_routes, 1)

# 3. Update demo_banner definition
old_demo = '''def demo_banner(lang):
    return html.Div(
        [
            html.Span("ⓘ", className="info-symbol"),
            html.B(tr(lang, "demo.title")),
            tr(lang, "demo.text"),
            html.Span(tr(lang, "demo.action"), className="banner-action"),
        ],
        className="demo-banner",
    )'''

new_demo = '''def demo_banner(lang, dismissed=False):
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
    )'''

assert old_demo in text, "old_demo not found"
text = text.replace(old_demo, new_demo, 1)

# 4. Helper function for variables catalog table
var_table_func = '''def variables_catalog_card(lang, dark):
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
'''

# 5. Update home_page to:
# - accept dismissed parameter
# - remove report-cta
# - insert variables_catalog_card under recent alerts
old_home_def = 'def home_page(values, lang, dark, profile):'
new_home_def = 'def home_page(values, lang, dark, profile, dismissed_demo=False):'
assert old_home_def in text, "old_home_def not found"
text = text.replace(old_home_def, new_home_def, 1)

old_home_demo = '''        critical_alert_banner(counts.get("Alto", 0), lang),
        demo_banner(lang),'''

new_home_demo = '''        critical_alert_banner(counts.get("Alto", 0), lang),
        demo_banner(lang, dismissed_demo),'''

assert old_home_demo in text, "old_home_demo not found"
text = text.replace(old_home_demo, new_home_demo, 1)

old_home_end = '''            className="card table-card",
        ),
        html.Div(
            [
                icon_box("▧", "blue"),
                html.Div([html.B(tr(lang, "home.report")), html.P(tr(lang, "home.report_sub"))]),
                html.Span("→", className="arrow"),
            ],
            className="report-cta",
        ),
    ]'''

new_home_end = '''            className="card table-card",
        ),
        variables_catalog_card(lang, dark),
    ]'''

assert old_home_end in text, "old_home_end not found"
text = text.replace(old_home_end, new_home_end, 1)

# Also update students_page, alerts_page, followups_page, reports_page to take dismissed_demo
text = text.replace('def students_page(values, lang, dark):', 'def students_page(values, lang, dark, dismissed_demo=False):')
text = text.replace('def alerts_page(values, lang, dark):', 'def alerts_page(values, lang, dark, dismissed_demo=False):')
text = text.replace('def followups_page(lang, dark, profile):', 'def followups_page(lang, dark, profile, dismissed_demo=False):')
text = text.replace('def reports_page(values, lang, dark):', 'def reports_page(values, lang, dark, dismissed_demo=False):')

# In those pages, replace demo_banner(lang) with demo_banner(lang, dismissed_demo)
# Note: home_page already handled above
text = text.replace('        demo_banner(lang),\n        filter_bar(values, lang),\n        html.Div(\n            [\n                kpi(tr(lang, "students.analyzed")', '        demo_banner(lang, dismissed_demo),\n        filter_bar(values, lang),\n        html.Div(\n            [\n                kpi(tr(lang, "students.analyzed")')
text = text.replace('        action_button(tr(lang, "export.alerts"), "export-btn"),\n        ),\n        demo_banner(lang),', '        action_button(tr(lang, "export.alerts"), "export-btn"),\n        ),\n        demo_banner(lang, dismissed_demo),')
text = text.replace('            action_button(tr(lang, "action.register_followup"), "open-followup"),\n            ),\n            demo_banner(lang),', '            action_button(tr(lang, "action.register_followup"), "open-followup"),\n            ),\n            demo_banner(lang, dismissed_demo),')
text = text.replace('            action_button(tr(lang, "action.register_followup"), "open-followup"),\n        ),\n        demo_banner(lang),', '            action_button(tr(lang, "action.register_followup"), "open-followup"),\n        ),\n        demo_banner(lang, dismissed_demo),')
text = text.replace('        action_button(tr(lang, "export.summary"), "export-btn"),\n        ),\n        demo_banner(lang),', '        action_button(tr(lang, "export.summary"), "export-btn"),\n        ),\n        demo_banner(lang, dismissed_demo),')

# 6. Insert variables_catalog_card definition before VARIABLES
var_anchor = 'VARIABLES = ['
assert var_anchor in text, "VARIABLES not found"
text = text.replace(var_anchor, var_table_func + '\n\n' + var_anchor, 1)

# 7. Update app.layout to include dcc.Store(id="demo-dismissed", data=False, storage_type="session")
old_layout_stores = '''        dcc.Store(id="filters", data={}),
        dcc.Store(id="report-format-store", data="csv"),
        dcc.Store(id="selected-student"),'''

new_layout_stores = '''        dcc.Store(id="filters", data={}),
        dcc.Store(id="report-format-store", data="csv"),
        dcc.Store(id="selected-student"),
        dcc.Store(id="demo-dismissed", data=False, storage_type="session"),'''

assert old_layout_stores in text, "old_layout_stores not found"
text = text.replace(old_layout_stores, new_layout_stores, 1)

# 8. Update apply_theme to take Input("auth", "data") so unauthenticated is ALWAYS theme-light
old_apply_theme = '''@callback(Output("app", "className"), Input("prefs", "data"))
def apply_theme(prefs):
    theme = (prefs or DEFAULT_PREFS).get("theme", "light")
    return f"app theme-{theme}"'''

new_apply_theme = '''@callback(
    Output("app", "className"),
    Input("prefs", "data"),
    Input("auth", "data"),
)
def apply_theme(prefs, auth):
    if not auth:
        return "app theme-light"
    theme = (prefs or DEFAULT_PREFS).get("theme", "light")
    return f"app theme-{theme}"'''

assert old_apply_theme in text, "old_apply_theme not found"
text = text.replace(old_apply_theme, new_apply_theme, 1)

# 9. Update render callback to accept Input("demo-dismissed", "data")
old_render_sig = '''@callback(
    Output("root", "children"),
    Input("url", "pathname"),
    Input("auth", "data"),
    Input("filters", "data"),
    Input("prefs", "data"),
    Input("profile", "data"),
)
def render(path, auth, values, prefs, profile):'''

new_render_sig = '''@callback(
    Output("root", "children"),
    Input("url", "pathname"),
    Input("auth", "data"),
    Input("filters", "data"),
    Input("prefs", "data"),
    Input("profile", "data"),
    Input("demo-dismissed", "data"),
)
def render(path, auth, values, prefs, profile, demo_dismissed):'''

assert old_render_sig in text, "old_render_sig not found"
text = text.replace(old_render_sig, new_render_sig, 1)

# Update render call body to pass demo_dismissed and remove /variables route
old_render_routes = '''    if path == "/estudiantes":
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
        content = home_page(values, lang, dark, profile)'''

new_render_routes = '''    dismissed_demo = bool(demo_dismissed)
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
        content = home_page(values, lang, dark, profile, dismissed_demo)'''

assert old_render_routes in text, "old_render_routes not found"
text = text.replace(old_render_routes, new_render_routes, 1)

# 10. Add callback to dismiss demo banner
dismiss_callback = '''
@callback(
    Output("demo-dismissed", "data"),
    Input("dismiss-demo-btn", "n_clicks"),
    prevent_initial_call=True,
)
def dismiss_demo_banner(clicks):
    if not clicks:
        raise PreventUpdate
    return True
'''

text += '\n' + dismiss_callback

with open('app.py', 'w', encoding='utf-8', newline='') as f:
    f.write(text)

print("app.py modified successfully")