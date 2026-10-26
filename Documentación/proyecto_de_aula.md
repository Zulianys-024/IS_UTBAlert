# PLANTILLA PROYECTO DE AULA
**Ingeniería de Software**
*Documento guía para formulación, desarrollo, seguimiento y entrega del proyecto.*

| Campo | Detalle |
| :--- | :--- |
| **Nombre del proyecto** | Alertas Tempranas |
| **Integrantes** | Brayan Maluenga, Zulianys Orozco, Juan Hernandez |
| **Grupo / curso** | Ingeniería de Software 1206 |
| **Docente** | Aisner Jose Marrugo Juliao |
| **Semestre** | Séptimo Semestre |
| **Fecha de inicio** | 24/08/2026 |
| **Fecha de entrega final** | 20/11/26 |

---

## 1. Propósito del proyecto de aula
El Proyecto de Aula busca integrar los conocimientos y prácticas trabajados en la asignatura de Ingeniería de Software mediante el desarrollo incremental de una solución de software a un problema real o suficientemente representativo. El proyecto se ejecutará durante el segundo y tercer corte, con evidencias de análisis, diseño, construcción, pruebas, gestión del trabajo y presentación de resultados.

La propuesta debe ser viable dentro del tiempo disponible. Se valorará más un producto funcional, bien diseñado y sustentado que una solución sobredimensionada e incompleta.

## 2. Normas de presentación y formato APA 7
Todo el documento deberá elaborarse aplicando las normas APA, séptima edición (APA 7), no únicamente en la lista de referencias. Esto incluye la presentación general del texto, jerarquía de títulos, citación de fuentes, tablas, figuras, gráficos, imágenes, notas y referencias. Cuando exista una directriz institucional específica que complemente APA 7, deberá seguirse también.

* Las referencias deben presentarse en formato APA 7 y, cuando exista, incluir DOI como enlace DOI. Para recursos web utilice la URL correspondiente según las reglas de APA 7.
* Mantenga consistencia tipográfica, de espaciado, márgenes, sangrías, numeración y niveles de encabezado en todo el documento.
* Utilice redacción académica, clara y coherente. Evite afirmaciones técnicas o estadísticas sin respaldo cuando requieran evidencia.
* No copie imágenes, diagramas, tablas o fragmentos de otras fuentes sin atribución. Si se adaptan, debe indicarse expresamente.
* Las figuras -incluidos gráficos, diagramas, capturas, modelos, arquitecturas e imágenes- deben numerarse consecutivamente (Figura 1, Figura 2, etc.), llevar título y reconocer la fuente cuando no sean de elaboración propia.
* Las tablas deben numerarse consecutivamente (Tabla 1, Tabla 2, etc.), llevar un título claro y, cuando corresponda, una nota con la fuente o indicación de elaboración propia.
* Incluya en la lista de referencias únicamente las fuentes citadas en el documento y asegúrese de que toda cita tenga su referencia correspondiente.
* Use citación autor-fecha para toda idea, dato, definición, modelo, metodología, imagen, tabla o información tomada o adaptada de una fuente externa.

## 3. Lineamientos generales
Además de los lineamientos técnicos, el equipo es responsable de la calidad académica del documento. La presentación completa debe ajustarse a APA 7: citas, referencias, tablas, figuras, gráficos, títulos, notas y atribución de fuentes. La ausencia de citación o la presentación de material ajeno como propio constituye una deficiencia académica.

* El proyecto será desarrollado en equipos definidos por el docente.
* Debe resolver una necesidad o problema claramente identificado y tener usuarios o actores definidos.
* El equipo deberá aplicar prácticas de desarrollo ágil y mantener trazabilidad entre requerimientos, implementación y pruebas.
* El código fuente deberá mantenerse en un repositorio de control de versiones.
* Cada integrante deberá evidenciar participación real en el proyecto.
* Las decisiones técnicas relevantes deberán estar justificadas.
* La solución debe incluir pruebas y evidencia de funcionamiento.
* El alcance podrá ajustarse durante el desarrollo, siempre que el cambio sea documentado y aprobado por el docente.

## 4. Identificación del proyecto
¿Qué debe desarrollar? Registre los datos que permiten identificar y localizar el proyecto: nombre, integrantes, grupo, responsable, metodología de trabajo y enlaces técnicos. Los enlaces al repositorio y a la demostración deben mantenerse accesibles para el docente durante el proceso de evaluación.

