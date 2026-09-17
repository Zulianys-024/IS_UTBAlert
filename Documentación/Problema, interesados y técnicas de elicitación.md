### 1. Descripción del problema

La deserción estudiantil en la Universidad Tecnológica de Bolívar (UTB) constituye un desafío crítico que impacta la permanencia académica y el desarrollo profesional de los estudiantes. Actualmente, la detección de casos en riesgo se ve obstaculizada por la dispersión de la información académica, lo que impide que los equipos institucionales actúen de manera preventiva antes de que el estudiante abandone sus estudios. 

**Usuarios y beneficiarios:** 
* **Usuarios directos:** Personal de Bienestar Universitario y responsables de acompañamiento estudiantil de la UTB, quienes requieren una herramienta centralizada para consultar estados de riesgo e iniciar rutas de apoyo.
* **Beneficiarios indirectos:** Estudiantes de la UTB en situación de vulnerabilidad académica, quienes recibirán intervenciones oportunas.

**Objetivo general del proyecto:**
Desarrollar una aplicación web tipo *dashboard* en Python (Dash) que procese datos simulados (*mock data*) para calcular el nivel de riesgo de deserción (Bajo, Medio, Alto) y generar alertas tempranas, permitiendo al área de bienestar realizar un seguimiento psicológico y académico oportuno.

---

### 2. Identificación de interesados

| Rol / Interesado | Relación con el proyecto | Principales necesidades y expectativas |
| :--- | :--- | :--- |
| **Personal de Bienestar Universitario** *(Usuario final directo)* | Usuarios activos principales encargados del seguimiento de casos de riesgo. | Visualizar alertas prioritarias (Riesgo Alto), filtrar estudiantes por programa y disponer de un módulo para registrar notas de seguimiento psicológico. |
| **Estudiantes de la UTB** *(Beneficiarios indirectos)* | Población evaluada a través de la base de datos simulada. | Recibir apoyo y orientación oportuna por parte de la universidad cuando sus indicadores académicos se vean afectados. |
| **Universidad Tecnológica de Bolívar (UTB)** *(Cliente / Institución)* | Entidad receptora del proyecto de aula. | Contar con una propuesta técnica viable que optimice la retención estudiantil mediante el análisis centralizado de datos. |
| **Administrador del Sistema** *(Rol técnico)* | Encargado del mantenimiento de la plataforma. | Gestionar credenciales de acceso, asegurar la disponibilidad de la aplicación y la integridad de la base de datos simulada. |

---

### 3. Técnicas de elicitación aplicadas

**1. Lluvia de ideas (*Brainstorming*)**
* **Objetivo:** Definir el alcance del proyecto, seleccionar el stack tecnológico (Dash/Python) y delimitar el motor de cálculo basado en datos simulados[cite: 1, 4].
* **Participantes:** Brayan Maluenga, Zulianys Orozco, Juan Hernandez (Equipo de desarrollo)[cite: 1, 4].
* **Periodo de aplicación:** 24 de agosto al 2 de septiembre de 2026[cite: 1, 4].
* **Herramienta utilizada:** Tablero digital colaborativo (Miro) y sesiones de trabajo técnico[cite: 3].
* **Principales hallazgos:** Se determinó no utilizar datos reales por implicaciones legales, prescindir del rol docente para enfocar la plataforma exclusivamente en el área de bienestar y utilizar un motor de riesgo parametrizado por umbrales[cite: 1, 4, 5].

**2. Revisión de prototipos y bocetos previos**
* **Objetivo:** Evaluar la interfaz y la estructura visual desarrollada en el proyecto del semestre anterior para adaptar su flujo a la nueva arquitectura en Dash[cite: 3].
* **Participantes:** Brayan Maluenga, Zulianys Orozco, Juan Hernandez[cite: 1, 4].
* **Periodo de aplicación:** 3 de septiembre al 10 de septiembre de 2026[cite: 3, 4].
* **Herramienta utilizada:** Prototipos navegables en Figma / Bocetos de interfaz[cite: 3].
* **Principales hallazgos:** Se identificó la necesidad de transformar el *dashboard* en un panel interactivo con tarjetas de alerta de riesgo alto en rojo y añadir una ventana modal para el registro de bitácoras del seguimiento psicológico (RF-07)[cite: 4, 5].

---

### 4. Muestras de las herramientas utilizadas

#### Muestra 1: Tablero de Lluvia de Ideas

| Categoría | Ideas recopiladas | Decisión / Resultado |
| :--- | :--- | :--- |
| **Enfoque de datos** | Usar base de datos real vs. datos simulados (*mock data*)[cite: 1, 4]. | **Aprobado usar *mock data*** para evitar trámites legales y manejo de datos sensibles[cite: 1, 4]. |
| **Usuarios finales** | Incluir a docentes y personal de bienestar vs. solo Bienestar Universitario[cite: 1, 4]. | **Aprobado solo Bienestar Universitario**; los docentes no añaden valor directo al flujo de intervención psicológica[cite: 1, 4]. |
| **Tecnología Frontend/Backend** | Usar Django/React vs. Python con Dash. | **Aprobado Dash**, permite integrar analítica de datos, gráficos Plotly y backend en Python de forma ágil. |
| **Acciones de intervención** | Enviar correos automáticos vs. permitir registro de notas de seguimiento[cite: 4, 5]. | **Aprobado registro de notas (RF-07)** para que el profesional guarde el historial del acompañamiento humano[cite: 4, 5]. |

---

#### Muestra 2: Prototipo del Semestre Pasado

![Antigua interfaz del prototipo anterior](Documentación/Prototipo%20anterior.jpeg)

*Nota: La captura del prototipo anterior evidencia la evolución de la interfaz desde la propuesta inicial hacia la versión actual adaptada en Dash para la UTB[cite: 1, 3, 4].*
