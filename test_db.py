"""Isolated permission tests. Run: .venv/Scripts/python -m pytest test_db.py -q"""
import time
from io import BytesIO
from pathlib import Path
from unittest.mock import MagicMock

import jwt
import pytest
from fastapi.testclient import TestClient

from app.services import db_service as db
from app.services.auth_service import create_access_token, hash_password, verify_password
from app.settings import AUTH_SECRET_KEY


@pytest.fixture
def database(tmp_path, monkeypatch):
    monkeypatch.setattr(db, "DB_PATH", tmp_path / "test.db")
    db.init_db()
    return db


@pytest.fixture
def client(database, monkeypatch):
    from app.rag.vector_store import VectorStore
    monkeypatch.setattr(VectorStore, "__init__", lambda self, **kwargs: setattr(self, "collection", MagicMock()))
    from app.main import app
    with TestClient(app) as client:
        yield client


def register(client, email="alice@example.com"):
    response = client.post("/auth/register", json={"email": email, "password": "long-password-123", "role": "admin"})
    assert response.status_code == 201
    data = response.json()["data"]
    assert data["user"]["role"] == "user"
    assert "password_hash" not in data["user"]
    return data["user"], {"Authorization": "Bearer " + data["access_token"]}


def test_login_register_and_validation(client):
    user, headers = register(client)
    assert client.get("/auth/me", headers=headers).json()["data"]["id"] == user["id"]
    assert client.post("/auth/register", json={"email": "ALICE@example.com", "password": "long-password-123"}).status_code == 409
    assert client.post("/auth/register", json={"email": "not-an-email", "password": "long-password-123"}).status_code == 422
    assert client.post("/auth/register", json={"email": "new@example.com", "password": "short"}).status_code == 422
    login = client.post("/auth/login", data={"username": "ALICE@example.com", "password": "long-password-123"})
    assert login.status_code == 200
    assert login.json()["token_type"] == "bearer"
    assert client.post("/auth/login", data={"username": user["email"], "password": "wrong"}).status_code == 401


@pytest.mark.parametrize("method,path,body", [
    ("GET", "/rag/documents", None), ("GET", "/rag/history", None),
    ("GET", "/auth/me", None), ("GET", "/auth/users", None),
    ("POST", "/rag/ask", {"question": "hello"}),
    ("POST", "/rag/ingest", {"text": "private"}),
    ("POST", "/agent/run", {"task": "hello"}),
    ("POST", "/analyze-jd", {"jd": "hello"}),
])
def test_anonymous_denied(client, method, path, body):
    assert client.request(method, path, json=body).status_code == 401


def test_anonymous_upload_denied(client):
    assert client.post("/rag/documents/upload", files={"file": ("test.txt", b"private")}).status_code == 401


@pytest.mark.parametrize("token", ["broken", "a.b.c", "eyJhbGciOiJub25lIn0.e30.", "\u4e2d\u6587"])
def test_malformed_token(client, token):
    # HTTP header encoding is latin-1; non-ASCII is tested directly below.
    if not token.isascii():
        from app.services.auth_service import decode_access_token
        with pytest.raises(ValueError):
            decode_access_token(token)
    else:
        assert client.get("/auth/me", headers={"Authorization": "Bearer " + token}).status_code == 401


def test_expired_tampered_and_deleted_user(client):
    user, headers = register(client)
    expired = jwt.encode({"sub": user["id"], "iat": 1, "exp": 2}, AUTH_SECRET_KEY, algorithm="HS256")
    bad_signature = jwt.encode({"sub": user["id"], "iat": int(time.time()), "exp": int(time.time()) + 600}, "a-different-key-that-is-long-enough", algorithm="HS256")
    for token in (expired, bad_signature, create_access_token("missing", "admin")):
        assert client.get("/auth/me", headers={"Authorization": "Bearer " + token}).status_code == 401


