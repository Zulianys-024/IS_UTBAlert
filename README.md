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

   Si quieres cambiar el dataset o el nombre del archivo final:
   ```bash
   python scripts/load_kaggle.py --dataset usuario/nombre-dataset --output-name nombre_archivo.csv
   ```
