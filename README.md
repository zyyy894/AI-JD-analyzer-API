# AI JD Analyzer

一个面向个人求职辅助的 FastAPI 应用，支持 JD 分析、简历与 JD 匹配、个人知识库问答和 Agent 任务。

## 功能

- 邮箱注册、JWT 登录、普通用户和管理员权限。
- TXT、MD、PDF、DOCX 文档上传，默认大小限制 10 MiB。
- 用户级文档、问答历史和 Chroma 向量隔离。
- JD 分析与简历-JD 匹配，并使用 Pydantic 校验结构化输出。
- 同步接口和后台异步任务接口。
- 原生 HTML/CSS/JavaScript 前端。

## 快速启动

```powershell
cd P:\pycharm\python\ai_jd_analyzer
.venv\Scripts\python.exe -m pip install -r requirements.txt
Copy-Item .env.example .env
# Fill in DEEPSEEK_API_KEY in .env
.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8001
```

Open `http://127.0.0.1:8001/` in a browser.

## Configuration

```env
DEEPSEEK_API_KEY=your-key
DEEPSEEK_BASE_URL=https://api.deepseek.com
DEEPSEEK_MODEL=deepseek-v4-flash
AUTH_SECRET_KEY=at-least-32-random-bytes
ACCESS_TOKEN_EXPIRE_MINUTES=120
MAX_UPLOAD_SIZE_BYTES=10485760
```

Do not commit `.env`, API keys, uploaded files, SQLite data, or Chroma data.

## Main API

- `POST /auth/register`, `POST /auth/login`, `GET /auth/me`
- `POST /rag/documents/upload`
- `POST /analyze-jd`
- `POST /analyze-jd/async`
- `POST /match-resume-jd`
- `POST /match-resume-jd/async`
- `POST /agent/run/async`
- `GET /tasks/{task_id}`

The match form uses multipart fields `resume` and `job_description`. The frontend exposes this under `04 / Match` with `Match now` and `Run in background` actions.

## Resume-JD match result

```json
{
  "match_score": 82.5,
  "matching_skills": ["Python", "FastAPI"],
  "missing_skills": ["Kubernetes"],
  "strengths": ["Backend API experience"],
  "gaps": ["No Kubernetes evidence"],
  "recommendations": ["Add a deployment project"],
  "summary": "Strong overall match"
}
```

Malformed model output returns HTTP 502 for synchronous requests and a `failed` task for asynchronous requests. Markdown JSON fences are accepted before validation.

## Admin and data isolation

Public registration always creates a normal user. Promote an account from a trusted local shell:

```powershell
.venv\Scripts\python.exe -m app.manage_users your-email@example.com --role admin
```

Old SQLite rows and Chroma vectors without an owner are not assigned to the first user. Re-upload legacy files after signing in.

## Tests

```powershell
.venv\Scripts\python.exe -m pytest test_db.py -q
```

Tests cover authentication, account status, user isolation, upload limits, task lifecycle, Chroma owner filtering, structured output validation, and resume-JD matching validation.

## Project status

This version is intended for local learning, demonstrations, and personal job-search assistance. It is not production-ready. Remaining work includes durable workers and retries, rate limiting, password recovery, scanned-PDF OCR, file scanning, Docker deployment, and broader end-to-end tests.

## Reference projects

- [FastAPI full-stack template](https://github.com/fastapi/full-stack-fastapi-template)
- [FastAPI Users](https://github.com/fastapi-users/fastapi-users)
- [fastapi-permissions](https://github.com/holgi/fastapi-permissions)
