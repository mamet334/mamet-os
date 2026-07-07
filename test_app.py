import asyncio
import os
import sys
sys.stdout.reconfigure(encoding='utf-8')
from pathlib import Path

# Setup path
sys.path.append(str(Path(__file__).parent / "backend"))

from orchestrator.main_orchestrator import MainOrchestrator

async def run_simulation():
    print("="*50)
    print("MAMET OS - FULL SYSTEM SIMULATION")
    print("="*50)
    
    orchestrator = MainOrchestrator()
    await orchestrator.boot()
    
    user_id = "test_user_1"
    
    # 1. KOLOM 2: Asisten Pribadi
    print("\n[SIMULASI KOLOM 2] Halo, ingat nama saya Slamet.")
    res = await orchestrator.process(
        user_id=user_id,
        column="kolom2",
        message="Halo, ingat nama saya Slamet. Tolong catat itu.",
        api_key=None
    )
    print(f"Response: {res.get('response')}")
    
    # 2. KOLOM 3: Engineer
    print("\n[SIMULASI KOLOM 3] Minta list folder")
    res = await orchestrator.process(
        user_id=user_id,
        column="kolom3",
        message="list folder backend",
        api_key=None
    )
    print(f"Response:\n{res.get('response')[:500]}...")
    
    # 3. KOLOM 1: Pencarian Cepat (RAG)
    print("\n[SIMULASI KOLOM 1] Cari dokumen tentang RAG")
    res = await orchestrator.process(
        user_id=user_id,
        column="kolom1",
        message="Apa itu RAG?",
        api_key=None
    )
    print(f"Response: {res.get('response')[:500]}")
    
    await orchestrator.shutdown()

if __name__ == "__main__":
    asyncio.run(run_simulation())
