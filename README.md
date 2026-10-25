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
   git clone [https://github.com/Zulianys-024/IS_UTBAlert.git](https://github.com/Zulianys-024/IS_UTBAlert.git)

## verificacion de la instalación de dependencias