# Sistema de Alertas Tempranas (UTBAlert) - UTB

Sistema web analítico desarrollado para la **Universidad Tecnológica de Bolívar (UTB)**, diseñado para centralizar variables académicas, procesar información estudiantil mediante datos simulados (*mock data*) y generar alertas tempranas orientadas a respaldar el seguimiento oportuno por parte del área de bienestar y acompañamiento estudiantil.

---

## Equipo de Trabajo

* **Brayan Maluenga**
* **Brayan Maluenga**
* **Zulianys Orozco**
* **Juan Hernandez**

* **Curso / Grupo:** Ingeniería de Software 1206 (Séptimo Semestre)
* **Docente:** Aisner Jose Marrugo Juliao

---

## Tecnologías y Herramientas

El código incluido implementa la generación de datos sintéticos en Python, su carga en PostgreSQL y un dashboard Dash/Plotly:

* **Generación de datos:** Python, NumPy y pandas.
* **Dashboard:** Dash y Plotly.
* **Base de Datos:** PostgreSQL, que puede alojarse en Supabase.
* **Control de Versiones:** Git y GitHub.
* **Gestión de Proyectos:** Tablero ágil con metodología **Kanban** utilizando **Trello**.

---

## Flujo de datos implementado

1. `scripts/simulado.py` genera los CSV sintéticos de estudiantes e historial en `data/synthetic/` y `data/processed/`.
2. `scripts/load_postgres.py` valida esos archivos y los carga en los catálogos y tablas definidos en `db/schema.sql`.
3. `utbapp/data_access.py` carga los CSV para la demo; el motor de riesgo calcula el indicador sobre el historial más reciente de cada estudiante.
4. `app.py` presenta el dashboard con filtros, gráficas, alertas, seguimientos y exportaciones.

---

## Ejecutar el dashboard localmente

En Windows, abre PowerShell en la carpeta del proyecto y ejecuta estos comandos,
uno por uno. Si PowerShell muestra un error con `&`, no pegues `&` al final de
`run.py` ni uses el botón "Run Code" de una extensión; inicia la aplicación
desde la terminal integrada:

```powershell
python -m venv .venv
& ".\.venv\Scripts\python.exe" -m pip install -r requirements.txt
Copy-Item .env.example .env
```

Edita `.env` y define como mínimo `SECRET_KEY` (puedes generarla con
`python -c "import secrets; print(secrets.token_hex(32))"`), el dominio
permitido (`ALLOWED_EMAIL_DOMAIN=utb.edu.co`) y deja `DEMO_MODE=false`.

Crea en la raíz el archivo local `admins.local.json` con las cuentas
administradoras iniciales. Este archivo no se versiona y sus contraseñas nunca
deben compartirse ni subirse al repositorio. Ejemplo con datos falsos:

```json
[
  {
    "nombre": "Ana Pérez",
    "correo": "ana.perez@utb.edu.co",
    "password": "cambiar-esta-clave"
  }
]
```

Después crea las cuentas y arranca la aplicación:

```powershell
& ".\.venv\Scripts\python.exe" seed_admins.py
& ".\.venv\Scripts\python.exe" run.py
```

Abre `http://127.0.0.1:8050`. Solo pueden iniciar sesión los usuarios
registrados con correo `@utb.edu.co` y contraseña válida. En el primer ingreso
la aplicación pide definir una contraseña nueva. `users.db`, `.env` y
`admins.local.json` están excluidos de Git.

Para administrar cuentas después del alta inicial:

```powershell
& ".\.venv\Scripts\python.exe" crear_admin.py
& ".\.venv\Scripts\python.exe" crear_admin.py --cambiar-password correo@utb.edu.co
& ".\.venv\Scripts\python.exe" crear_admin.py --desactivar correo@utb.edu.co
& ".\.venv\Scripts\python.exe" crear_admin.py --listar
```

La aplicación carga por defecto `data/processed/estudiantes_utb_sinteticos.csv` y `data/processed/historial_academico_utb_sintetico.csv`. Puede ejecutarse sin credenciales de PostgreSQL; `DATABASE_URL` continúa reservado para el cargador existente.

---

## Dashboard implementado

* Shell UTB con Inicio, Estudiantes, Variables de riesgo, Alertas, Seguimientos y Reportes.
* Filtros por programa, periodo, nivel, estado académico, riesgo y estado final.
* Motor de riesgo aislado y explicable en `utbapp/risk_engine.py`.
* Dona de distribución, tendencia de alertas, indicadores y tablas priorizadas.
* Exportación CSV y XLSX de los conjuntos filtrados.
* Registro de seguimientos en `data/seguimientos_demo.json`, única escritura de la interfaz en modo demostración.
* Estado vacío de seguimientos cuando aún no existe ninguna nota.
* Manifiesto de rutas en `/manus-routes.json`.

---

## Configuración y carga local

1. Clona este repositorio:
   ```bash
   git clone https://github.com/Zulianys-024/IS_UTBAlert.git
   cd IS_UTBAlert
   ```
2. Instala dependencias del proyecto:
   ```bash
   python -m pip install -r requirements.txt
   ```
3. Usa los CSV incluidos en `data/processed/` para poblar la base de datos. Para volver a generar los datos sintéticos, ejecuta:
   ```bash
   python scripts/simulado.py
   ```
   El generador guarda los originales en `data/synthetic/` y copias para la carga en `data/processed/`. No se requieren credenciales de Kaggle ni descargas externas.

## Carga en PostgreSQL

El cargador usa la variable de entorno `DATABASE_URL` para conectarse a PostgreSQL. Puede ser la URL de Supabase u otra base administrada. El navegador nunca se conecta directamente a la base: las credenciales se configuran solo en el entorno donde corre el cargador o el servidor.

1. Crea una base PostgreSQL y configura la variable. En Linux/macOS:
   ```bash
   export DATABASE_URL="postgresql://usuario:contraseña@host:5432/nombre_base?sslmode=require"
   ```
   No pongas la URL real en el README, en un archivo `.env` versionado, en el código ni en GitHub.
2. Ejecuta `db/schema.sql` para crear los catálogos, `ESTUDIANTE` y `VARIABLES_ACADEMICAS`. El esquema empieza eliminando esas tablas; ejecutarlo de nuevo borra los datos que ya contengan.
3. Carga los dos CSV sintéticos:
   ```bash
   python scripts/load_postgres.py
   ```

El cargador valida columnas, periodos, duplicados, estudiantes huérfanos y coherencia de programas antes de hacer upsert.

---

## Suposiciones del motor de riesgo

* C5 usa `nivel_actual × 10 %` como avance esperado de un plan de 10 niveles y exige como mínimo el 80 % de ese avance.
* C6 marca riesgo por cancelaciones cuando son mayores o iguales a 2 en el periodo.
* Alto = tres o más criterios, o C1 y C2 simultáneamente; Medio = uno o dos; Bajo = ninguno.
* El cálculo opera sobre el registro más reciente por estudiante, o sobre el periodo seleccionado.
* `estado_final` y `deserto` se muestran como resultado retrospectivo, pero no alimentan el riesgo.
* Los umbrales están centralizados en `DEFAULT_THRESHOLDS`; no están embebidos en los callbacks de la interfaz.
