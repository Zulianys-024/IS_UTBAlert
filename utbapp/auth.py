"""Autenticación local para UTBAlert.

Base SQLite con contraseñas hasheadas, validación del dominio institucional y
bloqueo temporal tras varios intentos fallidos.
"""

from __future__ import annotations

import os
import sqlite3
import threading
import time
from datetime import datetime
from math import ceil
from pathlib import Path

from dotenv import load_dotenv
from werkzeug.security import check_password_hash, generate_password_hash

from utbapp.i18n import tr

ROOT = Path(__file__).resolve().parents[1]
load_dotenv(ROOT / ".env")

USERS_DB = Path(os.getenv("USERS_DB", str(ROOT / "users.db")))
ALLOWED_EMAIL_DOMAIN = os.getenv("ALLOWED_EMAIL_DOMAIN", "utb.edu.co").strip().lower().lstrip("@")
MIN_PASSWORD_LENGTH = 8
MAX_FAILED_ATTEMPTS = 5
LOCKOUT_MINUTES = int(os.getenv("LOCKOUT_MINUTES", "5"))
PERMANENT_SESSION_DAYS = 30


def normalize_email(value: str | None) -> str:
    return (value or "").strip().lower()


def is_allowed_email(value: str | None) -> bool:
    correo = normalize_email(value)
    return bool(correo) and correo.endswith(f"@{ALLOWED_EMAIL_DOMAIN}") and correo != f"@{ALLOWED_EMAIL_DOMAIN}"


def validate_email(value: str | None) -> str:
    correo = normalize_email(value)
    if not is_allowed_email(correo):
        raise ValueError(f"El correo debe pertenecer al dominio @{ALLOWED_EMAIL_DOMAIN}.")
    return correo


def validate_password(value: str | None) -> str:
    password = value or ""
    if len(password) < MIN_PASSWORD_LENGTH:
        raise ValueError(f"La contraseña debe tener al menos {MIN_PASSWORD_LENGTH} caracteres.")
    return password


def normalize_gender(value: str | None) -> str | None:
    """Normaliza el género a ``"M"``/``"F"``; devuelve ``None`` si no está definido."""
    genero = (value or "").strip().upper()
    if genero in {"M", "MASCULINO", "HOMBRE"}:
        return "M"
    if genero in {"F", "FEMENINO", "MUJER"}:
        return "F"
    return None


def etiqueta_rol(rol: str | None, genero: str | None, lang: str = "es") -> str:
    """Etiqueta del rol según género; usado en cabecera, menú y perfil."""
    if (rol or "").strip().lower() == "admin":
        genero = normalize_gender(genero)
        if genero == "M":
            return tr(lang, "role.admin_m")
        if genero == "F":
            return tr(lang, "role.admin_f")
        return tr(lang, "role.admin_neutral")
    return (rol or "").strip().capitalize() or tr(lang, "role.admin_neutral")


