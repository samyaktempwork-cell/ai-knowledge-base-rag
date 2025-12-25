import os

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from dotenv import load_dotenv

from app.core.config import settings
from app.api.documents import router as documents_router
from app.api.query import router as query_router
from app.db.models import Base
from app.db.session import engine

# Load environment variables early
load_dotenv()

app = FastAPI(title=settings.APP_NAME)

# -------------------------
# Startup
# -------------------------
@app.on_event("startup")
def on_startup() -> None:
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    os.makedirs(settings.FAISS_DIR, exist_ok=True)
    os.makedirs(settings.DATA_DIR, exist_ok=True)
    # Create DB tables
    Base.metadata.create_all(bind=engine)

# -------------------------
# API Routers
# -------------------------
app.include_router(documents_router)
app.include_router(query_router)

# -------------------------
# UI Mount
# -------------------------
templates = Jinja2Templates(directory="app/ui/templates")
app.mount("/ui/static", StaticFiles(directory="app/ui/static"), name="ui-static")

@app.get("/ui", response_class=HTMLResponse)
def ui_home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# -------------------------
# Health / Root
# -------------------------
@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/")
def root():
    return {
        "message": "AI Knowledge Base RAG is running",
        "endpoints": {
            "health": "/health",
            "docs": "/docs",
            "ui": "/ui",
            "upload": "/v1/documents/upload",
            "query": "/v1/query"
        }
    }