| Campo | Detalle |
| :--- | :--- |
| **Nombre del proyecto** | Alertas Tempranas |
| **Equipo** | Brayan Maluenga, Zulianys Orozco, Juan Hernandez |
| **Lider / Scrum Master (si aplica)** | NA |
| **Repositorio** | https://github.com/Zulianys-024/IS_UTBAlert |
| **URL del producto / demo (si aplica)** | [Complete este campo] |
| **Metodología / marco de trabajo** | Kanban (gestión del tablero y flujo continuo de trabajo en Trello) |

## 5. Resumen ejecutivo
¿Qué debe desarrollar? Presente una visión completa y breve del proyecto. Un lector que solo consulte esta sección debe comprender qué problema se aborda, quién lo tiene, qué solución se construirá, cuál es el alcance del MVP, qué tecnologías generales se utilizarán y qué resultado se espera obtener. Redáctelo al final, aunque aparezca al inicio.

En máximo 250 palabras describa el problema, la solución propuesta, los usuarios objetivo, el alcance y el valor esperado.

Nuestro proyecto, "Alertas Tempranas", busca abordar la problemática de la deserción estudiantil, enfocándose en los factores de riesgo específicos presentes en el contexto de la Universidad Tecnológica de Bolívar (UTB). Para salvaguardar la privacidad de la información y evitar riesgos legales, la solución operará sobre una base de datos encontrada en internet.

Nuestra solución propuesta es desarrollar una aplicación web que consulte estos datos preexistentes y los analice para identificar patrones de comportamiento. A partir de este análisis, el sistema determinará si un perfil estudiantil presenta un nivel de riesgo bajo, medio o alto de abandonar sus estudios.

Los usuarios objetivos serán principalmente el personal de bienestar y los responsables del acompañamiento estudiantil de la UTB, e indirectamente los estudiantes de la institución. El MVP se centrará en el procesamiento de la información, el cálculo de los niveles de riesgo y la generación de alertas tempranas en la interfaz. No se busca predecir la deserción con total certeza, sino entregar una herramienta técnica y funcional para apoyar la detección oportuna de señales de riesgo.

## 6. Problema y contexto
¿Qué debe desarrollar? Sustente la necesidad que origina el proyecto. Evite formular el problema como ausencia de la solución ('no existe una aplicación'). Describa la situación problemática real y, cuando corresponda, respáldela con fuentes confiables citadas en APA 7.

### 10.1 Descripción del problema
Explique la situación actual, sus causas, consecuencias y por qué merece ser atendida.

La deserción estudiantil representa una problemática crítica en el ámbito de la educación superior, afectando de manera directa el proyecto de vida de los alumnos y los índices de permanencia institucional de la Universidad Tecnológica de Bolívar (UTB). En la actualidad, la situación se agrava debido a que los factores de riesgo académicos, socioeconómicos y de bienestar se encuentran dispersos en diferentes registros y dependencias.

* **Causas:** La principal causa de esta deficiencia en el seguimiento radica en la ausencia de una herramienta automatizada y centralizada que permita consolidar y procesar de forma unificada las variables que determinan el estado de vulnerabilidad de un estudiante. Esto obliga al personal de bienestar a realizar diagnósticos aislados y tardíos.
* **Consecuencias:** Como consecuencia, las señales tempranas de alerta pasan desapercibidas, impidiendo que la institución intervenga a tiempo para prevenir el abandono definitivo de los estudios por parte del alumno.
* **Por qué merece ser atendida:** Esta problemática merece ser atendida con urgencia porque la retención estudiantil no solo impacta la eficiencia y reputación de la UTB, sino que trunca las oportunidades de desarrollo profesional de los jóvenes. Contar con un sistema que procese información estructurada para calcular niveles de riesgo (bajo, medio o alto) permitirá optimizar los recursos de acompañamiento y focalizar los esfuerzos de retención de manera oportuna.

### 10.2 Usuarios y partes interesadas
Identifique usuarios, clientes, beneficiarios y demás stakeholders relevantes.

El proyecto está delimitado para el entorno institucional de la Universidad Tecnológica de Bolívar (UTB). A continuación se detallan los roles, beneficiarios y stakeholders clave del sistema:

