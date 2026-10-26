"""
Diccionario de mapeo de códigos de cursos a nombres de programas académicos de la UTB.
"""

PROGRAMAS_UTB = {
    33: "Ingeniería de Sistemas",
    171: "Ingeniería Industrial",
    8014: "Ingeniería Mecatrónica",
    9003: "Ingeniería Electrónica",
    9070: "Ingeniería Mecánica",
    9085: "Ingeniería Química",
    9119: "Ingeniería Civil",
    9130: "Ingeniería Ambiental",
    9147: "Administración de Empresas",
    9238: "Contaduría Pública",
    9254: "Economía",
    9500: "Finanzas y Negocios Internacionales",
    9556: "Comunicación Social y Medios Digitales",
    9670: "Psicología",
    9773: "Derecho",
    9853: "Ciencia de Datos",
    9991: "Arquitectura"
}

def obtener_nombre_programa(codigo_curso) -> str:
    """Devuelve el nombre amigable de la carrera según su código."""
    try:
        codigo_int = int(codigo_curso)
        return PROGRAMAS_UTB.get(codigo_int, f"Programa ({codigo_int})")
    except (ValueError, TypeError):
        return f"Programa ({codigo_curso})"
