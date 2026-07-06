"""
MAMET OS - Entry Point
=======================
File ini adalah titik awal booting MAMET OS.
Menjalankan FastAPI server dan memanggil Main Orchestrator.

Analog: Bootloader pada sistem operasi.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional

# ---------------------------------------------------------------------------
# Kernel MAMET OS
# ---------------------------------------------------------------------------
from orchestrator.main_orchestrator import MainOrchestrator

# ---------------------------------------------------------------------------
# Inisialisasi Aplikasi
# ---------------------------------------------------------------------------
app = FastAPI(
    title="MAMET OS",
    description="Sistem Operasi Kognitif Tiga Kanal",
    version="0.1.0"
)

# CORS - Izinkan akses dari frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Akan dibatasi nanti
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Inisialisasi Kernel
# ---------------------------------------------------------------------------
kernel = MainOrchestrator()

# ---------------------------------------------------------------------------
# Model Request/Response
# ---------------------------------------------------------------------------
class ChatRequest(BaseModel):
    """Request dari user melalui salah satu kolom chat."""
    user_id: str              # Email user yang login
    column: str               # "kolom1", "kolom2", "kolom3"
    message: str              # Isi pesan user
    api_key: Optional[str] = None  # OpenRouter API key user

class ChatResponse(BaseModel):
    """Response dari MAMET OS ke user."""
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
    """Health check."""
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
    Kernel yang memutuskan bagaimana memprosesnya.
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

# ---------------------------------------------------------------------------
# Startup & Shutdown
# ---------------------------------------------------------------------------

@app.on_event("startup")
async def startup():
    """Dijalankan saat server mulai."""
    await kernel.boot()
    print("✅ MAMET OS booted successfully")

@app.on_event("shutdown")
async def shutdown():
    """Dijalankan saat server berhenti."""
    await kernel.shutdown()
    print("👋 MAMET OS shutdown complete")