* **Estudiantes de la UTB (Beneficiarios indirectos):** Constituyen la población objetivo. Aunque no interactúan directamente con la plataforma, son los principales beneficiarios al recibir un acompañamiento académico y de bienestar oportuno cuando el sistema detecta señales de vulnerabilidad o riesgo.
* **Personal de Bienestar Universitario y Responsables de Acompañamiento (Usuarios finales):** Son los usuarios directos de la plataforma. Utilizan el panel de control y las alertas tempranas generadas a partir del procesamiento de los datos para identificar los casos críticos que requieren intervención, orientación o apoyo institucional.
* **Universidad Tecnológica de Bolívar - UTB (Cliente / Institución beneficiaria):** Actúa como la entidad receptora de la solución, fortaleciendo de manera centralizada sus estrategias institucionales de retención y permanencia estudiantil.

### 10.3 Justificación
Explique el valor académico, técnico y/o social de la solución.

La deserción estudiantil representa uno de los mayores desafíos para las instituciones de educación superior, afectando tanto el proyecto de vida de los estudiantes como los indicadores de retención de los programas académicos. Desde una perspectiva social y educativa, este proyecto aporta gran valor al proporcionar una herramienta que facilita el seguimiento oportuno por parte del área de bienestar. Mediante la detección de riesgos, los profesionales de bienestar podrán orientar la intervención hacia un acompañamiento integral y de apoyo psicológico, identificando si las bajas calificaciones obedecen a situaciones personales, socioeconómicas o emocionales ajenas al ámbito académico. En lugar de adoptar un enfoque meramente punitivo o reactivo, el sistema promueve la prevención y el bienestar humano de los estudiantes de la UTB.

Desde el punto de vista técnico, la solución ofrece un mecanismo centralizado y automatizado para consolidar estas variables. Esto optimiza los tiempos de respuesta del personal de acompañamiento y mejora la toma de decisiones institucionales, focalizando los recursos y esfuerzos de apoyo en aquellos estudiantes que realmente lo necesitan.

## 7. Objetivos
Los objetivos definen qué se pretende lograr y serán utilizados posteriormente para valorar los resultados. Deben guardar relación directa con el problema y con el alcance realmente ejecutable durante los dos cortes.

### 10.1 Objetivo general
Formule un único objetivo general, claro, medible y alineado con el producto a construir.

Desarrollar una aplicación web tipo dashboard en Python (Dash) que procese datos de índole pública en internet para calcular el nivel de riesgo de deserción (Bajo, Medio, Alto) y generar alertas tempranas, permitiendo al área de bienestar realizar un seguimiento psicológico y académico oportuno.

### 10.2 Objetivos específicos
Incluya entre 3 y 5 objetivos específicos.

1. Diseñar una base de datos centralizada que permita el registro seguro de la información de los estudiantes y el almacenamiento de las variables académicas y de bienestar relevantes.
2. Implementar un módulo de gestión de usuarios con roles definidos exclusivamente para el personal de bienestar y administradores, garantizando el acceso seguro a la información y a los tableros de control.
3. Desarrollar la lógica del sistema para procesar los datos de una base de datos pública preexistente y calcular de forma automática el nivel de riesgo de deserción del estudiante.
4. Construir una interfaz de usuario que permita consultar la información consolidada y visualizar las alertas tempranas generadas, facilitando la toma de decisiones.

## 8. Alcance del producto
Defina con precisión hasta dónde llegará el proyecto. Esta sección funciona como un acuerdo de expectativas: evita que el equipo intente construir más de lo que puede terminar y permite distinguir compromisos de ideas futuras.

### 10.1 Alcance incluido
Liste las capacidades que sí serán desarrolladas durante el semestre.

* Estructuración e implementación de una base de datos poblada con información estudiantil de una base de datos pública que contenga las variables, métricas y factores de riesgo propios de la UTB.
* Desarrollo de la lógica interna (algoritmo) que procesa la información de la base de datos para determinar el nivel de riesgo (bajo, medio, alto) de cada perfil.
* Diseño de un panel de control (dashboard) orientado a las necesidades específicas del área de bienestar y los responsables de acompañamiento de la UTB para la visualización de las alertas tempranas.

### 10.2 Fuera de alcance
Declare explícitamente funcionalidades o componentes que no serán desarrollados.

