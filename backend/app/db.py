import os
import sqlite3
from typing import Optional

DB_PATH = os.environ.get("AUTH_DB", "auth.db")


def set_db_path(path: str):
    global DB_PATH
    DB_PATH = path


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_connection()
    try:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT,
                name TEXT,
                google_id TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                token TEXT UNIQUE NOT NULL,
                user_id INTEGER NOT NULL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(user_id) REFERENCES users(id)
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS uploads (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                file_name TEXT NOT NULL,
                stored_name TEXT NOT NULL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(user_id) REFERENCES users(id)
            )
            """
        )
        conn.commit()
    finally:
        conn.close()


init_db()


def create_user(email: str, password_hash: str, name: Optional[str] = None, google_id: Optional[str] = None):
    conn = get_connection()
    try:
        cursor = conn.execute(
            "INSERT INTO users (email, password_hash, name, google_id) VALUES (?, ?, ?, ?)",
            (email, password_hash, name, google_id),
        )
        conn.commit()
        user_id = cursor.lastrowid
        return {"id": user_id, "email": email, "name": name, "google_id": google_id}
    finally:
        conn.close()


def get_user_by_id(user_id: int):
    conn = get_connection()
    try:
        row = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
        return dict(row) if row else None
    finally:
        conn.close()


def get_user_by_email(email: str):
    conn = get_connection()
    try:
        row = conn.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
        return dict(row) if row else None
    finally:
        conn.close()


def get_user_by_google_id(google_id: str):
    conn = get_connection()
    try:
        row = conn.execute("SELECT * FROM users WHERE google_id = ?", (google_id,)).fetchone()
        return dict(row) if row else None
    finally:
        conn.close()


def create_session(token: str, user_id: int):
    conn = get_connection()
    try:
        conn.execute("INSERT INTO sessions (token, user_id) VALUES (?, ?)", (token, user_id))
        conn.commit()
        return {"token": token, "user_id": user_id}
    finally:
        conn.close()


def get_session(token: str):
    conn = get_connection()
    try:
        row = conn.execute("SELECT * FROM sessions WHERE token = ?", (token,)).fetchone()
        return dict(row) if row else None
    finally:
        conn.close()


def save_upload(user_id: int, file_name: str, stored_name: str):
    conn = get_connection()
    try:
        conn.execute(
            "INSERT INTO uploads (user_id, file_name, stored_name) VALUES (?, ?, ?)",
            (user_id, file_name, stored_name),
        )
        conn.commit()
    finally:
        conn.close()


def list_uploads(user_id: int):
    conn = get_connection()
    try:
        rows = conn.execute(
            "SELECT file_name, stored_name FROM uploads WHERE user_id = ? ORDER BY id DESC",
            (user_id,),
        ).fetchall()
        return [dict(row) for row in rows]
    finally:
        conn.close()


def delete_upload(user_id: int, stored_name: str):
    conn = get_connection()
    try:
        conn.execute("DELETE FROM uploads WHERE user_id = ? AND stored_name = ?", (user_id, stored_name))
        conn.commit()
    finally:
        conn.close()
