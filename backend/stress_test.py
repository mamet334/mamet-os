import asyncio
import os
import sys
import time
import tracemalloc
from concurrent.futures import ThreadPoolExecutor

sys.path.append(os.path.join(os.getcwd(), 'backend'))

from orchestrator.main_orchestrator import MainOrchestrator
from ai.provider_router import ProviderRouter

# Mock fungsi chat dari ProviderRouter agar tidak butuh koneksi internet
# dan agar pengujian murni fokus pada stabilitas engine MAMET OS
def mock_chat(self, messages):
    return "[Mock Response] Stabilitas Terjaga."

ProviderRouter.chat = mock_chat

async def simulate_request(orchestrator, req_id, message):
    """Simulasi satu permintaan asinkron."""
    try:
        start_time = time.time()
        # Menggunakan kolom2 (Asisten Pribadi) agar memicu seluruh engine (RAG, Memory, Planner)
        response = await orchestrator.process(
            user_id="stress_test@mamet.os",
            column="kolom2",
            message=f"{message} [REQ-{req_id}]",
            api_key="mock_key"
        )
        elapsed = time.time() - start_time
        return {"id": req_id, "status": "success", "time": elapsed}
    except Exception as e:
        return {"id": req_id, "status": "error", "error": str(e)}

async def run_stress_test():
    print("="*60)
    print("🚨 MEMULAI PILAR D: UNIT & STRESS TEST 🚨")
    print("="*60)
    
    orchestrator = MainOrchestrator()
    await orchestrator.boot()
    
    # 1. TEST JATUH (API FALLBACK / ERROR HANDLING)
    print("\n[TEST 1] API Fallback & Error Handling")
    print("-" * 40)
    # Kita paksa ProviderRouter untuk error
    def mock_chat_error(self, messages):
        raise Exception("401 Client Error: Unauthorized (Key Invalid)")
    
    ProviderRouter.chat = mock_chat_error
    try:
        res = await orchestrator.process("stress_test@mamet.os", "kolom2", "Cek error API", api_key="invalid_key")
        print(f"✅ Sistem berhasil menangkap error tanpa crash!")
        print(f"   Response yang diberikan ke User: {res['response']}")
    except Exception as e:
        print(f"❌ SISTEM CRASH KARENA ERROR API TIDAK DITANGANI: {e}")
        
    # Kembalikan mock chat normal
    ProviderRouter.chat = mock_chat
    
    # 2. STRESS TEST CONCURRENCY (BOMBARDEMENT) & MEMORY LEAK
    print("\n[TEST 2] Concurrency Bombardment & Memory Leak Check")
    print("-" * 40)
    num_requests = 50
    print(f"Menembakkan {num_requests} request secara serentak (concurrent)...")
    
    tracemalloc.start()
    snapshot1 = tracemalloc.take_snapshot()
    
    start_total = time.time()
    
    # Buat 50 tugas secara bersamaan
    tasks = []
    for i in range(num_requests):
        tasks.append(simulate_request(orchestrator, i, "Halo asisten, tolong ingat ini."))
        
    results = await asyncio.gather(*tasks)
    
    end_total = time.time()
    snapshot2 = tracemalloc.take_snapshot()
    
    # Analisis hasil
    success_count = sum(1 for r in results if r["status"] == "success")
    error_count = sum(1 for r in results if r["status"] == "error")
    
    print(f"\n📊 HASIL STRESS TEST:")
    print(f"   Total Request : {num_requests}")
    print(f"   Sukses        : {success_count}")
    print(f"   Error         : {error_count}")
    print(f"   Total Waktu   : {end_total - start_total:.2f} detik")
    
    if error_count > 0:
        print("   Contoh Error  :")
        for r in results:
            if r["status"] == "error":
                print(f"      - {r['error']}")
                break
                
    # Cek Kebocoran Memori (Memory Leak)
    print("\n🔍 ANALISIS KEBOCORAN MEMORI (Top 3):")
    top_stats = snapshot2.compare_to(snapshot1, 'lineno')
    for stat in top_stats[:3]:
        print(f"   {stat}")
        
    # Jika alokasi tumbuh sangat besar, itu tanda bahaya
    total_diff = sum(stat.size_diff for stat in top_stats)
    print(f"   Total selisih memori: {total_diff / 1024:.2f} KB")
    
    print("\n="*60)
    print("SELESAI.")

if __name__ == "__main__":
    asyncio.run(run_stress_test())
