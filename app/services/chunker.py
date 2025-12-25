from app.core.config import settings


def chunk_text(text: str) -> list[str]:
    """
    Safe char-based chunking for MVP speed and reliability.

    Fixes infinite-loop cases when overlap >= size or when the window doesn't progress.
    Guarantees forward progress by using a positive step size.
    """
    size = int(settings.CHUNK_SIZE_CHARS)
    overlap = int(settings.CHUNK_OVERLAP_CHARS)

    text = (text or "").strip()
    if not text:
        return []

    # Safety: ensure overlap is not >= size
    if overlap >= size:
        overlap = max(0, size // 10)  # default to 10% overlap

    step = size - overlap
    if step <= 0:
        step = size  # guarantee progress

    chunks: list[str] = []
    n = len(text)

    start = 0
    while start < n:
        end = min(n, start + size)
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)

        if end >= n:
            break

        start += step  # always moves forward

    return chunks
