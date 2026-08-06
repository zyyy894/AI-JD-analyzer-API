from typing import List

from app.rag.splitter import split_text
from app.rag.vector_store import VectorStore
from app.services.llm_service import call_llm


class RagService:
    def __init__(self):
        self.vector_store = VectorStore(
            persist_path="./chroma_db",
            collection_name="job_docs"
        )

    def ingest_text(self, text: str) -> List[str]:
        chunks = split_text(
            text,
            chunk_size=500,
            chunk_overlap=100
        )

        self.vector_store.add_texts(chunks)
        return chunks

    def ask(self, question: str, top_k: int = 3) -> dict:
        contexts = self.vector_store.search(
            query=question,
            top_k=top_k
        )

        prompt = self._build_rag_prompt(question, contexts)
        answer = call_llm(prompt)

        return {
            "answer": answer,
            "sources": contexts
        }

    def _build_rag_prompt(
        self,
        question: str,
        contexts: List[str]
    ) -> str:
        context_text = "\n\n".join(contexts)

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