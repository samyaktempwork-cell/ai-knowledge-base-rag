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

##  Using the UI

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
---

##  Sample Test Files & Quick Validation

This repo can be tested end-to-end using the built-in UI **or** the APIs below.

###  Sample documents (recommended)
Add these to your repo under `sample_docs/` (or use your own PDFs/DOCXs):

- `sample_docs/WIND_Synthesis_AI_Overview_Sample.pdf`
- `sample_docs/Sample_Knowledge_Base_DOCX.docx`

###  Test via UI (fastest)
1. Start the server:
   ```bash
   uv run uvicorn app.main:app --reload
   ```
2. Open the UI:
   - `http://127.0.0.1:8000/ui`
3. Upload one or both sample files, then run the questions below.

###  Test via API (curl)
**Upload (Windows PowerShell):**
```powershell
curl -v -X POST "http://127.0.0.1:8000/v1/documents/upload" `
  -F "files=@sample_docs/WIND_Synthesis_AI_Overview_Sample.pdf" `
  -F "files=@sample_docs/Sample_Knowledge_Base_DOCX.docx"
```

**Ask a question (answerable):**
```powershell
curl -X POST "http://127.0.0.1:8000/v1/query" `
  -H "Content-Type: application/json" `
  -d "{ ""question"": ""List the core tasks and responsibilities of WIND Synthesis AI."", ""top_k"": 6 }"
```

**Ask a question (should be missing info / no hallucination):**
```powershell
curl -X POST "http://127.0.0.1:8000/v1/query" `
  -H "Content-Type: application/json" `
  -d "{ ""question"": ""What is the annual revenue and headquarters location of WIND Synthesis AI?"", ""top_k"": 6 }"
```

###  Suggested evaluation questions
Use these to validate key behaviors:

**Grounded answer + citations**
- “What is WIND Synthesis AI focused on?”
- “List the core tasks and responsibilities of WIND Synthesis AI.”
- “How does this system prevent hallucinations?”

**Missing info detection**
- “What is the annual revenue of WIND Synthesis AI?”
- “Where is WIND Synthesis AI headquartered?”

**Cross-document retrieval**
- “What does the DOCX say about missing information detection?”
- “How does the system generate citations?”
