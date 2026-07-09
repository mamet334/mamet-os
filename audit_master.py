import asyncio
import os
import sys
import json

# Tambahkan path agar modul mamet-os bisa diimport
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from orchestrator.main_orchestrator import MainOrchestrator
from ai.provider_router import ProviderRouter

# Mock fungsi chat dari ProviderRouter agar tidak butuh koneksi internet
def mock_chat(self, messages):
    print("\n" + "="*70)
    print("--- [LLM MOCK CEGATAN] ---")
    for msg in messages:
        if msg['role'] == 'system':
            print(f"[SYSTEM PROMPT]\n{msg['content']}\n")
    print("="*70 + "\n")
    return "[Mock Response] Perintah dieksekusi dengan sempurna."

ProviderRouter.chat = mock_chat

async def run_audit():
    print("*"*80)
    print("AUDIT SIMULASI MASTER: SEMUA FITUR PILAR B")
    print("*"*80)
    
    orchestrator = MainOrchestrator()
    await orchestrator.boot()
    
    test_cases = [
        {
            "name": "FITUR 1: PROJECT CONTEXT",
            "message": "Tolong baca file planning_engine.py dan jelaskan isinya.",
            "context": r"D:\SLAMET\other\mamet-os\backend\orchestrator"
        },
        {
            "name": "FITUR 2: DETEKSI EMOSI (BINGUNG)",
            "message": "Tolong banget, saya pusing gimana cara jalankan kode ini???",
            "context": None
        },
        {
            "name": "FITUR 3: MERINGKAS (STRUCTURED WRITING)",
            "message": "Coba buatkan kesimpulan dari arsitektur backend kita.",
            "context": None
        },
        {
            "name": "FITUR 4: TUGAS MULTI-LANGKAH OTONOM (ULTIMATE TEST)",
            "message": "Tolong ringkas dokumen planning_engine.py, lalu jelaskan dengan santai, kemudian simpan ke file hasil.md",
            "context": r"D:\SLAMET\other\mamet-os\backend\orchestrator"
        }
    ]
    
    for case in test_cases:
        print(f"\n\n{'='*80}")
        print(f"[TEST] MENGUJI: {case['name']}")
        print(f"[MSG]  PESAN  : '{case['message']}'")
        print(f"[DIR]  KONTEKS: '{case['context']}'")
        print(f"{'='*80}")
        
        # Eksekusi proses
        response = await orchestrator.process(
            user_id="default@mamet.os",
            column="kolom2",
            message=case['message'],
            project_context=case['context'],
            api_key="mock_key"
        )
        print("[OK] PENGUJIAN SELESAI UNTUK SKENARIO INI.")

if __name__ == "__main__":
    asyncio.run(run_audit())
