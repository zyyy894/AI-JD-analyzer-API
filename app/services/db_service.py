import json
import sqlite3
from pathlib import Path

DB_DIR = Path("data")
DB_DIR.mkdir(exist_ok=True)
DB_PATH = DB_DIR / "app.db"


def get_connection():
    return sqlite3.connect(DB_PATH)


def init_db():
    with get_connection() as conn:
        conn.execute("""
        CREATE TABLE IF NOT EXISTS documents (
            id TEXT PRIMARY KEY,
            filename TEXT NOT NULL,
            file_path TEXT NOT NULL,
            chunk_count INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)

        conn.execute("""
        CREATE TABLE IF NOT EXISTS qa_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            question TEXT NOT NULL,
            answer TEXT NOT NULL,
            sources TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)


def insert_document(document_id: str, filename: str, file_path: str, chunk_count: int):
    with get_connection() as conn:
        conn.execute(
            "INSERT INTO documents (id, filename, file_path, chunk_count) VALUES (?, ?, ?, ?)",
            (document_id, filename, file_path, chunk_count)
        )


def list_documents():
    with get_connection() as conn:
        conn.row_factory = sqlite3.Row
        rows = conn.execute(
            "SELECT id AS document_id, filename, chunk_count, created_at FROM documents ORDER BY created_at DESC"
        ).fetchall()
    return [dict(row) for row in rows]


def insert_qa_history(question: str, answer: str, sources: list):
    with get_connection() as conn:
        conn.execute(
            "INSERT INTO qa_history (question, answer, sources) VALUES (?, ?, ?)",
            (question, answer, json.dumps(sources, ensure_ascii=False))
        )


def list_qa_history(limit: int = 20):
    with get_connection() as conn:
        conn.row_factory = sqlite3.Row
        rows = conn.execute(
            "SELECT id, question, answer, sources, created_at FROM qa_history ORDER BY created_at DESC LIMIT ?",
            (limit,)
        ).fetchall()

    data = []
    for row in rows:
        item = dict(row)
        item["sources"] = json.loads(item["sources"])
        data.append(item)

    return data