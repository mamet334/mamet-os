import os
import asyncio
from orchestrator.evidence_collector import EvidenceCollector

async def audit():
    print("=== AUDIT LEGO EXPANSION ===")
    
    # 1. Create a broken plugin (syntax error)
    bad_syntax_path = os.path.join("custom_modules", "bad_syntax.py")
    with open(bad_syntax_path, "w") as f:
        f.write("class Broken(LegoModule\n    def __init__")
        
    # 2. Create a plugin that fails on init
    bad_init_path = os.path.join("custom_modules", "bad_init.py")
    with open(bad_init_path, "w") as f:
        f.write("from lego_modules.base_lego import LegoModule\n")
        f.write("from typing import Dict, Any\n")
        f.write("class BadInit(LegoModule):\n")
        f.write("    def __init__(self):\n")
        f.write("        raise ValueError('Simulated Init Crash')\n")
        f.write("    @property\n")
        f.write("    def name(self) -> str: return 'BadInit'\n")
        f.write("    @property\n")
        f.write("    def version(self) -> str: return '1.0'\n")
        f.write("    def can_handle(self, i): return False\n")
        f.write("    async def process(self, i): return {}\n")

    try:
        print("\n[TEST 1] Inisialisasi Evidence Collector (Error Handling Check)")
        # This will trigger LegoRegistry to scan custom_modules
        collector = EvidenceCollector()
        
        print("\n[TEST 2] Cek modul yang berhasil terdaftar")
        modules = collector.lego_registry.get_modules()
        module_names = [m['name'] for m in modules]
        print(f"Modul Aktif: {module_names}")
        
        if "HelloLego" in module_names and "BadInit" not in module_names:
            print("=> LULUS: Hanya modul yang valid yang didaftarkan.")
        else:
            print("=> GAGAL: Ada masalah pada proses filtering modul.")
            
        print("\n[TEST 3] Simulasi Input dari Orchestrator ke Lego Module")
        # Simulasikan Evidence Collector dipanggil dengan intent "hello_lego"
        plan = {
            "steps": ["check_lego_modules"],
            "intent": "hello_lego",
            "original_message": "test module lego"
        }
        
        result = await collector.collect("user123", "kolom2", plan)
        print(f"Hasil Collect: {result['items']}")
        
        passed = False
        for item in result.get("items", []):
            if item.get("source") == "lego_module" and item.get("data", {}).get("response") == "Hello dari Custom Module Lego!":
                passed = True
                break
                
        if passed:
            print("=> LULUS: End-to-end evidence collector berhasil merutekan dan mengambil respons Lego.")
        else:
            print("=> GAGAL: Routing data tidak berfungsi sebagaimana mestinya.")

    finally:
        # Cleanup
        if os.path.exists(bad_syntax_path): os.remove(bad_syntax_path)
        if os.path.exists(bad_init_path): os.remove(bad_init_path)

if __name__ == "__main__":
    asyncio.run(audit())
