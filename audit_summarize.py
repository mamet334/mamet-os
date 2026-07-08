import asyncio
import os
import sys
import json

# Tambahkan path agar modul mamet-os bisa diimport
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from orchestrator.main_orchestrator import MainOrchestrator
from ai.provider_router import ProviderRouter

# Mock fungsi chat dari ProviderRouter agar tidak butuh koneksi internet
# dan kita bisa mengintip System Prompt yang dihasilkan
original_chat = ProviderRouter.chat

def mock_chat(self, messages):
    print("\n" + "="*50)
    print("--- [LLM DI PANGGIL: MOCK CHAT] ---")
    for msg in messages:
        if msg['role'] == 'system':
            print(f"SYSTEM PROMPT:\n{msg['content']}\n")
    print("="*50 + "\n")
    return "[Mock Response] Laporan Terstruktur Berhasil Dibuat."

ProviderRouter.chat = mock_chat

async def run_audit():
    print("="*60)
    print("AUDIT SIMULASI: STRUCTURED SUMMARIZATION")
    print("="*60)
    
    orchestrator = MainOrchestrator()
    await orchestrator.boot()
    
    test_cases = [
        ("PERTANYAAN BIASA", "Jelaskan cara kerja memori SQLite."),
        ("MERINGKAS (RINGKAS)", "Tolong ringkas dokumen README.md yang panjang itu."),
        ("MERINGKAS (KESIMPULAN)", "Buatkan kesimpulan dari analisis kode backend kita."),
    ]
    
    for label, message in test_cases:
        print(f"\n>> MENGIRIM PESAN ({label}): '{message}'")
        
        # Eksekusi proses
        # Pakai api_key palsu agar decision engine masuk ke cabang LLM
        response = await orchestrator.process(
            user_id="default@mamet.os",
            column="kolom2",
            message=message,
            api_key="mock_key"
        )
        
        # Untuk membuktikan bahwa plan.get('requires_structured_format') aktif,
        # Kita bisa melihat hasil print dari System Prompt.

if __name__ == "__main__":
    asyncio.run(run_audit())
