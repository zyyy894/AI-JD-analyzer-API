"""Project paths shared by the application services.

All runtime data is kept beside the project instead of being resolved from
the process working directory. This is important when Uvicorn is started by
PyCharm, Task Scheduler, or a Windows service.
"""

from pathlib import Path
import os
import secrets
from dotenv import load_dotenv


PROJECT_ROOT = Path(__file__).resolve().parent.parent
ENV_FILE = PROJECT_ROOT / ".env"

DATA_DIR = PROJECT_ROOT / "data"
UPLOAD_DIR = PROJECT_ROOT / "uploads"
CHROMA_DIR = PROJECT_ROOT / "chroma_db"
LOG_DIR = PROJECT_ROOT / "logs"

FRONTEND_DIR = PROJECT_ROOT / "frontend"
INDEX_FILE = FRONTEND_DIR / "index.html"

load_dotenv(ENV_FILE)
AUTH_SECRET_KEY = os.getenv("AUTH_SECRET_KEY", "")
if AUTH_SECRET_KEY in {"", "replace-with-a-long-random-secret", "dev-only-change-this-secret"}:
    AUTH_SECRET_KEY = secrets.token_urlsafe(48)
elif len(AUTH_SECRET_KEY.encode("utf-8")) < 32:
    raise RuntimeError("AUTH_SECRET_KEY must contain at least 32 bytes")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "120"))
if ACCESS_TOKEN_EXPIRE_MINUTES <= 0:
    raise RuntimeError("ACCESS_TOKEN_EXPIRE_MINUTES must be positive")
MAX_UPLOAD_SIZE_BYTES = int(os.getenv("MAX_UPLOAD_SIZE_BYTES", str(10 * 1024 * 1024)))
if MAX_UPLOAD_SIZE_BYTES <= 0:
    raise RuntimeError("MAX_UPLOAD_SIZE_BYTES must be positive")

for runtime_dir in (DATA_DIR, UPLOAD_DIR, CHROMA_DIR, LOG_DIR):
    runtime_dir.mkdir(parents=True, exist_ok=True)
