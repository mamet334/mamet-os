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
    print("\n--- [LLM DI PANGGIL] ---")
    for msg in messages:
        if msg['role'] == 'system':
            print(f"SYSTEM PROMPT: {msg['content']}")
    return "[Mock Response] Selesai."

ProviderRouter.chat = mock_chat

async def run_audit():
    print("="*60)
    print("AUDIT SIMULASI: TONE ADAPTATION")
    print("="*60)
    
    orchestrator = MainOrchestrator()
    await orchestrator.boot()
    
    test_cases = [
        ("MARAH", "sistem ini error terus!! dasar jelek!"),
        ("BURU-BURU", "Cepat buatkan script sekarang!"),
        ("BINGUNG", "Tolong banget, saya bingung gimana cara pakai ini???"),
        ("SANTAI", "Halo bro, mantap nih aplikasinya wkwk"),
        ("NETRAL", "Apakah Anda bisa membantu saya menganalisis data ini?"),
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
