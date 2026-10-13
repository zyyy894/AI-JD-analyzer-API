from typing import List, Dict, Any
from uuid import uuid4

from app.rag.splitter import split_text
from app.rag.vector_store import VectorStore
from app.services.llm_service import call_llm
from app.settings import CHROMA_DIR


class RagService:
    def __init__(self):
        self.vector_store = VectorStore(
            persist_path=str(CHROMA_DIR),
            collection_name="job_docs"
        )

    def ingest_text(self, text: str, filename: str = "input.txt", *, user_id: str) -> List[str]:
        chunks = split_text(
            text,
            chunk_size=500,
            chunk_overlap=100
        )

        document_id = str(uuid4())

        self.vector_store.add_chunks(
            document_id=document_id,
            filename=filename,
            chunks=chunks,
            user_id=user_id,
        )

        return chunks

    def ask(self, question: str, top_k: int = 3, *, user_id: str) -> Dict[str, Any]:
        contexts = self.vector_store.search(
            query=question,
            top_k=top_k,
            user_id=user_id,
        )

        prompt = self._build_rag_prompt(question, contexts)
        answer = call_llm(prompt)

        return {
            "answer": answer,
            "sources": contexts
        }

    def ingest_document(self, document_id: str, filename: str, text: str, *, user_id: str) -> List[str]:
        chunks = split_text(text, chunk_size=500, chunk_overlap=100)
        self.vector_store.add_chunks(
            document_id=document_id,
            filename=filename,
            chunks=chunks,
            user_id=user_id,
        )
        return chunks

    def _build_rag_prompt(
        self,
        question: str,
        contexts: List[Dict[str, Any]]
    ) -> str:
        context_text = "\n\n".join(
            [
                context.get("content", "")
                for context in contexts
                if context.get("content")
            ]
        )

        if not context_text:
            context_text = "知识库中没有检索到相关资料。"

        return f"""
你是一个严谨的知识库问答助手。
请只根据参考资料回答问题。
如果资料中没有答案，请回答：资料中没有找到相关信息。
不要编造资料之外的内容。

参考资料：
{context_text}

用户问题：
{question}
"""