def test_user_data_and_legacy_isolation(client, database):
    alice, a = register(client)
    bob, b = register(client, "bob@example.com")
    for user in (alice, bob):
        database.insert_document(user["id"], user["id"], user["email"], "private.txt", 1)
        database.insert_qa_history(user["id"], user["email"], "private answer", [])
    with database.get_connection() as conn:
        conn.execute("INSERT INTO documents(id,filename,file_path,chunk_count) VALUES ('legacy','legacy.txt','old.txt',1)")
        conn.execute("INSERT INTO qa_history(question,answer,sources) VALUES ('legacy','old','[]')")
    for user, headers in ((alice, a), (bob, b)):
        docs = client.get("/rag/documents", headers=headers).json()["data"]
        history = client.get("/rag/history", headers=headers).json()["data"]
        assert len(docs) == len(history) == 1
        assert docs[0]["user_id"] == history[0]["user_id"] == user["id"]
    with pytest.raises(ValueError):
        database.list_documents()
    with pytest.raises(ValueError):
        database.list_qa_history()


def test_admin_and_disabled_account(client, database):
    admin, a = register(client)
    bob, b = register(client, "bob@example.com")
    assert client.get("/auth/users", headers=a).status_code == 403
    with database.get_connection() as conn:
        conn.execute("UPDATE users SET role='admin' WHERE id=?", (admin["id"],))
    users = client.get("/auth/users", headers=a)
    assert users.status_code == 200
    assert all("password_hash" not in row for row in users.json()["data"])
    path = f"/auth/users/{bob['id']}/active"
    assert client.patch(path + "?active=false", headers=b).status_code == 403
    assert client.patch(path + "?active=false", headers=a).status_code == 200
    assert client.get("/auth/me", headers=b).status_code == 401
    assert client.post("/auth/login", data={"username": bob["email"], "password": "long-password-123"}).status_code == 401
    assert client.patch(path + "?active=true", headers=a).status_code == 200
    assert client.get("/auth/me", headers=b).status_code == 200
    with database.get_connection() as conn:
        conn.execute("UPDATE users SET role='user' WHERE id=?", (admin["id"],))
    assert client.get("/auth/users", headers=a).status_code == 403


def test_vector_owner_filter():
    from app.rag.vector_store import VectorStore
    store = object.__new__(VectorStore)
    store.collection = MagicMock()
    store.collection.query.return_value = {"documents": [[]], "metadatas": [[]], "distances": [[]]}
    assert store.search("query", user_id="alice") == []
    assert store.collection.query.call_args.kwargs["where"] == {"user_id": "alice"}
    store.add_chunks("doc", "test.txt", ["private"], user_id="alice")
    assert store.collection.upsert.call_args.kwargs["metadatas"][0]["user_id"] == "alice"
    with pytest.raises(ValueError):
        store.search("query", user_id="")


def test_rag_and_agent_identity(client, monkeypatch):
    from app.api import rag_api, agent_api
    from app.agent import graph
    alice, headers = register(client)
    ask = MagicMock(return_value={"answer": "answer", "sources": []})
    monkeypatch.setattr(rag_api.rag_service, "ask", ask)
    assert client.post("/rag/ask", json={"question": "hello", "user_id": "bob"}, headers=headers).status_code == 200
    assert ask.call_args.kwargs["user_id"] == alice["id"]
    search = MagicMock(return_value={"answer": "scoped", "sources": []})
    monkeypatch.setattr(graph, "search_knowledge_base", search)
    monkeypatch.setattr(graph, "generate_report", lambda **kwargs: "report")
    # Exercises the compiled graph, including the knowledge route.
    result = client.post("/agent/run", json={"task": "\u77e5\u8bc6\u5e93", "user_id": "bob"}, headers=headers)
    assert result.status_code == 200
    assert search.call_args.kwargs["user_id"] == alice["id"]


def test_migration_and_unicode_password(database):
    database.init_db()
    database.init_db()
    password = "\u4e2d" * 100
    hashed = hash_password(password)
    assert hashed.startswith("$argon2")
    assert verify_password(password, hashed)
    assert not verify_password("wrong", hashed)


