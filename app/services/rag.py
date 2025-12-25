from sqlalchemy.orm import Session

from app.db.models import Chunk, Document
from app.services.embedder import embed_query
from app.services.vector_store import FaissStore
from app.services.llm import chat_text, chat_json
from app.services.prompts import (
    build_answer_prompt,
    build_completeness_prompt,
    build_enrichment_prompt,
)

def _retrieve_chunks(db: Session, store: FaissStore, question: str, top_k: int):
    qvec = embed_query(question)
    faiss_ids, scores = store.search(qvec, top_k=top_k)

    # Filter invalid IDs (FAISS returns -1 if not enough results)
    valid = [(fid, scores[i]) for i, fid in enumerate(faiss_ids) if fid is not None and fid >= 0]
    if not valid:
        return [], []

    fids = [v[0] for v in valid]
    score_map = {v[0]: float(v[1]) for v in valid}

    chunks = db.query(Chunk).filter(Chunk.faiss_id.in_(fids)).all()
    chunk_by_fid = {c.faiss_id: c for c in chunks}

    ordered_chunks = [chunk_by_fid[fid] for fid in fids if fid in chunk_by_fid]
    ordered_scores = [score_map.get(c.faiss_id, 0.0) for c in ordered_chunks]
    return ordered_chunks, ordered_scores

def answer_question(db: Session, store: FaissStore, question: str, top_k: int):
    chunks, scores = _retrieve_chunks(db, store, question, top_k)
    contexts = [c.text for c in chunks]

    if not contexts:
        return {
            "answer": "I don’t have enough indexed context to answer that yet. Please upload relevant documents.",
            "confidence": 0.0,
            "citations": [],
            "missing_info": ["Relevant documents or sections that contain the answer."],
            "enrichment_suggestions": [
                {"type": "document", "suggestion": "Upload documents that cover this topic (policies, SOPs, specs, FAQs)."}
            ],
        }

    # Build filename map for better citations
    doc_ids = list({c.document_id for c in chunks})
    docs = db.query(Document).filter(Document.id.in_(doc_ids)).all()
    doc_map = {d.id: d.filename for d in docs}

    # 1) Grounded answer
    answer_prompt = build_answer_prompt(question, contexts)
    answer = chat_text(answer_prompt)

    # 2) Citations (chunk refs + doc filename)
    citations = []
    for i, c in enumerate(chunks):
        fname = doc_map.get(c.document_id, "unknown")
        quote = c.text[:260].replace("\n", " ").strip()
        if len(c.text) > 260:
            quote += "..."
        citations.append({
            "document_id": c.document_id,
            "filename": fname,
            "chunk_id": c.id,
            "chunk_index": c.chunk_index,
            "context_ref": f"Context #{i+1}",
            "similarity": round(float(scores[i]) if i < len(scores) else 0.0, 4),
            "quote": quote
        })

    # 3) Completeness check
    completeness_prompt = build_completeness_prompt(question, answer, contexts)
    completeness = chat_json(completeness_prompt)

    confidence = float(completeness.get("confidence", 0.5))
    missing_info = completeness.get("missing_info", []) or []

    # 4) Enrichment suggestions
    enrichment_suggestions = []
    if missing_info:
        enrichment_prompt = build_enrichment_prompt(missing_info)
        enrich = chat_json(enrichment_prompt)
        enrichment_suggestions = enrich.get("enrichment_suggestions", []) or []

    # 5) Light confidence adjustment based on retrieval strength
    if scores:
        best = max(scores)
        if best < 0.20:
            confidence = min(confidence, 0.55)
        if best < 0.10:
            confidence = min(confidence, 0.40)

    # Clamp
    confidence = max(0.0, min(1.0, confidence))

    return {
        "answer": answer,
        "confidence": round(confidence, 2),
        "citations": citations,
        "missing_info": missing_info,
        "enrichment_suggestions": enrichment_suggestions
    }
