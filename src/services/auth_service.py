"""
Servicio simple de autenticación en sesión para UTBAlert (RF-01).
Permite acceso a roles de Bienestar Universitario y Administrador.
"""

from typing import Optional, Dict

USUARIOS_REGISTRADOS = {
    "juanavila@utb.edu.co": {
        "password": "juandavid123",
        "nombre": "Juan David Ávila",
        "rol": "Bienestar Universitario"
    },
    "bmaluenga@utb.edu.co": {
        "password": "brayanalberto456",
        "nombre": "Brayan Alberto Maluenga",
        "rol": "Bienestar Universitario"
    },
    "orozcoz@utb.edu.co": {
        "password": "zulianysliseth789",
        "nombre": "Zulianys Liseth Orozco",
        "rol": "Bienestar Universitario"
    },
    "admin@utb.edu.co": {
        "password": "adminutbalert",
        "nombre": "Administrador UTB",
        "rol": "Administrador"
    }
}


class AuthService:
    @staticmethod
    def validar_credenciales(email: str, password: str) -> Optional[Dict[str, str]]:
        if not email or not password:
            return None
        email_clean = email.strip().lower()
        usuario = USUARIOS_REGISTRADOS.get(email_clean)
        if usuario and usuario["password"] == password.strip():
            return {
                "email": email_clean,
                "nombre": usuario["nombre"],
                "rol": usuario["rol"]
            }
        return None
