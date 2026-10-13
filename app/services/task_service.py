import json
import re

from app.schemas import JDAnalyzeResult
from app.services.db_service import update_task
from app.services.llm_service import call_llm
from app.services.prompt_service import build_jd_analyze_prompt


def parse_structured_json(raw: str, model):
    text = raw.strip()
    fenced = re.search(r"```(?:json)?\s*(.*?)\s*```", text, flags=re.IGNORECASE | re.DOTALL)
    if fenced:
        text = fenced.group(1).strip()
    try:
        return model.model_validate(json.loads(text))
    except (json.JSONDecodeError, TypeError, ValueError) as exc:
        raise ValueError("Model output failed structured validation") from exc


def run_task(task_id: str):
    try:
        from app.services.db_service import get_connection
        with get_connection() as conn:
            row = conn.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()
        if not row:
            return
        task = dict(row)
        update_task(task_id, "running")
        payload = json.loads(task["payload"])
        if task["task_type"] == "jd_analysis":
            result = parse_structured_json(call_llm(build_jd_analyze_prompt(payload["jd"])), JDAnalyzeResult).model_dump()
        elif task["task_type"] == "resume_match":
            from app.rag.document_loader import load_document_text
            from app.services.match_service import match_resume_to_jd
            import os
            try:
                result = match_resume_to_jd(load_document_text(payload["file_path"]), payload["jd"])
            finally:
                os.unlink(payload["file_path"])
        elif task["task_type"] == "agent":
            from app.agent.graph import build_agent_graph
            result = build_agent_graph().invoke({"user_id": task["user_id"], "user_input": payload["task"], "intent": "", "tool_results": [], "final_answer": "", "markdown_report": ""})
        else:
            raise ValueError("Unknown task type")
        update_task(task_id, "succeeded", result=result)
    except Exception as exc:
        update_task(task_id, "failed", error=str(exc)[:1000])
