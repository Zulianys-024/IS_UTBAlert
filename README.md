# 🚨 Sistema de Alertas Tempranas (UTBAlert) - UTB

Sistema web analítico desarrollado para la **Universidad Tecnológica de Bolívar (UTB)**, diseñado para centralizar variables académicas, procesar información estudiantil mediante datos simulados (*mock data*) y generar alertas tempranas orientadas a respaldar el seguimiento oportuno por parte del área de bienestar y acompañamiento estudiantil.

---

## 👥 Equipo de Trabajo
* **Brayan Maluenga**
* **Zulianys Orozco**
* **Juan Hernandez**

* **Curso / Grupo:** Ingeniería de Software 1206 (Séptimo Semestre)
* **Docente:** Aisner Jose Marrugo Juliao

---

## 🛠️ Tecnologías y Herramientas
El proyecto está construido bajo un ecosistema en Python y metodologías modernas de desarrollo ágil:
* **Frontend y Backend:** Python / Dash (Plotly) para la creación del *dashboard* interactivo y la lógica de negocio integrada.
* **Base de Datos:** Relacional con estructuración de datos simulados (*mock data*).
* **Control de Versiones:** Git y GitHub.
* **Gestión de Proyectos:** Tablero ágil con metodología **Kanban** utilizando **Trello**.

---

## 📊 Arquitectura del Sistema
El sistema se encuentra estructurado en capas modulares que garantizan la separación de responsabilidades:
1. **Capa de Presentación:** Interfaz web tipo *dashboard* desarrollada en Dash para visualización de métricas y alertas.
2. **Capa de Lógica de Negocio:** Motor de cálculo de riesgo que procesa las variables de desempeño y bienestar, generando clasificaciones (Riesgo Bajo, Medio, Alto).
3. **Capa de Datos:** Gestor de acceso a la base de datos simulada estructurada bajo los parámetros de retención de la UTB.

---

## 🚀 Instalación y Ejecución Local

1. Clona este repositorio:
   ```bash
   git clone https://github.com/Zulianys-024/IS_UTBAlert.git
   cd IS_UTBAlert
   ```

2. Instala dependencias del proyecto:
   ```bash
   python -m pip install -r requirements.txt
   ```

3. Configura las credenciales de Kaggle de una de estas formas:

   - Recomendado: coloca el archivo `kaggle.json` descargado desde Kaggle en `%USERPROFILE%\.kaggle\kaggle.json` (crea la carpeta `.kaggle` si no existe). No lo guardes dentro del repositorio.
   - Alternativa en PowerShell:
     ```powershell
     $env:KAGGLE_USERNAME = "tu_usuario"
     $env:KAGGLE_KEY = "tu_api_key"
     ```
   - También puedes usar un API token:
     ```powershell
     $env:KAGGLE_API_TOKEN = "tu_api_token"
     ```

   En CMD, las variables de entorno se establecen así:
   ```bash
   set KAGGLE_USERNAME=tu_usuario
   set KAGGLE_KEY=tu_api_key
   ```

   En Linux/macOS:
   ```bash
   export KAGGLE_USERNAME=tu_usuario
   export KAGGLE_KEY=tu_api_key
   ```

4. Ejecuta el script para descargar el dataset:
   ```bash
   python scripts/load_kaggle.py
   ```

   Por defecto, se descarga `waleedejaz/predict-students-dropout-and-academic-success` y se sobrescribe `data/raw/uci_dropout_raw.csv`. El script de procesamiento lee ese archivo con el separador `;`.

   Para elegir otro dataset, cambiar el CSV descargado o cambiar el nombre del archivo final:
   ```bash
   python scripts/load_kaggle.py --dataset usuario/nombre-dataset --csv-file archivo.csv --output-name nombre_archivo.csv
   ```

## 🐘 Carga de datos en PostgreSQL

La aplicación y los scripts se conectan a PostgreSQL usando la variable de entorno `DATABASE_URL`. Puede ser la URL de una base administrada (por ejemplo, Supabase, Neon o Railway) o de una instancia local. Cada integrante puede usar la misma base compartida, sin instalar PostgreSQL localmente. El navegador nunca se conecta directamente a la base: solo el servidor de la aplicación debe tener acceso a las credenciales.

1. Crea una base PostgreSQL en tu proveedor y copia su URL de conexión. Mantén habilitado SSL si el proveedor lo requiere.
2. En la consola donde correrás el cargador, define la variable. En PowerShell:
   ```powershell
   $env:DATABASE_URL = "postgresql://usuario:contraseña@host:5432/nombre_base?sslmode=require"
   ```
   En Linux/macOS:
   ```bash
   export DATABASE_URL="postgresql://usuario:contraseña@host:5432/nombre_base?sslmode=require"
   ```
   En un despliegue web, agrega `DATABASE_URL` en la sección de variables/secretos del proveedor de hosting. No la pongas en el código, README, GitHub ni en el frontend.
3. Ejecuta `db/schema.sql` en esa base para crear `estudiantes_academicos`.
4. Instala dependencias y carga el CSV procesado:
   ```bash
   python -m pip install -r requirements.txt
   python scripts/load_postgres.py
   ```

`scripts/load_postgres.py` requiere que `DATABASE_URL` esté definida y da un error claro si falta. La carga inserta las columnas `student_id`, `course`, `curricular_units_1st_sem_enrolled`, `curricular_units_2nd_sem_enrolled`, `curricular_units_1st_sem_grade`, `curricular_units_2nd_sem_grade`, `target` y `attendance_percentage`. La columna `student_id` es clave primaria; repetir una carga con identificadores existentes produce un error por duplicados.

### Acceso para integrantes del equipo

El repositorio no incluye la contraseña ni la URL real de Supabase. Quien clone el proyecto debe solicitar al responsable de la base la variable `DATABASE_URL` por un canal privado y configurarla en su propio entorno antes de ejecutar `scripts/load_postgres.py`. El responsable debe compartir solo el acceso que cada integrante necesita y cambiar la contraseña si la URL se expone accidentalmente.

No agregues la URL real a este README, a un archivo `.env` versionado, al código ni a GitHub. La URL de PostgreSQL permite acceso directo a la base con los permisos de su usuario; cualquier persona que la obtenga podría consultar o modificar datos según esos permisos.

Para una demo pública donde cualquier visitante solo necesite consultar datos, no compartas `DATABASE_URL`. La arquitectura debe exponer lecturas mediante el backend de la aplicación o la API de Supabase con una clave publicable y políticas RLS de solo lectura. Las claves secretas y las contraseñas de PostgreSQL permanecen únicamente en el servidor. La clave publicable por sí sola no autoriza acceso: RLS y los permisos deben configurarse correctamente. Consulta [seguridad de datos en Supabase](https://supabase.com/docs/guides/database/secure-data) y [claves de API](https://supabase.com/docs/guides/getting-started/api-keys).
