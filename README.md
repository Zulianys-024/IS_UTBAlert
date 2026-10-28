# 🚨 Sistema de Alertas Tempranas (UTBAlert) - UTB

Sistema web analítico desarrollado para la **Universidad Tecnológica de Bolívar (UTB)**, diseñado para centralizar variables académicas, procesar información estudiantil mediante datos simulados (*mock data*) y generar alertas tempranas orientadas a respaldar el seguimiento oportuno por parte del área de bienestar y acompañamiento estudiantil.

---

## 👥 Equipo de Trabajo
* **Brayan Maluenga**
* **Zulianys Orozco**
* **Juan Hernandez**
* **alguien mas**

* **Curso / Grupo:** Ingeniería de Software 1206 (Séptimo Semestre)
* **Docente:** Aisner Jose Marrugo Juliao

---

## 🛠️ Tecnologías y Herramientas
El código incluido actualmente implementa la generación de datos sintéticos en Python y su carga en PostgreSQL:
* **Generación de datos:** Python, NumPy y pandas.
* **Base de Datos:** PostgreSQL, que puede alojarse en Supabase.
* **Control de Versiones:** Git y GitHub.
* **Gestión de Proyectos:** Tablero ágil con metodología **Kanban** utilizando **Trello**.

El dashboard web con Dash/Plotly forma parte del objetivo del proyecto, pero su código y punto de entrada todavía no están incluidos en este repositorio.

---

## 📊 Flujo de datos implementado
1. `scripts/simulado.py` genera los CSV sintéticos de estudiantes e historial en `data/synthetic/` y `data/processed/`.
2. `scripts/load_postgres.py` valida esos archivos y los carga en los catálogos y tablas definidos en `db/schema.sql`.
3. El dashboard y las consultas de alertas aún deben conectarse a estas tablas.

---

## 🚀 Configuración y carga local

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

## 🐘 Carga de datos en PostgreSQL

El cargador usa la variable de entorno `DATABASE_URL` para conectarse a PostgreSQL. Puede ser la URL de Supabase u otra base administrada. El navegador nunca se conecta directamente a la base: las credenciales se configuran solo en el entorno donde corre el cargador o el servidor.

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
3. Ejecuta `db/schema.sql` en esa base para crear los catálogos `PROGRAMA_ACADEMICO` y `PERIODO_ACADEMICO`, además de `ESTUDIANTE` y `VARIABLES_ACADEMICAS`. El esquema empieza eliminando esas tablas; ejecutarlo de nuevo borra los datos que ya contengan.
4. Instala las dependencias y carga los dos CSV sintéticos desde `data/processed/`:
   ```bash
   python -m pip install -r requirements.txt
   python scripts/load_postgres.py
   ```

`scripts/load_postgres.py` valida los archivos, registra los programas y periodos que requieren las claves foráneas y después carga estudiantes e historial. Las cargas repetidas actualizan filas existentes por sus claves; no eliminan registros que hayan desaparecido de los CSV. El script requiere que el esquema nuevo ya exista en la base.

### Acceso para integrantes del equipo

El repositorio no incluye la contraseña ni la URL real de Supabase. Quien clone el proyecto debe solicitar al responsable de la base la variable `DATABASE_URL` por un canal privado y configurarla en su propio entorno antes de ejecutar `scripts/load_postgres.py`. El responsable debe compartir solo el acceso que cada integrante necesita y cambiar la contraseña si la URL se expone accidentalmente.

No agregues la URL real a este README, a un archivo `.env` versionado, al código ni a GitHub. La URL de PostgreSQL permite acceso directo a la base con los permisos de su usuario; cualquier persona que la obtenga podría consultar o modificar datos según esos permisos.

Para una demo pública donde cualquier visitante solo necesite consultar datos, no compartas `DATABASE_URL`. La arquitectura debe exponer lecturas mediante el backend de la aplicación o la API de Supabase con una clave publicable y políticas RLS de solo lectura. Las claves secretas y las contraseñas de PostgreSQL permanecen únicamente en el servidor. La clave publicable por sí sola no autoriza acceso: RLS y los permisos deben configurarse correctamente. Consulta [seguridad de datos en Supabase](https://supabase.com/docs/guides/database/secure-data) y [claves de API](https://supabase.com/docs/guides/getting-started/api-keys).
