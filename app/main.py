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
from fastapi import UploadFile, File
from app.services.file_service import save_upload_file
from app.rag.document_loader import load_document_text
from app.services.db_service import (
    init_db,
    insert_document,
    list_documents,
    insert_qa_history,
    list_qa_history,
)
init_db()
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

    insert_qa_history(
        question=question,
        answer=result["answer"],
        sources=result["sources"],
    )

    return {
        "code": 200,
        "message": "回答成功",
        "data": result
    }
@app.post("/rag/documents/upload", response_model=ApiResponse)
def upload_document(file: UploadFile = File(...)):
    saved = save_upload_file(file)
    text = load_document_text(saved["file_path"])

    if not text.strip():
        raise HTTPException(status_code=400, detail="文档没有可入库文本")

    chunks = rag_service.ingest_document(
        document_id=saved["document_id"],
        filename=saved["filename"],
        text=text,
    )

    insert_document(
        document_id=saved["document_id"],
        filename=saved["filename"],
        file_path=saved["file_path"],
        chunk_count=len(chunks),
    )

    return {
        "code": 200,
        "message": "文档上传并入库成功",
        "data": {
            "document_id": saved["document_id"],
            "filename": saved["filename"],
            "chunk_count": len(chunks),
        }
    }
@app.get("/rag/documents", response_model=ApiResponse)
def rag_documents():
    return {
        "code": 200,
        "message": "success",
        "data": list_documents()
    }
@app.get("/rag/history", response_model=ApiResponse)
def rag_history():
    return {
        "code": 200,
        "message": "success",
        "data": list_qa_history()
    }