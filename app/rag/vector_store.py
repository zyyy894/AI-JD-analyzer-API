import chromadb
from typing import List, Dict, Any


class VectorStore:
    def __init__(self, persist_path: str = "./chroma_db", collection_name: str = "job_docs"):
        self.client = chromadb.PersistentClient(path=persist_path)
        self.collection = self.client.get_or_create_collection(name=collection_name)

    def add_chunks(self, document_id: str, filename: str, chunks: List[str]) -> None:
        ids = [f"{document_id}_chunk_{index}" for index in range(len(chunks))]

        metadatas = [
            {
                "document_id": document_id,
                "filename": filename,
                "chunk_index": index,
            }
            for index in range(len(chunks))
        ]

        self.collection.upsert(
            documents=chunks,
            ids=ids,
            metadatas=metadatas,
        )

    def search(self, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        results = self.collection.query(
            query_texts=[query],
            n_results=top_k,
        )

        documents = results.get("documents", [[]])[0]
        metadatas = results.get("metadatas", [[]])[0]
        distances = results.get("distances", [[]])[0]

        return [
            {
                "content": doc,
                "document_id": metadata.get("document_id"),
                "filename": metadata.get("filename"),
                "chunk_index": metadata.get("chunk_index"),
                "distance": distance,
            }
            for doc, metadata, distance in zip(documents, metadatas, distances)
        ]