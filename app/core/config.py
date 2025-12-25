from dotenv import load_dotenv
load_dotenv()

import os
from pydantic import BaseModel

class Settings(BaseModel):
    APP_NAME: str = "AI Knowledge Base RAG"

    DATA_DIR: str = os.getenv("DATA_DIR", "data")
    UPLOAD_DIR: str = os.getenv("UPLOAD_DIR", os.path.join("data", "uploads"))
    FAISS_DIR: str = os.getenv("FAISS_DIR", os.path.join("data", "faiss_index"))
    DB_URL: str = os.getenv("DB_URL", "sqlite:///./data/app.db")

    OPENAI_API_KEY: str | None = os.getenv("OPENAI_API_KEY")
    EMBED_MODEL: str = os.getenv("EMBED_MODEL", "text-embedding-3-small")
    CHAT_MODEL: str = os.getenv("CHAT_MODEL", "gpt-4o-mini")

    CHUNK_SIZE_CHARS: int = int(os.getenv("CHUNK_SIZE_CHARS", "2500"))
    CHUNK_OVERLAP_CHARS: int = int(os.getenv("CHUNK_OVERLAP_CHARS", "250"))

    TOP_K_DEFAULT: int = int(os.getenv("TOP_K_DEFAULT", "6"))
    MAX_TOP_K: int = int(os.getenv("MAX_TOP_K", "12"))

settings = Settings()
