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
    agent: Optional[str] = None

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
            api_key=req.api_key,
            agent=req.agent
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

# ================= AUTHENTICATION & DASHBOARD ================= #

class AuthRequest(BaseModel):
    email: str
    password: str

@app.post("/api/register")
async def register(req: AuthRequest):
    from auth.auth_handler import AuthHandler
    handler = AuthHandler()
    success = handler.register_user(req.email, req.password)
    if not success:
        raise HTTPException(status_code=400, detail="Email sudah terdaftar.")
    token = handler.create_access_token({"sub": req.email})
    return {"token": token, "message": "Pendaftaran berhasil"}

@app.post("/api/login")
async def login(req: AuthRequest):
    from auth.auth_handler import AuthHandler
    handler = AuthHandler()
    if not handler.verify_user(req.email, req.password):
        raise HTTPException(status_code=401, detail="Email atau password salah.")
    token = handler.create_access_token({"sub": req.email})
    return {"token": token, "email": req.email}

@app.get("/api/status")
async def get_system_status(email: str = "default"):
    """Mengembalikan status sistem untuk Dashboard Awal."""
    try:
        # Provider aktif
        from ai.provider_router import ProviderRouter
        router = ProviderRouter(email)
        provider = router.get_active_provider()
        provider_name = provider.name if provider else "Tidak ada"
        
        # RAG Status
        try:
            from rag.rag_engine import RAGEngine
            rag = RAGEngine()
            doc_count = len(rag.collection.get(include=['metadatas'])['ids'])
        except:
            doc_count = 0
            
        # User Memory Status
        from memory.user_memory import UserMemory
        memory = UserMemory(email)
        stats = memory.get_stats()
        fact_count = stats.get("total_facts", 0)
        
        # Budget
        from ai.usage_tracker import UsageTracker
        tracker = UsageTracker(email)
        budget = tracker.get_budget_status()
        
        # Backups
        from engineer.sandbox import EngineerSandbox
        sandbox = EngineerSandbox()
        backup_count = len(sandbox.list_backups())
        
        return {
            "kernel": "Tersambung",
            "ai_provider": provider_name,
            "rag": {"docs": doc_count},
            "memory": {"facts": fact_count},
            "engineer": "Siap",
            "backup": {"count": backup_count},
            "budget": budget
        }
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)