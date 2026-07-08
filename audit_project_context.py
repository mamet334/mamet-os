import asyncio
import os
import sys

# Tambahkan path agar modul mamet-os bisa diimport
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from orchestrator.main_orchestrator import MainOrchestrator

async def run_audit():
    print("="*60)
    print("AUDIT SIMULASI: PROJECT CONTEXT")
    print("="*60)
    
    # Inisialisasi Orchestrator
    print("\n1. Booting Orchestrator...")
    orchestrator = MainOrchestrator()
    await orchestrator.boot()
    
    # Path target yang akan dibaca (misalnya folder mamet-os/backend/orchestrator)
    target_project_path = os.path.join(os.getcwd(), 'backend', 'orchestrator')
    print(f"\n2. Setting Project Context ke: {target_project_path}")
    
    # Simulasi pertanyaan ke Asisten Pribadi (Kolom 2)
    # Bertanya soal salah satu file di dalam project context
    message = "Tolong baca file planning_engine.py dan jelaskan secara singkat apa fungsinya."
    print(f"\n3. Mengirim pesan ke Asisten (kolom2): '{message}'")
    
    print("\n4. Menjalankan proses...")
    response = await orchestrator.process(
        user_id="default@mamet.os",
        column="kolom2",
        message=message,
        api_key="dummy_key",  # Tidak butuh real key karena kita cuma mau lihat logs dan decision
        project_context=target_project_path
    )
    
    print("\n" + "="*60)
    print("HASIL AKHIR DECISION ENGINE")
    print("="*60)
    print(f"Action: {response.get('action')}")
    print(f"Message: {response.get('response')[:200]}...") # Print sebagian aja
    
    # Print rekam jejak
    actions = response.get('approval_details', {}).get('actions_taken', [])
    if not actions: # fallback kalau ga ada di approval details
        actions = []
    print(f"Rekam Jejak Internal: {actions}")
    
    print("="*60)

if __name__ == "__main__":
    asyncio.run(run_audit())
