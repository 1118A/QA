from sentence_transformers import SentenceTransformer

from app.config import EMBEDDING_MODEL_NAME


class EmbeddingModel:
    def __init__(self):
        self.model = SentenceTransformer(EMBEDDING_MODEL_NAME)

    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        embeddings = self.model.encode(
            texts,
            normalize_embeddings=True,
            show_progress_bar=True,
        )
        return embeddings.tolist()

    def embed_query(self, query: str) -> list[float]:
        embedding = self.model.encode(
            [query],
            normalize_embeddings=True,
        )
        return embedding[0].tolist()


embedding_model = EmbeddingModel()