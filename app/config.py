import os
from dotenv import load_dotenv
from pathlib import Path
load_dotenv()

BASE_DIR =  Path(__file__).resolve().parent.parent

DATA_DIR = BASE_DIR / "data"
REPOS_DIR = DATA_DIR / "repos"
CHROMA_DIR = DATA_DIR / "chroma"

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

EMBEDDING_MODEL_NAME = "BAAI/bge-small-en-v1.5"

SUPPORTED_EXTENSIONS = [
    ".py",
    ".js",
    ".jsx",
    ".ts",
    ".tsx",
]

CHROMA_COLLECTION_NAME = "codebase_qa"

GROQ_MODEL = "llama-3.3-70b-versatile"

TOP_K = 8