from app.config import TOP_K
from app.models.embeddings import embedding_model
from app.retrieval.vector_store import vector_store


def retrieve_relevant_chunks(
    question: str,
    top_k: int = TOP_K,
) -> list[dict]:
    query_embedding = embedding_model.embed_query(question)

    results = vector_store.search(
        query_embedding=query_embedding,
        top_k=5,
    )

    print("=" * 80)
    print("Retrieved Results")
    print("=" * 80)

    for r in results:
        print(r["score"], r["metadata"]["relative_path"])

    return results

    #return filtered