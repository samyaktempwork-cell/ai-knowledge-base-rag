from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.session import get_db
from app.services.vector_store import FaissStore
from app.services.rag import answer_question
from app.services.embedder import get_embedding_dim

router = APIRouter(prefix="/v1", tags=["query"])

class QueryRequest(BaseModel):
    question: str = Field(min_length=3, max_length=5000)
    top_k: int | None = None

@router.post("/query")
def query(req: QueryRequest, db: Session = Depends(get_db)):
    top_k = req.top_k or settings.TOP_K_DEFAULT
    if top_k < 1:
        top_k = 1
    if top_k > settings.MAX_TOP_K:
        top_k = settings.MAX_TOP_K

    dim = get_embedding_dim()
    store = FaissStore(dim=dim).load_or_create()

    if store.count() == 0:
        raise HTTPException(status_code=400, detail="No documents indexed yet. Upload documents first.")

    return answer_question(db, store, req.question, top_k)