def test_real_chroma_isolation(tmp_path):
    import chromadb
    from app.rag.vector_store import VectorStore

    class TestEmbedding:
        def name(self):
            return "permission-test"

        def __call__(self, input):
            return [[1.0, 0.0] for _ in input]

        def embed_query(self, input):
            return self(input)

    chroma = chromadb.EphemeralClient()
    collection = chroma.get_or_create_collection("permission_test", embedding_function=TestEmbedding())
    collection.upsert(ids=["a", "b", "old"], documents=["alice private", "bob private", "legacy private"],
                      embeddings=[[1.0, 0.0]] * 3,
                      metadatas=[{"user_id": "alice"}, {"user_id": "bob"}, {"filename": "legacy.txt"}])
    store = object.__new__(VectorStore)
    store.collection = collection
    assert [row["content"] for row in store.search("query", user_id="alice")] == ["alice private"]
    assert [row["content"] for row in store.search("query", user_id="bob")] == ["bob private"]
    assert store.search("query", user_id="outsider") == []


def test_existing_database_migration(tmp_path, monkeypatch):
    monkeypatch.setattr(db, "DB_PATH", tmp_path / "legacy.db")
    with db.get_connection() as conn:
        conn.execute("CREATE TABLE documents(id TEXT PRIMARY KEY, filename TEXT, file_path TEXT, chunk_count INTEGER, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)")
        conn.execute("CREATE TABLE qa_history(id INTEGER PRIMARY KEY, question TEXT, answer TEXT, sources TEXT, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)")
        conn.execute("INSERT INTO documents(id,filename,file_path,chunk_count) VALUES ('old','old.txt','old.txt',1)")
    db.init_db()
    db.init_db()
    assert db.list_documents("new-user") == []
    with db.get_connection() as conn:
        assert conn.execute("SELECT user_id FROM documents WHERE id='old'").fetchone()["user_id"] is None


def test_upload_size_limit_and_cleanup(tmp_path, monkeypatch):
    import app.services.file_service as file_service
    from fastapi import UploadFile
    from fastapi.exceptions import HTTPException

    monkeypatch.setattr(file_service, "UPLOAD_DIR", tmp_path)
    monkeypatch.setattr(file_service, "MAX_UPLOAD_SIZE_BYTES", 5)

    saved = file_service.save_upload_file(UploadFile(filename="resume.txt", file=BytesIO(b"12345")))
    assert Path(saved["file_path"]).read_bytes() == b"12345"

    with pytest.raises(HTTPException) as error:
        file_service.save_upload_file(UploadFile(filename="too-large.txt", file=BytesIO(b"123456")))
    assert error.value.status_code == 413
    assert list(tmp_path.glob("*too-large.txt")) == []

    with pytest.raises(HTTPException) as error:
        file_service.save_upload_file(UploadFile(filename="empty.txt", file=BytesIO(b"")))
    assert error.value.status_code == 400


def test_structured_output_validation():
    from app.schemas import JDAnalyzeResult
    from app.services.task_service import parse_structured_json

    result = parse_structured_json('```json\n{"core_skills":["Python"],"bonus_skills":[],"learning_plan":["RAG"],"resume_keywords":["FastAPI"],"summary":"Good fit"}\n```', JDAnalyzeResult)
    assert result.summary == "Good fit"
    with pytest.raises(ValueError):
        parse_structured_json('{"core_skills":"not-a-list"}', JDAnalyzeResult)


def test_resume_jd_match_output_validation():
    from app.services.match_service import parse_match_result

    raw = '{"match_score":82.5,"matching_skills":["Python"],"missing_skills":["Kubernetes"],"strengths":["API work"],"gaps":["No Kubernetes evidence"],"recommendations":["Add a deployment project"],"summary":"Strong match"}'
    result = parse_match_result(raw)
    assert result.match_score == 82.5
    with pytest.raises(ValueError):
        parse_match_result('{"match_score":120,"matching_skills":[],"missing_skills":[],"strengths":[],"gaps":[],"recommendations":[],"summary":"bad"}')


def test_task_lifecycle(database):
    task_id = database.create_task("alice", "jd_analysis", {"jd": "Python"})
    task = database.get_task(task_id, "alice")
    assert task["status"] == "pending"
    assert database.get_task(task_id, "bob") is None
    database.update_task(task_id, "running")
    database.update_task(task_id, "succeeded", result={"summary": "ok"})
    task = database.get_task(task_id, "alice")
    assert task["status"] == "succeeded"
    assert task["result"]["summary"] == "ok"


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-q"]))
