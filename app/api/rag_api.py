from fastapi import APIRouter, Depends, File, HTTPException, UploadFile

from app.dependencies import get_current_user
from app.rag.document_loader import load_document_text
from app.rag.rag_service import RagService
from app.schemas import ApiResponse, RagAskRequest, RagIngestRequest
from app.services.db_service import (
    insert_document,
    insert_qa_history,
    list_documents,
    list_qa_history,
)
from app.services.file_service import save_upload_file
from app.services.log_service import setup_logger

logger = setup_logger(__name__)

router = APIRouter(prefix="/rag", tags=["RAG"])

rag_service = RagService()

logger = setup_logger(__name__)


@router.post("/ingest", response_model=ApiResponse)
def rag_ingest(request: RagIngestRequest, user=Depends(get_current_user)):
    text = request.text.strip()

    if not text:
        raise HTTPException(status_code=400, detail="知识库文本不能为空")

    chunks = rag_service.ingest_text(text, user_id=user["id"])

    return {
        "code": 200,
        "message": "知识库写入成功",
        "data": {
            "chunk_count": len(chunks),
            "chunks": chunks
        }
    }


@router.post("/ask", response_model=ApiResponse)
def rag_ask(request: RagAskRequest, user=Depends(get_current_user)):
    question = request.question.strip()

    if not question:
        raise HTTPException(status_code=400, detail="问题不能为空")

    result = rag_service.ask(
        question=question,
        top_k=request.top_k,
        user_id=user["id"],
    )

    insert_qa_history(
        user_id=user["id"],
        question=question,
        answer=result["answer"],
        sources=result["sources"],
    )

    return {
        "code": 200,
        "message": "回答成功",
        "data": result
    }


@router.post("/documents/upload", response_model=ApiResponse)
def upload_document(file: UploadFile = File(...), user=Depends(get_current_user)):
    saved = save_upload_file(file)
    text = load_document_text(saved["file_path"])

    if not text.strip():
        raise HTTPException(status_code=400, detail="文档没有可入库文本")

    chunks = rag_service.ingest_document(
        document_id=saved["document_id"],
        filename=saved["filename"],
        text=text,
        user_id=user["id"],
    )

    insert_document(
        user_id=user["id"],
        document_id=saved["document_id"],
        filename=saved["filename"],
        file_path=saved["file_path"],
        chunk_count=len(chunks),
    )
    logger.info("document uploaded: %s", saved["filename"])

    return {
        "code": 200,
        "message": "文档上传并入库成功",
        "data": {
            "document_id": saved["document_id"],
            "filename": saved["filename"],
            "chunk_count": len(chunks),
        }
    }


@router.get("/documents", response_model=ApiResponse)
def rag_documents(user=Depends(get_current_user)):
    return {
        "code": 200,
        "message": "success",
        "data": list_documents(user_id=user["id"])
    }


@router.get("/history", response_model=ApiResponse)
def rag_history(user=Depends(get_current_user)):
    return {
        "code": 200,
        "message": "success",
        "data": list_qa_history(user_id=user["id"])
    }
from app.dependencies import get_current_user
