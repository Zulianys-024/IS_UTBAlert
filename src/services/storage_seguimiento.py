"""
Servicio para la persistencia local de notas y bitácoras de seguimiento psicológico (RF-07).
Almacena los datos en formato JSON local: data/seguimiento_psicologico.json
"""

import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any
import uuid

DATA_DIR = Path(__file__).resolve().parents[2] / "data"
JSON_FILE = DATA_DIR / "seguimiento_psicologico.json"


class StorageSeguimiento:
    @staticmethod
    def _asegurar_archivo():
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        if not JSON_FILE.exists():
            with open(JSON_FILE, "w", encoding="utf-8") as f:
                json.dump({}, f, indent=2, ensure_ascii=False)

    @classmethod
    def obtener_todas_las_notas(cls) -> Dict[str, List[Dict[str, Any]]]:
        cls._asegurar_archivo()
        try:
            with open(JSON_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}

    @classmethod
    def obtener_notas_estudiante(cls, student_id: str) -> List[Dict[str, Any]]:
        todas = cls.obtener_todas_las_notas()
        return todas.get(str(student_id), [])

    @classmethod
    def contar_seguimientos_totales(cls) -> int:
        todas = cls.obtener_todas_las_notas()
        return sum(len(notas) for notas in todas.values())

    @classmethod
    def guardar_nota(
        cls,
        student_id: str,
        profesional: str,
        motivo: str,
        observaciones: str,
        compromisos: str = ""
    ) -> Dict[str, Any]:
        """Registra una nueva bitácora de seguimiento para el estudiante."""
        cls._asegurar_archivo()
        todas = cls.obtener_todas_las_notas()
        sid = str(student_id)

        nueva_nota = {
            "id": str(uuid.uuid4())[:8],
            "fecha": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "profesional": profesional or "Personal de Bienestar",
            "motivo": motivo,
            "observaciones": observaciones,
            "compromisos": compromisos
        }

        if sid not in todas:
            todas[sid] = []

        todas[sid].insert(0, nueva_nota)  # Más reciente primero

        with open(JSON_FILE, "w", encoding="utf-8") as f:
            json.dump(todas, f, indent=2, ensure_ascii=False)

        return nueva_nota