* No se desarrollará un módulo para el registro, inserción o creación manual de nuevos perfiles estudiantiles desde la interfaz de usuario, ya que el sistema consumirá los datos previamente cargados en la base de datos.
* No se realizará ningún tipo de conexión, integración o extracción de datos reales provenientes de los sistemas de información institucionales oficiales de la UTB (como Banner u otros), eliminando así cualquier implicación legal sobre el manejo de datos sensibles.
* No se busca predecir con certeza que un estudiante abandonará sus estudios, ni se implementarán modelos predictivos complejos basados en Inteligencia Artificial.
* Variables socioeconómicas, psicológicas o de bienestar no estarán incluidas en esta versión por la complejidad y fluctuación de estas.

### 10.3 Producto mínimo viable (MVP)
Defina qué debe funcionar al finalizar el tercer corte para considerar exitoso el proyecto.

El MVP consistirá en una aplicación web tipo dashboard funcional que operará de manera independiente sobre una base de datos de internet con información estudiantil pública, que contenga algunos factores de retención de la UTB. El sistema será capaz de leer estos datos preexistentes, procesar las variables para calcular un nivel de riesgo (bajo, medio o alto) y generar las alertas tempranas correspondientes en la interfaz de usuario. Este entregable demostrará la viabilidad técnica y operativa de la herramienta como apoyo para detectar señales de riesgo, sin comprometer información real ni requerir la captura manual de datos por parte de los usuarios.

---

## 9. SEGUNDO CORTE - Formulación, análisis y diseño
Propósito del corte: transformar la idea inicial en una solución de software planificada y técnicamente sustentada. Al finalizar este corte el equipo debe poder explicar qué construirá, para quién, con qué requerimientos, arquitectura, datos, interfaz y plan de trabajo, además de mostrar el avance funcional solicitado.

Esta sección constituye la base de la entrega del segundo corte. El objetivo es demostrar que el equipo entiende el problema, ha definido un alcance viable y cuenta con un diseño suficientemente claro para iniciar/consolidar la construcción.

### 10.1 Requerimientos funcionales
Registre los requerimientos funcionales priorizados. Puede ampliar la tabla según sea necesario.

| ID | Requerimiento | Fuente | Prioridad | Criterio de aceptación | Estado |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **RF-01** | **Autenticación y control de acceso**<br>El sistema debe permitir el inicio de sesión seguro a usuarios del área de bienestar y administradores mediante credenciales registradas. | Personal de Bienestar / Diagrama de Casos de Uso | Alta | El sistema valida las credenciales y permite el acceso únicamente a usuarios autorizados asignando su rol correspondiente. | Pendiente |
| **RF-02** | **Carga y lectura de datos**<br>El sistema debe consultar automáticamente la información académica almacenada en la base de datos pública de internet sin requerir registros manuales. | Especificación técnica / Revisión documental | Alta | Los perfiles e indicadores académicos se cargan correctamente en la aplicación al iniciar la sesión. | Pendiente |
| **RF-03** | **Procesamiento y cálculo de riesgo académico**<br>El motor de riesgo debe analizar las variables académicas (promedio, créditos, inasistencias) y clasificar cada perfil en riesgo Bajo, Medio o Alto. | MotorDeRiesgo (Diagrama de Clases) | Alta | El sistema ejecuta el algoritmo de cálculo y asigna la categoría de riesgo correcta a cada estudiante evaluado. | Pendiente |
| **RF-04** | **Visualización del Dashboard analítico**<br>El sistema debe presentar un panel de control en Dash con gráficos interactivos que muestren métricas consolidadas del estado de los estudiantes. | Lluvia de ideas / Prototipo Dash | Alta | El tablero despliega correctamente los gráficos (distribución de riesgo, estadísticas por programa) actualizados dinámicamente. | Pendiente |
| **RF-05** | **Generación de alertas tempranas críticas**<br>El sistema debe resaltar mediante banners o tarjetas rojas de atención prioritaria a aquellos estudiantes cuyo nivel de riesgo sea Alto. | Objetivo general del proyecto | Alta | El sistema genera y resalta visualmente la alerta de riesgo alto en la interfaz principal del dashboard. | Pendiente |
| **RF-06** | **Filtrado dinámico de alertas**<br>El sistema debe permitir al usuario filtrar los estudiantes por nivel de riesgo (Bajo, Medio, Alto), programa académico y semestre. | Personal de Bienestar / DashboardController | Media | Al aplicar filtros desde la interfaz, los gráficos y la tabla de estudiantes se actualizan en tiempo real mostrando solo los registros coincidentes. | Pendiente |
| **RF-07** | **Detalle de perfil para seguimiento psicológico**<br>El sistema debe permitir al personal de bienestar seleccionar a un estudiante en alerta para ver el desglose de su información y registrar notas de seguimiento psicológico realizado. | Área de Bienestar Universitario UTB | Alta | Al seleccionar un caso, se despliega una ventana o panel de detalle con la información académica y un módulo de texto para guardar notas del acompañamiento humano. | Pendiente |
| **RF-08** | **Exportación de reportes de riesgo**<br>El sistema debe permitir exportar la lista de estudiantes filtrados por riesgo en formato estructurado (CSV o Excel) para uso administrativo del área de bienestar. | Gestión Administrativa de Bienestar | Baja | El sistema genera y descarga correctamente un archivo en formato CSV/Excel con los datos correspondientes a los filtros aplicados en el tablero. | Pendiente |

