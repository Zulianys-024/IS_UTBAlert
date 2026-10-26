"""
Motor de Cálculo de Riesgo Académico para UTBAlert.
Alineado con el Reglamento Estudiantil de la Universidad Tecnológica de Bolívar (UTB).

Reglas de Negocio:
- Estandarización de calificaciones: Las notas base 0-20 se promedian y se estandarizan a escala UTB (0.0 a 5.0).
- PPA = Promedio Ponderado Acumulado.
- Riesgo Alto (🔴): PPA <= 3.20 (Prueba Académica según reglamento) O Asistencia < 70%.
- Riesgo Medio (🟡): 3.20 < PPA < 3.70 O 70% <= Asistencia < 80%.
- Riesgo Bajo (🟢): PPA >= 3.70 Y Asistencia >= 80%.
"""

from typing import Tuple, Dict, Any
import pandas as pd


class MotorDeRiesgo:
    # Umbrales configurables (RNF-06 Mantenibilidad)
    UMBRAL_PRUEBA_ACADEMICA = 3.20   # Límite superior de Prueba Académica UTB
    UMBRAL_RIESGO_MEDIO_PPA = 3.70   # Límite superior de alerta media de PPA
    UMBRAL_ASISTENCIA_CRITICA = 70.0 # Por debajo es crítico (Riesgo Alto)
    UMBRAL_ASISTENCIA_MEDIA = 80.0   # Entre 70% y 79.9% es alerta preventiva

    @staticmethod
    def estandarizar_nota_a_escala_5(nota_base_20: float) -> float:
        """Convierte una nota de escala 0-20 a escala colombiana 0.0 - 5.0."""
        if pd.isna(nota_base_20) or nota_base_20 is None:
            return 0.0
        # Regla de tres: (nota / 20.0) * 5.0
        nota_5 = (float(nota_base_20) / 20.0) * 5.0
        return round(max(0.0, min(5.0, nota_5)), 2)

    @classmethod
    def calcular_ppa(cls, nota_sem1: float, nota_sem2: float) -> float:
        """
        Calcula el PPA estandarizado promediando las notas de ambos semestres.
        Si alguna es NaN o vacía, toma el semestre válido.
        """
        valid_grades = []
        if pd.notna(nota_sem1) and nota_sem1 is not None:
            valid_grades.append(float(nota_sem1))
        if pd.notna(nota_sem2) and nota_sem2 is not None:
            valid_grades.append(float(nota_sem2))

        if not valid_grades:
            return 0.0

        promedio_base_20 = sum(valid_grades) / len(valid_grades)
        return cls.estandarizar_nota_a_escala_5(promedio_base_20)

    @classmethod
    def evaluar_estudiante(cls, ppa: float, asistencia: float) -> Tuple[str, str, str]:
        """
        Clasifica a un estudiante según su PPA y porcentaje de asistencia.
        Retorna:
          (nivel_riesgo, color_badge, motivo_diagnostico)
        """
        ppa = float(ppa) if pd.notna(ppa) else 0.0
        asistencia = float(asistencia) if pd.notna(asistencia) else 0.0

        motivos = []
        if ppa <= cls.UMBRAL_PRUEBA_ACADEMICA:
            motivos.append(f"PPA en Prueba Académica ({ppa:.2f} ≤ {cls.UMBRAL_PRUEBA_ACADEMICA})")
        if asistencia < cls.UMBRAL_ASISTENCIA_CRITICA:
            motivos.append(f"Inasistencia Crítica ({asistencia:.1f}% < {cls.UMBRAL_ASISTENCIA_CRITICA}%)")

        if ppa <= cls.UMBRAL_PRUEBA_ACADEMICA or asistencia < cls.UMBRAL_ASISTENCIA_CRITICA:
            return "Alto", "danger", " & ".join(motivos) if motivos else "Riesgo crítico detectado"

        # Riesgo Medio
        if ppa < cls.UMBRAL_RIESGO_MEDIO_PPA or asistencia < cls.UMBRAL_ASISTENCIA_MEDIA:
            motivos_medios = []
            if ppa < cls.UMBRAL_RIESGO_MEDIO_PPA:
                motivos_medios.append(f"PPA en observación ({ppa:.2f})")
            if asistencia < cls.UMBRAL_ASISTENCIA_MEDIA:
                motivos_medios.append(f"Asistencia irregular ({asistencia:.1f}%)")
            return "Medio", "warning", " & ".join(motivos_medios)

        # Riesgo Bajo
        return "Bajo", "success", "Rendimiento y asistencia satisfactorios"

    @classmethod
    def procesar_dataframe(cls, df: pd.DataFrame) -> pd.DataFrame:
        """
        Procesa el DataFrame cargado de la BD o CSV:
        - Calcula el PPA estandarizado (0.0 - 5.0)
        - Asigna nivel_riesgo, badge_color y motivo
        """
        df = df.copy()

        # Asegurar nombres normalizados
        col_s1 = "curricular_units_1st_sem_grade"
        col_s2 = "curricular_units_2nd_sem_grade"
        col_asist = "attendance_percentage"

        # Calcular PPA fila por fila
        df["ppa"] = df.apply(
            lambda r: cls.calcular_ppa(r.get(col_s1), r.get(col_s2)), axis=1
        )

        # Asignar riesgo
        evaluaciones = df.apply(
            lambda r: cls.evaluar_estudiante(r["ppa"], r.get(col_asist, 0.0)), axis=1
        )
        df["nivel_riesgo"] = [ev[0] for ev in evaluaciones]
        df["badge_color"] = [ev[1] for ev in evaluaciones]
        df["motivo_riesgo"] = [ev[2] for ev in evaluaciones]

        return df
