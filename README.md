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

El repositorio **no está conectado permanentemente a una base de datos ni sincroniza datos con GitHub**. `scripts/load_postgres.py` abre una conexión cuando se ejecuta, lee `data/processed/estudiantes_academicos.csv` e intenta insertar sus filas en PostgreSQL. La configuración actual apunta a una instancia local (`localhost`) y a la base `proyecto_desercion`; por eso, cada persona debe tener PostgreSQL instalado y configurar su propia conexión.

Antes de ejecutar el cargador:

1. Crea la base de datos `proyecto_desercion` en PostgreSQL.
2. Conéctate a esa base y ejecuta el SQL de `db/schema.sql` para crear la tabla `estudiantes_academicos`.
3. Verifica que los datos de conexión de `scripts/load_postgres.py` correspondan a tu instancia y usuario local.
4. Confirma que el CSV procesado tenga las ocho columnas que el script inserta, en el mismo orden: `student_id`, `course`, `curricular_units_1st_sem_enrolled`, `curricular_units_2nd_sem_enrolled`, `curricular_units_1st_sem_grade`, `curricular_units_2nd_sem_grade`, `target` y `attendance_percentage`.
5. Ejecuta desde la raíz del proyecto:
   ```bash
   python scripts/load_postgres.py
   ```

La carga solo se realiza al ejecutar el script y queda guardada en la base local a la que se conectó. El script no crea la base de datos por sí solo. No publiques contraseñas ni las guardes en el repositorio; para compartir el proyecto, cada integrante debe usar sus propias credenciales. La columna `student_id` es clave primaria, así que volver a cargar filas con identificadores ya existentes puede producir un error por duplicados.
