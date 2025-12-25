#  AI Knowledge Base RAG

A **Retrieval-Augmented Generation (RAG)** system that allows teams to upload internal documents (PDF/DOCX), ask natural-language questions, and receive **grounded answers with citations, confidence scores, and explicit missing-information detection**.

This project is designed as a **production-aware MVP** that is easy to run locally, safe against hallucinations, and simple for companies to replicate.

---

##  Key Highlights

-  Upload and index PDF / DOCX documents  
-  Ask natural-language questions over uploaded content  
-  Answers are **strictly grounded** in retrieved document context  
-  Chunk-level **citations** for traceability  
-  Confidence scoring per answer  
-  Explicit **missing information detection** (no hallucination)  
-  Actionable enrichment suggestions  
-  Built-in UI (no frontend build required)  
-  Safe ingestion with logging, limits, and fallbacks  

---

##  Architecture Overview

```
User / Browser UI
        ↓
     FastAPI
        ├── Document Upload API
        │     ├── Text Extraction
        │     ├── Safe Chunking
        │     ├── Embeddings (OpenAI → Fallback)
        │     ├── FAISS Vector Store
        │     └── SQL Metadata Store
        │
        └── Query API
              ├── Query Embedding
              ├── Vector Similarity Search
              ├── Context Assembly
              ├── LLM Answer Generation
              └── Confidence + Enrichment Logic
```

---

##  Project Structure

```
ai-knowledge-base-rag/
├── app/
│   ├── api/          # Upload & query endpoints
│   ├── services/     # Extraction, chunking, embeddings, RAG
│   ├── ui/           # HTML / JS / CSS UI
│   ├── core/         # Configuration
│   ├── db/           # Database models & session
│   └── main.py       # Application entry point
│
├── data/
│   ├── uploads/      # Uploaded documents
│   └── faiss/        # FAISS index + metadata
│
├── pyproject.toml
├── README.md
└── .env
```

---

##  Getting Started (Company Replication Guide)

### 1️⃣ Prerequisites
- Python **3.12+**
- Windows / macOS / Linux
- OpenAI API key (chat API)

---

### 2️⃣ Clone Repository
```bash
git clone <repo-url>
cd ai-knowledge-base-rag
```

---

### 3️⃣ Create `.env` File
```env
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxx
```

> ℹ️ If embedding quota is unavailable, the system automatically uses a deterministic local embedding fallback so ingestion never blocks.

---

### 4️⃣ Install Dependencies
```bash
uv sync
```

---

### 5️⃣ Run the Application
```bash
uv run uvicorn app.main:app --reload
```

---

##  Access URLs

| Feature | URL |
|------|----|
| UI | http://127.0.0.1:8000/ui |
| Swagger Docs | http://127.0.0.1:8000/docs |
| Health Check | http://127.0.0.1:8000/health |
| Upload API | /v1/documents/upload |
| Query API | /v1/query |

---

## 🖥️ Using the UI

1. Open `/ui`  
2. Upload one or more documents  
3. Ask a question  
4. Review:
   - Answer  
   - Confidence score  
   - Citations  
   - Missing information  
   - Enrichment suggestions  

---

##  Design Trade-offs & Limitations

- **Vector Store (FAISS):**  
  Local FAISS index for simplicity and zero infrastructure.  
  *Limitation:* single-node, not horizontally scalable.

- **Embeddings & Fallback:**  
  OpenAI embeddings with deterministic local fallback.  
  *Limitation:* fallback embeddings are not semantically rich.

- **Chunking Strategy:**  
  Character-based chunking with validated overlap.  
  *Limitation:* not semantically aligned.

- **Confidence & Missing Info:**  
  Heuristic confidence scoring with explicit gap reporting.  
  *Limitation:* not statistically calibrated.

- **UI Scope:**  
  Minimal FastAPI-served UI.  
  *Limitation:* no authentication.

- **Testing:**  
  No formal unit tests due to time constraints; system is observable via logs and UI.

---

##  Summary

This project demonstrates **real-world RAG engineering** with an emphasis on:

- Trust and explainability  
- Safe AI behavior  
- Production-aware trade-offs  
- Clear extensibility path  

It is suitable for **enterprise knowledge bases, internal Q&A systems, and AI platform evaluations**.
