import numpy as np
import pandas as pd
from pathlib import Path

np.random.seed(42)

N_ESTUDIANTES = 1000
SEMESTRES_MAXIMOS = 10
ID_ESTUDIANTE_INICIAL = 11111

PROGRAMAS = {
    "Ingeniería Industrial": 169,
    "Ingeniería Civil": 170,
    "Ingeniería Electrónica": 170,
    "Ingeniería Mecatrónica": 172,
    "Ingeniería de Sistemas y Computación": 162,
    "Ingeniería Biomédica": 169,
    "Arquitectura": 170,
    "Ingeniería Ambiental": 171,
    "Ingeniería Química": 175,
    "Ingeniería Naval": 168,
    "Ingeniería Mecánica": 172,
}

PERIODOS = [
    "202201", "202202", "202301", "202302", "202401",
    "202402", "202501", "202502", "202601"
]

CREDITOS_POR_ASIGNATURA = 3
ASIGNATURAS_POR_SEMESTRE = 6
NOTA_MINIMA_APROBACION = 3.0
UMBRAL_PRUEBA_ACADEMICA = 3.20


def generar_codigo_estudiante(numero: int) -> str:
    """
    Genera identificadores tipo T00011111, T00011112, ...
    T000 es fijo y los cinco dígitos finales cambian.
    """
    return f"T000{numero:05d}"


def generar_nota(perfil: int) -> float:
    """
    perfil:
    0 = alto riesgo
    1 = riesgo medio
    2 = buen rendimiento
    """
    if perfil == 0:
        nota = np.random.normal(2.4, 0.8)
    elif perfil == 1:
        nota = np.random.normal(3.3, 0.6)
    else:
        nota = np.random.normal(4.1, 0.5)

    return round(float(np.clip(nota, 0.0, 5.0)), 2)


def clasificar_estado_academico(
    promedio_acumulado: float,
    materias_reprobadas_periodo: int,
    retraso_academico: int
) -> str:
    if (
        promedio_acumulado < 2.80
        and materias_reprobadas_periodo >= 3
        and retraso_academico >= 3
    ):
        return "PRUEBA_ACADEMICA_TOTAL"

    if promedio_acumulado < UMBRAL_PRUEBA_ACADEMICA:
        return "PRUEBA_ACADEMICA_PARCIAL"

    if promedio_acumulado < 3.50:
        return "RIESGO_ACADEMICO"

    return "REGULAR"


estudiantes = []
historial = []

