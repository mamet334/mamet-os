from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
from typing import Optional, Dict, Any
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import asyncio

from orchestrator.main_orchestrator import MainOrchestrator

app = FastAPI(title="MAMET OS API", description="API untuk MAMET OS Kernel")

# Setup CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global orchestrator instance
orchestrator = MainOrchestrator()

class ChatRequest(BaseModel):
    user_id: str
    column: str
    message: str
    api_key: Optional[str] = None

@app.on_event("startup")
async def startup_event():
    print("[API] Mem-booting MAMET OS Kernel...")
    await orchestrator.boot()

@app.on_event("shutdown")
async def shutdown_event():
    print("[API] Mematikan MAMET OS Kernel...")
    await orchestrator.shutdown()

@app.post("/api/process")
async def process_chat(req: ChatRequest):
    """Endpoint utama untuk memproses chat dari UI."""
    try:
        response = await orchestrator.process(
            user_id=req.user_id,
            column=req.column,
            message=req.message,
            api_key=req.api_key
        )
        return response
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

from fastapi import UploadFile, File

@app.post("/api/upload")
async def upload_document(file: UploadFile = File(...)):
    """Endpoint untuk mengunggah dokumen ke RAG."""
    try:
        content = await file.read()
        text_content = content.decode('utf-8', errors='ignore')
        
        # Inisialisasi RAGEngine
        from rag.rag_engine import RAGEngine
        rag = RAGEngine()
        
        result = rag.add_document(text_content, filename=file.filename)
        return result
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/budget")
async def get_budget(email: str = "default"):
    """Dapatkan status budget dan limit."""
    try:
        from ai.usage_tracker import UsageTracker
        tracker = UsageTracker(email)
        return tracker.get_budget_status()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/backups")
async def get_backups():
    """Dapatkan daftar backup (Sandbox Rollback)."""
    try:
        from engineer.sandbox import EngineerSandbox
        sandbox = EngineerSandbox()
        return {"backups": sandbox.list_backups()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

class RollbackRequest(BaseModel):
    filename: str

@app.post("/api/rollback")
async def execute_rollback(req: RollbackRequest):
    """Eksekusi rollback ke versi zip tertentu."""
    try:
        from engineer.sandbox import EngineerSandbox
        sandbox = EngineerSandbox()
        result = sandbox.rollback_to(req.filename)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)