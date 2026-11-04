# Prompt listo para usar

Copia el bloque siguiente y pégalo en el chat del compañero (o en un agente de IA que
tenga acceso al repositorio). Está escrito para que **no se vuelva a romper el diseño**
mientras se conservan las funcionalidades nuevas.

---

```text
Contexto
========
Trabajas sobre el repositorio IS_UTBAlert (Dash 4.5 + Python). El proyecto original tenía
un diseño ya aprobado (tipografía Inter, tarjetas blancas/gris azulado, tablas sin
mayúsculas, modo claro y oscuro consistentes). Después se añadieron funcionalidades
nuevas y, en el proceso, se alteró la estética:

  - En modo oscuro las tablas quedaron con el cuerpo blanco y las cabeceras azul marino
    en MAYÚSCULAS.
  - La tabla de /estudiantes se sale del ancho de la pantalla y desalinea la página.
  - Aparece una tarjeta roja de error de Dash ("Invalid argument `type` ... followup-date").
  - Aparece la barra de desarrollo de Dash ("Plotly Cloud / Errors / Callbacks / Server").

Objetivo
========
Restaurar el diseño visual original y CONSERVAR todas las funcionalidades añadidas.
No reescribas la lógica ni los callbacks. No cambies textos, datos ni rutas.

Reglas estrictas de diseño (invariantes)
========================================
1. Tipografía: la del proyecto (Inter). NO importes Google Fonts ni cambies
   `font-family` de `body`.
2. Tablas: los colores y tamaños se definen SOLO en `app.py` → `table_styles(dark)` como
   estilos inline. NO añadas reglas `th`/`td` en CSS, y menos con `!important`.
   - Modo claro: cabecera #F7F9FC / texto #748091, celdas #FFFFFF / texto #344054,
     sin `text-transform`, 11-12 px.
   - Modo oscuro: cabecera #16233A / texto #8FA0B8, celdas #111C2E / texto #D6E0EF.
3. Tarjetas y KPIs: se definen en `assets/style.css` (`.card`, `.kpi-card`,
   `.theme-dark .card`, etc.). No las redefinas.
4. Modales y formularios: usan las clases de `style.css` (`.modal-card`, `.search-input`,
   `.textarea`). No añadas `.modal-*`, `.Select-*` ni `.login-card`.
5. Colores: usa los tokens existentes de `style.css`
   (--blue:#153DDA, --ink:#17263C, --muted:#778292, --bg:#F7F9FC, --border:#E9EEF4).
6. Nada de `!important` sobre selectores globales ni sobre `.dash-*`.
7. Cada componente nuevo debe tener variante de modo claro Y oscuro
   (`.theme-dark .mi-componente`).

Qué conservar (no tocar)
========================
- El banner de alerta temprana crítica (RF-05) en `app.py`:
  `critical_alert_banner()`, el contenedor `critical-alert-banner-container`, el botón
  `critical-alert-banner` y el callback `on_critical_alert_click`.
- Las claves i18n `rf05.*` en `utbapp/i18n.py`.
- Los logos institucionales y los textos de marca actuales.
- Todos los callbacks, stores, filtros, exportaciones y tests.

Tareas concretas
================
1. `assets/custom.css`: elimina el `@import` de Google Fonts, el bloque `:root`, la regla
   `body`, y las reglas de `.glass-card`, `.kpi-*`, `.modal-*`, `.Select-*`,
   `.login-card`, `.login-header-logo`, `.nav-logo-img`. Elimina por completo las reglas
   `th`/`td` con `!important`.
   Deja el archivo SOLO con `.critical-alert-banner*`, en modo claro y oscuro
   (`.theme-dark .critical-alert-banner*`), más su versión responsive a 900 px.
2. `assets/style.css`: añade al final
       .table-card { min-width: 0; }
       .dash-table-container { overflow-x: auto; }
   para que las tablas anchas hagan scroll dentro de la tarjeta en vez de desbordar la
   página.
3. `app.py`: cambia `dcc.Input(id="followup-date", type="date", ...)` por
   `type="text"` con `placeholder="AAAA-MM-DD"` (Dash 4.5 no admite `type="date"`).
4. `run.py` y el bloque `if __name__ == "__main__"` de `app.py`: `debug=False`.
5. No modifiques nada más.

Criterios de aceptación (verifícalos en el navegador)
=====================================================
- [ ] En modo oscuro, en /estudiantes, /alertas, /seguimientos y /reportes:
      fondo de celdas = #111C2E, texto claro, cabeceras sin mayúsculas.
- [ ] En modo claro las tablas se ven igual que antes del cambio.
- [ ] A 1000 px de ancho no hay scroll horizontal de página
      (`document.documentElement.scrollWidth <= window.innerWidth`) en ninguna ruta.
- [ ] No aparece ninguna tarjeta roja de error de Dash en ninguna ruta.
- [ ] No aparece la barra de desarrollo de Dash.
- [ ] El banner de alerta crítica se ve correctamente en claro y en oscuro y sigue
      navegando a /estudiantes con el filtro de riesgo alto.
- [ ] `pytest` pasa completo.
- [ ] `git diff` toca como máximo: assets/custom.css, assets/style.css, app.py, run.py.

Entrega
=======
Haz los cambios en una rama llamada `fix/restaurar-diseno-visual` y abre un Pull Request
hacia `main`. En la descripción del PR incluye una captura de /estudiantes en modo oscuro
antes y después, y el resultado de `pytest`.
```

---

## Variante corta (si solo quieres pegar el diagnóstico)

```text
El modo oscuro se rompe porque assets/custom.css fuerza con !important
`th{background:#002B49;color:#fff;text-transform:uppercase}` y
`td{background:#FFF;color:#0F172A}`, y eso gana sobre los estilos inline que genera
table_styles() en app.py. Además sube el font-size de las celdas y hace que la tabla de
/estudiantes desborde la página (1308 px de scrollWidth en una ventana de 1000 px).

Quita de custom.css todo lo que no sea el banner de alerta crítica (incluido el @import
de Google Fonts, body, .kpi-*, .modal-*, .Select-*, .login-* y las reglas th/td con
!important), y añade en style.css:
  .table-card{min-width:0}
  .dash-table-container{overflow-x:auto}

No toques los callbacks ni el banner. Deja debug=False en run.py.
```
