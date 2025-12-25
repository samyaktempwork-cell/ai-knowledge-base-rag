import os
import shutil
import time

from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.session import get_db
from app.db.models import Document, Chunk
from app.services.extractor import extract_text, SUPPORTED_EXTS
from app.services.chunker import chunk_text
from app.services.embedder import embed_texts, persist_embedding_dim
from app.services.vector_store import FaissStore

router = APIRouter(prefix="/v1/documents", tags=["documents"])


@router.get("")
def list_documents(db: Session = Depends(get_db)):
    docs = db.query(Document).order_by(Document.created_at.desc()).all()
    return [
        {
            "document_id": d.id,
            "filename": d.filename,
            "source_type": d.source_type,
            "created_at": d.created_at.isoformat(),
        }
        for d in docs
    ]


@router.post("/upload")
async def upload_documents(files: list[UploadFile] = File(...), db: Session = Depends(get_db)):
    if not files:
        raise HTTPException(status_code=400, detail="No files provided.")

    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    os.makedirs(settings.FAISS_DIR, exist_ok=True)

    uploaded: list[dict] = []

    store: FaissStore | None = None

    # Safety limits (prevents huge RAM usage / long calls)
    MAX_TEXT_CHARS = int(os.getenv("MAX_TEXT_CHARS", "60000"))
    MAX_CHUNKS = int(os.getenv("MAX_CHUNKS", "25"))

    for f in files:
        overall_start = time.perf_counter()

        try:
            _, ext = os.path.splitext(f.filename or "")
            ext = (ext or "").lower()
            if ext not in SUPPORTED_EXTS:
                raise HTTPException(
                    status_code=400,
                    detail=f"Unsupported file type '{ext}'. Supported: {sorted(SUPPORTED_EXTS)}",
                )

            # Create doc record
            doc = Document(filename=f.filename, source_type="upload")
            db.add(doc)
            db.commit()
            db.refresh(doc)

            print(f"[UPLOAD] Start doc_id={doc.id} file={f.filename}")

            # Save file to disk
            safe_name = f"{doc.id}_{os.path.basename(f.filename)}"
            file_path = os.path.join(settings.UPLOAD_DIR, safe_name)

            t = time.perf_counter()
            with open(file_path, "wb") as out:
                shutil.copyfileobj(f.file, out)

            # Close upload stream
            try:
                await f.close()
            except Exception:
                pass

            print(f"[UPLOAD] Saved file in {time.perf_counter() - t:.2f}s path={file_path}")

            # Extract
            t = time.perf_counter()
            text = extract_text(file_path)
            print(f"[UPLOAD] Extracted chars={len(text)} in {time.perf_counter() - t:.2f}s")

            # Trim huge docs (demo-safe)
            if len(text) > MAX_TEXT_CHARS:
                print(f"[UPLOAD] Trimming text {len(text)} -> {MAX_TEXT_CHARS}")
                text = text[:MAX_TEXT_CHARS]

            # Chunk
            print("[UPLOAD] Chunking start...")
            t = time.perf_counter()
            chunks = chunk_text(text)
            print(f"[UPLOAD] Chunking done chunks={len(chunks)} in {time.perf_counter() - t:.2f}s")

            if not chunks:
                uploaded.append({"document_id": doc.id, "filename": f.filename, "chunks": 0})
                print(f"[UPLOAD] Done (no chunks). total={time.perf_counter() - overall_start:.2f}s")
                continue

            # Limit chunks (demo-safe)
            if len(chunks) > MAX_CHUNKS:
                print(f"[UPLOAD] Limiting chunks {len(chunks)} -> {MAX_CHUNKS}")
                chunks = chunks[:MAX_CHUNKS]

            # Embed
            print("[UPLOAD] Embedding start...")
            t = time.perf_counter()
            vectors = embed_texts(chunks)  # (n, dim)
            print(f"[UPLOAD] Embedding done shape={vectors.shape} in {time.perf_counter() - t:.2f}s")

            embedding_dim = int(vectors.shape[1])
            persist_embedding_dim(embedding_dim)

            # Load FAISS store once we know dim
            if store is None:
                t = time.perf_counter()
                store = FaissStore(dim=embedding_dim).load_or_create()
                print(f"[UPLOAD] FAISS load_or_create in {time.perf_counter() - t:.2f}s")

            # Add to FAISS
            t = time.perf_counter()
            faiss_ids = store.add(vectors)
            print(f"[UPLOAD] FAISS add vectors={len(faiss_ids)} in {time.perf_counter() - t:.2f}s")

            # Store chunks in DB with faiss_id mapping
            t = time.perf_counter()
            for idx, (chunk_val, fid) in enumerate(zip(chunks, faiss_ids)):
                db.add(
                    Chunk(
                        document_id=doc.id,
                        chunk_index=idx,
                        text=chunk_val,
                        faiss_id=fid,
                    )
                )
            db.commit()
            print(f"[UPLOAD] DB commit chunks={len(faiss_ids)} in {time.perf_counter() - t:.2f}s")

            # Save FAISS index
            t = time.perf_counter()
            store.save()
            print(f"[UPLOAD] FAISS save in {time.perf_counter() - t:.2f}s")

            # Free memory sooner
            del vectors
            del chunks

            uploaded.append({"document_id": doc.id, "filename": f.filename, "chunks": len(faiss_ids)})
            print(f"[UPLOAD] Done doc_id={doc.id} total={time.perf_counter() - overall_start:.2f}s")

        except HTTPException:
            # pass FastAPI errors through
            raise
        except Exception as e:
            # rollback to avoid DB lock/partial writes
            db.rollback()
            print(f"[UPLOAD][ERROR] file={getattr(f, 'filename', None)} error={e}")
            raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

    return {"uploaded": uploaded}
