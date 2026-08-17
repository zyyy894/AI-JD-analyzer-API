from fastapi import APIRouter, HTTPException
from app.services.log_service import setup_logger
from app.agent.graph import build_agent_graph
from app.schemas import AgentRequest, ApiResponse

router = APIRouter(prefix="/agent", tags=["Agent"])

agent_app = build_agent_graph()

logger = setup_logger(__name__)
@router.post("/run", response_model=ApiResponse)
def run_agent(request: AgentRequest):
    task = request.task.strip()

    if not task:
        raise HTTPException(status_code=400, detail="任务不能为空")

    result = agent_app.invoke({
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