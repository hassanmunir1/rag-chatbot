"""Central configuration (read from environment / .env)."""
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent
UPLOAD_DIR = BASE_DIR / "data" / "uploads"
CHROMA_DIR = str(BASE_DIR / "chroma_db")
COLLECTION_NAME = "rag_documents"

LLM_PROVIDER = os.getenv("LLM_PROVIDER", "ollama").lower()
LLM_MODEL = os.getenv("LLM_MODEL", "llama3.1")
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
EMBEDDING_MODEL = os.getenv(
    "EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2"
)

CHUNK_SIZE = 1000
CHUNK_OVERLAP = 150
TOP_K = 4            # chunks passed to the LLM
MAX_HISTORY_TURNS = 5  # past Q/A pairs kept in the prompt

SUPPORTED_EXTENSIONS = {".pdf", ".docx", ".txt", ".xlsx", ".xls"}
