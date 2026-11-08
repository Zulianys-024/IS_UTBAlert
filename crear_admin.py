"""CLI para administrar las cuentas de UTBAlert.

Ejemplos:
    python crear_admin.py
    python crear_admin.py --cambiar-password correo@utb.edu.co
    python crear_admin.py --desactivar correo@utb.edu.co
    python crear_admin.py --activar correo@utb.edu.co
    python crear_admin.py --listar

Las contraseñas se piden con getpass y nunca se muestran ni se guardan en claro.
"""

from __future__ import annotations

import argparse
import getpass
import sys

from utbapp.auth import (
    ALLOWED_EMAIL_DOMAIN,
    MIN_PASSWORD_LENGTH,
    create_admin,
    init_db,
    list_users,
    normalize_email,
    normalize_gender,
    set_active,
    set_password,
    validate_email,
    validate_password,
)


def ask_password(label: str = "Contraseña") -> str:
    while True:
        first = getpass.getpass(f"{label}: ")
        try:
            validate_password(first)
        except ValueError as exc:
            print(f"  {exc}")
            continue
        second = getpass.getpass("Confirma la contraseña: ")
        if first != second:
            print("  Las contraseñas no coinciden. Inténtalo de nuevo.")
            continue
        return first


def ask_gender() -> str | None:
    while True:
        raw = input("Género (M/F, opcional): ").strip()
        if not raw:
            return None
        genero = normalize_gender(raw)
        if genero:
            return genero
        print("  Usa M o F (o deja vacío para no definirlo).")


def add_admin() -> int:
    print(f"Alta de administrador · dominio @{ALLOWED_EMAIL_DOMAIN}")
    nombre = input("Nombre completo: ").strip()
    if not nombre:
        print("Error: el nombre es obligatorio.")
        return 1
    correo = input("Correo institucional: ").strip()
    try:
        correo = validate_email(correo)
    except ValueError as exc:
        print(f"Error: {exc}")
        return 1
    genero = ask_gender()
    password = ask_password()
    status, user = create_admin(
        nombre,
        correo,
        password,
        rol="admin",
        debe_cambiar_password=True,
        genero=genero,
    )
    if status == "created":
        print(f"[creado] {user['nombre']} <{user['correo']}> · deberá cambiar la contraseña al entrar")
    else:
        print(f"[existente] {user['nombre']} <{user['correo']}> · nombre actualizado, contraseña sin cambios")
    return 0


def change_password(correo: str) -> int:
    try:
        correo = validate_email(correo)
    except ValueError as exc:
        print(f"Error: {exc}")
        return 1
    print(f"Cambio de contraseña para {correo}")
    password = ask_password("Contraseña nueva")
    try:
        user = set_password(correo, password)
    except ValueError as exc:
        print(f"Error: {exc}")
        return 1
    print(f"[actualizado] {user['nombre']} <{user['correo']}>")
    return 0


def toggle_active(correo: str, active: bool) -> int:
    try:
        correo = validate_email(correo)
    except ValueError as exc:
        print(f"Error: {exc}")
        return 1
    try:
        user = set_active(correo, active)
    except ValueError as exc:
        print(f"Error: {exc}")
        return 1
    estado = "activo" if user["activo"] else "desactivado"
    print(f"[{estado}] {user['nombre']} <{user['correo']}>")
    return 0


def show_users() -> int:
    users = list_users()
    if not users:
        print("No hay usuarios registrados.")
        return 0
    for user in users:
        estado = "activo" if user["activo"] else "inactivo"
        cambio = " · debe cambiar contraseña" if user["debe_cambiar_password"] else ""
        ultimo = user.get("ultimo_acceso") or "sin acceso"
        print(f"{user['nombre']} <{user['correo']}> · {user['rol']} · {estado}{cambio} · último acceso: {ultimo}")
    return 0


def main(argv: list[str] | None = None) -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass
    parser = argparse.ArgumentParser(description="Administración de cuentas de UTBAlert")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--cambiar-password", metavar="CORREO", help="cambia la contraseña de una cuenta")
    group.add_argument("--desactivar", metavar="CORREO", help="desactiva una cuenta")
    group.add_argument("--activar", metavar="CORREO", help="reactiva una cuenta")
    group.add_argument("--listar", action="store_true", help="lista las cuentas registradas")
    args = parser.parse_args(argv)

    init_db()
    if args.listar:
        return show_users()
    if args.cambiar_password:
        return change_password(args.cambiar_password)
    if args.desactivar:
        return toggle_active(args.desactivar, False)
    if args.activar:
        return toggle_active(args.activar, True)
    return add_admin()


if __name__ == "__main__":
    sys.exit(main())
