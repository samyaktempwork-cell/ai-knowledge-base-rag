import os
import json
import hashlib
import numpy as np
from app.core.config import settings

META_PATH = os.path.join(settings.FAISS_DIR, "meta.json")

# Keep a stable dim for fallback so FAISS/indexing stays consistent
DEFAULT_DIM = 1536


def _client():
    if not settings.OPENAI_API_KEY:
        raise RuntimeError("OPENAI_API_KEY is not set.")
    from openai import OpenAI
    # timeout prevents "infinite loading" behavior
    return OpenAI(api_key=settings.OPENAI_API_KEY, timeout=20.0, max_retries=1)


def _local_fallback_embedding(text: str, dim: int = DEFAULT_DIM) -> np.ndarray:
    """
    Deterministic local embedding fallback using hashing.
    This is NOT semantically meaningful like real embeddings, but it:
    - prevents the system from hanging
    - keeps FAISS indexing/retrieval functional for demo
    - keeps dimensions stable
    """
    # sha256 -> 32 bytes; expand to dim by tiling
    digest = hashlib.sha256((text or "").encode("utf-8")).digest()
    base = np.frombuffer(digest, dtype=np.uint8).astype(np.float32)  # (32,)
    vec = np.tile(base, (dim // base.size) + 1)[:dim]

    # Normalize to unit length for cosine/IP usage
    norm = np.linalg.norm(vec)
    if norm > 0:
        vec = vec / norm
    return vec.astype(np.float32)


def embed_texts(texts: list[str]) -> np.ndarray:
    """
    Returns: (n, dim) float32 embeddings.
    Uses OpenAI embeddings when available; falls back to deterministic local embeddings
    when OpenAI is unavailable or quota-limited.
    """
    if not texts:
        return np.zeros((0, DEFAULT_DIM), dtype=np.float32)

    # Try OpenAI embeddings
    if settings.OPENAI_API_KEY:
        try:
            client = _client()
            resp = client.embeddings.create(
                model=settings.EMBED_MODEL,
                input=texts
            )
            vectors = np.array([item.embedding for item in resp.data], dtype=np.float32)

            # Persist dimension so FAISS can validate dim on next run
            if vectors.size > 0:
                persist_embedding_dim(int(vectors.shape[1]))

            return vectors

        except Exception as e:
            # Handle quota/network issues gracefully
            print(f"[WARN] OpenAI embeddings unavailable, using local fallback. Reason: {e}")

    # Local fallback
    dim = get_embedding_dim()
    vectors = np.stack([_local_fallback_embedding(t, dim=dim) for t in texts], axis=0)
    return vectors.astype(np.float32)


def embed_query(text: str) -> np.ndarray:
    return embed_texts([text])[0]


def persist_embedding_dim(dim: int) -> None:
    os.makedirs(settings.FAISS_DIR, exist_ok=True)
    payload = {"embedding_dim": int(dim), "embed_model": settings.EMBED_MODEL}
    with open(META_PATH, "w", encoding="utf-8") as f:
        json.dump(payload, f)


def get_embedding_dim() -> int:
    """
    Uses persisted meta.json if present; otherwise returns DEFAULT_DIM.
    """
    if os.path.exists(META_PATH):
        try:
            with open(META_PATH, "r", encoding="utf-8") as f:
                meta = json.load(f)
            d = int(meta.get("embedding_dim"))
            if d > 0:
                return d
        except Exception:
            pass

    return DEFAULT_DIM
