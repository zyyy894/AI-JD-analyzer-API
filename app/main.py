import json
from fastapi import FastAPI, HTTPException

from app.schemas import (
    JDAnalyzeRequest,
    RagIngestRequest,
    RagAskRequest,
    ApiResponse,
)
from app.services.prompt_service import build_jd_analyze_prompt
from app.services.llm_service import call_llm
from app.rag.rag_service import RagService

app = FastAPI(title="AI JD Analyzer")

rag_service = RagService()


@app.get("/health")
def health():
    return {
        "code": 200,
        "message": "success",
        "data": {
            "status": "ok"
        }
    }


@app.post("/analyze-jd", response_model=ApiResponse)
def analyze_jd(request: JDAnalyzeRequest):
    jd = request.jd.strip()

    if not jd:
        raise HTTPException(status_code=400, detail="JD不能为空")

    prompt = build_jd_analyze_prompt(jd)
    result_text = call_llm(prompt)

    try:
        result_json = json.loads(result_text)
    except json.JSONDecodeError:
        return {
            "code": 500,
            "message": "模型返回内容不是合法JSON",
            "data": result_text
        }

    return {
        "code": 200,
        "message": "success",
        "data": result_json
    }


@app.post("/rag/ingest", response_model=ApiResponse)
def rag_ingest(request: RagIngestRequest):
    text = request.text.strip()

    if not text:
        raise HTTPException(status_code=400, detail="知识库文本不能为空")

    chunks = rag_service.ingest_text(text)

    return {
        "code": 200,
        "message": "知识库写入成功",
        "data": {
            "chunk_count": len(chunks),
            "chunks": chunks
        }
    }


@app.post("/rag/ask", response_model=ApiResponse)
def rag_ask(request: RagAskRequest):
    question = request.question.strip()

    if not question:
        raise HTTPException(status_code=400, detail="问题不能为空")

    result = rag_service.ask(
        question=question,
        top_k=request.top_k
    )

    return {
        "code": 200,
        "message": "回答成功",
        "data": result
    }