"""Crea las cuentas administradoras iniciales a partir de admins.local.json.

Uso:
    python seed_admins.py

El archivo admins.local.json no se versiona y contiene las contraseñas en claro;
este script solo guarda sus hashes. Nunca imprime contraseñas.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

from utbapp.auth import (
    ALLOWED_EMAIL_DOMAIN,
    MIN_PASSWORD_LENGTH,
    USERS_DB,
    create_admin,
    init_db,
    normalize_email,
    normalize_gender,
    validate_email,
    validate_password,
)

ROOT = Path(__file__).resolve().parent
ADMINS_FILE = ROOT / "admins.local.json"


def load_records(path: Path) -> list[dict]:
    if not path.exists():
        raise FileNotFoundError(
            f"No se encontró {path.name}. Crea el archivo con la lista de administradores."
        )
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"{path.name} no contiene JSON válido.") from exc
    if isinstance(data, dict):
        data = [data]
    if not isinstance(data, list) or not data:
        raise ValueError(f"{path.name} debe contener una lista de administradores.")
    return data


def validate_records(records: list[dict]) -> list[dict]:
    valid = []
    errors = []
    for index, record in enumerate(records, start=1):
        if not isinstance(record, dict):
            errors.append(f"Registro {index}: formato inválido.")
            continue
        nombre = str(record.get("nombre") or "").strip()
        correo = normalize_email(record.get("correo"))
        password = record.get("password") or ""
        genero_raw = record.get("genero")
        label = f"Registro {index} ({correo or 'sin correo'})"
        try:
            if not nombre:
                raise ValueError("falta el nombre")
            validate_email(correo)
            validate_password(password)
            if genero_raw in (None, ""):
                genero = None
            else:
                genero = normalize_gender(genero_raw)
                if not genero:
                    raise ValueError("género inválido (usa M o F)")
        except ValueError as exc:
            errors.append(f"{label}: {exc}")
            continue
        valid.append({"nombre": nombre, "correo": correo, "password": password, "genero": genero})
    if errors:
        raise ValueError("\n".join(errors))
    return valid


def main() -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass
    try:
        records = validate_records(load_records(ADMINS_FILE))
    except (FileNotFoundError, ValueError) as exc:
        print(f"Error: {exc}")
        return 1

    init_db()
    print(f"Base de datos: {USERS_DB.name}")
    print(f"Dominio permitido: @{ALLOWED_EMAIL_DOMAIN}")
    print(f"Contraseña mínima: {MIN_PASSWORD_LENGTH} caracteres\n")

    created = 0
    for record in records:
        status, user = create_admin(
            record["nombre"],
            record["correo"],
            record["password"],
            rol="admin",
            debe_cambiar_password=True,
            genero=record["genero"],
        )
        if status == "created":
            created += 1
            print(f"[creado]    {user['nombre']} <{user['correo']}>")
        else:
            print(f"[existente] {user['nombre']} <{user['correo']}> · contraseña sin cambios")

    print(f"\nListo: {created} cuenta(s) nueva(s), {len(records) - created} ya existente(s).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
