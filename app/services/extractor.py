from pathlib import Path
from pypdf import PdfReader
from docx import Document as DocxDocument

SUPPORTED_EXTS = {".pdf", ".docx", ".txt", ".md"}

def extract_text(file_path: str) -> str:
    p = Path(file_path)
    ext = p.suffix.lower()

    if ext not in SUPPORTED_EXTS:
        raise ValueError(f"Unsupported file type: {ext}. Supported: {sorted(SUPPORTED_EXTS)}")

    if ext in [".txt", ".md"]:
        return p.read_text(encoding="utf-8", errors="ignore")

    if ext == ".pdf":
        reader = PdfReader(file_path)
        pages = []
        for page in reader.pages:
            pages.append(page.extract_text() or "")
        return "\n".join(pages)

    if ext == ".docx":
        doc = DocxDocument(file_path)
        return "\n".join([para.text for para in doc.paragraphs])

    raise ValueError(f"Unhandled file extension: {ext}")