### 10.2 Requerimientos no funcionales
Incluya atributos de calidad relevantes: seguridad, rendimiento, usabilidad, disponibilidad, mantenibilidad, compatibilidad, privacidad, etc.

| ID | Atributo | Requerimiento medible | Fuente | Prioridad | Evidencia / prueba |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **RNF-01** | Usabilidad | La interfaz del dashboard desarrollada en Dash debe ser intuitiva, permitiendo al personal de bienestar consultar las alertas de riesgo alto y aplicar filtros en un máximo de 4 clics desde el inicio de sesión. | Personal de Bienestar UTB/Pruebas de usabilidad. | Alta | Prueba de recorrido de usuario en la que el 90% de los evaluados complete la consulta de alertas en menos de 10 segundos. |
| **RNF-02** | Rendimiento | El tiempo de respuesta del sistema para procesar los datos, calcular los niveles de riesgo y renderizar los gráficos dinámicos en Dash debe ser menor o igual a 2.0 segundos. | Especificación técnica de arquitectura Dash. | Alta | Medición del tiempo de ejecución en la consola de desarrollo del navegador al aplicar filtros, verificando una latencia inferior a 2000 ms. |
| **RNF-03** | Seguridad | El sistema debe restringir el acceso al dashboard mediante autenticación obligatoria por usuario y contraseña, impidiendo el ingreso directo a rutas protegidas sin una sesión activa. | Módulo de autenticación/Diagrama de componentes | Alta | Intento de navegación directa hacia la URL interna del panel de control, validando la redirección automática a la vista de inicio de sesión. |
| **RNF-04** | Privacidad | El sistema operará de manera aislada utilizando exclusivamente una base de datos relacional poblada con mock data, garantizando la inexistencia de datos personales sensibles o reales de la UTB. | Alcance del proyecto | Alta | Confirmación de que el 100% de los registros corresponden a nombres e identificadores ficticios. |
| **RNF-05** | Compatibilidad | La aplicación web debe ser compatible y visualizase de forma correcta en los navegadores web modernos estándar (Google Chrome, Mozilla Firefox y Microsoft Edge). | Especificación de frontend web | Alta | Verificación del renderizado del dashboard en resoluciones estándar (1366x768 y 1920x1080) sin solapamiento de componentes visuales. |
| **RNF-06** | Mantenibilidad | El código del motor de cálculo de riesgo (MotorDeRiesgo) debe estar desacoplado de la interfaz de usuario en módulos independientes de Python, permitiendo modificar los umbrales de riesgo sin alterar el maquetado de Dash. | Diagrama de Clases / Buenas prácticas de arquitectura | Media | Inspección de código que demuestre la modificación del archivo de parámetros de umbral y su reflejo en el cálculo sin reescribir callbacks de Dash. |

### 10.3 Historias de usuario / casos de uso
Documente las funcionalidades principales. Para historias de usuario utilice: Como [rol], quiero [necesidad], para [beneficio], acompañada de criterios de aceptación.

**US-01: Autenticación de Usuarios en la Plataforma (RF-01)**
* **Historia de Usuario:** Como profesional del área de Bienestar Universitario, quiero iniciar sesión con mis credenciales institucionales seguras, para acceder al panel de alertas y proteger la privacidad de la información de los estudiantes.
* **Criterios de Aceptación:**
    1. El sistema presenta un formulario de inicio de sesión con campos de usuario y contraseña.
    2. Si las credenciales son válidas, redirige al usuario al dashboard principal (RF-04).
    3. Si las credenciales son incorrectas, muestra un mensaje de error claro sin exponer información sensible.

