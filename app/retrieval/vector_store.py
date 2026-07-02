import chromadb

from app.config import CHROMA_DIR, CHROMA_COLLECTION_NAME
from app.models.schemas import CodeChunk


class VectorStore:
    def __init__(self):
        CHROMA_DIR.mkdir(parents=True, exist_ok=True)

        self.client = chromadb.PersistentClient(
            path=str(CHROMA_DIR)
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
        if not chunks:
            return

        if not embeddings:
            return

        ids = []
        documents = []
        metadatas = []

        for chunk in chunks:
            ids.append(chunk.chunk_id)
            documents.append(chunk.content)
            metadatas.append({
                "file_path": chunk.file_path,
                "relative_path": chunk.relative_path,
                "start_line": chunk.start_line,
                "end_line": chunk.end_line,
                "symbol_name": chunk.symbol_name or "",
                "symbol_type": chunk.symbol_type,
                "language": chunk.language,
            })

        self.collection.upsert(
            ids=ids,
            documents=documents,
            embeddings=embeddings,
            metadatas=metadatas,
        )

    def search(
        self,
        query_embedding: list[float],
        top_k: int = 8,
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