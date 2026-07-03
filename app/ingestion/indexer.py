from app.ingestion.git_ops import clone_or_update_repo
from app.ingestion.file_loader import load_code_files
from app.ingestion.parser import parse_code_files
from app.models.embeddings import embedding_model
from app.retrieval.vector_store import vector_store


def index_repository(repo_url: str, reset_index: bool = True) -> dict:
    if reset_index:
        vector_store.reset()

    repo_path = clone_or_update_repo(repo_url)

    code_files = load_code_files(repo_path)

    if not code_files:
        return {
            "repo_path": str(repo_path),
            "files_indexed": 0,
            "chunks_indexed": 0,
            "message": "No supported code files found. Supported: .py, .js, .jsx, .ts, .tsx",
        }

    chunks = parse_code_files(code_files)

    if not chunks:
        return {
            "repo_path": str(repo_path),
            "files_indexed": len(code_files),
            "chunks_indexed": 0,
            "message": "Code files found, but no chunks were created.",
        }

    texts = []

    for chunk in chunks:
        text = f"""
File: {chunk.relative_path}
Symbol: {chunk.symbol_name}
Type: {chunk.symbol_type}
Language: {chunk.language}

Code:
{chunk.content[:2500]}
"""
        texts.append(text)

    embeddings = embedding_model.embed_texts(texts)

    if not embeddings:
        return {
            "repo_path": str(repo_path),
            "files_indexed": len(code_files),
            "chunks_indexed": len(chunks),
            "message": "Embeddings were not created.",
        }

    vector_store.add_chunks(chunks, embeddings)

    return {
        "repo_path": str(repo_path),
        "files_indexed": len(code_files),
        "chunks_indexed": len(chunks),
        "message": "Repository indexed successfully.",
    }