from app.ingestion.indexer import index_repository
from app.retrieval.retriever import retrieve_relevant_chunks
from app.retrieval.reranker import rerank_results
from app.generation.qa_engine import qa_engine


class CodebaseQAPipeline:

    def index_repo(self, repo_url: str):

        return index_repository(repo_url)

    def ask(self, question: str):

        retrieved = retrieve_relevant_chunks(question)

        reranked = rerank_results(retrieved)

        answer = qa_engine.answer(
            question=question,
            retrieved_chunks=reranked,
        )

        return {
            "answer": answer,
            "sources": reranked,
        }


pipeline = CodebaseQAPipeline()