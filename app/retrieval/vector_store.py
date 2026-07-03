import chromadb

from app.config import (
    CHROMA_API_KEY,
    CHROMA_TENANT,
    CHROMA_DATABASE,
    CHROMA_COLLECTION_NAME,
    MAX_DOCUMENT_CHARS,
    UPSERT_BATCH_SIZE,
)
from app.models.schemas import CodeChunk


class VectorStore:
    def __init__(self):
        self.client = chromadb.CloudClient(
            api_key=CHROMA_API_KEY,
            tenant=CHROMA_TENANT,
            database=CHROMA_DATABASE,
        )

        self.collection = self.client.get_or_create_collection(
            name=CHROMA_COLLECTION_NAME,
            metadata={"hnsw:space": "cosine"},
        )

    def add_chunks(
        self,
        chunks: list[CodeChunk],
        embeddings: list[list[float]],
    ) -> None:
        if not chunks or not embeddings:
            return

        ids = []
        documents = []
        metadatas = []
        filtered_embeddings = []

        for chunk, embedding in zip(chunks, embeddings):
            ids.append(chunk.chunk_id)
            documents.append(chunk.content[:MAX_DOCUMENT_CHARS])
            filtered_embeddings.append(embedding)

            metadatas.append({
                "file_path": chunk.file_path,
                "relative_path": chunk.relative_path,
                "start_line": chunk.start_line,
                "end_line": chunk.end_line,
                "symbol_name": chunk.symbol_name or "",
                "symbol_type": chunk.symbol_type,
                "language": chunk.language,
            })

        for i in range(0, len(ids), UPSERT_BATCH_SIZE):
            self.collection.upsert(
                ids=ids[i:i + UPSERT_BATCH_SIZE],
                documents=documents[i:i + UPSERT_BATCH_SIZE],
                embeddings=filtered_embeddings[i:i + UPSERT_BATCH_SIZE],
                metadatas=metadatas[i:i + UPSERT_BATCH_SIZE],
            )

    def search(
        self,
        query_embedding: list[float],
        top_k: int = 4,
    ) -> list[dict]:
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            include=["documents", "metadatas", "distances"],
        )

        items = []

        documents = results.get("documents", [[]])[0]
        metadatas = results.get("metadatas", [[]])[0]
        distances = results.get("distances", [[]])[0]

        for doc, meta, distance in zip(documents, metadatas, distances):
            items.append({
                "content": doc,
                "metadata": meta,
                "distance": distance,
                "score": 1 - distance,
            })

        return items

    def reset(self) -> None:
        try:
            self.client.delete_collection(CHROMA_COLLECTION_NAME)
        except Exception:
            pass

        self.collection = self.client.get_or_create_collection(
            name=CHROMA_COLLECTION_NAME,
            metadata={"hnsw:space": "cosine"},
        )


vector_store = VectorStore()