**US-02: Carga y Consolidación de Datos (RF-02)**
* **Historia de Usuario:** Como administrador técnico del sistema, quiero cargar y estructurar una base de datos con registros estudiantiles, para alimentar el sistema.
* **Criterios de Aceptación:**
    1. El sistema lee un archivo o estructura de datos relacional con información académica (promedio, asistencia, materias perdidas).
    2. Los datos cargados se encuentran estructurados y listos para ser procesados por el motor de riesgo.

**US-03: Algoritmo de Cálculo del Nivel de Riesgo (RF-03)**
* **Historia de Usuario:** Como profesional de acompañamiento estudiantil, quiero que el sistema evalúe automáticamente las variables académicas de cada estudiante, para clasificar su nivel de riesgo de deserción en Bajo, Medio o Alto.
* **Criterios de Aceptación:**
    1. El backend en Python procesa los indicadores académicos de la base de datos.
    2. Asigna una categoría de riesgo (Bajo, Medio, Alto) con base en umbrales de desempeño prefijados.
    3. El cálculo se ejecuta de forma automática al cargar o consultar la información.

**US-04: Panel Principal (Dashboard) de Alertas Tempranas (RF-04)**
* **Historia de Usuario:** Como usuario de Bienestar Universitario, quiero visualizar un dashboard interactivo desarrollado en Dash, para analizar gráficamente el estado general de los estudiantes y los indicadores de deserción por programa.
* **Criterios de Aceptación:**
    1. La interfaz muestra gráficos interactivos (Plotly) con la distribución total de estudiantes por nivel de riesgo.
    2. Presenta métricas consolidadas del número de casos críticos identificados.

**US-05: Visualización de Alertas Críticas - Resaltado en Rojo (RF-05)**
* **Historia de Usuario:** Como profesional de bienestar, quiero que las alertas de estudiantes en Riesgo Alto se destaquen con componentes visuales rojos, para priorizar de forma inmediata los casos más urgentes que requieren atención.
* **Criterios de Aceptación:**
    1. Las tarjetas de resumen y filas de la tabla correspondientes a "Riesgo Alto" se resaltan visualmente en color rojo.
    2. Se posicionan en el área superior de la interfaz para facilitar su detección rápida.

**US-06: Filtrado Dinámico de Estudiantes (RF-06)**
* **Historia de Usuario:** Como usuario de bienestar, quiero filtrar el listado de estudiantes por programa académico, semestre y nivel de riesgo, para realizar análisis focalizados en cohorts o facultades específicas de la UTB.
* **Criterios de Aceptación:**
    1. La interfaz incluye controles de selección desplegables (dropdowns) para programa y nivel de riesgo.
    2. Al cambiar un filtro, los gráficos y tablas del dashboard se actualizan dinámicamente sin recargar la página.

**US-07: Registro de Seguimiento Psicológico (RF-07)**
* **Historia de Usuario:** Como profesional del área de acompañamiento, quiero abrir una ventana modal al seleccionar un estudiante para registrar notas de seguimiento psicológico, para llevar un historial de las intervenciones humanas realizadas con cada caso en riesgo.
* **Criterios de Aceptación:**
    1. Al hacer clic en un estudiante en el dashboard, se despliega una ventana modal con el detalle del alumno.
    2. Incluye un formulario de texto donde el profesional puede redactar, guardar y consultar notas de seguimiento.

**US-08: Exportación de Listados a Formato CSV / Excel (RF-08)**
* **Historia de Usuario:** Como usuario de bienestar, quiero descargar el listado de estudiantes filtrados en formato CSV o Excel, para generar reportes impresos o compartirlos con la dirección académica de la UTB.
* **Criterios de Aceptación:**
    1. La interfaz cuenta con un botón "Exportar a Excel/CSV".
    2. Al presionar el botón, se descarga automáticamente un archivo estructurado con los datos filtrados en pantalla.

