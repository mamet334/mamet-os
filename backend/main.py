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
    project_context: Optional[str] = None

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
            agent=req.agent,
            project_context=req.project_context
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

# ================= PROVIDER CONFIGURATION ================= #

class ProviderRequest(BaseModel):
    email: str
    name: str
    api_key: str
    priority: int = 1

@app.post("/api/provider")
async def save_provider(req: ProviderRequest):
    try:
        from ai.provider_router import ProviderRouter
        router = ProviderRouter(email=req.email)
        router.add_provider(req.name, req.api_key, req.priority)
        return {"status": "success", "message": f"Provider {req.name} tersimpan"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/providers")
async def get_providers(email: str = "default"):
    try:
        import sqlite3
        import os
        db_path = os.path.join(os.path.expanduser("~"), ".mamet", email, "memory.db")
        if not os.path.exists(db_path):
            return {"providers": []}
            
        with sqlite3.connect(db_path) as conn:
            rows = conn.execute("SELECT name, is_active, priority FROM providers").fetchall()
            providers = [{"name": r[0], "is_active": bool(r[1]), "priority": r[2]} for r in rows]
            return {"providers": providers}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/provider/{name}")
async def delete_provider(name: str, email: str):
    try:
        import sqlite3
        import os
        db_path = os.path.join(os.path.expanduser("~"), ".mamet", email, "memory.db")
        with sqlite3.connect(db_path) as conn:
            conn.execute("DELETE FROM providers WHERE name = ?", (name,))
            conn.commit()
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/history/{email}")
async def get_chat_history(email: str):
    """Mengambil riwayat percakapan untuk semua kolom."""
    try:
        from memory.user_memory import UserMemory
        memory = UserMemory(email)
        history = memory.get_recent_conversations(limit=50) # Ambil 50 percakapan terakhir
        
        # Kelompokkan berdasarkan kolom
        grouped = {"kolom1": [], "kolom2": [], "kolom3": []}
        
        # Urutkan dari yang terlama ke terbaru
        for row in reversed(history):
            col = row.get("column_name", "kolom2")
            if col in grouped:
                grouped[col].append({"role": "user", "content": row.get("message", "")})
                grouped[col].append({"role": "system", "content": row.get("response", ""), "requires_approval": False})
                
        return grouped
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/history/{email}/{column}")
async def clear_chat_history(email: str, column: str):
    """Menghapus riwayat percakapan untuk kolom tertentu."""
    try:
        from memory.user_memory import UserMemory
        memory = UserMemory(email)
        memory.clear_conversations(column)
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

class DrawerSaveRequest(BaseModel):
    email: str
    column: str
    drawer_name: str

@app.post("/api/drawer/save")
async def save_drawer(req: DrawerSaveRequest):
    """Menyimpan meja aktif ke laci."""
    try:
        from memory.user_memory import UserMemory
        memory = UserMemory(req.email)
        memory.save_to_drawer(req.column, req.drawer_name)
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/drawer/load")
async def load_drawer(req: DrawerSaveRequest):
    """Mengambil dari laci ke meja aktif."""
    try:
        from memory.user_memory import UserMemory
        memory = UserMemory(req.email)
        memory.load_from_drawer(req.column, req.drawer_name)
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/drawer/list/{email}/{column}")
async def list_drawers(email: str, column: str):
    """Mendapatkan daftar laci."""
    try:
        from memory.user_memory import UserMemory
        memory = UserMemory(email)
        drawers = memory.list_drawers(column)
        return {"drawers": drawers}
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
    """Endpoint login minimal."""
    if req.email == "andreanastasya798@gmail.com" and req.password == "titan123@":
        import secrets
        token = secrets.token_hex(32)
        return {"token": token, "email": req.email}
    else:
        raise HTTPException(status_code=401, detail="Email atau password salah")

@app.post("/api/login2")
async def login2(req: AuthRequest):
    """Endpoint login minimal yang langsung memverifikasi kredensial."""
    # Verifikasi langsung tanpa AuthHandler
    email = req.email
    password = req.password
    
    # Untuk sementara, terima kredensial ini
    if email == "andreanastasya798@gmail.com" and password == "titan123@":
        import secrets
        token = secrets.token_hex(32)
        return {"token": token, "email": email}
    else:
        raise HTTPException(status_code=401, detail="Email atau password salah")

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

# ================= GOOGLE DRIVE SYNC (WARISAN DIGITAL) ================= #

class SyncRequest(BaseModel):
    email: str

@app.post("/api/sync/backup")
async def backup_to_drive(req: SyncRequest):
    """Mengunggah memory.db dan chroma_db ke Google Drive."""
    try:
        from memory.google_drive_sync import GoogleDriveSync
        sync = GoogleDriveSync(req.email)
        
        res_db = sync.backup_database()
        if res_db.get("status") != "success":
            raise HTTPException(status_code=500, detail=res_db.get("message", "Gagal backup DB"))
            
        res_chroma = sync.backup_chromadb()
        if res_chroma.get("status") != "success":
            return {"status": "partial", "message": f"{res_db['message']} namun RAG gagal: {res_chroma.get('message')}"}
            
        return {"status": "success", "message": "Backup memori dan RAG ke Google Drive berhasil!"}
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/sync/restore")
async def restore_from_drive(req: SyncRequest):
    """Memulihkan memory.db dari Google Drive."""
    try:
        from memory.google_drive_sync import GoogleDriveSync
        sync = GoogleDriveSync(req.email)
        
        res_db = sync.restore_database()
        if res_db.get("status") != "success":
            raise HTTPException(status_code=500, detail=res_db.get("message", "Gagal restore DB"))
            
        return {"status": "success", "message": res_db["message"]}
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)