for numero in range(
    ID_ESTUDIANTE_INICIAL,
    ID_ESTUDIANTE_INICIAL + N_ESTUDIANTES
):
    estudiante_id = generar_codigo_estudiante(numero)

    programa = np.random.choice(list(PROGRAMAS.keys()))
    creditos_plan = PROGRAMAS[programa]

    # El estudiante ingresa en uno de los primeros seis periodos
    posicion_ingreso = int(np.random.randint(0, 6))
    periodo_ingreso = PERIODOS[posicion_ingreso]

    # Perfil académico inicial
    perfil_inicial = int(
        np.random.choice([0, 1, 2], p=[0.20, 0.35, 0.45])
    )

    # Cantidad de semestres cursados
    if perfil_inicial == 0:
        semestres_cursados = int(np.random.randint(1, 5))
    elif perfil_inicial == 1:
        semestres_cursados = int(np.random.randint(2, 7))
    else:
        semestres_cursados = int(
            np.random.randint(3, SEMESTRES_MAXIMOS + 1)
        )

    # Evita registrar semestres que no tienen un periodo disponible en el dataset.
    semestres_cursados = min(
        semestres_cursados,
        len(PERIODOS) - posicion_ingreso,
    )

    # Probabilidad de deserción según perfil
    if perfil_inicial == 0:
        deserto = np.random.random() < 0.65
    elif perfil_inicial == 1:
        deserto = np.random.random() < 0.25
    else:
        deserto = np.random.random() < 0.05

    if deserto:
        estado_final = "DESERTOR"
    elif semestres_cursados >= 8:
        estado_final = "GRADUADO"
    else:
        estado_final = "ACTIVO"

    # Acumulados
    creditos_cursados_acumulados = 0
    creditos_aprobados_acumulados = 0
    creditos_reprobados_acumulados = 0
    puntos_acumulados = 0.0
    promedio_acumulado = 0.0
    retraso_academico = 0
    materias_reprobadas_acumuladas = 0
    nivel_actual = 1

    for indice_periodo in range(
        posicion_ingreso,
        min(posicion_ingreso + semestres_cursados, len(PERIODOS))
    ):
        periodo_academico = PERIODOS[indice_periodo]

        # Si ya está en riesgo, su desempeño tiende a empeorar
        if promedio_acumulado < UMBRAL_PRUEBA_ACADEMICA:
            perfil_actual = min(perfil_inicial, 1)
        else:
            perfil_actual = perfil_inicial

        # Cancelaciones
        if np.random.random() < 0.15:
            asignaturas_canceladas = int(np.random.randint(1, 3))
        else:
            asignaturas_canceladas = 0

        asignaturas_inscritas = ASIGNATURAS_POR_SEMESTRE
        asignaturas_cursadas = (
            asignaturas_inscritas - asignaturas_canceladas
        )

        creditos_inscritos = (
            asignaturas_inscritas * CREDITOS_POR_ASIGNATURA
        )
        creditos_cursados = (
            asignaturas_cursadas * CREDITOS_POR_ASIGNATURA
        )

        # Reprobaciones
        if perfil_actual == 0:
            asignaturas_reprobadas = int(
                np.random.randint(2, asignaturas_cursadas + 1)
            )
            asistencia = float(
                np.random.uniform(45.0, 70.0)
            )
        elif perfil_actual == 1:
            asignaturas_reprobadas = int(
                np.random.choice([0, 1, 2], p=[0.45, 0.40, 0.15])
            )
            asistencia = float(
                np.random.uniform(70.0, 85.0)
            )
        else:
            asignaturas_reprobadas = int(
                np.random.choice([0, 1], p=[0.88, 0.12])
            )
            asistencia = float(
                np.random.uniform(82.0, 100.0)
            )

        asignaturas_reprobadas = min(
            asignaturas_reprobadas,
            asignaturas_cursadas
        )
        asignaturas_aprobadas = (
            asignaturas_cursadas - asignaturas_reprobadas
        )

        # Genera notas y calcula promedio ponderado del semestre
        puntos_semestre = 0.0
        for _ in range(asignaturas_cursadas):
            nota = generar_nota(perfil_actual)
            puntos_semestre += nota * CREDITOS_POR_ASIGNATURA

        if creditos_cursados > 0:
            promedio_semestre = round(
                puntos_semestre / creditos_cursados, 2
            )
        else:
            promedio_semestre = 0.0

        # Actualiza acumulados
        creditos_aprobados_periodo = (
            asignaturas_aprobadas * CREDITOS_POR_ASIGNATURA
        )
        creditos_reprobados_periodo = (
            asignaturas_reprobadas * CREDITOS_POR_ASIGNATURA
        )

        creditos_cursados_acumulados += creditos_cursados
        creditos_aprobados_acumulados += creditos_aprobados_periodo
        creditos_reprobados_acumulados += creditos_reprobados_periodo
        materias_reprobadas_acumuladas += asignaturas_reprobadas

        # Promedio acumulado ponderado por créditos CURSADOS,
        # no solo aprobados
        puntos_acumulados += puntos_semestre

        if creditos_cursados_acumulados > 0:
            promedio_acumulado = round(
                puntos_acumulados / creditos_cursados_acumulados,
                2
            )

        # Retraso académico
        if asignaturas_reprobadas > 0:
            retraso_academico += asignaturas_reprobadas
        elif retraso_academico > 0 and promedio_semestre >= 4.0:
            retraso_academico -= 1

        # Avance del plan usando los créditos reales del programa
        avance_plan = round(
            (creditos_aprobados_acumulados / creditos_plan) * 100,
            2
        )
        avance_plan = min(avance_plan, 100.0)

        # El nivel avanza cada semestre cursado
        estado_academico = clasificar_estado_academico(
            promedio_acumulado,
            asignaturas_reprobadas,
            retraso_academico
        )

        historial.append({
            "estudiante_id": estudiante_id,
            "programa": programa,
            "periodo_academico": periodo_academico,
            "nivel_actual": nivel_actual,
            "promedio_ponderado_semestre": promedio_semestre,
            "promedio_ponderado_acumulado": promedio_acumulado,
            "asignaturas_inscritas": asignaturas_inscritas,
            "asignaturas_cursadas": asignaturas_cursadas,
            "asignaturas_aprobadas": asignaturas_aprobadas,
            "asignaturas_reprobadas_periodo": asignaturas_reprobadas,
            "asignaturas_reprobadas_acumuladas": materias_reprobadas_acumuladas,
            "asignaturas_canceladas": asignaturas_canceladas,
            "creditos_inscritos": creditos_inscritos,
            "creditos_cursados": creditos_cursados,
            "creditos_aprobados": creditos_aprobados_periodo,
            "creditos_reprobados_acumulados": creditos_reprobados_acumulados,
            "avance_plan": avance_plan,
            "retraso_academico": retraso_academico,
            "porcentaje_asistencia": round(asistencia, 2),
            "estado_academico": estado_academico,
            "deserto": deserto,
            "estado_final": estado_final
        })

        nivel_actual += 1

    # Estado de permanencia final aproximado
    if promedio_acumulado < 2.80 and retraso_academico >= 3:
        estado_permanencia = "PÉRDIDA_CARRERA"
    elif promedio_acumulado < UMBRAL_PRUEBA_ACADEMICA:
        estado_permanencia = "CONDICIONADO"
    else:
        estado_permanencia = "REGULAR"

    estudiantes.append({
        "estudiante_id": estudiante_id,
        "programa": programa,
        "periodo_ingreso": periodo_ingreso,
        "nivel_actual": nivel_actual - 1,
        "estado_permanencia": estado_permanencia,
        "semestres_cursados": semestres_cursados,
        "promedio_acumulado_final": promedio_acumulado,
        "creditos_aprobados_totales": creditos_aprobados_acumulados,
        "creditos_cursados_totales": creditos_cursados_acumulados,
        "creditos_reprobados_totales": creditos_reprobados_acumulados,
        "avance_plan_final": min(
            round((creditos_aprobados_acumulados / creditos_plan) * 100, 2),
            100.0,
        ),
        "estado_final": estado_final
    })

df_estudiantes = pd.DataFrame(estudiantes)
df_historial = pd.DataFrame(historial)

project_root = Path(__file__).resolve().parents[1]
salidas = [
    project_root / "data" / "synthetic",
    project_root / "data" / "processed",
]

for salida in salidas:
    salida.mkdir(parents=True, exist_ok=True)
    df_estudiantes.to_csv(
        salida / "estudiantes_utb_sinteticos.csv",
        index=False,
        encoding="utf-8-sig"
    )
    df_historial.to_csv(
        salida / "historial_academico_utb_sintetico.csv",
        index=False,
        encoding="utf-8-sig"
    )

print("Datos sintéticos generados correctamente")
print(f"Estudiantes: {len(df_estudiantes)}")
print(f"Registros de historial: {len(df_historial)}")
print("\nDistribución por estado final:")
print(df_estudiantes["estado_final"].value_counts())
print("\nDistribución por estado académico:")
print(df_historial["estado_academico"].value_counts())