| ID | Historia / tarea | Prioridad | Estimación | Responsable | Estado |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **US-01** | Autenticación de Usuarios en la Plataforma (RF-01) | Alta | 3 pts | Equipo de Desarrollo | Pendiente |
| **US-02** | Carga y Consolidación de Datos (RF-02) | Alta | 5 pts | Equipo de Desarrollo | Pendiente |
| **US-03** | Algoritmo de Cálculo del Nivel de Riesgo (RF-03) | Alta | 8 pts | Equipo de Desarrollo | Pendiente |
| **US-04** | Panel Principal (Dashboard) de Alertas Tempranas (RF-04) | Alta | 8 pts | Equipo de Desarrollo | Pendiente |
| **US-05** | Visualización de Alertas Críticas en Rojo (RF-05) | Alta | 3 pts | Equipo de Desarrollo | Pendiente |
| **US-06** | Filtrado Dinámico de Estudiantes (RF-06) | Media | 5 pts | Equipo de Desarrollo | Pendiente |
| **US-07** | Registro de Seguimiento Psicológico (RF-07) | Alta | 5 pts | Equipo de Desarrollo | Pendiente |
| **US-08** | Exportación de Listados a Formato CSV / Excel (RF-08) | Baja | 2 pts | Equipo de Desarrollo | Pendiente |

### 10.5 Arquitectura de software
Incluya el diagrama de arquitectura y explique componentes, responsabilidades, comunicación entre componentes y principales decisiones técnicas.

*[Inserte aquí el diagrama de arquitectura]*

### 10.6 Modelo de datos
Incluya el modelo entidad-relación, modelo lógico o estructura de persistencia utilizada, según corresponda.

*[Inserte aquí el diagrama/modelo de datos]*

### 10.7 Diseño de interfaz / prototipo
Incluya wireframes, mockups o prototipos de las interfaces principales y explique el flujo de usuario.

*[Inserte aquí imágenes o enlace al prototipo]*

### 10.8 Tecnologías y herramientas

| Categoría | Tecnología / herramienta | Justificación |
| :--- | :--- | :--- |
| **Frontend** | Dash (Plotly Dash) / HTML / CSS | Permite construir tableros de control interactivos directamente en Python, ofreciendo componentes visuales reactivos y gráficos dinámicos ideales para la visualización de alertas. |
| **Backend** | Python (Flask / Dash Core) | Facilita el desarrollo rápido de la lógica del sistema y el desacoplamiento del motor de cálculo de riesgo (MotorDeRiesgo) en módulos limpios y mantenibles. |
| **Base de datos** | PostgreSQL | Ofrece un sistema de gestión de bases de datos relacional robusto y escalable, con excelente soporte para despliegues en la nube y un almacenamiento estructurado de los registros estudiantiles. |
| **Control de versiones** | Git y GitHub | Garantiza el control de cambios, el trabajo colaborativo en equipo y la trazabilidad del repositorio oficial del proyecto (IS_UTBAlert). |
| **Pruebas** | Pruebas unitarias (Módulo unittest / pytest) y pruebas funcionales | Permite verificar de manera automatizada la correcta ejecución del algoritmo de cálculo de riesgo y validar los criterios de aceptación del MVP. |
| **Despliegue / infraestructura** | Entorno local (Localhost) / Render | Ofrece un entorno de ejecución eficiente y accesible para levantar el servidor web de Dash durante el desarrollo y las sustentaciones académicas. |
| **Gestión del proyecto** | Trello (Tablero Kanban) | Facilita la organización de historias de usuario, el seguimiento de iteraciones (sprints) y la gestión ágil del flujo de trabajo del equipo. |

### 10.9 Plan de trabajo del segundo al tercer corte

| Sprint / Iteración | Objetivo | Entregables | Responsables | Fecha |
| :--- | :--- | :--- | :--- | :--- |
| Iteración 1 |  |  |  |  |
| Iteración 2 |  |  |  |  |
| Iteración 3 |  |  |  |  |
| Iteración 4 |  |  |  |  |

### 10.10 Riesgos

| Riesgo | Probabilidad | Impacto | Respuesta / mitigación | Responsable |
| :--- | :--- | :--- | :--- | :--- |
|  |  |  |  |  |

### 10.11 Evidencias requeridas para el segundo corte
* Documento actualizado hasta la sección 8.
* Backlog priorizado y planificación de iteraciones.
* Repositorio creado y con historial de trabajo del equipo.
* Arquitectura y modelo de datos definidos.
* Prototipo o diseño de las interfaces principales.
* Avance funcional demostrable acordado con el docente.
* Presentación o demostración del avance.