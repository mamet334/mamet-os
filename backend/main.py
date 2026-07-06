"""
MAMET OS - Entry Point
=======================
Titik awal booting MAMET OS.
Menjalankan FastAPI server, memanggil Main Orchestrator,
dan menyediakan endpoint upload dokumen untuk RAG.
"""

import os
from fastapi import FastAPI, HTTPException, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional

# ---------------------------------------------------------------------------
# Kernel MAMET OS
# ---------------------------------------------------------------------------
from orchestrator.main_orchestrator import MainOrchestrator

# ---------------------------------------------------------------------------
# RAG Engine
# ---------------------------------------------------------------------------
from rag.rag_engine import RAGEngine

# ---------------------------------------------------------------------------
# Inisialisasi Aplikasi
# ---------------------------------------------------------------------------
app = FastAPI(
    title="MAMET OS",
    description="Sistem Operasi Kognitif Tiga Kanal",
    version="0.1.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Inisialisasi Kernel & RAG
# ---------------------------------------------------------------------------
kernel = MainOrchestrator()
rag_engine = RAGEngine(persist_dir=os.path.join(os.getcwd(), "chroma_db"))

# ---------------------------------------------------------------------------
# Model Request/Response
# ---------------------------------------------------------------------------
class ChatRequest(BaseModel):
    user_id: str
    column: str
    message: str
    api_key: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    sources: list = []
    actions_taken: list = []
    requires_approval: bool = False
    approval_details: dict = {}

# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.get("/")
async def root():
    return {
        "system": "MAMET OS",
        "status": "running",
        "version": "0.1.0"
    }

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Endpoint utama chat.
    Semua kolom (1, 2, 3) masuk melalui sini.
    """
    try:
        result = await kernel.process(
            user_id=request.user_id,
            column=request.column,
            message=request.message,
            api_key=request.api_key
        )
        return ChatResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    api_key: Optional[str] = None
):
    """
    Upload dokumen ke RAG.
    Menerima file PDF, TXT, MD, DOCX, CSV, JSON.
    """
    try:
        content = await file.read()
        filename = file.filename

        # Parsing berdasarkan ekstensi
        if filename.endswith('.pdf'):
            try:
                import fitz
                doc = fitz.open(stream=content, filetype="pdf")
                text = ""
                for page in doc:
                    text += page.get_text()
            except ImportError:
                return {"status": "error", "message": "PyMuPDF tidak terinstall. Install: pip install PyMuPDF"}
        elif filename.endswith('.docx'):
            try:
                from docx import Document
                from io import BytesIO
                doc = Document(BytesIO(content))
                text = "\n".join([para.text for para in doc.paragraphs])
            except ImportError:
                return {"status": "error", "message": "python-docx tidak terinstall"}
        elif filename.endswith('.csv'):
            # CSV: dibaca sebagai teks, tetap bisa di-search
            text = content.decode('utf-8', errors='ignore')
        elif filename.endswith('.json'):
            import json
            data = json.loads(content.decode('utf-8'))
            text = json.dumps(data, indent=2, ensure_ascii=False)
        else:
            # TXT, MD, atau plain text
            text = content.decode('utf-8', errors='ignore')

        if not text.strip():
            return {"status": "error", "message": "Dokumen kosong"}

        # Set API key jika diberikan
        if api_key:
            rag_engine.set_api_key(api_key)

        # Tambahkan ke RAG
        result = rag_engine.add_document(text, filename)
        return result

    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.get("/rag/stats")
async def rag_stats():
    """Statistik RAG."""
    return rag_engine.get_stats()

@app.on_event("startup")
async def startup():
    await kernel.boot()
    print("✅ MAMET OS booted successfully")

@app.on_event("shutdown")
async def shutdown():
    await kernel.shutdown()
    print("👋 MAMET OS shutdown complete")