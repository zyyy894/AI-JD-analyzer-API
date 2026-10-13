import json
import sqlite3
from uuid import uuid4
from contextlib import contextmanager

from app.settings import DATA_DIR

DB_PATH = DATA_DIR / "app.db"


@contextmanager
def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        with conn:
            yield conn
    finally:
        conn.close()


def _ensure_column(conn, table: str, column: str, column_type: str):
    columns = {row["name"] for row in conn.execute(f"PRAGMA table_info({table})").fetchall()}
    if column not in columns:
        conn.execute(f"ALTER TABLE {table} ADD COLUMN {column} {column_type}")


def init_db():
    with get_connection() as conn:
        conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id TEXT PRIMARY KEY,
            email TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            role TEXT NOT NULL DEFAULT 'user',
            is_active INTEGER NOT NULL DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)
        conn.execute("""
        CREATE TABLE IF NOT EXISTS documents (
            id TEXT PRIMARY KEY,
            user_id TEXT,
            filename TEXT NOT NULL,
            file_path TEXT NOT NULL,
            chunk_count INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)
        conn.execute("""
        CREATE TABLE IF NOT EXISTS qa_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT,
            question TEXT NOT NULL,
            answer TEXT NOT NULL,
            sources TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)
        _ensure_column(conn, "documents", "user_id", "TEXT")
        _ensure_column(conn, "qa_history", "user_id", "TEXT")
        conn.execute("CREATE INDEX IF NOT EXISTS documents_owner ON documents(user_id)")
        conn.execute("CREATE INDEX IF NOT EXISTS history_owner ON qa_history(user_id)")
        conn.execute("CREATE TABLE IF NOT EXISTS tasks (id TEXT PRIMARY KEY, user_id TEXT NOT NULL, task_type TEXT NOT NULL, status TEXT NOT NULL DEFAULT 'pending', payload TEXT NOT NULL, result TEXT, error TEXT, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, started_at TIMESTAMP, finished_at TIMESTAMP)")
        conn.execute("CREATE INDEX IF NOT EXISTS tasks_owner ON tasks(user_id, created_at)")


def create_user(email: str, password_hash: str, role: str = "user"):
    if role not in {"user", "admin"}:
        raise ValueError("Invalid role")
    user_id = uuid4().hex
    with get_connection() as conn:
        conn.execute(
            "INSERT INTO users (id, email, password_hash, role) VALUES (?, ?, ?, ?)",
            (user_id, email, password_hash, role),
        )
        return dict(conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone())


def get_user_by_email(email: str):
    with get_connection() as conn:
        row = conn.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
    return dict(row) if row else None


def get_user_by_id(user_id: str):
    with get_connection() as conn:
        row = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
    return dict(row) if row else None


def insert_document(user_id: str, document_id: str, filename: str, file_path: str, chunk_count: int):
    with get_connection() as conn:
        conn.execute(
            "INSERT INTO documents (id, user_id, filename, file_path, chunk_count) VALUES (?, ?, ?, ?, ?)",
            (document_id, user_id, filename, file_path, chunk_count),
        )


def list_documents(user_id: str | None = None, is_admin: bool = False):
    if not user_id:
        raise ValueError("An authenticated user ID is required")
    query = "SELECT id AS document_id, user_id, filename, chunk_count, created_at FROM documents"
    params = ()
    if user_id and not is_admin:
        query += " WHERE user_id = ?"
        params = (user_id,)
    query += " ORDER BY created_at DESC"
    with get_connection() as conn:
        return [dict(row) for row in conn.execute(query, params).fetchall()]


def insert_qa_history(user_id: str, question: str, answer: str, sources: list):
    with get_connection() as conn:
        conn.execute(
            "INSERT INTO qa_history (user_id, question, answer, sources) VALUES (?, ?, ?, ?)",
            (user_id, question, answer, json.dumps(sources, ensure_ascii=False)),
        )


def list_qa_history(user_id: str | None = None, is_admin: bool = False, limit: int = 20):
    if not user_id:
        raise ValueError("An authenticated user ID is required")
    query = "SELECT id, user_id, question, answer, sources, created_at FROM qa_history"
    params = []
    if user_id and not is_admin:
        query += " WHERE user_id = ?"
        params.append(user_id)
    query += " ORDER BY created_at DESC LIMIT ?"
    params.append(limit)
    with get_connection() as conn:
        rows = conn.execute(query, params).fetchall()
    data = []
    for row in rows:
        item = dict(row)
        item["sources"] = json.loads(item["sources"])
        data.append(item)
    return data


def create_task(user_id: str, task_type: str, payload: dict) -> str:
    task_id = uuid4().hex
    with get_connection() as conn:
        conn.execute("INSERT INTO tasks (id, user_id, task_type, payload) VALUES (?, ?, ?, ?)", (task_id, user_id, task_type, json.dumps(payload, ensure_ascii=False)))
    return task_id


def get_task(task_id: str, user_id: str, is_admin: bool = False):
    query = "SELECT * FROM tasks WHERE id = ?"
    params = [task_id]
    if not is_admin:
        query += " AND user_id = ?"
        params.append(user_id)
    with get_connection() as conn:
        row = conn.execute(query, params).fetchone()
    if not row:
        return None
    item = dict(row)
    item["payload"] = json.loads(item["payload"])
    item["result"] = json.loads(item["result"]) if item["result"] else None
    return item


def update_task(task_id: str, status: str, *, result=None, error=None):
    if status not in {"pending", "running", "succeeded", "failed"}:
        raise ValueError("Invalid task status")
    with get_connection() as conn:
        if status == "running":
            conn.execute("UPDATE tasks SET status = ?, started_at = CURRENT_TIMESTAMP WHERE id = ?", (status, task_id))
        elif status in {"succeeded", "failed"}:
            conn.execute("UPDATE tasks SET status = ?, result = ?, error = ?, finished_at = CURRENT_TIMESTAMP WHERE id = ?", (status, json.dumps(result, ensure_ascii=False) if result is not None else None, error, task_id))
        else:
            conn.execute("UPDATE tasks SET status = ? WHERE id = ?", (status, task_id))