def _connect() -> sqlite3.Connection:
    USERS_DB.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(USERS_DB, timeout=10)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    with _connect() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS usuarios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL,
                correo TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL,
                rol TEXT NOT NULL DEFAULT 'admin',
                genero TEXT,
                activo INTEGER NOT NULL DEFAULT 1,
                debe_cambiar_password INTEGER NOT NULL DEFAULT 1,
                creado_en TEXT NOT NULL,
                ultimo_acceso TEXT
            )
            """
        )
        conn.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_usuarios_correo ON usuarios (correo)")
        columns = {row[1] for row in conn.execute("PRAGMA table_info(usuarios)")}
        if "genero" not in columns:
            conn.execute("ALTER TABLE usuarios ADD COLUMN genero TEXT")


def _row_to_dict(row: sqlite3.Row | None) -> dict | None:
    if row is None:
        return None
    user = dict(row)
    user["activo"] = bool(user.get("activo"))
    user["debe_cambiar_password"] = bool(user.get("debe_cambiar_password"))
    return user


def get_user_by_email(correo: str | None) -> dict | None:
    correo = normalize_email(correo)
    if not correo:
        return None
    with _connect() as conn:
        row = conn.execute("SELECT * FROM usuarios WHERE correo = ?", (correo,)).fetchone()
    return _row_to_dict(row)


def get_user_by_id(user_id) -> dict | None:
    try:
        user_id = int(user_id)
    except (TypeError, ValueError):
        return None
    with _connect() as conn:
        row = conn.execute("SELECT * FROM usuarios WHERE id = ?", (user_id,)).fetchone()
    return _row_to_dict(row)


def list_users() -> list[dict]:
    with _connect() as conn:
        rows = conn.execute("SELECT * FROM usuarios ORDER BY nombre COLLATE NOCASE").fetchall()
    return [_row_to_dict(row) for row in rows]


def create_admin(
    nombre: str,
    correo: str | None,
    password: str | None,
    rol: str = "admin",
    debe_cambiar_password: bool = True,
    genero: str | None = None,
) -> tuple[str, dict]:
    """Crea un administrador o actualiza nombre/género si el correo ya existe.

    Nunca sobrescribe la contraseña de una cuenta existente. Devuelve
    ``("created"|"existing"|"updated", usuario)``.
    """
    nombre = (nombre or "").strip()
    correo = validate_email(correo)
    password = validate_password(password)
    genero = normalize_gender(genero)
    if not nombre:
        raise ValueError("El nombre es obligatorio.")

    init_db()
    existing = get_user_by_email(correo)
    with _connect() as conn:
        if existing:
            if genero:
                conn.execute(
                    "UPDATE usuarios SET nombre = ?, genero = ? WHERE id = ?",
                    (nombre, genero, existing["id"]),
                )
            else:
                conn.execute("UPDATE usuarios SET nombre = ? WHERE id = ?", (nombre, existing["id"]))
            return "updated", get_user_by_id(existing["id"])
        conn.execute(
            """
            INSERT INTO usuarios (nombre, correo, password_hash, rol, genero, activo, debe_cambiar_password, creado_en)
            VALUES (?, ?, ?, ?, ?, 1, ?, ?)
            """,
            (
                nombre,
                correo,
                generate_password_hash(password),
                rol,
                genero,
                int(bool(debe_cambiar_password)),
                datetime.now().isoformat(timespec="seconds"),
            ),
        )
    return "created", get_user_by_email(correo)


def authenticate(correo: str | None, password: str | None) -> dict | None:
    """Devuelve el usuario activo si el correo y la contraseña son válidos."""
    user = get_user_by_email(correo)
    if not user or not user["activo"]:
        return None
    if not check_password_hash(user["password_hash"], password or ""):
        return None
    return user


def record_login(user_id: int) -> dict | None:
    with _connect() as conn:
        conn.execute(
            "UPDATE usuarios SET ultimo_acceso = ? WHERE id = ?",
            (datetime.now().isoformat(timespec="seconds"), user_id),
        )
    return get_user_by_id(user_id)


def update_name(user_id: int, nombre: str) -> dict | None:
    nombre = (nombre or "").strip()
    if not nombre:
        raise ValueError("El nombre es obligatorio.")
    with _connect() as conn:
        conn.execute("UPDATE usuarios SET nombre = ? WHERE id = ?", (nombre, user_id))
    return get_user_by_id(user_id)


def set_password(correo: str | None, new_password: str | None, require_change: bool = False) -> dict:
    correo = validate_email(correo)
    new_password = validate_password(new_password)
    user = get_user_by_email(correo)
    if not user:
        raise ValueError("No existe un usuario con ese correo.")
    if check_password_hash(user["password_hash"], new_password):
        raise ValueError("La contraseña nueva debe ser distinta de la anterior.")
    with _connect() as conn:
        conn.execute(
            "UPDATE usuarios SET password_hash = ?, debe_cambiar_password = ? WHERE id = ?",
            (generate_password_hash(new_password), int(bool(require_change)), user["id"]),
        )
    return get_user_by_id(user["id"])


def change_own_password(user_id: int, current_password: str | None, new_password: str | None) -> dict:
    user = get_user_by_id(user_id)
    if not user or not user["activo"]:
        raise ValueError("La sesión no es válida.")
    if not check_password_hash(user["password_hash"], current_password or ""):
        raise ValueError("La contraseña actual no es correcta.")
    new_password = validate_password(new_password)
    if check_password_hash(user["password_hash"], new_password):
        raise ValueError("La contraseña nueva debe ser distinta de la anterior.")
    with _connect() as conn:
        conn.execute(
            "UPDATE usuarios SET password_hash = ?, debe_cambiar_password = 0 WHERE id = ?",
            (generate_password_hash(new_password), user_id),
        )
    return get_user_by_id(user_id)


def change_password_after_login(user_id: int, new_password: str | None) -> dict:
    """Cambio obligatorio tras el primer acceso: no pide la contraseña anterior."""
    user = get_user_by_id(user_id)
    if not user or not user["activo"]:
        raise ValueError("La sesión no es válida.")
    new_password = validate_password(new_password)
    if check_password_hash(user["password_hash"], new_password):
        raise ValueError("La contraseña nueva debe ser distinta de la anterior.")
    with _connect() as conn:
        conn.execute(
            "UPDATE usuarios SET password_hash = ?, debe_cambiar_password = 0 WHERE id = ?",
            (generate_password_hash(new_password), user_id),
        )
    return get_user_by_id(user_id)


def set_active(correo: str | None, active: bool) -> dict:
    correo = validate_email(correo)
    user = get_user_by_email(correo)
    if not user:
        raise ValueError("No existe un usuario con ese correo.")
    with _connect() as conn:
        conn.execute("UPDATE usuarios SET activo = ? WHERE id = ?", (int(bool(active)), user["id"]))
    return get_user_by_id(user["id"])


# ---------- Límite de intentos fallidos (por correo e IP) ----------
_attempts: dict[str, dict] = {}
_attempts_lock = threading.Lock()


def _keys(correo: str | None, ip: str | None) -> list[str]:
    keys = []
    correo = normalize_email(correo)
    if correo:
        keys.append(f"email:{correo}")
    if ip:
        keys.append(f"ip:{ip}")
    return keys


def lockout_seconds(correo: str | None, ip: str | None) -> int:
    now = time.time()
    remaining = 0
    with _attempts_lock:
        for key in _keys(correo, ip):
            state = _attempts.get(key)
            if not state:
                continue
            until = state.get("until", 0)
            if until > now:
                remaining = max(remaining, ceil(until - now))
            elif until:
                _attempts.pop(key, None)
    return remaining


def register_failure(correo: str | None, ip: str | None) -> int:
    """Suma un fallo y devuelve los segundos de bloqueo si se alcanzó el límite."""
    now = time.time()
    seconds = 0
    with _attempts_lock:
        for key in _keys(correo, ip):
            state = _attempts.setdefault(key, {"fails": 0, "until": 0})
            if state.get("until", 0) > now:
                seconds = max(seconds, ceil(state["until"] - now))
                continue
            state["fails"] = state.get("fails", 0) + 1
            if state["fails"] >= MAX_FAILED_ATTEMPTS:
                state["until"] = now + LOCKOUT_MINUTES * 60
                state["fails"] = 0
                seconds = max(seconds, LOCKOUT_MINUTES * 60)
    return seconds


def clear_failures(correo: str | None, ip: str | None) -> None:
    with _attempts_lock:
        for key in _keys(correo, ip):
            _attempts.pop(key, None)
