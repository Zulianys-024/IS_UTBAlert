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

![Antigua interfaz del prototipo anterior](https://github.com/Zulianys-024/IS_UTBAlert/blob/main/Documentación/Prototipo%20anterior.jpeg?raw=true)


*Nota: La captura del prototipo anterior evidencia la evolución de la interfaz desde la propuesta inicial hacia la versión actual adaptada en Dash para la UTB[cite: 1, 3, 4].*

### 5. Requerimientos identificados

Todos los requerimientos, tanto funcionales como no funcionales, se encuentran especificados en el documento del Proyecto de aula.

### 6. Priorización de requerimientos

Para establecer la prioridad de los requerimientos funcionales y no funcionales del sistema de Alertas Tempranas, el equipo utilizó un criterio de clasificación en tres niveles: **Alta, Media y Baja**. Esta escala se definió evaluando la criticidad operativa para el área de Bienestar Universitario de la UTB, el impacto en la estabilidad de la arquitectura en Dash y la viabilidad técnica para la entrega del Producto Mínimo Viable (MVP).

| Nivel de Prioridad | Criterio de Selección | Requerimientos Asignados | Justificación Técnica y Operativa |
| :--- | :--- | :--- | :--- |
| **Alta** *(Obligatorio / Crítico)* | Funcionalidades y atributos de calidad indispensables para el funcionamiento básico e indispensable del sistema. Su ausencia impide la operación de la plataforma. | **RF-01**, **RF-02**, **RF-03**, **RF-04**, **RF-05**,<br>**RNF-01**, **RNF-02**, **RNF-03**, **RNF-04**, **RNF-05**. | Constituyen el núcleo de la solución: autenticación de usuarios, consulta de la base de datos simulada (*mock data*), procesamiento del algoritmo de riesgo, visualización del *dashboard* en Dash, generación de alertas rojas prioritarias y cumplimiento de atributos de usabilidad, rendimiento, compatibilidad y privacidad. |
| **Media** *(Importante)* | Funcionalidades que aportan un alto valor operativo para el usuario final y mejoran el seguimiento, pero cuya omisión temporal no paraliza la aplicación. | **RF-06**, **RF-07**,<br>**RNF-06**. | Permiten al personal de bienestar filtrar los datos por programa/semestre y registrar las bitácoras del acompañamiento psicológico (RF-07), además de asegurar la mantenibilidad del código en Python y la compatibilidad con navegadores. |
| **Baja** *(Deseable)* | Capacidades complementarias que mejoran la gestión administrativa o la experiencia de uso, a desarrollarse si el tiempo del proyecto lo permite. | **RF-08**. | La exportación de listados a formatos CSV/Excel facilita el reporte externo, pero no es estrictamente necesaria para la detección visual de alertas dentro del panel. |

**Requerimientos considerados para la primera versión funcional (MVP):**
Para la versión funcional que se entregará al finalizar el periodo, se han seleccionado la totalidad de los requerimientos de prioridad **Alta** (**RF-01 a RF-05** y **RNF-01 a RNF-05**) junto con el requerimientos de prioridad **Media** **RF-06**. Esta selección garantiza que el área de bienestar disponga de una herramienta capaz de procesar los datos simulados, calcular niveles de riesgo y mostrar las alertas de riesgo alto.

### 7. Validación y ajuste del modelo previo

**Descripción de la concepción inicial:**

Inicialmente, nuestro proyecto "Alertas Tempranas" se planteó como una herramienta estrictamente de procesamiento y visualización pasiva. El modelado original contemplaba que el "Personal de Bienestar" iniciara sesión y el "Sistema Automático" simplemente procesara la base de datos simulada para mostrar las alertas en el panel de control[cite: 3]. El alcance original no contemplaba que el usuario interactuara insertando nueva información o extrayendo reportes del sistema[cite: 3].

**Hallazgos obtenidos durante la elicitación:**

Durante el levantamiento y análisis de requerimientos, se identificaron necesidades que ampliaron la idea inicial:

1. **Necesidad de registro de intervenciones:** Se determinó que no basta con visualizar la alerta, sino que el Personal de Bienestar requiere dejar constancia del acompañamiento humano realizado a través de "notas de seguimiento psicológico" (RF-07)[cite: 2].
2. **Uso administrativo de los datos:** Se identificó la necesidad de exportar la información filtrada (en Excel/CSV) para la gestión administrativa del área de bienestar, lo cual no estaba en el alcance inicial (RF-08)[cite: 2].
3. **Filtros avanzados:** Se hizo evidente que los usuarios necesitan filtrar la información no solo por nivel de riesgo, sino también por programa académico y semestre (RF-06)[cite: 2].
4. **Roles de usuario:** El requerimiento de autenticación (RF-01) evidenció la existencia de un rol "Administrador", el cual no estaba explícito como actor en los diagramas de casos de uso iniciales[cite: 2, 3].

**Cambios realizados en el alcance, funcionalidades y diagramas:**

Para dar respuesta a los hallazgos, el alcance pasó de ser un *Dashboard* pasivo a una herramienta interactiva de gestión básica de casos. Los diagramas se actualizarán de la siguiente manera:

* **Diagrama de Casos de Uso:** Se deben agregar los casos de uso "Registrar nota de seguimiento" y "Exportar reporte de riesgo" asociados al Personal de Bienestar. Se debe incluir al actor "Administrador".
* **Diagrama de Clases:** Se debe crear una nueva clase `SeguimientoPsicologico` relacionada con `EstudianteMock` para soportar el RF-07. Se deben ampliar los métodos en `DashboardController` para incluir la exportación y los nuevos parámetros de filtrado (programa y semestre).
* **Diagrama de Actividades / Secuencia:** Se deben incluir los flujos alternos donde el usuario selecciona un perfil y guarda una nota de seguimiento.
