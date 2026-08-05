import chromadb
from typing import List


class VectorStore:
    def __init__(
        self,
        persist_path: str = "./chroma_db",
        collection_name: str = "job_docs"
    ):
        self.client = chromadb.PersistentClient(path=persist_path)
        self.collection = self.client.get_or_create_collection(
            name=collection_name
        )

    def add_texts(self, texts: List[str]) -> None:
        ids = [f"chunk_{index}" for index in range(len(texts))]

        self.collection.upsert(
            documents=texts,
            ids=ids
        )

    def search(self, query: str, top_k: int = 3) -> List[str]:
        results = self.collection.query(
            query_texts=[query],
            n_results=top_k
        )

        documents = results.get("documents", [[]])[0]
        return documents