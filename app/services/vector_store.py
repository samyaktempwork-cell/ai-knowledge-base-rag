import os
import numpy as np
import faiss
from app.core.config import settings

INDEX_PATH = os.path.join(settings.FAISS_DIR, "index.faiss")

class FaissStore:
    """
    Uses cosine similarity by:
    - L2 normalizing vectors
    - IndexFlatIP (inner product)
    """
    def __init__(self, dim: int):
        self.dim = int(dim)
        self.index: faiss.Index | None = None

    def load_or_create(self) -> "FaissStore":
        os.makedirs(settings.FAISS_DIR, exist_ok=True)

        if os.path.exists(INDEX_PATH):
            self.index = faiss.read_index(INDEX_PATH)
            # Validate dim
            if getattr(self.index, "d", None) != self.dim:
                raise RuntimeError(
                    f"FAISS index dim ({self.index.d}) does not match expected dim ({self.dim}). "
                    f"Delete data/faiss_index/index.faiss and re-upload documents."
                )
        else:
            self.index = faiss.IndexFlatIP(self.dim)

        return self

    def add(self, vectors: np.ndarray) -> list[int]:
        if self.index is None:
            raise RuntimeError("FAISS index not loaded.")
        if vectors.ndim != 2 or vectors.shape[1] != self.dim:
            raise ValueError(f"Expected vectors shape (n, {self.dim}), got {vectors.shape}")

        vecs = vectors.astype(np.float32)
        faiss.normalize_L2(vecs)

        start_id = self.index.ntotal
        self.index.add(vecs)
        return list(range(start_id, start_id + vecs.shape[0]))

    def search(self, query_vec: np.ndarray, top_k: int) -> tuple[list[int], list[float]]:
        if self.index is None:
            raise RuntimeError("FAISS index not loaded.")
        q = query_vec.astype(np.float32).reshape(1, -1)
        if q.shape[1] != self.dim:
            raise ValueError(f"Expected query dim {self.dim}, got {q.shape[1]}")
        faiss.normalize_L2(q)

        scores, ids = self.index.search(q, top_k)
        return ids[0].tolist(), scores[0].tolist()

    def count(self) -> int:
        if self.index is None:
            return 0
        return int(self.index.ntotal)

    def save(self) -> None:
        if self.index is None:
            raise RuntimeError("FAISS index not loaded.")
        faiss.write_index(self.index, INDEX_PATH)
