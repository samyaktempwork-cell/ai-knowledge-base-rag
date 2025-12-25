# AI Knowledge Base RAG

A **Retrieval-Augmented Generation (RAG)** system that enables teams to upload internal documents (PDF/DOCX), ask natural-language questions, and receive **grounded answers with citations, confidence scores, and missing-information detection**.

This repository is designed as a **production-ready MVP** that companies can easily replicate and extend.

---

##  Key Features

###  Document Ingestion
- Upload **PDF** and **DOCX** files
- Automatic text extraction and safe chunking
- Metadata stored in a relational database
- Vector embeddings indexed using **FAISS**

###  Intelligent Q&A (RAG)
- Semantic retrieval over uploaded documents
- LLM answers strictly grounded in retrieved context
- Document + chunk-level citations
- Confidence score per answer
- Explicit **missing information detection**
- Actionable **enrichment suggestions**

###  Built-in UI (No Frontend Build Needed)
- Upload documents via browser
- Ask questions interactively
- View answers, confidence, citations, missing info
- Expand raw JSON for debugging

###  Production-Safe Design
- Deterministic local embedding fallback when OpenAI embeddings fail
- Infinite-loop-safe chunking logic
- Memory-safe ingestion limits
- Step-by-step logging for observability

---

##  Architecture Overview

User / UI  
↓  
FastAPI Application  
- Document Upload API  
- Query API  
- FAISS Vector Store  
- SQL Metadata Store  

---

##  Project Structure

ai-knowledge-base-rag/
- app/
  - api/
  - services/
  - ui/
  - core/
  - db/
- data/
- pyproject.toml
- README.md
- .env

---

##  Getting Started

### Prerequisites
- Python 3.12+
- OpenAI API Key

### Setup
```bash
git clone <repo-url>
cd ai-knowledge-base-rag
uv sync
```

Create `.env`:
```env
OPENAI_API_KEY=sk-xxxx
```

Run:
```bash
uv run uvicorn app.main:app --reload
```

---

##  URLs

- UI: http://127.0.0.1:8000/ui
- Docs: http://127.0.0.1:8000/docs
- Health: http://127.0.0.1:8000/health

---

##  Summary

A clean, safe, and extensible RAG MVP suitable for enterprise knowledge systems.
