from fastapi import BackgroundTasks, Depends, FastAPI, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.api.agent_api import router as agent_router
from app.api.auth_api import router as auth_router
from app.api.rag_api import router as rag_router
from app.dependencies import get_current_user
from app.schemas import ApiResponse, JDAnalyzeRequest, JDAnalyzeResult
from app.services.db_service import create_task, get_task, init_db
from app.services.llm_service import call_llm
from app.services.prompt_service import build_jd_analyze_prompt
from app.services.task_service import parse_structured_json, run_task
from app.services.file_service import save_upload_file
from app.rag.document_loader import load_document_text
from app.services.match_service import match_resume_to_jd
from pathlib import Path
from app.settings import FRONTEND_DIR, INDEX_FILE

if not FRONTEND_DIR.is_dir() or not INDEX_FILE.is_file():
    raise RuntimeError(f"Frontend files are missing under {FRONTEND_DIR}")

init_db()
app = FastAPI(title="AI JD Analyzer")
app.include_router(rag_router)
app.include_router(agent_router)
app.include_router(auth_router)
app.mount("/static", StaticFiles(directory=str(FRONTEND_DIR)), name="static")


@app.get("/")
def index():
    return FileResponse(str(INDEX_FILE))


@app.get("/health")
def health():
    return {"code": 200, "message": "success", "data": {"status": "ok"}}


@app.post("/analyze-jd", response_model=ApiResponse)
def analyze_jd(request: JDAnalyzeRequest, user=Depends(get_current_user)):
    try:
        result = parse_structured_json(call_llm(build_jd_analyze_prompt(request.jd.strip())), JDAnalyzeResult).model_dump()
    except ValueError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    return {"code": 200, "message": "success", "data": result}


@app.post("/analyze-jd/async", response_model=ApiResponse, status_code=202)
def analyze_jd_async(request: JDAnalyzeRequest, background_tasks: BackgroundTasks, user=Depends(get_current_user)):
    task_id = create_task(user["id"], "jd_analysis", {"jd": request.jd.strip()})
    background_tasks.add_task(run_task, task_id)
    return {"code": 202, "message": "Task accepted", "data": {"task_id": task_id, "status": "pending"}}


@app.get("/tasks/{task_id}", response_model=ApiResponse)
def task_status(task_id: str, user=Depends(get_current_user)):
    task = get_task(task_id, user["id"], user["role"] == "admin")
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return {"code": 200, "message": "success", "data": {
        "task_id": task["id"], "task_type": task["task_type"], "status": task["status"],
        "result": task["result"], "error": task["error"], "created_at": task["created_at"],
        "started_at": task["started_at"], "finished_at": task["finished_at"],
    }}


@app.post("/match-resume-jd", response_model=ApiResponse)
def match_resume_jd(resume: UploadFile = File(...), job_description: str = Form(...), user=Depends(get_current_user)):
    if not job_description.strip():
        raise HTTPException(status_code=400, detail="Job description cannot be empty")
    saved = save_upload_file(resume)
    try:
        text = load_document_text(saved["file_path"])
        if not text.strip():
            raise HTTPException(status_code=400, detail="Resume contains no readable text")
        result = match_resume_to_jd(text, job_description.strip())
        return {"code": 200, "message": "success", "data": result}
    except ValueError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    finally:
        Path(saved["file_path"]).unlink(missing_ok=True)


@app.post("/match-resume-jd/async", response_model=ApiResponse, status_code=202)
def match_resume_jd_async(background_tasks: BackgroundTasks, resume: UploadFile = File(...), job_description: str = Form(...), user=Depends(get_current_user)):
    if not job_description.strip():
        raise HTTPException(status_code=400, detail="Job description cannot be empty")
    saved = save_upload_file(resume)
    task_id = create_task(user["id"], "resume_match", {"file_path": saved["file_path"], "jd": job_description.strip()})
    background_tasks.add_task(run_task, task_id)
    return {"code": 202, "message": "Task accepted", "data": {"task_id": task_id, "status": "pending"}}
