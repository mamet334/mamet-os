import asyncio
import os
import sys

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
    return "[Mock Response] Tugas berantai selesai dikerjakan."

ProviderRouter.chat = mock_chat

async def run_audit():
    print("="*60)
    print("AUDIT SIMULASI: TUGAS MULTI-LANGKAH OTONOM")
    print("="*60)
    
    orchestrator = MainOrchestrator()
    await orchestrator.boot()
    
    test_cases = [
        ("TUGAS TUNGGAL", "Tolong carikan rumus phytagoras."),
        ("MULTI-LANGKAH (2 TAHAP)", "Tolong ringkas dokumen README.md, lalu jelaskan poin utamanya kepada saya secara santai."),
        ("MULTI-LANGKAH (3 TAHAP)", "Cari berita tentang AI, kemudian buatkan ringkasannya, dan simpan ke file berita.md"),
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

if __name__ == "__main__":
    asyncio.run(run_audit())
