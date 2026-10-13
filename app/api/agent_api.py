from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from app.dependencies import get_current_user
from app.services.log_service import setup_logger
from app.agent.graph import build_agent_graph
from app.schemas import AgentRequest, ApiResponse
from app.services.db_service import create_task
from app.services.task_service import run_task

router = APIRouter(prefix="/agent", tags=["Agent"])

agent_app = build_agent_graph()

logger = setup_logger(__name__)
@router.post("/run", response_model=ApiResponse)
def run_agent(request: AgentRequest, user=Depends(get_current_user)):
    task = request.task.strip()

    if not task:
        raise HTTPException(status_code=400, detail="任务不能为空")

    result = agent_app.invoke({
        "user_id": user["id"],
        "user_input": task,
        "intent": "",
        "tool_results": [],
        "final_answer": "",
        "markdown_report": "",
    })
    logger.info("agent task finished: %s", task)
    return {
        "code": 200,
        "message": "success",
        "data": result,
    }


@router.post("/run/async", response_model=ApiResponse, status_code=202)
def run_agent_async(request: AgentRequest, background_tasks: BackgroundTasks, user=Depends(get_current_user)):
    task = request.task.strip()
    if not task:
        raise HTTPException(status_code=400, detail="Task cannot be empty")
    task_id = create_task(user["id"], "agent", {"task": task})
    background_tasks.add_task(run_task, task_id)
    return {"code": 202, "message": "Task accepted", "data": {"task_id": task_id, "status": "pending"}}
